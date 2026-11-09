from __future__ import annotations

from datetime import date
import json
from pathlib import Path

import pytest

from backend.application.official_project_folder_check_service import OfficialFolderCheckPreview
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.public_folder_path_resolver import PublicFolderPathError, PublicFolderPathResolver
from backend.application.public_folder_workflow_service import (
    PublicFolderWorkflowBlockedError,
    PublicFolderWorkflowConflictError,
    PublicFolderWorkflowExecuteCommand,
    PublicFolderWorkflowService,
    PublicFolderWorkflowState,
    PublicFolderWorkflowFileRecord,
)
from backend.application.public_folder_year_resolver import PublicFolderYearResolver
from backend.domain import Project, ProjectStatus
from backend.infrastructure.files.public_folder_workflow_gateway import PublicFolderWorkflowGateway


def test_path_resolver_blocks_missing_public_root(tmp_path: Path) -> None:
    resolver = PublicFolderPathResolver()

    with pytest.raises(PublicFolderPathError):
        resolver.resolve(
            public_root=tmp_path / "missing",
            year=2026,
            project_folder_name="DL-1 Product",
        )

    assert not (tmp_path / "missing").exists()


def test_context_reports_existing_local_official_folder_as_available(tmp_path: Path) -> None:
    service, _repository, _paths = _service(tmp_path)

    context = service.context("P1")

    assert context.local_official_folder_available is True


def test_context_reports_public_project_folder_availability(tmp_path: Path) -> None:
    service, _repository, _paths = _service(tmp_path)
    context = service.context("P1")
    assert context.public_open_folder_available is False
    context.public_open_path.mkdir(parents=True)
    assert service.context("P1").public_open_folder_available is False
    _bind(service)
    assert service.context("P1").public_open_folder_available is True


def test_public_paths_use_company_directory_names(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path, existing_years=False)
    context = service.context("P1")
    assert context.public_open_path == paths["public"] / "Open projects" / "2026" / paths["local"].name
    assert context.public_closed_path == paths["public"] / "Closed projects" / "2026" / paths["local"].name


def test_sync_requires_existing_open_year_and_reports_missing_path(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path, existing_years=False)
    (paths["local"] / "file.txt").write_text("data", encoding="utf-8")
    (paths["public"] / "Open projects").mkdir()
    preview = service.preview_sync("P1")
    missing = paths["public"] / "Open projects" / "2026"
    assert preview.status == "blocked"
    assert any(str(missing) in message and "create" in message.lower() for message in preview.blockers)
    with pytest.raises(PublicFolderWorkflowBlockedError):
        service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
        ))
    assert not missing.exists()


def test_sync_only_needs_open_year_and_requires_creation_confirmation(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path, existing_years=False)
    (paths["public"] / "Open projects" / "2026").mkdir(parents=True)
    (paths["local"] / "nested").mkdir()
    (paths["local"] / "nested" / "file.txt").write_text("data", encoding="utf-8")
    preview = service.preview_sync("P1")
    assert preview.status == "ready"
    assert "create_missing_public_directories" in preview.required_confirmations
    with pytest.raises(PublicFolderWorkflowBlockedError, match="Directory creation"):
        service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash, confirmed=True,
        ))
    assert not preview.public_open_path.exists()
    result = service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
        preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
    ))
    assert result.status == "completed"
    assert (preview.public_open_path / "nested" / "file.txt").read_text(encoding="utf-8") == "data"
    assert not (paths["public"] / "Closed projects").exists()


def test_sync_ignores_unusable_closed_location(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path, existing_years=False)
    (paths["public"] / "Open projects" / "2026").mkdir(parents=True)
    closed = paths["public"] / "Closed projects"
    closed.write_text("not a directory", encoding="utf-8")
    (paths["local"] / "file.txt").write_text("data", encoding="utf-8")
    assert not service.context("P1").blockers
    preview = service.preview_sync("P1")
    assert preview.status == "ready"
    result = service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
        preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
    ))
    assert result.status == "completed"
    assert closed.read_text(encoding="utf-8") == "not a directory"


def test_submit_requires_closed_year_but_does_not_create_it(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path, existing_years=False)
    (paths["public"] / "Open projects" / "2026").mkdir(parents=True)
    (paths["local"] / "file.txt").write_text("data", encoding="utf-8")
    sync = service.preview_sync("P1")
    service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
        preview_hash=sync.preview_hash, confirmed=True, confirm_directory_creation=True,
    ))
    closed = paths["public"] / "Closed projects"
    preview = service.preview_submit("P1")
    assert preview.status == "blocked"
    assert any(str(closed) in message and "create" in message.lower() for message in preview.blockers)
    with pytest.raises(PublicFolderWorkflowBlockedError):
        service.execute_submit("P1", PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
        ))
    assert not closed.exists()
    assert (sync.public_open_path / "file.txt").exists()


def test_missing_year_directory_after_preview_is_never_recreated(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("data", encoding="utf-8")
    preview = service.preview_sync("P1")
    year = paths["public"] / "Open projects" / "2026"
    year.rename(year.with_name("removed-year"))
    with pytest.raises(PublicFolderWorkflowBlockedError, match="create it manually") as exc:
        service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
        ))
    assert str(year) in str(exc.value)
    assert not year.exists()


def test_missing_year_can_be_created_manually_before_retry(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path, existing_years=False)
    (paths["local"] / "file.txt").write_text("data", encoding="utf-8")
    first = service.preview_sync("P1")
    assert first.status == "blocked"
    year = paths["public"] / "Open projects" / "2026"
    year.mkdir(parents=True)
    retry = service.preview_sync("P1")
    assert retry.status == "ready"
    result = service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
        preview_hash=retry.preview_hash, confirmed=True, confirm_directory_creation=True,
    ))
    assert result.status == "completed"
    assert (year / paths["local"].name / "file.txt").read_text(encoding="utf-8") == "data"


def test_year_removed_after_execute_preview_reports_path_without_recreating(tmp_path: Path, monkeypatch) -> None:
    service, _, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("data", encoding="utf-8")
    preview = service.preview_sync("P1")
    year = paths["public"] / "Open projects" / "2026"
    original = service.preview_sync
    def remove_year_after_preview(project_id):
        fresh = original(project_id)
        year.rename(year.with_name("removed-year"))
        return fresh
    monkeypatch.setattr(service, "preview_sync", remove_year_after_preview)
    with pytest.raises(PublicFolderWorkflowBlockedError, match="create it manually") as exc:
        service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
        ))
    assert str(year) in str(exc.value)
    assert not year.exists()


def test_public_year_removed_during_file_copy_is_not_recreated(tmp_path: Path, monkeypatch) -> None:
    service, _, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("data", encoding="utf-8")
    preview = service.preview_sync("P1")
    original = PublicFolderWorkflowGateway.copy_new_file
    year = paths["public"] / "Open projects" / "2026"
    def remove_year(gateway, source, target, **kwargs):
        year.rename(year.with_name("removed-year"))
        return original(gateway, source, target, **kwargs)
    monkeypatch.setattr(PublicFolderWorkflowGateway, "copy_new_file", remove_year)
    result = service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
        preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
    ))
    assert result.status == "failed"
    assert any(str(year) in error and "create it manually" in error for error in result.errors)
    assert not year.exists()


def test_closed_year_removed_during_submit_is_not_recreated(tmp_path: Path, monkeypatch) -> None:
    service, _, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("data", encoding="utf-8")
    sync = service.preview_sync("P1")
    service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
        preview_hash=sync.preview_hash, confirmed=True, confirm_directory_creation=True,
    ))
    preview = service.preview_submit("P1")
    year = paths["public"] / "Closed projects" / "2026"
    original = PublicFolderWorkflowGateway.move_directory_no_overwrite
    def remove_year(gateway, source, target):
        year.rename(year.with_name("removed-year"))
        return original(gateway, source, target)
    monkeypatch.setattr(PublicFolderWorkflowGateway, "move_directory_no_overwrite", remove_year)
    result = service.execute_submit("P1", PublicFolderWorkflowExecuteCommand(
        preview_hash=preview.preview_hash, confirmed=True,
    ))
    assert result.status == "failed"
    assert any(str(year) in error and "create it manually" in error for error in result.errors)
    assert not year.exists()
    assert (sync.public_open_path / "file.txt").read_text(encoding="utf-8") == "data"


def test_public_root_name_occupied_by_file_blocks_with_path(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path, existing_years=False)
    open_root = paths["public"] / "Open projects"
    open_root.write_text("not a directory", encoding="utf-8")
    preview = service.preview_sync("P1")
    assert preview.status == "blocked"
    assert any(str(open_root) in message for message in preview.blockers)
    assert open_root.read_text(encoding="utf-8") == "not a directory"


def test_public_year_occupied_by_file_blocks_with_path(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path, existing_years=False)
    year = paths["public"] / "Open projects" / "2026"
    year.parent.mkdir()
    year.write_text("not a directory", encoding="utf-8")
    preview = service.preview_sync("P1")
    assert preview.status == "blocked"
    assert any(str(year) in message and "create" in message.lower() for message in preview.blockers)
    assert year.read_text(encoding="utf-8") == "not a directory"


def test_pull_does_not_require_open_directory(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path, existing_years=False)
    closed = paths["public"] / "Closed projects" / "2026" / paths["local"].name
    closed.mkdir(parents=True)
    (closed / "approved.txt").write_text("approved", encoding="utf-8")
    preview = service.preview_pull("P1")
    assert preview.status == "ready"
    result = service.execute_pull("P1", PublicFolderWorkflowExecuteCommand(
        preview_hash=preview.preview_hash, confirmed=True,
    ))
    assert result.status == "completed"
    assert not (paths["public"] / "Open projects").exists()


def test_legacy_path_record_never_authorizes_replacing_new_target(tmp_path: Path) -> None:
    service, repository, paths = _service(tmp_path)
    local = paths["local"] / "file.txt"
    local.write_text("new version", encoding="utf-8")
    target = paths["public"] / "Open projects" / "2026" / paths["local"].name / "file.txt"
    target.parent.mkdir(parents=True)
    target.write_text("old version", encoding="utf-8")
    fingerprint = PublicFolderWorkflowGateway().fingerprint(target)
    repository.save_file(PublicFolderWorkflowFileRecord(
        project_id="P1", relative_path=Path("file.txt"),
        public_path=paths["public"] / "Open" / "2026" / paths["local"].name / "file.txt",
        local_fingerprint=fingerprint, public_fingerprint=fingerprint,
        updated_at="2026-01-01", operation_id="legacy",
    ))
    preview = service.preview_sync("P1")
    assert preview.status == "conflict"
    with pytest.raises(PublicFolderWorkflowConflictError):
        service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True))
    assert target.read_text(encoding="utf-8") == "old version"


def test_sync_leaves_legacy_directories_untouched(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path)
    local = paths["local"] / "file.txt"
    local.write_text("current", encoding="utf-8")
    old_open = paths["public"] / "Open" / "2026" / paths["local"].name
    old_closed = paths["public"] / "Closed" / "2026" / paths["local"].name
    for folder in (old_open, old_closed):
        folder.mkdir(parents=True)
        (folder / "file.txt").write_text("legacy", encoding="utf-8")
    preview = service.preview_sync("P1")
    service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
        preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
    ))
    assert (paths["public"] / "Open projects" / "2026" / paths["local"].name / "file.txt").read_text(encoding="utf-8") == "current"
    assert (old_open / "file.txt").read_text(encoding="utf-8") == "legacy"
    assert (old_closed / "file.txt").read_text(encoding="utf-8") == "legacy"


def test_context_keeps_recorded_missing_local_official_folder_unavailable(tmp_path: Path) -> None:
    service, _repository, paths = _service(tmp_path)
    paths["local"].rmdir()

    context = service.context("P1")

    assert context.local_official_folder_path == paths["local"]
    assert context.local_official_folder_available is False


def test_sync_execute_copies_to_open_and_records_operation(tmp_path: Path) -> None:
    service, repository, paths = _service(tmp_path)
    (paths["local"] / "Submitted Material").mkdir()
    (paths["local"] / "Submitted Material" / "app.docx").write_text("v1", encoding="utf-8")

    preview = service.preview_sync("P1")
    result = service.execute_sync(
        "P1",
        PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash,
            confirmed=True,
            confirm_directory_creation=True,
            operator="tester",
        ),
    )

    copied = paths["public"] / "Open projects" / "2026" / paths["local"].name / "Submitted Material" / "app.docx"
    assert result.status == "completed"
    assert copied.read_text(encoding="utf-8") == "v1"
    assert repository.operations[-1].operation_type == "sync"
    assert repository.get_file("P1", Path("Submitted Material/app.docx")) is not None


def test_partial_sync_skips_conflict_and_preserves_colleague_files(tmp_path: Path) -> None:
    service, repository, paths = _service(tmp_path)
    (paths["local"] / "conflict.txt").write_text("local", encoding="utf-8")
    (paths["local"] / "new.txt").write_text("new", encoding="utf-8")
    target = paths["public"] / "Open projects" / "2026" / paths["local"].name
    target.mkdir(parents=True)
    (target / "conflict.txt").write_text("colleague", encoding="utf-8")
    (target / "extra.txt").write_text("extra", encoding="utf-8")
    preview = service.preview_sync("P1")
    assert preview.status == "partial"
    assert "confirm_existing_public_folder" in preview.required_confirmations
    with pytest.raises(PublicFolderWorkflowBlockedError):
        service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True))
    assert not (target / "new.txt").exists()
    result = service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True, confirm_existing_public_folder=True))
    assert result.status == "partial"
    assert result.counts["add"] == 1
    assert result.counts["conflict"] == 1
    assert (target / "new.txt").read_text(encoding="utf-8") == "new"
    assert (target / "conflict.txt").read_text(encoding="utf-8") == "colleague"
    assert (target / "extra.txt").read_text(encoding="utf-8") == "extra"
    assert repository.get_file("P1", Path("conflict.txt")) is None


def test_conflicting_directory_skips_entire_subtree_but_copies_other_files(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path)
    (paths["local"] / "blocked").mkdir()
    (paths["local"] / "blocked" / "nested.txt").write_text("nested", encoding="utf-8")
    (paths["local"] / "good.txt").write_text("good", encoding="utf-8")
    target = paths["public"] / "Open projects" / "2026" / paths["local"].name
    target.mkdir(parents=True)
    (target / "blocked").write_text("colleague", encoding="utf-8")
    preview = service.preview_sync("P1")
    result = service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True, confirm_existing_public_folder=True))
    assert result.status == "partial"
    assert (target / "blocked").read_text(encoding="utf-8") == "colleague"
    assert (target / "good.txt").read_text(encoding="utf-8") == "good"
    assert any(item.relative_path == Path("blocked/nested.txt") and item.status == "conflict" for item in result.items)


def test_preview_rejects_file_content_changes_even_if_action_is_unchanged(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path)
    source = paths["local"] / "new.txt"
    source.write_text("first", encoding="utf-8")
    preview = service.preview_sync("P1")
    source.write_text("changed", encoding="utf-8")
    with pytest.raises(PublicFolderWorkflowConflictError, match="stale"):
        service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True))
    assert not (paths["public"] / "Open projects" / "2026" / paths["local"].name / "new.txt").exists()


def test_managed_existing_file_update_is_skipped_without_overwriting(tmp_path: Path) -> None:
    service, repository, paths = _service(tmp_path)
    source = paths["local"] / "old.txt"
    source.write_text("first", encoding="utf-8")
    first = service.preview_sync("P1")
    service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(preview_hash=first.preview_hash, confirmed=True, confirm_directory_creation=True))
    source.write_text("updated", encoding="utf-8")
    (paths["local"] / "new.txt").write_text("new", encoding="utf-8")
    preview = service.preview_sync("P1")
    result = service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True))
    target = paths["public"] / "Open projects" / "2026" / paths["local"].name
    assert result.status == "partial"
    assert (target / "old.txt").read_text(encoding="utf-8") == "first"
    assert (target / "new.txt").read_text(encoding="utf-8") == "new"
    assert any(item.relative_path == Path("old.txt") and "manual review" in item.message for item in result.items)
    assert repository.operations[-1].counts == result.counts
    audit = json.loads(repository.operations[-1].metadata_json)
    assert any(item["relative_path"] == "old.txt" and item["status"] == "conflict" for item in audit["result_items"])


def test_empty_conflicting_directory_is_reported(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path)
    (paths["local"] / "empty").mkdir()
    (paths["local"] / "new.txt").write_text("new", encoding="utf-8")
    target = paths["public"] / "Open projects" / "2026" / paths["local"].name
    target.mkdir(parents=True)
    (target / "empty").write_text("colleague", encoding="utf-8")
    preview = service.preview_sync("P1")
    result = service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True, confirm_existing_public_folder=True))
    assert result.status == "partial"
    assert result.counts["directory_conflict"] == 1
    assert any(item.relative_path == Path("empty") and item.kind == "directory" and item.status == "conflict" for item in result.items)


def test_no_successful_files_is_failed_even_when_directories_created(tmp_path: Path, monkeypatch) -> None:
    service, repository, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("local", encoding="utf-8")
    preview = service.preview_sync("P1")
    def fail_copy(*args, **kwargs):
        raise FileExistsError("Target appeared during copy")
    monkeypatch.setattr(PublicFolderWorkflowGateway, "copy_new_file", fail_copy)
    result = service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True))
    assert result.status == "failed"
    assert result.counts["add"] == 0
    assert result.counts["conflict"] == 1
    assert repository.operations[-1].counts == result.counts
    assert any("Target appeared" in item.message for item in result.items)


def test_new_target_appearing_during_sync_is_skipped_and_other_files_continue(tmp_path: Path, monkeypatch) -> None:
    service, repository, paths = _service(tmp_path)
    (paths["local"] / "a.txt").write_text("local a", encoding="utf-8")
    (paths["local"] / "b.txt").write_text("local b", encoding="utf-8")
    preview = service.preview_sync("P1")
    original = PublicFolderWorkflowGateway.copy_new_file
    def competing_copy(gateway, source, target, **kwargs):
        if source.name == "a.txt":
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("colleague a", encoding="utf-8")
        return original(gateway, source, target, **kwargs)
    monkeypatch.setattr(PublicFolderWorkflowGateway, "copy_new_file", competing_copy)
    result = service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True))
    target = paths["public"] / "Open projects" / "2026" / paths["local"].name
    assert result.status == "partial"
    assert result.counts["add"] == 1 and result.counts["conflict"] == 1
    assert (target / "a.txt").read_text(encoding="utf-8") == "colleague a"
    assert (target / "b.txt").read_text(encoding="utf-8") == "local b"
    assert repository.operations[-1].counts == result.counts


def test_completed_copy_is_reported_if_post_sync_refresh_fails(tmp_path: Path, monkeypatch) -> None:
    service, repository, paths = _service(tmp_path)
    _bind(service)
    (paths["local"] / "file.txt").write_text("data", encoding="utf-8")
    preview = service.preview_sync("P1")
    original = PublicFolderWorkflowGateway.list_files
    calls = 0
    def fail_refresh(gateway, root):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("network unavailable")
        return original(gateway, root)
    monkeypatch.setattr(PublicFolderWorkflowGateway, "list_files", fail_refresh)
    result = service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True))
    target = paths["public"] / "Open projects" / "2026" / paths["local"].name / "file.txt"
    assert target.read_text(encoding="utf-8") == "data"
    assert result.status == "partial" and result.counts["add"] == 1
    assert any("Unable to refresh" in error for error in result.errors)
    assert repository.operations[-1].counts == result.counts


def test_execute_rejects_stale_preview_hash(tmp_path: Path) -> None:
    service, _repository, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("v1", encoding="utf-8")
    preview = service.preview_sync("P1")
    target = paths["public"] / "Open projects" / "2026" / paths["local"].name / "file.txt"
    target.parent.mkdir(parents=True)
    target.write_text("human", encoding="utf-8")

    with pytest.raises(PublicFolderWorkflowConflictError):
        service.execute_sync(
            "P1",
            PublicFolderWorkflowExecuteCommand(
                preview_hash=preview.preview_hash,
                confirmed=True,
                confirm_directory_creation=True,
            ),
        )


def test_submit_moves_open_to_closed_and_locks_sync(tmp_path: Path) -> None:
    service, repository, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("v1", encoding="utf-8")
    sync = service.preview_sync("P1")
    service.execute_sync(
        "P1",
        PublicFolderWorkflowExecuteCommand(
            preview_hash=sync.preview_hash,
            confirmed=True,
            confirm_directory_creation=True,
        ),
    )

    submit = service.preview_submit("P1")
    service.execute_submit(
        "P1",
        PublicFolderWorkflowExecuteCommand(
            preview_hash=submit.preview_hash,
            confirmed=True,
            confirm_directory_creation=True,
        ),
    )

    closed_file = paths["public"] / "Closed projects" / "2026" / paths["local"].name / "file.txt"
    assert closed_file.read_text(encoding="utf-8") == "v1"
    assert repository.get_state("P1").sync_locked is True
    assert "Sync is locked after Submit." in service.preview_sync("P1").blockers


def test_submit_preview_blocks_unmanaged_public_open_file(tmp_path: Path) -> None:
    service, _repository, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("v1", encoding="utf-8")
    sync = service.preview_sync("P1")
    service.execute_sync(
        "P1",
        PublicFolderWorkflowExecuteCommand(
            preview_hash=sync.preview_hash,
            confirmed=True,
            confirm_directory_creation=True,
        ),
    )
    open_folder = paths["public"] / "Open projects" / "2026" / paths["local"].name
    closed_folder = paths["public"] / "Closed projects" / "2026" / paths["local"].name
    unmanaged = open_folder / "human-extra.txt"
    unmanaged.write_text("outside ConnLab", encoding="utf-8")

    submit = service.preview_submit("P1")

    assert submit.status == "conflict"
    assert submit.next_action == "none"
    assert submit.counts["conflict"] == 1
    assert "Public Open file is not managed by ConnLab" in submit.conflicts[0]
    with pytest.raises(PublicFolderWorkflowConflictError):
        service.execute_submit(
            "P1",
            PublicFolderWorkflowExecuteCommand(
                preview_hash=submit.preview_hash,
                confirmed=True,
                confirm_directory_creation=True,
            ),
        )
    assert open_folder.is_dir()
    assert (open_folder / "file.txt").read_text(encoding="utf-8") == "v1"
    assert unmanaged.read_text(encoding="utf-8") == "outside ConnLab"
    assert not closed_folder.exists()


def test_submit_execute_rejects_stale_preview_when_unmanaged_file_appears(tmp_path: Path) -> None:
    service, _repository, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("v1", encoding="utf-8")
    sync = service.preview_sync("P1")
    service.execute_sync(
        "P1",
        PublicFolderWorkflowExecuteCommand(
            preview_hash=sync.preview_hash,
            confirmed=True,
            confirm_directory_creation=True,
        ),
    )
    submit = service.preview_submit("P1")
    assert submit.status == "ready"
    open_folder = paths["public"] / "Open projects" / "2026" / paths["local"].name
    closed_folder = paths["public"] / "Closed projects" / "2026" / paths["local"].name
    (open_folder / "human-extra.txt").write_text("outside ConnLab", encoding="utf-8")

    with pytest.raises(PublicFolderWorkflowConflictError, match="stale"):
        service.execute_submit(
            "P1",
            PublicFolderWorkflowExecuteCommand(
                preview_hash=submit.preview_hash,
                confirmed=True,
                confirm_directory_creation=True,
            ),
        )
    assert open_folder.is_dir()
    assert (open_folder / "human-extra.txt").exists()
    assert not closed_folder.exists()


def test_pull_copies_closed_to_local_history_without_overwriting_current(tmp_path: Path) -> None:
    service, _repository, paths = _service(tmp_path)
    closed = paths["public"] / "Closed projects" / "2026" / paths["local"].name
    closed.mkdir(parents=True)
    (closed / "approved.txt").write_text("approved", encoding="utf-8")
    (paths["local"] / "current.txt").write_text("current", encoding="utf-8")

    preview = service.preview_pull("P1")
    result = service.execute_pull(
        "P1",
        PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash,
            confirmed=True,
            confirm_directory_creation=True,
        ),
    )

    assert result.status == "completed"
    assert (paths["local"] / "current.txt").read_text(encoding="utf-8") == "current"
    assert preview.target_path is not None
    assert (preview.target_path / "approved.txt").read_text(encoding="utf-8") == "approved"


def test_sync_rejects_project_folder_created_after_execute_preview(tmp_path: Path, monkeypatch) -> None:
    service, _, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("local data", encoding="utf-8")
    parent = paths["public"] / "Open projects" / "2026"
    preview = service.preview_sync("P1")
    original = service.preview_sync
    target = parent / paths["local"].name

    def race(project_id):
        fresh = original(project_id)
        target.mkdir()
        (target / "colleague.txt").write_text("colleague", encoding="utf-8")
        return fresh

    monkeypatch.setattr(service, "preview_sync", race)
    with pytest.raises(PublicFolderWorkflowConflictError, match="appeared"):
        service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
        ))
    assert sorted(path.name for path in target.iterdir()) == ["colleague.txt"]


def test_existing_project_folder_replaced_after_preview_is_stale(tmp_path: Path) -> None:
    service, _, paths = _service(tmp_path)
    (paths["local"] / "new.txt").write_text("local", encoding="utf-8")
    target = paths["public"] / "Open projects" / "2026" / paths["local"].name
    target.mkdir(parents=True)
    (target / "existing.txt").write_text("same", encoding="utf-8")
    preview = service.preview_sync("P1")
    target.rename(target.with_name("other-folder"))
    target.mkdir()
    (target / "existing.txt").write_text("same", encoding="utf-8")
    with pytest.raises(PublicFolderWorkflowConflictError):
        service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
            confirm_existing_public_folder=True,
        ))
    assert not (target / "new.txt").exists()


def test_sync_skips_files_if_project_folder_identity_changes(tmp_path: Path, monkeypatch) -> None:
    import backend.application.public_folder_workflow_service as workflow

    service, _, paths = _service(tmp_path)
    _bind(service)
    (paths["local"] / "file.txt").write_text("local data", encoding="utf-8")
    preview = service.preview_sync("P1")
    original = workflow._directory_identity
    calls = 0

    def changed_identity(path):
        nonlocal calls
        calls += 1
        identity = original(path)
        return identity if calls == 1 else (identity[0], identity[1] + 1)

    monkeypatch.setattr(workflow, "_directory_identity", changed_identity)
    with pytest.raises(PublicFolderWorkflowConflictError, match="identity changed"):
        service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
        ))
    assert not (paths["public"] / "Open projects" / "2026" / paths["local"].name / "file.txt").exists()


def test_sync_reports_partial_when_identity_becomes_unavailable_after_one_copy(tmp_path: Path, monkeypatch) -> None:
    import backend.application.public_folder_workflow_service as workflow

    service, repository, paths = _service(tmp_path)
    _bind(service)
    for name in ("a.txt", "b.txt"):
        (paths["local"] / name).write_text(name, encoding="utf-8")
    preview = service.preview_sync("P1")
    original = workflow._directory_identity
    copied = False
    original_copy = service._gateway.copy_new_file
    def copy_once(*args, **kwargs):
        nonlocal copied
        original_copy(*args, **kwargs)
        copied = True
    monkeypatch.setattr(service._gateway, "copy_new_file", copy_once)
    def unavailable_after_first_file(path):
        if copied:
            raise PublicFolderWorkflowConflictError("Directory identity unavailable")
        return original(path)

    monkeypatch.setattr(workflow, "_directory_identity", unavailable_after_first_file)
    result = service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
        preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
    ))
    target = paths["public"] / "Open projects" / "2026" / paths["local"].name
    assert result.status == "partial"
    assert (target / "a.txt").read_text(encoding="utf-8") == "a.txt"
    assert not (target / "b.txt").exists()
    assert result.counts["add"] == 1
    assert repository.operations[-1].status == "partial"


def test_sync_record_failure_reports_copied_file_and_preserves_it(tmp_path: Path, monkeypatch) -> None:
    service, repository, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("local data", encoding="utf-8")
    preview = service.preview_sync("P1")

    def fail_record(_record):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(repository, "save_file", fail_record)
    with pytest.raises(ValueError, match="was copied.*record could not be saved"):
        service.execute_sync("P1", PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash, confirmed=True, confirm_directory_creation=True,
        ))
    target = paths["public"] / "Open projects" / "2026" / paths["local"].name / "file.txt"
    assert target.read_text(encoding="utf-8") == "local data"


def _bind(service):
    preview = service.binding_preview("P1")
    choice = "create" if preview["can_create"] else preview["candidates"][0]["candidate_id"]
    service.confirm_binding("P1", preview["expected_context"], choice)


def _service(tmp_path: Path, *, existing_years: bool = True):
    local = tmp_path / "local" / "DL-2026-06-001 Product"
    public = tmp_path / "PublicProject"
    local.mkdir(parents=True)
    public.mkdir()
    if existing_years:
        (public / "Open projects" / "2026").mkdir(parents=True)
        (public / "Closed projects" / "2026").mkdir(parents=True)
    project_repository = _Projects()
    ltr_repository = _Ltrs()
    repository = _WorkflowRepository()
    service = PublicFolderWorkflowService(
        project_repository=project_repository,
        workspace_repository=_Workspaces(local),
        year_resolver=PublicFolderYearResolver(
            project_repository=project_repository,
            ltr_repository=ltr_repository,
        ),
        workflow_repository=repository,
        folder_check_service=_FolderCheck(local),
        public_root=public,
        gateway=PublicFolderWorkflowGateway(),
    )
    return service, repository, {"local": local, "public": public}


class _Projects:
    def get(self, project_id: str) -> Project | None:
        if project_id != "P1":
            return None
        return Project(
            project_id="P1",
            project_no="DL-2026-06-001",
            product_name="Product",
            requestor="User",
            status=ProjectStatus.LTR_REGISTERED,
            created_on=date(2026, 6, 30),
        )


class _Ltrs:
    def list_by_project(self, project_id: str):
        return []


class _Workspaces:
    def __init__(self, official_folder: Path) -> None:
        self._official_folder = official_folder

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        return OfficialWorkspaceRecord(
            workspace_id="workspace",
            project_id=project_id,
            dl_number="DL-2026-06-001",
            local_workspace_path=self._official_folder.parent,
            source_book_path=self._official_folder.parent / "Source Book",
            official_folder_path=self._official_folder,
            manifest_path=self._official_folder.parent / ".connlab" / "manifest.json",
            template_source_path=Path("template"),
            created_at="2026-06-30T00:00:00+00:00",
        )


class _FolderCheck:
    def __init__(self, official_folder: Path) -> None:
        self._official_folder = official_folder

    def preview(self, project_id: str) -> OfficialFolderCheckPreview:
        return OfficialFolderCheckPreview(
            project_id=project_id,
            status="ready",
            local_workspace_path=self._official_folder.parent,
            official_project_folder_path=self._official_folder,
            required_folders=tuple(),
            required_files=tuple(),
            blockers=tuple(),
            warnings=tuple(),
            next_action="none",
        )


class _WorkflowRepository:
    def __init__(self) -> None:
        self.states: dict[str, PublicFolderWorkflowState] = {}
        self.files = {}
        self.operations = []

    def get_state(self, project_id: str) -> PublicFolderWorkflowState:
        return self.states.get(project_id, PublicFolderWorkflowState(project_id=project_id))

    def save_state(self, state: PublicFolderWorkflowState) -> PublicFolderWorkflowState:
        self.states[state.project_id] = state
        return state

    def get_file(self, project_id: str, relative_path: Path):
        return self.files.get((project_id, relative_path.as_posix()))

    def save_file(self, record):
        self.files[(record.project_id, record.relative_path.as_posix())] = record
        return record

    def rebase_files(self, *, project_id: str, old_root: Path, new_root: Path, operation_id: str, updated_at: str) -> None:
        for key, record in list(self.files.items()):
            if key[0] != project_id:
                continue
            try:
                relative = record.public_path.relative_to(old_root)
            except ValueError:
                continue
            self.files[key] = record.__class__(
                project_id=record.project_id,
                relative_path=record.relative_path,
                public_path=new_root / relative,
                local_fingerprint=record.local_fingerprint,
                public_fingerprint=record.public_fingerprint,
                updated_at=updated_at,
                operation_id=operation_id,
            )

    def save_operation(self, record):
        self.operations.append(record)
        return record
