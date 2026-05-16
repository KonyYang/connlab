from __future__ import annotations

from fastapi.testclient import TestClient

from backend.api.main import app


def test_runtime_projection_read_only_snapshot_returns_deterministic_payload() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/runtime-projection/read-only-snapshot",
        json={
            "project_reference": "P-001",
            "matrix_reference": "M-001",
            "rows": [
                {
                    "group_identity": "G1",
                    "group_label": "Group 1",
                    "row_context": {
                        "test_item_label": "LLCR",
                        "section": "6.1",
                        "method": "EIA-364-23E",
                        "condition": "20mV max",
                        "requirement": "Initial <= 0.40mO",
                    },
                    "raw_step_token_value": "2,3(a)",
                    "projection_state": {
                        "lifecycle": "in_progress",
                        "evidence": "missing",
                        "report_sync": "stale",
                        "stale": "stale",
                        "attention": "p1",
                    },
                },
                {
                    "group_identity": "G2",
                    "group_label": "Group 2",
                    "row_context": {
                        "test_item_label": "CR",
                        "section": "6.2",
                        "method": "EIA-364-06",
                        "condition": "1A max",
                        "requirement": "See spec",
                    },
                    "raw_step_token_value": "2",
                },
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_reference"] == "P-001"
    assert payload["matrix_reference"] == "M-001"
    assert payload["runtime_projection_summary"]["total_tokens"] == 3
    assert payload["matrix_overview"]["group_count"] == 2
    assert payload["step_workspace"] is None


def test_runtime_projection_read_only_snapshot_selected_token_and_warning() -> None:
    client = TestClient(app)
    seed = client.post(
        "/api/runtime-projection/read-only-snapshot",
        json={
            "project_reference": "P-001",
            "matrix_reference": "M-001",
            "rows": [
                {
                    "group_identity": "G1",
                    "group_label": "Group 1",
                    "row_context": {
                        "test_item_label": "LLCR",
                        "section": "6.1",
                        "method": "EIA-364-23E",
                        "condition": "20mV max",
                        "requirement": "Initial <= 0.40mO",
                    },
                    "raw_step_token_value": "2, A",
                }
            ],
        },
    )
    assert seed.status_code == 200
    selected_reference = seed.json()["matrix_overview"]["groups"][0]["tokens"][0][
        "token_reference"
    ]

    response = client.post(
        "/api/runtime-projection/read-only-snapshot",
        json={
            "project_reference": "P-001",
            "matrix_reference": "M-001",
            "selected_token_reference": selected_reference,
            "rows": [
                {
                    "group_identity": "G1",
                    "group_label": "Group 1",
                    "row_context": {
                        "test_item_label": "LLCR",
                        "section": "6.1",
                        "method": "EIA-364-23E",
                        "condition": "20mV max",
                        "requirement": "Initial <= 0.40mO",
                    },
                    "raw_step_token_value": "2, A",
                }
            ],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "Unrecognized step token: 'A'." in payload["parser_warnings"]
    assert payload["step_workspace"] is not None
    assert payload["step_workspace"]["found"] is True
    assert payload["step_workspace"]["selected_token"]["token_reference"] == selected_reference
