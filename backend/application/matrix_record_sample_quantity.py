"""Resolve record-specific sample counts without flattening split allocations."""

from __future__ import annotations

import re

_POSITIVE_INTEGER = re.compile(r"^[1-9][0-9]*$")
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
    if _POSITIVE_INTEGER.fullmatch(normalized_expression):
        return int(normalized_expression)
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
