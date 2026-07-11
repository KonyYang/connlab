from backend.application.matrix_step_quantity_authority_comparison import (
    step_quantity_authority_matches,
)
from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
    MatrixStepContactFamily,
    MatrixStepContactPlan,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    ProjectMatrixDraftStepQuantity,
)


def test_step_quantity_authority_ignores_storage_ids_and_timestamps() -> None:
    draft = _draft()
    confirmed = _confirmed(
        family_count="4",
        confirmed_quantity_id="confirmed-quantity-other",
        confirmed_at="2026-07-11T12:00:00+00:00",
    )

    assert step_quantity_authority_matches(draft, confirmed) is True


def test_step_quantity_authority_detects_contact_plan_family_change() -> None:
    draft = _draft()
    confirmed = _confirmed(family_count="5")

    assert step_quantity_authority_matches(draft, confirmed) is False


def _draft() -> ProjectMatrixDraftSnapshot:
    plan = _plan("4")
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="draft-1",
            project_id="P1",
            source_import_id="source-1",
            source_snapshot_id="snapshot-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-07-11T08:00:00+00:00",
            updated_at="2026-07-11T08:01:00+00:00",
            base_confirmed_matrix_id="confirmed-1",
        ),
        groups=(
            ProjectMatrixDraftGroup(
                draft_group_id="draft-group-1",
                project_matrix_draft_id="draft-1",
                source_group_snapshot_id="source-group-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
            ),
        ),
        rows=(
            ProjectMatrixDraftRow(
                draft_row_id="draft-row-1",
                project_matrix_draft_id="draft-1",
                source_row_snapshot_id="source-row-1",
                row_order=1,
                test_item="LLCR",
            ),
        ),
        cells=(
            ProjectMatrixDraftCell(
                draft_cell_id="draft-cell-1",
                project_matrix_draft_id="draft-1",
                draft_row_id="draft-row-1",
                draft_group_id="draft-group-1",
                cell_value="1",
            ),
        ),
        step_quantities=(
            ProjectMatrixDraftStepQuantity(
                draft_step_quantity_id="draft-quantity-1",
                project_matrix_draft_id="draft-1",
                draft_group_id="draft-group-1",
                draft_row_id="draft-row-1",
                step_sequence=1,
                step_suffix_note=None,
                raw_token="1",
                test_points_per_sample="4",
                readings_per_point="1",
                contact_points_per_sample="4",
                source="matrix_contact_plan",
                review_required=False,
                review_reason=None,
                updated_at="2026-07-11T08:01:00+00:00",
                contact_plan=plan,
            ),
        ),
    )


def _confirmed(
    *,
    family_count: str,
    confirmed_quantity_id: str = "confirmed-quantity-1",
    confirmed_at: str = "2026-07-11T09:00:00+00:00",
) -> ConfirmedMatrixSnapshot:
    plan = _plan(family_count)
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="confirmed-1",
            project_id="P1",
            project_matrix_draft_id="draft-previous",
            source_import_id="source-1",
            source_snapshot_id="snapshot-1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at=confirmed_at,
        ),
        groups=(
            ConfirmedMatrixGroup(
                confirmed_group_id="confirmed-group-1",
                confirmed_matrix_id="confirmed-1",
                draft_group_id="draft-group-old",
                source_group_snapshot_id="source-group-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                sample_quantity_expression="5",
            ),
        ),
        rows=(
            ConfirmedMatrixRow(
                confirmed_row_id="confirmed-row-1",
                confirmed_matrix_id="confirmed-1",
                draft_row_id="draft-row-old",
                source_row_snapshot_id="source-row-1",
                row_order=1,
                test_item="LLCR",
            ),
        ),
        step_quantities=(
            ConfirmedMatrixStepQuantity(
                confirmed_step_quantity_id=confirmed_quantity_id,
                confirmed_matrix_id="confirmed-1",
                confirmed_group_id="confirmed-group-1",
                confirmed_row_id="confirmed-row-1",
                draft_group_id="draft-group-old",
                draft_row_id="draft-row-old",
                step_sequence=1,
                step_suffix_note=" ",
                raw_token="1",
                test_points_per_sample="4",
                readings_per_point="1",
                contact_points_per_sample="4",
                source="matrix_contact_plan",
                review_required=False,
                review_reason=None,
                confirmed_at=confirmed_at,
                contact_plan=plan,
            ),
        ),
    )


def _plan(count: str) -> MatrixStepContactPlan:
    return MatrixStepContactPlan(
        contact_kind="llcr",
        coverage_status="eligible",
        included=True,
        exclusion_reason=None,
        is_override=False,
        readings_per_sample=count,
        families=(
            MatrixStepContactFamily(
                family_id="high_power_pin",
                family_label="High Power Pin",
                count_per_sample=count,
                record_label="High Power Pin contact",
                record_prefix="HP",
                included=True,
                is_custom=False,
            ),
        ),
    )
