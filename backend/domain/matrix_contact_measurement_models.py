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


@dataclass(frozen=True, slots=True)
class MatrixPointCategory:
    prefix: str
    point_expression: str
    cr_selected: bool = True


@dataclass(frozen=True, slots=True)
class MatrixPointProfile:
    categories: tuple[MatrixPointCategory, ...]
    delta_r_enabled: bool = True
    ir_points_per_sample: str | None = None
    dwv_points_per_sample: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixStepPointCategory:
    prefix: str
    point_expression: str


@dataclass(frozen=True, slots=True)
class MatrixStepPointOverride:
    draft_group_id: str
    draft_row_id: str
    step_sequence: int
    step_suffix_note: str
    categories: tuple[MatrixStepPointCategory, ...]


def point_profile_to_json(profile: MatrixPointProfile | None) -> str | None:
    if profile is None:
        return None
    payload = asdict(profile)
    # Adding optional electrical settings must not alter legacy LLCR/CR fingerprints.
    for key in ("ir_points_per_sample", "dwv_points_per_sample"):
        if payload[key] is None:
            del payload[key]
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def point_profile_from_json(value: str | None) -> MatrixPointProfile | None:
    if not value:
        return None
    payload = json.loads(value)
    return MatrixPointProfile(
        categories=tuple(MatrixPointCategory(**category) for category in payload["categories"]),
        delta_r_enabled=bool(payload["delta_r_enabled"]),
        ir_points_per_sample=payload.get("ir_points_per_sample"),
        dwv_points_per_sample=payload.get("dwv_points_per_sample"),
    )


def point_overrides_to_json(overrides: tuple[MatrixStepPointOverride, ...]) -> str:
    return json.dumps([asdict(item) for item in overrides], separators=(",", ":"), sort_keys=True)


def point_overrides_from_json(value: str | None) -> tuple[MatrixStepPointOverride, ...]:
    if not value:
        return ()
    return tuple(
        MatrixStepPointOverride(
            draft_group_id=item["draft_group_id"],
            draft_row_id=item["draft_row_id"],
            step_sequence=int(item["step_sequence"]),
            step_suffix_note=item["step_suffix_note"],
            categories=tuple(MatrixStepPointCategory(**category) for category in item["categories"]),
        )
        for item in json.loads(value)
    )


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
