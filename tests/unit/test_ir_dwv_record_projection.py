from dataclasses import replace

import pytest

from backend.application.matrix_editor_ir_dwv_record_projection import (
    build_matrix_editor_ir_dwv_record_projection,
)
from backend.application.matrix_editor_llcr_cr_record_projection import (
    MatrixEditorLlcrCrRecordGroupInput as Group,
    MatrixEditorLlcrCrRecordRowInput as Row,
)
from backend.application.matrix_step_text_output import MatrixStepTextOutputOverride
from backend.domain.matrix_contact_measurement_models import MatrixPointProfile


def _build(**patch):
    values = dict(
        project_id="P1",
        groups=(Group("g1", "1", "5+5(d)", draft_group_id="group-1"),),
        rows=(
            Row("IR", condition="500VDC 2min. unmated", group_values={"g1": "2,6"}, draft_row_id="ir"),
            Row("Reseating", group_values={"g1": "4"}, draft_row_id="reseating"),
            Row("DWV", condition="1500VDC 1min.", group_values={"g1": "2,6"}, draft_row_id="dwv"),
        ),
        point_profile=MatrixPointProfile((), electrical_point_pairs="Odd&Even，P1 and S2; PE-HOUSING"),
    )
    values.update(patch)
    return build_matrix_editor_ir_dwv_record_projection(**values)


def test_projection_combines_equal_step_numbers_and_uses_primary_samples():
    result = _build()
    assert result.status == "ready"
    group = result.workbook.groups[0]
    assert group.label == "Group 1"
    assert group.sample_count == 5
    assert len(group.steps) == 2
    assert [step.label for step in group.steps] == ["Initial", "Final"]
    assert group.steps[0].measurement_pairs == ("Odd&Even", "P1 and S2", "PE-HOUSING")
    assert group.steps[0].expected_fee_quantity == 15
    assert group.steps[0].ir_condition == "500VDC 2min. unmated"
    assert group.steps[0].dwv_condition == "1500VDC 1min."
    assert any(item.code == "primary_sample_quantity" for item in result.diagnostics)


def test_projection_combines_adjacent_ir_and_dwv_steps_as_one_round():
    result = _build(rows=(
        Row("Insulation Resistance", condition="500 V", group_values={"g1": "2"}),
        Row("Dielectric Withstanding Voltage", condition="1500 V", group_values={"g1": "3"}),
    ))
    assert [(step.ir_enabled, step.dwv_enabled) for step in result.workbook.groups[0].steps] == [
        (True, True),
    ]


def test_projection_preserves_explicit_stage_description():
    result = _build(step_text_overrides=(MatrixStepTextOutputOverride(
        group_key="g1", row_order=1, step_sequence=6, step_suffix_note="",
        description="After reseating", requirement=None,
    ),))
    assert result.workbook.groups[0].steps[1].label == "After reseating"
    assert result.workbook.groups[0].steps[1].description_is_override


def test_projection_follows_group_execution_rounds_and_retains_both_source_steps():
    result = _build(rows=(
        Row("Visual", group_values={"g1": "1,10"}),
        Row("IR", condition="500 VDC 2 min", requirement="1000 MΩ minimum", group_values={"g1": "2,5,8"}),
        Row("DWV", condition="1500 VDC 1 min", requirement="1 mA maximum", group_values={"g1": "3,6,9"}),
        Row("Thermal Shock", group_values={"g1": "4"}),
        Row("Humidity", group_values={"g1": "7"}),
    ))
    assert result.status == "ready"
    steps = result.workbook.groups[0].steps
    assert len(steps) == 3
    assert [step.label for step in steps] == ["Initial", "After Thermal Shock", "Final"]
    assert all(step.ir_enabled and step.dwv_enabled for step in steps)
    assert [(step.ir_source_step.step_sequence, step.dwv_source_step.step_sequence) for step in steps] == [(2, 3), (5, 6), (8, 9)]
    assert steps[0].ir_source_step.requirement == "1000 MΩ minimum"
    assert steps[0].dwv_source_step.requirement == "1 mA maximum"


@pytest.mark.parametrize("separator", [
    Row("Humidity", group_values={"g1": "3"}),
    Row("DWV", group_values={"g1": "3(b)"}),
])
def test_projection_does_not_zip_electrical_sides_across_operations_or_suffixes(separator):
    rows = (Row("IR", group_values={"g1": "2(a)"}), separator)
    if separator.test_item != "DWV":
        rows += (Row("DWV", group_values={"g1": "4(a)"}),)
    result = _build(rows=rows)
    assert [(step.ir_enabled, step.dwv_enabled) for step in result.workbook.groups[0].steps] == [(True, False), (False, True)]


def test_projection_blocks_duplicate_electrical_step_identity():
    result = _build(rows=(Row("IR", group_values={"g1": "2"}), Row("IR", group_values={"g1": "2"}), Row("DWV", group_values={"g1": "3"})))
    assert result.status == "blocked"
    assert result.workbook.groups == ()
    assert any(item.code == "ambiguous_step" for item in result.diagnostics)


@pytest.mark.parametrize("profile", [None, MatrixPointProfile((), ir_points_per_sample="1", dwv_points_per_sample="1")])
def test_projection_blocks_count_only_points_without_inventing_pair_names(profile):
    result = _build(point_profile=profile)
    assert result.status == "blocked"
    assert result.workbook.groups == ()
    assert any("measurement pairs" in item.message for item in result.diagnostics)


@pytest.mark.parametrize("samples", ["0", "3.5", "unknown"])
def test_projection_blocks_invalid_sample_quantity(samples):
    result = _build(groups=(Group("g1", "1", samples),))
    assert result.status == "blocked"


def test_generation_context_uses_authority_and_changes_fingerprint(tmp_path):
    from types import SimpleNamespace
    from backend.application.matrix_editor_ir_dwv_record_generation_service import MatrixEditorIrDwvRecordGenerationService
    from backend.application.matrix_editor_llcr_cr_record_generation_service import GenerateMatrixEditorLlcrCrRecordCommand
    basic = SimpleNamespace(version=1, values={"product_description": "Connector", "requested_by": "Requestor", "project_leader": "Not the tester"})
    template = SimpleNamespace(template_fingerprint=lambda: "template-one", validate_projection=lambda _: None)
    service = MatrixEditorIrDwvRecordGenerationService(
        confirmed_store=SimpleNamespace(get_active_by_project=lambda _: None),
        basic_information_store=SimpleNamespace(get_latest_confirmed=lambda _: basic),
        ltr_store=SimpleNamespace(list_by_project=lambda _: [SimpleNamespace(status="registered", ltr_number="DL-001", registered_on="2026-10-01")]),
        workbook_gateway=template, artifact_store=None,
    )
    draft = GenerateMatrixEditorLlcrCrRecordCommand("P1", "ir_dwv", (Group("g1", "1", "7"),), (Row("IR", group_values={"g1": "2"}),), point_profile=MatrixPointProfile((), electrical_point_pairs="Odd&Even"))
    first = service.build_draft_projection(**{key: getattr(draft, key) for key in draft.__dataclass_fields__})
    assert first.workbook.product_name == "Connector"
    assert first.workbook.requestor == "Requestor"
    assert first.workbook.tested_by == ""
    assert first.workbook.equipment == ()
    assert any(item.code == "equipment_template_defaults" and "Instrument" in item.message and "Gage ID" in item.message for item in first.diagnostics)
    basic.values["product_description"] = "Updated connector"
    changed = service.build_draft_projection(**{key: getattr(draft, key) for key in draft.__dataclass_fields__})
    assert changed.preview_fingerprint != first.preview_fingerprint
    template.template_fingerprint = lambda: "template-two"
    assert service.build_draft_projection(**{key: getattr(draft, key) for key in draft.__dataclass_fields__}).preview_fingerprint != changed.preview_fingerprint


def test_generation_context_reports_template_failure_as_blocker():
    from types import SimpleNamespace
    from backend.application.matrix_editor_ir_dwv_record_generation_service import MatrixEditorIrDwvRecordGenerationService
    def unavailable():
        raise ValueError("Template is locked by Excel")
    service = MatrixEditorIrDwvRecordGenerationService(
        confirmed_store=SimpleNamespace(get_active_by_project=lambda _: None),
        basic_information_store=SimpleNamespace(get_latest_confirmed=lambda _: None),
        ltr_store=SimpleNamespace(list_by_project=lambda _: []),
        workbook_gateway=SimpleNamespace(template_fingerprint=unavailable), artifact_store=None,
    )
    result = service.build_draft_projection(project_id="P1", groups=(Group("g1", "1", "5"),), rows=(Row("IR", group_values={"g1": "1"}),), point_profile=MatrixPointProfile((), electrical_point_pairs="Odd&Even"))
    assert result.status == "blocked"
    assert any(item.level == "error" and "locked" in item.message for item in result.diagnostics)
