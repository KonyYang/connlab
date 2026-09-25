from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

import pytest

from backend.application.official_project_workspace_service import (
    OfficialProjectWorkspaceService,
    OfficialWorkspaceCreateError,
    OfficialWorkspaceRecord,
    _unique_backup_path,
    _prepare_history_archive,
    resolve_official_template_root,
)
from backend.application.official_folder_relocation_service import (
    OfficialFolderRelocationService, _require_relocation_path_capacity,
)
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.files.recoverable_output_publisher import file_identity
from backend.application.project_lifecycle_write_guard import ProjectLifecycleReadonlyError
from backend.infrastructure.official_workspace_manifest import (
    OfficialWorkspaceManifest,
    OfficialWorkspaceManifestGateway,
)
from backend.domain import ApplicationForm, LtrRecord, LtrStatus, Project, ProjectLifecycleState, ProjectStatus
from backend.shared.config import OfficialWorkspaceSettings
from backend.application.project_basic_information_output import ConfirmedBasicInformationSnapshot


class _BasicReader:
    def __init__(self, values=None):
        self.values = values

    def get_latest_confirmed(self, project_id):
        if self.values is None:
            return None
        return ConfirmedBasicInformationSnapshot(
            project_id, 3, self.values, "confirmed-source", None, None
        )

    def get_preview_snapshot(self, project_id):
        raise AssertionError("Official folder naming must not read unconfirmed drafts")


@pytest.mark.parametrize("values, expected", [
    ({"product_description": "Customized PBU Connector with 14P",
      "test_item": "Solderability  and Mechanical Testing", "dl_number": "WRONG"},
     "DL-2025-11-074 Customized PBU Connector with 14P Solderability and Mechanical Testing"),
    (None, "DL-2025-11-074 Coolpower Qualification test"),
    ({"product_description": "", "test_item": ""},
     "DL-2025-11-074 Coolpower Qualification test"),
])
def test_workspace_names_use_confirmed_basic_information_only(tmp_path, values, expected):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path, basic_information_reader=_BasicReader(values),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    preview = service.preview("project-1")
    assert preview.official_folder_path.name == expected
    result = service.create("project-1")
    assert result.official_folder_path.name == expected
    assert result.official_folder_path.is_dir()
    assert json.loads(result.record.manifest_path.read_text(encoding="utf-8"))[
        "official_project_folder_path"
    ] == str(result.official_folder_path)


def test_confirmed_name_change_does_not_silently_move_existing_files(tmp_path):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    reader = _BasicReader()
    service = _service(
        tmp_path, basic_information_reader=reader,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    original = service.create("project-1")
    operator_file = original.official_folder_path / "Test results" / "operator.txt"
    operator_file.write_text("retained", encoding="utf-8")
    reader.values = {"product_description": "New connector", "test_item": "New testing"}
    preview = service.preview("project-1")
    assert preview.official_folder_path == original.official_folder_path
    assert preview.suggested_folder_path == (
        original.record.local_workspace_path / "DL-2025-11-074 New connector New testing"
    )
    assert any("different official folder name" in warning for warning in preview.warnings)
    assert operator_file.read_text(encoding="utf-8") == "retained"
    assert not (original.record.local_workspace_path / "DL-2025-11-074 New connector New testing").exists()


def test_rebuild_of_indexed_legacy_workspace_keeps_new_folder_in_that_workspace(tmp_path):
    template = _make_template(tmp_path / "template")
    current_root = tmp_path / "current"
    current_root.mkdir()
    legacy_root = current_root / "legacy"
    legacy_root.mkdir()
    reader, repository = _BasicReader(), _WorkspaceRepo()
    legacy = _service(
        tmp_path, repository=repository, basic_information_reader=reader,
        settings=OfficialWorkspaceSettings(legacy_root, template, None),
    )
    original = legacy.create("project-1")
    reader.values = {"product_description": "Confirmed connector", "test_item": "Qualification"}
    current = _service(
        tmp_path, repository=repository, basic_information_reader=reader,
        settings=OfficialWorkspaceSettings(current_root, template, None),
    )

    assert current.preview("project-1").suggested_folder_path == (
        current_root / "DL-2025-11-074" / "DL-2025-11-074 Confirmed connector Qualification"
    )
    rebuild = current.preview_for_rebuild("project-1")
    assert rebuild.conflict_paths == (original.official_folder_path,)
    assert rebuild.official_folder_path == (
        original.record.local_workspace_path / "DL-2025-11-074 Confirmed connector Qualification"
    )
    assert not (current_root / "DL-2025-11-074").exists()


@pytest.mark.parametrize("retain_manifest_identity", [True, False])
def test_rebuild_rejects_replaced_folder_when_manifest_has_identity(tmp_path, retain_manifest_identity):
    template = _make_template(tmp_path / "template")
    root = tmp_path / "workspaces"
    root.mkdir()
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(root, template, None),
    )
    original = service.create("project-1")
    manifest = original.record.manifest_path
    if not retain_manifest_identity:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload.pop("official_folder_identity")
        manifest.write_text(json.dumps(payload), encoding="utf-8")
    original.official_folder_path.rename(tmp_path / "detached-original")
    original.official_folder_path.mkdir()

    reviewed = service.preview_for_rebuild("project-1")

    if retain_manifest_identity:
        assert reviewed.status == "conflict"
        assert any("identity" in blocker for blocker in reviewed.blockers)
    else:
        assert reviewed.status == "completed"
        assert reviewed.conflict_paths == (original.official_folder_path,)


def test_legacy_pre_effect_rebuild_keeps_original_approved_folder_name(tmp_path):
    from backend.infrastructure.files.recoverable_workspace_publisher import RecoverableWorkspacePublisher

    template = _make_template(tmp_path / "template")
    (template / "template.txt").write_text("new template", encoding="utf-8")
    root = tmp_path / "workspaces"
    root.mkdir()
    reader, repository = _BasicReader(), _WorkspaceRepo()
    service = _service(
        tmp_path, repository=repository, basic_information_reader=reader,
        settings=OfficialWorkspaceSettings(root, template, None),
    )
    original = service.create("project-1")
    (original.official_folder_path / "operator.txt").write_text("archived", encoding="utf-8")
    reader.values = {"product_description": "New connector", "test_item": "New testing"}
    journal = GenerationJournal(tmp_path / "legacy-generation-journal")
    state = journal.create("project-1", "backup_and_recreate", "original reviewed inputs")
    assert "archive_source_identity_only" not in state

    rebuilt = service.create(
        "project-1", conflict_strategy="backup_and_recreate",
        recovery=RecoverableWorkspacePublisher(journal, state),
    )

    assert rebuilt.official_folder_path == original.official_folder_path
    assert (rebuilt.official_folder_path / "template.txt").read_text(encoding="utf-8") == "new template"
    assert not (rebuilt.official_folder_path / "operator.txt").exists()
    assert not (original.record.local_workspace_path / "DL-2025-11-074 New connector New testing").exists()


def test_create_and_rebuild_block_multiple_active_ltr_children(tmp_path):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    first = workspace / "DL-2025-11-074 First"
    second = workspace / "DL-2025-11-074 Second"
    first.mkdir(parents=True)
    second.mkdir()
    (first / "operator.txt").write_text("first", encoding="utf-8")
    (second / "operator.txt").write_text("second", encoding="utf-8")

    preview = service.preview("project-1")
    assert preview.status == "conflict"
    assert "multiple" in preview.blockers[0].lower()
    assert preview.conflict_options == ()
    with pytest.raises(OfficialWorkspaceCreateError):
        service.create("project-1", conflict_strategy="backup_and_recreate")
    assert (first / "operator.txt").read_text(encoding="utf-8") == "first"
    assert (second / "operator.txt").read_text(encoding="utf-8") == "second"


def test_reviewed_same_project_rename_moves_folder_and_updates_identity(tmp_path):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    reader = _BasicReader()
    repository = _WorkspaceRepo()
    workspace_service = _service(
        tmp_path, repository=repository, basic_information_reader=reader,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    original = workspace_service.create("project-1")
    (original.official_folder_path / "Test results" / "operator.txt").write_text("kept", encoding="utf-8")
    reader.values = {"product_description": "New connector", "test_item": "New testing"}
    relocation = OfficialFolderRelocationService(
        workspace_service=workspace_service, workspace_repository=repository,
        journal=GenerationJournal(tmp_path / "relocation-journal"),
    )
    reviewed = relocation.preview("project-1")

    assert reviewed.status == "rename_available"
    result = relocation.apply("project-1", "rename_to_confirmed", reviewed.expected_context)

    target = original.record.local_workspace_path / "DL-2025-11-074 New connector New testing"
    assert result.official_folder_path == target
    assert (target / "Test results" / "operator.txt").read_text(encoding="utf-8") == "kept"
    assert not original.official_folder_path.exists()
    assert repository.saved.official_folder_path == target
    assert json.loads(original.record.manifest_path.read_text(encoding="utf-8"))["official_project_folder_path"] == str(target)


def test_unique_manual_name_can_be_explicitly_rebound_without_replacing_it(tmp_path):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    reader = _BasicReader()
    repository = _WorkspaceRepo()
    workspace_service = _service(
        tmp_path, repository=repository, basic_information_reader=reader,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    original = workspace_service.create("project-1")
    custom = original.record.local_workspace_path / "DL-2025-11-074 Operator Custom"
    original.official_folder_path.rename(custom)
    (custom / "operator.txt").write_text("kept", encoding="utf-8")
    reader.values = {"product_description": "New connector", "test_item": "New testing"}
    relocation = OfficialFolderRelocationService(
        workspace_service=workspace_service, workspace_repository=repository,
        journal=GenerationJournal(tmp_path / "relocation-journal"),
    )
    reviewed = relocation.preview("project-1")

    assert reviewed.status == "manual_relink_available"
    assert reviewed.candidate_path == custom
    assert {option.key for option in reviewed.actions} == {
        "rebind_and_rename", "rebind_keep_custom"
    }
    result = relocation.apply("project-1", "rebind_keep_custom", reviewed.expected_context)
    assert result.official_folder_path == custom
    assert (custom / "operator.txt").read_text(encoding="utf-8") == "kept"
    assert repository.saved.official_folder_path == custom
    assert json.loads(original.record.manifest_path.read_text(encoding="utf-8"))["official_project_folder_path"] == str(custom)
    assert relocation.preview("project-1").status == "not_needed"


def test_confirmed_name_can_be_explicitly_kept_without_renaming(tmp_path):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    reader = _BasicReader()
    repository = _WorkspaceRepo()
    workspace_service = _service(
        tmp_path, repository=repository, basic_information_reader=reader,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    original = workspace_service.create("project-1")
    reader.values = {"product_description": "New connector", "test_item": "New testing"}
    relocation = OfficialFolderRelocationService(
        workspace_service=workspace_service, workspace_repository=repository,
        journal=GenerationJournal(tmp_path / "relocation-journal"),
    )
    reviewed = relocation.preview("project-1")
    assert {option.key for option in reviewed.actions} == {
        "rename_to_confirmed", "keep_current_name",
    }
    result = relocation.apply("project-1", "keep_current_name", reviewed.expected_context)
    assert result.official_folder_path == original.official_folder_path
    assert relocation.preview("project-1").status == "not_needed"
    reader.values = {"product_description": "Another connector", "test_item": "New testing"}
    assert relocation.preview("project-1").status == "rename_available"


def test_unique_manual_name_can_be_rebound_to_confirmed_name(tmp_path):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    reader = _BasicReader()
    repository = _WorkspaceRepo()
    workspace_service = _service(
        tmp_path, repository=repository, basic_information_reader=reader,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    original = workspace_service.create("project-1")
    custom = original.record.local_workspace_path / "DL-2025-11-074 Operator Custom"
    original.official_folder_path.rename(custom)
    (custom / "operator.txt").write_text("kept", encoding="utf-8")
    reader.values = {"product_description": "New connector", "test_item": "New testing"}
    relocation = OfficialFolderRelocationService(
        workspace_service=workspace_service, workspace_repository=repository,
        journal=GenerationJournal(tmp_path / "relocation-journal"),
    )
    reviewed = relocation.preview("project-1")

    assert reviewed.status == "manual_relink_available"
    result = relocation.apply("project-1", "rebind_and_rename", reviewed.expected_context)

    confirmed = original.record.local_workspace_path / "DL-2025-11-074 New connector New testing"
    assert result.official_folder_path == confirmed
    assert (confirmed / "operator.txt").read_text(encoding="utf-8") == "kept"
    assert not custom.exists()
    assert repository.saved.official_folder_path == confirmed
    assert json.loads(original.record.manifest_path.read_text(encoding="utf-8"))["official_project_folder_path"] == str(confirmed)


def test_manual_rebind_rejects_a_replacement_folder_with_the_same_dl_prefix(tmp_path):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    repository = _WorkspaceRepo()
    workspace_service = _service(
        tmp_path, repository=repository, basic_information_reader=_BasicReader(),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    original = workspace_service.create("project-1")
    retained = original.record.local_workspace_path / "operator-retained"
    original.official_folder_path.rename(retained)
    replacement = original.record.local_workspace_path / "DL-2025-11-074 Operator Replacement"
    replacement.mkdir()
    (replacement / "foreign.txt").write_text("foreign", encoding="utf-8")
    relocation = OfficialFolderRelocationService(
        workspace_service=workspace_service, workspace_repository=repository,
        journal=GenerationJournal(tmp_path / "relocation-journal"),
    )

    preview = relocation.preview("project-1")
    assert preview.status == "blocked"
    assert "identity" in preview.blockers[0].lower()
    assert preview.actions == ()
    assert (replacement / "foreign.txt").read_text(encoding="utf-8") == "foreign"


def test_manual_rebind_requires_manifest_folder_identity_proof(tmp_path):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    repository = _WorkspaceRepo()
    workspace_service = _service(
        tmp_path, repository=repository, basic_information_reader=_BasicReader(),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    original = workspace_service.create("project-1")
    manifest_path = original.record.manifest_path
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload.pop("official_folder_identity", None)
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    candidate = original.record.local_workspace_path / "DL-2025-11-074 Operator Custom"
    original.official_folder_path.rename(candidate)
    relocation = OfficialFolderRelocationService(
        workspace_service=workspace_service, workspace_repository=repository,
        journal=GenerationJournal(tmp_path / "relocation-journal"),
    )

    preview = relocation.preview("project-1")
    assert preview.status == "blocked"
    assert "identity" in preview.blockers[0].lower()
    assert preview.actions == ()


def test_interrupted_folder_move_resumes_without_second_move_or_data_loss(tmp_path):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    reader = _BasicReader()

    class FailingOnceRepository(_WorkspaceRepo):
        def __init__(self):
            super().__init__()
            self.fail_once = True

        def publish_relocation(self, record, *, source, target, operation_id, expected_identity):
            if self.fail_once:
                self.fail_once = False
                raise OSError("simulated database commit failure")
            return super().publish_relocation(
                record, source=source, target=target, operation_id=operation_id,
                expected_identity=expected_identity,
            )

    repository = FailingOnceRepository()
    workspace_service = _service(
        tmp_path, repository=repository, basic_information_reader=reader,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    original = workspace_service.create("project-1")
    reader.values = {"product_description": "New connector", "test_item": "New testing"}
    journal = GenerationJournal(tmp_path / "relocation-journal")
    relocation = OfficialFolderRelocationService(
        workspace_service=workspace_service, workspace_repository=repository,
        journal=journal,
    )
    reviewed = relocation.preview("project-1")
    with pytest.raises(OSError, match="simulated database commit failure"):
        relocation.apply("project-1", "rename_to_confirmed", reviewed.expected_context)
    target = original.record.local_workspace_path / "DL-2025-11-074 New connector New testing"
    assert target.is_dir()
    assert repository.saved.official_folder_path == original.official_folder_path

    restarted = OfficialFolderRelocationService(
        workspace_service=workspace_service, workspace_repository=repository,
        journal=GenerationJournal(tmp_path / "relocation-journal"),
    )
    pending = restarted.preview("project-1")
    assert pending.status == "interrupted"
    result = restarted.apply("project-1", "resume", pending.expected_context)

    assert result.official_folder_path == target
    assert repository.saved.official_folder_path == target
    assert not original.official_folder_path.exists()


def test_relocation_revalidates_manifest_before_moving_any_folder(tmp_path, monkeypatch):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    reader = _BasicReader()
    repository = _WorkspaceRepo()
    workspace_service = _service(
        tmp_path, repository=repository, basic_information_reader=reader,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    original = workspace_service.create("project-1")
    reader.values = {"product_description": "New connector", "test_item": "New testing"}
    journal = GenerationJournal(tmp_path / "relocation-journal")
    relocation = OfficialFolderRelocationService(
        workspace_service=workspace_service, workspace_repository=repository,
        journal=journal,
    )
    reviewed = relocation.preview("project-1")
    real_save = journal.save
    tampered = False

    def save_then_change_manifest(state):
        nonlocal tampered
        real_save(state)
        if not tampered and state.get("effects", {}).get("relocation"):
            tampered = True
            manifest_path = original.record.manifest_path
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["project_id"] = "foreign-project"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(journal, "save", save_then_change_manifest)
    with pytest.raises((OfficialWorkspaceCreateError, ValueError)):
        relocation.apply("project-1", "rename_to_confirmed", reviewed.expected_context)
    assert original.official_folder_path.is_dir()
    assert not reviewed.suggested_path.exists()


def test_relocation_identity_failure_does_not_leave_unresumable_empty_journal(tmp_path, monkeypatch):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    reader = _BasicReader()
    repository = _WorkspaceRepo()
    workspace_service = _service(
        tmp_path, repository=repository, basic_information_reader=reader,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    original = workspace_service.create("project-1")
    reader.values = {"product_description": "New connector", "test_item": "New testing"}
    journal = GenerationJournal(tmp_path / "relocation-journal")
    relocation = OfficialFolderRelocationService(
        workspace_service=workspace_service, workspace_repository=repository,
        journal=journal,
    )
    reviewed = relocation.preview("project-1")
    real_identity = file_identity
    identity_calls = 0

    def fail_after_apply_preview(path):
        nonlocal identity_calls
        identity_calls += 1
        if identity_calls == 2:
            raise OSError("identity unavailable")
        return real_identity(path)

    monkeypatch.setattr(
        "backend.application.official_folder_relocation_service.file_identity",
        fail_after_apply_preview,
    )

    with pytest.raises(OSError, match="identity unavailable"):
        relocation.apply("project-1", "rename_to_confirmed", reviewed.expected_context)
    assert journal.read("project-1") is None
    assert original.official_folder_path.is_dir()


def test_crash_after_relocation_journal_create_can_clear_empty_attempt(tmp_path):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    repository = _WorkspaceRepo()
    workspace_service = _service(
        tmp_path, repository=repository,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces", template_path=template,
            public_drive_root=None,
        ),
    )
    original = workspace_service.create("project-1")
    journal = GenerationJournal(tmp_path / "relocation-journal")
    journal.create("project-1", "rename_to_confirmed", "reviewed")
    relocation = OfficialFolderRelocationService(
        workspace_service=workspace_service, workspace_repository=repository,
        journal=journal,
    )

    preview = relocation.preview("project-1")
    assert preview.status == "interrupted"
    assert {action.key for action in preview.actions} == {"resume"}
    result = relocation.apply("project-1", "resume", preview.expected_context)
    assert result.official_folder_path == original.official_folder_path
    assert journal.read("project-1")["status"] == "completed"
    assert original.official_folder_path.is_dir()


@pytest.mark.parametrize("moved", [False, True])
def test_archive_rebuild_can_supersede_only_unmoved_relocation_attempt(tmp_path, moved):
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    reader = _BasicReader()
    repository = _WorkspaceRepo()
    workspace_service = _service(
        tmp_path, repository=repository, basic_information_reader=reader,
        settings=OfficialWorkspaceSettings(tmp_path / "workspaces", template, None),
    )
    original = workspace_service.create("project-1")
    old = original.official_folder_path
    (old / "operator.docx").write_bytes(b"edited after relocation preview")
    reader.values = {"product_description": "Confirmed", "test_item": "Qualification testing"}
    journal = GenerationJournal(tmp_path / "relocation-journal")
    pending = journal.create("project-1", "rename_to_confirmed", "stale preview context")
    pending["effects"]["relocation"] = {
        "source": str(old), "target": str(old.with_name("DL-2025-11-074 Old target")),
        "suggested": str(old.with_name("DL-2025-11-074 Old target")),
        "directory_identity": file_identity(old), "record": original.record,
        "moved": moved,
    }
    journal.save(pending)
    relocation = OfficialFolderRelocationService(
        workspace_service=workspace_service, workspace_repository=repository, journal=journal,
    )

    if moved:
        with pytest.raises(OfficialWorkspaceCreateError, match="move|recovery"):
            relocation.abandon_unmoved_for_rebuild("project-1", old)
        assert journal.read("project-1")["status"] == "queued"
    else:
        relocation.abandon_unmoved_for_rebuild("project-1", old)
        assert journal.read("project-1")["status"] == "completed"
    assert (old / "operator.docx").read_bytes() == b"edited after relocation preview"


def test_preview_ready_for_new_workspace(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        project=Project(
            project_id="project-1",
            project_no="DL-2025-11-074",
            product_name="Coolpower",
            requestor="Alice",
            status=ProjectStatus.CONFIRMED,
        ),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "ready"
    assert preview.local_workspace_path == tmp_path / "workspaces" / "DL-2025-11-074"
    assert preview.source_book_path == preview.local_workspace_path / "Source Book"
    assert preview.official_folder_path == (
        preview.local_workspace_path / "DL-2025-11-074 Coolpower Qualification test"
    )
    assert any("Public Project locations is not configured" in warning for warning in preview.warnings)
    assert not preview.blockers


def test_resolve_template_folder_with_workspace_template_child(
    tmp_path: Path,
) -> None:
    template_folder = tmp_path / "Template"
    official_template = _make_template(
        template_folder / "DL-XXXX-YY-ZZZ project" / "DL-XXXX-YY-ZZZ Title"
    )
    (template_folder / "E-4243_D Customer Feedback Form.xlsx").write_text(
        "placeholder",
        encoding="utf-8",
    )

    resolved = resolve_official_template_root(template_folder)

    assert resolved.path == official_template
    assert resolved.mode == "workspace_template_child_root"


def test_existing_empty_dl_workspace_is_ready_for_initial_creation(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    existing_workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    existing_workspace.mkdir(parents=True)
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=tmp_path / "public",
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "ready"
    assert any(
        "empty local project workspace" in warning.lower()
        for warning in preview.warnings
    )


def test_existing_official_folder_blocks_create(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    official_folder = (
        tmp_path
        / "workspaces"
        / "DL-2025-11-074"
        / "DL-2025-11-074 Coolpower Qualification test"
    )
    official_folder.mkdir(parents=True)
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=tmp_path / "public",
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "conflict"
    assert "Source Book is missing" in preview.blockers[0]
    with pytest.raises(OfficialWorkspaceCreateError, match="Source Book is missing"):
        service.create("project-1")


def test_preview_existing_official_folder_reports_conflict_choices(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    official_folder = (
        tmp_path
        / "workspaces"
        / "DL-2025-11-074"
        / "DL-2025-11-074 Coolpower Qualification test"
    )
    official_folder.mkdir(parents=True)
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=tmp_path / "public",
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "conflict"
    assert preview.conflict_paths == (official_folder,)
    assert {option.key for option in preview.conflict_options} == {"backup_and_recreate"}


def test_create_with_backup_strategy_preserves_existing_official_folder(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    (template / "template.txt").write_text("new", encoding="utf-8")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    official_folder.mkdir(parents=True)
    (official_folder / "old.txt").write_text("old", encoding="utf-8")
    repo = _WorkspaceRepo()
    service = _service(
        tmp_path,
        repository=repo,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=tmp_path / "public",
        ),
    )

    result = service.create("project-1", conflict_strategy="backup_and_recreate")

    backups = list((workspace / "History" / "Folders").glob("DL-2025-11-074 Coolpower Qualification test [0-9]*"))
    assert len(backups) == 1
    assert (backups[0] / "old.txt").read_text(encoding="utf-8") == "old"
    assert (result.official_folder_path / "template.txt").read_text(encoding="utf-8") == "new"
    assert repo.saved is not None


def test_new_continue_existing_strategy_is_rejected_without_mutating_operator_files(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    (template / "template.txt").write_text("new", encoding="utf-8")
    (template / "shared.txt").write_text("template", encoding="utf-8")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    official_folder.mkdir(parents=True)
    (official_folder / "operator.txt").write_text("keep", encoding="utf-8")
    (official_folder / "shared.txt").write_text("manual", encoding="utf-8")
    repo = _WorkspaceRepo()
    service = _service(
        tmp_path,
        repository=repo,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=tmp_path / "public",
        ),
    )

    with pytest.raises(OfficialWorkspaceCreateError, match="not available for new"):
        service.create("project-1", conflict_strategy="continue_existing")

    assert (official_folder / "operator.txt").read_text(encoding="utf-8") == "keep"
    assert (official_folder / "shared.txt").read_text(encoding="utf-8") == "manual"
    assert not (official_folder / "template.txt").exists()
    assert not (workspace / "Source Book").exists()
    assert not list(workspace.glob("*Backup*"))
    assert repo.saved is None


def test_new_overwrite_strategy_is_rejected_without_mutating_operator_files(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    (template / "template.txt").write_text("new", encoding="utf-8")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    official_folder.mkdir(parents=True)
    (official_folder / "old.txt").write_text("old", encoding="utf-8")
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=tmp_path / "public",
        ),
    )

    with pytest.raises(OfficialWorkspaceCreateError, match="not available for new"):
        service.create("project-1", conflict_strategy="overwrite_rebuild")

    assert (official_folder / "old.txt").read_text(encoding="utf-8") == "old"
    assert not (official_folder / "template.txt").exists()
    assert not list((workspace / ".connlab" / "tmp").glob("overwrite-old-*"))


def test_backup_strategy_preserves_existing_folder_when_final_move_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    template = _make_template(tmp_path / "template")
    (template / "template.txt").write_text("new", encoding="utf-8")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    official_folder.mkdir(parents=True)
    (official_folder / "old.txt").write_text("old", encoding="utf-8")
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=tmp_path / "public",
        ),
    )
    real_move = shutil.move

    def fail_final_move(source: str, target: str) -> str:
        if source.endswith(template.name) and target.endswith("Qualification test"):
            raise OSError("final move failed")
        return real_move(source, target)

    monkeypatch.setattr(
        "backend.application.official_project_workspace_service.shutil.move",
        fail_final_move,
    )

    with pytest.raises(OfficialWorkspaceCreateError, match="final move failed"):
        service.create("project-1", conflict_strategy="backup_and_recreate")

    backups = list((workspace / "History" / "Folders").glob("DL-2025-11-074 Coolpower Qualification test [0-9]*"))
    assert len(backups) == 1
    assert (backups[0] / "old.txt").read_text(encoding="utf-8") == "old"
    assert not official_folder.exists()
    assert not list((workspace / ".connlab" / "tmp").glob("*"))


def test_existing_ltr_workspace_reports_conflict_choices(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    workspace.mkdir(parents=True)
    (workspace / "legacy.txt").write_text("legacy", encoding="utf-8")
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=tmp_path / "public",
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "conflict"
    assert workspace in preview.conflict_paths
    assert preview.conflict_options == ()


def test_create_with_backup_strategy_does_not_move_entire_ltr_workspace(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    (template / "template.txt").write_text("new", encoding="utf-8")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    workspace.mkdir(parents=True)
    (workspace / "legacy.txt").write_text("legacy", encoding="utf-8")
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=tmp_path / "public",
        ),
    )

    with pytest.raises(OfficialWorkspaceCreateError):
        service.create("project-1", conflict_strategy="backup_and_recreate")

    assert (workspace / "legacy.txt").read_text(encoding="utf-8") == "legacy"
    assert not list((tmp_path / "workspaces").glob("DL-2025-11-074 [0-9]*"))
    assert not (workspace / "DL-2025-11-074 Coolpower Qualification test").exists()


@pytest.mark.skipif(os.name != "nt", reason="Windows legacy path boundary")
def test_history_archive_long_path_blocks_before_moving_original(tmp_path):
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    workspace.mkdir(parents=True)
    original = None
    for extra in range(45, 160):
        candidate = workspace / ("DL-2025-11-074 " + "P" * extra)
        archived = workspace / "History" / "Folders" / (candidate.name + " 20260925000000")
        if len(str(candidate)) < 248 and len(str(archived)) >= 248:
            original = candidate
            break
    assert original is not None
    original.mkdir()
    (original / "operator.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(OfficialWorkspaceCreateError, match="path.*long|length"):
        _unique_backup_path(original)
    assert (original / "operator.txt").read_text(encoding="utf-8") == "keep"
    assert not (workspace / "History").exists()


def test_history_archive_parent_replacement_blocks_before_creating_folders(tmp_path, monkeypatch):
    from backend.application import official_project_workspace_service as module

    workspace = tmp_path / "DL-001"
    history = workspace / "History"
    history.mkdir(parents=True)
    original_history = workspace / "History-original"
    actual_identity = module.stable_folder_identity
    replaced = False

    def replace_after_identity(path):
        nonlocal replaced
        identity = actual_identity(path)
        if path == history and not replaced:
            history.rename(original_history)
            history.mkdir()
            replaced = True
        return identity

    monkeypatch.setattr(module, "stable_folder_identity", replace_after_identity)
    with pytest.raises(OfficialWorkspaceCreateError, match="changed|identity"):
        _prepare_history_archive(history / "Folders" / "DL-001 Old 20260925000000")
    assert replaced
    assert not (history / "Folders").exists()
    assert not (original_history / "Folders").exists()


@pytest.mark.skipif(os.name != "nt", reason="Windows legacy path boundary")
def test_relocation_long_path_blocks_before_moving_original(tmp_path):
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    source = workspace / "DL-2025-11-074 Short"
    source.mkdir(parents=True)
    (source / "operator.txt").write_text("keep", encoding="utf-8")
    target = None
    for extra in range(50, 170):
        candidate = workspace / ("DL-2025-11-074 " + "P" * extra)
        if len(str(candidate)) >= 248:
            target = candidate
            break
    assert target is not None
    with pytest.raises(OfficialWorkspaceCreateError, match="path.*long"):
        _require_relocation_path_capacity(source, target)
    assert (source / "operator.txt").read_text(encoding="utf-8") == "keep"
    assert not target.exists()


def test_create_from_adoptable_workspace_adds_missing_pieces(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    workspace.mkdir(parents=True)
    repo = _WorkspaceRepo()
    service = _service(
        tmp_path,
        repository=repo,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    result = service.create("project-1")

    assert (workspace / "Source Book").is_dir()
    assert (workspace / ".connlab" / "manifest.json").is_file()
    assert (result.official_folder_path / "Submitted Material").is_dir()
    assert repo.saved is not None
    assert repo.saved.official_folder_path == result.official_folder_path


def test_preview_completed_after_connlab_created_workspace(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    repo = _WorkspaceRepo()
    service = _service(
        tmp_path,
        repository=repo,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    result = service.create("project-1")
    preview = service.preview("project-1")

    assert preview.status == "completed"
    assert preview.official_folder_path == result.official_folder_path
    assert preview.local_workspace_path == result.record.local_workspace_path
    assert not preview.blockers


def test_completed_workspace_can_be_rebuilt_with_backup_strategy(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    (template / "template.txt").write_text("new", encoding="utf-8")
    (tmp_path / "workspaces").mkdir()
    repo = _WorkspaceRepo()
    service = _service(
        tmp_path,
        repository=repo,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )
    first = service.create("project-1")
    old_note = first.official_folder_path / "operator-note.txt"
    old_note.write_text("old folder content", encoding="utf-8")

    rebuilt = service.create("project-1", conflict_strategy="backup_and_recreate")

    backups = list((first.record.local_workspace_path / "History" / "Folders").glob(
        f"{first.official_folder_path.name} [0-9]*"
    ))
    assert len(backups) == 1
    assert (backups[0] / "operator-note.txt").read_text(encoding="utf-8") == "old folder content"
    assert not old_note.exists()
    assert (rebuilt.official_folder_path / "template.txt").read_text(encoding="utf-8") == "new"
    assert [child.name for child in first.record.local_workspace_path.iterdir()
            if child.is_dir() and child.name.startswith("DL-2025-11-074 ")] == [first.official_folder_path.name]
    assert repo.saved is not None
    assert repo.saved.workspace_id == rebuilt.record.workspace_id


def test_preview_keeps_completed_workspace_when_current_naming_rule_changes(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    repo = _WorkspaceRepo()
    service = _service(
        tmp_path,
        repository=repo,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )
    result = service.create("project-1")
    service_with_updated_identity = _service(
        tmp_path,
        repository=repo,
        ltr_repository=_LtrRepo(
            [
                LtrRecord(
                    ltr_id="ltr-1",
                    project_id="project-1",
                    ltr_number="DL-2025-11-074",
                    status=LtrStatus.REGISTERED,
                    registered_on=date(2026, 5, 11),
                    notes=json.dumps(
                        {
                            "operator_note": json.dumps(
                                {
                                    "source": "new_project_setup_confirmation",
                                    "test_item": "Qualification Testing",
                                },
                                sort_keys=True,
                            )
                        },
                        sort_keys=True,
                    ),
                )
            ]
        ),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service_with_updated_identity.preview("project-1")

    assert preview.status == "completed"
    assert preview.official_folder_path == result.official_folder_path
    assert any("current naming rule" in warning for warning in preview.warnings)
    assert not preview.blockers


def test_preview_uses_registered_ltr_when_project_no_is_missing(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        project=Project(
            project_id="project-1",
            project_no=None,
            product_name="Coolpower",
            requestor="Alice",
            status=ProjectStatus.CONFIRMED,
        ),
        ltr_repository=_LtrRepo(
            [
                LtrRecord(
                    ltr_id="ltr-1",
                    project_id="project-1",
                    ltr_number="DL-2025-11-074",
                    status=LtrStatus.REGISTERED,
                )
            ]
        ),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "ready"
    assert preview.dl_number == "DL-2025-11-074"
    assert preview.local_workspace_path == tmp_path / "workspaces" / "DL-2025-11-074"


def test_preview_prefers_registered_ltr_over_legacy_project_no(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        project=Project(
            project_id="project-1",
            project_no="1453402",
            product_name="Coolpower",
            requestor="Alice",
            status=ProjectStatus.CONFIRMED,
        ),
        ltr_repository=_LtrRepo(
            [
                LtrRecord(
                    ltr_id="ltr-1",
                    project_id="project-1",
                    ltr_number="DL-2025-11-074",
                    status=LtrStatus.REGISTERED,
                )
            ]
        ),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.dl_number == "DL-2025-11-074"
    assert preview.local_workspace_path == tmp_path / "workspaces" / "DL-2025-11-074"


def test_preview_uses_application_form_requested_testing_in_folder_name(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        forms=[
            ApplicationForm(
                form_id="form-1",
                project_id="project-1",
                form_no="E-3718",
                revision="H",
                requester="Alice",
                requested_testing="Thermal cycling and contact resistance",
            )
        ],
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.official_folder_path == (
        tmp_path
        / "workspaces"
        / "DL-2025-11-074"
        / "DL-2025-11-074 Coolpower Thermal cycling and contact resistance"
    )


def test_preview_uses_ltr_sample_description_and_test_item_in_folder_name(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        project=Project(
            project_id="project-1",
            project_no="1453402",
            product_name="Coolpower HDF 3.40mm pin",
            requestor="Alice",
            status=ProjectStatus.CONFIRMED,
        ),
        ltr_repository=_LtrRepo(
            [
                LtrRecord(
                    ltr_id="ltr-1",
                    project_id="project-1",
                    ltr_number="DL-2026-05-011",
                    status=LtrStatus.REGISTERED,
                    registered_on=date(2026, 5, 11),
                    notes=json.dumps(
                        {
                            "operator_note": json.dumps(
                                {
                                    "source": "new_project_setup_confirmation",
                                    "sample_description": "Stale LTR sample text",
                                    "test_item": "Qualification Testing",
                                },
                                sort_keys=True,
                            )
                        },
                        sort_keys=True,
                    ),
                )
            ]
        ),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.official_folder_path == (
        tmp_path
        / "workspaces"
        / "DL-2026-05-011"
        / "DL-2026-05-011 Coolpower HDF 3.40mm pin Qualification Testing"
    )


def test_foreign_project_manifest_is_a_recoverable_whole_workspace_conflict(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    manifest_dir = workspace / ".connlab"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(
        '{"schema_version":1,"project_id":"other","official_project_folder_path":"x"}',
        encoding="utf-8",
    )
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "conflict"
    assert "Workspace manifest does not match" in preview.blockers[0]
    assert preview.conflict_paths == (workspace,)
    assert preview.conflict_options == ()


def test_backup_rebuild_rejects_foreign_workspace_without_moving_anything(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    (template / "template.txt").write_text("new", encoding="utf-8")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    manifest_dir = workspace / ".connlab"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(
        '{"schema_version":1,"project_id":"other","official_project_folder_path":"x"}',
        encoding="utf-8",
    )
    (workspace / "legacy.txt").write_text("legacy", encoding="utf-8")
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    with pytest.raises(OfficialWorkspaceCreateError, match="manifest"):
        service.create("project-1", conflict_strategy="backup_and_recreate")

    assert (workspace / "legacy.txt").read_text(encoding="utf-8") == "legacy"
    assert json.loads((manifest_dir / "manifest.json").read_text(encoding="utf-8"))["project_id"] == "other"
    assert not list((tmp_path / "workspaces").glob("DL-2025-11-074 [0-9]*"))


def test_unreadable_manifest_remains_blocked_as_an_inconsistency(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    manifest_dir = workspace / ".connlab"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text("not-json", encoding="utf-8")
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "conflict"
    assert "cannot be read" in preview.blockers[0]
    assert preview.conflict_paths == (workspace,)
    assert preview.conflict_options == ()


def test_missing_stale_workspace_record_replans_under_current_project_root(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    current_root = tmp_path / "current-workspaces"
    current_root.mkdir()
    old_workspace = tmp_path / "old-workspaces" / "DL-2025-11-074"
    repository = _WorkspaceRepo()
    repository.saved = OfficialWorkspaceRecord(
        workspace_id="stale-workspace",
        project_id="project-1",
        dl_number="DL-2025-11-074",
        local_workspace_path=old_workspace,
        source_book_path=old_workspace / "Source Book",
        official_folder_path=(
            old_workspace / "DL-2025-11-074 Coolpower Qualification test"
        ),
        manifest_path=old_workspace / ".connlab" / "manifest.json",
        template_source_path=template,
        created_at="2026-06-01T00:00:00+00:00",
    )
    service = _service(
        tmp_path,
        repository=repository,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=current_root,
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "ready"
    assert not preview.blockers
    assert preview.local_workspace_path == current_root / "DL-2025-11-074"
    assert any("previous workspace record" in warning.lower() for warning in preview.warnings)

    result = service.create("project-1")

    assert result.record.local_workspace_path == current_root / "DL-2025-11-074"
    assert result.record.official_folder_path.is_dir()
    assert repository.saved == result.record


def test_unique_relocated_legacy_manifest_can_be_explicitly_linked(tmp_path: Path) -> None:
    root = tmp_path / "workspaces"
    workspace = root / "legacy-DL-2025-11-074"
    official_folder = workspace / "DL-2025-11-074 Original operator folder"
    (workspace / "Source Book").mkdir(parents=True)
    official_folder.mkdir()
    operator_file = official_folder / "operator-report.docx"
    operator_file.write_bytes(b"operator-owned")
    manifest = workspace / ".connlab" / "manifest.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({
        "project_id": "project-1", "dl_number": "DL-2025-11-074",
        "official_project_folder_path": "E:/OldMachine/DL-2025-11-074 Original operator folder",
    }), encoding="utf-8")
    repository = _WorkspaceRepo()
    service = _service(tmp_path, repository=repository, settings=OfficialWorkspaceSettings(
        root, None, None,
    ))

    preview = service.preview("project-1")
    assert preview.status == "adoptable"
    assert preview.local_workspace_path == workspace
    assert preview.official_folder_path == official_folder
    assert repository.saved is None
    linked = service.adopt_existing("project-1")
    assert linked.record.local_workspace_path == workspace
    assert operator_file.read_bytes() == b"operator-owned"


def test_closed_project_cannot_link_a_legacy_workspace(tmp_path: Path) -> None:
    root = tmp_path / "workspaces"
    workspace = root / "DL-2025-11-074"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    (workspace / "Source Book").mkdir(parents=True)
    official_folder.mkdir()
    repository = _WorkspaceRepo()
    service = _service(
        tmp_path,
        project=Project(
            project_id="project-1", project_no="DL-2025-11-074",
            product_name="Coolpower", requestor="Alice",
            lifecycle_state=ProjectLifecycleState.CLOSED,
        ),
        repository=repository,
        settings=OfficialWorkspaceSettings(root, None, None),
    )

    assert service.preview("project-1").status == "adoptable"
    with pytest.raises(ProjectLifecycleReadonlyError, match="closed"):
        service.adopt_existing("project-1")
    assert repository.saved is None
    assert not (workspace / ".connlab").exists()


def test_ambiguous_relocated_legacy_manifests_never_bind_automatically(tmp_path: Path) -> None:
    root = tmp_path / "workspaces"
    for name in ("legacy-A", "legacy-B"):
        workspace = root / name
        (workspace / "Source Book").mkdir(parents=True)
        official_folder = workspace / "DL-2025-11-074 Original operator folder"
        official_folder.mkdir()
        manifest = workspace / ".connlab" / "manifest.json"
        manifest.parent.mkdir()
        manifest.write_text(json.dumps({
            "project_id": "project-1", "dl_number": "DL-2025-11-074",
            "official_project_folder_path": str(official_folder),
        }), encoding="utf-8")
    repository = _WorkspaceRepo()
    service = _service(tmp_path, repository=repository, settings=OfficialWorkspaceSettings(
        root, None, None,
    ))

    preview = service.preview("project-1")
    assert preview.status == "blocked"
    assert "Multiple" in preview.blockers[0]
    with pytest.raises(OfficialWorkspaceCreateError):
        service.adopt_existing("project-1")
    assert repository.saved is None


@pytest.mark.parametrize("identity", [
    {"project_id": "another-project", "dl_number": "DL-2025-11-074"},
    {"project_id": "project-1", "dl_number": "DL-2024-01-001"},
    {"project_id": "project-1"},
])
def test_relocated_legacy_candidate_requires_project_and_dl_manifest_identity(
    tmp_path: Path, identity: dict[str, str]
) -> None:
    root = tmp_path / "workspaces"
    workspace = root / "legacy-DL-2025-11-074"
    official_folder = workspace / "DL-2025-11-074 Original operator folder"
    (workspace / "Source Book").mkdir(parents=True)
    official_folder.mkdir()
    manifest = workspace / ".connlab" / "manifest.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({
        **identity, "official_project_folder_path": str(official_folder),
    }), encoding="utf-8")
    template = _make_template(tmp_path / "template")
    service = _service(tmp_path, settings=OfficialWorkspaceSettings(root, template, None))

    preview = service.preview("project-1")
    assert preview.status == "ready"
    assert preview.local_workspace_path == root / "DL-2025-11-074"
    assert preview.local_workspace_path != workspace


@pytest.mark.parametrize(
    "escaped_component",
    ["workspace", "source_book", "official_folder", "manifest"],
)
def test_completed_record_rejects_paths_outside_configured_workspace_relationships(
    tmp_path: Path,
    escaped_component: str,
) -> None:
    template = _make_template(tmp_path / "template")
    root = tmp_path / "workspaces"
    root.mkdir()
    workspace = root / "DL-2025-11-074"
    source_book = workspace / "Source Book"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    manifest = workspace / ".connlab" / "manifest.json"
    if escaped_component == "workspace":
        workspace = tmp_path / "outside" / "DL-2025-11-074"
        source_book = workspace / "Source Book"
        official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
        manifest = workspace / ".connlab" / "manifest.json"
    elif escaped_component == "source_book":
        source_book = tmp_path / "outside-source"
    elif escaped_component == "official_folder":
        official_folder = tmp_path / "outside-official"
    elif escaped_component == "manifest":
        manifest = tmp_path / "outside-manifest.json"
    source_book.mkdir(parents=True)
    official_folder.mkdir(parents=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(
            {
                "project_id": "project-1",
                "dl_number": "DL-2025-11-074",
                "official_project_folder_path": str(official_folder),
            }
        ),
        encoding="utf-8",
    )
    repository = _WorkspaceRepo()
    repository.saved = OfficialWorkspaceRecord(
        workspace_id="retained",
        project_id="project-1",
        dl_number="DL-2025-11-074",
        local_workspace_path=workspace,
        source_book_path=source_book,
        official_folder_path=official_folder,
        manifest_path=manifest,
        template_source_path=template,
        created_at="2026-06-01T00:00:00+00:00",
    )
    service = _service(
        tmp_path,
        repository=repository,
        settings=OfficialWorkspaceSettings(root, template, None),
    )

    preview = service.preview("project-1")

    assert preview.status == "inconsistent"
    assert "workspace record" in preview.blockers[0].lower()


def test_completed_record_fails_closed_when_retained_path_is_redirected(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    root = tmp_path / "workspaces"
    root.mkdir()
    workspace = root / "legacy-DL-2025-11-074"
    source_book = workspace / "Source Book"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    manifest = workspace / ".connlab" / "manifest.json"
    source_book.mkdir(parents=True)
    official_folder.mkdir()
    manifest.parent.mkdir()
    manifest.write_text(
        json.dumps(
            {
                "project_id": "project-1",
                "official_project_folder_path": str(official_folder),
            }
        ),
        encoding="utf-8",
    )
    repository = _WorkspaceRepo()
    repository.saved = OfficialWorkspaceRecord(
        "retained",
        "project-1",
        "DL-2025-11-074",
        workspace,
        source_book,
        official_folder,
        manifest,
        template,
        "2026-06-01T00:00:00+00:00",
    )
    service = _service(
        tmp_path,
        repository=repository,
        manifest_gateway=_RedirectingManifestGateway(workspace),
        settings=OfficialWorkspaceSettings(root, template, None),
    )

    preview = service.preview("project-1")

    assert preview.status == "inconsistent"
    assert "symbolic link or junction" in preview.blockers[0]


def test_missing_recorded_official_folder_can_be_regenerated(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    source_book = workspace / "Source Book"
    source_book.mkdir(parents=True)
    old_missing_folder = workspace / "DL-2025-11-074 Coolpower Old test"
    repository = _WorkspaceRepo()
    repository.saved = OfficialWorkspaceRecord(
        workspace_id="workspace-1",
        project_id="project-1",
        dl_number="DL-2025-11-074",
        local_workspace_path=workspace,
        source_book_path=source_book,
        official_folder_path=old_missing_folder,
        manifest_path=workspace / ".connlab" / "manifest.json",
        template_source_path=template,
        created_at="2026-06-01T00:00:00+00:00",
    )
    service = _service(
        tmp_path,
        repository=repository,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "ready"
    assert not preview.blockers
    assert preview.official_folder_path == workspace / (
        "DL-2025-11-074 Coolpower Qualification test"
    )
    assert any("missing official project folder" in warning for warning in preview.warnings)
    with pytest.raises(OfficialWorkspaceCreateError, match="cannot be linked"):
        service.adopt_existing("project-1")

    result = service.create("project-1")

    assert result.official_folder_path == preview.official_folder_path
    assert result.official_folder_path.is_dir()
    assert repository.saved is not None
    assert repository.saved.official_folder_path == preview.official_folder_path


@pytest.mark.parametrize("foreign_manifest", [False, True])
def test_missing_recorded_folder_never_links_without_verified_existing_folder(
    tmp_path: Path, foreign_manifest: bool,
) -> None:
    template = _make_template(tmp_path / "template") if foreign_manifest else tmp_path / "unavailable-template"
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    (workspace / "Source Book").mkdir(parents=True)
    missing = workspace / "DL-2025-11-074 Coolpower Old test"
    manifest = workspace / ".connlab" / "manifest.json"
    if foreign_manifest:
        manifest.parent.mkdir()
        manifest.write_text(json.dumps({
            "project_id": "other-project", "dl_number": "DL-2025-11-074",
            "official_project_folder_path": str(missing),
        }), encoding="utf-8")
    original_manifest = manifest.read_bytes() if foreign_manifest else None
    repository = _WorkspaceRepo()
    repository.saved = OfficialWorkspaceRecord(
        "workspace-1", "project-1", "DL-2025-11-074", workspace,
        workspace / "Source Book", missing, manifest,
        template, "2026-06-01T00:00:00+00:00",
    )
    service = _service(tmp_path, repository=repository, settings=OfficialWorkspaceSettings(
        tmp_path / "workspaces", template, None,
    ))

    preview = service.preview("project-1")
    assert preview.status in {"blocked", "inconsistent", "conflict"}
    assert preview.status != "adoptable"
    with pytest.raises(OfficialWorkspaceCreateError):
        service.adopt_existing("project-1")
    with pytest.raises(OfficialWorkspaceCreateError):
        service.create("project-1")
    assert not missing.exists()
    assert (manifest.read_bytes() if foreign_manifest else None) == original_manifest


@pytest.mark.parametrize("candidate_count, foreign_manifest", [(1, False), (2, False), (1, True)])
def test_recorded_workspace_inner_folder_candidate_requires_manual_review(
    tmp_path: Path, candidate_count: int, foreign_manifest: bool,
) -> None:
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    (workspace / "Source Book").mkdir(parents=True)
    old_missing = workspace / "DL-2025-11-074 Coolpower Old test"
    renamed = workspace / "DL-2025-11-074 Coolpower Renamed test"
    renamed.mkdir()
    operator_file = renamed / "operator-owned.txt"
    operator_file.write_bytes(b"operator bytes")
    if candidate_count == 2:
        (workspace / "DL-2025-11-074 Another possible folder").mkdir()
    manifest = workspace / ".connlab" / "manifest.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({
        "project_id": "other-project" if foreign_manifest else "project-1",
        "dl_number": "DL-2025-11-074",
        "official_project_folder_path": str(old_missing),
    }), encoding="utf-8")
    original_manifest = manifest.read_bytes()
    repository = _WorkspaceRepo()
    repository.saved = OfficialWorkspaceRecord(
        "workspace-1", "project-1", "DL-2025-11-074", workspace,
        workspace / "Source Book", old_missing, manifest,
        tmp_path / "unavailable-template", "2026-06-01T00:00:00+00:00",
    )
    service = _service(tmp_path, repository=repository, settings=OfficialWorkspaceSettings(
        tmp_path / "workspaces", tmp_path / "unavailable-template", None,
    ))

    preview = service.preview("project-1")
    assert preview.status == ("conflict" if candidate_count == 2 else "inconsistent")
    if candidate_count == 2:
        assert "multiple active" in preview.blockers[0].lower()
        assert preview.conflict_options == ()
    elif not foreign_manifest:
        assert str(renamed) in preview.blockers[0]
        assert "manual review" in preview.blockers[0].lower()
    with pytest.raises(OfficialWorkspaceCreateError):
        service.adopt_existing("project-1")
    with pytest.raises(OfficialWorkspaceCreateError):
        service.create("project-1")
    assert manifest.read_bytes() == original_manifest
    assert repository.saved.official_folder_path == old_missing
    assert operator_file.read_bytes() == b"operator bytes"


def test_manifest_without_workspace_record_is_identity_only_adoptable(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    manifest_dir = workspace / ".connlab"
    official_folder.mkdir(parents=True)
    (workspace / "Source Book").mkdir()
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "project_id": "project-1",
                "official_project_folder_path": str(official_folder),
            }
        ),
        encoding="utf-8",
    )
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "adoptable"
    assert preview.blockers == tuple()


@pytest.mark.parametrize("payload", ["[]", '"manifest"', "7"])
def test_non_object_manifest_is_an_actionable_conflict(
    tmp_path: Path, payload: str
) -> None:
    root = tmp_path / "workspaces"
    workspace = root / "DL-2025-11-074"
    manifest = workspace / ".connlab" / "manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(payload, encoding="utf-8")
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(root, None, None),
    )

    preview = service.preview("project-1")

    assert preview.status == "conflict"
    assert "cannot be read" in preview.blockers[0]


def test_non_object_manifest_on_retained_record_is_inconsistent_not_an_exception(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    root = tmp_path / "workspaces"
    root.mkdir()
    repository = _WorkspaceRepo()
    service = _service(
        tmp_path,
        repository=repository,
        settings=OfficialWorkspaceSettings(root, template, None),
    )
    created = service.create("project-1")
    created.record.manifest_path.write_text("[]", encoding="utf-8")

    preview = service.preview("project-1")

    assert preview.status == "inconsistent"
    assert "cannot be read" in preview.blockers[0]


def test_portable_same_project_manifest_is_adoptable_under_current_configured_root(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    source_book = workspace / "Source Book"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    source_book.mkdir(parents=True)
    official_folder.mkdir()
    manifest = workspace / ".connlab" / "manifest.json"
    manifest.parent.mkdir()
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "project_id": "project-1",
                "dl_number": "DL-2025-11-074",
                "local_workspace_path": "E:/OldMachine/DL-2025-11-074",
                "source_book_path": "E:/OldMachine/DL-2025-11-074/Source Book",
                "official_project_folder_path": (
                    "E:/OldMachine/DL-2025-11-074/"
                    "DL-2025-11-074 Coolpower Qualification test"
                ),
                "template_source_path": "E:/OldMachine/template",
                "created_at": "2026-06-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "adoptable"
    assert preview.local_workspace_path == workspace
    assert preview.source_book_path == source_book
    assert preview.official_folder_path == official_folder
    assert not preview.blockers


def test_adopt_existing_only_rebinds_manifest_and_workspace_index(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    source_book = workspace / "Source Book"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    source_book.mkdir(parents=True)
    official_folder.mkdir()
    operator_file = official_folder / "operator-report.docx"
    operator_file.write_bytes(b"operator-owned")
    before = {
        path.relative_to(workspace): (path.is_dir(), path.stat().st_size, path.stat().st_mtime_ns)
        for path in (source_book, official_folder, operator_file)
    }
    repository = _WorkspaceRepo()
    service = _service(
        tmp_path,
        repository=repository,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    result = service.adopt_existing("project-1")

    after = {
        path.relative_to(workspace): (path.is_dir(), path.stat().st_size, path.stat().st_mtime_ns)
        for path in (source_book, official_folder, operator_file)
    }
    assert after == before
    assert operator_file.read_bytes() == b"operator-owned"
    assert repository.saved == result.record
    assert result.created_paths == (workspace / ".connlab" / "manifest.json",)
    assert not (official_folder / "template.txt").exists()
    assert not list(workspace.parent.glob("DL-2025-11-074 *"))
    assert service.preview("project-1").status == "completed"


def test_create_rejects_adoptable_folder_without_mutating_operator_tree(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    source_book = workspace / "Source Book"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    source_book.mkdir(parents=True)
    official_folder.mkdir()
    operator_file = official_folder / "operator-report.docx"
    operator_file.write_bytes(b"operator-owned")
    before = {
        path.relative_to(workspace): (path.is_dir(), path.stat().st_size, path.stat().st_mtime_ns)
        for path in workspace.rglob("*")
    }
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    with pytest.raises(OfficialWorkspaceCreateError, match="Link existing folder"):
        service.create("project-1")

    after = {
        path.relative_to(workspace): (path.is_dir(), path.stat().st_size, path.stat().st_mtime_ns)
        for path in workspace.rglob("*")
    }
    assert after == before
    assert operator_file.read_bytes() == b"operator-owned"
    assert not (workspace / ".connlab").exists()


def test_adoption_does_not_require_configured_template_to_be_available(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    source_book = workspace / "Source Book"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    source_book.mkdir(parents=True)
    official_folder.mkdir()
    operator_file = official_folder / "operator-report.docx"
    operator_file.write_bytes(b"operator-owned")
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=None,
            public_drive_root=None,
        ),
    )

    assert service.preview("project-1").status == "adoptable"
    result = service.adopt_existing("project-1")

    assert result.record.template_source_path == official_folder
    assert operator_file.read_bytes() == b"operator-owned"
    with pytest.raises(OfficialWorkspaceCreateError, match="configured project workspace root"):
        service.create("project-1", conflict_strategy="backup_and_recreate")
    assert operator_file.read_bytes() == b"operator-owned"


def test_missing_template_names_settings_action_without_authorizing_creation(
    tmp_path: Path,
) -> None:
    root = tmp_path / "workspaces"
    root.mkdir()
    missing_template = tmp_path / "unavailable-template"
    service = _service(tmp_path, settings=OfficialWorkspaceSettings(
        root, missing_template, None,
    ))

    preview = service.preview("project-1")
    assert preview.status == "blocked"
    assert str(missing_template) in preview.blockers[0]
    assert "Settings" in preview.blockers[0]
    assert "Project Folder Template" in preview.blockers[0]
    with pytest.raises(OfficialWorkspaceCreateError):
        service.create("project-1")
    assert not (root / "DL-2025-11-074").exists()


def test_rebuild_never_uses_another_project_operator_tree_as_retained_template(
    tmp_path: Path,
) -> None:
    root = tmp_path / "workspaces"
    current_workspace = root / "DL-2025-11-074"
    source_book = current_workspace / "Source Book"
    official_folder = current_workspace / "DL-2025-11-074 Coolpower Qualification test"
    source_book.mkdir(parents=True)
    official_folder.mkdir()
    (official_folder / "current-report.docx").write_bytes(b"current")
    other_project_folder = _make_template(
        root / "DL-2024-01-001" / "DL-2024-01-001 Other project"
    )
    other_operator_file = other_project_folder / "operator-report.docx"
    other_operator_file.write_bytes(b"other-project")
    manifest = current_workspace / ".connlab" / "manifest.json"
    manifest.parent.mkdir()
    manifest.write_text(
        json.dumps(
            {
                "project_id": "project-1",
                "dl_number": "DL-2025-11-074",
                "official_project_folder_path": str(official_folder),
                "template_source_path": str(other_project_folder),
            }
        ),
        encoding="utf-8",
    )
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=root,
            template_path=tmp_path / "unavailable-template",
            public_drive_root=None,
        ),
    )
    service.adopt_existing("project-1")

    with pytest.raises(OfficialWorkspaceCreateError, match="Template folder does not exist"):
        service.create("project-1", conflict_strategy="backup_and_recreate")

    assert other_operator_file.read_bytes() == b"other-project"
    assert (official_folder / "current-report.docx").read_bytes() == b"current"


def test_adoption_does_not_overwrite_a_different_folder_manifest_inserted_after_initial_check(
    tmp_path: Path,
) -> None:
    path = tmp_path / ".connlab" / "manifest.json"
    path.parent.mkdir(parents=True)
    current = OfficialWorkspaceManifest(
        schema_version=1,
        project_id="project-1",
        dl_number="DL-2025-11-074",
        local_workspace_path="D:/old/DL-2025-11-074",
        source_book_path="D:/old/DL-2025-11-074/Source Book",
        official_project_folder_path="D:/old/DL-2025-11-074/Official",
        template_source_path="D:/old/template",
        created_at="2026-06-01T00:00:00+00:00",
    )
    gateway = _InterveningManifestGateway()
    gateway.write(path, current)
    rebound = replace(
        current,
        local_workspace_path=str(tmp_path / "DL-2025-11-074"),
    )

    with pytest.raises(ValueError, match="reviewed official project folder"):
        gateway.write_adoption(path, rebound)

    preserved = json.loads(path.read_text(encoding="utf-8"))
    assert preserved["project_id"] == "project-1"
    assert preserved["official_project_folder_path"] == "D:/other/Unexpected Folder"


@pytest.mark.skipif(os.name != "nt", reason="Windows junction regression")
def test_adoption_preview_fails_closed_for_workspace_junction(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    root = tmp_path / "workspaces"
    root.mkdir()
    target = tmp_path / "outside-workspace"
    source_book = target / "Source Book"
    official_folder = target / "DL-2025-11-074 Coolpower Qualification test"
    source_book.mkdir(parents=True)
    official_folder.mkdir()
    workspace = root / "DL-2025-11-074"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(workspace), str(target)],
        check=False,
        capture_output=True,
        text=True,
    )
    if created.returncode != 0:
        pytest.skip(f"Junction creation unavailable: {created.stderr or created.stdout}")
    try:
        service = _service(
            tmp_path,
            settings=OfficialWorkspaceSettings(
                local_workspace_root=root,
                template_path=template,
                public_drive_root=None,
            ),
        )

        preview = service.preview("project-1")

        assert preview.status == "conflict"
        assert "symbolic link or junction" in preview.blockers[0]
        with pytest.raises(OfficialWorkspaceCreateError, match="cannot be linked"):
            service.adopt_existing("project-1")
    finally:
        workspace.rmdir()


@pytest.mark.skipif(os.name != "nt", reason="Windows file-lock regression")
def test_completed_identity_ignores_business_file_mutations_and_locks(tmp_path: Path) -> None:
    import ctypes
    from ctypes import wintypes

    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    repository = _WorkspaceRepo()
    service = _service(
        tmp_path,
        repository=repository,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )
    created = service.create("project-1")
    operator_file = created.official_folder_path / "operator-owned.docx"
    operator_file.write_bytes(b"first")
    operator_file.write_bytes(b"operator changed this file")

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    handle = kernel32.CreateFileW(str(operator_file), 0x80000000, 0, None, 3, 0, None)
    assert handle != wintypes.HANDLE(-1).value, ctypes.get_last_error()
    try:
        assert service.preview("project-1").status == "completed"
        assert service.adopt_existing("project-1").record == created.record
    finally:
        kernel32.CloseHandle(handle)


def test_failed_template_copy_cleans_temp_without_final_folder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    def fail_copytree(source: Path, target: Path) -> None:
        target.mkdir(parents=True)
        (target / "partial.txt").write_text("partial", encoding="utf-8")
        raise OSError("copy failed")

    monkeypatch.setattr(
        "backend.application.official_project_workspace_service._copytree_no_overwrite",
        fail_copytree,
    )

    with pytest.raises(OfficialWorkspaceCreateError, match="copy failed"):
        service.create("project-1")

    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    final_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    assert not final_folder.exists()
    assert not list((workspace / ".connlab" / "tmp").glob("*"))


@dataclass
class _ProjectRepo:
    project: Project

    def get(self, project_id: str) -> Project | None:
        return self.project if self.project.project_id == project_id else None


class _InterveningManifestGateway(OfficialWorkspaceManifestGateway):
    """Simulate another folder identity winning after the reviewed first read."""

    def __init__(self) -> None:
        self._intervene = True

    def read(self, path: Path) -> dict[str, object]:
        payload = super().read(path)
        if self._intervene:
            self._intervene = False
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project_id": "project-1",
                        "dl_number": "DL-2025-11-074",
                        "official_project_folder_path": "D:/other/Unexpected Folder",
                    }
                ),
                encoding="utf-8",
            )
        return payload


class _RedirectingManifestGateway(OfficialWorkspaceManifestGateway):
    def __init__(self, redirected: Path) -> None:
        self.redirected = redirected

    def first_redirected_path(self, *paths: Path) -> Path | None:
        return self.redirected if self.redirected in paths else None


class _WorkspaceRepo:
    def __init__(self) -> None:
        self.saved: OfficialWorkspaceRecord | None = None

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        return self.saved if self.saved and self.saved.project_id == project_id else None

    def save(self, record: OfficialWorkspaceRecord) -> OfficialWorkspaceRecord:
        self.saved = record
        return record

    def publish_relocation(
        self, record: OfficialWorkspaceRecord, *, source: Path, target: Path,
        operation_id: str, expected_identity: list[int],
    ) -> OfficialWorkspaceRecord:
        return self.save(record)

    def preflight_placed_materials(
        self, record: OfficialWorkspaceRecord, *, source: Path,
    ) -> None:
        pass


class _LtrRepo:
    def __init__(self, records: list[LtrRecord] | None = None) -> None:
        self._records = records or []

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        return [record for record in self._records if record.project_id == project_id]


class _ApplicationFormRepo:
    def __init__(self, forms: list[ApplicationForm] | None = None) -> None:
        self._forms = forms or []

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        return [form for form in self._forms if form.project_id == project_id]


def _service(
    tmp_path: Path,
    *,
    project: Project | None = None,
    repository: _WorkspaceRepo | None = None,
    ltr_repository: _LtrRepo | None = None,
    forms: list[ApplicationForm] | None = None,
    basic_information_reader=None,
    manifest_gateway: OfficialWorkspaceManifestGateway | None = None,
    settings: OfficialWorkspaceSettings,
) -> OfficialProjectWorkspaceService:
    return OfficialProjectWorkspaceService(
        project_repository=_ProjectRepo(
            project
            or Project(
                project_id="project-1",
                project_no="DL-2025-11-074",
                product_name="Coolpower",
                requestor="Alice",
                status=ProjectStatus.CONFIRMED,
            )
        ),
        workspace_repository=repository or _WorkspaceRepo(),
        ltr_repository=ltr_repository or _default_ltr_repo(),
        application_form_repository=_ApplicationFormRepo(forms),
        basic_information_reader=basic_information_reader,
        manifest_gateway=manifest_gateway,
        settings=settings,
    )


def _default_ltr_repo() -> _LtrRepo:
    return _LtrRepo(
        [
            LtrRecord(
                ltr_id="ltr-1",
                project_id="project-1",
                ltr_number="DL-2025-11-074",
                status=LtrStatus.REGISTERED,
                registered_on=date(2026, 5, 11),
                notes=None,
            )
        ]
    )


def _make_template(path: Path) -> Path:
    (path / "E-mail").mkdir(parents=True)
    (path / "Submitted Material").mkdir()
    (path / "Photos").mkdir()
    (path / "Test results" / "Final Examination").mkdir(parents=True)
    return path
