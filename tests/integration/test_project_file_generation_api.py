"""New transport plus the existing canonical write fences use isolated fixtures."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from backend.api import dependencies as deps
from backend.api.routes_project_file_generation import get_service, router
from backend.api.main import app
from backend.infrastructure.files.project_file_generation_journal import ProjectFileGenerationJournal
from backend.shared.config import Settings


def test_file_api_accepts_only_choices_and_server_tokens_and_returns_202():
    class Service:
        def start(self, project_id, request):
            return {"project_id": project_id, "request_id": request["request_id"]}
    isolated = FastAPI()
    isolated.include_router(router)
    isolated.dependency_overrides[get_service] = Service
    client = TestClient(isolated)
    payload = {"request_id": "r", "workspace_token": "trusted", "items": [
        {"key": "test_status", "source_token": "matrix", "action": "generate_missing"}]}
    assert client.post("/api/projects/p1/project-folder/files/start", json=payload).status_code == 202
    assert client.post("/api/projects/p1/project-folder/files/start", json={**payload, "target_path": "C:/arbitrary"}).status_code == 422


@pytest.mark.parametrize("status", ["queued", "running", "interrupted", "corrupted"])
@pytest.mark.parametrize("suffix", ["/project-folder/application-form/write-back", "/request-material/collect"])
def test_new_operation_fences_retained_writers_even_without_live_worker(tmp_path, status, suffix):
    settings = Settings(data_dir=tmp_path / "data", projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates", database_path=tmp_path / "fixture.sqlite")
    journal = ProjectFileGenerationJournal(settings.data_dir / "project_file_generation")
    state = journal.create("p1", "r", "signature", "workspace", [])
    if status == "corrupted":
        (journal.project_path("p1") / "operation.json").write_text("{}", encoding="utf-8")
    else:
        state["status"] = status
        journal.save(state)
    app.dependency_overrides[deps.get_settings] = lambda: settings
    try:
        response = TestClient(app, raise_server_exceptions=False).post("/api/projects/p1" + suffix)
        assert response.status_code == 409, response.text
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("suffix", ["open-local", "open-public"])
@pytest.mark.parametrize("live_lock", [False, True])
@pytest.mark.parametrize("registry_state", ["active", "trash"])
def test_folder_open_during_generation_preserves_registry_access_without_explorer(tmp_path, suffix, live_lock, registry_state):
    from contextlib import nullcontext
    from types import SimpleNamespace
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool
    from backend.application.project_folder_open_service import ProjectFolderOpenService, ProjectFolderOpenResult
    from backend.domain import Project
    from backend.infrastructure.files.generation_journal import GenerationJournal
    from backend.infrastructure.storage.database import Base, create_session_factory
    from backend.infrastructure.storage.repositories.project import ProjectRepository

    settings = Settings(data_dir=tmp_path / "data", database_path=tmp_path / "isolated.sqlite",
        projects_dir=tmp_path / "projects", templates_dir=tmp_path / "templates")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    with sessions() as session:
        ProjectRepository(session).create(Project(project_id="p1", project_no=None, product_name="Fixture", requestor="Tester", registry_state=registry_state))
        session.commit()
    def isolated_session():
        with sessions() as session:
            yield session
    journal = ProjectFileGenerationJournal(settings.data_dir / "project_file_generation")
    state = journal.create("p1", "r", "signature", "workspace", [])
    state["status"] = "interrupted"
    journal.save(state)
    opened = []
    def open_directory(path):
        opened.append(path)
        return ProjectFolderOpenResult("p1", "opened", "Opened", path)
    context = SimpleNamespace(local_official_folder_path=tmp_path / "local", public_open_path=tmp_path / "public")
    service = ProjectFolderOpenService(workflow_service=SimpleNamespace(context=lambda _: context),
        gateway=SimpleNamespace(open_directory=open_directory))
    app.dependency_overrides[deps.get_settings] = lambda: settings
    app.dependency_overrides[deps.get_session] = isolated_session
    app.dependency_overrides[deps.get_project_folder_open_service] = lambda: service
    try:
        lock = GenerationJournal(settings.data_dir / "project_folder_generation").lock("p1") if live_lock else nullcontext()
        with lock:
            response = TestClient(app).post(f"/api/projects/p1/folder/{suffix}")
        if registry_state == "active":
            assert response.status_code == 200, response.text
            assert opened == [tmp_path / ("local" if suffix == "open-local" else "public")]
        else:
            assert response.status_code == 409, response.text
            assert response.json()["detail"]["code"] == "project_registry_read_only"
            assert opened == []
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
