"""Retained HTTP writers must not bypass the durable generation operation."""

from pathlib import Path

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine

from backend.api import dependencies as deps
from backend.api.main import app
from backend.application.project_folder_generation_service import ProjectFolderGenerationService
from backend.domain import Project, ProjectStatus, ExternalResource, ExternalResourceType, LtrRecord, LtrStatus
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.storage.database import Base, create_session_factory
from backend.shared.config import Settings


ROUTES = (
    ("/official-workspace/create", deps.get_official_project_workspace_service),
    ("/request-material/collect", deps.get_project_request_material_collection_service),
    ("/project-folder/required-forms/generate", deps.get_project_folder_required_forms_service),
    ("/project-folder/application-form/write-back", deps.get_project_application_form_write_back_service),
)


def _body(root: Path):
    return dict(expected_official_project_folder_path=str(root), expected_confirmed_matrix_id="matrix",
        expected_confirmed_revision=1, expected_confirmed_fee_id="fee", expected_confirmed_fee_revision=1,
        expected_confirmed_fee_pricing_draft_edit_id="fee-edit", expected_confirmed_basic_information_version=1,
        expected_confirmed_basic_information_source_signature_hash="basic", expected_customer_feedback_template_path=str(root),
        expected_targets=[])


@pytest.fixture
def isolated(tmp_path):
    settings = Settings(data_dir=tmp_path / "data", projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates", database_path=tmp_path / "fixture.sqlite")
    app.dependency_overrides[deps.get_settings] = lambda: settings
    try:
        yield GenerationJournal(settings.data_dir / "project_folder_generation")
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("path,dependency", ROUTES)
@pytest.mark.parametrize("status", ["queued", "blocked"])
def test_retained_write_routes_reject_unfinished_generation_before_mutation(isolated, tmp_path, path, dependency, status):
    state = isolated.create("P1", None, "fixture")
    state["status"] = status
    isolated.save(state)
    entered = []

    class ForbiddenWrite:
        def __getattr__(self, name):
            def fail(*args, **kwargs):
                entered.append(name)
                raise AssertionError("Retained writer bypassed unfinished generation")
            return fail

    app.dependency_overrides[dependency] = ForbiddenWrite
    response = TestClient(app, raise_server_exceptions=False).post(
        "/api/projects/P1" + path, json=_body(tmp_path) if "required-forms" in path else {})
    assert response.status_code == 409, response.text
    assert "generation" in response.json()["detail"].lower()
    assert entered == []


@pytest.mark.parametrize("previous_completed", [False, True])
def test_legacy_workspace_holds_project_lock_through_database_commit_and_releases_it(isolated, tmp_path, previous_completed):
    if previous_completed:
        previous = ProjectFolderGenerationService(isolated, lambda _: "fixture",
            lambda state, step: None, lambda run: run())
        previous.start("P1", None, "fixture", "previous")
        assert previous.read("P1")["status"] == "completed"
    engine = create_engine(f"sqlite:///{(tmp_path / 'fixture.sqlite').as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    template, destination = tmp_path / "template", tmp_path / "output"
    destination.mkdir()
    for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
        (template / name).mkdir(parents=True)
    (template / "fixture.txt").write_text("original", encoding="utf-8")
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(project_id="P1", project_no="DL-001",
            product_name="Connector", requestor="Test", status=ProjectStatus.DRAFT))
        deps.LtrRecordRepository(session).create(LtrRecord(ltr_id="ltr", project_id="P1",
            ltr_number="DL-001", status=LtrStatus.REGISTERED))
        resources = deps.ExternalResourceRepository(session)
        resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, destination))
        resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
        session.commit()
    committed = []

    def temporary_session():
        with sessions() as session:
            yield session
            with pytest.raises(ValueError, match="already running"):
                with isolated.lock("P1"):
                    pass
            session.commit()
            committed.append(True)

    app.dependency_overrides[deps.get_session] = temporary_session
    try:
        response = TestClient(app).post("/api/projects/P1/official-workspace/create", json={})
        assert response.status_code == 201, response.text
        assert committed == [True]
        with sessions() as session:
            record = deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1")
            assert (record.official_folder_path / "fixture.txt").read_text(encoding="utf-8") == "original"
        with isolated.lock("P1"):
            pass
    finally:
        engine.dispose()


def test_live_lock_and_damaged_journal_reject_legacy_write_without_entering_service(isolated):
    # The service must not even be constructed when another writer owns the project.
    def forbidden_service():
        raise AssertionError("Writer dependencies should be resolved after the guard")

    app.dependency_overrides[deps.get_project_application_form_write_back_service] = forbidden_service
    client = TestClient(app)
    url = "/api/projects/P1/project-folder/application-form/write-back"
    with isolated.lock("P1"):
        assert client.post(url).status_code == 409
    isolated.create("P1", None, "fixture")
    (isolated.project_path("P1") / "operation.json").write_text("damaged journal", encoding="utf-8")
    response = client.post(url)
    assert response.status_code == 409
    assert "damaged" in response.json()["detail"]
