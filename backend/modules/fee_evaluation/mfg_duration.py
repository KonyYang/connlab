"""Resolve MFG fee duration from explicit days or labeled phase hours."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re

_DAY_PATTERN = re.compile(
    r"(?<![a-z])(\d+(?:\.\d+)?)\s*(?:d|day|days)\b",
    re.IGNORECASE,
)
_CLASS_IIA_PATTERN = re.compile(r"\bclass\s+iia\b", re.IGNORECASE)
_HOUR_VALUE = r"(?P<value>\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours)\b"
_HOURS_PER_DAY = Decimal("24")


def resolve_mfg_duration_days(
    text: str,
    *,
    class_confirmed: bool = False,
) -> Decimal | None:
    """Return exact MFG days only when the duration authority is complete."""
    normalized = " ".join((text or "").split())
    explicit_days = _DAY_PATTERN.search(normalized)
    if explicit_days:
        return _decimal(explicit_days.group(1))
    if not class_confirmed and not _CLASS_IIA_PATTERN.search(normalized):
        return None

    unmated_hours = _phase_hours(normalized, phase="unmated")
    mated_hours = _phase_hours(normalized, phase="mated")
    if (
        unmated_hours is None
        or mated_hours is None
        or unmated_hours <= 0
        or mated_hours <= 0
    ):
        return None
    return (unmated_hours + mated_hours) / _HOURS_PER_DAY


def _phase_hours(text: str, *, phase: str) -> Decimal | None:
    label = rf"\b{phase}\b"
    label_before = re.compile(
        rf"{label}(?:\s+condition)?\s*(?:for|duration|:|-)?\s*{_HOUR_VALUE}",
        re.IGNORECASE,
    )
    value_before = re.compile(
        rf"{_HOUR_VALUE}\s*{label}",
        re.IGNORECASE,
    )
    values = {
        parsed
        for match in (*label_before.finditer(text), *value_before.finditer(text))
        if (parsed := _decimal(match.group("value"))) is not None
    }
    if len(values) != 1:
        return None
    return values.pop()


def _decimal(value: str) -> Decimal | None:
    try:
        return Decimal(value)
    except InvalidOperation:
        return None
