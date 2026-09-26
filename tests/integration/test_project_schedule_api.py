"""Read-only historical schedule API remains available for Matrix migration."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.api.dependencies import get_project_schedule_service
from backend.api.main import app
from backend.api.routes_project_schedule import router
from backend.application.project_schedule_service import ProjectScheduleService
from backend.domain.project_schedule_models import ProjectScheduleRevision
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.models import ProjectModel
from backend.infrastructure.storage.repositories.project_schedule import ProjectScheduleRepository


def test_historical_schedule_get_remains_available_but_confirm_is_gone() -> None:
    app.dependency_overrides[get_project_schedule_service] = lambda: _ReadOnlyService()
    try:
        with TestClient(app) as client:
            response = client.get("/api/projects/P1/project-schedule")
            retired = client.post("/api/projects/P1/project-schedule/confirm", json={
                "actor": "operator", "post_test_buffer_days": "1",
                "test_start_date": "2026-09-10", "test_complete_date": "2026-09-11",
                "estimated_completion_date": "2026-09-12",
            })
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["confirmed_revision"]["revision_id"] == "psr-old"
    assert retired.status_code == 410
    assert retired.json()["detail"]["code"] == "project_schedule_confirm_retired"


def test_retired_endpoint_cannot_create_schedule_for_new_project() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    init_db(engine)
    with Session(engine) as session:
        session.add(ProjectModel(
            project_id="P1", project_no="DL-1", product_name="Product",
            requestor="User", status="registered",
        ))
        session.commit()

    def service_dependency():
        with Session(engine) as session:
            yield ProjectScheduleService(
                repository=ProjectScheduleRepository(session),
                basic_information_reader=_NoConfirmedSources(),
                confirmed_matrix_store=_NoConfirmedSources(),
                clock=lambda: "2026-09-08T00:00:00Z",
            )
            session.commit()

    isolated_app = FastAPI()
    isolated_app.include_router(router)
    isolated_app.dependency_overrides[get_project_schedule_service] = service_dependency
    with TestClient(isolated_app) as client:
        workspace = client.get("/api/projects/P1/project-schedule")
        refused = client.post("/api/projects/P1/project-schedule/confirm", json={
            "actor": "operator", "post_test_buffer_days": "0",
            "test_start_date": "2026-09-10", "test_complete_date": "2026-09-10",
            "estimated_completion_date": "2026-09-10",
        })
    assert workspace.status_code == 200
    assert workspace.json()["confirmed_revision"] is None
    assert refused.status_code == 410
    with Session(engine) as session:
        assert ProjectScheduleRepository(session).active_revision("P1") is None
    engine.dispose()


class _NoConfirmedSources:
    def get_latest_confirmed(self, project_id):
        return None

    def get_active_by_project(self, project_id):
        return None


class _ReadOnlyService:
    def get_workspace(self, project_id: str):
        from backend.domain.project_schedule_models import ProjectScheduleSuggestion, ProjectScheduleWorkspace
        return ProjectScheduleWorkspace(
            status="confirmed", project_id=project_id, sample_received_date="2026-09-01",
            critical_group_id=None, critical_group_days="0",
            suggestion=ProjectScheduleSuggestion("1", "2026-09-10", "2026-09-11", "2026-09-12"),
            confirmed_revision=ProjectScheduleRevision(
                revision_id="psr-old", project_id=project_id, revision_sequence=1,
                state="confirmed", fingerprint="old", matrix_input_fingerprint="old-matrix",
                based_on_confirmed_matrix_id=None, based_on_confirmed_matrix_revision=None,
                based_on_basic_information_version=None, sample_received_date="2026-09-01",
                post_test_buffer_days="1", test_start_date="2026-09-10",
                test_complete_date="2026-09-11", estimated_completion_date="2026-09-12",
                confirmed_by="historical operator", confirmed_at="2026-09-12T00:00:00Z",
            ),
        )
