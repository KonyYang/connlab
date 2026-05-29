"""Shared selected-group sample quantity validation helpers."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Protocol


class SampleQuantityGroup(Protocol):
    """Structural protocol for selected-group sample quantity checks."""

    group_label: str
    group_key: str
    is_selected: bool
    sample_quantity_expression: str | None


@dataclass(frozen=True, slots=True)
class SampleQuantityViolation:
    """One selected group with invalid sample quantity expression."""

    group_label: str
    group_key: str


_DIGIT_PATTERN = re.compile(r"\d")


def find_selected_sample_quantity_violations(
    groups: tuple[SampleQuantityGroup, ...],
) -> tuple[SampleQuantityViolation, ...]:
    """Return selected groups whose sample quantity is blank or has no digit."""
    violations: list[SampleQuantityViolation] = []
    for group in groups:
        if not bool(group.is_selected):
            continue
        expression = (group.sample_quantity_expression or "").strip()
        if not expression or _DIGIT_PATTERN.search(expression) is None:
            label = group.group_label.strip() or group.group_key.strip() or "group"
            violations.append(
                SampleQuantityViolation(group_label=label, group_key=group.group_key.strip())
            )
    return tuple(violations)


def format_sample_quantity_violation_message(
    violations: tuple[SampleQuantityViolation, ...],
) -> str:
    """Build business-readable violation message for selected groups."""
    labels = ", ".join(item.group_label for item in violations)
    return f"Sample quantity is required for selected groups: {labels}."

