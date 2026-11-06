from dataclasses import replace
from decimal import Decimal
from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile

from docx import Document
import pytest

from backend.infrastructure.office.report_authoring.batch_document import ReportBatchDocument
from backend.infrastructure.office.test_report_document_gateway import TestReportDocumentGateway
from tests.unit.report_authoring.test_batch_document import mechanical, picture
from tests.unit.test_test_report_document_gateway import _llcr_dataset


def report(path):
    document = Document()
    document.add_paragraph('Original product').runs[0].bold = True
    document.add_paragraph('Group 1 Test Results')
    table = document.add_table(rows=2, cols=6)
    for cell, label in zip(table.rows[0].cells, ['Step', 'Test', 'Requirement', 'Step Description', 'Result', 'Comment']):
        cell.text = label
    for cell, value in zip(table.rows[1].cells, ['2', 'Low Level Contact Resistance', 'Initial ≤0.25mΩ',
                                               'Manual step description', 'Old LLCR', 'Pending']):
        cell.text = value
    document.add_paragraph('Group B Test Results')
    table = document.add_table(rows=2, cols=4)
    for cell, label in zip(table.rows[0].cells, ['Step', 'Test', 'Result', 'Comment']):
        cell.text = label
    for cell, value in zip(table.rows[1].cells, ['2', 'Retention Force', 'Old force', 'Pending']):
        cell.text = value
    document.add_picture(BytesIO(picture('blue')))
    document.add_paragraph('Approved photo caption')
    document.add_paragraph('*** End of Report ***')
    document.save(path)


def test_batch_combines_existing_llcr_with_results_facts_and_photos_in_one_copy(tmp_path):
    source, output = tmp_path / 'source.docx', tmp_path / 'batch.docx'
    report(source)
    original = source.read_bytes()
    dataset = _llcr_dataset()
    writer = ReportBatchDocument()
    request = {'fact_replacements': [('Original product', 'Current product')],
        'results': [{'result': mechanical()}], 'photos': [{'slot_id': 'photo-1', 'content': picture('green')}],
        'llcr_dataset': dataset}
    plan = writer.preview(source, **request)
    assert plan['ready'], plan['conflicts']
    assert plan['llcr']['rows'][0]['current_result'] == 'Old LLCR'
    assert plan['llcr']['rows'][0]['new_result'] == 'Initial ≤0.198mΩ'
    assert plan['llcr']['appendix']['action'] == 'create'
    assert plan['results'][0]['target']['appendix_title'] == 'Appendix B'
    assert plan['llcr']['guard_regions']
    writer.update(source, output, plan, **request)
    result = Document(output)
    assert result.tables[0].cell(1, 4).text == 'Initial ≤0.198mΩ'
    assert result.tables[0].cell(1, 5).text == 'Pass'
    assert '410' in result.tables[1].cell(1, 2).text
    assert result.paragraphs[0].text == 'Current product' and result.paragraphs[0].runs[0].bold
    with ZipFile(output) as package:
        xml = package.read('word/document.xml').decode()
        assert xml.count('Appendix A:') == 1
        assert xml.count('Appendix B:') == 1
        assert xml.index('Appendix A:') < xml.index('Appendix B:') < xml.index('End of Report')
    assert source.read_bytes() == original


def test_undecided_llcr_does_not_write_workflow_state_into_report_conclusion(tmp_path):
    source, output = tmp_path / 'source.docx', tmp_path / 'review.docx'
    report(source)
    dataset = _llcr_dataset()
    entry = replace(dataset.payload.entries[0], confirmed_outcome='not_determined',
                    override_reason='Engineering acceptance is awaiting review.')
    dataset = replace(dataset, payload=replace(dataset.payload, entries=(entry,)))
    original = source.read_bytes()
    writer = ReportBatchDocument()
    request = {'fact_replacements': [], 'results': [], 'photos': [], 'llcr_dataset': dataset}
    plan = writer.preview(source, **request)
    assert plan['ready'], plan['conflicts']
    writer.update(source, output, plan, **request)
    assert Document(output).tables[0].cell(1, 5).text == ''
    assert plan['llcr']['rows'][0]['new_comment'] == ''
    assert Document(output).tables[0].cell(1, 4).text == 'Initial ≤0.198mΩ'
    assert source.read_bytes() == original


@pytest.mark.parametrize('problem', ['requirement', 'ambiguous', 'appendix_layout', 'legacy_delta'])
def test_llcr_target_or_legacy_semantics_problem_blocks_during_preview(tmp_path, problem):
    source = tmp_path / 'source.docx'
    report(source)
    dataset = _llcr_dataset()
    document = Document(source)
    if problem == 'requirement':
        document.tables[0].cell(1, 2).text = 'Different approved requirement'
    elif problem == 'ambiguous':
        from copy import deepcopy
        document.tables[0]._tbl.append(deepcopy(document.tables[0].rows[1]._tr))
    elif problem == 'appendix_layout':
        end = document.paragraphs[-1]._p
        heading = document.add_paragraph('Appendix A: unrelated manual layout')
        table = document.add_table(rows=1, cols=2)
        end.addprevious(heading._p); end.addprevious(table._tbl)
    else:
        entry = replace(dataset.payload.entries[0], stage='delta', stage_label='Final LLCR')
        dataset = replace(dataset, payload=replace(dataset.payload, entries=(entry,)))
    document.save(source)
    original = source.read_bytes()
    writer = ReportBatchDocument()
    requested = {'fact_replacements': [], 'results': [], 'photos': [], 'llcr_dataset': dataset}
    plan = writer.preview(source, **requested)
    assert not plan['ready']
    assert any(item['code'] == 'invalid_llcr_target' for item in plan['conflicts'])
    with pytest.raises(ValueError, match='conflict'):
        writer.update(source, tmp_path / 'blocked.docx', plan, **requested)
    assert not (tmp_path / 'blocked.docx').exists()
    assert source.read_bytes() == original


@pytest.mark.parametrize('overlap', ['result_row', 'appendix_a', 'fact_group', 'fact_requirement', 'photo'])
def test_llcr_write_and_matching_guards_join_batch_overlap_checks(tmp_path, overlap):
    source = tmp_path / 'source.docx'
    report(source)
    requested = {'fact_replacements': [], 'results': [], 'photos': [], 'llcr_dataset': _llcr_dataset()}
    if overlap == 'result_row':
        requested['results'] = [{'result': mechanical(group='1')}]
    elif overlap == 'appendix_a':
        requested['results'] = [{'result': mechanical(), 'target': {'appendix_title': 'Appendix A'}}]
    elif overlap == 'fact_group':
        requested['fact_replacements'] = [('Group 1 Test Results', 'Group X Test Results')]
    elif overlap == 'fact_requirement':
        requested['fact_replacements'] = [('Initial ≤0.25mΩ', 'Initial ≤0.30mΩ')]
    else:
        prepared = tmp_path / 'prepared.docx'
        TestReportDocumentGateway().synchronize_llcr_results(source_path=source, output_path=prepared, dataset=_llcr_dataset())
        document = Document(prepared)
        document.tables[-1].cell(2, 2).paragraphs[0].add_run().add_picture(BytesIO(picture('red')))
        document.save(source)
        requested['photos'] = [{'slot_id': 'photo-2', 'content': picture('green')}]
    plan = ReportBatchDocument().preview(source, **requested)
    assert not plan['ready']
    assert any(item['code'] == 'target_overlap' for item in plan['conflicts'])


def test_llcr_gateway_preview_reuses_the_same_target_and_appendix_rules_as_apply(tmp_path):
    source, output = tmp_path / 'source.docx', tmp_path / 'updated.docx'
    report(source)
    original = source.read_bytes()
    gateway = TestReportDocumentGateway()
    first = gateway.preview_llcr_results(source_path=source, dataset=_llcr_dataset())
    assert source.read_bytes() == original
    assert first['changed']
    assert first['rows'][0]['requirement'] == 'Initial ≤0.25mΩ'
    gateway.synchronize_llcr_results(source_path=source, output_path=output, dataset=_llcr_dataset())
    second = gateway.preview_llcr_results(source_path=output, dataset=_llcr_dataset())
    assert not second['changed']
    assert second['appendix']['action'] == 'reuse'
    assert second['rows'][0]['current_result'] == first['rows'][0]['new_result']
    assert second['dataset_sha256'] == first['dataset_sha256']


def test_changed_confirmed_llcr_dataset_cannot_use_old_batch_preview(tmp_path):
    source, output = tmp_path / 'source.docx', tmp_path / 'updated.docx'
    report(source)
    writer = ReportBatchDocument()
    dataset = _llcr_dataset()
    plan = writer.preview(source, fact_replacements=[], results=[], photos=[], llcr_dataset=dataset)
    changed = replace(dataset, payload=replace(dataset.payload,
        entries=(replace(dataset.payload.entries[0], summary_max=Decimal('0.199')),)))
    with pytest.raises(ValueError, match='changed'):
        writer.update(source, output, plan, fact_replacements=[], results=[], photos=[], llcr_dataset=changed)
    assert not output.exists()


def test_llcr_last_preserves_temperature_editable_chart_and_unrelated_package_parts(tmp_path):
    from lxml import etree
    from backend.infrastructure.office.report_authoring.temperature_chart import insert_temperature_chart
    from tests.unit.report_authoring.test_batch_document import temperature
    source, output = tmp_path / 'source.docx', tmp_path / 'updated.docx'
    report(source)
    document = Document(source); document.tables[1].cell(1, 1).text = 'Temperature Rise'; document.save(source)
    result = temperature()
    result['target']['group_label'] = 'B'
    requested = {'fact_replacements': [], 'results': [{'result': result}], 'photos': [], 'llcr_dataset': _llcr_dataset()}
    writer = ReportBatchDocument(temperature_chart=insert_temperature_chart)
    plan = writer.preview(source, **requested)
    assert plan['ready'], plan['conflicts']
    writer.update(source, output, plan, **requested)
    with ZipFile(output) as after, ZipFile(source) as before:
        charts = [name for name in after.namelist() if name.startswith('word/charts/') and name.endswith('.xml') and '/_rels/' not in name]
        assert len(charts) == 1
        assert b'\x50\x4b' == next(after.read(name)[:2] for name in after.namelist() if name.startswith('word/embeddings/'))
        assert etree.fromstring(after.read('word/document.xml')).xpath(
            'count(//c:chart)', namespaces={'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}) == 1
        assert after.read('word/styles.xml') == before.read('word/styles.xml')
    assert Document(output).tables[0].cell(1, 4).text == 'Initial ≤0.198mΩ'


def test_llcr_preview_accepts_equivalent_word_namespace_prefixes(tmp_path):
    source, output = tmp_path / 'source.docx', tmp_path / 'updated.docx'
    report(source)
    package_bytes = BytesIO()
    with ZipFile(source) as original, ZipFile(package_bytes, 'w') as rewritten:
        for info in original.infolist():
            content = original.read(info.filename)
            if info.filename == 'word/document.xml':
                content = content.replace(b'xmlns:w=', b'xmlns:q=').replace(b'w:', b'q:')
            rewritten.writestr(info, content)
    source.write_bytes(package_bytes.getvalue())
    writer = ReportBatchDocument()
    requested = {'fact_replacements': [], 'results': [], 'photos': [], 'llcr_dataset': _llcr_dataset()}
    plan = writer.preview(source, **requested)
    assert plan['ready'], plan['conflicts']
    writer.update(source, output, plan, **requested)
    assert Document(output).tables[0].cell(1, 4).text == 'Initial ≤0.198mΩ'
