"""Deterministic normalizer for row-level Condition/Requirement text."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class McrNormalizationResult:
    condition: str | None
    requirement: str | None
    notes: tuple[str, ...] = ()


def normalize_condition_requirement(
    *,
    test_item: str | None,
    condition: str | None,
    requirement: str | None,
    source_text: str,
) -> McrNormalizationResult:
    """Normalize MCR text for approved deterministic families only."""
    family = _family(test_item, source_text)
    notes: list[str] = []
    normalized_condition = _normalize_condition(condition)
    normalized_requirement = _normalize_requirement(requirement)

    if family == "llcr":
        llcr = _normalize_llcr_requirement(source_text, normalized_requirement)
        if llcr is not None:
            normalized_requirement = llcr
            notes.append("normalized-llcr-requirement")
    elif family == "temperature_rise":
        normalized = _normalize_temperature_requirement(source_text, normalized_requirement)
        if normalized is not None:
            normalized_requirement = normalized
            notes.append("normalized-temperature-requirement")
    elif family == "mating_force":
        normalized = _normalize_mating_unmating_requirement(source_text, normalized_requirement)
        if normalized is not None:
            normalized_requirement = normalized
            notes.append("normalized-mating-unmating-requirement")

    return McrNormalizationResult(
        condition=normalized_condition,
        requirement=normalized_requirement,
        notes=tuple(notes),
    )


def _normalize_condition(condition: str | None) -> str | None:
    if not condition:
        return None
    return _collapse_ws(_standardize_units(condition))


def _normalize_requirement(requirement: str | None) -> str | None:
    if not requirement:
        return None
    return _collapse_ws(_standardize_units(requirement))


def _normalize_llcr_requirement(source_text: str, current_requirement: str | None) -> str | None:
    text = _standardize_units(source_text)
    initial_match = re.search(
        r"(?:shall\s+not\s+exceed|must\s+not\s+exceed|<=|≤|max(?:imum)?\.?)\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:mΩ|mohm|milliohms?)\s*(?:initially|initial)?",
        text,
        re.IGNORECASE,
    )
    delta_match = re.search(
        r"(?:maximum\s+change(?:\s+is)?|change)\s*[:=]?\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:mΩ|mohm|milliohms?)",
        text,
        re.IGNORECASE,
    )
    if initial_match and delta_match:
        return (
            f"Initial <= {initial_match.group('value')} mΩ; "
            f"ΔR <= {delta_match.group('value')} mΩ"
        )
    return current_requirement


def _normalize_temperature_requirement(source_text: str, current_requirement: str | None) -> str | None:
    text = _standardize_units(" ".join(part for part in (current_requirement, source_text) if part))
    match = re.search(
        r"(?:shall\s+not\s+exceed|must\s+not\s+exceed|max(?:imum)?\.?|<=|≤)\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:℃|C)",
        text,
        re.IGNORECASE,
    )
    if not match:
        return current_requirement
    return f"<= {match.group('value')} ℃"


def _normalize_mating_unmating_requirement(source_text: str, current_requirement: str | None) -> str | None:
    text = _standardize_units(" ".join(part for part in (source_text, current_requirement) if part))
    mating = re.search(
        r"(?:mating|force\s+to\s+mate|mate)[^.;]*?"
        r"(?:shall\s+not\s+exceed|must\s+not\s+exceed|max(?:imum)?\.?|<=|≤)\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*N\b",
        text,
        re.IGNORECASE,
    )
    unmating = re.search(
        r"(?:un-?mating|unmating)[^.;]*?"
        r"(?:shall\s+not\s+less\s+than|not\s+less\s+than|min(?:imum)?\.?|>=|≥)\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*N\b",
        text,
        re.IGNORECASE,
    )
    if mating and unmating:
        return (
            f"Mating Force <= {mating.group('value')} N; "
            f"Un-mating Force >= {unmating.group('value')} N"
        )
    return current_requirement


def _family(test_item: str | None, source_text: str) -> str:
    text = _collapse_ws((test_item or "").lower())
    source = _collapse_ws(source_text.lower())
    combined = f"{text} {source}".strip()
    if "llcr" in combined or (
        "contact resistance" in combined and "low level" in combined
    ) or "low level contact resistance" in combined:
        return "llcr"
    if "temperature rise" in combined:
        return "temperature_rise"
    if "mating" in combined and "force" in combined:
        return "mating_force"
    return "other"


def _standardize_units(text: str) -> str:
    normalized = text
    normalized = re.sub(r"\bmilliohms?\b", "mΩ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bmohms?\b", "mΩ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bmohm\b", "mΩ", normalized, flags=re.IGNORECASE)
    normalized = normalized.replace("≤", "<=").replace("≥", ">=")
    normalized = re.sub(r"(?<=\d)\s*[cC]\b", " ℃", normalized)
    normalized = re.sub(r"(?<=\d)\s*(?=[NA]\b)", " ", normalized)
    return normalized


def _collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
