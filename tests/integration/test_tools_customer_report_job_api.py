from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend.api import dependencies as deps
from backend.api.main import app
from backend.shared.config import Settings


class _TemplateStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def get_by_type(self, _resource_type):
        return SimpleNamespace(active=True, path=self._path)


class _Jobs:
    def __init__(self) -> None:
        self.started = None

    def start(self, **kwargs):
        self.started = kwargs
        return {
            "operation_id": "job-1",
            "status": "queued",
            "stage": "queued",
            "elapsed_seconds": 0,
            "message": None,
        }

    def read(self, operation_id: str):
        assert operation_id == "job-1"
        return {
            "operation_id": operation_id,
            "status": "running",
            "stage": "cleaning_content",
            "elapsed_seconds": 12.5,
            "message": None,
        }


def test_customer_report_job_start_returns_before_generation_and_can_be_polled(
    tmp_path: Path,
) -> None:
    data = tmp_path / "data"
    templates = tmp_path / "templates"
    projects = tmp_path / "projects"
    data.mkdir()
    templates.mkdir()
    projects.mkdir()
    (templates / "E-4515_F.docx").write_bytes(b"template")
    settings = Settings(
        data_dir=data,
        templates_dir=templates,
        projects_dir=projects,
        database_path=tmp_path / "fixture.sqlite",
    )
    jobs = _Jobs()
    app.dependency_overrides[deps.get_settings] = lambda: settings
    app.dependency_overrides[deps.get_test_report_template_resource_store] = (
        lambda: _TemplateStore(templates)
    )
    app.dependency_overrides[deps.get_tools_customer_report_job_service] = lambda: jobs
    try:
        client = TestClient(app)
        started = client.post(
            "/api/tools/customer-report/jobs",
            files={"file": ("internal.docx", b"source", "application/octet-stream")},
        )
        status = client.get("/api/tools/customer-report/jobs/job-1")
    finally:
        app.dependency_overrides.pop(deps.get_settings, None)
        app.dependency_overrides.pop(deps.get_test_report_template_resource_store, None)
        app.dependency_overrides.pop(deps.get_tools_customer_report_job_service, None)

    assert started.status_code == 202, started.text
    assert started.json()["status"] == "queued"
    assert jobs.started is not None
    assert jobs.started["source_path"].read_bytes() == b"source"
    assert status.status_code == 200, status.text
    assert status.json()["stage"] == "cleaning_content"
    assert status.json()["elapsed_seconds"] == 12.5
