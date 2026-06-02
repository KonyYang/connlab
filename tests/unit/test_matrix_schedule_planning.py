"""Tests for Matrix schedule planning helpers."""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.application.matrix_schedule_planning import (
    MatrixScheduleFields,
    MatrixScheduleValidationError,
    calculate_group_test_days,
    parse_buffer_days,
    parse_day_expression,
    validate_planned_schedule,
)


def test_parse_plain_decimal_day_expression() -> None:
    parsed = parse_day_expression("0.5")

    assert parsed is not None
    assert parsed.multiplier is False
    assert parsed.value == Decimal("0.5")


def test_parse_multiplier_day_expression() -> None:
    parsed = parse_day_expression("0.5x")

    assert parsed is not None
    assert parsed.multiplier is True
    assert parsed.value == Decimal("0.5")


@pytest.mark.parametrize("value", ["abc", "x", "0.x", "-1", "1xx"])
def test_parse_rejects_invalid_day_expression(value: str) -> None:
    with pytest.raises(MatrixScheduleValidationError):
        parse_day_expression(value)


def test_multiplier_day_expression_counts_group_tokens() -> None:
    totals = calculate_group_test_days(
        rows=[{"row_id": "r1", "day_expression": "0.5x"}],
        cells=[{"row_id": "r1", "group_id": "g1", "cell_value": "2,7"}],
        selected_group_ids=["g1"],
    )

    assert totals["g1"] == Decimal("1.0")


def test_plain_day_expression_counts_once_when_group_has_tokens() -> None:
    totals = calculate_group_test_days(
        rows=[{"row_id": "r1", "day_expression": "1"}],
        cells=[
            {"row_id": "r1", "group_id": "g1", "cell_value": "2,7"},
            {"row_id": "r1", "group_id": "g2", "cell_value": ""},
        ],
        selected_group_ids=["g1", "g2"],
    )

    assert totals == {"g1": Decimal("1"), "g2": Decimal("0")}


def test_information_and_sample_rows_do_not_contribute_days() -> None:
    totals = calculate_group_test_days(
        rows=[
            {"row_id": "r1", "day_expression": "10", "is_information_row": True},
            {"row_id": "r2", "day_expression": "10", "is_sample_row": True},
        ],
        cells=[
            {"row_id": "r1", "group_id": "g1", "cell_value": "1"},
            {"row_id": "r2", "group_id": "g1", "cell_value": "2"},
        ],
        selected_group_ids=["g1"],
    )

    assert totals["g1"] == Decimal("0")


def test_invalid_day_expression_is_ignored_when_row_has_no_selected_group_tokens() -> None:
    totals = calculate_group_test_days(
        rows=[{"row_id": "r1", "day_expression": "bad"}],
        cells=[
            {"row_id": "r1", "group_id": "g1", "cell_value": ""},
            {"row_id": "r1", "group_id": "g2", "cell_value": "1"},
        ],
        selected_group_ids=["g1"],
    )

    assert totals["g1"] == Decimal("0")


def test_invalid_day_expression_blocks_when_selected_group_has_tokens() -> None:
    with pytest.raises(MatrixScheduleValidationError):
        calculate_group_test_days(
            rows=[{"row_id": "r1", "day_expression": "bad"}],
            cells=[{"row_id": "r1", "group_id": "g1", "cell_value": "1"}],
            selected_group_ids=["g1"],
        )


def test_buffer_days_accept_blank_as_zero_and_reject_multiplier() -> None:
    assert parse_buffer_days("", value_name="Pre-test buffer days") == Decimal("0")
    with pytest.raises(MatrixScheduleValidationError):
        parse_buffer_days("0.5x", value_name="Pre-test buffer days")


def test_schedule_validation_uses_calendar_day_ceiling_for_decimal_days() -> None:
    with pytest.raises(MatrixScheduleValidationError):
        validate_planned_schedule(
            fields=MatrixScheduleFields(
                pre_test_buffer_days="1",
                post_test_buffer_days="1",
                sample_received_date="2026-06-01",
                planned_test_start_date="2026-06-02",
                planned_test_complete_date="2026-06-04",
                estimated_completion_date="2026-06-05",
            ),
            group_test_days={"g1": Decimal("2.5")},
        )

    result = validate_planned_schedule(
        fields=MatrixScheduleFields(
            pre_test_buffer_days="1",
            post_test_buffer_days="1",
            sample_received_date="2026-06-01",
            planned_test_start_date="2026-06-02",
            planned_test_complete_date="2026-06-05",
            estimated_completion_date="2026-06-06",
        ),
        group_test_days={"g1": Decimal("2.5")},
    )

    assert result.critical_group_id == "g1"
    assert result.total_cycle_days == Decimal("4.5")


def test_schedule_validation_requires_all_dates_when_any_date_is_filled() -> None:
    with pytest.raises(MatrixScheduleValidationError):
        validate_planned_schedule(
            fields=MatrixScheduleFields(sample_received_date="2026-06-01"),
            group_test_days={},
        )
