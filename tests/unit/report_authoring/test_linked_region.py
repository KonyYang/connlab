from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from docx import Document
import pytest
from lxml import etree

from backend.infrastructure.office.report_authoring.linked_region import LinkedReportRegion


def linked_source():
    document = Document(); document.add_paragraph('Temperature source')
    normal_fonts = document.styles['Normal'].element.get_or_add_rPr().get_or_add_rFonts()
    for name, value in [('ascii', 'Arial'), ('hAnsi', 'Arial'), ('eastAsia', 'PMingLiU'), ('cs', 'Arial')]:
        normal_fonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}' + name, value)
    table = document.add_table(rows=2, cols=2); table.cell(0, 0).text = 'Current / A'; table.cell(0, 1).text = 'Max / °C'
    table.cell(1, 0).text = '100'; table.cell(1, 1).text = '26'
    document.add_paragraph('Temperature native curve')
    stream = BytesIO(); document.save(stream)
    with ZipFile(stream) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    root = etree.fromstring(parts['word/document.xml'])
    w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    r = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    c = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
    drawing = etree.SubElement(root.find(f'{{{w}}}body')[2], f'{{{w}}}r')
    etree.SubElement(drawing, f'{{{c}}}chart').set(f'{{{r}}}id', 'rIdChart')
    parts['word/document.xml'] = etree.tostring(root)
    rel = etree.fromstring(parts['word/_rels/document.xml.rels'])
    rel.append(etree.Element('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship',
        Id='rIdChart', Type=r+'/chart', Target='charts/chart1.xml'))
    parts['word/_rels/document.xml.rels'] = etree.tostring(rel)
    chart = etree.Element(f'{{{c}}}chartSpace', nsmap={'c': c, 'r': r})
    series = etree.SubElement(chart, f'{{{c}}}ser')
    title = etree.SubElement(etree.SubElement(series, f'{{{c}}}tx'), f'{{{c}}}strRef')
    title_cache = etree.SubElement(title, f'{{{c}}}strCache'); etree.SubElement(title_cache, f'{{{c}}}ptCount', val='1')
    etree.SubElement(etree.SubElement(title_cache, f'{{{c}}}pt', idx='0'), f'{{{c}}}v').text = 'Max T-rise'
    for axis in ('xVal', 'yVal'):
        reference = etree.SubElement(etree.SubElement(series, f'{{{c}}}{axis}'), f'{{{c}}}numRef')
        etree.SubElement(reference, f'{{{c}}}f').text = 'summary!A1:A2'
        cache = etree.SubElement(reference, f'{{{c}}}numCache'); etree.SubElement(cache, f'{{{c}}}ptCount', val='2')
        for index, value in enumerate(('0', '26')):
            etree.SubElement(etree.SubElement(cache, f'{{{c}}}pt', idx=str(index)), f'{{{c}}}v').text = value
    etree.SubElement(chart, f'{{{c}}}externalData').set(f'{{{r}}}id', 'rIdExternal')
    parts['word/charts/chart1.xml'] = etree.tostring(chart)
    parts['word/charts/_rels/chart1.xml.rels'] = (f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdExternal" Type="{r}/oleObject" Target="file:///never-read/source.xlsx" TargetMode="External"/></Relationships>').encode()
    content_types = etree.fromstring(parts['[Content_Types].xml'])
    content_types.append(etree.Element('{http://schemas.openxmlformats.org/package/2006/content-types}Override',
        PartName='/word/charts/chart1.xml', ContentType='application/vnd.openxmlformats-officedocument.drawingml.chart+xml'))
    parts['[Content_Types].xml'] = etree.tostring(content_types)
    output = BytesIO()
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for name, content in parts.items(): archive.writestr(name, content)
    return output.getvalue()


def test_linked_temperature_requires_acknowledgement_and_preserves_frozen_native_curve(tmp_path):
    reader = LinkedReportRegion(); raw = linked_source()
    with pytest.raises(ValueError, match='frozen'):
        reader.preview(raw, {'start': 0, 'end': 2, 'freeze_external_charts': False})
    data = reader.preview(raw, {'start': 0, 'end': 2, 'freeze_external_charts': True})
    assert data['frozen_chart_count'] == 1
    target = tmp_path/'target.docx'
    document = Document(); document.add_paragraph('TARGET IDENTITY'); document.save(target)
    reader.append(target, data, 'linked-test')
    reader.append(target, data, 'linked-test')
    with ZipFile(target) as archive:
        all_parts = {name: archive.read(name) for name in archive.namelist()}
    assert b'TARGET IDENTITY' in all_parts['word/document.xml']
    charts = [value for name, value in all_parts.items() if name.endswith('/chart1.xml')]
    assert len(charts) == 1 and b'numLit' in charts[0] and b'externalData' not in charts[0]
    assert etree.fromstring(charts[0]).find('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}tx/{http://schemas.openxmlformats.org/drawingml/2006/chart}v').text == 'Max T-rise'
    assert all(b'never-read' not in value for value in all_parts.values())
    assert '26' in ''.join(Document(target).element.xpath('//w:t/text()'))


def test_linked_region_result_writer_and_customer_supplement_use_same_native_evidence(tmp_path):
    from tests.unit.report_authoring.test_results_document import fixture_report, mechanical
    from backend.infrastructure.office.report_authoring.results_document import ReportResultsDocument
    from backend.infrastructure.office.report_authoring.customer_copy import CustomerReportCopy
    data = LinkedReportRegion().preview(linked_source(), {'start': 0, 'end': 2, 'freeze_external_charts': True})
    data['adoption'] = {'report_identity': 'SOURCE-032B', 'source_version': 'Rev A', 'source_locator': 'Table 1', 'adopted_scope': 'Temperature only', 'confirmed': True, 'customer_reference_allowed': True}
    data['adoption_notes'] = ['Reference SOURCE-032B Rev A; temperature only']
    result = mechanical(); result.update(kind='linked_temperature', data=data)
    source = tmp_path/'original.docx'; output = tmp_path/'working.docx'; fixture_report(source)
    before = source.read_bytes()
    ReportResultsDocument().update(source, output, result, result_table=0, result_row=1, appendix_table=1, appendix_title='Appendix B')
    assert source.read_bytes() == before
    class RemoveAppendixConverter:
        def generate_customer_report(self, *, source_path, template_path, output_path):
            document = Document(); document.add_paragraph('Customer report'); document.save(output_path)
    customer = tmp_path/'customer.docx'
    def no_recalculation(*args):
        raise AssertionError('An adopted native chart must not be recalculated')
    CustomerReportCopy(converter=RemoveAppendixConverter(), template=lambda: source, temperature_chart=no_recalculation).generate(output, customer, [result])
    with ZipFile(output) as internal, ZipFile(customer) as external:
        chart = next(internal.read(name) for name in internal.namelist() if name.endswith('/chart1.xml'))
        assert chart == next(external.read(name) for name in external.namelist() if name.endswith('/chart1.xml'))
        text = ''.join(etree.fromstring(external.read('word/document.xml')).xpath('//*[local-name()="t"]/text()'))
        assert '26' in text and 'temperature only' in text
