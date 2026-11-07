from dataclasses import replace, asdict
from types import SimpleNamespace

import pytest

from backend.application.report_authoring.photo_plan import ReportPhotoPlan
from backend.application.report_authoring.service import ReportAuthoringService
from backend.domain.report_authoring import ReportAuthoringState, ReportSource


def photo_service():
    sources = tuple(ReportSource(key, 'photo', name, 'a' * 64, 1, 'now') for key, name in [('a', 'SN1.png'), ('b', 'Renamed.png')])
    slots = [{'slot_id': key, 'supported': True, 'caption': 'Figure 1 Group Ab', 'media_sha256': 'old', 'coverage': 'needs_review'} for key in ('photo-1', 'photo-2')]
    output = {'output_id': 'out', 'artifact': asdict(ReportSource('out', 'working_copy', 'copy.docx', 'c' * 64, 1, 'now'))}
    state = ReportAuthoringState('P1', sources=sources, outputs=(output,))
    context = {'matrix_id': 'M1', 'steps': [{'group_id': 'g', 'row_id': 'r', 'step_token': '1', 'group_label': 'Ab'}]}
    review = {'review_sha256': 'b' * 64, 'slots': slots}
    authoring = SimpleNamespace(document_review=SimpleNamespace(current=lambda *_: (state, context, output, review)),
        assets=SimpleNamespace(read=lambda *_: b'copy'), _source=ReportAuthoringService._source,
        _source_family=ReportAuthoringService._source_family, _now=lambda: 'now',
        repository=SimpleNamespace(save=lambda updated, revision: replace(updated, revision=revision + 1)))
    assignment = {'scope': 'step', 'slot_id': 'photo-1', 'source_id': 'a', 'group_id': 'g', 'row_id': 'r',
        'step_token': '1', 'sample_ids': ['SN1'], 'stage': 'after', 'reason': 'Current specimen record', 'reuse_reason': '',
        'crop_mode': 'preserve', 'accept_slot_transform': False, 'accept_context_change': False}
    request = {'review_sha256': 'b' * 64, 'confirmed_by': 'Tester', 'assignments': [assignment]}
    return ReportPhotoPlan(authoring), request, state, context, review


def test_same_photo_bytes_under_different_names_require_explicit_reuse_reason():
    service, request, *_ = photo_service()
    request['assignments'].append({**request['assignments'][0], 'slot_id': 'photo-2', 'source_id': 'b'})
    with pytest.raises(ValueError, match='intentional reuse'):
        service.confirm('P1', request)
    for assignment in request['assignments']:
        assignment['reuse_reason'] = 'Intentional shared specimen overview for two stages'
    saved = service.confirm('P1', request)
    assert len(saved.outputs[-1]['photo_plan']['assignments']) == 2


def test_overview_does_not_require_a_fictional_step_but_step_caption_change_is_explicit():
    service, request, state, context, review = photo_service()
    review['slots'][0]['caption'] = 'Figure 1 Group ZZ'
    with pytest.raises(ValueError, match='another Group'):
        service.confirm('P1', request)
    request['assignments'][0]['accept_context_change'] = True
    assert service.confirm('P1', request).outputs[-1]['photo_plan']['assignments'][0]['accept_context_change']
    request['assignments'][0].update(scope='sample_overview', group_id='', row_id='', step_token='', accept_context_change=False)
    assert service.confirm('P1', request).outputs[-1]['photo_plan']['assignments'][0]['scope'] == 'sample_overview'


def test_a_confirmed_photo_plan_rejects_a_newer_source_version():
    service, request, state, context, review = photo_service()
    saved = service.confirm('P1', request)
    output = saved.outputs[-1]
    changed = replace(saved, sources=(*saved.sources, replace(saved.sources[0], source_id='new', sha256='d' * 64)))
    service.authoring.photos = SimpleNamespace(inspect=lambda _: [{key: value for key, value in slot.items() if key != 'coverage'} for slot in review['slots']])
    service.authoring.assets.path = lambda *_: 'copy'
    with pytest.raises(ValueError, match='source or target changed'):
        service.assignments(changed, context, output, output['photo_plan']['plan_id'])
