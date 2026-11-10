from pathlib import Path

import pytest

from backend.infrastructure.files.project_file_generation_journal import ProjectFileGenerationJournal
from backend.infrastructure.files.recoverable_project_file_publisher import RecoverableProjectFilePublisher


def operation(journal):
    state = journal.create("p1", "request-1", "signature", "workspace", [])
    return state


def test_replacement_retains_verified_history_and_never_overwrites_new_target(tmp_path):
    journal = ProjectFileGenerationJournal(tmp_path / "journal")
    state = operation(journal)
    stage = tmp_path / "stage.xlsx"
    target = tmp_path / "work" / "form.xlsx"
    history = tmp_path / "History" / "Files" / "form.xlsx"
    target.parent.mkdir()
    stage.write_bytes(b"new workbook")
    target.write_bytes(b"operator workbook")
    publisher = RecoverableProjectFilePublisher(journal, state)
    effect = publisher.prepare(stage, target, history)
    publisher.publish(effect)
    assert target.read_bytes() == b"new workbook"
    assert history.read_bytes() == b"operator workbook"
    assert effect["phase"] == "published"
    target.unlink()
    target.write_bytes(b"manual replacement")
    with pytest.raises(ValueError, match="changed|reappeared"):
        publisher.publish(effect)
    assert target.read_bytes() == b"manual replacement"
    assert history.read_bytes() == b"operator workbook"


def test_new_file_publication_refuses_target_that_appeared_after_preview(tmp_path):
    journal = ProjectFileGenerationJournal(tmp_path / "journal")
    state = operation(journal)
    stage, target = tmp_path / "stage", tmp_path / "target"
    stage.write_bytes(b"generated")
    publisher = RecoverableProjectFilePublisher(journal, state)
    effect = publisher.prepare(stage, target, None)
    target.write_bytes(b"manual")
    with pytest.raises(ValueError, match="changed|reappeared"):
        publisher.publish(effect)
    assert target.read_bytes() == b"manual"


def test_dedicated_journal_retains_request_identity_after_new_operation(tmp_path):
    journal = ProjectFileGenerationJournal(tmp_path)
    first = operation(journal)
    first["status"] = "completed"
    journal.save(first)
    journal.create("p1", "request-2", "signature-2", "workspace", [])
    assert journal.find_request("p1", "request-1")["operation_id"] == first["operation_id"]
    path = journal.project_path("p1") / "operation.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="journal"):
        journal.read("p1")


def test_archive_move_race_retains_the_racing_file_and_refuses_publication(tmp_path, monkeypatch):
    import backend.infrastructure.files.recoverable_project_file_publisher as module
    journal = ProjectFileGenerationJournal(tmp_path / "journal")
    state = operation(journal)
    stage, target, backup = tmp_path / "stage", tmp_path / "target", tmp_path / "History" / "backup"
    stage.write_bytes(b"generated")
    target.write_bytes(b"reviewed")
    publisher = RecoverableProjectFilePublisher(journal, state)
    effect = publisher.prepare(stage, target, backup)
    real_move = module._move_without_replace

    def race(source, destination):
        source.unlink()
        source.write_bytes(b"colleague revision")
        real_move(source, destination)

    monkeypatch.setattr(module, "_move_without_replace", race)
    with pytest.raises(ValueError, match="backup changed"):
        publisher.publish(effect)
    assert backup.read_bytes() == b"colleague revision"
    assert stage.read_bytes() == b"generated"
    assert not target.exists()


def test_published_recovery_still_verifies_history_backup(tmp_path):
    journal = ProjectFileGenerationJournal(tmp_path / "journal")
    state = operation(journal)
    stage, target, backup = tmp_path / "stage", tmp_path / "target", tmp_path / "History" / "backup"
    stage.write_bytes(b"new")
    target.write_bytes(b"old")
    publisher = RecoverableProjectFilePublisher(journal, state)
    effect = publisher.prepare(stage, target, backup)
    publisher.publish(effect)
    backup.write_bytes(b"modified history")
    with pytest.raises(ValueError, match="backup changed"):
        publisher.publish(effect)
    assert target.read_bytes() == b"new"


def test_same_bytes_replaced_inode_does_not_satisfy_replacement_review(tmp_path):
    from backend.infrastructure.files.recoverable_output_publisher import file_identity, file_hash
    journal = ProjectFileGenerationJournal(tmp_path / "journal")
    state = operation(journal)
    stage, target, backup = tmp_path / "stage", tmp_path / "target", tmp_path / "backup"
    stage.write_bytes(b"new")
    target.write_bytes(b"old")
    reviewed_identity, reviewed_hash = file_identity(target), file_hash(target)
    target.rename(tmp_path / "retained-old")
    target.write_bytes(b"old")
    with pytest.raises(ValueError, match="identity|changed"):
        RecoverableProjectFilePublisher(journal, state).prepare(stage, target, backup,
            expected_prior=reviewed_hash, expected_identity=reviewed_identity)
    assert target.read_bytes() == b"old"


@pytest.mark.parametrize("replaced", ["stage", "target", "history"])
def test_parent_directory_replacement_stops_publication_without_touching_files(tmp_path, replaced):
    journal = ProjectFileGenerationJournal(tmp_path / "journal")
    state = operation(journal)
    for name in ("stage", "target", "history"):
        (tmp_path / name).mkdir()
    stage, target, backup = tmp_path / "stage" / "new", tmp_path / "target" / "old", tmp_path / "history" / "backup"
    stage.write_bytes(b"new")
    target.write_bytes(b"old")
    publisher = RecoverableProjectFilePublisher(journal, state)
    effect = publisher.prepare(stage, target, backup)
    directory = tmp_path / replaced
    retained = tmp_path / (replaced + "-retained")
    directory.rename(retained)
    directory.mkdir()
    with pytest.raises((ValueError, OSError)):
        publisher.publish(effect)
    if replaced == "stage":
        assert (retained / "new").read_bytes() == b"new"
    elif replaced == "target":
        assert (retained / "old").read_bytes() == b"old"
    else:
        assert target.read_bytes() == b"old"
    assert not backup.exists()
