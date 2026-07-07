"""Deterministic helpers for Matrix planning day and schedule validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import re
from typing import Iterable, Mapping


class MatrixScheduleValidationError(ValueError):
    """Raised when Matrix planning values fail validation."""


@dataclass(frozen=True, slots=True)
class ParsedDayExpression:
    """Parsed row-level planned day expression."""

    value: Decimal
    multiplier: bool


@dataclass(frozen=True, slots=True)
class MatrixScheduleFields:
    """Root-level Matrix planning schedule fields."""

    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixScheduleValidationResult:
    """Validated schedule calculation result."""

    critical_group_id: str | None
    critical_group_test_days: Decimal
    total_cycle_days: Decimal


def parse_day_expression(value: str | None) -> ParsedDayExpression | None:
    """Parse an editable row Day expression."""
    text = (value or "").strip()
    if not text:
        return None
    multiplier = text.lower().endswith("x")
    number_text = text[:-1] if multiplier else text
    parsed = _parse_non_negative_decimal(number_text, value_name="Day")
    return ParsedDayExpression(value=parsed, multiplier=multiplier)


def parse_buffer_days(value: str | None, *, value_name: str) -> Decimal:
    """Parse a root-level non-negative buffer day value; blank means zero."""
    text = (value or "").strip()
    if not text:
        return Decimal("0")
    if text.lower().endswith("x"):
        raise MatrixScheduleValidationError(f"{value_name} must be a non-negative decimal.")
    return _parse_non_negative_decimal(text, value_name=value_name)


def count_step_tokens(cell_value: str | None) -> int:
    """Count step-like tokens using the Matrix Editor comma/space token convention."""
    text = (cell_value or "").strip()
    if not text:
        return 0
    return len([token for token in re.split(r"[\s,，、\u040e\u045e]+", text) if token.strip()])


def calculate_group_test_days(
    *,
    rows: Iterable[Mapping[str, object]],
    cells: Iterable[Mapping[str, object]],
    selected_group_ids: Iterable[str],
) -> dict[str, Decimal]:
    """Calculate planned test days by selected group id."""
    selected = [group_id for group_id in selected_group_ids if group_id]
    totals = {group_id: Decimal("0") for group_id in selected}
    selected_set = set(selected)
    active_row_ids: set[str] = set()
    cell_payloads: list[Mapping[str, object]] = []
    for cell in cells:
        cell_payloads.append(cell)
        row_id = str(cell.get("row_id") or cell.get("draft_row_id") or "")
        group_id = str(cell.get("group_id") or cell.get("draft_group_id") or "")
        if group_id not in selected_set:
            continue
        if count_step_tokens(_optional_string(cell.get("cell_value"))) > 0:
            active_row_ids.add(row_id)
    row_day_by_id: dict[str, ParsedDayExpression] = {}
    for row in rows:
        if bool(row.get("is_sample_row")) or bool(row.get("is_information_row")):
            continue
        row_id = str(row.get("row_id") or row.get("draft_row_id") or "")
        if not row_id or row_id not in active_row_ids:
            continue
        parsed = parse_day_expression(_optional_string(row.get("day_expression")))
        if parsed is not None:
            row_day_by_id[row_id] = parsed
    for cell in cell_payloads:
        row_id = str(cell.get("row_id") or cell.get("draft_row_id") or "")
        group_id = str(cell.get("group_id") or cell.get("draft_group_id") or "")
        if group_id not in selected_set:
            continue
        parsed = row_day_by_id.get(row_id)
        if parsed is None:
            continue
        token_count = count_step_tokens(_optional_string(cell.get("cell_value")))
        if token_count == 0:
            continue
        contribution = parsed.value * Decimal(token_count) if parsed.multiplier else parsed.value
        totals[group_id] += contribution
    return totals


def validate_planned_schedule(
    *,
    fields: MatrixScheduleFields,
    group_test_days: Mapping[str, Decimal],
) -> MatrixScheduleValidationResult:
    """Validate root schedule fields against calculated group days."""
    post_days = parse_buffer_days(fields.post_test_buffer_days, value_name="Post-test buffer days")
    critical_group_id, critical_days = _critical_group(group_test_days)
    total_cycle_days = critical_days + post_days
    dates = _parse_planned_dates(fields)
    if dates is None:
        return MatrixScheduleValidationResult(
            critical_group_id=critical_group_id,
            critical_group_test_days=critical_days,
            total_cycle_days=total_cycle_days,
        )
    received, start, complete, estimated = dates
    _require_date_at_least(
        actual=start,
        minimum=received,
        message="planned_test_start_date is earlier than sample_received_date.",
    )
    _require_date_at_least(
        actual=complete,
        minimum=start + timedelta(days=_ceil_days(critical_days)),
        message="planned_test_complete_date is earlier than planned_test_start_date plus critical group test days.",
    )
    _require_date_at_least(
        actual=estimated,
        minimum=complete + timedelta(days=_ceil_days(post_days)),
        message="estimated_completion_date is earlier than planned_test_complete_date plus post-test buffer days.",
    )
    return MatrixScheduleValidationResult(
        critical_group_id=critical_group_id,
        critical_group_test_days=critical_days,
        total_cycle_days=total_cycle_days,
    )


def _parse_non_negative_decimal(value: str, *, value_name: str) -> Decimal:
    text = value.strip()
    if not re.fullmatch(r"\d+(?:\.\d+)?", text):
        raise MatrixScheduleValidationError(f"{value_name} must be a non-negative decimal.")
    try:
        parsed = Decimal(text)
    except InvalidOperation as exc:
        raise MatrixScheduleValidationError(f"{value_name} must be a non-negative decimal.") from exc
    if parsed < 0:
        raise MatrixScheduleValidationError(f"{value_name} must be non-negative.")
    return parsed


def _parse_planned_dates(
    fields: MatrixScheduleFields,
) -> tuple[date, date, date, date] | None:
    values = [
        fields.sample_received_date,
        fields.planned_test_start_date,
        fields.planned_test_complete_date,
        fields.estimated_completion_date,
    ]
    filled = [(value or "").strip() for value in values]
    if not any(filled):
        return None
    if not all(filled):
        raise MatrixScheduleValidationError(
            "All planned date fields are required when any planned date is filled."
        )
    try:
        return tuple(date.fromisoformat(value) for value in filled)  # type: ignore[return-value]
    except ValueError as exc:
        raise MatrixScheduleValidationError("Planned dates must use YYYY-MM-DD format.") from exc


def _critical_group(group_test_days: Mapping[str, Decimal]) -> tuple[str | None, Decimal]:
    if not group_test_days:
        return None, Decimal("0")
    group_id, days = max(group_test_days.items(), key=lambda item: (item[1], item[0]))
    return group_id, days


def _ceil_days(value: Decimal) -> int:
    if value <= 0:
        return 0
    return int(value.to_integral_value(rounding=ROUND_CEILING))


def _require_date_at_least(*, actual: date, minimum: date, message: str) -> None:
    if actual < minimum:
        raise MatrixScheduleValidationError(message)


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) else None
