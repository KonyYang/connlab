"""Durable publication is exercised only against temporary fixtures."""

from pathlib import Path

import pytest

from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.files.recoverable_output_publisher import RecoverableOutputPublisher


class PowerLoss(BaseException):
    pass


def test_publication_recovers_file_before_record_without_rewriting(tmp_path):
    journal = GenerationJournal(tmp_path / "jobs")
    state = journal.create("project", None, "inputs")
    source = tmp_path / "source.docx"
    source.write_bytes(b"complete document")
    target = tmp_path / "final.docx"
    publisher = RecoverableOutputPublisher(journal, state, "forms")
    publisher.publish_file("form", source, target, None, {"kind": "form"})
    before = target.stat().st_mtime_ns
    reloaded = journal.read("project")
    recovered = RecoverableOutputPublisher(GenerationJournal(tmp_path / "jobs"), reloaded, "forms")
    records = []
    recovered.recover_files(records.append)
    assert target.read_bytes() == b"complete document"
    assert target.stat().st_mtime_ns == before
    assert records == [{"kind": "form"}]
    assert not list(tmp_path.glob(".connlab-*.docx"))


def test_recovery_refuses_foreign_target_and_damaged_journal(tmp_path):
    journal = GenerationJournal(tmp_path / "jobs")
    state = journal.create("project", None, "inputs")
    source = tmp_path / "source"
    source.write_bytes(b"ours")
    target = tmp_path / "final"
    publisher = RecoverableOutputPublisher(journal, state, "forms")
    publisher.publish_file("form", source, target, None)
    target.write_bytes(b"foreign edit")
    with pytest.raises(ValueError, match="changed"):
        publisher.recover_files(lambda _: None)
    assert target.read_bytes() == b"foreign edit"
    (journal.project_path("project") / "operation.json").write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError, match="damaged"):
        GenerationJournal(tmp_path / "jobs").read("project")


def test_project_lock_is_shared_between_instances_and_released(tmp_path):
    first, second = GenerationJournal(tmp_path), GenerationJournal(tmp_path)
    with first.lock("p"):
        with pytest.raises(ValueError, match="already running"):
            with second.lock("p"):
                pass
    with second.lock("p"):
        assert second.read("p") is None


def test_matching_bytes_without_owned_file_identity_are_not_claimed(tmp_path):
    journal = GenerationJournal(tmp_path / "jobs")
    state = journal.create("p", None, "inputs")
    source, target = tmp_path / "source", tmp_path / "target"
    source.write_bytes(b"same bytes")
    publisher = RecoverableOutputPublisher(journal, state, "forms")
    publisher.publish_file("form", source, target, None)
    foreign = tmp_path / "foreign"
    foreign.write_bytes(b"same bytes")
    foreign.replace(target)
    with pytest.raises(ValueError, match="changed"):
        publisher.recover_files(lambda _: None)
    assert target.read_bytes() == b"same bytes"
