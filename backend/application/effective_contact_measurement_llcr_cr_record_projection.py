"""Formal TASK_360B projection sourced from effective confirmed plan authority."""

from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json

from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordProjection,
    build_llcr_cr_record_projection,
)
from backend.application.contact_measurement_plan_confirmed_consumer_adapter import (
    EffectiveContactMeasurementPlan,
)
from backend.domain import ConfirmedMatrixSnapshot


def build_effective_llcr_cr_record_projection(
    snapshot: ConfirmedMatrixSnapshot,
    effective: EffectiveContactMeasurementPlan,
) -> LlcrCrRecordProjection:
    """Use only effective confirmed targets, retaining legacy only for rollback states."""
    if effective.legacy_fallback_allowed:
        return build_llcr_cr_record_projection(snapshot)
    if effective.status in {"authority_corrupt", "empty"}:
        return _blocked_projection(snapshot, effective)
    projected = build_llcr_cr_record_projection(_snapshot_with_effective_contacts(snapshot, effective))
    if projected.status != "ready":
        return projected
    status = "complete" if effective.status == "complete" else "partial_compatible"
    diagnostics = projected.diagnostics + tuple(
        _omission_diagnostic(snapshot.version.confirmed_matrix_id, message)
        for message in effective.diagnostics
    )
    fingerprint = _fingerprint(projected, effective, diagnostics)
    return replace(
        projected,
        status=status,
        diagnostics=diagnostics,
        preview_fingerprint=fingerprint,
        measurement_plan_revision_id=effective.revision_id,
        measurement_plan_revision_sequence=effective.revision_sequence,
        effective_measurement_plan_status=effective.status,
        omission_diagnostics=effective.diagnostics,
    )


def _snapshot_with_effective_contacts(
    snapshot: ConfirmedMatrixSnapshot,
    effective: EffectiveContactMeasurementPlan,
) -> ConfirmedMatrixSnapshot:
    lookup = effective.lookup
    quantities = []
    for quantity in snapshot.step_quantities:
        key = (
            quantity.confirmed_group_id,
            quantity.confirmed_row_id,
            quantity.step_sequence,
            (quantity.step_suffix_note or "").strip(),
        )
        target = lookup.get(key)
        if target is not None:
            quantities.append(replace(quantity, contact_plan=target.contact_plan))
        elif quantity.contact_plan is not None:
            quantities.append(replace(quantity, contact_plan=None))
        else:
            quantities.append(quantity)
    return replace(snapshot, step_quantities=tuple(quantities))


def _blocked_projection(
    snapshot: ConfirmedMatrixSnapshot,
    effective: EffectiveContactMeasurementPlan,
) -> LlcrCrRecordProjection:
    return LlcrCrRecordProjection(
        project_id=snapshot.version.project_id,
        confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
        confirmed_revision=snapshot.version.confirmed_revision,
        status="blocked" if effective.status == "authority_corrupt" else "empty",
        sections=(),
        diagnostics=(),
        preview_fingerprint=None,
        measurement_plan_revision_id=effective.revision_id,
        measurement_plan_revision_sequence=effective.revision_sequence,
        effective_measurement_plan_status=effective.status,
        omission_diagnostics=effective.diagnostics,
    )


def _omission_diagnostic(matrix_id: str, message: str):
    from backend.application.confirmed_matrix_llcr_cr_record_projection import (
        LlcrCrRecordDiagnostic,
    )

    return LlcrCrRecordDiagnostic(
        code="measurement_plan_omission",
        severity="review_required",
        message=message,
    )


def _fingerprint(
    projection: LlcrCrRecordProjection,
    effective: EffectiveContactMeasurementPlan,
    diagnostics: tuple,
) -> str:
    payload = {
        "base": projection.preview_fingerprint,
        "plan_revision_id": effective.revision_id,
        "plan_revision_sequence": effective.revision_sequence,
        "status": effective.status,
        "diagnostics": [item.message for item in diagnostics],
    }
    return sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
