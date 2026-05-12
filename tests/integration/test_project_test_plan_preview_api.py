from __future__ import annotations

from pathlib import Path

from docx import Document
from fastapi.testclient import TestClient

from backend.api.main import app


def test_matrix_preview_api_extracts_docx_matrix(tmp_path: Path) -> None:
    docx_path = tmp_path / "product-spec.docx"
    _write_product_spec_docx(docx_path)
    client = TestClient(app)

    response = client.post(
        "/api/test-plan/matrix-preview-from-path",
        json={"source_path": str(docx_path), "project_id": "P1"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == "P1"
    assert payload["source_format"] == ".docx"
    assert payload["capability_status"] == "supported"
    assert payload["selected_table_index"] == 1
    assert payload["blockers"] == []
    assert [group["group_label"] for group in payload["groups"]] == [
        "Group 1",
        "Group 2",
    ]
    group_1 = payload["groups"][0]
    assert [step["sequence"] for step in group_1["steps"]] == [1, 2, 5, 8, 10]
    assert group_1["steps"][1]["test_item"] == "Contact Resistance (Low Level)"
    assert group_1["steps"][1]["source_section"] == "6.1"


def test_matrix_preview_api_reports_doc_and_pdf_as_deferred(tmp_path: Path) -> None:
    doc_path = tmp_path / "spec.doc"
    pdf_path = tmp_path / "spec.pdf"
    doc_path.write_bytes(b"legacy-doc-placeholder")
    pdf_path.write_bytes(b"%PDF-1.4")
    client = TestClient(app)

    doc_response = client.post(
        "/api/test-plan/matrix-preview-from-path",
        json={"source_path": str(doc_path)},
    )
    pdf_response = client.post(
        "/api/test-plan/matrix-preview-from-path",
        json={"source_path": str(pdf_path)},
    )

    assert doc_response.status_code == 200
    assert doc_response.json()["capability_status"] == "deferred"
    assert ".doc product specifications require" in doc_response.json()["blockers"][0]
    assert pdf_response.status_code == 200
    assert pdf_response.json()["capability_status"] == "deferred"
    assert "PDF product specifications require" in pdf_response.json()["blockers"][0]


def test_matrix_preview_api_reports_missing_source(tmp_path: Path) -> None:
    client = TestClient(app)

    response = client.post(
        "/api/test-plan/matrix-preview-from-path",
        json={"source_path": str(tmp_path / "missing.docx")},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def _write_product_spec_docx(path: Path) -> None:
    document = Document()
    table = document.add_table(rows=4, cols=4)
    rows = [
        ["test Items", "Section", "Group 1", "Group 2"],
        ["Examination of Product", "5.4", "1,10", "1,13"],
        ["Contact Resistance (Low Level)", "6.1", "2,5,8", "2,5,10"],
        ["Durability", "7.1", "", "3"],
    ]
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            table.cell(row_index, column_index).text = value
    document.save(path)
