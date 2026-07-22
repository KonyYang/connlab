"""Source-faithful Damp Heat condition extraction."""

from __future__ import annotations

import re

from backend.modules.test_plan.condition_text_collectors import collect_condition_segments

_DAMP_HEAT_LABELS = (
    "damp heat condition",
    "temperature",
    "humidity",
    "rh",
    "duration",
    "hours",
)
_CONDITION_FACT_PATTERNS = (
    re.compile(
        r"(?<![\w.])[+-]?\d+(?:\.\d+)?\s*(?:°\s*)?(?:℃|[CF])(?![A-Za-z])",
        re.IGNORECASE,
    ),
    re.compile(r"(?<![\w.])\d+(?:\.\d+)?\s*%\s*(?:RH\b)?", re.IGNORECASE),
    re.compile(
        r"(?<![\w.])\d+(?:\.\d+)?\s*(?:h|hr|hrs|hours?|days?|cycles?)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bdamp\s+heat\s+condition\s*:\s*(?:[A-Z]\d*|\d+)\b", re.IGNORECASE),
)


def extract_damp_heat_condition(text: str) -> str | None:
    """Return only explicit Damp Heat condition facts from source text."""
    condition = collect_condition_segments(text, _DAMP_HEAT_LABELS)
    if condition is None:
        return None
    segments = (
        segment
        for segment in condition.split("; ")
        if any(pattern.search(segment) for pattern in _CONDITION_FACT_PATTERNS)
    )
    return "; ".join(segments) or None
