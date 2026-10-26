from dataclasses import replace
from backend.application.report_authoring.service import ReportAuthoringService
from backend.domain.report_authoring import ReportAuthoringState, ReportSource, ReportMapping
import pytest


@pytest.mark.parametrize('change', ['matrix', 'source', 'report', 'decision'])
def test_read_state_invalidates_customer_check_but_keeps_history(change):
    source = ReportSource('s1', 'original', 'Report.docx', 'a'*64, 1, 'now')
    mapping = ReportMapping('m1', 's1', 'acceptance', 'Approval', 'Source record', value='Pass', status='confirmed',
        reason='Project-specific evidence', group_id='g', row_id='r', step_token='1', matrix_id='matrix1')
    state = ReportAuthoringState('P1', sources=(source,), mappings=(mapping,), base_source_id='s1',
        outputs=({'operation': 'prepare_base', 'output_id': 'o1', 'artifact': {'sha256': 'b'*64}},))
    context = {'matrix_id': 'matrix1'}
    audit = {'passed': True, 'issues': [], 'review_context_sha256': ReportAuthoringService._review_context_sha256(state, context)}
    state = replace(state, customer_outputs=({'output_id': 'c1', 'status': 'package_checked', 'audit': audit},))
    if change == 'matrix': context = {'matrix_id': 'matrix2'}
    if change == 'source': state = replace(state, sources=(source, replace(source, source_id='s2', sha256='c'*64)))
    if change == 'report': state = replace(state, outputs=({'operation': 'prepare_base', 'output_id': 'o2', 'artifact': {'sha256': 'c'*64}},))
    if change == 'decision': state = replace(state, mappings=(replace(mapping, status='pending'),))
    class Repository:
        def get(self, project_id): return state
    service = ReportAuthoringService(repository=Repository(), assets=None, inspect_upload=None, project_context=lambda _: context)
    effective, _ = service.state('P1')
    customer = effective.customer_outputs[-1]
    assert customer['status'] == 'needs_review' and not customer['audit']['passed']
    assert customer['recorded_audit']['passed']
