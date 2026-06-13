from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import get_official_project_workspace_service
from backend.api.main import app
from backend.application.official_project_workspace_service import (
    OfficialWorkspaceCreateError,
    OfficialWorkspaceCreateResult,
    OfficialWorkspaceNotFoundError,
    OfficialWorkspacePreview,
    OfficialWorkspaceRecord,
)


def test_official_workspace_preview_api_returns_typed_preview() -> None:
    service = _FakeWorkspaceService(
        preview=OfficialWorkspacePreview(
            project_id="P1",
            dl_number="DL-2025-11-074",
            local_workspace_root=Path("D:/Projects"),
            local_workspace_path=Path("D:/Projects/DL-2025-11-074"),
            source_book_path=Path("D:/Projects/DL-2025-11-074/Source Book"),
            template_path=Path("D:/Template/DL-XXXX-YY-ZZZ project"),
            official_folder_path=Path("D:/Projects/DL-2025-11-074/DL-2025-11-074 Product Qualification test"),
            manifest_path=Path("D:/Projects/DL-2025-11-074/.connlab/manifest.json"),
            template_root_mode="template_root",
            status="ready",
            blockers=(),
            warnings=("Public Project locations is not configured; upload readiness will be checked later.",),
            planned_paths=(Path("D:/Projects/DL-2025-11-074"),),
        )
    )
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/official-workspace/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == "P1"
    assert payload["status"] == "ready"
    assert payload["dl_number"] == "DL-2025-11-074"
    assert payload["warnings"][0].startswith("Public Project locations")


def test_official_workspace_create_api_returns_created_paths() -> None:
    record = OfficialWorkspaceRecord(
        workspace_id="W1",
        project_id="P1",
        dl_number="DL-2025-11-074",
        local_workspace_path=Path("D:/Projects/DL-2025-11-074"),
        source_book_path=Path("D:/Projects/DL-2025-11-074/Source Book"),
        official_folder_path=Path("D:/Projects/DL-2025-11-074/DL-2025-11-074 Product Qualification test"),
        manifest_path=Path("D:/Projects/DL-2025-11-074/.connlab/manifest.json"),
        template_source_path=Path("D:/Template/DL-XXXX-YY-ZZZ project"),
        created_at="2026-06-12T00:00:00+00:00",
    )
    service = _FakeWorkspaceService(
        create=OfficialWorkspaceCreateResult(
            record=record,
            created_paths=(record.local_workspace_path, record.official_folder_path),
            warnings=(),
        )
    )
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.post("/api/projects/P1/official-workspace/create")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    payload = response.json()
    assert payload["workspace_id"] == "W1"
    assert payload["official_project_folder_path"].endswith("Qualification test")
    assert len(payload["created_paths"]) == 2


def test_official_workspace_create_blocked_returns_409() -> None:
    service = _FakeWorkspaceService(error=OfficialWorkspaceCreateError("Official project folder already exists"))
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.post("/api/projects/P1/official-workspace/create")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_official_workspace_missing_project_returns_404() -> None:
    service = _FakeWorkspaceService(error=OfficialWorkspaceNotFoundError("Project not found: P404"))
    app.dependency_overrides[get_official_project_workspace_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P404/official-workspace/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"]


class _FakeWorkspaceService:
    def __init__(
        self,
        *,
        preview: OfficialWorkspacePreview | None = None,
        create: OfficialWorkspaceCreateResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self._preview = preview
        self._create = create
        self._error = error

    def preview(self, project_id: str) -> OfficialWorkspacePreview:
        if self._error:
            raise self._error
        assert self._preview is not None
        return self._preview

    def create(self, project_id: str) -> OfficialWorkspaceCreateResult:
        if self._error:
            raise self._error
        assert self._create is not None
        return self._create
