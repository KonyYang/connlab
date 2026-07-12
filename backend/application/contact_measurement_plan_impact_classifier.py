"""Pure compatibility classification for one contact-plan target binding."""

from __future__ import annotations

from dataclasses import dataclass

from backend.application.contact_measurement_plan_identity import (
    build_candidate_subject_key,
    build_target_key,
)
from backend.domain import ConfirmedMatrixSnapshot


_STRUCTURAL = {"group", "row", "step", "suffix", "contact_kind", "eligible", "included"}


@dataclass(frozen=True, slots=True)
class ContactMeasurementPlanImpactResult:
    """Pure target comparison result used by lifecycle and projection services."""

    status: str
    categories_by_target: dict[str, str]
    new_target_keys: tuple[str, ...]
    candidate_subjects_by_target: dict[str, str]
    deleted_target_keys: tuple[str, ...]


def classify_revision_targets(
    stored_targets: tuple[object, ...],
    current_matrix: ConfirmedMatrixSnapshot,
) -> ContactMeasurementPlanImpactResult:
    """Compare persisted plan targets to the current confirmed Matrix only."""
    candidates = _current_candidates(current_matrix)
    categories: dict[str, str] = {}
    stored_keys = {str(target.stable_target_key) for target in stored_targets}
    for target in stored_targets:
        key = str(target.stable_target_key)
        candidate = candidates.get(key)
        if candidate is None:
            categories[key] = "structural_review_required"
            continue
        categories[key] = classify_target_change(
            _stored_values(target),
            {name: value for name, value in candidate.items() if name != "candidate_subject_key"},
        )
    new_keys = tuple(sorted(set(candidates) - stored_keys))
    deleted_keys = tuple(
        sorted(
            key
            for key, category in categories.items()
            if category == "structural_review_required"
        )
    )
    needs_review = bool(new_keys) or any(
        category in {"structural_review_required", "projection_review_required"}
        for category in categories.values()
    )
    has_compatible_change = any(
        category in {"text_refresh_compatible", "sample_quantity_compatible"}
        for category in categories.values()
    )
    status = "needs_review" if needs_review else (
        "compatible_refresh" if has_compatible_change else "unchanged"
    )
    return ContactMeasurementPlanImpactResult(
        status=status,
        categories_by_target=categories,
        new_target_keys=new_keys,
        candidate_subjects_by_target={
            key: str(candidates[key]["candidate_subject_key"])
            for key in new_keys
        },
        deleted_target_keys=deleted_keys,
    )


def classify_target_change(before: dict[str, str], after: dict[str, str]) -> str:
    """Classify a normalized target delta without persistence side effects."""
    if before == after:
        return "unchanged"
    if any(before.get(key) != after.get(key) for key in _STRUCTURAL):
        return "structural_review_required"
    if before.get("sample") != after.get("sample"):
        return "sample_quantity_compatible" if _positive(after.get("sample")) else "projection_review_required"
    return "text_refresh_compatible"


def _positive(value: str | None) -> bool:
    return bool(value and value.isdecimal() and int(value) > 0)


def _current_candidates(snapshot: ConfirmedMatrixSnapshot) -> dict[str, dict[str, str]]:
    groups = {group.confirmed_group_id: group for group in snapshot.groups}
    rows = {row.confirmed_row_id: row for row in snapshot.rows}
    candidates: dict[str, dict[str, str]] = {}
    for quantity in snapshot.step_quantities:
        plan = quantity.contact_plan
        group = groups.get(quantity.confirmed_group_id)
        row = rows.get(quantity.confirmed_row_id)
        if plan is None or group is None or row is None:
            continue
        if plan.contact_kind not in {"llcr", "cr_specified_current"}:
            continue
        if not group.source_group_snapshot_id or not row.source_row_snapshot_id:
            continue
        key = build_target_key(
            group.source_group_snapshot_id,
            None,
            row.source_row_snapshot_id,
            None,
            quantity.step_sequence,
            quantity.step_suffix_note,
        )
        candidates[key] = {
            "group": group.source_group_snapshot_id,
            "row": row.source_row_snapshot_id,
            "step": str(quantity.step_sequence),
            "suffix": (quantity.step_suffix_note or "").strip().lower(),
            "contact_kind": plan.contact_kind,
            "eligible": "true",
            "included": "true" if plan.included else "false",
            "sample": group.sample_quantity_expression.strip(),
            "group_label": group.group_label,
            "test_item": row.test_item,
            "candidate_subject_key": build_candidate_subject_key(
                snapshot.version.confirmed_matrix_id,
                group.confirmed_group_id,
                row.confirmed_row_id,
                quantity.step_sequence,
                quantity.step_suffix_note,
            ),
        }
    return candidates


def _stored_values(target: object) -> dict[str, str]:
    return {
        "group": _lineage_value(
            getattr(target, "source_group_snapshot_id"),
            getattr(target, "manual_group_anchor_id"),
        ),
        "row": _lineage_value(
            getattr(target, "source_row_snapshot_id"),
            getattr(target, "manual_row_anchor_id"),
        ),
        "step": str(getattr(target, "step_sequence")),
        "suffix": str(getattr(target, "step_suffix_note") or "").strip().lower(),
        "contact_kind": str(getattr(target, "contact_kind")),
        "eligible": "true" if bool(getattr(target, "eligible")) else "false",
        "included": "true" if bool(getattr(target, "included")) else "false",
        "sample": str(getattr(target, "sample_quantity_expression") or "").strip(),
        "group_label": str(getattr(target, "group_label") or ""),
        "test_item": str(getattr(target, "test_item") or ""),
    }


def _lineage_value(source: object, manual: object) -> str:
    return str(source or manual or "").strip()
