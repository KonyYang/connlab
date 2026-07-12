"""TASK_361E formal workbook projection coverage."""

from backend.application.contact_measurement_plan_confirmed_consumer_adapter import (
    EffectiveContactMeasurementPlan,
    EffectiveContactMeasurementTarget,
)
from backend.application.effective_contact_measurement_llcr_cr_record_projection import (
    build_effective_llcr_cr_record_projection,
)
from backend.domain import MatrixStepContactPlan
from tests.unit.test_confirmed_matrix_llcr_cr_record_projection import _snapshot


def test_partial_effective_projection_uses_confirmed_target_and_marks_output() -> None:
    snapshot = _snapshot()
    plan = snapshot.step_quantities[0].contact_plan
    assert plan is not None
    effective = EffectiveContactMeasurementPlan(
        status="partial_compatible", snapshot=snapshot, revision_id="revision-1",
        revision_sequence=2, diagnostics=("One target requires review.",),
        targets=(EffectiveContactMeasurementTarget("group-1", "row-1", 2, "", plan),),
    )

    result = build_effective_llcr_cr_record_projection(snapshot, effective)

    assert result.status == "partial_compatible"
    assert result.measurement_plan_revision_sequence == 2
    assert result.preview_fingerprint is not None
    assert result.row_count == 6


def test_corrupt_effective_authority_blocks_formal_output_without_legacy_fallback() -> None:
    snapshot = _snapshot()
    result = build_effective_llcr_cr_record_projection(
        snapshot,
        EffectiveContactMeasurementPlan(
            status="authority_corrupt", snapshot=snapshot, revision_id=None,
            revision_sequence=None, targets=(), diagnostics=("Maintenance required.",),
        ),
    )

    assert result.status == "blocked"
    assert result.sections == ()
    assert result.preview_fingerprint is None
