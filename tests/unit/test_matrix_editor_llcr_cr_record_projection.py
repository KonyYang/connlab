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


def test_exact_draft_step_text_reaches_llcr_stages_without_changing_record_type(tmp_path):
    from backend.application.matrix_step_text_output import MatrixStepTextOutputOverride

    projection = build_matrix_editor_llcr_cr_record_projection(
        project_id="project-1", record_type="llcr",
        groups=(MatrixEditorLlcrCrRecordGroupInput("g1", "1", "5"),),
        rows=(MatrixEditorLlcrCrRecordRowInput("sample", is_sample_row=True),
              MatrixEditorLlcrCrRecordRowInput("LLCR", requirement="<= 10 mOhm",
                                               group_values={"g1": "1,2(a),3"})),
        point_profile=_point_profile(),
        step_text_overrides=(MatrixStepTextOutputOverride("g1", 2, 2, "(a)", "Custom stage", ""),),
    )
    assert projection.status == "ready"
    stages = projection.sections[0].stages
    assert stages[1].label == "Custom stage"
    assert stages[1].test_item == "LLCR"
    assert stages[1].requirement == ""
    assert stages[0].label == "Initial"
    assert stages[2].label == "Final"
    from backend.infrastructure.office.llcr_cr_specialized_record_workbook_gateway import (
        LlcrCrSpecializedRecordWorkbookGateway,
    )
    from openpyxl import load_workbook

    path = LlcrCrSpecializedRecordWorkbookGateway().write(
        output_path=tmp_path / "record.xlsx", projection=projection)
    workbook = load_workbook(path)
    try:
        assert workbook["Summary"]["B4"].value == "Custom stage"
        assert workbook["SIG"]["B12"].value == "Custom stage"
    finally:
        workbook.close()
