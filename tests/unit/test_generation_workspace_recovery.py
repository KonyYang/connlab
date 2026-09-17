from pathlib import Path
from types import SimpleNamespace
from datetime import datetime
import os
import stat

import pytest

from backend.application.official_project_workspace_service import OfficialWorkspacePreview
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.files.recoverable_workspace_publisher import RecoverableWorkspacePublisher


class PowerLoss(BaseException):
    pass


def test_history_uses_original_local_mtime_and_preserves_name_collision(tmp_path):
    preview = _existing_workspace_preview(tmp_path, False)
    target = preview.official_folder_path
    stamp = datetime(2026, 9, 13, 14, 30, 25).timestamp()
    os.utime(target, (stamp, stamp))
    reserved = target.with_name("official 20260913143025")
    reserved.mkdir()
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "backup_and_recreate", "context")
    RecoverableWorkspacePublisher(journal, state).create(
        preview, "backup_and_recreate", SimpleNamespace(save=lambda record: record)
    )
    assert (target.with_name("official 20260913143025-1") / "operator.txt").read_text() == "keep"
    assert reserved.is_dir()


def test_overwrite_retains_recovery_copy_until_successful_finalization(tmp_path):
    preview = _existing_workspace_preview(tmp_path, False)
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "overwrite_rebuild", "context")
    publisher = RecoverableWorkspacePublisher(journal, state)
    publisher.create(preview, "overwrite_rebuild", SimpleNamespace(save=lambda record: record))
    backup = Path(state["effects"]["workspace"]["backup"])
    assert (backup / "operator.txt").read_text() == "keep"
    assert backup.name == "overwrite-old"
    publisher.finalize()
    assert not backup.exists()
    assert (preview.official_folder_path / "template.txt").read_text() == "new"
    RecoverableWorkspacePublisher(journal, journal.read("p")).finalize()


@pytest.mark.skipif(os.name != "nt", reason="Windows readonly deletion semantics")
@pytest.mark.parametrize("whole", [False, True])
@pytest.mark.parametrize("readonly_target", ["nested", "nested/old.txt", "."])
def test_overwrite_finalization_removes_readonly_owned_entries(
    tmp_path, whole, readonly_target
):
    preview = _existing_workspace_preview(tmp_path, whole)
    nested = preview.conflict_paths[0] / "nested"
    nested.mkdir()
    (nested / "old.txt").write_text("old", encoding="utf-8")
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "overwrite_rebuild", "context")
    publisher = RecoverableWorkspacePublisher(journal, state)
    publisher.create(preview, "overwrite_rebuild", SimpleNamespace(save=lambda record: record))
    backup = Path(state["effects"]["workspace"]["backup"])
    readonly = backup / readonly_target
    readonly.chmod(stat.S_IREAD)
    try:
        assert readonly.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY
        publisher.finalize()
        assert not backup.exists()
        assert journal.read("p")["effects"]["workspace"]["overwrite_deleted"] is True
        assert (preview.official_folder_path / "template.txt").read_text(encoding="utf-8") == "new"
        RecoverableWorkspacePublisher(journal, journal.read("p")).finalize()
    finally:
        if readonly.exists():
            readonly.chmod(stat.S_IWRITE)


@pytest.mark.skipif(os.name != "nt", reason="Windows readonly deletion semantics")
@pytest.mark.parametrize("readonly", [False, True])
def test_overwrite_cleanup_preserves_external_hardlink_attributes(tmp_path, readonly):
    preview = _existing_workspace_preview(tmp_path, False)
    alias = tmp_path / "external-alias.txt"
    os.link(preview.official_folder_path / "operator.txt", alias)
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "overwrite_rebuild", "context")
    publisher = RecoverableWorkspacePublisher(journal, state)
    publisher.create(preview, "overwrite_rebuild", SimpleNamespace(save=lambda record: record))
    backup = Path(state["effects"]["workspace"]["backup"])
    if readonly:
        alias.chmod(stat.S_IREAD)
    attributes = alias.stat().st_file_attributes
    try:
        if readonly:
            with pytest.raises(ValueError, match="hard link"):
                publisher.finalize()
            assert (backup / "operator.txt").read_text(encoding="utf-8") == "keep"
            assert not journal.read("p")["effects"]["workspace"].get("overwrite_deleted")
        else:
            publisher.finalize()
            assert not backup.exists()
        assert alias.read_text(encoding="utf-8") == "keep"
        assert alias.stat().st_file_attributes == attributes
    finally:
        alias.chmod(stat.S_IWRITE)


@pytest.mark.skipif(os.name != "nt", reason="Windows readonly deletion semantics")
@pytest.mark.parametrize("change", ["new", "changed", "foreign_root", "redirected", "context"])
def test_readonly_retry_revalidates_before_changing_attributes(tmp_path, monkeypatch, change):
    import subprocess

    preview = _existing_workspace_preview(tmp_path, False)
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "overwrite_rebuild", "context")
    context_changed = False

    def verify_context():
        if context_changed:
            raise ValueError("Generation inputs changed")

    publisher = RecoverableWorkspacePublisher(journal, state, verify_context)
    publisher.create(preview, "overwrite_rebuild", SimpleNamespace(save=lambda record: record))
    backup = Path(state["effects"]["workspace"]["backup"])
    target = backup / "operator.txt"
    target.chmod(stat.S_IREAD)
    real_unlink, real_chmod = Path.unlink, Path.chmod
    attribute_changes = []
    retained = tmp_path / "retained"
    junction = backup / "redirected"

    def denied_after_change(path, *args, **kwargs):
        nonlocal context_changed
        if path != target:
            return real_unlink(path, *args, **kwargs)
        if change == "new":
            (backup / "new.txt").write_text("must survive", encoding="utf-8")
        elif change == "changed":
            real_chmod(target, stat.S_IWRITE)
            target.write_text("operator edits", encoding="utf-8")
            real_chmod(target, stat.S_IREAD)
        elif change == "foreign_root":
            backup.rename(retained)
            backup.mkdir()
            target.write_text("keep", encoding="utf-8")
            real_chmod(target, stat.S_IREAD)
        elif change == "redirected":
            retained.mkdir()
            (retained / "external.txt").write_text("must survive", encoding="utf-8")
            subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(retained)],
                           check=True, capture_output=True)
        else:
            context_changed = True
        raise PermissionError(5, "Access denied", str(path))

    monkeypatch.setattr(Path, "unlink", denied_after_change)
    monkeypatch.setattr(Path, "chmod", lambda path, *args, **kwargs: attribute_changes.append(path))
    try:
        with pytest.raises(ValueError):
            publisher.finalize()
        assert attribute_changes == []
        assert target.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY
        assert target.read_text(encoding="utf-8") == ("operator edits" if change == "changed" else "keep")
        assert not journal.read("p")["effects"]["workspace"].get("overwrite_deleted")
        if change == "redirected":
            assert (retained / "external.txt").read_text(encoding="utf-8") == "must survive"
    finally:
        if junction.exists():
            junction.rmdir()
        real_chmod(target, stat.S_IWRITE)
        if (retained / "operator.txt").exists():
            real_chmod(retained / "operator.txt", stat.S_IWRITE)


@pytest.mark.skipif(os.name != "nt", reason="Windows readonly deletion semantics")
def test_history_finalization_keeps_readonly_copy_unchanged(tmp_path):
    preview = _existing_workspace_preview(tmp_path, False)
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "backup_and_recreate", "context")
    publisher = RecoverableWorkspacePublisher(journal, state)
    publisher.create(preview, "backup_and_recreate", SimpleNamespace(save=lambda record: record))
    backup = Path(state["effects"]["workspace"]["backup"])
    backup.chmod(stat.S_IREAD)
    try:
        publisher.finalize()
        assert backup.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY
        assert (backup / "operator.txt").read_text(encoding="utf-8") == "keep"
    finally:
        backup.chmod(stat.S_IWRITE)


@pytest.mark.skipif(os.name != "nt", reason="Windows sharing violation")
@pytest.mark.parametrize("readonly", [False, True])
def test_locked_cleanup_remains_pending_then_resumes_without_replaying_outputs(tmp_path, monkeypatch, readonly):
    import ctypes
    from ctypes import wintypes
    from backend.application.project_folder_generation_service import GENERATION_STEPS, ProjectFolderGenerationService

    preview = _existing_workspace_preview(tmp_path, False)
    journal = GenerationJournal(tmp_path / "journal")
    steps, queued, deletion_attempts, handles = [], [], [], []
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                   ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    real_unlink = Path.unlink

    def count_deletion(path, *args, **kwargs):
        if path.name == "operator.txt":
            deletion_attempts.append(path)
        return real_unlink(path, *args, **kwargs)

    def step(state, name):
        steps.append(name)
        if name == "workspace":
            RecoverableWorkspacePublisher(journal, state).create(
                preview, "overwrite_rebuild", SimpleNamespace(save=lambda record: record)
            )
            target = Path(state["effects"]["workspace"]["backup"]) / "operator.txt"
            if readonly:
                target.chmod(stat.S_IREAD)
            # Permit reads and attribute changes, but deliberately deny delete sharing.
            handle = kernel32.CreateFileW(str(target), 0x80000000, 3, None, 3, 0, None)
            assert handle != wintypes.HANDLE(-1).value, ctypes.get_last_error()
            handles.append(handle)

    monkeypatch.setattr(Path, "unlink", count_deletion)
    service = ProjectFolderGenerationService(
        journal, lambda _: "same", step, queued.append,
        finalize=lambda state: RecoverableWorkspacePublisher(journal, state).finalize(),
    )
    try:
        started = service.start("p", "overwrite_rebuild", "same", "request")
        queued.pop()()
        blocked = service.read("p")
        assert blocked["status"] == "blocked"
        assert blocked["can_restart"] is False
        assert "Stage: folder_finalization" in blocked["message"]
        assert journal.read("p")["finalization_pending"] is True
        assert len(deletion_attempts) == (2 if readonly else 1)
        assert deletion_attempts[0].read_text(encoding="utf-8") == "keep"
    finally:
        for handle in handles:
            kernel32.CloseHandle(handle)

    service.resume("p", started["operation_id"])
    queued.pop()()
    assert service.read("p")["status"] == "completed"
    assert steps == list(GENERATION_STEPS)
    assert not deletion_attempts[0].parent.exists()
    assert (preview.official_folder_path / "template.txt").read_text(encoding="utf-8") == "new"


@pytest.mark.parametrize("foreign_content", [False, True])
def test_overwrite_finalization_recovers_partial_delete_but_rejects_new_content(
    tmp_path, monkeypatch, foreign_content
):
    preview = _existing_workspace_preview(tmp_path, False)
    (preview.official_folder_path / "second.txt").write_text("old", encoding="utf-8")
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "overwrite_rebuild", "context")
    publisher = RecoverableWorkspacePublisher(journal, state)
    publisher.create(preview, "overwrite_rebuild", SimpleNamespace(save=lambda record: record))
    backup = Path(state["effects"]["workspace"]["backup"])
    real_unlink = Path.unlink
    def interrupt(path, *args, **kwargs):
        real_unlink(path, *args, **kwargs)
        if path.parent == backup:
            raise PowerLoss()
    monkeypatch.setattr(Path, "unlink", interrupt)
    with pytest.raises(PowerLoss):
        publisher.finalize()
    monkeypatch.setattr(Path, "unlink", real_unlink)
    assert len(list(backup.iterdir())) == 1
    if foreign_content:
        (backup / "new.txt").write_text("must survive", encoding="utf-8")
        with pytest.raises(ValueError, match="changed during deletion"):
            RecoverableWorkspacePublisher(journal, journal.read("p")).finalize()
        assert (backup / "new.txt").read_text() == "must survive"
    else:
        RecoverableWorkspacePublisher(journal, journal.read("p")).finalize()
        assert not backup.exists()


def test_history_recovery_rejects_foreign_same_content_directory(tmp_path, monkeypatch):
    preview = _existing_workspace_preview(tmp_path, False)
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "backup_and_recreate", "context")
    real_rename = Path.rename
    def interrupt(path, target):
        result = real_rename(path, target)
        if path == preview.official_folder_path:
            raise PowerLoss()
        return result
    monkeypatch.setattr(Path, "rename", interrupt)
    with pytest.raises(PowerLoss):
        RecoverableWorkspacePublisher(journal, state).create(
            preview, "backup_and_recreate", SimpleNamespace(save=lambda record: record)
        )
    monkeypatch.setattr(Path, "rename", real_rename)
    backup = Path(state["effects"]["workspace"]["backup"])
    backup.rename(backup.with_name("actual-history"))
    backup.mkdir()
    (backup / "operator.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="conflict target changed"):
        RecoverableWorkspacePublisher(journal, journal.read("p")).recover(
            SimpleNamespace(save=lambda record: record)
        )
    assert (backup / "operator.txt").read_text() == "keep"


def test_old_overwrite_journal_does_not_authorize_deleting_retained_copy(tmp_path):
    preview = _existing_workspace_preview(tmp_path, False)
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "overwrite_rebuild", "context")
    publisher = RecoverableWorkspacePublisher(journal, state)
    publisher.create(preview, "overwrite_rebuild", SimpleNamespace(save=lambda record: record))
    effect = state["effects"]["workspace"]
    effect.pop("overwrite_cleanup")  # Prior-version durable journal has no deletion intent.
    journal.save(state)
    RecoverableWorkspacePublisher(journal, journal.read("p")).finalize()
    assert (Path(effect["backup"]) / "operator.txt").read_text() == "keep"


def _existing_workspace_preview(tmp_path, whole):
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new", encoding="utf-8")
    workspace = tmp_path / "DL1"
    official = workspace / "official"
    official.mkdir(parents=True)
    conflict = workspace if whole else official
    (conflict / "operator.txt").write_text("keep", encoding="utf-8")
    return OfficialWorkspacePreview(
        project_id="p", dl_number="DL1", local_workspace_root=tmp_path,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=official,
        manifest_path=workspace / ".connlab" / "manifest.json",
        template_root_mode="template_root", status="exists",
        blockers=("Existing folder",), warnings=(), planned_paths=(),
        conflict_paths=(conflict,),
    )


@pytest.mark.parametrize("whole", [True, False])
@pytest.mark.parametrize("window", ["persisted_checkpoint", "locked_folder_edit"])
def test_unpublished_rebuild_with_changed_original_can_be_reviewed_again(
    tmp_path, monkeypatch, whole, window
):
    preview = _existing_workspace_preview(tmp_path, whole)
    conflict = preview.conflict_paths[0]
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "backup_and_recreate", "context")
    real_rename = Path.rename

    def interrupt_before_move(path, target):
        if path == conflict:
            if window == "locked_folder_edit":
                (conflict / "operator.txt").write_text("operator saved edits", encoding="utf-8")
                raise PermissionError(5, "Access is denied", str(path))
            raise PowerLoss()
        return real_rename(path, target)

    monkeypatch.setattr(Path, "rename", interrupt_before_move)
    publisher = RecoverableWorkspacePublisher(journal, state)
    with pytest.raises(PermissionError if window == "locked_folder_edit" else PowerLoss):
        publisher.create(preview, "backup_and_recreate", SimpleNamespace(save=lambda record: record))
    if window == "persisted_checkpoint":
        (conflict / "operator.txt").write_text("operator saved edits", encoding="utf-8")
        monkeypatch.setattr(Path, "rename", real_rename)
        with pytest.raises(ValueError, match="fresh preview"):
            RecoverableWorkspacePublisher(journal, journal.read("p")).recover(
                SimpleNamespace(save=lambda record: record)
            )

    assert (conflict / "operator.txt").read_text(encoding="utf-8") == "operator saved edits"
    assert not list(tmp_path.rglob("*.connlab-backup-*"))
    assert not preview.manifest_path.exists()
    assert journal.read("p")["effects"] == {}
    assert not list((tmp_path / ".connlab" / "generation").rglob("*-workspace"))
    assert not list((tmp_path / ".connlab" / "generation").rglob("*-source-book"))


@pytest.mark.parametrize("guard", [
    "backup", "foreign_stage", "outside_stage", "changed_stage", "source_book_content",
    "missing_identity", "manifest_effect", "completed_workspace", "context_changed",
])
def test_changed_original_does_not_release_unproven_workspace_publication(
    tmp_path, monkeypatch, guard
):
    preview = _existing_workspace_preview(tmp_path, False)
    conflict = preview.conflict_paths[0]
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "backup_and_recreate", "context")
    real_rename = Path.rename

    def stop_before_move(path, target):
        if path == conflict:
            raise PowerLoss()
        return real_rename(path, target)

    monkeypatch.setattr(Path, "rename", stop_before_move)
    with pytest.raises(PowerLoss):
        RecoverableWorkspacePublisher(journal, state).create(
            preview, "backup_and_recreate", SimpleNamespace(save=lambda record: record)
        )
    monkeypatch.setattr(Path, "rename", real_rename)
    state = journal.read("p")
    effect = state["effects"]["workspace"]
    stage = Path(effect["stage"])
    (conflict / "operator.txt").write_text("operator edits", encoding="utf-8")
    if guard == "backup":
        backup = Path(effect["backup"])
        backup.mkdir()
        (backup / "retained.txt").write_text("backup", encoding="utf-8")
    elif guard == "foreign_stage":
        stage.rename(stage.with_name("owned-original"))
        stage.mkdir()
        (stage / "template.txt").write_text("new", encoding="utf-8")
    elif guard == "outside_stage":
        outside = tmp_path / "outside-stage"
        stage.rename(outside)
        stage = outside
        effect["stage"] = str(outside)
    elif guard == "changed_stage":
        (stage / "operator.txt").write_text("do not delete", encoding="utf-8")
    elif guard == "source_book_content":
        (Path(effect["source_book_stage"]) / "operator.txt").write_text("do not delete", encoding="utf-8")
    elif guard == "missing_identity":
        effect.pop("existing_target_identity")
    elif guard == "manifest_effect":
        state["effects"]["workspace:manifest"] = {"step": "workspace"}
    elif guard == "completed_workspace":
        state["completed_steps"].append("workspace")
    journal.save(state)

    def verify_context():
        if guard == "context_changed":
            raise ValueError("Generation inputs changed")

    with pytest.raises(ValueError):
        RecoverableWorkspacePublisher(journal, journal.read("p"), verify_context).recover(
            SimpleNamespace(save=lambda record: record)
        )

    assert stage.is_dir()
    assert (stage / "template.txt").read_text(encoding="utf-8") == "new"
    assert Path(effect["source_book_stage"]).is_dir()
    assert (conflict / "operator.txt").read_text(encoding="utf-8") == "operator edits"
    assert journal.read("p")["effects"] == state["effects"]
    if guard == "backup":
        assert (Path(effect["backup"]) / "retained.txt").read_text(encoding="utf-8") == "backup"


@pytest.mark.parametrize("existing_empty", [False, True])
def test_workspace_recovers_directory_manifest_and_database_gap(tmp_path, existing_empty):
    template = tmp_path / "template"
    template.mkdir()
    (template / "original.txt").write_text("template", encoding="utf-8")
    workspace = tmp_path / "DL1"
    if existing_empty:
        workspace.mkdir()
    preview = OfficialWorkspacePreview(
        project_id="p", dl_number="DL1", local_workspace_root=tmp_path,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=workspace / "official",
        manifest_path=workspace / ".connlab" / "manifest.json", template_root_mode="template_root",
        status="adoptable" if existing_empty else "ready", blockers=(), warnings=(), planned_paths=(),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", None, "context")
    publisher = RecoverableWorkspacePublisher(journal, state)
    def interrupted_save(_):
        raise PowerLoss()
    with pytest.raises(PowerLoss):
        publisher.create(preview, None, SimpleNamespace(save=interrupted_save))
    before = (workspace / "official" / "original.txt").stat().st_mtime_ns
    records = []
    recovered = RecoverableWorkspacePublisher(journal, journal.read("p"))
    recovered.recover(SimpleNamespace(save=lambda record: records.append(record) or record))
    assert len(records) == 1
    assert records[0].project_id == "p"
    assert preview.manifest_path.is_file()
    assert (workspace / "official" / "original.txt").stat().st_mtime_ns == before


def test_locked_conflict_leaves_operator_folder_unchanged_and_restartable(
    tmp_path, monkeypatch
):
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new", encoding="utf-8")
    workspace = tmp_path / "DL1"
    workspace.mkdir()
    (workspace / "operator.txt").write_text("keep", encoding="utf-8")
    preview = OfficialWorkspacePreview(
        project_id="p",
        dl_number="DL1",
        local_workspace_root=tmp_path,
        local_workspace_path=workspace,
        source_book_path=workspace / "Source Book",
        template_path=template,
        official_folder_path=workspace / "official",
        manifest_path=workspace / ".connlab" / "manifest.json",
        template_root_mode="template_root",
        status="exists",
        blockers=(f"Local project workspace already exists: {workspace}",),
        warnings=(),
        planned_paths=(),
        conflict_paths=(workspace,),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "backup_and_recreate", "context")
    real_rename = Path.rename

    def fail_locked_conflict(path, target):
        if path == workspace:
            raise PermissionError(5, "Access is denied", str(path))
        return real_rename(path, target)

    monkeypatch.setattr(Path, "rename", fail_locked_conflict)
    publisher = RecoverableWorkspacePublisher(journal, state)

    with pytest.raises(PermissionError, match="Access is denied"):
        publisher.create(
            preview,
            "backup_and_recreate",
            SimpleNamespace(save=lambda record: record),
        )

    assert (workspace / "operator.txt").read_text(encoding="utf-8") == "keep"
    assert not list(tmp_path.glob("DL1.connlab-backup-*"))
    # A failure before the old folder moves has no external effect. Its staged
    # effect must not make the operation permanently non-replaceable.
    assert journal.read("p")["effects"] == {}
    assert not list((tmp_path / ".connlab" / "generation").rglob("*-workspace"))


def test_recoverable_continue_existing_adds_only_missing_template_content(tmp_path):
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new", encoding="utf-8")
    workspace = tmp_path / "DL1"
    official = workspace / "official"
    official.mkdir(parents=True)
    (official / "operator.txt").write_text("keep", encoding="utf-8")
    preview = OfficialWorkspacePreview(
        project_id="p",
        dl_number="DL1",
        local_workspace_root=tmp_path,
        local_workspace_path=workspace,
        source_book_path=workspace / "Source Book",
        template_path=template,
        official_folder_path=official,
        manifest_path=workspace / ".connlab" / "manifest.json",
        template_root_mode="template_root",
        status="exists",
        blockers=(f"Official project folder already exists: {official}",),
        warnings=(),
        planned_paths=(),
        conflict_paths=(official,),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "continue_existing", "context")
    records = []

    result = RecoverableWorkspacePublisher(journal, state).create(
        preview,
        "continue_existing",
        SimpleNamespace(save=lambda record: records.append(record) or record),
    )

    assert result.record == records[0]
    assert (official / "operator.txt").read_text(encoding="utf-8") == "keep"
    assert (official / "template.txt").read_text(encoding="utf-8") == "new"
    assert preview.source_book_path.is_dir()
    assert preview.manifest_path.is_file()
    assert not list(workspace.glob("*Backup*"))
    assert not list((tmp_path / ".connlab" / "generation").rglob("*-workspace"))


def test_continue_existing_does_not_read_operator_files_before_adding_missing_content(
    tmp_path, monkeypatch
):
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new", encoding="utf-8")
    workspace = tmp_path / "DL1"
    official = workspace / "official"
    official.mkdir(parents=True)
    (official / "open-report.docx").write_text("operator", encoding="utf-8")
    preview = OfficialWorkspacePreview(
        project_id="p", dl_number="DL1", local_workspace_root=tmp_path,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=official,
        manifest_path=workspace / ".connlab" / "manifest.json",
        template_root_mode="template_root", status="exists",
        blockers=("Existing folder",), warnings=(), planned_paths=(),
        conflict_paths=(official,),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "continue_existing", "context")
    from backend.infrastructure.files import recoverable_workspace_publisher as module
    real_tree_hash = module.tree_hash

    def unreadable_operator_tree(path):
        if path == official:
            raise PermissionError(5, "Access is denied", str(path))
        return real_tree_hash(path)

    monkeypatch.setattr(module, "tree_hash", unreadable_operator_tree)

    RecoverableWorkspacePublisher(journal, state).create(
        preview, "continue_existing", SimpleNamespace(save=lambda record: record)
    )

    assert (official / "open-report.docx").read_text(encoding="utf-8") == "operator"
    assert (official / "template.txt").read_text(encoding="utf-8") == "new"


def test_continue_existing_recovers_if_interrupted_after_missing_content_is_added(
    tmp_path, monkeypatch
):
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new", encoding="utf-8")
    workspace = tmp_path / "DL1"
    official = workspace / "official"
    official.mkdir(parents=True)
    (official / "operator.txt").write_text("keep", encoding="utf-8")
    preview = OfficialWorkspacePreview(
        project_id="p", dl_number="DL1", local_workspace_root=tmp_path,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=official,
        manifest_path=workspace / ".connlab" / "manifest.json",
        template_root_mode="template_root", status="exists",
        blockers=("Existing folder",), warnings=(), planned_paths=(),
        conflict_paths=(official,),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("p", "continue_existing", "context")
    from backend.infrastructure.files import recoverable_workspace_publisher as module
    real_merge = module.merge_missing_workspace_tree

    def interrupted_merge(source, target):
        real_merge(source, target)
        raise PowerLoss()

    monkeypatch.setattr(module, "merge_missing_workspace_tree", interrupted_merge)
    with pytest.raises(PowerLoss):
        RecoverableWorkspacePublisher(journal, state).create(
            preview, "continue_existing", SimpleNamespace(save=lambda record: record)
        )
    monkeypatch.setattr(module, "merge_missing_workspace_tree", real_merge)
    records = []

    RecoverableWorkspacePublisher(journal, journal.read("p")).recover(
        SimpleNamespace(save=lambda record: records.append(record) or record)
    )

    assert len(records) == 1
    assert (official / "operator.txt").read_text(encoding="utf-8") == "keep"
    assert (official / "template.txt").read_text(encoding="utf-8") == "new"
    assert preview.manifest_path.is_file()
