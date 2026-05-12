"""Source-backed duration hint detection for test-plan text."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DurationHint:
    """One explicit duration phrase found in source text."""

    text: str
    source_text: str


class DurationHintParser:
    """Detect explicit duration hints without estimating missing values."""

    _PATTERN = re.compile(
        r"\b\d+(?:\.\d+)?\s*(?:hours?|hrs?|h|days?|d|minutes?|mins?)\b",
        re.IGNORECASE,
    )

    def first_hint(self, source_text: str | None) -> DurationHint | None:
        """Return the first explicit duration phrase from source text."""
        if not source_text:
            return None
        match = self._PATTERN.search(source_text)
        if match is None:
            return None
        return DurationHint(text=match.group(0), source_text=source_text)
