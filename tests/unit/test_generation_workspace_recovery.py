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
