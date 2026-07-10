"""Structured Matrix contact measurement authority records."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class MatrixStepContactFamily:
    """One named contact family used by a Matrix Step contact plan."""

    family_id: str
    family_label: str
    count_per_sample: str
    record_label: str
    record_prefix: str
    included: bool
    is_custom: bool


@dataclass(frozen=True, slots=True)
class MatrixStepContactPlan:
    """Structured coverage and family authority for one eligible Group-Step."""

    contact_kind: str
    coverage_status: str
    included: bool
    exclusion_reason: str | None
    is_override: bool
    readings_per_sample: str | None
    families: tuple[MatrixStepContactFamily, ...]


def contact_plan_to_json(plan: MatrixStepContactPlan | None) -> str | None:
    """Serialize typed contact authority for local SQLite storage."""
    if plan is None:
        return None
    return json.dumps(asdict(plan), separators=(",", ":"), sort_keys=True)


def contact_plan_from_json(value: str | None) -> MatrixStepContactPlan | None:
    """Deserialize a persisted contact authority record without using review text."""
    if value is None or not value.strip():
        return None
    payload = json.loads(value)
    families = tuple(
        MatrixStepContactFamily(
            family_id=entry["family_id"],
            family_label=entry["family_label"],
            count_per_sample=entry["count_per_sample"],
            record_label=entry["record_label"],
            record_prefix=entry["record_prefix"],
            included=bool(entry["included"]),
            is_custom=bool(entry["is_custom"]),
        )
        for entry in payload["families"]
    )
    return MatrixStepContactPlan(
        contact_kind=payload["contact_kind"],
        coverage_status=payload["coverage_status"],
        included=bool(payload["included"]),
        exclusion_reason=payload.get("exclusion_reason"),
        is_override=bool(payload["is_override"]),
        readings_per_sample=payload.get("readings_per_sample"),
        families=families,
    )
