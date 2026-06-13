from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import get_public_drive_upload_service
from backend.api.main import app
from backend.application.public_drive_upload_service import (
    PublicDriveUploadConflictError,
    PublicDriveUploadItem,
    PublicDriveUploadPreview,
    PublicDriveUploadResult,
)


def test_public_drive_preview_api_returns_directory_and_file_items() -> None:
    service = _FakePublicDriveUploadService(
        preview=_preview(
            status="ready",
            items=(
                _item("directory", "Photos", "add"),
                _item("file", "Submitted Material/app.docx", "add"),
            ),
        )
    )
    app.dependency_overrides[get_public_drive_upload_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/public-drive/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["items"][0]["kind"] == "directory"
    assert data["items"][0]["action"] == "add"
    assert data["items"][1]["kind"] == "file"


def test_public_drive_preview_api_returns_blocked_status() -> None:
    service = _FakePublicDriveUploadService(
        preview=_preview(
            status="blocked",
            blockers=("Public Project locations is not configured.",),
        )
    )
    app.dependency_overrides[get_public_drive_upload_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.get("/api/projects/P1/public-drive/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "blocked"
    assert data["blockers"] == ["Public Project locations is not configured."]


def test_public_drive_upload_api_returns_current_preview_after_copy() -> None:
    result = PublicDriveUploadResult(
        project_id="P1",
        upload_status="completed",
        copied=(_item("file", "Submitted Material/app.docx", "add"),),
        updated=tuple(),
        skipped=tuple(),
        conflicts=tuple(),
        failed=tuple(),
        errors=tuple(),
        preview=_preview(status="current", items=(_item("file", "Submitted Material/app.docx", "skip"),)),
    )
    service = _FakePublicDriveUploadService(result=result)
    app.dependency_overrides[get_public_drive_upload_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.post("/api/projects/P1/public-drive/upload")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["upload_status"] == "completed"
    assert data["preview"]["status"] == "current"


def test_public_drive_upload_api_conflict_returns_409() -> None:
    service = _FakePublicDriveUploadService(
        error=PublicDriveUploadConflictError("Resolve public-drive conflicts before upload.")
    )
    app.dependency_overrides[get_public_drive_upload_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.post("/api/projects/P1/public-drive/upload")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert "conflicts" in response.json()["detail"]


def _preview(
    *,
    status: str,
    items: tuple[PublicDriveUploadItem, ...] = tuple(),
    blockers: tuple[str, ...] = tuple(),
) -> PublicDriveUploadPreview:
    counts = {key: 0 for key in ("add", "update", "skip", "conflict", "deferred")}
    for item in items:
        counts[item.action] += 1
    return PublicDriveUploadPreview(
        project_id="P1",
        status=status,
        local_official_folder_path=Path("D:/Test Project/DL-001/DL-001 Product Qualification test"),
        public_project_folder_path=Path("D:/Public/DL-001/DL-001 Product Qualification test"),
        items=items,
        blockers=blockers,
        warnings=tuple(),
        counts=counts,
        next_action="upload" if status == "ready" else "none",
    )


def _item(kind: str, relative_path: str, action: str) -> PublicDriveUploadItem:
    return PublicDriveUploadItem(
        kind=kind,
        relative_path=Path(relative_path),
        local_path=Path("D:/local") / relative_path if kind == "file" else None,
        public_path=Path("D:/public") / relative_path,
        action=action,
        status="ready" if action in {"add", "update"} else "current",
        message="Test item.",
    )


class _FakePublicDriveUploadService:
    def __init__(
        self,
        *,
        preview: PublicDriveUploadPreview | None = None,
        result: PublicDriveUploadResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self._preview = preview
        self._result = result
        self._error = error

    def preview(self, project_id: str) -> PublicDriveUploadPreview:
        assert self._preview is not None
        return self._preview

    def upload(self, project_id: str) -> PublicDriveUploadResult:
        if self._error:
            raise self._error
        assert self._result is not None
        return self._result
