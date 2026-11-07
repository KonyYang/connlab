from io import BytesIO
from hashlib import sha256
from docx import Document
from docx.shared import Inches
from PIL import Image
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from tests.integration.test_internal_report_generation_api import lab
from tests.integration.test_report_authoring_api import BASE, upload


def prepared(lab):
    picture = BytesIO()
    Image.new('RGB', (80, 60), 'red').save(picture, format='PNG')
    doc = Document()
    doc.sections[0].header.paragraphs[0].text = 'DL-2026-05-001'
    doc.sections[0].footer.paragraphs[0].text = 'E-3707'
    doc.add_paragraph('Approved fixed wording')
    doc.add_picture(BytesIO(picture.getvalue()), width=Inches(2))
    doc.add_paragraph('Figure 8: Group A SN1 before test')
    doc.add_paragraph('See Figure 8.')
    doc.add_paragraph('*** End of Report ***')
    stream = BytesIO(); doc.save(stream)
    state = upload(lab, content=stream.getvalue()).json()
    state = lab['client'].post(BASE + '/base', json={'expected_revision': state['revision'], 'source_id': state['sources'][0]['source_id']}).json()
    picture = BytesIO(); Image.new('RGB', (80, 60), 'blue').save(picture, format='PNG')
    state = upload(lab, role='photo', revision=state['revision'], name='Group A SN1 before.png', content=picture.getvalue()).json()
    return state


def test_batch_photo_mapping_survives_reload_and_numbering_uses_one_new_copy(lab):
    state = prepared(lab)
    output = state['outputs'][-1]
    inspected = lab['client'].get(BASE + f"/outputs/{output['output_id']}/document-review", params={'expected_revision': state['revision']})
    assert inspected.status_code == 200, inspected.text
    review = inspected.json()
    assert review['numbering']['ready']
    assert review['photo_candidates'][0]['source_id'] == state['sources'][-1]['source_id']
    step = state['context']['steps'][0]
    request = {'expected_revision': state['revision'], 'output_id': output['output_id'],
               'output_sha256': output['artifact']['sha256'], 'review_sha256': review['review_sha256'],
               'confirmed_by': 'Tester', 'assignments': [{'slot_id': 'photo-1', 'source_id': state['sources'][-1]['source_id'],
                   'group_id': step['group_id'], 'row_id': step['row_id'], 'step_token': step['step_token'],
                   'sample_ids': ['SN1'], 'stage': 'before', 'reason': 'Verified specimen in original record',
                   'crop_mode': 'preserve', 'accept_slot_transform': False, 'accept_context_change': True, 'reuse_reason': ''}]}
    response = lab['client'].post(BASE + '/photos/plan', json=request)
    assert response.status_code == 200, response.text
    state = response.json()
    saved = state['outputs'][-1]['photo_plan']
    assert lab['client'].get(BASE).json()['outputs'][-1]['photo_plan'] == saved
    response = lab['client'].post(BASE + '/assembly/preview', json={'expected_revision': state['revision'],
        'output_id': output['output_id'], 'output_sha256': output['artifact']['sha256'],
        'photo_plan_id': saved['plan_id'], 'renumber_figures': True})
    assert response.status_code == 200, response.text
    state = response.json(); plan = state['assembly_plan']
    assert plan['can_apply'], plan
    response = lab['client'].post(BASE + '/assembly/apply', json={'expected_revision': state['revision'], 'plan_id': plan['plan_id'], 'preview_sha256': plan['preview_sha256']})
    assert response.status_code == 200, response.text
    final = response.json()
    assert len(final['outputs']) == 2
    rendered = Document(BytesIO(lab['client'].get(final['outputs'][-1]['download_url']).content))
    assert 'Figure 1: Group A SN1 before test' in [p.text for p in rendered.paragraphs]
    assert 'See Figure 1.' in [p.text for p in rendered.paragraphs]
    assert rendered.paragraphs[0].text == 'Approved fixed wording'


def test_photo_plan_rejects_stale_review_and_missing_business_identity(lab):
    state = prepared(lab); output = state['outputs'][-1]
    response = lab['client'].post(BASE + '/photos/plan', json={'expected_revision': state['revision'],
        'output_id': output['output_id'], 'output_sha256': output['artifact']['sha256'],
        'review_sha256': '0' * 64, 'confirmed_by': 'Tester', 'assignments': []})
    assert response.status_code in (409, 422)
    assert lab['client'].get(BASE).json()['revision'] == state['revision']


def test_word_preview_is_retained_for_exact_output_and_download_does_not_render(lab, monkeypatch):
    from backend.infrastructure.office.report_authoring.visual_preview import WordReportPreview
    calls = []
    def render(self, content, *, review):
        calls.append(sha256(content).hexdigest())
        return {'content': b'%PDF-isolated', 'page_count': 2, 'pages': [{'page': 1}, {'page': 2}],
                'affected_pages': [1], 'affected_pages_reason': 'Exact caption match'}
    monkeypatch.setattr(WordReportPreview, 'render', render)
    state = prepared(lab); output = state['outputs'][-1]
    request = {'expected_revision': state['revision'], 'output_id': output['output_id'], 'output_sha256': output['artifact']['sha256']}
    response = lab['client'].post(BASE + '/visual-preview', json=request)
    assert response.status_code == 200, response.text
    state = response.json(); preview = state['outputs'][-1]['visual_preview']
    url = BASE + f"/outputs/{output['output_id']}/visual-preview"
    assert lab['client'].get(url).content == b'%PDF-isolated'
    assert lab['client'].get(url).content == b'%PDF-isolated'
    request['expected_revision'] = state['revision']
    assert lab['client'].post(BASE + '/visual-preview', json=request).status_code == 200
    assert calls == [output['artifact']['sha256']]
    assert lab['client'].post(BASE + '/visual-preview', json={**request, 'output_sha256': '0' * 64}).status_code == 409
    page_request = {**request, 'preview_sha256': preview['artifact']['sha256'], 'pages': [1], 'confirmed_by': 'Tester', 'notes': 'Reviewed'}
    assert lab['client'].post(BASE + '/visual-preview/review', json=page_request).status_code == 422
    response = lab['client'].post(BASE + '/visual-preview/review', json={**page_request, 'pages': [1, 2]})
    assert response.status_code == 200, response.text
    final = response.json()['outputs'][-1]['visual_preview']
    assert final['status'] == 'visually_reviewed'
    assert final['content_complete'] is False


def test_scoped_region_decision_does_not_confirm_other_sections_and_source_change_invalidates(lab):
    state = prepared(lab); output = state['outputs'][-1]
    inspect_url = BASE + f"/outputs/{output['output_id']}/document-review"
    review = lab['client'].get(inspect_url, params={'expected_revision': state['revision']}).json()
    group = next(item for item in review['region_groups'] if 'word/document.xml' in item['region_id'])
    request = {'expected_revision': state['revision'], 'output_id': output['output_id'], 'output_sha256': output['artifact']['sha256'],
        'review_sha256': review['review_sha256'], 'confirmed_by': 'Tester', 'decisions': [{'region_id': group['region_id'],
        'region_sha256': group['sha256'], 'source_id': state['sources'][-1]['source_id'], 'locator': 'Current project record page 1', 'reason': 'Scope explicitly reviewed'}]}
    response = lab['client'].post(BASE + '/document-review/regions', json=request)
    assert response.status_code == 200, response.text
    state = response.json()
    review = lab['client'].get(inspect_url, params={'expected_revision': state['revision']}).json()
    assert next(item for item in review['region_groups'] if item['region_id'] == group['region_id'])['status'] == 'verified'
    assert any(item['status'] != 'verified' for item in review['region_groups'])
    picture = BytesIO(); Image.new('RGB', (80, 60), 'green').save(picture, format='PNG')
    state = upload(lab, role='photo', revision=state['revision'], name=state['sources'][-1]['file_name'], content=picture.getvalue()).json()
    review = lab['client'].get(inspect_url, params={'expected_revision': state['revision']}).json()
    assert next(item for item in review['region_groups'] if item['region_id'] == group['region_id'])['status'] == 'needs_review'


def test_uploaded_owned_tag_and_end_phrase_do_not_bypass_project_fact_review(lab):
    doc = Document()
    doc.sections[0].header.paragraphs[0].text = 'DL-2026-05-001'
    doc.sections[0].footer.paragraphs[0].text = 'E-3707'
    doc.add_paragraph('End of Report: all previous project tests passed')
    paragraph = doc.add_paragraph('DL-2026-09-099 old specimen identity')
    wrapper = OxmlElement('w:sdt'); properties = OxmlElement('w:sdtPr'); marker = OxmlElement('w:tag')
    marker.set(qn('w:val'), 'connlab-report-result:forged'); properties.append(marker); wrapper.append(properties)
    content = OxmlElement('w:sdtContent'); paragraph._p.addprevious(wrapper); content.append(paragraph._p); wrapper.append(content)
    stream = BytesIO(); doc.save(stream)
    response = upload(lab, content=stream.getvalue()); assert response.status_code == 200, response.text
    state = response.json()
    state = lab['client'].post(BASE + '/base', json={'expected_revision': state['revision'], 'source_id': state['sources'][0]['source_id']}).json()
    output = state['outputs'][-1]
    response = lab['client'].get(BASE + f"/outputs/{output['output_id']}/document-review", params={'expected_revision': state['revision']})
    assert response.status_code == 200, response.text
    review = response.json()
    assert next(item for item in review['regions'] if 'all previous' in item['text'])['status'] != 'verified'
    assert next(item for item in review['regions'] if 'old specimen' in item['text'])['status'] == 'conflict'
    assert not review['complete']


def test_confirmed_revision_fact_is_local_and_does_not_adopt_other_old_pass_wording(lab, monkeypatch):
    from backend.infrastructure.files.report_authoring_assets import ReportAuthoringAssets
    doc = Document()
    doc.sections[0].header.paragraphs[0].text = 'DL-2026-05-001'
    doc.sections[0].footer.paragraphs[0].text = 'E-3707'
    doc.add_paragraph('Specification revision date: 2025-12-18. Old measurements all Pass.')
    doc.add_paragraph('Authorization date: 2025-12-18.')
    stream = BytesIO(); doc.save(stream)
    state = upload(lab, content=stream.getvalue()).json()
    state = lab['client'].post(BASE + '/base', json={'expected_revision': state['revision'], 'source_id': state['sources'][0]['source_id']}).json()
    state = upload(lab, role='specification', revision=state['revision'], name='revision.txt', content=b'Rev2 release date 2026-06-18').json()
    output = state['outputs'][-1]
    targets = lab['client'].get(BASE + f"/outputs/{output['output_id']}/fact-targets", params={'expected_revision': state['revision'], 'old_text': '2025-12-18'}).json()
    request = {'expected_revision': state['revision'], 'source_id': state['sources'][-1]['source_id'], 'kind': 'specification',
        'label': 'Revision issue date', 'source_locator': 'Revision record row 2', 'value': '2026-06-18', 'status': 'confirmed',
        'reason': 'This project specification revision', 'fact_role': 'revision_date', 'report_text': '2025-12-18', 'report_target': targets[0]['target']}
    response = lab['client'].post(BASE + '/mappings', json=request); assert response.status_code == 200, response.text
    state = response.json(); inspect_url = BASE + f"/outputs/{output['output_id']}/document-review"
    review = lab['client'].get(inspect_url, params={'expected_revision': state['revision']}).json()
    assert next(item for item in review['regions'] if item['text'].startswith('Specification'))['status'] == 'conflict'
    assert next(item for item in review['regions'] if item['text'].startswith('Authorization'))['status'] != 'conflict'
    # A confirmation of a date already present still cannot authorize the other
    # old results and Pass wording in the paragraph.
    request.update(expected_revision=state['revision'], mapping_id=state['mappings'][0]['mapping_id'], value='2025-12-18')
    state = lab['client'].post(BASE + '/mappings', json=request).json()
    review = lab['client'].get(inspect_url, params={'expected_revision': state['revision']}).json()
    assert next(item for item in review['regions'] if item['text'].startswith('Specification'))['status'] == 'partially_verified'
    original_read = ReportAuthoringAssets.read
    missing_id = state['sources'][-1]['source_id']
    def unavailable(self, project_id, source):
        if source.source_id == missing_id:
            raise OSError('isolated unavailable source')
        return original_read(self, project_id, source)
    monkeypatch.setattr(ReportAuthoringAssets, 'read', unavailable)
    response = lab['client'].get(inspect_url, params={'expected_revision': state['revision']})
    assert response.status_code == 200, response.text
    region = next(item for item in response.json()['regions'] if item['text'].startswith('Specification'))
    assert region['status'] not in ('verified', 'partially_verified')
    assert any('missing or superseded' in reason for reason in region['reasons'])
