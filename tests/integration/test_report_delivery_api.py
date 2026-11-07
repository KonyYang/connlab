from tests.integration.test_report_authoring_api import lab, upload, BASE
from tests.integration.test_report_batch_assembly_api import prepared_results, preview_batch
from tests.integration.test_internal_report_generation_api import official_report


def ready_pair(lab, monkeypatch):
    from backend.api import dependencies as deps
    from backend.infrastructure.office.report_authoring.visual_preview import WordReportPreview
    from tests.integration.test_report_authoring_api import docx_bytes
    (lab['settings'].templates_dir/'E-4515 Customer Report.docx').write_bytes(docx_bytes())
    class Converter:
        def generate_customer_report(self, *, source_path, template_path, output_path):
            output_path.write_bytes(source_path.read_bytes())
    monkeypatch.setattr(deps, 'CustomerReportDocumentGateway', Converter)
    monkeypatch.setattr(WordReportPreview, 'render', lambda self, content, review: {
        'content': b'%PDF-isolated-boundary', 'page_count': 1, 'pages': [{'page': 1}],
        'affected_pages': [1], 'affected_pages_reason': 'Isolated Word boundary'})
    old, local = official_report(lab)
    state, _ = prepared_results(lab)
    preview = preview_batch(lab, state).json(); plan = preview['assembly_plan']
    response = lab['client'].post(BASE+'/assembly/apply', json={'expected_revision': preview['revision'],
        'plan_id': plan['plan_id'], 'preview_sha256': plan['preview_sha256']})
    assert response.status_code == 200, response.text
    state = response.json(); output = state['outputs'][-1]
    review = lab['client'].get(BASE+f"/outputs/{output['output_id']}/document-review", params={'expected_revision': state['revision']}).json()
    response = lab['client'].post(BASE+'/delivery/content-review', json={'expected_revision': state['revision'],
        'output_id': output['output_id'], 'output_sha256': output['artifact']['sha256'],
        'review_sha256': review['review_sha256'], 'confirmed_by': 'Isolated reviewer', 'notes': 'Checked this same-project retained content'})
    assert response.status_code == 200, response.text
    state = response.json()
    response = lab['client'].post(BASE+'/customer/generate', json={'expected_revision': state['revision'],
        'output_id': output['output_id'], 'output_sha256': output['artifact']['sha256']})
    assert response.status_code == 200, response.text
    state = response.json(); customer = state['customer_outputs'][-1]
    response = lab['client'].post(BASE+'/customer/check', json={'expected_revision': state['revision'],
        'output_id': customer['output_id'], 'output_sha256': customer['artifact']['sha256'],
        'disclosure_scope_confirmed': True, 'reviewed_by': 'QA', 'content_review_sha256': output['artifact']['sha256']})
    assert response.status_code == 200, response.text
    state = response.json()
    checked_parts = {}
    for issue in state['customer_outputs'][-1]['audit']['issues']:
        if issue.get('sha256') and issue['code'] in {'unreviewed_package_part', 'unreviewed_embedding', 'visual_review_required'}:
            downloaded = lab['client'].get(BASE+f"/customer/{customer['output_id']}/part", params={'part': issue['location']})
            assert downloaded.status_code == 200, downloaded.text
            from hashlib import sha256
            assert sha256(downloaded.content).hexdigest() == issue['sha256']
            checked_parts[issue['location']] = issue['sha256']
    response = lab['client'].post(BASE+'/customer/check', json={'expected_revision': state['revision'],
        'output_id': customer['output_id'], 'output_sha256': customer['artifact']['sha256'],
        'disclosure_scope_confirmed': True, 'reviewed_by': 'QA', 'content_review_sha256': output['artifact']['sha256'],
        'reviewed_parts': checked_parts})
    assert response.status_code == 200, response.text
    state = response.json()
    assert state['customer_outputs'][-1]['audit']['passed'], state['customer_outputs'][-1]['audit']['issues']
    for item in [output, customer]:
        identity = {'expected_revision': state['revision'], 'output_id': item['output_id'], 'output_sha256': item['artifact']['sha256']}
        response = lab['client'].post(BASE+'/visual-preview', json=identity)
        assert response.status_code == 200, response.text
        state = response.json()
        selected = next(entry for entry in [*state['outputs'], *state['customer_outputs']] if entry['output_id'] == item['output_id'])
        response = lab['client'].post(BASE+'/visual-preview/review', json={**identity, 'expected_revision': state['revision'],
            'preview_sha256': selected['visual_preview']['artifact']['sha256'], 'pages': [1], 'confirmed_by': 'QA', 'notes': 'Isolated Word boundary'})
        assert response.status_code == 200, response.text
        state = response.json()
    return state, old, local


def save_request(state, preview):
    return {'expected_revision': state['revision'], 'output_id': state['outputs'][-1]['output_id'],
        'output_sha256': state['outputs'][-1]['artifact']['sha256'],
        'customer_output_id': state['customer_outputs'][-1]['output_id'],
        'preview_sha256': preview['preview_sha256'], 'confirmed_by': 'Isolated QA'}


def test_exact_reviewed_pair_saves_bytes_with_history_and_replay_never_regenerates(lab, monkeypatch):
    state, old, local = ready_pair(lab, monkeypatch)
    old_bytes = old.read_bytes()
    expected = lab['client'].get(state['outputs'][-1]['download_url']).content
    response = lab['client'].get(BASE+'/delivery')
    assert response.status_code == 200, response.text
    preview = response.json()
    assert preview['can_save'], preview['issues']
    request = save_request(state, preview)
    response = lab['client'].post(BASE+'/delivery/save', json=request)
    assert response.status_code == 200, response.text
    final = response.json()
    assert final['delivery']['status'] == 'completed'
    assert final['delivery']['formal_release'] is False
    assert old.read_bytes() == expected
    assert [p.read_bytes() for p in (local/'History'/'Report').glob('*.docx')] == [old_bytes]
    assert 'approved_intent' not in final['delivery']
    repeated = lab['client'].post(BASE+'/delivery/resume', json={'operation_id': final['delivery']['operation_id']})
    assert repeated.status_code == 200, repeated.text
    assert repeated.json() == final
    assert lab['client'].post(BASE+'/delivery/save', json=request).json() == final
    assert len(list((local/'History'/'Report').glob('*.docx'))) == 1


def test_customer_failure_retains_saved_internal_and_resume_only_finishes_customer(lab, monkeypatch):
    from backend.infrastructure.files.report_publication_gateway import ReportPublicationGateway
    state, old, local = ready_pair(lab, monkeypatch)
    preview = lab['client'].get(BASE+'/delivery').json()
    original_publish = ReportPublicationGateway.publish_regenerated_current
    def occupied(self, **values):
        if values.get('receipt') and values['receipt'].role == 'customer':
            raise PermissionError('isolated customer is open in Word')
        return original_publish(self, **values)
    monkeypatch.setattr(ReportPublicationGateway, 'publish_regenerated_current', occupied)
    failed = lab['client'].post(BASE+'/delivery/save', json=save_request(state, preview))
    assert failed.status_code == 409, failed.text
    saved_bytes, saved_time = old.read_bytes(), old.stat().st_mtime_ns
    pending = lab['client'].get(BASE+'/delivery').json()['operation']
    assert pending['status'] == 'saving'
    assert pending['items'][0]['status'] == 'committed'
    assert pending['items'][1]['status'] == 'planned'
    monkeypatch.setattr(ReportPublicationGateway, 'publish_regenerated_current', original_publish)
    resumed = lab['client'].post(BASE+'/delivery/resume', json={'operation_id': pending['operation_id']})
    assert resumed.status_code == 200, resumed.text
    assert resumed.json()['delivery']['status'] == 'completed'
    assert old.read_bytes() == saved_bytes and old.stat().st_mtime_ns == saved_time
    assert len(list((local/'History'/'Report').glob('*.docx'))) == 1


def test_same_bytes_replaced_target_identity_is_not_silently_accepted(lab, monkeypatch):
    from pathlib import Path
    state, old, local = ready_pair(lab, monkeypatch)
    preview = lab['client'].get(BASE+'/delivery').json()
    data = old.read_bytes()
    separate = old.with_suffix('.other'); separate.write_bytes(data)
    separate.replace(old)
    failed = lab['client'].post(BASE+'/delivery/save', json=save_request(state, preview))
    assert failed.status_code == 409, failed.text
    assert old.read_bytes() == data
    assert not list((local/'History'/'Report').glob('*.docx'))


def test_missing_receipt_after_durable_approval_resumes_without_new_authorization(lab, monkeypatch):
    from backend.infrastructure.files.report_delivery_receipt import ReportDeliveryReceipts
    state, old, local = ready_pair(lab, monkeypatch)
    old_bytes = old.read_bytes()
    preview = lab['client'].get(BASE+'/delivery').json()
    original_begin = ReportDeliveryReceipts.begin
    def unavailable(*args, **kwargs):
        raise OSError('isolated receipt disk unavailable')
    monkeypatch.setattr(ReportDeliveryReceipts, 'begin', unavailable)
    failed = lab['client'].post(BASE+'/delivery/save', json=save_request(state, preview))
    assert failed.status_code == 503, failed.text
    pending = lab['client'].get(BASE).json()
    assert pending['delivery']['status'] == 'saving'
    assert old.read_bytes() == old_bytes
    assert not list((local/'History'/'Report').glob('*.docx'))
    blocked = lab['client'].post(BASE+'/customer/generate', json={'expected_revision': pending['revision'],
        'output_id': state['outputs'][-1]['output_id'], 'output_sha256': state['outputs'][-1]['artifact']['sha256']})
    assert blocked.status_code == 409
    monkeypatch.setattr(ReportDeliveryReceipts, 'begin', original_begin)
    resumed = lab['client'].post(BASE+'/delivery/resume', json={'operation_id': pending['delivery']['operation_id']})
    assert resumed.status_code == 200, resumed.text
    assert resumed.json()['delivery']['status'] == 'completed'
    assert len(list((local/'History'/'Report').glob('*.docx'))) == 1


def test_customer_visual_role_does_not_allow_internal_region_decisions(lab, monkeypatch):
    state, _, _ = ready_pair(lab, monkeypatch)
    customer = state['customer_outputs'][-1]
    identity = {'expected_revision': state['revision'], 'output_id': customer['output_id'], 'output_sha256': customer['artifact']['sha256']}
    bad = lab['client'].post(BASE+'/delivery/content-review', json={**identity,
        'review_sha256': '0'*64, 'confirmed_by': 'QA', 'notes': 'Cannot review customer as original'})
    assert bad.status_code == 422
    bad = lab['client'].post(BASE+'/document-review/regions', json={**identity,
        'review_sha256': '0'*64, 'confirmed_by': 'QA', 'decisions': [{'region_id': 'x', 'region_sha256': '0'*64,
            'source_id': state['sources'][0]['source_id'], 'locator': 'x', 'reason': 'No role confusion'}]})
    assert bad.status_code == 422


def test_valid_save_shape_cannot_bypass_missing_review_or_changed_source(lab, monkeypatch):
    state, old, local = ready_pair(lab, monkeypatch)
    ready = lab['client'].get(BASE+'/delivery').json()
    assert ready['can_save'], ready['issues']
    request = save_request(state, ready)
    old_bytes = old.read_bytes()
    from backend.infrastructure.files.report_authoring_assets import ReportAuthoringAssets
    from backend.domain.report_authoring import ReportSource
    source = state['sources'][-1]
    path = ReportAuthoringAssets(lab['settings'].data_dir/'report_authoring_assets').path('P1', ReportSource(**{
        key: value for key, value in source.items() if key != 'download_url'}))
    path.unlink()  # Isolated consumed input disappears after the reviewed preview.
    failed = lab['client'].post(BASE+'/delivery/save', json=request)
    assert failed.status_code in {409, 422}
    assert old.read_bytes() == old_bytes
    assert not list((local/'History'/'Report').glob('*.docx'))


def test_delivery_reports_missing_copy_and_cannot_accept_a_client_pass(lab):
    response = lab['client'].get(BASE + '/delivery')
    assert response.status_code == 200, response.text
    assert not response.json()['can_save']
    assert any('working copy' in issue['message'].lower() for issue in response.json()['issues'])
    state = upload(lab).json()
    state = lab['client'].post(BASE+'/base', json={'expected_revision': state['revision'],
        'source_id': state['sources'][0]['source_id']}).json()
    before = state
    response = lab['client'].post(BASE+'/delivery/preview', json={
        'expected_revision': state['revision'], 'output_id': state['outputs'][-1]['output_id'],
        'output_sha256': state['outputs'][-1]['artifact']['sha256'], 'customer_output_id': None})
    assert response.status_code == 200, response.text
    assert not response.json()['can_save']
    assert any(item['code'] == 'coverage_incomplete' for item in response.json()['issues'])
    rejected = lab['client'].post(BASE+'/delivery/save', json={
        'expected_revision': state['revision'], 'preview_sha256': response.json()['preview_sha256'],
        'confirmed_by': 'QA', 'passed': True})
    assert rejected.status_code == 422
    assert lab['client'].get(BASE).json() == before
