from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.api.dependencies import get_project_schedule_service
from backend.api.main import app
from backend.api.routes_project_schedule import router
from backend.application.project_schedule_service import ProjectScheduleConflictError, ProjectScheduleService
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.models import ProjectModel
from backend.infrastructure.storage.repositories.project_schedule import ProjectScheduleRepository
from backend.domain.project_schedule_models import (
    ProjectScheduleRevision,
    ProjectScheduleSuggestion,
    ProjectScheduleWorkspace,
)


def test_project_schedule_workspace_and_confirm_have_typed_public_contract() -> None:
    service = _ScheduleService()
    app.dependency_overrides[get_project_schedule_service] = lambda: service
    try:
        with TestClient(app) as client:
            workspace = client.get("/api/projects/P1/project-schedule")
            confirmed = client.post(
                "/api/projects/P1/project-schedule/confirm",
                json={
                    "actor": "operator",
                    "expected_revision_id": None,
                    "expected_fingerprint": None,
                    "post_test_buffer_days": "2",
                    "test_start_date": "2026-09-10",
                    "test_complete_date": "2026-09-13",
                    "estimated_completion_date": "2026-09-15",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert workspace.status_code == 200
    assert workspace.json()["sample_received_date"] == "2026-09-08"
    assert workspace.json()["critical_group_days"] == "3"
    assert confirmed.status_code == 200
    assert confirmed.json()["revision_id"] == "psr-1"
    assert service.last_command.confirmed_by == "operator"


def test_project_schedule_stale_confirm_is_a_conflict() -> None:
    app.dependency_overrides[get_project_schedule_service] = lambda: _ConflictService()
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/projects/P1/project-schedule/confirm",
                json={
                    "actor": "operator",
                    "post_test_buffer_days": "0",
                    "test_start_date": "2026-09-10",
                    "test_complete_date": "2026-09-13",
                    "estimated_completion_date": "2026-09-13",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_schedule_conflict"


def test_schedule_api_confirms_and_reopens_without_basic_or_matrix_authority():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    init_db(engine)
    with Session(engine) as session:
        session.add(ProjectModel(project_id="P1", project_no="DL-1", product_name="Product", requestor="User", status="registered"))
        session.commit()

    def service_dependency():
        with Session(engine) as session:
            yield ProjectScheduleService(repository=ProjectScheduleRepository(session),
                basic_information_reader=_NoConfirmedSources(), confirmed_matrix_store=_NoConfirmedSources(),
                clock=lambda: "2026-09-08T00:00:00Z")
            session.commit()

    isolated_app = FastAPI()
    isolated_app.include_router(router)
    isolated_app.dependency_overrides[get_project_schedule_service] = service_dependency
    with TestClient(isolated_app) as client:
        workspace = client.get("/api/projects/P1/project-schedule")
        assert workspace.status_code == 200
        assert workspace.json()["sample_received_date"] == ""
        payload = {"actor": "operator", "post_test_buffer_days": "0",
            "test_start_date": "2026-09-10", "test_complete_date": "2026-09-10",
            "estimated_completion_date": "2026-09-10"}
        invalid = client.post("/api/projects/P1/project-schedule/confirm", json={**payload, "test_start_date": " "})
        assert invalid.status_code == 422
        confirmed = client.post("/api/projects/P1/project-schedule/confirm", json=payload)
        assert confirmed.status_code == 200
        revision = confirmed.json()
        assert revision["based_on_confirmed_matrix_id"] is None
        assert revision["based_on_confirmed_matrix_revision"] is None
        assert revision["based_on_basic_information_version"] is None
        assert revision["sample_received_date"] == ""
        reopened = client.get("/api/projects/P1/project-schedule").json()
        assert reopened["status"] == "confirmed"
        assert reopened["confirmed_revision"] == revision
        stale = client.post("/api/projects/P1/project-schedule/confirm", json=payload)
        assert stale.status_code == 409
        missing_workspace = client.get("/api/projects/missing-project/project-schedule")
        missing_confirmation = client.post("/api/projects/missing-project/project-schedule/confirm", json=payload)
        assert missing_workspace.status_code == missing_confirmation.status_code == 404
        assert missing_confirmation.json()["detail"]["code"] == "project_not_found"
    with Session(engine) as session:
        repository = ProjectScheduleRepository(session)
        assert repository.active_revision("missing-project") is None
        assert repository.highest_revision_sequence("missing-project") == 0
    engine.dispose()


class _NoConfirmedSources:
    def get_latest_confirmed(self, project_id):
        return None

    def get_active_by_project(self, project_id):
        return None


class _ScheduleService:
    last_command = None

    def get_workspace(self, project_id: str):
        return ProjectScheduleWorkspace(
            status="not_started",
            project_id=project_id,
            sample_received_date="2026-09-08",
            critical_group_id="g1",
            critical_group_days="3",
            suggestion=ProjectScheduleSuggestion("2", "2026-09-10", "2026-09-13", "2026-09-15"),
            confirmed_revision=None,
        )

    def confirm(self, command):
        self.last_command = command
        return ProjectScheduleRevision(
            revision_id="psr-1", project_id=command.project_id, revision_sequence=1,
            state="confirmed", fingerprint="fp", matrix_input_fingerprint="mfp",
            based_on_confirmed_matrix_id="cm-1", based_on_confirmed_matrix_revision=1,
            based_on_basic_information_version=1, sample_received_date="2026-09-08",
            post_test_buffer_days=command.post_test_buffer_days,
            test_start_date=command.test_start_date,
            test_complete_date=command.test_complete_date,
            estimated_completion_date=command.estimated_completion_date,
            confirmed_by=command.confirmed_by, confirmed_at="2026-09-08T00:00:00Z",
        )


class _ConflictService:
    def confirm(self, _command):
        raise ProjectScheduleConflictError("Project Schedule changed.")
