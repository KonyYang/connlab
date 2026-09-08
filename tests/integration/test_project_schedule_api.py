from fastapi.testclient import TestClient

from backend.api.dependencies import get_project_schedule_service
from backend.api.main import app
from backend.application.project_schedule_service import ProjectScheduleConflictError
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
