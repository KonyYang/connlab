from __future__ import annotations

from backend.modules.test_plan.matrix_step_sequence_validation import (
    parse_step_tokens,
    validate_group_step_sequences,
)


def test_parse_step_tokens_extracts_sequence_and_suffix() -> None:
    parsed, warnings = parse_step_tokens("1 3(a),4(b)\n5")
    assert warnings == ()
    assert [item.sequence for item in parsed] == [1, 3, 4, 5]
    assert [item.suffix_note for item in parsed] == [None, "(a)", "(b)", None]


def test_parse_step_tokens_reports_invalid_values() -> None:
    parsed, warnings = parse_step_tokens("A, B")
    assert parsed == ()
    assert "No valid numeric step token was found." in warnings


def test_validate_group_step_sequences_reports_duplicates_and_gaps() -> None:
    blockers = validate_group_step_sequences("Group 1", [1, 2, 2, 4])
    assert "Group 1: duplicate step sequence 2." in blockers
    assert "Group 1: missing step sequence between 2 and 4." in blockers
