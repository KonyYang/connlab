from hashlib import sha256
from io import BytesIO

from fastapi.testclient import TestClient
from openpyxl import Workbook, load_workbook
import pytest

from backend.api.main import app
from tests.unit.test_temperature_rise_calculations import baseline_rows


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


def test_import_prepare_analyze_and_download_round_trip_without_project_authority():
    client = TestClient(app)
    source = scanner_bytes()
    digest = sha256(source).hexdigest()
    imported = client.post('/api/tools/temperature-rise/import', files={'file': ('scanner.xlsx', source)})
    assert imported.status_code == 200, imported.text
    data = imported.json()
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
