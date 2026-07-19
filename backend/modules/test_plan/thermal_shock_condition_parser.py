"""Canonical Thermal Shock condition extraction from specification text."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re

_METHOD_PATTERN = re.compile(r"\bmethod\s+(?P<value>[A-Z])\b", re.IGNORECASE)
_TEMPERATURE_DWELL_PATTERN = re.compile(
    r"(?P<temperature>[+-]?\d+(?:\.\d+)?)\s*(?:°\s*)?(?:℃|C)\s*"
    r"\(\s*(?P<minutes>\d+(?:\.\d+)?)\s*(?:min|mins|minute|minutes)\s*\)",
    re.IGNORECASE,
)
_CYCLE_PATTERN = re.compile(
    r"\brepeat\s+(?P<value>\d+(?:\.\d+)?)\s*cycles?\b",
    re.IGNORECASE,
)
_MINUTES_PER_HOUR = Decimal("60")


def extract_thermal_shock_condition(text: str) -> str | None:
    """Return source-supported schedule facts and derive only complete dwell hours."""
    normalized = " ".join((text or "").split())
    if not normalized:
        return None

    method = _unique_text(_METHOD_PATTERN, normalized, uppercase=True)
    cycles = _unique_decimal(_CYCLE_PATTERN, normalized)
    pairs = _unambiguous_temperature_dwells(normalized)

    schedule_parts: list[str] = []
    if method is not None:
        schedule_parts.append(f"Method {method}")
    schedule_parts.extend(
        f"{temperature} ℃ ({_format_decimal(minutes)} min)"
        for temperature, minutes in pairs
    )

    segments: list[str] = []
    if schedule_parts:
        segments.append(", ".join(schedule_parts))
    if cycles is not None:
        segments.append(f"repeat {_format_decimal(cycles)} cycles")
    if cycles is not None and len(pairs) == 2:
        total_hours = cycles * sum((minutes for _, minutes in pairs), Decimal("0"))
        total_hours /= _MINUTES_PER_HOUR
        segments.append(f"total {_format_decimal(total_hours)} hours")
    return "; ".join(segments) or None


def _unambiguous_temperature_dwells(text: str) -> tuple[tuple[str, Decimal], ...]:
    ordered_temperatures: list[str] = []
    dwell_values: dict[str, set[Decimal]] = {}
    for match in _TEMPERATURE_DWELL_PATTERN.finditer(text):
        temperature = _format_temperature(match.group("temperature"))
        minutes = _decimal(match.group("minutes"))
        if minutes is None:
            continue
        if temperature not in dwell_values:
            ordered_temperatures.append(temperature)
            dwell_values[temperature] = set()
        dwell_values[temperature].add(minutes)
    return tuple(
        (temperature, next(iter(dwell_values[temperature])))
        for temperature in ordered_temperatures
        if len(dwell_values[temperature]) == 1
    )


def _unique_text(pattern: re.Pattern[str], text: str, *, uppercase: bool) -> str | None:
    values = {match.group("value") for match in pattern.finditer(text)}
    if len(values) != 1:
        return None
    value = values.pop()
    return value.upper() if uppercase else value


def _unique_decimal(pattern: re.Pattern[str], text: str) -> Decimal | None:
    values = {
        value
        for match in pattern.finditer(text)
        if (value := _decimal(match.group("value"))) is not None
    }
    if len(values) != 1:
        return None
    return values.pop()


def _decimal(value: str) -> Decimal | None:
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _format_temperature(value: str) -> str:
    sign = "+" if value.startswith("+") else "-" if value.startswith("-") else ""
    unsigned = value.lstrip("+-")
    parsed = _decimal(unsigned)
    return f"{sign}{_format_decimal(parsed)}" if parsed is not None else value


def _format_decimal(value: Decimal) -> str:
    formatted = format(value, "f")
    if "." in formatted:
        return formatted.rstrip("0").rstrip(".")
    return formatted
