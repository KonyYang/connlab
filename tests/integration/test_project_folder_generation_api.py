from pathlib import Path
from dataclasses import replace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from backend.api import dependencies as deps
from backend.api.main import app
from backend.api.project_folder_generation_composition import ProjectFolderGenerationRunner
from backend.domain import Project, ProjectStatus, ExternalResource, ExternalResourceType, LtrRecord, LtrStatus, ProjectLifecycleState
from backend.infrastructure.storage.database import Base, create_session_factory
from backend.shared.config import Settings


def test_real_context_and_routes_start_continue_after_request_and_reconnect(tmp_path):
    settings = Settings(data_dir=tmp_path / "data", projects_dir=tmp_path / "projects", templates_dir=tmp_path / "templates",
                        database_path=tmp_path / "fixture.sqlite")
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    template, destination = tmp_path / "template", tmp_path / "output"
    destination.mkdir()
    for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
        (template / name).mkdir(parents=True)
    (template / "template.txt").write_text("fixture", encoding="utf-8")
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(project_id="P1", project_no="DL-001", product_name="Connector",
                                                     requestor="Test", status=ProjectStatus.DRAFT))
        deps.LtrRecordRepository(session).create(LtrRecord(ltr_id="ltr", project_id="P1", ltr_number="DL-001", status=LtrStatus.REGISTERED))
        resources = deps.ExternalResourceRepository(session)
        resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, destination))
        resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    service = runner.service()
    queued = []
    service.dispatch = queued.append
    app.dependency_overrides[deps.get_project_folder_generation_service] = lambda: service
    try:
        client = TestClient(app)
        url = "/api/projects/P1/project-folder/generation"
        assert client.get(url).json() is None
        before_context = runner.context("P1")
        preview = client.get(url + "/preview")
        assert preview.status_code == 200, preview.text
        body = {**preview.json(), "request_id": "request-one"}
        stale = client.post(url + "/start", json={**body, "expected_context": "stale"})
        assert stale.status_code == 409
        started = client.post(url + "/start", json=body)
        assert started.status_code == 202, started.text
        assert client.get(url).json()["status"] == "queued"
        queued.pop()()  # A backend callback; no browser write drives continuation.
        result = client.get(url).json()
        assert result["status"] == "blocked"  # Fixture deliberately has no Application Form.
        assert result["completed_steps"] == ["workspace"], result
        assert runner.context("P1") == before_context  # Own folder/index are not source authority.
        with sessions() as session:
            workspace = deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1")
            assert workspace.official_folder_path.is_dir()
        repeated = client.post(url + "/start", json=body)
        assert repeated.json()["operation_id"] == result["operation_id"]
        assert queued == []
        resume = client.post(url + "/resume", json={"operation_id": result["operation_id"]})
        assert resume.status_code == 202
        assert len(queued) == 1
        queued.pop()()
        (template / "template.txt").write_text("changed template", encoding="utf-8")
        assert runner.context("P1") != before_context
        assert client.post(url + "/resume", json={"operation_id": result["operation_id"]}).status_code == 409
        assert client.post(url + "/resume", json={"operation_id": "different"}).status_code == 409
        assert result["can_restart"] is True
        fresh_preview = client.get(url + "/preview").json()
        new_body = {"expected_context": fresh_preview["expected_context"], "request_id": "corrected-inputs",
                    "replaces_operation_id": result["operation_id"]}
        fresh = client.post(url + "/start", json=new_body)
        assert fresh.status_code == 202, fresh.text
        assert fresh.json()["operation_id"] != result["operation_id"]
        assert runner.journal.read_archived("P1", result["operation_id"])["context"] == before_context
        queued.pop()()
        result = client.get(url).json()
        with sessions() as session:
            project = deps.ProjectRepository(session).get("P1")
            deps.ProjectRepository(session).update(replace(project, lifecycle_state=ProjectLifecycleState.CLOSED))
            session.commit()
        assert client.post(url + "/resume", json={"operation_id": result["operation_id"]}).status_code == 409
        assert queued == []
    finally:
        app.dependency_overrides.clear()
        runner.pool.shutdown()
        engine.dispose()
