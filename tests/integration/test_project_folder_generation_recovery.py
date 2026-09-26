"""New-process recovery through the real runner, SQLite and fake form generator."""

from pathlib import Path
import json
import os
import runpy
import subprocess
import sys
import shutil
import stat
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine

from backend.api import dependencies as deps
from backend.api.project_folder_generation_composition import ProjectFolderGenerationRunner
from backend.domain import Project, ProjectStatus, FileAsset, FileAssetType, LtrRecord, LtrStatus
from backend.domain import ExternalResource, ExternalResourceType
from backend.application.official_project_workspace_service import OfficialWorkspacePreview, OfficialWorkspaceRecord
from backend.application.project_basic_information_service import ConfirmProjectBasicInformationCommand
from backend.application.project_folder_generation_service import ProjectFolderGenerationService, ProjectFolderInUseError
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.files.recoverable_workspace_publisher import RecoverableWorkspacePublisher
from backend.infrastructure.official_workspace_manifest import (
    OfficialWorkspaceManifest, OfficialWorkspaceManifestGateway, stable_folder_identity,
)
from backend.infrastructure.storage.database import Base, create_session_factory
from backend.infrastructure.storage.project_schedule_schema_migration import bootstrap_project_schedule_schema
from backend.shared.config import Settings
from backend.application.project_application_form_write_back_service import ProjectApplicationFormWriteBackService
from backend.infrastructure.files.project_folder_required_forms_gateway import ProjectFolderRequiredFormsFileGateway


def _settings(root):
    return Settings(data_dir=root / "data", projects_dir=root / "projects", templates_dir=root / "templates",
                    database_path=root / "fixture.sqlite")


def _archive_recreate_preview(tmp_path):
    workspace = tmp_path / "projects" / "DL-001"
    old, new = workspace / "DL-001 Original", workspace / "DL-001 Confirmed"
    old.mkdir(parents=True)
    (old / "operator.txt").write_text("keep", encoding="utf-8")
    (workspace / "Source Book").mkdir()
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new", encoding="utf-8")
    manifest_path = workspace / ".connlab" / "manifest.json"
    OfficialWorkspaceManifestGateway().write_adoption(manifest_path, OfficialWorkspaceManifest(
        1, "P1", "DL-001", str(workspace), str(workspace / "Source Book"),
        str(old), str(template), "2026-09-25T00:00:00+00:00", stable_folder_identity(old),
    ))
    preview = OfficialWorkspacePreview(
        project_id="P1", dl_number="DL-001", local_workspace_root=workspace.parent,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=new, manifest_path=manifest_path,
        template_root_mode="template_root", status="completed", blockers=(), warnings=(),
        planned_paths=(), conflict_paths=(old,),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("P1", "backup_and_recreate", "context")
    state["archive_source_identity_only"] = True
    journal.save(state)
    return preview, journal, state, old, new


@pytest.mark.parametrize("stage_change", ["empty", "altered"])
def test_recovery_rejects_changed_stage_before_archive_side_effects(tmp_path, monkeypatch, stage_change):
    preview, journal, state, old, new = _archive_recreate_preview(tmp_path)
    original_save = journal.save

    def interrupt_after_checkpoint(saved_state):
        original_save(saved_state)
        if saved_state["effects"].get("workspace"):
            raise OSError("simulated interruption after durable checkpoint")

    with monkeypatch.context() as patch:
        patch.setattr(journal, "save", interrupt_after_checkpoint)
        with pytest.raises(OSError, match="simulated interruption"):
            RecoverableWorkspacePublisher(journal, state).create(
                preview, "backup_and_recreate", SimpleNamespace(save=lambda record: record),
            )

    effect = journal.read("P1")["effects"]["workspace"]
    staged_file = Path(effect["stage"]) / "template.txt"
    if stage_change == "empty":
        staged_file.unlink()
    else:
        staged_file.write_text("changed", encoding="utf-8")

    with pytest.raises(ValueError, match="stage changed"):
        RecoverableWorkspacePublisher(journal, journal.read("P1")).recover(
            SimpleNamespace(save=lambda record: record)
        )

    assert (old / "operator.txt").read_text(encoding="utf-8") == "keep"
    assert not (preview.local_workspace_path / "History").exists()
    assert not Path(effect["backup"]).exists()
    assert not new.exists()


def test_partial_stage_cleanup_does_not_retain_corrupt_checkpoint(tmp_path, monkeypatch):
    preview, journal, state, old, new = _archive_recreate_preview(tmp_path)
    real_rename = Path.rename
    orphan_stages = []

    def deny_old_folder_move(path, target):
        if path == old:
            raise PermissionError("simulated WinError 5")
        return real_rename(path, target)

    def partially_delete_stage(path):
        orphan_stages.append(Path(path))
        (Path(path) / "template.txt").unlink()
        raise PermissionError("simulated partial stage cleanup")

    with monkeypatch.context() as patch:
        patch.setattr(Path, "rename", deny_old_folder_move)
        patch.setattr(shutil, "rmtree", partially_delete_stage)
        with pytest.raises(ProjectFolderInUseError, match="DL-001 Original"):
            RecoverableWorkspacePublisher(journal, state).create(
                preview, "backup_and_recreate", SimpleNamespace(save=lambda record: record),
            )

    assert "workspace" not in state["effects"]
    assert "workspace" not in journal.read("P1")["effects"]
    assert (old / "operator.txt").read_text(encoding="utf-8") == "keep"
    assert not new.exists()
    assert len(orphan_stages) == 1
    assert orphan_stages[0].is_dir()
    assert not (orphan_stages[0] / "template.txt").exists()

    retry_state = journal.create("P1", "backup_and_recreate", "context")
    retry_state["archive_source_identity_only"] = True
    journal.save(retry_state)
    result = RecoverableWorkspacePublisher(journal, retry_state).create(
        preview, "backup_and_recreate", SimpleNamespace(save=lambda record: record),
    )

    archives = list((preview.local_workspace_path / "History" / "Folders").glob("DL-001 Original *"))
    assert len(archives) == 1
    assert (archives[0] / "operator.txt").read_text(encoding="utf-8") == "keep"
    assert (result.official_folder_path / "template.txt").read_text(encoding="utf-8") == "new"
    assert orphan_stages[0].is_dir()


def test_recoverable_backup_archives_only_active_ltr_child_under_history(tmp_path):
    workspace = tmp_path / "projects" / "DL-001"
    official = workspace / "DL-001 Original"
    official.mkdir(parents=True)
    (workspace / "Source Book").mkdir()
    (workspace / "History").mkdir()
    (workspace / "History" / "existing.txt").write_text("keep", encoding="utf-8")
    (official / "operator.txt").write_text("keep", encoding="utf-8")
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new", encoding="utf-8")
    preview = OfficialWorkspacePreview(
        project_id="P1", dl_number="DL-001", local_workspace_root=workspace.parent,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=official,
        manifest_path=workspace / ".connlab" / "manifest.json",
        template_root_mode="template_root", status="completed", blockers=(), warnings=(),
        planned_paths=(), conflict_paths=(official,),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("P1", "backup_and_recreate", "fixture")

    class Repository:
        def save(self, record):
            return record

    result = RecoverableWorkspacePublisher(journal, state).create(
        preview, "backup_and_recreate", Repository()
    )

    archives = list((workspace / "History" / "Folders").glob("DL-001 Original [0-9]*"))
    assert len(archives) == 1
    assert (archives[0] / "operator.txt").read_text(encoding="utf-8") == "keep"
    assert (workspace / "History" / "existing.txt").read_text(encoding="utf-8") == "keep"
    assert (result.official_folder_path / "template.txt").read_text(encoding="utf-8") == "new"
    assert json.loads(result.record.manifest_path.read_text(encoding="utf-8"))[
        "official_folder_identity"
    ] == [result.official_folder_path.stat().st_dev, result.official_folder_path.stat().st_ino]


@pytest.mark.parametrize("ltr_workspace_name", ["DL-001", "legacy-DL-001"])
def test_rebuild_archives_changed_old_tree_without_reading_it_and_uses_confirmed_name(tmp_path, monkeypatch, ltr_workspace_name):
    workspace = tmp_path / "projects" / ltr_workspace_name
    old, new = workspace / "DL-001 Original", workspace / "DL-001 Confirmed Description"
    (old / "arbitrary operator directory").mkdir(parents=True)
    (old / "arbitrary operator directory" / "updated.docx").write_bytes(b"operator-edited")
    (workspace / "Source Book").mkdir()
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new", encoding="utf-8")
    manifest_path = workspace / ".connlab" / "manifest.json"
    OfficialWorkspaceManifestGateway().write_adoption(manifest_path, OfficialWorkspaceManifest(
        1, "P1", "DL-001", str(workspace), str(workspace / "Source Book"),
        str(old), str(template), "2026-09-25T00:00:00+00:00", stable_folder_identity(old),
    ))
    preview = OfficialWorkspacePreview(
        project_id="P1", dl_number="DL-001", local_workspace_root=workspace.parent,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=new,
        manifest_path=manifest_path,
        template_root_mode="template_root", status="completed", blockers=(), warnings=(),
        planned_paths=(), conflict_paths=(old,),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("P1", "backup_and_recreate", "context")
    state["archive_source_identity_only"] = True
    journal.save(state)
    from backend.infrastructure.files import recoverable_workspace_publisher as module
    real_tree_hash = module.tree_hash

    def reject_old_tree(path):
        if path == old or path.parent == old:
            raise PermissionError("old business files must not be inspected")
        return real_tree_hash(path)

    monkeypatch.setattr(module, "tree_hash", reject_old_tree)
    real_rglob = Path.rglob

    def reject_old_descendant_scan(path, pattern):
        if path == old:
            raise AssertionError("archive must not inspect old subfolders or files")
        return real_rglob(path, pattern)

    monkeypatch.setattr(Path, "rglob", reject_old_descendant_scan)
    def operator_updates_after_review():
        (old / "arbitrary operator directory" / "updated.docx").write_bytes(b"second edit")

    result = RecoverableWorkspacePublisher(
        journal, state, verify_initial_preview=operator_updates_after_review,
    ).create(
        preview, "backup_and_recreate", SimpleNamespace(save=lambda record: record)
    )

    archived = Path(state["effects"]["workspace"]["backup"])
    assert result.official_folder_path == new
    assert (archived / "arbitrary operator directory" / "updated.docx").read_bytes() == b"second edit"
    assert not (new / "arbitrary operator directory").exists()
    assert (new / "template.txt").read_text(encoding="utf-8") == "new"


def test_rebuild_never_publishes_outside_indexed_ltr_workspace(tmp_path):
    workspace = tmp_path / "legacy" / "DL-001"
    old = workspace / "DL-001 Original"
    old.mkdir(parents=True)
    (old / "operator.txt").write_text("keep", encoding="utf-8")
    (workspace / "Source Book").mkdir()
    current_workspace = tmp_path / "current" / "DL-001"
    current_workspace.mkdir(parents=True)
    foreign_target = current_workspace / "DL-001 Confirmed"
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new", encoding="utf-8")
    preview = OfficialWorkspacePreview(
        project_id="P1", dl_number="DL-001", local_workspace_root=workspace.parent,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=foreign_target,
        manifest_path=workspace / ".connlab" / "manifest.json",
        template_root_mode="template_root", status="completed", blockers=(), warnings=(),
        planned_paths=(), conflict_paths=(old,),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("P1", "backup_and_recreate", "context")
    state["archive_source_identity_only"] = True
    journal.save(state)

    with pytest.raises(ValueError, match="indexed LTR workspace"):
        RecoverableWorkspacePublisher(journal, state).create(
            preview, "backup_and_recreate", SimpleNamespace(save=lambda record: record),
        )

    assert (old / "operator.txt").read_text(encoding="utf-8") == "keep"
    assert not foreign_target.exists()
    assert not (workspace / "History" / "Folders").exists()


@pytest.mark.parametrize("change", ["replaced_source", "removed_manifest"])
def test_rebuild_rejects_changed_manifest_or_source_after_review(tmp_path, change):
    workspace = tmp_path / "projects" / "DL-001"
    old = workspace / "DL-001 Original"
    old.mkdir(parents=True)
    (old / "operator.txt").write_text("original", encoding="utf-8")
    (workspace / "Source Book").mkdir()
    manifest_path = workspace / ".connlab" / "manifest.json"
    OfficialWorkspaceManifestGateway().write_adoption(manifest_path, OfficialWorkspaceManifest(
        1, "P1", "DL-001", str(workspace), str(workspace / "Source Book"),
        str(old), str(tmp_path / "template"), "2026-09-25T00:00:00+00:00",
        stable_folder_identity(old),
    ))
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new", encoding="utf-8")
    preview = OfficialWorkspacePreview(
        project_id="P1", dl_number="DL-001", local_workspace_root=workspace.parent,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=workspace / "DL-001 Confirmed",
        manifest_path=manifest_path, template_root_mode="template_root", status="completed",
        blockers=(), warnings=(), planned_paths=(), conflict_paths=(old,),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("P1", "backup_and_recreate", "context")
    state["archive_source_identity_only"] = True
    journal.save(state)

    def replace_source_after_review():
        if change == "removed_manifest":
            manifest_path.unlink()
        else:
            old.rename(tmp_path / "detached-original")
            old.mkdir()
            (old / "operator.txt").write_text("replacement", encoding="utf-8")

    with pytest.raises(ValueError, match="identity"):
        RecoverableWorkspacePublisher(
            journal, state, verify_initial_preview=replace_source_after_review,
        ).create(preview, "backup_and_recreate", SimpleNamespace(save=lambda record: record))

    assert (old / "operator.txt").read_text(encoding="utf-8") == (
        "original" if change == "removed_manifest" else "replacement"
    )
    assert not (workspace / "History" / "Folders").exists()
    assert not (workspace / "DL-001 Confirmed").exists()


def test_recovery_blocks_new_active_sibling_after_old_folder_was_archived(tmp_path, monkeypatch):
    workspace = tmp_path / "projects" / "DL-001"
    old, new = workspace / "DL-001 Original", workspace / "DL-001 Confirmed"
    old.mkdir(parents=True)
    (old / "operator.txt").write_text("old content", encoding="utf-8")
    (workspace / "Source Book").mkdir()
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new content", encoding="utf-8")
    manifest_path = workspace / ".connlab" / "manifest.json"
    OfficialWorkspaceManifestGateway().write_adoption(manifest_path, OfficialWorkspaceManifest(
        1, "P1", "DL-001", str(workspace), str(workspace / "Source Book"),
        str(old), str(template), "2026-09-25T00:00:00+00:00", stable_folder_identity(old),
    ))
    preview = OfficialWorkspacePreview(
        project_id="P1", dl_number="DL-001", local_workspace_root=workspace.parent,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=new,
        manifest_path=manifest_path,
        template_root_mode="template_root", status="completed", blockers=(), warnings=(),
        planned_paths=(), conflict_paths=(old,),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("P1", "backup_and_recreate", "context")
    state["archive_source_identity_only"] = True
    journal.save(state)
    publisher = RecoverableWorkspacePublisher(journal, state)
    real_rename = Path.rename
    interrupted = False

    def interrupt_after_archive(path, target):
        nonlocal interrupted
        if path == Path(state["effects"]["workspace"]["stage"]) and target == new and not interrupted:
            interrupted = True
            raise OSError("simulated process interruption before publishing the new folder")
        return real_rename(path, target)

    monkeypatch.setattr(Path, "rename", interrupt_after_archive)
    with pytest.raises(OSError, match="simulated process interruption"):
        publisher.create(preview, "backup_and_recreate", SimpleNamespace(save=lambda record: record))
    monkeypatch.setattr(Path, "rename", real_rename)
    archived = Path(state["effects"]["workspace"]["backup"])
    assert (archived / "operator.txt").read_text(encoding="utf-8") == "old content"
    sibling = workspace / "DL-001 Unexpected sibling"
    sibling.mkdir()

    with pytest.raises(ValueError, match="active LTR folder"):
        publisher.recover(SimpleNamespace(save=lambda record: record))

    assert sibling.is_dir()
    assert (archived / "operator.txt").read_text(encoding="utf-8") == "old content"
    assert not new.exists()


def test_recovery_blocks_new_active_sibling_after_new_folder_was_published(tmp_path):
    workspace = tmp_path / "projects" / "DL-001"
    old, new = workspace / "DL-001 Original", workspace / "DL-001 Confirmed"
    old.mkdir(parents=True)
    (old / "operator.txt").write_text("old content", encoding="utf-8")
    (workspace / "Source Book").mkdir()
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new content", encoding="utf-8")
    manifest_path = workspace / ".connlab" / "manifest.json"
    OfficialWorkspaceManifestGateway().write_adoption(manifest_path, OfficialWorkspaceManifest(
        1, "P1", "DL-001", str(workspace), str(workspace / "Source Book"),
        str(old), str(template), "2026-09-25T00:00:00+00:00", stable_folder_identity(old),
    ))
    preview = OfficialWorkspacePreview(
        project_id="P1", dl_number="DL-001", local_workspace_root=workspace.parent,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=new, manifest_path=manifest_path,
        template_root_mode="template_root", status="completed", blockers=(), warnings=(),
        planned_paths=(), conflict_paths=(old,),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("P1", "backup_and_recreate", "context")
    state["archive_source_identity_only"] = True
    journal.save(state)

    class Repository:
        def __init__(self):
            self.fail_once = True

        def save(self, record):
            if self.fail_once:
                self.fail_once = False
                raise OSError("simulated index write outage")
            return record

    repository = Repository()
    publisher = RecoverableWorkspacePublisher(journal, state)
    with pytest.raises(OSError, match="simulated index write outage"):
        publisher.create(preview, "backup_and_recreate", repository)
    archived = Path(state["effects"]["workspace"]["backup"])
    assert (archived / "operator.txt").read_text(encoding="utf-8") == "old content"
    assert (new / "template.txt").read_text(encoding="utf-8") == "new content"
    sibling = workspace / "DL-001 Unexpected sibling"
    sibling.mkdir()

    with pytest.raises(ValueError, match="active LTR folder"):
        publisher.recover(repository)

    assert sibling.is_dir()
    assert (archived / "operator.txt").read_text(encoding="utf-8") == "old content"


@pytest.mark.parametrize("archived_asset_type", [
    None, FileAssetType.APPLICATION_FORM, FileAssetType.OTHER, FileAssetType.LTR,
])
def test_runner_rebuild_uses_latest_confirmed_name_and_never_copies_old_business_tree(tmp_path, archived_asset_type):
    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    bootstrap_project_schedule_schema(engine)
    sessions = create_session_factory(engine)
    template = tmp_path / "template"
    for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
        (template / name).mkdir(parents=True)
    (template / "template.txt").write_text("template", encoding="utf-8")
    root = tmp_path / "output"
    root.mkdir()
    workspace = root / "DL-001"
    old = workspace / "DL-001 Original Qualification Testing"
    (old / "operator subfolder").mkdir(parents=True)
    (old / "operator subfolder" / "changed.docx").write_bytes(b"keep in history")
    (workspace / "Source Book").mkdir()
    manifest_path = workspace / ".connlab" / "manifest.json"
    record = OfficialWorkspaceRecord(
        "workspace-1", "P1", "DL-001", workspace, workspace / "Source Book",
        old, manifest_path, template, "2026-09-25T00:00:00+00:00",
    )
    OfficialWorkspaceManifestGateway().write_adoption(manifest_path, OfficialWorkspaceManifest(
        1, "P1", "DL-001", str(workspace), str(workspace / "Source Book"),
        str(old), str(template), record.created_at, stable_folder_identity(old),
    ))
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(
            project_id="P1", project_no="DL-001", product_name="Fallback",
            requestor="Test", status=ProjectStatus.DRAFT,
        ))
        deps.LtrRecordRepository(session).create(LtrRecord("ltr", "P1", "DL-001", LtrStatus.REGISTERED))
        resources = deps.ExternalResourceRepository(session)
        resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, root))
        resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
        deps.ProjectOfficialWorkspaceRepository(session).save(record)
        if archived_asset_type is not None:
            deps.FileAssetRepository(session).create(FileAsset(
                "source", "P1", archived_asset_type,
                old / "operator subfolder" / "changed.docx",
                original_name="changed.docx",
                source_role="selected_application_form" if archived_asset_type == FileAssetType.APPLICATION_FORM else None,
            ))
        deps.get_project_basic_information_service(session).confirm(ConfirmProjectBasicInformationCommand(
            project_id="P1", confirmed_by="operator", values={
                "dl_number": "DL-001", "project_type": "NPD", "product_description": "Confirmed Product",
                "test_item": "Qualification Testing", "tests_to_be_performed": "Qualification Testing",
                "requested_by": "Test", "project_leader": "Engineer", "lab_performing_tests": "Dongguan",
            },
        ))
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    runner.context = lambda _project_id: "confirmed authority"
    runner.preview_context_matches = lambda *_args, **_kwargs: True
    try:
        actual_preview = runner.preview("P1", "backup_rebuild")
        preview = actual_preview["workspace_preview"]
        assert preview["conflict_paths"] == [str(old)]
        assert preview["official_project_folder_path"] == str(workspace / "DL-001 Confirmed Product Qualification Testing")
        if archived_asset_type is not None:
            assert any("inside the folder being archived" in item for item in actual_preview["start_blockers"])
            with pytest.raises(ValueError, match="inside the folder being archived"):
                runner.service().start(
                    "P1", "backup_and_recreate", actual_preview["expected_context"], "reviewed-archive",
                )
            assert old.is_dir()
            return
        relocation_journal = GenerationJournal(settings.data_dir / "official_folder_relocation")
        pending = relocation_journal.create("P1", "rename_to_confirmed", "old reviewed name")
        pending["effects"]["relocation"] = {
            "source": str(old), "target": str(workspace / "DL-001 Old target"),
            "suggested": str(workspace / "DL-001 Old target"),
            "directory_identity": stable_folder_identity(old), "record": record,
        }
        relocation_journal.save(pending)
        runner.preview = lambda _project_id, _intent="create": {
            "expected_context": actual_preview["expected_context"],
            "start_blockers": [], "review_conflicts": [],
            "workspace_preview": {"status": "completed", "conflict_paths": [str(old)]},
        }
        service = runner.service()
        queued = []
        service.dispatch = queued.append
        started = service.start("P1", "backup_and_recreate", actual_preview["expected_context"], "reviewed-archive")
        assert started["status"] == "queued"
        assert relocation_journal.read("P1")["status"] == "completed"
        state = runner.journal.read("P1")
        runner.run_step(state, "workspace")
        with sessions() as session:
            updated = deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1")
        assert updated.official_folder_path == workspace / "DL-001 Confirmed Product Qualification Testing"
        archived = next((workspace / "History" / "Folders").glob("DL-001 Original Qualification Testing *"))
        assert (archived / "operator subfolder" / "changed.docx").read_bytes() == b"keep in history"
        assert not (updated.official_folder_path / "operator subfolder").exists()
        assert (updated.official_folder_path / "template.txt").read_text(encoding="utf-8") == "template"
    finally:
        runner.pool.shutdown()
        engine.dispose()


def test_resume_recovery_after_archived_source_move_uses_saved_workspace_effect(tmp_path):
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("P1", "backup_and_recreate", "confirmed inputs")
    state.update(status="blocked", preview_context="pre-move review", preview_context_version=2)
    state["effects"]["workspace"] = {"step": "workspace", "type": "workspace"}
    journal.save(state)
    queued = []
    service = ProjectFolderGenerationService(
        journal, lambda _project_id: "confirmed inputs", lambda *_args: None,
        queued.append, preview=lambda *_args: {"expected_context": "post-move review"},
    )

    resumed = service.resume("P1", state["operation_id"])

    assert resumed["status"] == "queued"
    assert len(queued) == 1


def test_legacy_pre_effect_rebuild_resume_keeps_original_folder_target(tmp_path):
    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    bootstrap_project_schedule_schema(engine)
    sessions = create_session_factory(engine)
    template = tmp_path / "template"
    for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
        (template / name).mkdir(parents=True)
    (template / "template.txt").write_text("template-only", encoding="utf-8")
    root = tmp_path / "output"
    root.mkdir()
    workspace = root / "DL-001"
    old = workspace / "DL-001 Original"
    old.mkdir(parents=True)
    (old / "operator.txt").write_text("keep in History", encoding="utf-8")
    (workspace / "Source Book").mkdir()
    manifest_path = workspace / ".connlab" / "manifest.json"
    record = OfficialWorkspaceRecord(
        "workspace-1", "P1", "DL-001", workspace, workspace / "Source Book",
        old, manifest_path, template, "2026-09-25T00:00:00+00:00",
    )
    OfficialWorkspaceManifestGateway().write_adoption(manifest_path, OfficialWorkspaceManifest(
        1, "P1", "DL-001", str(workspace), str(workspace / "Source Book"),
        str(old), str(template), record.created_at, stable_folder_identity(old),
    ))
    with sessions() as session:
        deps.ProjectRepository(session).create(Project("P1", "DL-001", "Fallback", "Test", ProjectStatus.DRAFT))
        deps.LtrRecordRepository(session).create(LtrRecord("ltr", "P1", "DL-001", LtrStatus.REGISTERED))
        resources = deps.ExternalResourceRepository(session)
        resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, root))
        resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
        deps.ProjectOfficialWorkspaceRepository(session).save(record)
        deps.get_project_basic_information_service(session).confirm(ConfirmProjectBasicInformationCommand(
            project_id="P1", confirmed_by="operator", values={
                "dl_number": "DL-001", "project_type": "NPD", "product_description": "Confirmed Product",
                "test_item": "Qualification Testing", "tests_to_be_performed": "Qualification Testing",
                "requested_by": "Test", "project_leader": "Engineer", "lab_performing_tests": "Dongguan",
            },
        ))
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    runner.context = lambda _project_id: "approved historical inputs"
    try:
        state = runner.journal.create("P1", "backup_and_recreate", "approved historical inputs")
        historical_preview = runner.preview("P1", "backup_rebuild")
        state.update(status="blocked", preview_context=historical_preview["legacy_expected_context"])
        runner.journal.save(state)
        queued = []
        service = runner.service()
        service.dispatch = queued.append

        resumed = service.resume("P1", state["operation_id"])
        assert resumed["status"] == "queued"
        assert len(queued) == 1
        runner.run_step(runner.journal.read("P1"), "workspace")

        with sessions() as session:
            rebuilt = deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1")
        assert rebuilt.official_folder_path == old
        assert (old / "template.txt").read_text(encoding="utf-8") == "template-only"
        assert not (old / "operator.txt").exists()
        assert not (workspace / "DL-001 Confirmed Product Qualification Testing").exists()
        archived = next((workspace / "History" / "Folders").glob("DL-001 Original *"))
        assert (archived / "operator.txt").read_text(encoding="utf-8") == "keep in History"
    finally:
        runner.pool.shutdown()
        engine.dispose()


@pytest.mark.parametrize("legacy_manifest", [False, True])
def test_runner_update_in_place_reuses_verified_custom_folder_without_rebuilding(tmp_path, legacy_manifest):
    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    template = tmp_path / "template"
    for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
        (template / name).mkdir(parents=True)
    (template / "new-template-file.txt").write_text("new", encoding="utf-8")
    output = tmp_path / "output"
    output.mkdir()
    workspace = output / "DL-001"
    custom = workspace / "DL-001 Operator Custom"
    custom.mkdir(parents=True)
    (workspace / "Source Book").mkdir()
    operator_file = custom / "operator.txt"
    operator_file.write_text("keep", encoding="utf-8")
    manifest_path = workspace / ".connlab" / "manifest.json"
    record = OfficialWorkspaceRecord(
        "workspace-1", "P1", "DL-001", workspace, workspace / "Source Book",
        custom, manifest_path, template, "2026-09-25T00:00:00+00:00",
    )
    OfficialWorkspaceManifestGateway().write_adoption(manifest_path, OfficialWorkspaceManifest(
        1, "P1", "DL-001", str(workspace), str(workspace / "Source Book"),
        str(custom), str(template), record.created_at,
        None if legacy_manifest else stable_folder_identity(custom),
        "DL-001 Connector Qualification Testing",
    ))
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(
            project_id="P1", project_no="DL-001", product_name="Connector",
            requestor="Test", status=ProjectStatus.DRAFT,
        ))
        deps.LtrRecordRepository(session).create(LtrRecord(
            "ltr", "P1", "DL-001", LtrStatus.REGISTERED,
        ))
        resources = deps.ExternalResourceRepository(session)
        resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, output))
        resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
        deps.ProjectOfficialWorkspaceRepository(session).save(record)
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    runner.context = lambda _project_id: "fixture"
    runner.preview_context_matches = lambda *_args, **_kwargs: True
    state = runner.journal.create("P1", "update_in_place", "fixture")
    state.update(preview_context="fixture", preview_context_version=2)
    runner.journal.save(state)
    try:
        runner.run_step(state, "workspace")
        with sessions() as session:
            retained = deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1")
        assert retained.official_folder_path == custom
        assert operator_file.read_text(encoding="utf-8") == "keep"
        assert not (custom / "new-template-file.txt").exists()
        assert not (workspace / "History").exists()
        assert state["workspace_directories"]["official_folder_path"]["identity"] == stable_folder_identity(custom)
    finally:
        runner.pool.shutdown()
        engine.dispose()


@pytest.mark.skipif(os.name != "nt", reason="Windows readonly deletion semantics")
@pytest.mark.parametrize("input_change", ["first_denial", "after_chmod", None])
def test_runner_revalidates_real_inputs_around_readonly_cleanup(tmp_path, monkeypatch, input_change):
    # Runner.context loads schedule storage lazily; register it before fixture DDL.
    from backend.infrastructure.storage import models_project_schedule  # noqa: F401

    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    source = tmp_path / "source.txt"
    source.write_text("approved input", encoding="utf-8")
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(
            project_id="P1", project_no="DL-001", product_name="Fixture",
            requestor="Test", status=ProjectStatus.DRAFT,
        ))
        deps.FileAssetRepository(session).create(FileAsset(
            "attachment", "P1", FileAssetType.ATTACHMENT, source,
            original_name=source.name, source_role="supporting_attachment",
        ))
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    workspace = tmp_path / "workspace"
    official, template = workspace / "Official", tmp_path / "template"
    official.mkdir(parents=True)
    template.mkdir()
    (official / "old.txt").write_text("previous output", encoding="utf-8")
    (template / "new.txt").write_text("generated output", encoding="utf-8")
    preview = OfficialWorkspacePreview(
        project_id="P1", dl_number="DL-001", local_workspace_root=tmp_path,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=official,
        manifest_path=workspace / ".connlab" / "manifest.json",
        template_root_mode="template_root", status="exists", blockers=(), warnings=(),
        planned_paths=(), conflict_paths=(official,),
    )
    target = None
    real_unlink, real_chmod = Path.unlink, Path.chmod
    attempts, attribute_changes = [], []
    try:
        state = runner.journal.create("P1", "overwrite_rebuild", runner.context("P1"))
        with sessions() as session:
            RecoverableWorkspacePublisher(runner.journal, state).create(
                preview, "overwrite_rebuild", deps.ProjectOfficialWorkspaceRepository(session)
            )
            session.commit()
        backup = Path(state["effects"]["workspace"]["backup"])
        target = backup / "old.txt"
        target.chmod(stat.S_IREAD)

        def unlink(path, *args, **kwargs):
            if path == target:
                attempts.append(path)
            try:
                return real_unlink(path, *args, **kwargs)
            except PermissionError:
                if path == target and input_change == "first_denial":
                    source.write_text("changed input", encoding="utf-8")
                raise

        def chmod(path, *args, **kwargs):
            result = real_chmod(path, *args, **kwargs)
            if path == target:
                attribute_changes.append(path)
                if input_change == "after_chmod":
                    source.write_text("changed input", encoding="utf-8")
            return result

        monkeypatch.setattr(Path, "unlink", unlink)
        monkeypatch.setattr(Path, "chmod", chmod)
        if input_change is not None:
            with pytest.raises(ValueError, match="Generation inputs changed"):
                runner.finalize(state)
            assert target.read_text(encoding="utf-8") == "previous output"
            assert len(attempts) == 1
            assert len(attribute_changes) == (1 if input_change == "after_chmod" else 0)
            assert bool(target.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY) == (
                input_change == "first_denial"
            )
            assert not runner.journal.read("P1")["effects"]["workspace"].get("overwrite_deleted")
        else:
            runner.finalize(state)
            assert not backup.exists()
            assert len(attempts) == 2
            assert len(attribute_changes) == 1
            assert runner.journal.read("P1")["effects"]["workspace"]["overwrite_deleted"] is True
        assert (official / "new.txt").read_text(encoding="utf-8") == "generated output"
    finally:
        if target is not None and target.exists():
            real_chmod(target, stat.S_IWRITE)
        runner.pool.shutdown()
        engine.dispose()


@pytest.mark.parametrize("missing_attachment", [False, True])
def test_materials_step_commits_warning_only_collection_but_rejects_unresolved_sources(tmp_path, missing_attachment):
    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    workspace, official = tmp_path / "workspace", tmp_path / "workspace" / "Official"
    official.mkdir(parents=True)
    source = tmp_path / "application.docx"
    source.write_bytes(b"submitted form")
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(project_id="P1", project_no="DL-001", product_name="Fixture", requestor="Test", status=ProjectStatus.DRAFT))
        deps.ProjectOfficialWorkspaceRepository(session).save(OfficialWorkspaceRecord(
            workspace_id="workspace", project_id="P1", dl_number="DL-001", local_workspace_path=workspace,
            source_book_path=workspace / "Source Book", official_folder_path=official,
            manifest_path=workspace / ".connlab" / "manifest.json", template_source_path=tmp_path / "template", created_at="2026-09-05T00:00:00+00:00"))
        deps.FileAssetRepository(session).create(FileAsset("app", "P1", FileAssetType.APPLICATION_FORM,
            source, original_name=source.name, source_role="selected_application_form"))
        if missing_attachment:
            deps.FileAssetRepository(session).create(FileAsset("attachment", "P1", FileAssetType.ATTACHMENT,
                tmp_path / "missing.pdf", original_name="missing.pdf", source_role="supporting_attachment"))
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    runner.context = lambda _: "fixture authority"
    state = runner.journal.create("P1", None, "fixture authority")
    try:
        if missing_attachment:
            with pytest.raises(ValueError, match="material|source"):
                runner.run_step(state, "materials")
        else:
            runner.run_step(state, "materials")
            with sessions() as session:
                collection = deps.ProjectRequestMaterialCollectionRepository(session).latest_by_project("P1")
                assert collection.collection_id == state["operation_id"]
                assert "Request email missing" in collection.warnings
            target = official / "Submitted Material" / source.name
            before = target.stat().st_mtime_ns
            runner.run_step(state, "materials")
            assert target.stat().st_mtime_ns == before
    finally:
        runner.pool.shutdown()
        engine.dispose()


def _child(root, mode):
    settings = _settings(root)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    sessions = create_session_factory(engine)
    fixtures = runpy.run_path(str(Path(__file__).parents[1] / "unit" / "test_project_folder_required_forms_service.py"))
    runner = ProjectFolderGenerationRunner(sessions, settings)
    state = runner.journal.read("P1")
    runner.context = lambda _: "fixture authority"
    generator = fixtures["_Generator"](root)
    if mode == "recover":
        def reject_repeat(**kwargs):
            raise AssertionError("Recovery regenerated a published form")
        generator.generate = reject_repeat
    deps.get_project_folder_required_forms_service = lambda session, settings: fixtures["_service"](
        root, output_service=deps.get_project_output_record_service(session), generator=generator)
    if mode == "before_db":
        from backend.application.project_output_record_service import ProjectOutputRecordService
        ProjectOutputRecordService.register_output = lambda *args, **kwargs: os._exit(23)
    runner.run_step(state, "customer_feedback_form")
    runner.pool.shutdown()
    engine.dispose()
    if mode == "after_db":
        os._exit(24)


def _application_child(root, mode):
    settings = _settings(root)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    runner = ProjectFolderGenerationRunner(create_session_factory(engine), settings)
    state = runner.journal.read("P1")
    runner.context = lambda _: "fixture authority"
    fixtures = runpy.run_path(str(Path(__file__).parents[1] / "unit" / "test_project_application_form_write_back_service.py"))
    official, source = root / "official", root / "source.docx"
    target = official / "Submitted Material" / "application.docx"
    class FakeOffice:
        def write_word_application_form_fields_with_owned_session(self, staged, fields):
            assert staged != target
            assert target.read_bytes() == source.read_bytes()
            if mode == "app_recover":
                raise AssertionError("Recovery repeated Office edits")
            staged.write_bytes(b"partial fake Office edit" if mode == "app_office" else b"complete fake Office result")
            if mode == "app_office":
                os._exit(41)
            return SimpleNamespace(changed_fields=(), unchanged_fields=(), warnings=())
    deps.get_project_application_form_write_back_service = lambda session, settings: ProjectApplicationFormWriteBackService(
        project_store=fixtures["_ProjectStore"](), workspace_store=fixtures["_WorkspaceStore"](official),
        application_form_store=fixtures["_ApplicationFormStore"](), file_asset_store=fixtures["_FileAssetStore"](source),
        basic_information_reader=fixtures["_BasicInformationReader"](fixtures["_basic_information"]()),
        output_record_service=deps.get_project_output_record_service(session),
        file_gateway=ProjectFolderRequiredFormsFileGateway(), office=FakeOffice(),
    )
    if mode == "app_before_db":
        from backend.application.project_output_record_service import ProjectOutputRecordService
        ProjectOutputRecordService.register_output = lambda *args, **kwargs: os._exit(42)
    runner.run_step(state, "application_form")
    runner.pool.shutdown()
    engine.dispose()
    if mode == "app_after_db":
        os._exit(43)


@pytest.mark.parametrize("window,exit_code", [("before_db", 23), ("after_db", 24)])
def test_new_process_recovers_published_output_and_committed_record_without_regeneration(tmp_path, window, exit_code):
    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(project_id="P1", project_no="DL-001", product_name="Fixture",
                                                     requestor="Test", status=ProjectStatus.DRAFT))
        session.commit()
    journal = GenerationJournal(settings.data_dir / "project_folder_generation")
    state = journal.create("P1", None, "fixture authority")
    # This fixture exercises one real form step, not an earlier workspace execution.
    state.update(step=3, completed_steps=[])
    journal.save(state)
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).parents[2]))
    def run(mode):
        return subprocess.run([sys.executable, str(Path(__file__).resolve()), str(tmp_path), mode],
                              env=env, capture_output=True, text=True, timeout=40)
    crashed = run(window)
    assert crashed.returncode == exit_code, crashed.stdout + crashed.stderr
    state = journal.read("P1")
    effect = state["effects"]["customer_feedback_form:customer_feedback_form"]
    target = Path(effect["target"])
    original_bytes, original_mtime = target.read_bytes(), target.stat().st_mtime_ns
    recovered = run("recover")
    assert recovered.returncode == 0, recovered.stdout + recovered.stderr
    recovered_again = run("recover")
    assert recovered_again.returncode == 0, recovered_again.stdout + recovered_again.stderr
    with sessions() as session:
        records = deps.get_project_output_record_service(session).list_records("P1")
        assert len(records) == 1
        assert records[0].output_path == str(target)
    assert target.read_bytes() == original_bytes
    assert target.stat().st_mtime_ns == original_mtime
    engine.dispose()


@pytest.mark.parametrize("window,exit_code", [("app_office", 41), ("app_before_db", 42), ("app_after_db", 43)])
def test_application_form_process_crash_never_edits_final_in_place_or_repeats_committed_office(tmp_path, window, exit_code):
    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(project_id="P1", project_no="DL-001", product_name="Fixture", requestor="Test", status=ProjectStatus.DRAFT))
        session.commit()
    source, target = tmp_path / "source.docx", tmp_path / "official" / "Submitted Material" / "application.docx"
    source.write_bytes(b"original source bytes")
    target.parent.mkdir(parents=True)
    shutil.copy2(source, target)
    journal = GenerationJournal(settings.data_dir / "project_folder_generation")
    journal.create("P1", None, "fixture authority")
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).parents[2]))
    def run(mode):
        return subprocess.run([sys.executable, str(Path(__file__).resolve()), str(tmp_path), mode], env=env,
                              capture_output=True, text=True, timeout=40)
    crashed = run(window)
    assert crashed.returncode == exit_code, crashed.stdout + crashed.stderr
    if window == "app_office":
        assert target.read_bytes() == b"original source bytes"
        assert set(path.name for path in target.parent.iterdir()) == {"application.docx"}
        recovered = run("app_finish")
    else:
        assert target.read_bytes() == b"complete fake Office result"
        recovered = run("app_recover")
    assert recovered.returncode == 0, recovered.stdout + recovered.stderr
    before = target.stat().st_mtime_ns
    recovered_again = run("app_recover")
    assert recovered_again.returncode == 0, recovered_again.stdout + recovered_again.stderr
    assert target.read_bytes() == b"complete fake Office result"
    assert target.stat().st_mtime_ns == before
    assert source.read_bytes() == b"original source bytes"
    with sessions() as session:
        assert len(deps.get_project_output_record_service(session).list_records("P1")) == 1
    engine.dispose()


if __name__ == "__main__":
    (_application_child if sys.argv[2].startswith("app_") else _child)(Path(sys.argv[1]), sys.argv[2])
