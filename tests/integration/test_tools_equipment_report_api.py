from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from docx import Document
from fastapi.testclient import TestClient
import pytest

from backend.api import dependencies as deps
from backend.api.main import app
from backend.application.external_excel_read_service import EquipmentCalibrationReadResult, EquipmentCalibrationRow
from backend.application.tools_equipment_report_service import ToolsEquipmentReportService
from backend.infrastructure.office.equipment_id_document_reader import EquipmentIdDocumentReader
from backend.infrastructure.office.test_report_document_gateway import TestReportDocumentGateway
from backend.shared.config import Settings


class Catalog:
    def __init__(self, path):
        self.path = path

    def read_equipment_calibrations(self):
        return EquipmentCalibrationReadResult(str(self.path), ("All Equip.",), (
            EquipmentCalibrationRow("DG-Q-0033", "Multimeter", "Keysight", "2024-01-01", "2025-01-01", "All Equip."),
            EquipmentCalibrationRow("DG-L-0002", "Microscope", "Nikon", "Not calibrated", "Not applicable", "All Equip."),
        ))


def report_bytes():
    document = Document()
    document.add_paragraph("LABORATORY TEST REPORT")
    document.add_paragraph("Reviewer manual content must remain.")
    document.add_paragraph("7. EQUIPMENT")
    table = document.add_table(rows=2, cols=5)
    for cell, value in zip(table.rows[0].cells, ("Item", "Manufacturer", "ID Number", "Last Cal.", "Cal. Due")):
        cell.text = value
    table.cell(1, 0).text = "old equipment"
    data = BytesIO()
    document.save(data)
    return data.getvalue()


@pytest.fixture
def client(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    workbook = tmp_path / "catalog.xlsx"
    workbook.write_bytes(b"fixture")
    settings = Settings(data_dir=data, templates_dir=tmp_path / "templates",
                        projects_dir=tmp_path / "projects", database_path=tmp_path / "test.sqlite")
    instance = ToolsEquipmentReportService(source_reader=EquipmentIdDocumentReader(),
        catalog_reader=Catalog(workbook), report_writer=TestReportDocumentGateway())
    app.dependency_overrides[deps.get_settings] = lambda: settings
    app.dependency_overrides[deps.get_tools_equipment_report_service] = lambda: instance
    try:
        yield TestClient(app), data
    finally:
        app.dependency_overrides.pop(deps.get_settings, None)
        app.dependency_overrides.pop(deps.get_tools_equipment_report_service, None)


def test_download_updates_equipment_preserves_manual_content_and_cleans_temporary_files(client):
    test_client, data = client
    source = report_bytes()
    digest = sha256(source).hexdigest()
    response = test_client.post("/api/tools/equipment-list",
        files={"file": ("../Internal.docx", source, "application/octet-stream")},
        data={"references_text": "Q-0033, DG-Q-0033; L-0002; DG-Q-9999"})
    assert response.status_code == 200, response.text
    assert "Internal_EquipmentUpdated.docx" in response.headers["content-disposition"]
    review = json.loads(response.headers["x-equipment-review"])
    assert review["unmatched"] == ["DG-Q-9999"]
    assert review["expired"] == ["Q-0033"]
    assert review["incomplete"] == []
    updated = Document(BytesIO(response.content))
    assert updated.paragraphs[1].text == "Reviewer manual content must remain."
    assert [cell.text for cell in updated.tables[0].rows[1].cells] == [
        "Multimeter", "Keysight", "DG-Q-0033", "01-Jan-2024", "01-Jan-2025"]
    assert updated.tables[0].cell(2, 3).text == "Not calibrated"
    assert str(updated.tables[0].cell(1, 4).paragraphs[0].runs[0].font.color.rgb) == "FF0000"
    assert updated.tables[0].cell(3, 2).text == "DG-Q-9999"
    assert sha256(source).hexdigest() == digest
    assert list(data.iterdir()) == []


def test_equipment_upload_can_share_report_filename_without_overwriting_it(client):
    test_client, data = client
    selection = Document()
    selection.add_paragraph("L-0002")
    equipment = BytesIO()
    selection.save(equipment)
    response = test_client.post("/api/tools/equipment-list", files={
        "file": ("same.docx", report_bytes()), "equipment_file": ("same.docx", equipment.getvalue()),
    })
    assert response.status_code == 200, response.text
    assert Document(BytesIO(response.content)).tables[0].cell(1, 2).text == "DG-L-0002"
    assert list(data.iterdir()) == []


@pytest.mark.parametrize("report,selection,expected", [
    (b"not a report", {"references_text": "Q-0033"}, 422),
    (report_bytes(), {}, 422),
], ids=["invalid-docx", "missing-selection"])
def test_invalid_inputs_do_not_download_and_cleanup_uploads(client, report, selection, expected):
    test_client, data = client
    response = test_client.post("/api/tools/equipment-list",
        files={"file": ("report.docx", report)}, data=selection)
    assert response.status_code == expected, response.text
    assert "content-disposition" not in response.headers
    assert list(data.iterdir()) == []


def test_invalid_equipment_upload_returns_actionable_error_and_no_download(client):
    test_client, data = client
    response = test_client.post("/api/tools/equipment-list", files={
        "file": ("report.docx", report_bytes()), "equipment_file": ("EquipmentID.docx", b"bad file"),
    })
    assert response.status_code == 422
    assert "valid .docx" in response.json()["detail"]
    assert list(data.iterdir()) == []


def test_both_equipment_sources_are_rejected(client):
    test_client, data = client
    response = test_client.post("/api/tools/equipment-list", files={
        "file": ("report.docx", report_bytes()), "equipment_file": ("EquipmentID.docx", b"unused"),
    }, data={"references_text": "Q-0033"})
    assert response.status_code == 422
    assert "not both" in response.json()["detail"]
    assert list(data.iterdir()) == []


def test_large_review_is_bounded_and_reports_omitted_items(client):
    test_client, _data = client
    references = [f"未知设备{i}-{'器' * 60}" for i in range(80)]
    response = test_client.post("/api/tools/equipment-list",
        files={"file": ("report.docx", report_bytes())}, data={"references_text": "\n".join(references)})
    assert response.status_code == 200, response.text
    encoded = response.headers["x-equipment-review"]
    assert len(encoded) <= 7000
    review = json.loads(encoded)
    assert len(review["unmatched"]) + review["omitted"]["unmatched"] == 80
    assert review["omitted"]["unmatched"] > 0
