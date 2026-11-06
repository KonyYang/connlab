"""Optional package downloads leave existing standalone XLSX contracts intact."""
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.routes_tools_temperature import router as temperature_router
from backend.api.routes_tools_mechanical_summary import router as mechanical_router
from tests.unit.test_report_tools_package import service, temperature_input, instrument_pdf, workbook_bytes


def client():
    app = FastAPI()
    app.include_router(temperature_router)
    app.include_router(mechanical_router)
    return TestClient(app)


def test_temperature_package_endpoint_preserves_original_and_produces_reusable_analysis():
    raw, request = temperature_input()
    response = client().post('/api/tools/temperature-rise/export-package',
        files={'file': ('scanner.csv', raw, 'text/csv')}, data={'request': json.dumps(request)})
    assert response.status_code == 200, response.text
    assert response.headers['content-type'] == 'application/zip'
    assert '_ReportResults.zip' in response.headers['content-disposition']
    restored = service().inspect(response.content)
    assert restored['sources'][0]['content'] == raw
    assert restored['entries'][0]['data']['analysis']['points'][-1]['maximum'] == 24


def test_temperature_package_endpoint_rejects_modified_source_table():
    raw, request = temperature_input()
    response = client().post('/api/tools/temperature-rise/export-package',
        files={'file': ('scanner.csv', raw.replace(b'44', b'99'), 'text/csv')}, data={'request': json.dumps(request)})
    assert response.status_code == 422
    assert 'source' in response.json()['detail'].lower()


def test_mechanical_package_endpoint_returns_retained_sources_without_project_write(monkeypatch):
    monkeypatch.setattr('backend.infrastructure.office.mechanical_summary_folder.generate_folder_workbook', workbook_bytes)
    raw = instrument_pdf(['DL-2026-09-032', 'Retention Force', 'Fmax', '1 #1 2890 11.6', '2 #2 2970 11.5'])
    response = client().post('/api/tools/mechanical-summary/folder/export-package',
        files=[('files', ('Test results/retention.pdf', raw, 'application/pdf'))])
    assert response.status_code == 200, response.text
    restored = service().inspect(response.content)
    assert restored['sources'][0]['content'] == raw
    assert restored['entries'][0]['data']['summary']['average'] == '2930.0'
