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


def import_manual_project(client, tmp_path, folder_name="DL-2026-01-002 Legacy connector"):
    destination = tmp_path / "projects"
    destination.mkdir(exist_ok=True)
    selected = client.post("/api/project-library/destination", json={"folder": str(destination)})
    assert selected.status_code == 200, selected.text
    source = tmp_path / "incoming" / folder_name
    source.mkdir(parents=True)
    (source / "evidence.txt").write_text("original evidence", encoding="utf-8")
    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    result = client.post("/api/project-library/batches", json={**{key: plan[key] for key in ("plan_id", "fingerprint")}, "selected": [str(source)]}).json()
    assert result["counts"]["added"] == 1, result
    member = client.get("/api/project-library/members/" + result["items"][0]["member_id"]).json()
    return member, source


def test_imported_project_recycle_retains_historical_identifier_files_and_identity(client, tmp_path):
    member, source = import_manual_project(client, tmp_path)
    project_id = member["project_id"]
    assert client.get(f"/api/projects/{project_id}").json()["library_member_id"] == member["member_id"]
    row = client.get("/api/projects/registry").json()[0]
    assert row["display_project_id"] == "DL-2026-01-002"
    assert row["has_registered_ltr"] is False
    removed = client.post(f"/api/project-registry/{project_id}/trash", json={"token": preview(client, project_id, "trash")["token"], "reason": "Imported by mistake"})
    assert removed.status_code == 200, removed.text
    retained = client.get("/api/project-registry/entries?location=trash").json()[0]
    assert retained["display_project_id"] == "DL-2026-01-002"
    assert retained["project_id"] == project_id
    assert retained["reason"] == "Imported by mistake"
    restored = client.post(f"/api/project-registry/{project_id}/restore", json={"token": preview(client, project_id, "restore")["token"]})
    assert restored.status_code == 200, restored.text
    assert restored.json()["project_id"] == project_id
    assert len(client.get("/api/projects/registry").json()) == 1
    assert (Path(member["folder_path"]) / source.name / "evidence.txt").read_text(encoding="utf-8") == "original evidence"
    assert (source / "evidence.txt").read_text(encoding="utf-8") == "original evidence"
    assert client.get(f"/api/projects/{project_id}/ltr").json() == []


def test_unnumbered_import_is_a_project_with_access_to_original_files(client, tmp_path):
    member, source = import_manual_project(client, tmp_path, "Unnumbered archive")
    project = client.get("/api/projects/" + member["project_id"]).json()
    assert project["library_member_id"] == member["member_id"]
    assert project["project_no"] is None
    rows = client.get("/api/projects/registry").json()
    assert len(rows) == 1 and rows[0]["project_id"] == member["project_id"]
    assert rows[0]["has_registered_ltr"] is False
    assert rows[0]["total_group_count"] is None
    files = client.get("/api/project-library/members/" + member["member_id"] + "/files").json()
    assert any(row["name"] == "evidence.txt" for row in files["items"])
    assert (source / "evidence.txt").read_text(encoding="utf-8") == "original evidence"


def test_restoring_imported_project_checks_registered_ltr_conflict(client, tmp_path, storage):
    member, _ = import_manual_project(client, tmp_path)
    project_id = member["project_id"]
    removed = client.post(f"/api/project-registry/{project_id}/trash", json={"token": preview(client, project_id, "trash")["token"], "reason": "Review later"})
    assert removed.status_code == 200
    current = create(client, "Current working project")
    register_number(storage, current)
    check = preview(client, project_id, "restore")
    assert [row["project_id"] for row in check["conflicts"]] == [current]
    blocked = client.post(f"/api/project-registry/{project_id}/restore", json={"token": check["token"]})
    assert blocked.status_code == 409
    assert client.get(f"/api/projects/{current}").json()["registry_state"] == "active"
    assert client.get(f"/api/projects/{project_id}").json()["registry_state"] == "trash"


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
