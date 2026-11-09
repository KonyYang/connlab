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


@pytest.mark.parametrize("failure", ["first_identity", "stage_hash", "final_identity"])
def test_stage_metadata_failure_is_blocking_and_cannot_orphan_syncable_file(tmp_path, monkeypatch, failure):
    import backend.infrastructure.files.recoverable_output_publisher as output
    source = tmp_path / "source.pdf"
    source.write_bytes(b"complete source")
    folder = tmp_path / "business"
    folder.mkdir()
    journal = BasicProjectWorkspaceJournal(tmp_path / "journal")
    state = journal.create("P1", None, "context")
    original_identity, original_hash = output.file_identity, output.file_hash
    calls = 0
    def identity(path):
        nonlocal calls
        if path.name.startswith(".connlab-"):
            calls += 1
            if (failure == "first_identity" and calls == 1) or (failure == "final_identity" and calls == 2):
                raise OSError("staged identity unavailable")
        return original_identity(path)
    def file_hash(path):
        if failure == "stage_hash" and path.name.startswith(".connlab-"):
            raise OSError("staged metadata unavailable")
        return original_hash(path)
    monkeypatch.setattr(output, "file_identity", identity)
    monkeypatch.setattr(output, "file_hash", file_hash)
    with pytest.raises(ValueError):
        BasicMaterialPublisher(journal, state, "materials").publish_file("source", source, folder / "source.pdf", None)
    assert not (folder / "source.pdf").exists()
    retained = BasicProjectWorkspaceJournal(journal.root).read("P1")
    assert not list(folder.iterdir()) or any(item.get("preparing") for item in retained["effects"].values())


def test_unknown_stage_identity_remains_durable_block_after_fresh_resume(tmp_path, monkeypatch):
    import backend.infrastructure.files.recoverable_output_publisher as output
    source = tmp_path / "source.pdf"
    source.write_bytes(b"source")
    folder = tmp_path / "business"
    folder.mkdir()
    journal = BasicProjectWorkspaceJournal(tmp_path / "journal")
    state = journal.create("P1", None, "context")
    original = output.os.fstat
    monkeypatch.setattr(output.os, "fstat", lambda *_: (_ for _ in ()).throw(OSError("opened identity unavailable")))
    with pytest.raises(ValueError):
        BasicMaterialPublisher(journal, state, "materials").publish_file("source", source, folder / "source.pdf", None)
    monkeypatch.setattr(output.os, "fstat", original)
    fresh_journal = BasicProjectWorkspaceJournal(journal.root)
    fresh_state = fresh_journal.read("P1")
    with pytest.raises(ValueError) as blocked:
        BasicMaterialPublisher(fresh_journal, fresh_state, "materials").recover_files(lambda _: None)
    assert not (folder / "source.pdf").exists()
    assert list(folder.iterdir())
    assert str(next(folder.iterdir())) in str(blocked.value)
    assert fresh_journal.read("P1")["effects"]
