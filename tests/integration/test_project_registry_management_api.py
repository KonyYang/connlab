"""Isolated HTTP workflow for local project registry and conditional closure."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.infrastructure.storage.database import init_db, create_session_factory
from backend.shared.config import Settings
from backend.domain import LtrRecord, LtrStatus
from backend.infrastructure.storage.repositories import LtrRecordRepository


@pytest.fixture
def storage():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    init_db(engine)
    sessions = create_session_factory(engine)
    yield sessions
    engine.dispose()


@pytest.fixture
def client(tmp_path, storage):
    def session_override():
        with storage() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
    settings = Settings(data_dir=tmp_path / "data", projects_dir=tmp_path / "projects",
                        templates_dir=tmp_path / "templates", database_path=tmp_path / "unused.db")
    app.dependency_overrides[get_session] = session_override
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def create(client, name="Sample"):
    response = client.post("/api/projects", json={"project_no": "DL-2026-01-002", "product_name": name, "requestor": "User"})
    assert response.status_code == 201, response.text
    return response.json()["project_id"]


def preview(client, project_id, action):
    result = client.get(f"/api/project-registry/{project_id}/preview", params={"action": action})
    assert result.status_code == 200, result.text
    return result.json()


def test_trash_restore_conflict_and_readonly_detail_are_consistent(client, storage):
    old = create(client, "Original sample")
    register_number(storage, old)
    token = preview(client, old, "trash")["token"]
    response = client.post(f"/api/project-registry/{old}/trash", json={"token": token, "reason": "Mistake"})
    assert response.status_code == 200, response.text
    assert client.get("/api/projects").json() == []
    assert client.get("/api/projects/registry").json() == []
    assert client.get(f"/api/projects/{old}").json()["registry_state"] == "trash"
    lifecycle = client.get(f"/api/projects/{old}/lifecycle").json()
    assert lifecycle["registry_state"] == "trash"
    assert lifecycle["readonly"] is True
    assert lifecycle["allowed_actions"] == []
    assert client.get("/api/project-registry/entries?location=trash").json()[0]["project_id"] == old
    new = create(client, "New sample")
    register_number(storage, new)
    restore = preview(client, old, "restore")
    assert restore["conflicts"][0]["project_id"] == new
    blocked = client.post(f"/api/project-registry/{old}/restore", json={"token": restore["token"]})
    assert blocked.status_code == 409
    restored = client.post(f"/api/project-registry/{old}/restore", json={
        "token": restore["token"], "destination": "active", "replace_conflicts": True})
    assert restored.status_code == 200, restored.text
    assert [p["project_id"] for p in client.get("/api/projects").json()] == [old]
    assert client.get(f"/api/projects/{new}").json()["product_name"] == "New sample"
    assert client.get("/api/project-registry/entries?location=history").json()[0]["project_id"] == new


def register_number(storage, project_id):
    with storage() as session:
        LtrRecordRepository(session).create(LtrRecord(
            ltr_id="ltr-"+project_id, project_id=project_id, ltr_number="DL-2026-01-002",
            status=LtrStatus.REGISTERED, is_current_owner=False))
        session.commit()


@pytest.mark.parametrize("reason", ["completed", "cancelled", "cannot_test"])
def test_explicit_closure_reason_accepts_omitted_note(client, reason):
    project_id = create(client)
    response = client.post(f"/api/projects/{project_id}/lifecycle/close", json={"reason_category": reason})
    assert response.status_code == 200, response.text
    assert response.json()["closed_reason"] == ""
    assert response.json()["close_reason_category"] == reason


def test_other_reason_requires_note_and_unselected_reason_cannot_close(client):
    project_id = create(client)
    assert client.post(f"/api/projects/{project_id}/lifecycle/close", json={"reason_category": "other"}).status_code == 409
    assert client.post(f"/api/projects/{project_id}/lifecycle/close", json={"note": "Done"}).status_code == 422
    assert client.get(f"/api/projects/{project_id}/lifecycle").json()["lifecycle_state"] == "active"


def test_hidden_project_readonly_details_keep_temporary_intake_context(client):
    created = client.post("/api/projects/temporary", json={
        "request_summary": "Trial", "sample_description": "Connector-X", "test_item": "Vibration",
        "requestor": "User", "source_asset_ids": ["fixture-source"], "notes": "Keep original source"})
    assert created.status_code == 201, created.text
    project_id = created.json()["project_id"]
    moved = client.post(f"/api/project-registry/{project_id}/trash", json={
        "token": preview(client, project_id, "trash")["token"], "reason": "Mistake"})
    assert moved.status_code == 200, moved.text
    detail = client.get(f"/api/projects/{project_id}").json()
    assert detail["sample_description"] == "Connector-X"
    assert detail["test_item"] == "Vibration"
    assert detail["temporary_source_asset_ids"] == ["fixture-source"]
    assert detail["temporary_notes"] == "Keep original source"


@pytest.mark.parametrize("reason", ["failed", "duplicate"])
def test_new_close_api_rejects_legacy_reason(client, reason):
    project_id = create(client)
    response = client.post(f"/api/projects/{project_id}/lifecycle/close", json={"reason_category": reason, "note": "Legacy"})
    assert response.status_code == 409, response.text
    assert client.get(f"/api/projects/{project_id}/lifecycle").json()["lifecycle_state"] == "active"
