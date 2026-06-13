from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import get_official_project_folder_check_service
from backend.api.main import app
from backend.application.official_project_folder_check_service import (
    OfficialFolderCheckItem,
    OfficialFolderCheckPreview,
    OfficialFolderRepairResult,
    OfficialProjectFolderCheckConflictError,
    OfficialProjectFolderCheckNotFoundError,
)


def test_official_folder_check_preview_returns_typed_response() -> None:
    service = _FakeOfficialFolderCheckService(
        preview=OfficialFolderCheckPreview(
            project_id="P1",
            status="missing",
            local_workspace_path=Path("D:/Test Project/DL-001"),
            official_project_folder_path=Path("D:/Test Project/DL-001/DL-001 Product Qualification test"),
            required_folders=(
                OfficialFolderCheckItem(
                    key="photos",
                    label="Photos",
                    kind="folder",
                    status="missing",
                    path=Path("D:/Test Project/DL-001/DL-001 Product Qualification test/Photos"),
                    message="Folder is missing.",
                    repairable=True,
                ),
            ),
            required_files=tuple(),
            blockers=tuple(),
            warnings=tuple(),
            next_action="repair_folders",
        )
    )
    app.dependency_overrides[get_official_project_folder_check_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/official-folder/check")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "P1"
    assert body["status"] == "missing"
    assert body["required_folders"][0]["key"] == "photos"
    assert body["next_action"] == "repair_folders"


def test_official_folder_repair_returns_partial_fields() -> None:
    preview = OfficialFolderCheckPreview(
        project_id="P1",
        status="ready",
        local_workspace_path=Path("D:/Test Project/DL-001"),
        official_project_folder_path=Path("D:/Test Project/DL-001/DL-001 Product Qualification test"),
        required_folders=tuple(),
        required_files=tuple(),
        blockers=tuple(),
        warnings=tuple(),
        next_action="none",
    )
    service = _FakeOfficialFolderCheckService(
        repair=OfficialFolderRepairResult(
            project_id="P1",
            repair_status="partial",
            created_paths=(Path("D:/Test Project/DL-001/DL-001 Product Qualification test/E-mail"),),
            unresolved_conflicts=tuple(),
            errors=("folder creation failed",),
            preview=preview,
        )
    )
    app.dependency_overrides[get_official_project_folder_check_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.post("/api/projects/P1/official-folder/repair-folders")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["repair_status"] == "partial"
    assert body["created_paths"]
    assert body["errors"] == ["folder creation failed"]
    assert body["preview"]["status"] == "ready"


def test_official_folder_check_missing_project_returns_404() -> None:
    service = _FakeOfficialFolderCheckService(
        error=OfficialProjectFolderCheckNotFoundError("Project not found: P404")
    )
    app.dependency_overrides[get_official_project_folder_check_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P404/official-folder/check")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"]


def test_official_folder_repair_conflict_returns_409() -> None:
    service = _FakeOfficialFolderCheckService(
        error=OfficialProjectFolderCheckConflictError("Required folder path conflict.")
    )
    app.dependency_overrides[get_official_project_folder_check_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.post("/api/projects/P1/official-folder/repair-folders")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert "conflict" in response.json()["detail"]


class _FakeOfficialFolderCheckService:
    def __init__(
        self,
        *,
        preview: OfficialFolderCheckPreview | None = None,
        repair: OfficialFolderRepairResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self._preview = preview
        self._repair = repair
        self._error = error

    def preview(self, project_id: str) -> OfficialFolderCheckPreview:
        if self._error:
            raise self._error
        assert self._preview is not None
        return self._preview

    def repair_folders(self, project_id: str) -> OfficialFolderRepairResult:
        if self._error:
            raise self._error
        assert self._repair is not None
        return self._repair
