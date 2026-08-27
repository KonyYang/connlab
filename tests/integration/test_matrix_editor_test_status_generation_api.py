from __future__ import annotations

from io import BytesIO
from pathlib import Path

from openpyxl import load_workbook

from backend.api.main import app
from tests.integration.test_confirmed_matrix_test_record_preview_api import (
    _client,
    _seed_project,
)


def test_matrix_editor_test_status_generation_uses_current_ui_payload(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        response = client.post(
            "/api/projects/P1/matrix-editor/test-status-draft/generate",
            json={
                "source": "matrix_editor_current_ui_state",
                "project_reference": "DL-2026-08-004",
                "groups": [
                    {
                        "group_key": "g1",
                        "group_label": "1",
                        "sample_quantity_expression": "5+5(d)",
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
                        "group_values": {"g1": "1,8"},
                    }
                ],
            },
        )

        assert response.status_code == 200
        assert (
            "DL-2026-08-004%20test%20status.xlsx"
            in response.headers["content-disposition"]
        )
        workbook = load_workbook(BytesIO(response.content), data_only=False)
        sheet = workbook["Test Status"]
        assert sheet["A2"].value == "Unsaved Visual Check"
        assert sheet["B2"].value == "1,8"
        assert sheet["B3"].value == "5+5(d)"
        assert sheet["B4"].value is None
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
