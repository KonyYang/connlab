"""Reviewed Tools distinctions remain visible in the generated report copy."""
from zipfile import ZipFile
from lxml import etree
from backend.infrastructure.office.report_authoring.word_copy import NS

from backend.infrastructure.office.report_authoring.results_document import ReportResultsDocument, result_notes
from tests.unit.report_authoring.test_results_document import fixture_report, mechanical
from tests.unit.test_report_tools_package import service, temperature_input


def test_package_force_appendix_keeps_part_and_raw_signed_force(tmp_path):
    source, output = tmp_path / 'original.docx', tmp_path / 'copy.docx'
    fixture_report(source)
    result = mechanical()
    for index, row in enumerate(result['data']['rows']):
        row.update(part=f'End {index + 1}', raw_value='-' + row['value'])
    ReportResultsDocument().update(source, output, result, result_table=0, result_row=1,
        appendix_table=1, appendix_title='Appendix B')
    with ZipFile(output) as archive:
        document = etree.fromstring(archive.read('word/document.xml'))
    table = document.xpath('//w:tbl', namespaces=NS)[-1]
    rows = [[ ''.join(cell.xpath('.//w:t/text()', namespaces=NS)) for cell in row.xpath('./w:tc', namespaces=NS)]
            for row in table.xpath('./w:tr', namespaces=NS)]
    assert rows[0] == [
        'Sample SN', 'Instrument record', 'Color', 'Part', 'Retention hold force (N)', 'Raw signed force (N)', 'Hold (s)']
    assert 'End 1' in rows[1]
    assert '-410' in rows[1]


def test_temperature_notes_distinguish_tools_effective_decision_from_fitted_curve():
    source, request = temperature_input()
    _, content = service().export_temperature(source, 'scanner.csv', request)
    data = service().inspect(content)['entries'][0]['data']
    fitted = data['analysis']['maximum_fit']['fitted_coefficients'].copy()
    notes = result_notes({'kind': 'temperature', 'data': data})
    assert any('Tools effective Max' in note and '0.0005' in note for note in notes)
    assert any('not the fitted chart curve' in note for note in notes)
    assert data['analysis']['maximum_fit']['fitted_coefficients'] == fitted
