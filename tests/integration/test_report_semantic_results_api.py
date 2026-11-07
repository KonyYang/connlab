"""Measured and adopted evidence remains scoped to an explicitly selected report Step."""
from io import BytesIO

from tests.integration.test_report_authoring_api import lab, BASE
from tests.unit.test_report_tools_package import service, workbook_bytes


def qualitative_package():
    from openpyxl import Workbook
    from backend.infrastructure.files.mechanical_summary_folder import analyze_folder
    book = Workbook()
    for name, value in {'D8': 'Max', 'D9': '[N]', 'A13': '1', 'D13': '105.13'}.items():
        book.active[name] = value
    stream = BytesIO(); book.save(stream); book.close()
    files = [('DL-2026-05-001 polarisation.xlsx', stream.getvalue())]
    analysis = analyze_folder(files); section = analysis['sections'][0]
    table = {'title': 'Polarisation', 'row_heading': 'Receptacle', 'column_heading': 'Header',
        'columns': ['SN1'], 'samples': ['SN1'], 'results': [['Pass']], 'diagonal': True, 'curves': ['1']}
    review = {'project': analysis['project'], 'sections': {section['id']: {'tables': [table], 'qualitative_confirmed': True}}}
    package = service(); package.mechanical_renderer = workbook_bytes
    return package.export_mechanical(files, review)


def test_qualitative_package_confirms_observations_without_importing_report_pass(lab):
    name, content = qualitative_package()
    uploaded = lab['client'].post(BASE + '/sources', data={'role': 'tools_result_package', 'expected_revision': 0},
        files={'file': (name, content)})
    assert uploaded.status_code == 200, uploaded.text
    state = uploaded.json(); source = state['sources'][-1]
    overview = lab['client'].get(BASE + '/sources/' + source['source_id'] + '/package').json()
    entry = overview['entries'][0]
    assert entry['supported_for_report'] is True
    step = state['context']['steps'][0]
    request = {'expected_revision': state['revision'], 'source_id': source['source_id'], 'kind': 'mechanical_qualitative',
        'package_entry_id': entry['entry_id'], **{key: step[key] for key in ('group_id', 'row_id', 'step_token')}}
    preview = lab['client'].post(BASE + '/results/preview', json=request)
    assert preview.status_code == 200, preview.text
    assert preview.json()['data']['tables'][0]['results'] == [['Pass']]
    assert preview.json()['outcome'] == 'pending'
    assert 'summary' not in preview.json()['data']
    confirmed = lab['client'].post(BASE + '/results/confirm', json={**request, 'preview_sha256': preview.json()['preview_sha256']})
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()['outputs'] == []
    assert lab['client'].get(source['download_url']).content == content


def test_electrical_cell_selection_supports_horizontal_samples_and_preserves_missing_breakdown(lab):
    from tests.integration.test_report_authoring_api import upload
    from openpyxl import Workbook
    workbook = Workbook(); workbook.active.title = 'Group B'
    workbook.active.append(['', 'SN1', 'SN2']); workbook.active.append(['P1/P2', 0.1, 0])
    buffer = BytesIO(); workbook.save(buffer); workbook.close(); original = buffer.getvalue()
    state = upload(lab, role='evidence', name='electrical.xlsx', content=original).json()
    step = state['context']['steps'][0]
    request = {'expected_revision': state['revision'], 'source_id': state['sources'][-1]['source_id'], 'kind': 'electrical',
        **{key: step[key] for key in ('group_id', 'row_id', 'step_token')},
        'semantic_selection': {'type': 'electrical', 'selection_confirmed': True, 'records': [
            {'measurement': 'dwv', 'stage': 'Final', 'unit': 'µA', 'voltage_v': '4000', 'duration_s': '60',
             'condition_locator': 'Test condition B14', 'cells': {'sample': sample, 'pair': 'A2', 'value': value}}
            for sample, value in [('B1', 'B2'), ('C1', 'C2')]]}}
    preview = lab['client'].post(BASE + '/results/preview', json=request)
    assert preview.status_code == 200, preview.text
    rows = preview.json()['data']['rows']
    assert [row['value'] for row in rows] == ['0.1', '0']
    assert all(row['breakdown'] == 'not_recorded' and row['missing'] for row in rows)
    rejected = lab['client'].post(BASE + '/results/preview', json={**request, 'outcome': 'pass', 'acceptance_reason': 'Legacy says pass'})
    assert rejected.status_code == 422 and 'Missing measurements' in rejected.text
    response = lab['client'].post(BASE + '/results/confirm', json={**request, 'preview_sha256': preview.json()['preview_sha256']})
    assert response.status_code == 200, response.text
    state = lab['client'].get(BASE).json()
    assert state['results'][0]['data']['rows'] == rows
    from docx import Document
    from tests.integration.test_report_authoring_api import docx_bytes
    document = Document(BytesIO(docx_bytes())); document.add_paragraph(f"Group {step['group_label']} Test Results")
    table = document.add_table(rows=2, cols=3)
    for cell, label in zip(table.rows[0].cells, ['Step', 'Result', 'Comment']): cell.text = label
    table.cell(1, 0).text = step['step_token']; buffer = BytesIO(); document.save(buffer)
    state = upload(lab, revision=state['revision'], content=buffer.getvalue()).json()
    state = lab['client'].post(BASE + '/base', json={'expected_revision': state['revision'], 'source_id': state['sources'][-1]['source_id']}).json()
    from tests.integration.test_report_batch_assembly_api import preview_batch
    response = preview_batch(lab, state)
    assert response.status_code == 200, response.text
    state = response.json(); plan = state['assembly_plan']
    assert plan['can_apply'] is True
    applied = lab['client'].post(BASE + '/assembly/apply', json={'expected_revision': state['revision'], 'plan_id': plan['plan_id'], 'preview_sha256': plan['preview_sha256']})
    assert applied.status_code == 200, applied.text
    output = applied.json()['outputs'][-1]
    document = Document(BytesIO(lab['client'].get(output['download_url']).content))
    assert '0.1 µA' in document.tables[0].cell(1, 1).text
    assert document.tables[0].cell(1, 2).text == ''
    assert lab['client'].get(state['sources'][0]['download_url']).content == original


def test_final_absolute_and_delta_remain_distinct_in_one_result(lab):
    from tests.integration.test_report_authoring_api import upload
    state = upload(lab, role='cr', name='stages.csv', content=b'SN,Initial,Final\nSN1,1.1,2.4\n').json()
    step = state['context']['steps'][0]
    request = {'expected_revision': state['revision'], 'source_id': state['sources'][-1]['source_id'], 'kind': 'resistance_stages',
        **{key: step[key] for key in ('group_id', 'row_id', 'step_token')}, 'semantic_selection': {
        'type': 'resistance_stages', 'selection_confirmed': True, 'records': [
            {'stage': 'Final', 'quantity': 'absolute', 'unit': 'mΩ', 'cells': {'sample': 'A2', 'value': 'C2'}},
            {'stage': 'Final', 'quantity': 'delta_from_absolute', 'unit': 'mΩ', 'cells': {'sample': 'A2', 'value': 'C2', 'baseline': 'B2'}}]}}
    preview = lab['client'].post(BASE + '/results/preview', json=request)
    assert preview.status_code == 200, preview.text
    rows = preview.json()['data']['rows']
    assert [(row['quantity'], row['value']) for row in rows] == [('absolute', '2.4'), ('delta', '1.3')]


def test_related_region_retains_exact_applicability_and_rejects_stale_adoption(lab):
    from tests.integration.test_report_authoring_api import upload
    from tests.unit.report_authoring.test_linked_region import linked_source
    raw = linked_source()
    response = upload(lab, role='evidence', name='source-temperature.docx', content=raw)
    assert response.status_code == 200, response.text
    state = response.json(); source = state['sources'][-1]; step = state['context']['steps'][0]
    inspection = lab['client'].get(BASE + '/sources/' + source['source_id'] + '/region')
    assert inspection.status_code == 200 and inspection.json()[1]['tables'] == 1
    request = {'expected_revision': state['revision'], 'source_id': source['source_id'], 'kind': 'linked_temperature',
        **{key: step[key] for key in ('group_id', 'row_id', 'step_token')},
        'linked_region': {'start': 0, 'end': 2, 'freeze_external_charts': True},
        'adoption': {'report_identity': 'DL-2026-09-032B', 'source_version': 'Rev A', 'source_locator': 'Table 1 and curve',
            'adopted_scope': 'Temperature evidence only', 'applicability_reason': 'Matching approved specimen and test setup',
            'adverse_observations': 'Review original limitation', 'confirmed': True, 'customer_reference_allowed': True}}
    preview = lab['client'].post(BASE + '/results/preview', json=request)
    assert preview.status_code == 200, preview.text
    assert preview.json()['data']['frozen_chart_count'] == 1
    assert preview.json()['outcome'] == 'pending'
    changed = {**request, 'adoption': {**request['adoption'], 'source_version': 'Rev B'}, 'preview_sha256': preview.json()['preview_sha256']}
    assert lab['client'].post(BASE + '/results/confirm', json=changed).status_code == 409
    confirmed = lab['client'].post(BASE + '/results/confirm', json={**request, 'preview_sha256': preview.json()['preview_sha256']})
    assert confirmed.status_code == 200, confirmed.text
    reopened = lab['client'].get(BASE).json()
    assert reopened['results'][0]['data']['adoption']['source_version'] == 'Rev A'
    assert lab['client'].get(source['download_url']).content == raw
