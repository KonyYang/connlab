from __future__ import annotations

from fastapi.testclient import TestClient

from backend.api.dependencies import get_project_package_preview_service
from backend.api.main import app
from backend.application.project_package_preview_service import (
    ProjectPackageAuthorityContext,
    ProjectPackageFolderPreview,
    ProjectPackagePreview,
    ProjectPackagePreviewItem,
    ProjectPackagePreviewProjectNotFoundError,
)


def test_project_package_preview_api_returns_typed_preview() -> None:
    client = TestClient(app)
    app.dependency_overrides[get_project_package_preview_service] = lambda: FakePreviewService(
        _blocked_preview()
    )
    try:
        response = client.get("/api/projects/P1/project-package/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked"
    assert payload["project_folder"]["status"] == "blocked"
    assert payload["authority_context"]["matrix_source"] == "missing"
    assert payload["required_items"][0]["key"] == "test_record"
    assert payload["blockers"] == ["Create the project folder before previewing package targets."]


def test_project_package_preview_api_missing_project_returns_404() -> None:
    client = TestClient(app)
    app.dependency_overrides[get_project_package_preview_service] = lambda: FakePreviewService(
        error=ProjectPackagePreviewProjectNotFoundError("Project not found: P404")
    )
    try:
        response = client.get("/api/projects/P404/project-package/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert "Project not found" in response.text


class FakePreviewService:
    def __init__(
        self,
        result: ProjectPackagePreview | None = None,
        *,
        error: Exception | None = None,
    ) -> None:
        self._result = result
        self._error = error

    def preview(self, project_id: str) -> ProjectPackagePreview:
        if self._error is not None:
            raise self._error
        assert self._result is not None
        return self._result


def _blocked_preview() -> ProjectPackagePreview:
    return ProjectPackagePreview(
        project_id="P1",
        status="blocked",
        project_folder=ProjectPackageFolderPreview(
            status="blocked",
            path=None,
            message="Create the project folder before previewing package targets.",
        ),
        authority_context=ProjectPackageAuthorityContext(
            confirmed_matrix_id=None,
            confirmed_revision=None,
            matrix_source="missing",
            project_matrix_draft_id=None,
            confirmed_fee_id=None,
            confirmed_fee_revision=None,
            confirmed_fee_status="missing",
        ),
        required_items=(
            ProjectPackagePreviewItem(
                key="test_record",
                label="Test Record",
                status="blocked",
                target_folder=None,
                target_path=None,
                message="Confirm Matrix before Test Record generation.",
            ),
        ),
        optional_items=(),
        blockers=("Create the project folder before previewing package targets.",),
        warnings=(),
    )
