from __future__ import annotations

from pathlib import Path

from docx import Document

from backend.api.main import app
from tests.integration.test_confirmed_matrix_test_record_preview_api import (
    _client,
    _seed_project,
    _seed_source_import,
)


def test_confirmed_matrix_test_record_generation_api_downloads_docx(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        draft = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1"]},
        )
        draft_id = draft.json()["record"]["project_matrix_draft_id"]
        confirm = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirm.status_code == 201

        response = client.post("/api/projects/P1/confirmed-matrix/test-record-draft/generate")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        output = tmp_path / "downloaded.docx"
        output.write_bytes(response.content)
        document = Document(output)
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        table_text = "\n".join(
            cell.text for table in document.tables for row in table.rows for cell in row.cells
        )
        assert "ConnLab Test Record Draft" in text
        assert "Product Description: Connector" in text
        assert "Group Number: G1" in text
        assert "Sample Quantity & Number: 5" in text
        assert "Visual" in table_text
        assert "LLCR" in table_text
        assert "G2" not in text
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_confirmed_matrix_test_record_generation_api_returns_404_without_active_matrix(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        response = client.post("/api/projects/P1/confirmed-matrix/test-record-draft/generate")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
