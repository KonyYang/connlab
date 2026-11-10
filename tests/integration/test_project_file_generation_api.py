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
