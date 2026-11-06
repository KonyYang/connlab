from copy import deepcopy
from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile

import pytest
from docx import Document
from PIL import Image

from backend.infrastructure.office.report_authoring.batch_document import ReportBatchDocument


def picture(color):
    image = BytesIO()
    Image.new('RGB', (40, 20), color).save(image, 'PNG')
    return image.getvalue()


def mechanical(identity='force', group='B', step='2'):
    return {'result_id': identity, 'kind': 'mechanical',
        'target': {'group_label': group, 'step_token': step}, 'outcome': 'pending',
        'data': {'test_type': 'retention', 'quantity': 'hold', 'unit': 'N',
            'rows': [{'sample_id': 'SN1', 'record_id': 'r1', 'color': 'Orange', 'value': '410', 'hold_seconds': '6'}],
            'summary': {'min': '410', 'max': '410', 'average': '410', 'stdev': '0'}}}


def report(path):
    document = Document()
    document.add_paragraph('Original product').runs[0].bold = True
    document.sections[0].header.paragraphs[0].text = 'Original product header'
    for group in ('A', 'B'):
        document.add_paragraph(f'Group {group} Test Results')
        table = document.add_table(rows=2, cols=4)
        for cell, label in zip(table.rows[0].cells, ['Step', 'Test Item', 'Result', 'Comment']):
            cell.text = label
        for cell, label in zip(table.rows[1].cells, ['2', 'Retention Force', 'Old value', 'Pass']):
            cell.text = label
        if group == 'A':
            document.add_paragraph('Table-1: Temperature Rise Measurements')
            old = document.add_table(rows=1, cols=2)
            old.cell(0, 0).text = 'Applied current'
            old.cell(0, 1).text = 'OLD TEMPERATURE'
            document.add_picture(BytesIO(picture('red')))
            document.add_paragraph('The maximum rise reached 99°C.')
    document.add_picture(BytesIO(picture('blue')))
    document.add_paragraph('KEEP PHOTO CAPTION')
    document.add_paragraph('Appendix B: old force')
    document.add_table(rows=1, cols=2).cell(0, 0).text = 'OLD FORCE'
    document.add_paragraph('*** End of Report ***')
    document.save(path)


def temperature():
    from dataclasses import asdict
    from backend.application.tools_temperature_service import ToolsTemperatureService
    from backend.domain.temperature_data import DataSelection
    from backend.infrastructure.office.temperature_workbook_gateway import TemperatureWorkbookGateway
    workbook = TemperatureWorkbookGateway()
    data = workbook.read_upload(b'Ambient,I,T1\n20,100,26\n20,100,26\n20,200,45\n20,200,45\n', 'data.csv')
    selection = DataSelection(header_row=1, start_row=2, end_row=5, ambient_column=1, current_column=2,
        temperature_columns=(3,), thermocouples_per_sample=1, sample_count=1)
    analysis = ToolsTemperatureService(workbook).analyze(data, selection, zero_intercept=True)
    return {'result_id': 'temperature', 'kind': 'temperature', 'target': {'group_label': 'A', 'step_token': '2'},
        'outcome': 'pending', 'data': {'analysis': asdict(analysis),
            'selection': {'ambient_column': 1, 'temperature_columns': [3]},
            'raw_rows': [{'source_row': index + 1, 'values': list(row)} for index, row in enumerate(data.rows)]}}


def batch_input(source):
    from backend.infrastructure.office.report_authoring.results_document import ReportResultsDocument
    candidate = ReportResultsDocument().inspect(source, temperature())
    blocks = candidate['evidence_blocks']
    start = next(item['block_index'] for item in blocks if item['text'].startswith('Table-1'))
    end = next(item['block_index'] for item in blocks if '99°C' in item['text'])
    return {'fact_replacements': [('Original product', 'Current product')],
        'results': [
            {'result': temperature(), 'target': {'result_table': 0, 'result_row': 1,
                'appendix_table': None, 'appendix_title': '', 'evidence_start': start, 'evidence_end': end}},
            {'result': mechanical(), 'target': {'result_table': 2, 'result_row': 1,
                'appendix_table': 3, 'appendix_title': 'Appendix B'}}],
        'photos': [{'slot_id': 'photo-2', 'content': picture('green')}]}


def test_batch_freezes_original_table_block_and_photo_locations_and_preserves_source(tmp_path):
    from backend.infrastructure.office.report_authoring.temperature_chart import insert_temperature_chart
    from backend.infrastructure.office.report_authoring.photo_slots import read_photo_slot
    source, output = tmp_path / 'source.docx', tmp_path / 'assembled.docx'
    report(source)
    original = source.read_bytes()
    writer = ReportBatchDocument(temperature_chart=insert_temperature_chart)
    requested = batch_input(source)
    plan = writer.preview(source, **requested)
    assert plan['ready'], plan['conflicts']
    assert plan['source_sha256'] == sha256(original).hexdigest()
    force_preview = plan['results'][1]
    assert force_preview['current_result'] == 'Old value'
    assert force_preview['current_comment'] == 'Pass'
    assert '410' in force_preview['new_result']
    assert force_preview['new_comment'] == ''
    writer.update(source, output, plan, **requested)
    assert source.read_bytes() == original
    after = Document(output)
    assert after.paragraphs[0].text == 'Current product'
    assert after.paragraphs[0].runs[0].bold
    assert after.sections[0].header.paragraphs[0].text == 'Current product header'
    assert '410' in after.tables[1].cell(1, 2).text
    assert after.tables[1].cell(1, 3).text == ''
    assert read_photo_slot(output, 'photo-1')[0] == picture('green')
    with ZipFile(output) as package:
        xml = package.read('word/document.xml').decode()
        assert 'OLD TEMPERATURE' not in xml and '99°C' not in xml and 'OLD FORCE' not in xml
        assert 'KEEP PHOTO CAPTION' in xml and 'End of Report' in xml
        assert xml.count('connlab-report-result:temperature') == 1
        assert xml.count('connlab-report-result:force') == 1
        assert picture('green') in [package.read(name) for name in package.namelist() if name.startswith('word/media/')]
    with ZipFile(source) as before, ZipFile(output) as after_zip:
        assert before.read('word/styles.xml') == after_zip.read('word/styles.xml')


def test_batch_leaves_unselected_group_pagination_and_table_unchanged(tmp_path):
    source, output = tmp_path / 'source.docx', tmp_path / 'assembled.docx'
    report(source)
    before = Document(source)
    untouched_heading = before.paragraphs[1]._p.xml
    untouched_table = before.tables[0]._tbl.xml
    writer = ReportBatchDocument()
    requested = {'fact_replacements': [], 'photos': [],
                 'results': [{'result': mechanical(), 'target': {
                     'result_table': 2, 'result_row': 1, 'appendix_table': 3,
                     'appendix_title': 'Appendix B'}}]}
    plan = writer.preview(source, **requested)
    assert plan['ready'], plan['conflicts']
    writer.update(source, output, plan, **requested)
    after = Document(output)
    assert after.paragraphs[1]._p.xml == untouched_heading
    assert after.tables[0]._tbl.xml == untouched_table


def test_batch_keeps_downstream_group_heading_with_table_until_explicit_page_boundary(tmp_path):
    source, output = tmp_path / 'source.docx', tmp_path / 'assembled.docx'
    document = Document()
    for group in ('A', 'B', 'C', 'D', 'E'):
        heading = document.add_paragraph(f'Group {group} Test Results')
        if group == 'D':
            heading.paragraph_format.page_break_before = True
        table = document.add_table(rows=2, cols=3)
        for cell, label in zip(table.rows[0].cells, ['Step', 'Result', 'Comment']):
            cell.text = label
        table.cell(1, 0).text = '2'
    document.save(source)
    before_tables = [table._tbl.xml for table in document.tables[-3:]]
    before_headings = {p.text: p._p.xml for p in document.paragraphs if 'Test Results' in p.text}
    writer = ReportBatchDocument()
    requested = {'fact_replacements': [], 'photos': [], 'results': [{'result': mechanical()}]}
    plan = writer.preview(source, **requested)
    assert plan['ready'], plan['conflicts']
    writer.update(source, output, plan, **requested)
    after = Document(output)
    headings = {p.text: p for p in after.paragraphs if 'Test Results' in p.text}
    assert headings['Group C Test Results'].paragraph_format.keep_with_next is True
    assert 'Group C Test Results' in ' '.join(change['label'] for change in plan['changes'])
    assert headings['Group A Test Results']._p.xml == before_headings['Group A Test Results']
    for group in ('D', 'E'):
        assert headings[f'Group {group} Test Results']._p.xml == before_headings[f'Group {group} Test Results']
    assert [table._tbl.xml for table in after.tables[-3:]] == before_tables


@pytest.mark.parametrize('overlap', ['result', 'photo', 'fact'])
def test_overlap_is_previewed_before_any_output_is_written(tmp_path, overlap):
    source = tmp_path / 'source.docx'
    report(source)
    requested = batch_input(source)
    if overlap == 'result':
        duplicate = deepcopy(requested['results'][1])
        duplicate['result']['result_id'] = 'other-force'
        requested['results'].append(duplicate)
    elif overlap == 'photo':
        requested['photos'][0]['slot_id'] = 'photo-1'
    else:
        requested['fact_replacements'] = [('Old value', 'Changed value')]
    writer = ReportBatchDocument()
    plan = writer.preview(source, **requested)
    assert not plan['ready']
    assert any(item['code'] == 'target_overlap' for item in plan['conflicts'])
    with pytest.raises(ValueError, match='conflict|overlap'):
        writer.update(source, tmp_path / 'must-not-exist.docx', plan, **requested)
    assert not (tmp_path / 'must-not-exist.docx').exists()


def test_changed_source_or_changed_selection_cannot_apply_a_preview(tmp_path):
    source, output = tmp_path / 'source.docx', tmp_path / 'output.docx'
    report(source)
    writer = ReportBatchDocument()
    requested = {'fact_replacements': [], 'results': [{'result': mechanical()}], 'photos': []}
    plan = writer.preview(source, **requested)
    assert plan['ready']
    changed = deepcopy(requested)
    changed['results'][0]['result']['data']['rows'][0]['value'] = '999'
    with pytest.raises(ValueError, match='changed|refresh'):
        writer.update(source, output, plan, **changed)
    document = Document(source)
    document.add_paragraph('User edit')
    document.save(source)
    with pytest.raises(ValueError, match='changed|refresh'):
        writer.update(source, output, plan, **requested)
    assert not output.exists()


def test_ambiguous_result_row_requires_explicit_mapping(tmp_path):
    source = tmp_path / 'source.docx'
    report(source)
    document = Document(source)
    document.add_paragraph('Group B Test Results')
    table = document.add_table(rows=2, cols=3)
    for cell, value in zip(table.rows[0].cells, ['Step', 'Result', 'Comment']):
        cell.text = value
    table.cell(1, 0).text = '2'
    document.save(source)
    writer = ReportBatchDocument()
    plan = writer.preview(source, fact_replacements=[], results=[{'result': mechanical()}], photos=[])
    assert not plan['ready']
    assert plan['conflicts'][0]['code'] == 'ambiguous_result_target'
    assert len(plan['results'][0]['candidates']['result_rows']) == 2


@pytest.mark.parametrize('title', ['Appendix D', 'Appendix 4'])
def test_two_new_appendices_cannot_claim_the_same_identifier(tmp_path, title):
    source = tmp_path / 'source.docx'
    document = Document()
    for group in ('A', 'B'):
        document.add_paragraph(f'Group {group} Test Results')
        table = document.add_table(rows=2, cols=3)
        for cell, value in zip(table.rows[0].cells, ['Step', 'Result', 'Comment']):
            cell.text = value
        table.cell(1, 0).text = '2'
    document.save(source)
    plan = ReportBatchDocument().preview(source, fact_replacements=[], photos=[], results=[
        {'result': mechanical('first', 'A'), 'target': {'appendix_title': title}},
        {'result': mechanical('second', 'B'), 'target': {'appendix_title': title}}])
    assert not plan['ready']
    assert any(item['code'] == 'appendix_identity_conflict' for item in plan['conflicts'])


def test_late_chart_failure_does_not_leave_a_partial_output(tmp_path):
    source, output = tmp_path / 'source.docx', tmp_path / 'output.docx'
    report(source)
    original = source.read_bytes()
    requested = batch_input(source)

    def unavailable_chart(*args):
        raise ValueError('Synthetic chart export failure')

    writer = ReportBatchDocument(temperature_chart=unavailable_chart)
    plan = writer.preview(source, **requested)
    with pytest.raises(ValueError, match='Synthetic chart'):
        writer.update(source, output, plan, **requested)
    assert not output.exists()
    assert source.read_bytes() == original


def test_protected_original_is_restored_once_after_the_whole_batch(tmp_path):
    from backend.infrastructure.office.office_protected_document_gateway import ProtectedWordPackageGateway
    source, plain, output = tmp_path / 'source.docx', tmp_path / 'plain.docx', tmp_path / 'output.docx'
    document = Document(); document.add_paragraph('Original product'); document.save(plain)
    source.write_bytes(b'protected-original')

    class TestProtector:
        def __init__(self):
            self.calls = 0

        def encrypt_and_verify(self, *, source_path, output_path, **kwargs):
            self.calls += 1
            output_path.write_bytes(b'protected:' + source_path.read_bytes())

    protector = TestProtector()
    gateway = ProtectedWordPackageGateway(
        protected_detector=lambda path: path.read_bytes() == b'protected-original',
        decryptor=lambda source, output, password: output.write_bytes(plain.read_bytes()), protector=protector)
    writer = ReportBatchDocument(protected=gateway)
    requested = {'fact_replacements': [('Original product', 'New product')], 'results': [], 'photos': []}
    plan = writer.preview(source, **requested)
    writer.update(source, output, plan, **requested)
    assert protector.calls == 1
    assert output.read_bytes().startswith(b'protected:PK')
    assert source.read_bytes() == b'protected-original'


def test_existing_output_and_new_generated_evidence_are_not_overwritten_by_facts(tmp_path):
    source, output = tmp_path / 'source.docx', tmp_path / 'existing.docx'
    report(source)
    document = Document(source); document.add_paragraph('Existing SN1 label'); document.save(source)
    writer = ReportBatchDocument()
    conflict = writer.preview(source, fact_replacements=[('SN1', 'SN2')],
        results=[{'result': mechanical()}], photos=[])
    assert not conflict['ready']
    assert any('measurement evidence' in item['message'] for item in conflict['conflicts'])
    requested = {'fact_replacements': [('Original product', 'Current product')], 'results': [], 'photos': []}
    plan = writer.preview(source, **requested)
    output.write_bytes(b'User report')
    with pytest.raises(ValueError, match='exists'):
        writer.update(source, output, plan, **requested)
    assert output.read_bytes() == b'User report'
