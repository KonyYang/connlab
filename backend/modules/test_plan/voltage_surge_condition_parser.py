"""Canonical pin-scoped Voltage surge condition extraction."""

from __future__ import annotations

import re

_POWER_PIN_PATTERN = re.compile(r"\bpower\s+pin\b", re.IGNORECASE)
_SIGNAL_NOT_INVOLVED_PATTERN = re.compile(
    r"\bsignal\s+pin\s*:\s*not\s+involved\b",
    re.IGNORECASE,
)
_DIFFERENTIAL_PATTERN = re.compile(
    r"\bdifferential\s+mode\s*[:\-–—]?\s*(?P<value>\d+(?:\.\d+)?)\s*k\s*a\b",
    re.IGNORECASE,
)
_COMMON_PATTERN = re.compile(
    r"\bcommon\s+mode\s*[:\-–—]?\s*(?P<value>\d+(?:\.\d+)?)\s*k\s*a\b",
    re.IGNORECASE,
)
_WAVEFORM_PATTERN = re.compile(
    r"\bwaveform\s*[:\-–—]?\s*(?P<value>\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?)\s*"
    r"(?:μs|µs|us)\b",
    re.IGNORECASE,
)


def extract_voltage_surge_condition(text: str) -> str | None:
    """Return only label-bound Power Pin and Signal Pin surge facts."""
    normalized = " ".join((text or "").split())
    if not normalized:
        return None

    segments: list[str] = []
    if _POWER_PIN_PATTERN.search(normalized):
        power_parts: list[str] = []
        differential = _unique_value(_DIFFERENTIAL_PATTERN, normalized)
        common = _unique_value(_COMMON_PATTERN, normalized)
        waveform = _unique_value(_WAVEFORM_PATTERN, normalized)
        if differential is not None:
            power_parts.append(f"Differential Mode {differential} kA")
        if common is not None:
            power_parts.append(f"Common Mode {common} kA")
        if waveform is not None:
            power_parts.append(f"Waveform {waveform.replace(' ', '')} μs")
        segments.append("Power Pin" + (f": {'; '.join(power_parts)}" if power_parts else ""))

    if _SIGNAL_NOT_INVOLVED_PATTERN.search(normalized):
        segments.append("Signal Pin: Not involved")
    return "; ".join(segments) or None


def _unique_value(pattern: re.Pattern[str], text: str) -> str | None:
    values = {match.group("value") for match in pattern.finditer(text)}
    if len(values) != 1:
        return None
    return values.pop()
