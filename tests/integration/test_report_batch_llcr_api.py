"""Existing confirmed LLCR datasets join the reviewed batch without being copied or recalculated."""
from dataclasses import replace
from io import BytesIO

from docx import Document
import pytest

from backend.infrastructure.storage.repositories import ConfirmedMatrixAuthorityRepository
from backend.infrastructure.storage.repositories.result_dataset import ResultDatasetRepository
from backend.infrastructure.office.test_report_document_gateway import TestReportDocumentGateway as WordGateway
from tests.integration.test_internal_report_generation_api import lab
from tests.integration.test_report_authoring_api import BASE, upload
from tests.integration.test_report_preparation_coverage import confirm_cr
from tests.unit.test_result_dataset_repository import _dataset


def seed_llcr(lab, *, revision=1, outcome='pass'):
    step = lab['client'].get(BASE).json()['context']['steps'][0]
    dataset = _dataset(f'llcr-{revision}', revision)
    entry = replace(dataset.payload.entries[0], confirmed_group_id=step['group_id'],
        confirmed_row_id=step['row_id'], group_label=step['group_label'],
        matrix_step_token=step['step_token'], matrix_step_sequence=int(step['step_token']),
        provisional_outcome=outcome, confirmed_outcome=outcome)
    with lab['factory']() as session:
        matrix = ConfirmedMatrixAuthorityRepository(session).get_active_by_project('P1')
        dataset = replace(dataset, confirmed_matrix_id=matrix.version.confirmed_matrix_id,
            confirmed_matrix_revision=matrix.version.confirmed_revision,
            payload=replace(dataset.payload, entries=(entry,), summary_rows=()))
        ResultDatasetRepository(session).create_dataset(dataset)
        session.commit()
    return dataset


def test_current_llcr_is_visible_as_read_only_coverage_not_a_second_result_record(lab):
    dataset = seed_llcr(lab)
    response = lab['client'].get(BASE + '/coverage')
    assert response.status_code == 200, response.text
    coverage = response.json()
    assert coverage['llcr_dataset']['dataset_id'] == dataset.dataset_id
    entry = coverage['llcr_dataset']['entries'][0]
    assert entry['summary'] == {'min': '0.198', 'max': '0.198', 'average': '0.198', 'unit': 'mΩ'}
    assert entry['stage_label'] == 'Initial LLCR'
    assert coverage['rows'][0]['status'] == 'ready'
    assert coverage['rows'][0]['applied_result_ids'] == []
    assert coverage['complete'] is False
    assert lab['client'].get(BASE).json()['results'] == []
    with lab['factory']() as session:
        assert ResultDatasetRepository(session).get_dataset(dataset.dataset_id) == dataset


def prepared_llcr_and_cr(lab, *, outcome='pass'):
    dataset = seed_llcr(lab, outcome=outcome)
    context = lab['client'].get(BASE).json()['context']
    document = Document()
    document.sections[0].header.paragraphs[0].text = 'DL-2026-05-001'
    document.sections[0].footer.paragraphs[0].text = 'E-3707'
    document.add_paragraph('Approved wording stays unchanged')
    for index, step in enumerate(context['steps']):
        document.add_paragraph(f"Group {step['group_label']} Test Results")
        table = document.add_table(rows=2, cols=6)
        for cell, value in zip(table.rows[0].cells, ['Step', 'Test', 'Requirement', 'Step Description', 'Result', 'Comment']):
            cell.text = value
        table.cell(1, 0).text = step['step_token']
        table.cell(1, 1).text = 'Contact Resistance (Low Level)' if index == 0 else step['test_item']
        table.cell(1, 2).text = dataset.payload.entries[0].requirement if index == 0 else 'Approved CR requirement'
    document.add_paragraph('*** End of Report ***')
    stream = BytesIO()
    document.save(stream)
    original = stream.getvalue()
    state = upload(lab, content=original).json()
    response = lab['client'].post(BASE + '/base', json={
        'expected_revision': state['revision'], 'source_id': state['sources'][0]['source_id']})
    assert response.status_code == 200, response.text
    state = upload(lab, revision=response.json()['revision'], role='cr', name='CR.csv',
                   content=b'SN,V,I\nSN1,50,100\n').json()
    return confirm_cr(lab, state, step_index=1, outcome='pass'), dataset, original


def preview(lab, state, dataset_id):
    output = state['outputs'][-1]
    return lab['client'].post(BASE + '/assembly/preview', json={
        'expected_revision': state['revision'], 'output_id': output['output_id'],
        'output_sha256': output['artifact']['sha256'], 'llcr_dataset_id': dataset_id,
        'results': [{'result_id': result['result_id']} for result in state['results']]})


def apply(lab, state):
    plan = state['assembly_plan']
    return lab['client'].post(BASE + '/assembly/apply', json={
        'expected_revision': state['revision'], 'plan_id': plan['plan_id'],
        'preview_sha256': plan['preview_sha256']})


@pytest.mark.parametrize('outcome,complete', [('pass', True), ('not_determined', False)])
def test_llcr_and_cr_share_one_preview_one_copy_without_recalculating_or_claiming_pending_complete(lab, outcome, complete):
    initial, dataset, original = prepared_llcr_and_cr(lab, outcome=outcome)
    response = preview(lab, initial, dataset.dataset_id)
    assert response.status_code == 200, response.text
    state = response.json()
    plan = state['assembly_plan']
    assert plan['can_apply'] is True, plan['issues']
    assert plan['document_plan']['llcr']['dataset_id'] == dataset.dataset_id
    assert plan['omitted'] == []
    assert bool(plan['issues']) is (outcome == 'not_determined')
    applied = apply(lab, state)
    assert applied.status_code == 200, applied.text
    final = applied.json()
    assert len(final['outputs']) == 2
    assert len(final['results']) == 1
    output = final['outputs'][-1]
    assert output['evidence']['llcr_dataset_id'] == dataset.dataset_id
    content = lab['client'].get(output['download_url']).content
    doc = Document(BytesIO(content))
    assert '0.198' in doc.tables[0].cell(1, 4).text
    assert '0.5' in doc.tables[1].cell(1, 4).text
    assert any('Appendix A' in p.text for p in doc.paragraphs)
    assert doc.paragraphs[0].text == 'Approved wording stays unchanged'
    assert lab['client'].get(initial['sources'][0]['download_url']).content == original
    assert lab['client'].get(BASE + '/coverage').json()['complete'] is complete
    assert apply(lab, state).json() == final
    with lab['factory']() as session:
        assert ResultDatasetRepository(session).get_dataset(dataset.dataset_id) == dataset


def test_new_llcr_revision_invalidates_old_plan_but_never_silently_substitutes_selection(lab):
    initial, dataset, _ = prepared_llcr_and_cr(lab)
    response = preview(lab, initial, dataset.dataset_id)
    assert response.status_code == 200, response.text
    state = response.json()
    newest = seed_llcr(lab, revision=2)
    reopened = lab['client'].get(BASE).json()
    assert reopened['assembly_plan']['can_apply'] is False
    assert reopened['assembly_plan']['request']['llcr_dataset_id'] == dataset.dataset_id
    assert lab['client'].get(BASE + '/coverage').json()['llcr_dataset']['dataset_id'] == newest.dataset_id
    assert apply(lab, state).status_code == 409
    assert preview(lab, reopened, dataset.dataset_id).status_code == 409
    assert lab['client'].get(BASE).json()['outputs'] == initial['outputs']


def test_existing_single_llcr_update_counts_as_applied_but_new_dataset_cannot_borrow_it(lab, monkeypatch):
    initial, dataset, _ = prepared_llcr_and_cr(lab)
    monkeypatch.setattr(lab['writer'], 'synchronize_llcr_results',
                        WordGateway().synchronize_llcr_results, raising=False)
    response = lab['client'].post(BASE + '/working-copy/llcr', json={
        'expected_revision': initial['revision'], 'dataset_revision_id': dataset.dataset_id,
        'expected_sha256': initial['outputs'][-1]['artifact']['sha256']})
    assert response.status_code == 200, response.text
    coverage = lab['client'].get(BASE + '/coverage').json()
    assert coverage['rows'][0]['applied_result_ids'] == coverage['rows'][0]['usable_result_ids']
    assert coverage['rows'][0]['applied_result_ids']
    seed_llcr(lab, revision=2)
    current = lab['client'].get(BASE + '/coverage').json()
    assert current['rows'][0]['applied_result_ids'] == []
    assert current['complete'] is False
    # The legacy single-update route keeps its existing historical-dataset meaning.
    state = response.json()
    repeated = lab['client'].post(BASE + '/working-copy/llcr', json={
        'expected_revision': state['revision'], 'dataset_revision_id': dataset.dataset_id,
        'expected_sha256': state['outputs'][-1]['artifact']['sha256']})
    assert repeated.status_code == 200, repeated.text


def test_llcr_only_batch_keeps_unselected_cr_omitted_and_matrix_change_invalidates_plan(lab):
    from backend.infrastructure.storage.models_confirmed_matrix_authority import ConfirmedMatrixVersionModel

    initial, dataset, _ = prepared_llcr_and_cr(lab)
    output = initial['outputs'][-1]
    response = lab['client'].post(BASE + '/assembly/preview', json={
        'expected_revision': initial['revision'], 'output_id': output['output_id'],
        'output_sha256': output['artifact']['sha256'], 'llcr_dataset_id': dataset.dataset_id})
    assert response.status_code == 200, response.text
    state = response.json()
    assert state['assembly_plan']['can_apply'] is True
    assert len(state['assembly_plan']['omitted']) == 1
    with lab['factory']() as session:
        session.get(ConfirmedMatrixVersionModel, dataset.confirmed_matrix_id).confirmed_revision += 1
        session.commit()
    coverage = lab['client'].get(BASE + '/coverage').json()
    assert coverage['llcr_dataset'] is None
    assert 'stale' in coverage['llcr_unavailable_reason'].lower()
    assert lab['client'].get(BASE).json()['assembly_plan']['can_apply'] is False
    assert apply(lab, state).status_code == 409
    assert lab['client'].get(BASE).json()['outputs'] == initial['outputs']


def test_dataset_changed_during_generation_does_not_publish_the_generated_copy(lab, monkeypatch):
    from backend.infrastructure.office.report_authoring.batch_document import ReportBatchDocument

    initial, dataset, original = prepared_llcr_and_cr(lab)
    response = preview(lab, initial, dataset.dataset_id)
    assert response.status_code == 200, response.text
    state = response.json()
    update = ReportBatchDocument.update

    def changed_after_write(self, *args, **kwargs):
        result = update(self, *args, **kwargs)
        seed_llcr(lab, revision=2)
        return result

    monkeypatch.setattr(ReportBatchDocument, 'update', changed_after_write)
    response = apply(lab, state)
    assert response.status_code == 409, response.text
    assert lab['client'].get(BASE).json()['outputs'] == initial['outputs']
    assert lab['client'].get(initial['sources'][0]['download_url']).content == original


def customer_check(lab, state, monkeypatch):
    from backend.api import dependencies
    from tests.integration.test_report_authoring_api import docx_bytes

    (lab['settings'].templates_dir / 'E-4515 Customer Report.docx').write_bytes(docx_bytes())

    class Converter:
        def generate_customer_report(self, *, source_path, template_path, output_path):
            output_path.write_bytes(source_path.read_bytes())

    monkeypatch.setattr(dependencies, 'CustomerReportDocumentGateway', Converter)
    internal = state['outputs'][-1]
    generated = lab['client'].post(BASE + '/customer/generate', json={
        'expected_revision': state['revision'], 'output_id': internal['output_id'],
        'output_sha256': internal['artifact']['sha256']})
    assert generated.status_code == 200, generated.text
    state = generated.json()
    customer = state['customer_outputs'][-1]
    request = {'expected_revision': state['revision'], 'output_id': customer['output_id'],
        'output_sha256': customer['artifact']['sha256'], 'disclosure_scope_confirmed': True,
        'content_review_sha256': internal['artifact']['sha256']}
    first = lab['client'].post(BASE + '/customer/check', json=request)
    assert first.status_code == 200, first.text
    checked = first.json()
    request.update(expected_revision=checked['revision'], reviewed_parts={
        item['location']: item['sha256'] for item in checked['customer_outputs'][-1]['audit']['issues']
        if item['code'] == 'unreviewed_package_part'})
    second = lab['client'].post(BASE + '/customer/check', json=request)
    assert second.status_code == 200, second.text
    return second.json(), request


def test_new_llcr_authority_invalidates_customer_audit_and_recheck_cannot_bypass_stale_result(lab, monkeypatch):
    initial, dataset, _ = prepared_llcr_and_cr(lab)
    prepared = preview(lab, initial, dataset.dataset_id).json()
    completed = apply(lab, prepared).json()
    checked, request = customer_check(lab, completed, monkeypatch)
    assert checked['customer_outputs'][-1]['audit']['passed'] is True
    seed_llcr(lab, revision=2)
    reopened = lab['client'].get(BASE).json()
    assert reopened['customer_outputs'][-1]['status'] == 'needs_review'
    assert reopened['customer_outputs'][-1]['audit']['passed'] is False
    checked = lab['client'].post(BASE + '/customer/check', json={**request, 'expected_revision': reopened['revision']})
    assert checked.status_code == 200, checked.text
    audit = checked.json()['customer_outputs'][-1]['audit']
    assert audit['passed'] is False
    assert any(issue['code'] == 'stale_llcr_result' for issue in audit['issues'])


def test_customer_check_cannot_treat_applied_not_determined_llcr_as_pass(lab, monkeypatch):
    initial, dataset, _ = prepared_llcr_and_cr(lab, outcome='not_determined')
    completed = apply(lab, preview(lab, initial, dataset.dataset_id).json()).json()
    checked, _ = customer_check(lab, completed, monkeypatch)
    audit = checked['customer_outputs'][-1]['audit']
    assert audit['passed'] is False
    assert any(issue['code'] == 'pending_llcr_decision' for issue in audit['issues'])


def test_same_dataset_id_with_changed_payload_cannot_inherit_applied_coverage(lab):
    import json
    from backend.infrastructure.storage.models_result_dataset import ResultDatasetRevisionModel

    initial, dataset, _ = prepared_llcr_and_cr(lab)
    completed = apply(lab, preview(lab, initial, dataset.dataset_id).json())
    assert completed.status_code == 200, completed.text
    assert lab['client'].get(BASE + '/coverage').json()['complete'] is True
    # Simulate an out-of-band change only in the isolated DB: repository API is
    # append-only, but SQLite itself does not prohibit rewriting payload bytes.
    with lab['factory']() as session:
        row = session.get(ResultDatasetRevisionModel, dataset.dataset_id)
        payload = json.loads(row.payload_json)
        payload['entries'][0]['summary_max'] = '0.199'
        row.payload_json = json.dumps(payload)
        session.commit()
    coverage = lab['client'].get(BASE + '/coverage').json()
    assert coverage['llcr_dataset']['dataset_id'] == dataset.dataset_id
    assert coverage['llcr_dataset']['entries'][0]['summary']['max'] == '0.199'
    assert coverage['rows'][0]['applied_result_ids'] == []
    assert coverage['complete'] is False
    assert lab['client'].get(BASE).json()['outputs'] == completed.json()['outputs']


def test_explicit_same_content_new_llcr_revision_records_identity_once_on_legacy_update(lab, monkeypatch):
    initial, dataset, _ = prepared_llcr_and_cr(lab)
    completed = apply(lab, preview(lab, initial, dataset.dataset_id).json()).json()
    before = completed['outputs'][-1]
    newest = seed_llcr(lab, revision=2)
    monkeypatch.setattr(lab['writer'], 'synchronize_llcr_results',
                        WordGateway().synchronize_llcr_results, raising=False)
    request = {'expected_revision': completed['revision'], 'dataset_revision_id': newest.dataset_id,
               'expected_sha256': before['artifact']['sha256']}
    updated = lab['client'].post(BASE + '/working-copy/llcr', json=request)
    assert updated.status_code == 200, updated.text
    state = updated.json()
    assert len(state['outputs']) == len(completed['outputs']) + 1
    assert state['outputs'][-1]['artifact']['sha256'] == before['artifact']['sha256']
    assert state['outputs'][-1]['evidence']['dataset_revision_id'] == newest.dataset_id
    assert lab['client'].get(BASE + '/coverage').json()['complete'] is True
    repeated = lab['client'].post(BASE + '/working-copy/llcr', json={**request, 'expected_revision': state['revision']})
    assert repeated.status_code == 200, repeated.text
    assert repeated.json() == state
