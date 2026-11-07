from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from docx import Document
import pytest
from lxml import etree

from backend.infrastructure.office.report_authoring.linked_region import LinkedReportRegion


@pytest.mark.parametrize('modifier, amount, expected', [
    ('themeTint', 'FF', '336699'), ('themeTint', '00', 'FFFFFF'), ('themeTint', '99', '75A3D1'),
    ('themeShade', 'FF', '336699'), ('themeShade', '00', '000000'), ('themeShade', '99', '1F3D5C')])
def test_source_word_theme_modifiers_preserve_hue_and_use_hsl_luminance(modifier, amount, expected):
    from backend.infrastructure.office.report_authoring.linked_region import resolve_theme_colors, W, A
    theme = etree.fromstring(f'<a:theme xmlns:a="{A}"><a:themeElements><a:clrScheme><a:accent1><a:srgbClr val="336699"/></a:accent1></a:clrScheme></a:themeElements></a:theme>'.encode())
    color = etree.Element(f'{{{W}}}color')
    color.set(f'{{{W}}}themeColor', 'accent1'); color.set(f'{{{W}}}{modifier}', amount)
    resolve_theme_colors(color, theme)
    assert color.get(f'{{{W}}}val') == expected
    assert color.get(f'{{{W}}}{modifier}') is None


def test_foreground_and_background_theme_modifiers_are_independent():
    from backend.infrastructure.office.report_authoring.linked_region import resolve_theme_colors, W, A
    theme = etree.fromstring(f'<a:theme xmlns:a="{A}"><a:themeElements><a:clrScheme><a:accent1><a:srgbClr val="336699"/></a:accent1></a:clrScheme></a:themeElements></a:theme>'.encode())
    shading = etree.Element(f'{{{W}}}shd')
    for name, value in [('themeColor', 'accent1'), ('themeFill', 'accent1'), ('themeTint', '00'), ('themeFillShade', '99')]:
        shading.set(f'{{{W}}}{name}', value)
    resolve_theme_colors(shading, theme)
    assert shading.get(f'{{{W}}}val') == 'FFFFFF'
    assert shading.get(f'{{{W}}}fill') == '1F3D5C'
    assert not any('theme' in key for key in shading.attrib)


def test_shading_changes_luminance_not_each_rgb_channel():
    from backend.infrastructure.office.report_authoring.linked_region import resolve_theme_colors, W, A
    theme = etree.fromstring(f'<a:theme xmlns:a="{A}"><a:themeElements><a:clrScheme><a:accent1><a:srgbClr val="99CCFF"/></a:accent1></a:clrScheme></a:themeElements></a:theme>'.encode())
    color = etree.Element(f'{{{W}}}color')
    color.set(f'{{{W}}}themeColor', 'accent1'); color.set(f'{{{W}}}themeShade', '99')
    resolve_theme_colors(color, theme)
    assert color.get(f'{{{W}}}val') == '007AF5'


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
    text_properties = etree.SubElement(chart, f'{{{c}}}txPr')
    a = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    etree.SubElement(etree.SubElement(etree.SubElement(text_properties, f'{{{a}}}p'), f'{{{a}}}pPr'), f'{{{a}}}defRPr', sz='1000')
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
    with ZipFile(target) as archive:
        original_theme = archive.read('word/theme/theme1.xml')
        original_styles = etree.fromstring(archive.read('word/styles.xml'))
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
    assert all_parts['word/theme/theme1.xml'] == original_theme
    updated_styles = etree.fromstring(all_parts['word/styles.xml'])
    w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    for original in original_styles:
        identity = original.get(f'{{{w}}}styleId')
        counterpart = next((style for style in updated_styles if style.tag == original.tag and style.get(f'{{{w}}}styleId') == identity), None)
        assert counterpart is not None
        assert etree.tostring(counterpart, method='c14n') == etree.tostring(original, method='c14n')


@pytest.mark.parametrize('reference', ['footnoteReference', 'endnoteReference', 'commentReference',
    'commentRangeStart', 'commentRangeEnd', 'bookmarkStart', 'bookmarkEnd', 'hyperlink'])
def test_region_rejects_document_level_references_without_copying_or_remapping(reference):
    raw = linked_source()
    with ZipFile(BytesIO(raw)) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    root = etree.fromstring(parts['word/document.xml'])
    element = etree.SubElement(root.find(f'{{{w}}}body')[0], f'{{{w}}}{reference}')
    element.set(f'{{{w}}}anchor' if reference == 'hyperlink' else f'{{{w}}}id', '1')
    if reference == 'bookmarkStart': element.set(f'{{{w}}}name', 'TargetExistingBookmark')
    parts['word/document.xml'] = etree.tostring(root)
    stream = BytesIO()
    with ZipFile(stream, 'w', ZIP_DEFLATED) as archive:
        for name, content in parts.items(): archive.writestr(name, content)
    original = stream.getvalue()
    with pytest.raises(ValueError, match='document-level references'):
        LinkedReportRegion().preview(original, {'start': 0, 'end': 2, 'freeze_external_charts': True})
    assert stream.getvalue() == original


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


def test_adopted_fixed_table_and_native_chart_fit_six_inches_without_changing_chart_or_target_parts(tmp_path):
    from docx.shared import Inches
    from backend.infrastructure.office.report_authoring.linked_region import W, A, C
    wp = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
    with ZipFile(BytesIO(linked_source())) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    root = etree.fromstring(parts['word/document.xml']); body = root.find(f'{{{W}}}body')
    table = body[1]
    table.find(f'{{{W}}}tblPr/{{{W}}}tblW').attrib.update({f'{{{W}}}type': 'dxa', f'{{{W}}}w': '10095'})
    for column, width in zip(table.find(f'{{{W}}}tblGrid'), (5000, 5095)): column.set(f'{{{W}}}w', str(width))
    for row in table.findall(f'{{{W}}}tr'):
        properties = etree.SubElement(row, f'{{{W}}}trPr')
        etree.SubElement(properties, f'{{{W}}}trHeight', {f'{{{W}}}val': '300', f'{{{W}}}hRule': 'atLeast'})
        for cell, width in zip(row.findall(f'{{{W}}}tc'), (5000, 5095)):
            cell.find(f'{{{W}}}tcPr/{{{W}}}tcW').set(f'{{{W}}}w', str(width))
    chart = body[2].find(f'.//{{{C}}}chart'); run = chart.getparent(); run.remove(chart)
    inline = etree.SubElement(etree.SubElement(run, f'{{{W}}}drawing'), f'{{{wp}}}inline')
    etree.SubElement(inline, f'{{{wp}}}extent', cx='6324600', cy='3600450')
    etree.SubElement(inline, f'{{{wp}}}docPr', id='1', name='Native curve')
    etree.SubElement(etree.SubElement(inline, f'{{{A}}}graphic'), f'{{{A}}}graphicData', uri=C).append(chart)
    parts['word/document.xml'] = etree.tostring(root)
    stream = BytesIO()
    with ZipFile(stream, 'w', ZIP_DEFLATED) as archive:
        for name, content in parts.items(): archive.writestr(name, content)
    original = stream.getvalue(); reader = LinkedReportRegion()
    data = reader.preview(original, {'start': 0, 'end': 2, 'freeze_external_charts': True})
    target, wide = tmp_path/'six-inch.docx', tmp_path/'wide-control.docx'
    document = Document(); document.sections[0].page_width = Inches(8.5)
    document.sections[0].left_margin = document.sections[0].right_margin = Inches(1.25)
    document.sections[0].header.paragraphs[0].text = 'Target header unchanged'
    document.add_paragraph('Target body'); document.save(target)
    with ZipFile(target) as archive:
        before = {name: archive.read(name) for name in archive.namelist()}
    document.sections[0].page_width = Inches(11); document.save(wide)
    reader.append(target, data, 'width-check'); reader.append(wide, data, 'width-check')
    with ZipFile(target) as archive, ZipFile(wide) as control:
        root = etree.fromstring(archive.read('word/document.xml'))
        table = root.find(f'.//{{{W}}}tbl')
        assert int(table.find(f'{{{W}}}tblPr/{{{W}}}tblW').get(f'{{{W}}}w')) <= 8640
        assert sum(int(col.get(f'{{{W}}}w')) for col in table.find(f'{{{W}}}tblGrid')) <= 8640
        for row in table.findall(f'{{{W}}}tr'):
            assert sum(int(cell.find(f'{{{W}}}tcPr/{{{W}}}tcW').get(f'{{{W}}}w')) for cell in row.findall(f'{{{W}}}tc')) <= 8640
        extent = root.find(f'.//{{{wp}}}extent')
        assert int(extent.get('cx')) <= 8640 * 635
        assert int(extent.get('cy')) / int(extent.get('cx')) == pytest.approx(3600450 / 6324600, abs=1e-6)
        chart_name = next(name for name in archive.namelist() if name.endswith('/chart1.xml'))
        scaled_chart = etree.fromstring(archive.read(chart_name)); original_chart = etree.fromstring(control.read(chart_name))
        sizes = scaled_chart.xpath('//@sz'); original_sizes = original_chart.xpath('//@sz')
        assert sizes and all(int(size) < int(original) for size, original in zip(sizes, original_sizes))
        assert [etree.tostring(series, method='c14n') for series in scaled_chart.findall(f'.//{{{C}}}ser')] == [etree.tostring(series, method='c14n') for series in original_chart.findall(f'.//{{{C}}}ser')]
        for chart_tree in (scaled_chart, original_chart):
            for element in chart_tree.iter():
                if element.tag in {f'{{{A}}}rPr', f'{{{A}}}defRPr', f'{{{A}}}endParaRPr'}: element.attrib.pop('sz', None)
        assert etree.tostring(scaled_chart, method='c14n') == etree.tostring(original_chart, method='c14n')
        assert all(int(size.get(f'{{{W}}}val')) < 22 for size in table.findall(f'.//{{{W}}}rPr/{{{W}}}sz'))
        assert table.findall(f'.//{{{W}}}rPr/{{{W}}}sz')
        assert all(int(height.get(f'{{{W}}}val')) < 300 for height in table.findall(f'.//{{{W}}}trHeight'))
        assert int(table.find(f'{{{W}}}tblPr/{{{W}}}tblCellMar/{{{W}}}left').get(f'{{{W}}}w')) < 108
        for name in ('word/header1.xml', 'word/theme/theme1.xml'):
            assert archive.read(name) == before[name]
        assert etree.tostring(root.find(f'{{{W}}}body/{{{W}}}sectPr')) == etree.tostring(etree.fromstring(before['word/document.xml']).find(f'{{{W}}}body/{{{W}}}sectPr'))
    assert stream.getvalue() == original
    # No geometric shrink means no font override or source-chart byte change.
    from base64 import b64decode, b64encode
    with ZipFile(wide) as archive:
        assert archive.read(chart_name) == b64decode(data['parts']['word/charts/chart1.xml'])
    from copy import deepcopy
    unresolved = deepcopy(data); styles = etree.fromstring(b64decode(unresolved['parts']['word/styles.xml']))
    for element in list(styles.iter()):
        if element.tag in {f'{{{W}}}sz', f'{{{W}}}szCs'}: element.getparent().remove(element)
    unresolved['parts']['word/styles.xml'] = b64encode(etree.tostring(styles)).decode()
    unsafe = tmp_path/'unresolved.docx'; Document().save(unsafe); before = unsafe.read_bytes()
    with pytest.raises(ValueError, match='font size'):
        reader.append(unsafe, unresolved, 'unresolved-size')
    assert unsafe.read_bytes() == before
    repeated = deepcopy(data); block = etree.fromstring(repeated['blocks'][2].encode())
    drawing = deepcopy(block.find(f'.//{{{wp}}}inline').getparent())
    drawing.find(f'{{{wp}}}inline/{{{wp}}}extent').set('cx', '3000000')
    etree.SubElement(block, f'{{{W}}}r').append(drawing)
    repeated['blocks'][2] = etree.tostring(block).decode()
    with pytest.raises(ValueError, match='incompatible adopted display sizes'):
        reader.append(unsafe, repeated, 'mixed-shared-chart')
    assert unsafe.read_bytes() == before


def test_floating_adopted_drawing_is_rejected_without_changing_target(tmp_path):
    from backend.infrastructure.office.report_authoring.linked_region import W, WP
    reader = LinkedReportRegion()
    data = reader.preview(linked_source(), {'start': 0, 'end': 2, 'freeze_external_charts': True})
    block = etree.fromstring(data['blocks'][2].encode())
    etree.SubElement(etree.SubElement(block, f'{{{W}}}drawing'), f'{{{WP}}}anchor')
    data['blocks'][2] = etree.tostring(block).decode()
    target = tmp_path/'unchanged.docx'; Document().save(target); before = target.read_bytes()
    with pytest.raises(ValueError, match='Floating'):
        reader.append(target, data, 'unsupported-placement')
    assert target.read_bytes() == before


def test_native_chart_with_unknown_default_font_size_is_not_guessed():
    from backend.infrastructure.office.report_authoring.linked_region import scale_chart_text, C, A
    with ZipFile(BytesIO(linked_source())) as archive:
        chart = etree.fromstring(archive.read('word/charts/chart1.xml'))
    chart.find(f'{{{C}}}txPr/{{{A}}}p/{{{A}}}pPr/{{{A}}}defRPr').attrib.pop('sz')
    with pytest.raises(ValueError, match='font size'):
        scale_chart_text(etree.tostring(chart), 0.85)
