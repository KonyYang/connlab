"""Deterministic Matrix step token parsing and sequence continuity validation."""

from __future__ import annotations

import re
from dataclasses import dataclass


_TOKEN_SPLIT_RE = re.compile(r"[,\s]+")
_TOKEN_PARSE_RE = re.compile(r"^(?P<number>\d+)(?P<suffix>.*)$")


@dataclass(frozen=True, slots=True)
class ParsedStepToken:
    """One parsed Matrix step token."""

    raw_token: str
    sequence: int
    suffix_note: str | None


def parse_step_tokens(value: str | None) -> tuple[tuple[ParsedStepToken, ...], tuple[str, ...]]:
    """Parse step tokens separated by comma, whitespace, or newline."""
    if value is None:
        return (), ("Step token is missing.",)
    normalized = value.strip()
    if not normalized:
        return (), ("Step token is missing.",)
    parsed: list[ParsedStepToken] = []
    warnings: list[str] = []
    for token in (part.strip() for part in _TOKEN_SPLIT_RE.split(normalized) if part.strip()):
        match = _TOKEN_PARSE_RE.match(token)
        if match is None:
            warnings.append(f"Unrecognized step token: '{token}'.")
            continue
        suffix = match.group("suffix").strip() or None
        parsed.append(
            ParsedStepToken(
                raw_token=token,
                sequence=int(match.group("number")),
                suffix_note=suffix,
            )
        )
    if not parsed:
        warnings.append("No valid numeric step token was found.")
    return tuple(parsed), tuple(warnings)


def validate_group_step_sequences(group_label: str, sequences: list[int]) -> tuple[str, ...]:
    """Return continuity blockers for one group sequence list."""
    if not sequences:
        return (f"{group_label}: at least one step is required.",)
    blockers: list[str] = []
    sorted_sequences = sorted(sequences)
    if sorted_sequences[0] != 1:
        blockers.append(f"{group_label}: step sequence must start at 1.")
    seen: set[int] = set()
    duplicates: set[int] = set()
    for sequence in sequences:
        if sequence in seen:
            duplicates.add(sequence)
        seen.add(sequence)
    for duplicate in sorted(duplicates):
        blockers.append(f"{group_label}: duplicate step sequence {duplicate}.")
    for previous, current in zip(sorted_sequences, sorted_sequences[1:]):
        if current - previous > 1:
            blockers.append(
                f"{group_label}: missing step sequence between {previous} and {current}."
            )
    return tuple(blockers)
