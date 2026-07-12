from backend.application.contact_measurement_plan_impact_classifier import (
    classify_revision_targets,
    classify_target_change,
)
from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
    MatrixStepContactPlan,
)


def test_classifier_keeps_text_and_valid_sample_changes_compatible() -> None:
    assert classify_target_change({"method": "A", "sample": "5"}, {"method": "B", "sample": "5"}) == "text_refresh_compatible"
    assert classify_target_change({"method": "A", "sample": "5"}, {"method": "A", "sample": "6"}) == "sample_quantity_compatible"


def test_classifier_requires_review_for_identity_or_invalid_sample_change() -> None:
    assert classify_target_change({"step": "1", "sample": "5"}, {"step": "2", "sample": "5"}) == "structural_review_required"
    assert classify_target_change({"sample": "5"}, {"sample": "many"}) == "projection_review_required"


def test_revision_classifier_keeps_matching_target_compatible_and_marks_new_target() -> None:
    stored_target = type(
        "StoredTarget",
        (),
        {
            "stable_target_key": "cmp-target:v1|group:sg-1|row:sr-1|step:1|suffix:",
            "source_group_snapshot_id": "sg-1",
            "manual_group_anchor_id": None,
            "source_row_snapshot_id": "sr-1",
            "manual_row_anchor_id": None,
            "step_sequence": 1,
            "step_suffix_note": "",
            "contact_kind": "llcr",
            "eligible": True,
            "included": True,
            "group_label": "Old group",
            "test_item": "LLCR",
            "sample_quantity_expression": "2",
        },
    )()

    result = classify_revision_targets((stored_target,), _snapshot_with_new_target())

    assert result.status == "needs_review"
    assert result.categories_by_target[
        "cmp-target:v1|group:sg-1|row:sr-1|step:1|suffix:"
    ] == "sample_quantity_compatible"
    assert result.new_target_keys == (
        "cmp-target:v1|group:sg-2|row:sr-1|step:1|suffix:",
    )
    assert result.candidate_subjects_by_target[
        "cmp-target:v1|group:sg-2|row:sr-1|step:1|suffix:"
    ] == "cmp-candidate:v1|matrix:cmv-2|group:cg-2|row:cr-1|step:1|suffix:"


def _snapshot_with_new_target() -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="cmv-2",
            project_id="P1",
            project_matrix_draft_id="pmd-2",
            source_import_id="smi-2",
            source_snapshot_id="sms-2",
            confirmed_revision=2,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-07-12T10:00:00Z",
        ),
        groups=(
            ConfirmedMatrixGroup(
                confirmed_group_id="cg-1",
                confirmed_matrix_id="cmv-2",
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="Current group",
                sample_quantity_expression="3",
            ),
            ConfirmedMatrixGroup(
                confirmed_group_id="cg-2",
                confirmed_matrix_id="cmv-2",
                draft_group_id="dg-2",
                source_group_snapshot_id="sg-2",
                group_order=2,
                group_key="g2",
                group_label="New group",
                sample_quantity_expression="2",
            ),
        ),
        rows=(
            ConfirmedMatrixRow(
                confirmed_row_id="cr-1",
                confirmed_matrix_id="cmv-2",
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="LLCR",
            ),
        ),
        step_quantities=(
            *(
                ConfirmedMatrixStepQuantity(
                    confirmed_step_quantity_id=f"q-{group_id}",
                    confirmed_matrix_id="cmv-2",
                    confirmed_group_id=group_id,
                    confirmed_row_id="cr-1",
                    draft_group_id=f"d{group_id}",
                    draft_row_id="dr-1",
                    step_sequence=1,
                    step_suffix_note=None,
                    raw_token="1",
                    test_points_per_sample=None,
                    readings_per_point=None,
                    contact_points_per_sample=None,
                    source="matrix_contact_plan",
                    review_required=False,
                    review_reason=None,
                    confirmed_at="2026-07-12T10:00:00Z",
                    contact_plan=MatrixStepContactPlan(
                        contact_kind="llcr",
                        coverage_status="included",
                        included=True,
                        exclusion_reason=None,
                        is_override=False,
                        readings_per_sample="2",
                        families=(),
                    ),
                )
                for group_id in ("cg-1", "cg-2")
            ),
        ),
    )
