from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.official_project_workspace_service import OfficialWorkspacePreview
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.files.recoverable_workspace_publisher import RecoverableWorkspacePublisher


class PowerLoss(BaseException):
    pass


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
