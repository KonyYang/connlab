"""All selected-copy edits share one durable lineage, never the official file."""
from hashlib import sha256
from io import BytesIO
from types import SimpleNamespace
import shutil

from docx import Document

from backend.api import dependencies as deps
from tests.integration.test_report_section_draft_api import section_lab, lab
from tests.integration.test_internal_report_generation_api import official_report
from tests.integration.test_report_authoring_api import docx_bytes


BASE = '/api/projects/P1/report-workspace/authoring'
SOURCE = '/api/projects/P1/report-workspace/update-source'


def adopt(lab):
    source = lab['client'].get(SOURCE).json()
    response = lab['client'].post(BASE + '/working-copy/adopt', json={
        'expected_revision': 0, 'source_sha256': source['file_sha256'],
        'source_mode': source['mode']})
    assert response.status_code == 200, response.text
    return response.json()


def test_adopt_official_then_llcr_updates_only_selected_copy_and_survives_reload(section_lab):
    lab = section_lab
    official, local = official_report(lab)
    official.write_bytes(docx_bytes())
    before = official.read_bytes()
    state = adopt(lab)
    first = state['outputs'][-1]
    updated = lab['client'].post(BASE + '/working-copy/llcr', json={
        'expected_revision': state['revision'], 'expected_sha256': first['artifact']['sha256'],
        'dataset_revision_id': 'dataset-1'})
    assert updated.status_code == 200, updated.text
    state = updated.json()
    output = state['outputs'][-1]
    assert output['parent_output_id'] == first['output_id']
    document = Document(BytesIO(lab['client'].get(output['download_url']).content))
    assert 'Confirmed LLCR results' in [p.text for p in document.paragraphs]
    assert lab['client'].get(BASE).json()['outputs'][-1] == output
    assert official.read_bytes() == before
    assert not (local / 'History').exists()
    assert lab['client'].get(SOURCE).json()['file_sha256'] == sha256(before).hexdigest()
    assert lab['client'].get(first['download_url']).status_code == 200


def test_stale_working_copy_and_changed_adoption_source_do_not_advance(section_lab):
    lab = section_lab
    source = lab['client'].get(SOURCE).json()
    response = lab['client'].post(BASE + '/working-copy/adopt', json={
        'expected_revision': 0, 'source_sha256': '0' * 64, 'source_mode': source['mode']})
    assert response.status_code == 409
    assert lab['client'].get(BASE).json()['revision'] == 0
    state = adopt(lab)
    before = lab['original'].read_bytes()
    response = lab['client'].post(BASE + '/working-copy/llcr', json={
        'expected_revision': state['revision'], 'expected_sha256': '0' * 64,
        'dataset_revision_id': 'dataset-1'})
    assert response.status_code == 409
    assert lab['client'].get(BASE).json() == state
    assert lab['original'].read_bytes() == before


def test_equipment_chains_after_llcr_without_switching_source(section_lab, monkeypatch):
    lab = section_lab
    catalog = lab['root'] / 'catalog.xls'
    catalog.write_bytes(b'isolated calibration boundary')
    reader = SimpleNamespace(read_equipment_calibrations=lambda: SimpleNamespace(resource_path=catalog, rows=(
        SimpleNamespace(equipment_id='DG-Q-0033', equipment_name='Meter', manufacturer='Maker',
            last_calibration_date='2026-01-01', calibration_due_date='2027-01-01', source_sheet='All'),)))
    monkeypatch.setattr(deps, 'ExternalExcelReadService', lambda resources: reader)
    def update(*, source_path, output_path, rows):
        document = Document(source_path)
        document.add_paragraph('Equipment: ' + rows[0].id_number)
        document.save(output_path)
        return output_path
    monkeypatch.setattr(lab['writer'], 'synchronize_equipment_list', update, raising=False)
    state = adopt(lab)
    before = lab['original'].read_bytes()
    state = lab['client'].post(BASE + '/working-copy/llcr', json={
        'expected_revision': state['revision'], 'expected_sha256': state['outputs'][-1]['artifact']['sha256'],
        'dataset_revision_id': 'dataset-1'}).json()
    first = state['outputs'][-1]
    data = {'expected_revision': state['revision'], 'expected_sha256': first['artifact']['sha256']}
    missing = lab['client'].post(BASE + '/working-copy/equipment', data=data)
    assert missing.status_code == 200, missing.text
    assert missing.json()['status'] == 'source_required'
    assert lab['client'].get(BASE).json()['revision'] == state['revision']
    result = lab['client'].post(BASE + '/working-copy/equipment', data={**data, 'references_text': 'DG-Q-0033'})
    assert result.status_code == 200, result.text
    output = result.json()['outputs'][-1]
    assert output['parent_output_id'] == first['output_id']
    text = '\n'.join(p.text for p in Document(BytesIO(lab['client'].get(output['download_url']).content)).paragraphs)
    assert 'Confirmed LLCR results' in text and 'Equipment: DG-Q-0033' in text
    assert lab['original'].read_bytes() == before
    assert lab['client'].get(SOURCE).json()['file_sha256'] == sha256(before).hexdigest()


def test_unchanged_equipment_rows_still_retain_the_new_selection(section_lab, monkeypatch):
    lab = section_lab
    monkeypatch.setattr(deps, 'get_tools_equipment_report_service', lambda session: SimpleNamespace(
        update=lambda **values: (shutil.copy2(values['source_path'], values['output_path']) and
            SimpleNamespace(statistics={'filled': 1, 'unmatched': [], 'incomplete': [], 'expired': []}))))
    state = adopt(lab)
    before = state['outputs'][-1]['artifact']['sha256']
    response = lab['client'].post(BASE + '/working-copy/equipment', data={
        'expected_revision': state['revision'], 'expected_sha256': before, 'references_text': 'DG-Q-0033'})
    assert response.status_code == 200, response.text
    current = lab['client'].get(BASE).json()
    assert current['outputs'][-1]['evidence']['references_text'] == 'DG-Q-0033'
    assert current['outputs'][-1]['artifact']['sha256'] == before
    again = lab['client'].post(BASE + '/working-copy/equipment', data={
        'expected_revision': current['revision'], 'expected_sha256': before})
    assert again.status_code == 200, again.text
    assert again.json() == current
