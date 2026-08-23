from __future__ import annotations

from dataclasses import replace

from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    build_point_profile_llcr_cr_record_projection,
    build_llcr_cr_record_projection,
)
from backend.application.contact_point_profile_confirmed_consumer_adapter import (
    EffectiveConfirmedPointProfile,
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


def test_point_profile_projection_builds_separate_type_views_from_matrix_stages() -> None:
    snapshot = _matrix_with_llcr_and_cr_stages()
    profile = EffectiveConfirmedPointProfile(
        status="confirmed",
        readings_per_sample="4",
        revision_id="profile-1",
        revision_sequence=3,
        fingerprint="profile-fingerprint",
        lineage="Confirmed Project Point Profile",
        message=None,
        cr_readings_per_sample="2",
        categories=(
            {
                "category_id": "ppc-1", "category_ordinal": 0, "label": "Signal",
                "count_per_sample": 2, "record_prefix": "SIG", "included": True,
                "point_expression": "1,3",
            },
            {
                "category_id": "ppc-2", "category_ordinal": 1, "label": "Power",
                "count_per_sample": 2, "record_prefix": "PWR", "included": True,
                "point_expression": "2,4",
            },
        ),
        cr_category_ids=("ppc-2",),
        delta_r_enabled=False,
    )

    llcr = build_point_profile_llcr_cr_record_projection(snapshot, profile, "llcr")
    cr = build_point_profile_llcr_cr_record_projection(snapshot, profile, "cr")

    assert llcr.status == "ready"
    assert llcr.record_type == "llcr"
    assert llcr.delta_r_enabled is False
    assert [section.category_id for section in llcr.sections] == ["ppc-1", "ppc-2"]
    assert [stage.label for stage in llcr.sections[0].stages] == ["Initial", "Final"]
    assert [row.contact_id for row in llcr.sections[0].rows] == ["SIG1", "SIG3", "SIG1", "SIG3"]

    assert cr.status == "ready"
    assert cr.record_type == "cr"
    assert [section.category_id for section in cr.sections] == ["ppc-2"]
    assert cr.sections[0].stages[0].test_current_ampere == "10"
    assert [row.contact_id for row in cr.sections[0].rows] == ["PWR2", "PWR4", "PWR2", "PWR4"]


def test_point_profile_projection_blocks_when_confirmed_profile_is_unusable() -> None:
    profile = EffectiveConfirmedPointProfile(
        status="draft", readings_per_sample=None, revision_id=None,
        revision_sequence=None, fingerprint=None, lineage=None,
        message="Confirm Point Profile before generating test records.",
    )

    projection = build_point_profile_llcr_cr_record_projection(_snapshot(), profile, "llcr")

    assert projection.status == "blocked"
    assert projection.preview_fingerprint is None
    assert projection.diagnostics[0].code == "point_profile_not_confirmed"


def test_point_profile_stage_label_skips_other_resistance_measurements() -> None:
    source = _matrix_with_llcr_and_cr_stages()
    final = source.rows[2]
    cr = source.rows[3]
    shifted_cr = replace(cr, row_order=3)
    middle = replace(
        final,
        confirmed_row_id="row-middle",
        draft_row_id="draft-row-middle",
        row_order=4,
    )
    shifted_final = replace(final, row_order=5)
    quantities = tuple(
        replace(
            quantity,
            step_sequence=(
                5 if quantity.confirmed_row_id == final.confirmed_row_id
                else 3 if quantity.confirmed_row_id == cr.confirmed_row_id
                else quantity.step_sequence
            ),
        )
        for quantity in source.step_quantities
    ) + (
        replace(
            source.step_quantities[0],
            confirmed_step_quantity_id="quantity-middle",
            confirmed_row_id=middle.confirmed_row_id,
            draft_row_id=middle.draft_row_id,
            step_sequence=4,
            raw_token="4",
            contact_plan=None,
        ),
    )
    snapshot = replace(
        source,
        rows=(source.rows[0], source.rows[1], shifted_cr, middle, shifted_final),
        step_quantities=quantities,
    )
    profile = EffectiveConfirmedPointProfile(
        status="confirmed",
        readings_per_sample="1",
        revision_id="profile-1",
        revision_sequence=1,
        fingerprint="profile-fingerprint",
        lineage="Confirmed Project Point Profile",
        message=None,
        categories=({
            "category_id": "ppc-1", "category_ordinal": 0, "label": "Signal",
            "count_per_sample": 1, "record_prefix": "SIG", "included": True,
            "point_expression": "1",
        },),
    )

    projection = build_point_profile_llcr_cr_record_projection(snapshot, profile, "llcr")

    assert [stage.label for stage in projection.sections[0].stages] == [
        "Initial", "After DURABILITY, 20 Cycles", "Final",
    ]


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


def _matrix_with_llcr_and_cr_stages() -> ConfirmedMatrixSnapshot:
    source = _snapshot()
    group = source.groups[0]
    llcr_initial = replace(source.rows[0], row_order=1, test_item="LLCR", condition="100 mA max")
    durability = replace(
        source.rows[0], confirmed_row_id="row-2", draft_row_id="draft-row-2",
        row_order=2, test_item="DURABILITY, 20 Cycles", condition=None,
    )
    llcr_final = replace(
        source.rows[0], confirmed_row_id="row-3", draft_row_id="draft-row-3",
        row_order=3, test_item="CONTACT RESISTANCE AT LOW LEVEL", condition="100 mA max",
    )
    cr = replace(
        source.rows[0], confirmed_row_id="row-4", draft_row_id="draft-row-4",
        row_order=4, test_item="CONTACT RESISTANCE (Power)", condition="10 A max",
    )
    base = source.step_quantities[0]
    quantities = (
        replace(base, confirmed_row_id=llcr_initial.confirmed_row_id, draft_row_id=llcr_initial.draft_row_id, step_sequence=1, raw_token="1", contact_plan=None),
        replace(base, confirmed_step_quantity_id="quantity-2", confirmed_row_id=durability.confirmed_row_id, draft_row_id=durability.draft_row_id, step_sequence=2, raw_token="2", contact_plan=None),
        replace(base, confirmed_step_quantity_id="quantity-3", confirmed_row_id=llcr_final.confirmed_row_id, draft_row_id=llcr_final.draft_row_id, step_sequence=3, raw_token="3", contact_plan=None),
        replace(base, confirmed_step_quantity_id="quantity-4", confirmed_row_id=cr.confirmed_row_id, draft_row_id=cr.draft_row_id, step_sequence=4, raw_token="4", contact_plan=None),
    )
    return replace(
        source,
        groups=(replace(group, sample_quantity_expression="2"),),
        rows=(llcr_initial, durability, llcr_final, cr),
        step_quantities=quantities,
    )
