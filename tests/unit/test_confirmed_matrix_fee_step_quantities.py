from backend.application.confirmed_matrix_fee_step_quantities import (
    _matched_context,
    build_step_quantity_contexts,
    build_step_quantity_lookup,
)
from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixStepQuantity,
    MatrixStepContactFamily,
    MatrixStepContactPlan,
)
from backend.modules.test_plan.matrix_step_sequence_validation import ParsedStepToken


def test_fee_context_prefers_confirmed_contact_plan_readings_per_sample() -> None:
    quantity = ConfirmedMatrixStepQuantity(
        confirmed_step_quantity_id="cmsq-1",
        confirmed_matrix_id="cmv-1",
        confirmed_group_id="cmg-1",
        confirmed_row_id="cmr-1",
        draft_group_id="dmg-1",
        draft_row_id="dmr-1",
        step_sequence=1,
        step_suffix_note=None,
        raw_token="1",
        test_points_per_sample="1",
        readings_per_point="1",
        contact_points_per_sample="1",
        source="matrix_contact_plan",
        review_required=False,
        review_reason=None,
        confirmed_at="2026-07-10T09:00:00+00:00",
        contact_plan=MatrixStepContactPlan(
            contact_kind="llcr",
            coverage_status="eligible",
            included=True,
            exclusion_reason=None,
            is_override=False,
            readings_per_sample="5",
            families=(
                MatrixStepContactFamily(
                    family_id="signal_pin",
                    family_label="Signal Pin",
                    count_per_sample="5",
                    record_label="Signal Pin contact",
                    record_prefix="SIG",
                    included=True,
                    is_custom=False,
                ),
            ),
        ),
    )

    context = _matched_context(
        token=ParsedStepToken(sequence=1, raw_token="1", suffix_note=None),
        quantity=quantity,
    )

    assert context.total_readings == "5"
    assert context.test_points_per_sample == "5"
    assert context.readings_per_point == "1"


def test_effective_contact_authority_blocks_legacy_fallback_for_omitted_target() -> None:
    quantity = _quantity()
    contexts = build_step_quantity_contexts(
        group=ConfirmedMatrixGroup(
            confirmed_group_id="cmg-1", confirmed_matrix_id="cmv-1", draft_group_id="dmg-1",
            source_group_snapshot_id=None, group_order=1, group_key="g1", group_label="G1",
            sample_quantity_expression="2",
        ),
        row=ConfirmedMatrixRow(
            confirmed_row_id="cmr-1", confirmed_matrix_id="cmv-1", draft_row_id="dmr-1",
            source_row_snapshot_id=None, row_order=1, test_item="LLCR",
        ),
        parsed_tokens=(ParsedStepToken(sequence=1, raw_token="1", suffix_note=None),),
        step_quantity_lookup={("cmg-1", "cmr-1", 1, ""): quantity},
        effective_contact_targets={},
        effective_contact_status="partial_compatible",
        is_llcr_or_specified_current=True,
    )

    assert contexts[0].review_required is True
    assert contexts[0].total_readings is None
    assert contexts[0].source == "confirmed_measurement_plan"


def _quantity() -> ConfirmedMatrixStepQuantity:
    return ConfirmedMatrixStepQuantity(
        confirmed_step_quantity_id="cmsq-1", confirmed_matrix_id="cmv-1",
        confirmed_group_id="cmg-1", confirmed_row_id="cmr-1", draft_group_id="dmg-1",
        draft_row_id="dmr-1", step_sequence=1, step_suffix_note=None, raw_token="1",
        test_points_per_sample="1", readings_per_point="1", contact_points_per_sample="1",
        source="matrix_contact_plan", review_required=False, review_reason=None,
        confirmed_at="2026-07-10T09:00:00+00:00", contact_plan=None,
    )
