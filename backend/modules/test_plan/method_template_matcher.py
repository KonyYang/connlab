"""Deterministic matcher and fill-empty fallback applier for template MCR."""

from __future__ import annotations

import re
from dataclasses import dataclass

from backend.modules.test_plan.method_template_library import (
    METHOD_TEMPLATE_LIBRARY,
    MethodTemplateEntry,
)


@dataclass(frozen=True, slots=True)
class TemplateFallbackResult:
    method: str | None
    condition: str | None
    requirement: str | None
    matched_family: str | None = None
    matched_provenance: str | None = None


def normalize_test_item(value: str | None) -> str:
    """Normalize test-item text for deterministic alias matching."""
    text = (value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def match_template(test_item: str | None) -> MethodTemplateEntry | None:
    """Return matched template entry or None."""
    normalized = normalize_test_item(test_item)
    if not normalized:
        return None
    for entry in METHOD_TEMPLATE_LIBRARY:
        for alias in entry.aliases:
            normalized_alias = normalize_test_item(alias)
            if normalized == normalized_alias:
                return entry
    return None


def apply_fill_empty_fallback(
    *,
    test_item: str | None,
    method: str | None,
    condition: str | None,
    requirement: str | None,
) -> TemplateFallbackResult:
    """Fill only empty fields from template fallback and never override non-empty values."""
    entry = match_template(test_item)
    if entry is None:
        return TemplateFallbackResult(method=method, condition=condition, requirement=requirement)
    return TemplateFallbackResult(
        method=method or entry.fallback_method,
        condition=condition or entry.fallback_condition,
        requirement=requirement or entry.fallback_requirement,
        matched_family=entry.family,
        matched_provenance=entry.provenance,
    )
