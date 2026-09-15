"""Matrix group identity invariants shared by draft and authority workflows."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol


class MatrixGroupKey(Protocol):
    group_key: str


def find_duplicate_matrix_group_keys(groups: Iterable[MatrixGroupKey]) -> tuple[str, ...]:
    """Return normalized group keys that occur more than once, in encounter order."""
    seen: set[str] = set()
    duplicates: list[str] = []
    for group in groups:
        key = group.group_key.strip()
        if not key:
            continue
        if key in seen and key not in duplicates:
            duplicates.append(key)
        seen.add(key)
    return tuple(duplicates)


def format_duplicate_matrix_group_key_message(keys: Iterable[str]) -> str:
    return f"Duplicate Matrix group key: {', '.join(keys)}"
