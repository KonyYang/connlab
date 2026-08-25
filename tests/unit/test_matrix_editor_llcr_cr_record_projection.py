from backend.application.contact_point_profile_confirmed_consumer_adapter import (
    EffectiveConfirmedPointProfile,
)
from backend.application.matrix_editor_llcr_cr_record_projection import (
    MatrixEditorLlcrCrRecordGroupInput,
    MatrixEditorLlcrCrRecordRowInput,
    build_matrix_editor_llcr_cr_record_projection,
)


def test_current_matrix_editor_draft_sample_quantity_drives_llcr_rows() -> None:
    projection = build_matrix_editor_llcr_cr_record_projection(
        project_id="project-1",
        record_type="llcr",
        groups=(
            MatrixEditorLlcrCrRecordGroupInput(
                group_key="group_6",
                group_label="6",
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorLlcrCrRecordRowInput(
                test_item="Contact Resistance (Low Level)",
                condition="20 mV, 100 mA",
                requirement="Initial <= 0.25 mOhm; delta R <= 0.17 mOhm",
                group_values={"group_6": "2,6"},
            ),
        ),
        point_profile=_point_profile(),
    )

    assert projection.status == "ready"
    assert projection.record_type == "llcr"
    assert projection.confirmed_matrix_id == "Unconfirmed Matrix draft"
    assert projection.matrix_source == "matrix_editor_current_ui_state"
    assert projection.sections[0].sample_count == 5
    assert len(projection.sections[0].rows) == 10
    assert [stage.source_step for stage in projection.sections[0].stages] == ["2", "6"]


def test_current_matrix_editor_draft_accepts_footnoted_sample_quantity() -> None:
    projection = build_matrix_editor_llcr_cr_record_projection(
        project_id="project-1",
        record_type="llcr",
        groups=(
            MatrixEditorLlcrCrRecordGroupInput(
                group_key="group_3",
                group_label="3",
                sample_quantity_expression="3(a)",
                sample_note="(a) Male connector and Female connector",
            ),
        ),
        rows=(
            MatrixEditorLlcrCrRecordRowInput(
                test_item="Contact Resistance (Low Level)",
                group_values={"group_3": "2"},
            ),
        ),
        point_profile=_point_profile(),
    )

    assert projection.status == "ready"
    assert projection.diagnostics == ()
    assert projection.sections[0].sample_count == 3
    assert len(projection.sections[0].rows) == 6


def test_ambiguous_composite_sample_quantity_requires_review() -> None:
    projection = build_matrix_editor_llcr_cr_record_projection(
        project_id="project-1",
        record_type="llcr",
        groups=(
            MatrixEditorLlcrCrRecordGroupInput(
                group_key="group_6",
                group_label="6",
                sample_quantity_expression="5+5(d)",
                sample_note="(d) Split samples between two test methods.",
            ),
        ),
        rows=(
            MatrixEditorLlcrCrRecordRowInput(
                test_item="Contact Resistance (Low Level)",
                group_values={"group_6": "2"},
            ),
        ),
        point_profile=_point_profile(),
    )

    assert projection.status == "review_required"
    assert projection.sections == ()
    assert projection.diagnostics[0].code == "sample_quantity_not_positive_integer"


def test_explicit_llcr_and_dwv_split_uses_only_the_llcr_sample_allocation() -> None:
    projection = build_matrix_editor_llcr_cr_record_projection(
        project_id="project-1",
        record_type="llcr",
        groups=(
            MatrixEditorLlcrCrRecordGroupInput(
                group_key="group_6",
                group_label="6",
                sample_quantity_expression="5+5(d)",
                sample_note=(
                    "(d) 5pcs for LLCR test another 5pcs loose connector for DWV test."
                ),
            ),
        ),
        rows=(
            MatrixEditorLlcrCrRecordRowInput(
                test_item="Contact Resistance (Low Level)",
                group_values={"group_6": "2"},
            ),
        ),
        point_profile=_point_profile(),
    )

    assert projection.status == "ready"
    assert projection.sections[0].sample_count == 5
    assert len(projection.sections[0].rows) == 10


def _point_profile() -> EffectiveConfirmedPointProfile:
    return EffectiveConfirmedPointProfile(
        status="confirmed",
        readings_per_sample="2",
        revision_id="profile-1",
        revision_sequence=3,
        fingerprint="profile-fingerprint",
        lineage="Confirmed Project Point Profile",
        message=None,
        categories=(
            {
                "category_id": "signal",
                "category_ordinal": 0,
                "label": "Signal",
                "count_per_sample": 2,
                "record_prefix": "SIG",
                "included": True,
                "point_expression": "1-2",
            },
        ),
    )
