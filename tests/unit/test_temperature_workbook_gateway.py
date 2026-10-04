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
