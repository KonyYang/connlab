from __future__ import annotations

from backend.api.main import app
from tests.integration.test_matrix_revision_flow_api import (
    _client,
    _seed_project,
    _seed_source_import,
)


def test_confirmed_matrix_authority_history_api_returns_empty_entries_without_history(tmp_path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        response = client.get("/api/projects/P1/confirmed-matrix/authority-history")
        assert response.status_code == 200
        payload = response.json()
        assert payload["project_id"] == "P1"
        assert payload["entries"] == []
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_confirmed_matrix_authority_history_api_returns_desc_history_with_recommendation(
    tmp_path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1", "g2"]},
        )
        assert created.status_code == 201
        base_draft_id = created.json()["record"]["project_matrix_draft_id"]

        confirmed_base = client.post(
            f"/api/projects/P1/matrix-drafts/{base_draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirmed_base.status_code == 201

        revision_create = client.post("/api/projects/P1/matrix-revisions")
        assert revision_create.status_code == 201
        revision_draft = revision_create.json()
        revision_draft_id = revision_draft["record"]["project_matrix_draft_id"]

        revised_cells = []
        for index, cell in enumerate(revision_draft["cells"]):
            revised = dict(cell)
            if index == 0:
                revised["cell_value"] = f"{cell['cell_value']}(a)"
            revised_cells.append(revised)

        save_revision = client.put(
            f"/api/projects/P1/matrix-drafts/{revision_draft_id}",
            json={
                "groups": revision_draft["groups"],
                "rows": revision_draft["rows"],
                "cells": revised_cells,
            },
        )
        assert save_revision.status_code == 200

        confirm_revision = client.post(
            f"/api/projects/P1/matrix-drafts/{revision_draft_id}/confirm-revision",
            json={"confirmed_by": "operator", "superseded_reason": "Update token"},
        )
        assert confirm_revision.status_code == 201

        response = client.get("/api/projects/P1/confirmed-matrix/authority-history")
        assert response.status_code == 200
        payload = response.json()
        assert payload["project_id"] == "P1"
        entries = payload["entries"]
        assert len(entries) == 2
        assert entries[0]["confirmed_revision"] == 2
        assert entries[1]["confirmed_revision"] == 1
        assert entries[0]["is_active_authority"] is True
        assert entries[1]["is_active_authority"] is False
        assert entries[0]["record_regeneration_recommended"] is True
        assert entries[1]["record_regeneration_recommended"] is True
        assert entries[0]["token_change_count"] > 0
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
