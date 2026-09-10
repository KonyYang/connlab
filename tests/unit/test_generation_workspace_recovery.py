from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.official_project_workspace_service import OfficialWorkspacePreview
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.files.recoverable_workspace_publisher import RecoverableWorkspacePublisher


class PowerLoss(BaseException):
    pass


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
