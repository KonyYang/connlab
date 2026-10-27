"""Exact recovered values survive the journal's public persistence boundary."""
from decimal import Decimal, localcontext

import pytest

from backend.infrastructure.files.generation_journal import GenerationJournal, fingerprint


def test_recovered_decimal_context_and_effects_round_trip_without_precision_loss(tmp_path):
    durations = {"duration_value": Decimal("2.5000000000"),
                 "normalized_hours": Decimal("2.5000000000")}
    payload = {"matrix": {"duration_authorities": [durations]}}
    with localcontext() as context:
        context.prec = 3
        signature = fingerprint(payload)
    assert signature == fingerprint(payload)

    journal = GenerationJournal(tmp_path / "journals")
    state = journal.create("restored-project", None, signature)
    state["effects"] = {"duration": durations,
                        "measurement": Decimal("0.0855111111111111")}
    journal.save(state)

    reloaded = GenerationJournal(journal.root).read("restored-project")
    assert reloaded["context"] == signature
    assert reloaded["effects"] == {
        "duration": {"duration_value": "2.5000000000", "normalized_hours": "2.5000000000"},
        "measurement": "0.0855111111111111",
    }
    assert durations["duration_value"].as_tuple() == Decimal("2.5000000000").as_tuple()
    journal.create("restored-project", None, "next-progress")
    assert journal.read_archived("restored-project", state["operation_id"]) == reloaded


def test_unknown_effect_does_not_replace_a_recoverable_journal(tmp_path):
    journal = GenerationJournal(tmp_path / "journals")
    state = journal.create("legacy-project", None, "existing-context")
    state["effects"] = {"kept": [1, True, None, "original"]}
    journal.save(state)
    unsupported = {**state, "effects": {"unknown": object()}}
    with pytest.raises(TypeError):
        journal.save(unsupported)
    assert GenerationJournal(journal.root).read("legacy-project") == state
