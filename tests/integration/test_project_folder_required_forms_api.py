from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import get_project_folder_required_forms_service
from backend.api.main import app
from backend.application.project_folder_required_forms_service import (
    RequiredFormPreviewItem,
    RequiredFormsContextMismatchError,
    RequiredFormsGenerateResult,
    RequiredFormsPreview,
)
from backend.application.project_lifecycle_write_guard import ProjectLifecycleReadonlyError
from backend.domain import ProjectClosureType, ProjectLifecycleState, ProjectOutputKind


def test_required_forms_preview_api_returns_project_folder_contract() -> None:
    service = _Service()
    app.dependency_overrides[get_project_folder_required_forms_service] = lambda: service
    try:
        response = TestClient(app).get("/api/projects/P1/project-folder/required-forms/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == "P1"
    assert payload["status"] == "ready"
    assert payload["confirmed_basic_information_version"] == 2
    assert payload["confirmed_basic_information_source_signature_hash"] == "basic-hash"
    assert payload["items"][0]["key"] == "test_record"
    assert "Submitted Material" in payload["items"][0]["target_path"]


def test_required_forms_generate_api_rejects_stale_context() -> None:
    service = _Service(stale=True)
    app.dependency_overrides[get_project_folder_required_forms_service] = lambda: service
    try:
        response = TestClient(app).post(
            "/api/projects/P1/project-folder/required-forms/generate",
            json=_request_payload(),
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409


def test_required_forms_generate_api_passes_basic_information_context() -> None:
    service = _Service()
    app.dependency_overrides[get_project_folder_required_forms_service] = lambda: service
    try:
        response = TestClient(app).post(
            "/api/projects/P1/project-folder/required-forms/generate",
            json=_request_payload(),
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert service.last_command.expected_confirmed_basic_information_version == 2
    assert (
        service.last_command.expected_confirmed_basic_information_source_signature_hash
        == "basic-hash"
    )


def test_required_forms_generate_stopped_returns_structured_409_without_mutation() -> None:
    service = _Service(lifecycle_state=ProjectLifecycleState.STOPPED)
    app.dependency_overrides[get_project_folder_required_forms_service] = lambda: service
    try:
        response = TestClient(app, raise_server_exceptions=False).post(
            "/api/projects/P1/project-folder/required-forms/generate",
            json=_request_payload(),
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "project_lifecycle_readonly"
    assert detail["project_id"] == "P1"
    assert detail["lifecycle_state"] == "stopped"
    assert detail["close_reason_category"] is None
    assert detail["close_reason_label"] is None
    assert detail["message"] == "This project is stopped. Activate it before making changes."
    assert detail["allowed_actions"] == ["activate"]
    assert service.last_command is None


def test_required_forms_generate_closed_returns_structured_409_without_mutation() -> None:
    service = _Service(
        lifecycle_state=ProjectLifecycleState.CLOSED,
        closure_type=ProjectClosureType.COMPLETED,
    )
    app.dependency_overrides[get_project_folder_required_forms_service] = lambda: service
    try:
        response = TestClient(app, raise_server_exceptions=False).post(
            "/api/projects/P1/project-folder/required-forms/generate",
            json=_request_payload(),
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "project_lifecycle_readonly"
    assert detail["project_id"] == "P1"
    assert detail["lifecycle_state"] == "closed"
    assert detail["closure_type"] == "completed"
    assert detail["close_reason_category"] == "completed"
    assert detail["close_reason_label"] == "Completed"
    assert detail["message"] == "This project is closed. Activate it before making changes."
    assert detail["allowed_actions"] == ["activate"]
    assert service.last_command is None


def test_required_forms_generate_legacy_administrative_uses_business_copy() -> None:
    service = _Service(
        lifecycle_state=ProjectLifecycleState.CLOSED,
        closure_type=ProjectClosureType.ADMINISTRATIVE,
    )
    app.dependency_overrides[get_project_folder_required_forms_service] = lambda: service
    try:
        response = TestClient(app, raise_server_exceptions=False).post(
            "/api/projects/P1/project-folder/required-forms/generate",
            json=_request_payload(),
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "project_lifecycle_readonly"
    assert detail["project_id"] == "P1"
    assert detail["lifecycle_state"] == "closed"
    assert detail["closure_type"] is None
    assert detail["close_reason_category"] == "other"
    assert detail["close_reason_label"] == "Other"
    assert "administrative" not in detail["message"].lower()
    assert "readonly" not in detail["message"].lower()
    assert detail["allowed_actions"] == ["activate"]
    assert service.last_command is None


def test_no_old_project_package_execute_route() -> None:
    response = TestClient(app).post("/api/projects/P1/project-package/execute", json={})

    assert response.status_code in {404, 405}


class _Service:
    def __init__(
        self,
        *,
        stale: bool = False,
        lifecycle_state: ProjectLifecycleState | None = None,
        closure_type: ProjectClosureType | None = None,
    ) -> None:
        self.stale = stale
        self.lifecycle_state = lifecycle_state
        self.closure_type = closure_type
        self.last_command = None

    def preview(self, project_id: str) -> RequiredFormsPreview:
        return _preview(project_id)

    def generate(self, command) -> RequiredFormsGenerateResult:
        if self.lifecycle_state is not None:
            raise ProjectLifecycleReadonlyError(
                project_id=command.project_id,
                lifecycle_state=self.lifecycle_state,
                closure_type=self.closure_type,
                message=_lifecycle_message(self.lifecycle_state, self.closure_type),
                allowed_actions=(
                    ("activate",)
                    if self.lifecycle_state is not ProjectLifecycleState.ACTIVE
                    else ()
                ),
            )
        if self.stale:
            raise RequiredFormsContextMismatchError("Required forms preview is stale.")
        self.last_command = command
        return RequiredFormsGenerateResult(
            project_id=command.project_id,
            status="generated",
            official_project_folder_path=command.expected_official_project_folder_path,
            items=tuple(),
            warnings=tuple(),
        )


def _lifecycle_message(
    lifecycle_state: ProjectLifecycleState,
    closure_type: ProjectClosureType | None,
) -> str:
    if lifecycle_state is ProjectLifecycleState.STOPPED:
        return "This project is stopped. Activate it before making changes."
    return "This project is closed. Activate it before making changes."


def _preview(project_id: str) -> RequiredFormsPreview:
    official = Path("D:/Test Project/DL-001/DL-001 Connector Qualification test")
    return RequiredFormsPreview(
        project_id=project_id,
        status="ready",
        official_project_folder_path=official,
        confirmed_matrix_id="CM1",
        confirmed_revision=1,
        confirmed_fee_id="CF1",
        confirmed_fee_revision=1,
        confirmed_fee_pricing_draft_edit_id="PD1",
        confirmed_basic_information_version=2,
        confirmed_basic_information_source_signature_hash="basic-hash",
        customer_feedback_template_path=Path("D:/Source/Template/E-4243.xlsx"),
        source_context_signature="matrix:CM1@1|fee:CF1@1|pricing:PD1|basic:2@basic-hash",
        items=(
            RequiredFormPreviewItem(
                key="test_record",
                label="Test Record",
                target_path=official / "Submitted Material" / "DL-001 Test Record.docx",
                status="ready",
                action="generate",
                message="Ready.",
                output_kind=ProjectOutputKind.TEST_RECORD_FORM,
            ),
        ),
        blockers=tuple(),
        warnings=tuple(),
    )


def _request_payload() -> dict[str, object]:
    official = "D:/Test Project/DL-001/DL-001 Connector Qualification test"
    return {
        "expected_official_project_folder_path": official,
        "expected_confirmed_matrix_id": "CM1",
        "expected_confirmed_revision": 1,
        "expected_confirmed_fee_id": "CF1",
        "expected_confirmed_fee_revision": 1,
        "expected_confirmed_fee_pricing_draft_edit_id": "PD1",
        "expected_confirmed_basic_information_version": 2,
        "expected_confirmed_basic_information_source_signature_hash": "basic-hash",
        "expected_customer_feedback_template_path": "D:/Source/Template/E-4243.xlsx",
        "expected_targets": [
            {
                "key": "test_record",
                "target_path": f"{official}/Submitted Material/DL-001 Test Record.docx",
            }
        ],
    }
