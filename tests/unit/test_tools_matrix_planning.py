import pytest
from backend.application.tools_matrix_planning import evaluate_planning_fees

def matrix():
    return {'groups':[{'draft_group_id':'g1','group_order':1,'group_key':'1','group_label':'1','is_selected':True,'sample_quantity_expression':'5'}],
      'rows':[{'draft_row_id':'r1','row_order':1,'test_item':'LLCR','method':'EIA-364-23','condition':'20mV','requirement':'20mOhm','is_sample_row':False}],
      'cells':[{'draft_group_id':'g1','draft_row_id':'r1','cell_value':'1'}],
      'point_profile':{'categories':[{'prefix':'HP','point_expression':'1,2','cr_selected':True}],'delta_r_enabled':True},
      'point_overrides':[], 'duration_authorities':[], 'step_text_overrides':[]}

def test_fee_estimate_reuses_matrix_points_and_has_stable_row_identity():
    first=evaluate_planning_fees(matrix())
    second=evaluate_planning_fees(matrix())
    line=first.groups[0].line_items[0]
    assert str(line.unit_price) == '1.5'
    assert str(line.units) == '10'
    assert line.line_id == second.groups[0].line_items[0].line_id
    assert first.header.project_id == ''


def test_estimate_respects_duration_and_step_override_without_confirming_authority():
    from backend.application.tools_matrix_snapshot import planning_snapshot
    payload = matrix()
    payload['rows'][0].update(test_item='High Temperature Life', condition='96 hours')
    payload['duration_authorities'] = [{
        'draft_group_id':'g1','draft_row_id':'r1','step_sequence':1,
        'duration_value':'96','duration_unit':'hour','source_kind':'manual_edit',
        'source_field':'condition','lineage_fingerprint':'planning-row','authority_revision':'1','status':'usable'}]
    payload['step_text_overrides'] = [{'draft_group_id':'g1','draft_row_id':'r1', 'step_sequence':1,
        'description':'High Temperature Life', 'requirement':'Retained requirement'}]
    payload['planned_test_start_date'] = '2026-11-06'
    snapshot = planning_snapshot(payload)
    assert snapshot.version.is_active_authority is False
    assert snapshot.version.planned_test_start_date == '2026-11-06'
    assert snapshot.step_text_overrides[0].requirement == 'Retained requirement'
    assert evaluate_planning_fees(payload).groups[0].line_items[0].units == 96


def test_legacy_pricing_remaps_exact_row_identity_and_preserves_unmatched():
    from dataclasses import replace
    from types import SimpleNamespace
    from backend.application.tools_matrix_snapshot import planning_snapshot
    from backend.application.tools_legacy_recovery import recover_pricing
    from backend.application.fee_evaluation_edited_export_values import (
        FeeEvaluationEditedExportRow, FeeEvaluationEditedExportSummary, FeeEvaluationEditedExportValues)
    snapshot = planning_snapshot(matrix())
    original = replace(snapshot,
        groups=(replace(snapshot.groups[0], confirmed_group_id='old-group'),),
        rows=(replace(snapshot.rows[0], confirmed_row_id='old-row'),))
    row = FeeEvaluationEditedExportRow('old-line','old-group','old-row','1',0,'2','3','per reading','7','0','0','21','manual')
    missing = replace(row,step_token='99')
    values = FeeEvaluationEditedExportValues((row,missing),FeeEvaluationEditedExportSummary('0','0','','200'))
    result, skipped = recover_pricing(matrix(), SimpleNamespace(edited_values=values), original)
    assert len(result.rows) == 1 and result.rows[0].units == '7'
    assert result.rows[0].confirmed_group_id == 'g1'
    assert result.rows[0].confirmed_row_id == 'r1'
    assert result.rows[0].source_line_id == 'tools-planning:1:r1:1:0'
    assert skipped == ['old-group / 99']
    assert values.rows == (row,missing)


def test_legacy_unmatched_manual_and_inactive_fees_are_reported_not_silently_discarded():
    from types import SimpleNamespace
    from backend.application.tools_legacy_recovery import recover_pricing
    from backend.application.fee_evaluation_edited_export_values import FeeEvaluationEditedExportValues, FeeEvaluationEditedExportSummary, FeeEvaluationEditedManualRow
    manual = FeeEvaluationEditedManualRow('sample_preparation','1','50','per sample','2','0','0','100','retained','absent','99','99')
    values=FeeEvaluationEditedExportValues((),FeeEvaluationEditedExportSummary('0','0','','200'),(manual,),
        (SimpleNamespace(previous_row=SimpleNamespace(step_token='7')),))
    copied, skipped=recover_pricing(matrix(),SimpleNamespace(edited_values=values),None)
    assert copied.manual_rows == ()
    assert skipped == ['sample_preparation / 99','Inactive fee row / 7']
    assert values.manual_rows == (manual,)


def test_legacy_unselected_matrix_keeps_recovery_available_with_saved_fees():
    from types import SimpleNamespace
    from backend.application.tools_legacy_recovery import recover_pricing
    from backend.application.fee_evaluation_edited_export_values import FeeEvaluationEditedExportValues, FeeEvaluationEditedExportSummary
    payload=matrix();payload['groups'][0]['is_selected']=False
    values=FeeEvaluationEditedExportValues((),FeeEvaluationEditedExportSummary('0','0','','200'))
    copied,skipped=recover_pricing(payload,SimpleNamespace(edited_values=values),None)
    assert copied is None
    assert 'Select at least one Matrix group' in skipped[0]
