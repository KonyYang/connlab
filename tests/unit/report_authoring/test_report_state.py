from backend.application.report_authoring.service import ReportAuthoringService
from backend.domain.report_authoring import ReportAuthoringState


def test_current_result_set_supersedes_previous_measurement_at_same_matrix_target():
    target = {'group_id': 'g1', 'row_id': 'r1', 'step_token': '2'}
    old = {'result_id': 'old', 'target': target, 'kind': 'temperature'}
    new = {'result_id': 'new', 'target': target, 'kind': 'temperature'}
    state = ReportAuthoringState('P1', results=(old, new), outputs=(
        {'operation': 'prepare_base'}, {'operation': 'result_update', 'evidence': {'result_id': 'old'}},
        {'operation': 'photo_replacement'}, {'operation': 'result_update', 'evidence': {'result_id': 'new'}}))
    assert ReportAuthoringService.active_result_ids(state) == ['new']
    restarted = ReportAuthoringState('P1', results=(old, new), outputs=(*state.outputs, {'operation': 'prepare_base'}))
    assert ReportAuthoringService.active_result_ids(restarted) == []
