"""Pure domain values for grouped lookup options."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LookupOption:
    """One selectable value in a backend-managed lookup group."""

    option_id: str
    group_key: str
    value: str
    label: str
    sort_order: int
    active: bool = True
