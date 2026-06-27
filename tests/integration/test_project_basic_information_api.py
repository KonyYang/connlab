from __future__ import annotations

from fastapi.testclient import TestClient

from backend.api.dependencies import get_project_basic_information_service
from backend.api.main import app
from backend.application.project_lifecycle_write_guard import (
    ProjectLifecycleReadonlyError,
    ProjectLifecycleWriteGuardNotFoundError,
)
from backend.application.project_basic_information_service import (
    ProjectBasicInformationDraft,
    ProjectBasicInformationFieldSuggestion,
    ProjectBasicInformationMissingRequiredError,
    ProjectBasicInformationProjectNotFoundError,
    ProjectBasicInformationRecord,
    ProjectBasicInformationResult,
)
from backend.domain import ProjectLifecycleState


def test_get_basic_information_returns_typed_unconfirmed_draft() -> None:
    service = _Service()
    app.dependency_overrides[get_project_basic_information_service] = lambda: service
    try:
        response = TestClient(app).get("/api/projects/P1/basic-information")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == "P1"
    assert payload["status"] == "unconfirmed"
    assert payload["draft"]["values"]["dl_number"] == "DL-2026-05-011"


def test_put_basic_information_draft_saves_values() -> None:
    service = _Service()
    app.dependency_overrides[get_project_basic_information_service] = lambda: service
    try:
        response = TestClient(app).put(
            "/api/projects/P1/basic-information/draft",
            json={"values": {"project_type": "PEX"}},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert service.saved_values == {"project_type": "PEX"}
    assert response.json()["draft"]["values"]["project_type"] == "PEX"


def test_post_basic_information_confirm_returns_confirmed_version() -> None:
    service = _Service()
    app.dependency_overrides[get_project_basic_information_service] = lambda: service
    try:
        response = TestClient(app).post(
            "/api/projects/P1/basic-information/confirm",
            json={"values": _complete_values(), "confirmed_by": "Lab User"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "confirmed"
    assert payload["latest_confirmed"]["version"] == 1
    assert service.confirmed_by == "Lab User"


def test_post_basic_information_confirm_missing_fields_returns_422() -> None:
    service = _Service(missing=True)
    app.dependency_overrides[get_project_basic_information_service] = lambda: service
    try:
        response = TestClient(app).post(
            "/api/projects/P1/basic-information/confirm",
            json={"values": {"dl_number": "DL-2026-05-011"}, "confirmed_by": "Lab User"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert "Project Type" in response.json()["detail"]["missing_labels"]


def test_get_basic_information_nonexistent_project_returns_404() -> None:
    service = _Service(not_found=True)
    app.dependency_overrides[get_project_basic_information_service] = lambda: service
    try:
        response = TestClient(app).get("/api/projects/NOPE/basic-information")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found: NOPE"


def test_lifecycle_readonly_draft_save_returns_structured_409_without_mutation() -> None:
    service = _Service(lifecycle_readonly=True)
    app.dependency_overrides[get_project_basic_information_service] = lambda: service
    try:
        response = TestClient(app, raise_server_exceptions=False).put(
            "/api/projects/P1/basic-information/draft",
            json={"values": {"project_type": "PEX"}},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "project_lifecycle_readonly"
    assert detail["project_id"] == "P1"
    assert detail["lifecycle_state"] == "stopped"
    assert detail["closure_type"] is None
    assert detail["allowed_actions"] == ["resume", "close"]
    assert service.saved_values is None


def test_lifecycle_guard_missing_project_maps_to_404() -> None:
    service = _Service(lifecycle_guard_not_found=True)
    app.dependency_overrides[get_project_basic_information_service] = lambda: service
    try:
        response = TestClient(app, raise_server_exceptions=False).put(
            "/api/projects/NOPE/basic-information/draft",
            json={"values": {"project_type": "PEX"}},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found: NOPE"


def _complete_values() -> dict[str, str]:
    return {
        "dl_number": "DL-2026-05-011",
        "project_type": "NPD",
        "product_description": "Coolpower HDF",
        "test_item": "Qualification Testing",
        "requested_by": "MP Cao",
        "project_leader": "Even Yang",
        "lab_performing_tests": "Dongguan",
    }


class _Service:
    def __init__(
        self,
        *,
        missing: bool = False,
        not_found: bool = False,
        lifecycle_readonly: bool = False,
        lifecycle_guard_not_found: bool = False,
    ) -> None:
        self.missing = missing
        self.not_found = not_found
        self.lifecycle_readonly = lifecycle_readonly
        self.lifecycle_guard_not_found = lifecycle_guard_not_found
        self.saved_values: dict[str, str] | None = None
        self.confirmed_by: str | None = None

    def get(self, project_id: str) -> ProjectBasicInformationResult:
        if self.not_found:
            raise ProjectBasicInformationProjectNotFoundError(
                f"Project not found: {project_id}"
            )
        return _result(project_id, status="unconfirmed")

    def save_draft(self, command) -> ProjectBasicInformationResult:
        if self.lifecycle_guard_not_found:
            raise ProjectLifecycleWriteGuardNotFoundError(
                f"Project not found: {command.project_id}"
            )
        if self.lifecycle_readonly:
            raise ProjectLifecycleReadonlyError(
                project_id=command.project_id,
                lifecycle_state=ProjectLifecycleState.STOPPED,
                closure_type=None,
                message="This project is stopped. Resume it before making changes.",
                allowed_actions=("resume", "close"),
            )
        self.saved_values = command.values
        return _result(command.project_id, status="unconfirmed", values=command.values)

    def confirm(self, command) -> ProjectBasicInformationResult:
        if self.lifecycle_readonly:
            raise ProjectLifecycleReadonlyError(
                project_id=command.project_id,
                lifecycle_state=ProjectLifecycleState.STOPPED,
                closure_type=None,
                message="This project is stopped. Resume it before making changes.",
                allowed_actions=("resume", "close"),
            )
        if self.missing:
            raise ProjectBasicInformationMissingRequiredError(
                missing_fields=("project_type",),
                missing_labels=("Project Type",),
            )
        self.confirmed_by = command.confirmed_by
        return _result(
            command.project_id,
            status="confirmed",
            values=command.values,
            confirmed=True,
        )


def _result(
    project_id: str,
    *,
    status: str,
    values: dict[str, str] | None = None,
    confirmed: bool = False,
) -> ProjectBasicInformationResult:
    draft_values = values or {"dl_number": "DL-2026-05-011"}
    latest_confirmed = None
    if confirmed:
        latest_confirmed = ProjectBasicInformationRecord(
            record_id="BASIC-1",
            project_id=project_id,
            status="confirmed",
            version=1,
            values=draft_values,
            source_signature="sig",
            created_at="2026-06-20T09:00:00+08:00",
            updated_at="2026-06-20T09:00:00+08:00",
            confirmed_at="2026-06-20T09:00:00+08:00",
            confirmed_by="Lab User",
        )
    return ProjectBasicInformationResult(
        project_id=project_id,
        status=status,
        draft=ProjectBasicInformationDraft(values=draft_values),
        latest_confirmed=latest_confirmed,
        field_suggestions={
            "dl_number": ProjectBasicInformationFieldSuggestion(
                field_key="dl_number",
                source="project_identity",
                source_value="DL-2026-05-011",
                needs_review=False,
            )
        },
        changed_source_fields=tuple(),
        missing_required_fields=tuple(),
        missing_required_labels=tuple(),
        blockers=tuple(),
        warnings=tuple(),
    )
