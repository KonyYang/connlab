"""Validation and derivation for Matrix Step contact plan authority."""

from __future__ import annotations

import re
from decimal import Decimal

from backend.domain import MatrixStepContactFamily, MatrixStepContactPlan


_CONTACT_KINDS = {"llcr", "cr_specified_current"}
_COVERAGE_STATUSES = {"eligible", "excluded", "manual_override"}
_DECIMAL = re.compile(r"^\d+(?:\.\d+)?$")
_PREFIX = re.compile(r"^[A-Z0-9_]{1,16}$")


def normalize_contact_plan(plan: MatrixStepContactPlan) -> MatrixStepContactPlan:
    """Validate target coverage and derive readings from included family records."""
    if plan.contact_kind not in _CONTACT_KINDS:
        raise ValueError("Contact plan kind is not supported.")
    if plan.coverage_status not in _COVERAGE_STATUSES:
        raise ValueError("Contact target coverage status is not supported.")
    if plan.included and plan.coverage_status == "excluded":
        raise ValueError("Excluded contact targets cannot be included.")
    if not plan.included and not _clean(plan.exclusion_reason):
        raise ValueError("Excluded contact targets require a short reason.")

    seen_ids: set[str] = set()
    families: list[MatrixStepContactFamily] = []
    total = Decimal("0")
    for family in plan.families:
        family_id = _clean(family.family_id)
        label = _clean(family.family_label)
        prefix = _clean(family.record_prefix).upper()
        if not family_id or family_id in seen_ids:
            raise ValueError("Contact family identifiers must be unique.")
        if not label:
            raise ValueError("Contact family label is required.")
        if not _PREFIX.fullmatch(prefix):
            raise ValueError("Contact family prefix must use up to 16 letters, numbers, or underscores.")
        count = _normalize_count(family.count_per_sample)
        if family.included and not count:
            raise ValueError("Included contact families require a non-negative count.")
        if family.included:
            total += Decimal(count)
        seen_ids.add(family_id)
        families.append(
            MatrixStepContactFamily(
                family_id=family_id,
                family_label=label,
                count_per_sample=count or "0",
                record_label=_record_label(label),
                record_prefix=prefix,
                included=family.included,
                is_custom=family.is_custom,
            )
        )

    if plan.included and not families:
        raise ValueError("Included contact targets require at least one contact family.")
    readings = _format_decimal(total) if plan.included else None
    return MatrixStepContactPlan(
        contact_kind=plan.contact_kind,
        coverage_status=plan.coverage_status,
        included=plan.included,
        exclusion_reason=_clean(plan.exclusion_reason) if not plan.included else None,
        is_override=plan.is_override,
        readings_per_sample=readings,
        families=tuple(families),
    )


def _normalize_count(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    if not _DECIMAL.fullmatch(text):
        raise ValueError("Contact family count must be a non-negative number.")
    return _format_decimal(Decimal(text))


def _format_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    return format(normalized, "f") if normalized != normalized.to_integral() else str(int(normalized))


def _clean(value: str | None) -> str:
    return value.strip() if value else ""


def _record_label(label: str) -> str:
    return label if label.lower().endswith("contact") else f"{label} contact"
