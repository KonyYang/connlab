from hashlib import sha256
from io import BytesIO, StringIO
import csv

from fastapi.testclient import TestClient
from openpyxl import Workbook, load_workbook
import pytest

from backend.api.main import app
from tests.unit.test_temperature_rise_calculations import baseline_rows
from tests.unit.test_temperature_data_preparation import grouped_scanner


def scanner_bytes():
    book = Workbook()
    book.active.title = 'Initial Data'
    book.active.append(['Scan', 'Time', *(f'TC{i}' for i in range(1, 21)), 'Ambient', 'Current'])
    for row in baseline_rows():
        book.active.append([row.source_row, '17:17', *row.temperatures, row.ambient, row.current])
    stream = BytesIO()
    book.save(stream)
    book.close()
    return stream.getvalue()


def test_grouped_csv_import_reports_auxiliary_currents_and_nonzero_intercept_default():
    source_table = grouped_scanner()
    stream = StringIO(newline='')
    csv.writer(stream, delimiter='\t').writerows(source_table.rows)
    source = stream.getvalue().encode('utf-16')
    client = TestClient(app)
    response = client.post('/api/tools/temperature-rise/import', files={'file': ('scanner.csv', source)})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result['selection']['current_column'] == 35
    layout = result['channel_layout']
    assert layout['current_columns'] == [34, 35, 36, 37]
    assert layout['stable_current_columns'] == [34, 36, 37]
    assert [group['sample_id'] for group in layout['sample_groups']] == ['1', '2', '3']
    assert layout['zero_intercept_default'] is False
    request = {'table': result['table'], 'selection': result['selection']}
    review = client.post('/api/tools/temperature-rise/prepare', json=request).json()
    assert not review['ready']
    assert [row['current'] for row in review['measurements'][:3]] == [0, 0, 10]
    assert result['table']['rows'][1][34] == '0.009999'
    download = client.post('/api/tools/temperature-rise/download', json={
        **request, 'zero_intercept': False, 'acknowledge_warnings': True,
    })
    assert download.status_code == 200, download.text[:300]
    book = load_workbook(BytesIO(download.content), data_only=True)
    initial = book['Initial Data']
    assert initial.max_column == 36
    assert 'Retained Current [AH:' in initial.cell(5, 34).value
    assert [float(initial.cell(6, column).value) for column in (34, 35, 36)] == [125.001, 3.001, 1.02]
    assert initial.cell(6, 33).value == 0  # Only the selected AI current is normalized.
    book.close()


def test_import_prepare_analyze_and_download_round_trip_without_project_authority():
    client = TestClient(app)
    source = scanner_bytes()
    digest = sha256(source).hexdigest()
    imported = client.post('/api/tools/temperature-rise/import', files={'file': ('scanner.xlsx', source)})
    assert imported.status_code == 200, imported.text
    data = imported.json()
    assert data['region_issue'] is None
    assert data['selection']['header_row'] == 1
    assert data['selection']['start_row'] == 2
    assert data['selection']['end_row'] == 301
    request = {'table': data['table'], 'selection': data['selection'], 'acknowledge_warnings': False, 'zero_intercept': True}
    confirmed = client.post('/api/tools/temperature-rise/prepare', json=request)
    assert confirmed.status_code == 200
    assert confirmed.json()['ready']
    analyzed = client.post('/api/tools/temperature-rise/analyze', json=request)
    assert analyzed.status_code == 200, analyzed.text
    analysis = analyzed.json()
    assert analysis['maximum_fit']['coefficients']['a'] == .004677
    maximum, average = analysis['maximum_fit']['coefficients'], analysis['average_fit']['coefficients']
    calculated = client.post('/api/tools/temperature-rise/current', json={'coefficients': maximum, 'target_rise': 30})
    assert calculated.json()['current'] == pytest.approx(66.54445742154181)
    parameters = {'max_temperature': 105, 'step': 2.5, 'ambient_point': 75}
    derating = client.post('/api/tools/temperature-rise/derating', json={'coefficients': average, **parameters})
    assert derating.json()['annotation']['basic'] == pytest.approx(68.38881593205294)
    download = client.post('/api/tools/temperature-rise/download', json={**request,
        'maximum_coefficients': maximum, 'average_coefficients': average, 'target_rise': 30, 'derating': parameters})
    assert download.status_code == 200, download.text[:300]
    assert 'scanner_T-rise_Derating.xlsx' in download.headers['content-disposition']
    book = load_workbook(BytesIO(download.content), data_only=True)
    assert book['Derating']['C36'].value == pytest.approx(54.71105274564235)
    book.close()
    assert sha256(source).hexdigest() == digest


def test_utf16_scanner_csv_uses_the_same_confirmation_calculation_and_excel_download_flow():
    stream = StringIO(newline='')
    writer = csv.writer(stream, delimiter='\t')
    writer.writerow(['名称:', '扫描仪数据'])
    writer.writerow(['扫描', '时间', *(f'TC{i}' for i in range(1, 21)), 'Ambient', 'Current'])
    for row in baseline_rows():
        writer.writerow([row.source_row, '2024/10/28 17:10:16:391', *row.temperatures, row.ambient, row.current])
    source = stream.getvalue().encode('utf-16')
    digest = sha256(source).hexdigest()
    client = TestClient(app)
    imported = client.post('/api/tools/temperature-rise/import', files={'file': ('../scanner.csv', source)})
    assert imported.status_code == 200, imported.text
    data = imported.json()
    assert data['table']['file_name'] == 'scanner.csv'
    assert data['table']['rows'][0] == ['名称:', '扫描仪数据']
    assert data['region_issue'] is None
    assert data['selection']['header_row'] == 2
    request = {'table': data['table'], 'selection': data['selection'], 'zero_intercept': True}
    assert client.post('/api/tools/temperature-rise/prepare', json=request).json()['ready']
    analyzed = client.post('/api/tools/temperature-rise/analyze', json=request)
    assert analyzed.status_code == 200, analyzed.text
    assert analyzed.json()['maximum_fit']['coefficients']['a'] == .004677
    download = client.post('/api/tools/temperature-rise/download', json=request)
    assert download.status_code == 200, download.text[:300]
    assert 'scanner_T-rise_Derating.xlsx' in download.headers['content-disposition']
    book = load_workbook(BytesIO(download.content), data_only=False)
    assert len(book['T-riseChart']._charts) == 1
    assert book['Initial Data']['B6'].value == baseline_rows()[0].temperatures[0]
    assert book['Initial Data']['A2'].value == 'Source: scanner.csv / Initial Data'
    book.close()
    assert sha256(source).hexdigest() == digest


def test_analyze_requires_warning_confirmation_and_invalid_cells_remain_blockers():
    client = TestClient(app)
    data = client.post('/api/tools/temperature-rise/import', files={'file': ('scanner.xlsx', scanner_bytes())}).json()
    request = {'table': data['table'], 'selection': data['selection'], 'zero_intercept': True}
    request['table']['rows'][-1][-1] = 0
    review = client.post('/api/tools/temperature-rise/prepare', json=request).json()
    assert not review['ready']
    assert any(issue['code'] == 'zero_current' for issue in review['issues'])
    assert client.post('/api/tools/temperature-rise/analyze', json=request).status_code == 422
    request['acknowledge_warnings'] = True
    assert client.post('/api/tools/temperature-rise/analyze', json=request).status_code == 200
    request['table']['rows'][-1][2] = None
    assert client.post('/api/tools/temperature-rise/analyze', json=request).status_code == 422


def test_import_rejects_unreadable_files_and_download_name_uses_no_client_path():
    client = TestClient(app)
    response = client.post('/api/tools/temperature-rise/import', files={'file': ('bad.xlsx', b'not a workbook')})
    assert response.status_code == 422
    data = client.post('/api/tools/temperature-rise/import', files={'file': ('../scanner.xlsx', scanner_bytes())}).json()
    assert data['table']['file_name'] == 'scanner.xlsx'


def test_unidentified_region_retains_source_for_manual_recovery_and_still_requires_data_validation():
    book = Workbook()
    book.active.title = 'Data'
    book.active.append(['Probe', 'Room', 'Supply'])
    book.active.append([25, 20, 10])
    book.active.append([26, 20, 0])
    stream = BytesIO()
    book.save(stream)
    book.close()
    content = stream.getvalue()
    client = TestClient(app)
    imported = client.post('/api/tools/temperature-rise/import', files={'file': ('custom.xlsx', content)})
    assert imported.status_code == 200
    data = imported.json()
    assert data['selection'] is None
    assert 'data region' in data['region_issue']
    assert data['table']['rows'] == [['Probe', 'Room', 'Supply'], [25, 20, 10], [26, 20, 0]]
    assert client.post('/api/tools/temperature-rise/analyze', json={
        'table': data['table'], 'selection': None,
    }).status_code == 422

    recovered = client.post('/api/tools/temperature-rise/import', files={'file': ('custom.xlsx', content)},
                            data={'header_row': 1, 'start_row': 2, 'end_row': 3})
    assert recovered.status_code == 200
    data = recovered.json()
    assert data['region_issue'] is None
    assert data['selection']['start_row'] == 2
    assert data['selection']['excluded_rows'] == []
    review = client.post('/api/tools/temperature-rise/prepare', json={
        'table': data['table'], 'selection': data['selection'],
    }).json()
    assert not review['ready']
    assert any(issue['code'] == 'zero_current' for issue in review['issues'])
    for override in ({'header_row': 1}, {'header_row': 2, 'start_row': 2, 'end_row': 3},
                     {'header_row': 1, 'start_row': 2, 'end_row': 99}):
        assert client.post('/api/tools/temperature-rise/import', files={'file': ('custom.xlsx', content)},
                           data=override).status_code == 422


def test_multiple_regions_require_operator_choice_and_a_different_sheet_can_recover_automatically():
    book = Workbook()
    sheet = book.active
    sheet.title = 'Ambiguous'
    header = ['Scan', 'Time', 'TC1', 'Ambient', 'Current']
    sheet.append(header)
    sheet.append([1, '17:17', 25, 20, 10])
    sheet.append(header)
    sheet.append([2, '17:18', 30, 20, 20])
    other = book.create_sheet('Complete')
    other.append(header)
    other.append([1, '17:17', 25, 20, 10])
    other.append([2, '17:18', 25, 20, 0])
    stream = BytesIO()
    book.save(stream)
    book.close()
    content = stream.getvalue()
    client = TestClient(app)
    def import_sheet(**data):
        response = client.post('/api/tools/temperature-rise/import', files={'file': ('scanner.xlsx', content)}, data=data)
        assert response.status_code == 200, response.text
        return response.json()

    ambiguous = import_sheet(sheet_name='Ambiguous')
    assert ambiguous['selection'] is None
    assert 'Multiple' in ambiguous['region_issue']
    assert len(ambiguous['table']['rows']) == 4
    manual = import_sheet(sheet_name='Ambiguous', header_row=3, start_row=4, end_row=4)
    assert manual['selection']['header_row'] == 3
    assert manual['region_issue'] is None
    automatic = import_sheet(sheet_name='Complete')
    assert automatic['region_issue'] is None
    assert automatic['selection']['end_row'] == 3
    assert automatic['selection']['excluded_rows'] == []
    assert automatic['table']['rows'][-1][-1] == 0
