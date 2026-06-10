from __future__ import annotations

from pathlib import Path

from docx import Document

from backend.api.dependencies import get_settings
from backend.api.main import app
from backend.shared.config import Settings, TestRecordSettings
from tests.integration.test_confirmed_matrix_test_record_generation_api import (
    _build_template,
    _seed_header_metadata_sources,
)
from tests.integration.test_confirmed_matrix_test_record_preview_api import (
    _client,
    _seed_project,
)


def test_matrix_editor_test_record_generation_uses_current_ui_payload(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        template_path = _build_template(tmp_path / "template.docx")
        app.dependency_overrides[get_settings] = lambda: Settings(
            data_dir=tmp_path / "data",
            projects_dir=tmp_path / "projects",
            templates_dir=tmp_path / "templates",
            database_path=tmp_path / "connlab.sqlite3",
            test_record=TestRecordSettings(template_path=template_path),
        )
        _seed_project("P1", tmp_path)
        _seed_header_metadata_sources("P1", tmp_path)

        response = client.post(
            "/api/projects/P1/matrix-editor/test-record-draft/generate",
            json={
                "source": "matrix_editor_current_ui_state",
                "groups": [
                    {
                        "group_key": "g1",
                        "group_label": "1",
                        "sample_quantity_expression": "7",
                    }
                ],
                "rows": [
                    {
                        "test_item": "Unsaved Visual Check",
                        "section": "9.9",
                        "method": "Unsaved method from UI",
                        "condition": "Unsaved condition from UI",
                        "requirement": "Unsaved requirement from UI",
                        "is_sample_row": False,
                        "group_values": {"g1": "1"},
                    }
                ],
            },
        )

        assert response.status_code == 200
        assert "Preview" in response.headers["content-disposition"]
        assert "Unconfirmed" in response.headers["content-disposition"]
        output = tmp_path / "downloaded-preview.docx"
        output.write_bytes(response.content)
        document = Document(output)
        body_text = "\n".join(
            cell.text for table in document.tables for row in table.rows for cell in row.cells
        )
        assert "Unsaved Visual Check" in body_text
        assert "Unsaved method from UI" in body_text
        assert "Unsaved condition from UI" in body_text
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_editor_test_record_generation_rejects_wrong_source(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        response = client.post(
            "/api/projects/P1/matrix-editor/test-record-draft/generate",
            json={"source": "saved_draft", "groups": [], "rows": []},
        )
        assert response.status_code == 422
        assert response.json()["detail"] == (
            "Matrix Editor Test Record preview requires current UI state payload."
        )
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
