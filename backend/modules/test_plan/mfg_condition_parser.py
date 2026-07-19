"""Canonical MFG condition extraction from one specification section."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re

_CLASS_PATTERN = re.compile(r"\bclass\s+(?P<value>[ivx]+a?)\b", re.IGNORECASE)
_HOUR_VALUE = r"(?P<value>\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours)\b"


def extract_mfg_condition(text: str) -> str | None:
    """Return only unambiguous Class and labeled phase-duration facts."""
    normalized = " ".join((text or "").split())
    if not normalized:
        return None

    segments: list[str] = []
    class_match = _CLASS_PATTERN.search(normalized)
    if class_match:
        segments.append(f"Class {class_match.group('value').upper()}")

    for phase in ("unmated", "mated"):
        hours = _phase_hours(normalized, phase=phase)
        if hours is not None:
            segments.append(f"{phase} {_format_decimal(hours)} hours")

    return "; ".join(segments) or None


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


def _format_decimal(value: Decimal) -> str:
    formatted = format(value, "f")
    if "." in formatted:
        return formatted.rstrip("0").rstrip(".")
    return formatted
