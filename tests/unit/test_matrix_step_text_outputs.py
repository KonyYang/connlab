from types import SimpleNamespace as NS

from backend.application.confirmed_matrix_test_record_preview_service import (
    BuildConfirmedMatrixTestRecordPreviewCommand, ConfirmedMatrixTestRecordPreviewService,
)
from backend.application.matrix_editor_test_record_authority import (
    ConfirmedMatrixTestRecordAuthorityMatcher, build_matrix_editor_test_record_signature,
)


def snapshot():
    groups = tuple(NS(confirmed_group_id=f"c{k}", group_key=k, group_label=k,
                      sample_quantity_expression="5") for k in ("g1", "g2"))
    row = NS(confirmed_row_id="r1", row_order=1, test_item="LLCR", source_section="6.1",
             method="M1", condition="Normal", requirement="Initial: 10; Delta: 20")
    return NS(version=NS(project_id="P1", confirmed_matrix_id="v1", confirmed_revision=1),
              groups=groups, rows=(row,), step_quantities=(),
              cells=tuple(NS(confirmed_group_id=g.confirmed_group_id, confirmed_row_id="r1",
                             cell_value="1,2(a),3") for g in groups),
              step_text_overrides=(NS(confirmed_group_id="cg1", confirmed_row_id="r1",
                                     step_sequence=2, step_suffix_note="(a)",
                                     description=" Only this step ", requirement=""),))


class Store:
    def __init__(self, value):
        self.value = value

    def get_active_by_project(self, project_id):
        return self.value


def test_confirmed_step_text_overrides_only_exact_step_after_derived_defaults():
    source = snapshot()
    result = ConfirmedMatrixTestRecordPreviewService(confirmed_store=Store(source)).build_preview(
        BuildConfirmedMatrixTestRecordPreviewCommand(project_id="P1")
    )
    step = result.groups[0].steps[1]
    assert step.test_item == "LLCR"
    assert step.description == " Only this step "
    assert step.requirement == ""
    assert result.groups[0].steps[0].description is None
    assert result.groups[1].steps[1].description is None
    assert result.groups[1].steps[1].requirement != ""
    assert source.rows[0].requirement == "Initial: 10; Delta: 20"


def test_formal_matcher_requires_exact_step_text_and_normalizes_sample_row_positions():
    source = snapshot()
    matcher = ConfirmedMatrixTestRecordAuthorityMatcher(Store(source))
    rows = (NS(test_item="samples", is_sample_row=True),
            NS(test_item="LLCR", section="6.1", method="M1", condition="Normal",
               requirement="Initial: 10; Delta: 20", is_sample_row=False,
               group_values={"g1": "1,2(a),3", "g2": "1,2(a),3"}))
    override = NS(group_key="g1", row_order=2, step_sequence=2, step_suffix_note="(a)",
                  description=" Only this step ", requirement="")
    signature = build_matrix_editor_test_record_signature(
        groups=source.groups, rows=rows, step_text_overrides=(override,))
    assert matcher.matches_active_authority("P1", signature)
    override.description = "unsaved change"
    assert not matcher.matches_active_authority("P1", build_matrix_editor_test_record_signature(
        groups=source.groups, rows=rows, step_text_overrides=(override,)))
    assert not matcher.matches_active_authority("P1", build_matrix_editor_test_record_signature(
        groups=source.groups, rows=rows))


def test_live_draft_document_keeps_step_text_and_does_not_change_classification(tmp_path):
    from backend.application.matrix_editor_test_record_document_generation_service import (
        GenerateMatrixEditorTestRecordDocumentCommand, MatrixEditorTestRecordDocumentGenerationService,
        MatrixEditorTestRecordGroupInput, MatrixEditorTestRecordRowInput,
    )
    from backend.application.matrix_step_text_output import MatrixStepTextOutputOverride

    class Writer:
        def generate_from_confirmed_matrix(self, **kwargs):
            self.groups = kwargs["groups"]
            return kwargs["output_path"]

    template = tmp_path / "template.docx"
    template.touch()
    writer = Writer()
    service = MatrixEditorTestRecordDocumentGenerationService(
        project_store=NS(get=lambda _: NS(project_no="P1", product_name="test")), writer=writer)
    service.generate(GenerateMatrixEditorTestRecordDocumentCommand(
        project_id="P1", output_dir=tmp_path, template_path=template,
        groups=(MatrixEditorTestRecordGroupInput("g1", "1", "5"),),
        rows=(MatrixEditorTestRecordRowInput("samples", is_sample_row=True),
              MatrixEditorTestRecordRowInput("LLCR", requirement="Initial: 10; Delta: 20",
                                             group_values={"g1": "1,2(a),3"})),
        step_text_overrides=(MatrixStepTextOutputOverride("g1", 2, 2, "(a)", " Special ", ""),),
    ))
    assert writer.groups[0].steps[1].test_item == "LLCR"
    assert writer.groups[0].steps[1].description == " Special "
    assert writer.groups[0].steps[1].requirement == ""
    assert writer.groups[0].steps[0].description is None


def test_runtime_selected_step_uses_confirmed_text_without_spreading_to_other_tokens():
    from backend.application.confirmed_matrix_runtime_projection_service import (
        BuildConfirmedMatrixRuntimeProjectionCommand, ConfirmedMatrixRuntimeProjectionService,
    )
    from backend.application.runtime_projection_read_only_service import RuntimeProjectionReadOnlyService

    source = snapshot()
    service = ConfirmedMatrixRuntimeProjectionService(
        confirmed_store=Store(source), runtime_projection_service=RuntimeProjectionReadOnlyService())
    result = service.build_snapshot(BuildConfirmedMatrixRuntimeProjectionCommand(
        project_id="P1", selected_token_reference="P1|v1:r1|g1|2|(a)"))
    token = result.step_workspace.selected_token
    assert token.test_item_label == " Only this step "
    assert token.requirement == ""
    other = service.build_snapshot(BuildConfirmedMatrixRuntimeProjectionCommand(
        project_id="P1", selected_token_reference="P1|v1:r1|g2|2|(a)"))
    assert other.step_workspace.selected_token.test_item_label == "LLCR"


def test_live_output_rejects_stale_suffix_or_duplicate_override_before_publication():
    import pytest

    source = snapshot()
    row = NS(test_item="LLCR", section="", method="", condition="", requirement="",
             is_sample_row=False, group_values={"g1": "2(a)", "g2": "2(a)"})
    override = NS(group_key="g1", row_order=1, step_sequence=2, step_suffix_note="(b)",
                  description="x", requirement=None)
    with pytest.raises(ValueError, match="unknown step"):
        build_matrix_editor_test_record_signature(groups=source.groups, rows=(row,),
                                                  step_text_overrides=(override,))
    override.step_suffix_note = "(a)"
    with pytest.raises(ValueError, match="Duplicate"):
        build_matrix_editor_test_record_signature(groups=source.groups, rows=(row,),
                                                  step_text_overrides=(override, override))
