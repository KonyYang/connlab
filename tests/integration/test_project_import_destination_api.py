"""First-use import location uses the instance's Settings, never a new database."""
from pathlib import Path
from dataclasses import replace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.routes_project_library import router
from backend.domain import ExternalResource, ExternalResourceType
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.repositories import ExternalResourceRepository
from backend.shared.config import Settings


@pytest.fixture
def instance(tmp_path):
    settings = Settings(tmp_path / "Data", tmp_path / "unused-default", tmp_path / "Templates", tmp_path / "Data/connlab.sqlite3")
    settings.ensure_directories()
    engine = create_engine(f"sqlite:///{settings.database_path}", connect_args={"check_same_thread": False})
    init_db(engine)
    app = FastAPI()
    app.include_router(router)

    def session_override():
        with Session(engine) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = session_override
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as client:
        yield client, settings, engine
    engine.dispose()


def test_existing_settings_save_location_enables_import_without_relocating_database(instance, tmp_path):
    client, settings, engine = instance
    destination = tmp_path / "Existing project folder"
    destination.mkdir()
    with Session(engine) as session:
        ExternalResourceRepository(session).upsert(ExternalResource(
            resource_id="project-location", resource_type=ExternalResourceType.PROJECT_OUTPUT_ROOT,
            path=destination, active=True,
        ))
        session.commit()
    runtime = client.get("/api/project-library/runtime").json()
    assert runtime["configured"] is True
    assert Path(runtime["projects_root"]) == destination
    assert Path(runtime["database_path"]) == settings.database_path
    assert Path(runtime["data_root"]) == settings.data_dir
    assert not (destination / "Data").exists()


def test_first_use_saves_location_then_requires_final_confirmation_before_copy(instance, tmp_path):
    client, settings, _ = instance
    before = client.get("/api/project-library/runtime").json()
    assert before["configured"] is False
    destination = tmp_path / "Projects Dev"
    destination.mkdir()
    saved = client.post("/api/project-library/destination", json={"folder": str(destination)})
    assert saved.status_code == 200, saved.text
    assert saved.json()["configured"] is True
    assert saved.json()["database_path"] == before["database_path"]
    assert saved.json()["data_root"] == before["data_root"]

    source = tmp_path / "USB" / "DL-2021-01-030A1 Old project"
    source.mkdir(parents=True)
    (source / "notes.txt").write_text("Original measurements", encoding="utf-8")
    review = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]})
    assert review.status_code == 200, review.text
    plan = review.json()
    assert plan["items"][0]["status"] == "ready"
    assert Path(plan["projects_root"]) == destination
    assert not list(destination.iterdir())
    assert client.get("/api/project-library/members").json()["items"] == []
    received = client.post("/api/project-library/batches", json={
        **{key: plan[key] for key in ("plan_id", "fingerprint")}, "selected": [str(source)],
    })
    assert received.status_code == 200, received.text
    assert received.json()["counts"]["added"] == 1
    member = client.get("/api/project-library/members").json()["items"][0]
    assert member["ltr_number"] == "DL-2021-01-030A1"
    assert Path(member["folder_path"]).is_relative_to(destination)
    assert (Path(member["folder_path"]) / "notes.txt").read_text(encoding="utf-8") == "Original measurements"
    assert (source / "notes.txt").read_text(encoding="utf-8") == "Original measurements"
    assert client.get("/api/project-library/runtime").json()["database_path"] == str(settings.database_path)


@pytest.mark.parametrize("invalid", ["missing", "file", "relative", "data"])
def test_unusable_location_is_not_saved(instance, tmp_path, invalid):
    client, settings, _ = instance
    file = tmp_path / "not-a-folder.txt"
    file.write_text("keep", encoding="utf-8")
    path = {"missing": str(tmp_path / "missing"), "file": str(file), "relative": "projects", "data": str(settings.data_dir)}[invalid]
    response = client.post("/api/project-library/destination", json={"folder": path})
    assert response.status_code == 409, response.text
    assert client.get("/api/project-library/runtime").json()["configured"] is False
    assert file.read_text(encoding="utf-8") == "keep"


def test_changed_destination_invalidates_previous_import_confirmation(instance, tmp_path):
    client, _, _ = instance
    first, second = tmp_path / "First", tmp_path / "Second"
    first.mkdir()
    second.mkdir()
    source = tmp_path / "DL-2026-10-001 Project"
    source.mkdir()
    (source / "record.txt").write_text("original", encoding="utf-8")
    assert client.post("/api/project-library/destination", json={"folder": str(first)}).status_code == 200
    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    assert client.post("/api/project-library/destination", json={"folder": str(second)}).status_code == 200
    stale = client.post("/api/project-library/batches", json={
        **{key: plan[key] for key in ("plan_id", "fingerprint")}, "selected": [str(source)],
    })
    assert stale.status_code == 409, stale.text
    assert not list(first.iterdir()) and not list(second.iterdir())
    assert client.get("/api/project-library/members").json()["items"] == []


def test_managed_library_keeps_its_explicit_storage_binding(instance, tmp_path):
    client, settings, _ = instance
    client.app.dependency_overrides[get_settings] = lambda: replace(settings, library_root=tmp_path)
    runtime = client.get("/api/project-library/runtime").json()
    assert runtime["configured"] is True and runtime["destination_editable"] is False
    other = tmp_path / "Other"
    other.mkdir()
    assert client.post("/api/project-library/destination", json={"folder": str(other)}).status_code == 409
    assert client.get("/api/project-library/runtime").json()["projects_root"] == str(settings.projects_dir)


def test_open_location_uses_only_the_registered_server_path(instance, tmp_path, monkeypatch):
    client, _, _ = instance
    from backend.infrastructure.files.local_folder_open_gateway import LocalFolderOpenGateway
    opened = []
    monkeypatch.setattr(LocalFolderOpenGateway, "open_directory", lambda self, path: opened.append(path))
    assert client.post("/api/project-library/open-destination").status_code == 409
    destination = tmp_path / "Selected destination"
    destination.mkdir()
    assert client.post("/api/project-library/destination", json={"folder": str(destination)}).status_code == 200
    response = client.post("/api/project-library/open-destination", json={"folder": "D:/untrusted-client-path"})
    assert response.status_code == 200, response.text
    assert opened == [destination]


def test_failed_folder_open_is_not_reported_as_opened(instance, tmp_path, monkeypatch):
    from types import SimpleNamespace
    from backend.infrastructure.files.local_folder_open_gateway import LocalFolderOpenGateway
    client, _, _ = instance
    destination = tmp_path / "Projects"
    destination.mkdir()
    assert client.post("/api/project-library/destination", json={"folder": str(destination)}).status_code == 200
    monkeypatch.setattr(LocalFolderOpenGateway, "open_directory", lambda self, path: SimpleNamespace(status="blocked", message="Access was denied."))
    result = client.post("/api/project-library/open-destination")
    assert result.status_code == 200, result.text
    assert result.json() == {"status": "blocked", "message": "Access was denied."}


def test_resume_cannot_copy_to_a_previous_destination(instance, tmp_path, monkeypatch):
    client, _, _ = instance
    from backend.infrastructure.project_library import files
    second = tmp_path / "Destination"
    first = second / "Old location"
    first.mkdir(parents=True)
    source = tmp_path / "DL-2026-10-002 Project"
    source.mkdir()
    (source / "record.txt").write_text("original", encoding="utf-8")
    assert client.post("/api/project-library/destination", json={"folder": str(first)}).status_code == 200
    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    original_copy = files.copy_verified
    def unavailable(*args):
        raise OSError("Temporary copy failure")
    monkeypatch.setattr(files, "copy_verified", unavailable)
    failed = client.post("/api/project-library/batches", json={
        **{key: plan[key] for key in ("plan_id", "fingerprint")}, "selected": [str(source)],
    }).json()
    assert failed["status"] == "interrupted", failed
    monkeypatch.setattr(files, "copy_verified", original_copy)
    assert client.post("/api/project-library/destination", json={"folder": str(second)}).status_code == 200
    resumed = client.post(f"/api/project-library/batches/{failed['batch_id']}/resume")
    assert resumed.status_code == 409, resumed.text
    assert not list(first.iterdir())
    assert client.get("/api/project-library/members").json()["items"] == []
