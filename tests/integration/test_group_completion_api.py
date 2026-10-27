from pathlib import Path
from dataclasses import replace

from backend.api.main import app
from tests.integration.test_confirmed_matrix_authority_api import _fill_matrix_dates
from tests.integration.test_confirmed_matrix_runtime_projection_api import _client, _seed_project, _seed_source_import


def test_mark_and_revoke_group_completion_visible_in_registry(tmp_path: Path):
    client, engine, sessions = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_id = _seed_source_import("P1", tmp_path)
        draft = client.post("/api/projects/P1/matrix-drafts", json={"source_import_id": source_id, "selected_group_keys": ["g1"]}).json()["record"]["project_matrix_draft_id"]
        _fill_matrix_dates(client, draft)
        confirmation = client.post(f"/api/projects/P1/matrix-drafts/{draft}/confirm", json={"confirmed_by": "operator"}).json()
        matrix_id = confirmation["version"]["confirmed_matrix_id"]
        response = client.get("/api/projects/P1/group-completion")
        assert response.status_code == 200
        assert response.json()["completed_count"] == 0
        assert response.json()["total_count"] == 1
        marked = client.put("/api/projects/P1/group-completion/g1", json={"confirmed_matrix_id": matrix_id, "completed": True})
        assert marked.status_code == 200
        assert marked.json()["completed_count"] == 1
        registry = client.get("/api/projects/registry").json()[0]
        assert registry["completed_group_count"] == 1
        assert registry["total_group_count"] == 1
        stale = client.put("/api/projects/P1/group-completion/g1", json={"confirmed_matrix_id": "outdated", "completed": False})
        assert stale.status_code == 409
        assert client.get("/api/projects/P1/group-completion").json()["completed_count"] == 1
        revoked = client.put("/api/projects/P1/group-completion/g1", json={"confirmed_matrix_id": matrix_id, "completed": False})
        assert revoked.status_code == 200
        assert revoked.json()["completed_count"] == 0
        from backend.application.group_completion_service import GroupCompletionService
        from backend.infrastructure.storage.repositories.confirmed_matrix_authority import ConfirmedMatrixAuthorityRepository
        from backend.infrastructure.storage.repositories.group_completion import GroupCompletionRepository
        with sessions() as session:
            original = ConfirmedMatrixAuthorityRepository(session).get(matrix_id)
            reimported = replace(original, version=replace(original.version, confirmed_revision=2), groups=(replace(original.groups[0], source_group_snapshot_id="other-source"),))
            class Matrices:
                def get_active_by_project(self, project_id): return reimported
                def list_by_project(self, project_id): return (original, reimported)
            status = GroupCompletionService(Matrices(), GroupCompletionRepository(session), lambda _: None, lambda: "now").read("P1")
            assert status["groups"][0]["needs_review"] is False
        assert client.post("/api/projects/P1/lifecycle/stop", json={"reason": "Paused"}).status_code == 200
        blocked = client.put("/api/projects/P1/group-completion/g1", json={"confirmed_matrix_id": matrix_id, "completed": True})
        assert blocked.status_code == 409
        assert client.get("/api/projects/P1/group-completion").json()["completed_count"] == 0
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_changed_group_does_not_regain_completion_if_later_reverted(tmp_path: Path):
    from backend.application.group_completion_service import GroupCompletionService
    from backend.infrastructure.storage.repositories.confirmed_matrix_authority import ConfirmedMatrixAuthorityRepository
    from backend.infrastructure.storage.repositories.group_completion import GroupCompletionRepository
    client, engine, sessions = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_id = _seed_source_import("P1", tmp_path)
        draft = client.post("/api/projects/P1/matrix-drafts", json={"source_import_id": source_id, "selected_group_keys": ["g1"]}).json()["record"]["project_matrix_draft_id"]
        _fill_matrix_dates(client, draft)
        result = client.post(f"/api/projects/P1/matrix-drafts/{draft}/confirm", json={"confirmed_by": "operator"}).json()
        matrix_id = result["version"]["confirmed_matrix_id"]
        assert client.put("/api/projects/P1/group-completion/g1", json={"confirmed_matrix_id": matrix_id, "completed": True}).status_code == 200
        with sessions() as session:
            first = ConfirmedMatrixAuthorityRepository(session).get(matrix_id)
            changed = replace(first, version=replace(first.version, confirmed_revision=2),
                              rows=(replace(first.rows[0], condition="Changed condition"), *first.rows[1:]))
            reverted = replace(first, version=replace(first.version, confirmed_revision=3))
            class Matrices:
                def get_active_by_project(self, project_id): return reverted
                def list_by_project(self, project_id): return (first, changed, reverted)
            service = GroupCompletionService(Matrices(), GroupCompletionRepository(session), lambda _: None, lambda: "now")
            state = service.read("P1")
            assert state["completed_count"] == 0
            assert state["groups"][0]["needs_review"] is True
            class UnchangedMatrices:
                def get_active_by_project(self, project_id): return reverted
                def list_by_project(self, project_id): return (first, replace(first, version=replace(first.version, confirmed_revision=2)), reverted)
            unchanged_service = GroupCompletionService(UnchangedMatrices(), GroupCompletionRepository(session), lambda _: None, lambda: "now")
            assert unchanged_service.read("P1")["completed_count"] == 1
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_completion_survives_date_only_matrix_revision(tmp_path: Path):
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_id = _seed_source_import("P1", tmp_path)
        draft = client.post("/api/projects/P1/matrix-drafts", json={"source_import_id": source_id, "selected_group_keys": ["g1"]}).json()["record"]["project_matrix_draft_id"]
        _fill_matrix_dates(client, draft)
        first = client.post(f"/api/projects/P1/matrix-drafts/{draft}/confirm", json={"confirmed_by": "operator"}).json()
        matrix_id = first["version"]["confirmed_matrix_id"]
        assert client.put("/api/projects/P1/group-completion/g1", json={"confirmed_matrix_id": matrix_id, "completed": True}).status_code == 200
        revision = client.post("/api/projects/P1/matrix-revisions").json()
        revision_id = revision["record"]["project_matrix_draft_id"]
        saved = client.put(f"/api/projects/P1/matrix-drafts/{revision_id}", json={
            "post_test_buffer_days": "0", "planned_test_start_date": "2026-06-02",
            "planned_test_complete_date": "2026-06-04", "estimated_completion_date": "2026-06-04",
            "groups": revision["groups"], "rows": revision["rows"], "cells": revision["cells"],
        })
        assert saved.status_code == 200, saved.text
        revised = client.post(f"/api/projects/P1/matrix-drafts/{revision_id}/confirm-revision", json={"confirmed_by": "operator", "superseded_reason": "Dates"})
        assert revised.status_code == 201, revised.text
        assert client.get("/api/projects/P1/group-completion").json()["completed_count"] == 1
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_other_group_point_changes_do_not_clear_completed_group(tmp_path: Path):
    from backend.application.group_completion_service import GroupCompletionService
    from backend.domain.matrix_contact_measurement_models import MatrixStepPointCategory, MatrixStepPointOverride
    from backend.infrastructure.storage.repositories.confirmed_matrix_authority import ConfirmedMatrixAuthorityRepository
    from backend.infrastructure.storage.repositories.group_completion import GroupCompletionRepository
    client, engine, sessions = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_id = _seed_source_import("P1", tmp_path)
        draft = client.post("/api/projects/P1/matrix-drafts", json={"source_import_id": source_id, "selected_group_keys": ["g1", "g2"]}).json()["record"]["project_matrix_draft_id"]
        _fill_matrix_dates(client, draft)
        first = client.post(f"/api/projects/P1/matrix-drafts/{draft}/confirm", json={"confirmed_by": "operator"}).json()
        matrix_id = first["version"]["confirmed_matrix_id"]
        assert client.put("/api/projects/P1/group-completion/g1", json={"confirmed_matrix_id": matrix_id, "completed": True}).status_code == 200
        with sessions() as session:
            original = ConfirmedMatrixAuthorityRepository(session).get(matrix_id)
            second_group = next(group for group in original.groups if group.group_key == "g2")
            override = MatrixStepPointOverride(draft_group_id=second_group.draft_group_id,
                draft_row_id=original.rows[0].draft_row_id, step_sequence=1, step_suffix_note="",
                categories=(MatrixStepPointCategory(prefix="HP", point_expression="1,2"),))
            revised = replace(original, version=replace(original.version, confirmed_revision=2, point_overrides=(override,)))
            class Matrices:
                def get_active_by_project(self, project_id): return revised
                def list_by_project(self, project_id): return (original, revised)
            service = GroupCompletionService(Matrices(), GroupCompletionRepository(session), lambda _: None, lambda: "now")
            assert service.read("P1")["completed_count"] == 1
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
