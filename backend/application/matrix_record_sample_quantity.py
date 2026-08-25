"""Resolve record-specific sample counts without flattening split allocations."""

from __future__ import annotations

import re

_SIMPLE_POSITIVE_SAMPLE_COUNT = re.compile(
    r"^(?P<count>[1-9][0-9]*)\s*(?:\([A-Za-z]+\)\s*)*$"
)
_EXPRESSION_NUMBER = re.compile(r"[0-9]+")
_EXPLICIT_RECORD_ALLOCATION = re.compile(
    r"(?P<count>[1-9][0-9]*)\s*(?:pcs?|pieces?)\s+(?:for|to)\s+(?:the\s+)?"
    r"(?P<record>LLCR|CR)\b",
    re.IGNORECASE,
)


def resolve_matrix_record_sample_count(
    expression: str | None,
    sample_note: str | None,
    record_type: str,
) -> int | None:
    """Return one safe LLCR/CR count, or ``None`` when allocation is ambiguous."""
    normalized_expression = str(expression or "").strip()
    simple_count = parse_simple_positive_sample_count(normalized_expression)
    if simple_count is not None:
        return simple_count
    expected_record = (
        "LLCR" if record_type == "llcr" else "CR" if record_type == "cr" else None
    )
    if expected_record is None:
        return None
    expression_counts = {
        int(value) for value in _EXPRESSION_NUMBER.findall(normalized_expression)
    }
    allocations = {
        int(match.group("count"))
        for match in _EXPLICIT_RECORD_ALLOCATION.finditer(str(sample_note or ""))
        if match.group("record").upper() == expected_record
    }
    if len(allocations) != 1:
        return None
    resolved = next(iter(allocations))
    return resolved if resolved in expression_counts else None


def parse_simple_positive_sample_count(expression: object) -> int | None:
    """Parse one positive count with optional alphabetic footnote markers."""
    match = _SIMPLE_POSITIVE_SAMPLE_COUNT.fullmatch(str(expression or "").strip())
    return int(match.group("count")) if match else None
