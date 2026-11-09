from pathlib import Path

import pytest

from backend.infrastructure.files.basic_project_workspace_publisher import BasicProjectWorkspaceJournal, BasicMaterialPublisher


def test_failed_source_copy_leaves_no_syncable_partial_stage(tmp_path, monkeypatch):
    import backend.infrastructure.files.recoverable_output_publisher as output
    source = tmp_path / "source.pdf"
    source.write_bytes(b"complete source")
    folder = tmp_path / "business"
    folder.mkdir()
    journal = BasicProjectWorkspaceJournal(tmp_path / "journal")
    state = journal.create("P1", None, "context")
    def fail(input_file, destination):
        destination.write(b"partial")
        raise PermissionError("source disconnected")
    monkeypatch.setattr(output.shutil, "copyfileobj", fail)
    with pytest.raises(PermissionError):
        BasicMaterialPublisher(journal, state, "materials").publish_file("source", source, folder / "source.pdf", None)
    assert list(folder.iterdir()) == []


def test_basic_journal_failure_is_not_an_ordinary_file_error(tmp_path, monkeypatch):
    from backend.infrastructure.files.generation_journal import GenerationJournal
    journal = BasicProjectWorkspaceJournal(tmp_path / "journal")
    state = journal.create("P1", None, "context")
    monkeypatch.setattr(GenerationJournal, "_write", lambda *_: (_ for _ in ()).throw(OSError("journal unavailable")))
    with pytest.raises(ValueError, match="recovery journal"):
        journal.save(state)
