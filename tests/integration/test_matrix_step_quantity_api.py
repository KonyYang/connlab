from __future__ import annotations

from pathlib import Path

from tests.integration.test_confirmed_matrix_authority_api import (
    _client,
    _seed_project,
    _seed_source_import,
)


def test_retired_matrix_step_quantity_api_is_not_exposed(tmp_path: Path) -> None:
    client, engine, _session_factory = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1"]},
        )
        assert created.status_code == 201
        draft_id = created.json()["record"]["project_matrix_draft_id"]
        endpoint = f"/api/projects/P1/matrix-drafts/{draft_id}/step-quantities"

        assert client.get(endpoint).status_code == 404
        assert client.put(endpoint, json={"items": []}).status_code == 404
    finally:
        engine.dispose()
