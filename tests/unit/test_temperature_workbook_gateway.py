from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from openpyxl import Workbook, load_workbook
import pytest

from backend.application.temperature_data_preparation import prepare_data, suggest_selection
from backend.domain.temperature_data import DataSelection, WorkbookTable
from backend.domain.temperature_rise import Coefficients, analyze_temperature_rise, generate_derating
from backend.infrastructure.office.temperature_workbook_gateway import TemperatureWorkbookGateway
from tests.unit.test_temperature_rise_calculations import baseline_rows


def test_reader_preserves_bytes_and_accepts_explicit_sheet(tmp_path):
    source = tmp_path / 'scanner.xlsx'
    book = Workbook()
    book.active.title = 'Notes'
    data = book.create_sheet('Initial Data')
    data.append(['Scan', 'Time', 'TC1', 'Ambient', 'Current'])
    data.append([1, '17:17', 28, 25, 10])
    data.append([2, '17:18', 29, 25, 10])
    book.save(source)
    digest = sha256(source.read_bytes()).hexdigest()
    table = TemperatureWorkbookGateway().read(source)
    assert table.sheet_name == 'Initial Data'
    assert table.sheet_names == ('Notes', 'Initial Data')
    assert table.rows[-1] == (2, '17:18', 29, 25, 10)
    choice = suggest_selection(table)
    assert choice.temperature_columns == (3,)
    assert choice.ambient_column == 4
    assert choice.current_column == 5
    assert sha256(source.read_bytes()).hexdigest() == digest
    with pytest.raises(ValueError, match='sheet'):
        TemperatureWorkbookGateway().read(source, sheet_name='Absent')


def test_export_contains_native_xy_charts_formulas_cached_values_and_source_mapping(tmp_path):
    rows = baseline_rows()
    headers = ('Original Scan', *(f'TC{i}' for i in range(1, 21)), 'Ambient', 'Current')
    values = tuple((row.source_row, *row.temperatures, row.ambient, row.current) for row in rows)
    table = WorkbookTable('scanner.xlsx', ('Initial Data',), 'Initial Data', (headers, *values))
    selection = DataSelection(1, 2, 301, 22, 23, tuple(range(2, 22)), 4)
    prepared = prepare_data(table, selection)
    analysis = analyze_temperature_rise(prepared.measurements, thermocouples_per_sample=4, zero_intercept=True)
    derating = generate_derating(analysis.average_fit.coefficients, max_temperature=105, step=2.5, ambient_point=75)
    output = tmp_path / 'result.xlsx'
    TemperatureWorkbookGateway().write(output, table=table, selection=selection, prepared=prepared,
        analysis=analysis, maximum_coefficients=analysis.maximum_fit.coefficients,
        average_coefficients=analysis.average_fit.coefficients, target_rise=30, derating=derating)
    book = load_workbook(output, data_only=False)
    assert book.sheetnames == ['Initial Data', 'T-riseChart', 'Derating']
    assert len(book['T-riseChart']._charts) == 1
    assert len(book['Derating']._charts) == 1
    assert book['T-riseChart']._charts[0].__class__.__name__ == 'ScatterChart'
    assert [series.trendline.order for series in book['T-riseChart']._charts[0].series] == [2, 2]
    assert all(series.trendline.intercept == 0 for series in book['T-riseChart']._charts[0].series)
    assert 'SQRT' in book['Derating']['B6'].value
    assert book['Derating'].freeze_panes == 'B6'
    assert book['Initial Data']['B5'].value.startswith('Sample 1 / TC 1')
    book.close()
    cached = load_workbook(output, data_only=True)
    assert cached['Derating']['B36'].value == pytest.approx(68.38881593205294)
    assert cached['Derating']['C36'].value == pytest.approx(54.71105274564235)
    assert cached['Derating']['B48'].value == 0
    cached.close()
    with ZipFile(output) as archive:
        assert not any('vba' in name.lower() for name in archive.namelist())
        charts = [name for name in archive.namelist() if name.startswith('xl/charts/chart') and name.endswith('.xml')]
        assert len(charts) == 2
        ns = {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}
        for name in charts:
            tree = ET.fromstring(archive.read(name))
            assert tree.findall('.//c:numCache/c:pt', ns), 'Charts must render before Excel recalculates.'
            drawing = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
            for line in tree.iter(f'{drawing}ln'):
                fills = [child for child in line if child.tag in {
                    f'{drawing}{kind}' for kind in ('noFill', 'solidFill', 'gradFill', 'pattFill')
                }]
                assert len(fills) <= 1, 'Excel rejects mutually exclusive line-fill elements.'


def test_export_refuses_existing_file(tmp_path):
    source = tmp_path / 'existing.xlsx'
    source.write_bytes(b'keep')
    with pytest.raises(ValueError, match='new'):
        TemperatureWorkbookGateway().write(source, table=None, selection=None, prepared=None,
            analysis=None, maximum_coefficients=None, average_coefficients=None, target_rise=None, derating=None)
    assert source.read_bytes() == b'keep'


def _report_export(tmp_path, maximum=None, average=None):
    rows = baseline_rows()
    table = WorkbookTable('scanner.xlsx', ('Initial Data',), 'Initial Data', (
        ('Scan', *(f'TC{i}' for i in range(1, 21)), 'Ambient', 'Current'),
        *((row.source_row, *row.temperatures, row.ambient, row.current) for row in rows)))
    selection = DataSelection(1, 2, 301, 22, 23, tuple(range(2, 22)), 4)
    prepared = prepare_data(table, selection)
    analysis = analyze_temperature_rise(prepared.measurements, thermocouples_per_sample=4, zero_intercept=True)
    output = tmp_path / 'report-ready.xlsx'
    TemperatureWorkbookGateway().write(output, table=table, selection=selection, prepared=prepared,
        analysis=analysis, maximum_coefficients=maximum or analysis.maximum_fit.coefficients,
        average_coefficients=average or analysis.average_fit.coefficients, target_rise=30, derating=None)
    return output, analysis


def test_report_export_has_traceable_key_readings_and_copyable_formula_summary(tmp_path):
    output, analysis = _report_export(tmp_path)
    book = load_workbook(output)
    sheet = book['T-riseChart']
    summary = next(book.defined_names['TemperatureRiseSummary'].destinations)[1]
    block = sheet[summary.replace('$', '')]
    assert block[0][0].value == 'Applied Current (A)'
    labels = [row[0].value for row in block]
    assert labels[1:6] == ['1#- T1', '1#- T2', '1#- T3', '1#- T4', '1# Max T-Rise']
    assert labels[-2:] == ['Max T-Rise', 'Avg of max T-Rise on each sample']
    assert block[1][2].data_type == 'f'
    assert block[5][2].value.startswith('=MAX(')
    assert block[-1][2].value.startswith('=AVERAGE(')
    assert block[1][2].number_format == '0.0'
    assert block[5][2].fill.fgColor != block[1][2].fill.fgColor
    assert block[-2][0].font.bold
    assert block[-2][2].border.bottom.style is not None
    raw_range = next(book.defined_names['KeyStageReadings'].destinations)[1]
    raw = sheet[raw_range.replace('$', '')]
    assert len(raw) == 7  # six genuine endpoints, no fabricated raw row for the inserted origin
    assert [row[0].value for row in raw[1:]] == [p.source_row for p in analysis.points if p.source_row]
    assert raw[1][1].value == 81  # original scanner scan, distinct from source row 51
    assert not sheet.protection.sheet
    book.close()
    cached = load_workbook(output, data_only=True)
    values = cached['T-riseChart'][summary.replace('$', '')]
    assert [cell.value for cell in values[-2][1:]] == pytest.approx([p.maximum for p in analysis.points])
    assert [cell.value for cell in values[-1][1:]] == pytest.approx([p.average for p in analysis.points])
    cached.close()


def test_report_export_has_editable_y_calculator_and_named_bold_colored_equations(tmp_path):
    output, _ = _report_export(tmp_path)
    book = load_workbook(output)
    sheet = book['T-riseChart']
    area = next(book.defined_names['CurrentCalculator'].destinations)[1]
    calculator = sheet[area.replace('$', '')]
    assert [c.value for c in calculator[0]] == ['y (°C)', 'a', 'b', 'c', 'x (A)']
    assert calculator[1][0].value == 30
    assert all(cell.data_type == 'f' and 'ROUND(' in cell.value for cell in calculator[1][1:4])
    assert calculator[1][-1].data_type == 'f'
    assert 'SQRT' in calculator[1][-1].value
    book.close()
    with ZipFile(output) as archive:
        ns = {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
              'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
        root = ET.fromstring(archive.read('xl/charts/chart1.xml'))
        labels = root.findall('.//c:trendline/c:trendlineLbl', ns)
        assert len(labels) == 2
        equations = [''.join(e.itertext()) for e in labels]
        assert 'Max T-Rise: y =' in equations[0]
        assert 'Avg of max T-Rise on each sample: y =' in equations[1]
        colors = []
        for label in labels:
            assert label.find('.//a:defRPr', ns).get('b') == '1'
            colors.append(label.find('.//a:srgbClr', ns).get('val'))
            assert label.find('c:tx/c:strRef/c:f', ns) is not None, 'Equation label stays linked when data is edited in Excel.'
        assert colors[0] != colors[1]
    cached = load_workbook(output, data_only=True)
    assert cached['T-riseChart'][calculator[1][-1].coordinate].value == pytest.approx(66.54445742154181)
    cached.close()


def test_report_chart_names_follow_summary_cells_and_labels_stack_at_upper_left(tmp_path):
    output, _ = _report_export(tmp_path)
    book = load_workbook(output)
    sheet = book['T-riseChart']
    assert sheet.freeze_panes is None
    assert book['Initial Data'].freeze_panes == 'B6'
    assert book['Derating'].freeze_panes is None  # No Derating was requested for this export.
    summary = sheet[next(book.defined_names['TemperatureRiseSummary'].destinations)[1].replace('$', '')]
    labels = [row[0] for row in summary[-2:]]
    chart = sheet._charts[0]
    positions = []
    for series, cell in zip(chart.series, labels):
        title = series.tx.strRef
        assert title.f == f"'T-riseChart'!$A${cell.row}"
        assert title.strCache.pt[0].v == cell.value
        label = series.trendline.trendlineLbl
        equation_cell = sheet[label.tx.strRef.f.split('!')[1].replace('$', '')]
        name_cell = sheet[f'A{equation_cell.row}']
        assert name_cell.value == f'=A{cell.row}'
        assert label.tx.strRef.strCache.pt[0].v.startswith(cell.value + ': y = ')
        position = label.layout.manualLayout
        assert .1 <= position.x <= .2  # Inside the left of the plot, not the axes or right edge.
        assert .1 <= position.y <= .4
        positions.append(position)
    assert positions[0].x == positions[1].x
    assert positions[1].y > positions[0].y
    book.close()


@pytest.mark.parametrize('constant_rise', [False, True])
def test_report_formulas_honor_spare_channel_order_current_scale_and_unconstrained_fit(tmp_path, constant_rise):
    headers = ('Current (mA)', 'Scanner Note', 'Spare', 'Ambient', 'TC1', 'Unused', 'Time')
    rows = []
    for current, rise in ((10000, 4), (20000, 9), (30000, 16)):
        value = 0 if constant_rise else rise
        rows.extend([(current, '=1+1', 25 + value, 25, 25 + value / 2, 999, '10:00')] * 2)
    table = WorkbookTable('reordered.xlsx', ('Data',), 'Data', (headers, *rows))
    selection = DataSelection(1, 2, 7, 4, 1, (5, 3), 2, current_multiplier=.001)
    prepared = prepare_data(table, selection)
    analysis = analyze_temperature_rise(prepared.measurements, thermocouples_per_sample=2, zero_intercept=False)
    output = tmp_path / 'mapped-report.xlsx'
    TemperatureWorkbookGateway().write(output, table=table, selection=selection, prepared=prepared,
        analysis=analysis, maximum_coefficients=analysis.maximum_fit.coefficients,
        average_coefficients=analysis.average_fit.coefficients, target_rise=None, derating=None)
    book = load_workbook(output)
    sheet = book['T-riseChart']
    raw = sheet[next(book.defined_names['KeyStageReadings'].destinations)[1].replace('$', '')]
    assert raw[1][2].value == '=1+1'
    assert raw[1][2].data_type == 's'
    rises = sheet[next(book.defined_names['StageTemperatureRise'].destinations)[1].replace('$', '')]
    assert rises[1][1].value == '=F2-$E2'  # TC1 first, replacement Spare second
    assert rises[1][2].value == '=D2-$E2'
    assert rises[1][-1].value == '=B2*0.001'
    summary = next(book.defined_names['TemperatureRiseSummary'].destinations)[1].replace('$', '')
    assert sheet._charts[0].series[0].trendline.intercept is None
    assert any('LINEST(' in cell.value and 'TRUE' in cell.value
               for row in sheet for cell in row if cell.data_type == 'f')
    book.close()
    cached = load_workbook(output, data_only=True)
    block = cached['T-riseChart'][summary]
    assert [cell.value for cell in block[0][1:]] == [0, 10, 20, 30]
    assert [cell.value for cell in block[-2][1:]] == pytest.approx([p.maximum for p in analysis.points])
    assert [cell.value for cell in block[-1][1:]] == pytest.approx([p.average for p in analysis.points])
    cached.close()


def test_report_preserves_operator_coefficient_overrides_instead_of_replacing_them_with_fits(tmp_path):
    maximum, average = Coefficients(.005, .1, 0), Coefficients(.004, .2, 0)
    output, _ = _report_export(tmp_path, maximum, average)
    book = load_workbook(output)
    sheet = book['T-riseChart']
    maximum_area = next(book.defined_names['CurrentCalculator'].destinations)[1].replace('$', '')
    average_area = next(book.defined_names['AverageCoefficients'].destinations)[1].replace('$', '')
    assert [cell.value for cell in sheet[maximum_area][1][1:4]] == [.005, .1, 0]
    assert [cell.value for cell in sheet[average_area][1][1:4]] == [.004, .2, 0]
    book.close()
