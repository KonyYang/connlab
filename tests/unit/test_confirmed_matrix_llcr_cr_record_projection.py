from __future__ import annotations

from dataclasses import replace

from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    build_llcr_cr_record_projection,
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
)


def test_projection_expands_confirmed_included_family_counts_in_snapshot_order() -> None:
    projection = build_llcr_cr_record_projection(_snapshot())

    assert projection.status == "ready"
    assert projection.confirmed_revision == 4
    assert len(projection.sections) == 1
    section = projection.sections[0]
    assert section.record_type == "llcr"
    assert section.sample_count == 2
    assert section.readings_per_sample == 3
    assert [row.contact_id for row in section.rows] == [
        "SIG1",
        "SIG2",
        "HP1",
        "SIG1",
        "SIG2",
        "HP1",
    ]


def test_projection_omits_zero_count_and_blocks_fractional_count_without_rounding() -> None:
    snapshot = _snapshot(
        families=(
            _family("signal", "Signal", "0", "SIG"),
            _family("high", "High power", "1.5", "HP"),
        ),
        readings_per_sample="1.5",
    )

    projection = build_llcr_cr_record_projection(snapshot)

    assert projection.status == "review_required"
    assert projection.sections == ()
    assert [diagnostic.code for diagnostic in projection.diagnostics] == [
        "family_count_not_positive_integer"
    ]


def test_projection_blocks_prefix_collision_only_within_one_group_step_type() -> None:
    snapshot = _snapshot(
        families=(
            _family("signal", "Signal", "1", "SIG"),
            _family("custom", "Custom", "1", "s-i-g"),
        ),
        readings_per_sample="2",
    )

    projection = build_llcr_cr_record_projection(snapshot)

    assert projection.status == "blocked"
    assert projection.sections == ()
    assert projection.diagnostics[0].code == "normalized_prefix_collision"
    assert projection.diagnostics[0].normalized_prefix == "SIG"
    assert projection.diagnostics[0].first_family_id == "signal"
    assert projection.diagnostics[0].first_family_label == "Signal"
    assert projection.diagnostics[0].second_family_id == "custom"
    assert projection.diagnostics[0].second_family_label == "Custom"


def test_projection_permits_same_prefix_in_a_different_confirmed_group_step_section() -> None:
    source = _snapshot()
    second_group = replace(
        source.groups[0],
        confirmed_group_id="group-2",
        draft_group_id="draft-group-2",
        group_order=2,
        group_label="Group 2",
    )
    second_quantity = replace(
        source.step_quantities[0],
        confirmed_step_quantity_id="quantity-2",
        confirmed_group_id=second_group.confirmed_group_id,
        draft_group_id=second_group.draft_group_id,
    )
    projection = build_llcr_cr_record_projection(
        replace(source, groups=(source.groups[0], second_group), step_quantities=(source.step_quantities[0], second_quantity))
    )

    assert projection.status == "ready"
    assert len(projection.sections) == 2
    assert projection.diagnostics == ()
    assert [section.group_label for section in projection.sections] == ["Group 1", "Group 2"]


def _snapshot(
    *,
    families: tuple[MatrixStepContactFamily, ...] | None = None,
    readings_per_sample: str = "3",
) -> ConfirmedMatrixSnapshot:
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id="cmv-1",
        project_id="project-1",
        project_matrix_draft_id="draft-1",
        source_import_id="import-1",
        source_snapshot_id="source-1",
        confirmed_revision=4,
        is_active_authority=True,
        status=ConfirmedMatrixStatus.CONFIRMED,
        confirmed_by="operator",
        confirmed_at="2026-07-10T10:00:00+00:00",
    )
    group = ConfirmedMatrixGroup(
        confirmed_group_id="group-1",
        confirmed_matrix_id=version.confirmed_matrix_id,
        draft_group_id="draft-group-1",
        source_group_snapshot_id=None,
        group_order=1,
        group_key="G1",
        group_label="Group 1",
        sample_quantity_expression="2",
    )
    row = ConfirmedMatrixRow(
        confirmed_row_id="row-1",
        confirmed_matrix_id=version.confirmed_matrix_id,
        draft_row_id="draft-row-1",
        source_row_snapshot_id=None,
        row_order=1,
        test_item="LLCR",
    )
    plan = MatrixStepContactPlan(
        contact_kind="llcr",
        coverage_status="eligible",
        included=True,
        exclusion_reason=None,
        is_override=False,
        readings_per_sample=readings_per_sample,
        families=families
        or (
            _family("signal", "Signal", "2", "SIG"),
            _family("high", "High power", "1", "HP"),
        ),
    )
    quantity = ConfirmedMatrixStepQuantity(
        confirmed_step_quantity_id="quantity-1",
        confirmed_matrix_id=version.confirmed_matrix_id,
        confirmed_group_id=group.confirmed_group_id,
        confirmed_row_id=row.confirmed_row_id,
        draft_group_id=group.draft_group_id,
        draft_row_id=row.draft_row_id,
        step_sequence=2,
        step_suffix_note=None,
        raw_token="2",
        test_points_per_sample=None,
        readings_per_point=None,
        contact_points_per_sample=None,
        source="matrix_contact_plan",
        review_required=False,
        review_reason=None,
        confirmed_at=version.confirmed_at,
        contact_plan=plan,
    )
    return ConfirmedMatrixSnapshot(version=version, groups=(group,), rows=(row,), step_quantities=(quantity,))


def _family(
    family_id: str,
    label: str,
    count: str,
    prefix: str,
) -> MatrixStepContactFamily:
    return MatrixStepContactFamily(
        family_id=family_id,
        family_label=label,
        count_per_sample=count,
        record_label=f"{label} contact",
        record_prefix=prefix,
        included=True,
        is_custom=family_id == "custom",
    )
