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


def test_matrix_preview_api_maps_variant_marker_note_with_path_text(tmp_path: Path) -> None:
    docx_path = tmp_path / "product-spec-marker-variant.docx"
    _write_product_spec_docx_with_variant_note(docx_path)
    client = TestClient(app)

    response = client.post(
        "/api/test-plan/matrix-preview-from-path",
        json={"source_path": str(docx_path), "project_id": "P2"},
    )

    assert response.status_code == 200
    payload = response.json()
    group_1 = payload["groups"][0]
    step_1 = group_1["steps"][0]
    assert step_1["raw_token"] == "1(a)"
    assert step_1["source_note"] is not None
    assert "GS-12-2113" in step_1["source_note"]
    assert "Rev7.doc" in step_1["source_note"]


def test_matrix_preview_api_uses_last_contiguous_note_block_for_marker_mapping(tmp_path: Path) -> None:
    docx_path = tmp_path / "product-spec-note-block-scope.docx"
    _write_product_spec_docx_with_conflicting_note_blocks(docx_path)
    client = TestClient(app)

    response = client.post(
        "/api/test-plan/matrix-preview-from-path",
        json={"source_path": str(docx_path), "project_id": "P3"},
    )

    assert response.status_code == 200
    payload = response.json()
    group_1 = payload["groups"][0]
    notes_by_token = {step["raw_token"]: step.get("source_note") for step in group_1["steps"]}
    assert notes_by_token["3(a)"] == "(a) Precondition specimens with 20 durability cycles;"
    assert notes_by_token["10(c)"] == "(c) Energize at current for 18℃ temperature rise;"
    assert group_1["sample_note"] == "(e) Test with different 5 samples for solder ability and Resistance to solder heat, respectively"


def test_matrix_preview_api_rejects_test_record_like_docx(tmp_path: Path) -> None:
    docx_path = tmp_path / "test-record-like.docx"
    _write_test_record_like_docx(docx_path)
    client = TestClient(app)

    response = client.post(
        "/api/test-plan/matrix-preview-from-path",
        json={"source_path": str(docx_path), "project_id": "P4"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["groups"] == []
    assert payload["selected_table_index"] is None
    assert payload["capability_status"] == "unsupported"
    assert "No Matrix table" in payload["blockers"][0]


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


def _write_product_spec_docx_with_variant_note(path: Path) -> None:
    document = Document()
    table = document.add_table(rows=2, cols=3)
    rows = [
        ["test Items", "Section", "Group 1"],
        ["Examination", "5.5", "1(a)"],
    ]
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            table.cell(row_index, column_index).text = value
    document.add_paragraph(
        "a) C:\\Users\\White\\Desktop\\AI information\\Spec\\GS-12-2113 CoolPower HDF 3.40mm product specification_20251219_Rev7.doc"
    )
    document.save(path)


def _write_product_spec_docx_with_conflicting_note_blocks(path: Path) -> None:
    document = Document()
    table = document.add_table(rows=4, cols=3)
    rows = [
        ["test Items", "Section", "Group 1"],
        ["Durability", "8.11", "3(a)"],
        ["Vibration Random", "8.9", "10(c)"],
        ["Samples Quantity (PCS)", "", "5+(5e)"],
    ]
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            table.cell(row_index, column_index).text = value
    document.add_paragraph("(a) Precondition Category E Test")
    document.add_paragraph("(c) Minimum solder coverage: 95 %")
    document.add_paragraph("Table 5: Qualification Test Table")
    document.add_paragraph("Precondition specimens with 20 durability cycles;")
    document.add_paragraph("Precondition specimens with 212 hours high temperature life;")
    document.add_paragraph("Energize at current for 18℃ temperature rise;")
    document.add_paragraph("5pcs for LLCR test another 5pcs loose connector for DWV test.")
    document.add_paragraph("(e) Test with different 5 samples for solder ability and Resistance to solder heat, respectively")
    document.save(path)


def _write_test_record_like_docx(path: Path) -> None:
    document = Document()
    table = document.add_table(rows=4, cols=5)
    rows = [
        ["Test Item", "Requirement", "Result", "Judgement", "Record"],
        ["1", "As spec", "Pass", "OK", "notes"],
        ["2", "As spec", "Pass", "OK", "notes"],
        ["3", "As spec", "Pass", "OK", "notes"],
    ]
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            table.cell(row_index, column_index).text = value
    document.save(path)
