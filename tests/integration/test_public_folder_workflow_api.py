from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import get_public_folder_workflow_service
from backend.api.main import app
from backend.application.public_folder_workflow_service import (
    PublicFolderWorkflowConflictError,
    PublicFolderWorkflowContext,
    PublicFolderWorkflowItem,
    PublicFolderWorkflowPreview,
    PublicFolderWorkflowResult,
    PublicFolderWorkflowState,
)


def test_public_folder_workflow_preview_api_returns_paths_and_hash() -> None:
    service = _FakeService(preview=_preview())
    app.dependency_overrides[get_public_folder_workflow_service] = lambda: service
    try:
        response = TestClient(app).post("/api/projects/P1/public-folder-workflow/sync/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["operation_type"] == "sync"
    assert payload["public_folder_year"] == 2026
    assert payload["preview_hash"] == "hash"
    assert payload["items"][0]["action"] == "add"


def test_public_folder_workflow_execute_stale_preview_maps_to_409() -> None:
    service = _FakeService(error=PublicFolderWorkflowConflictError("Public folder preview is stale."))
    app.dependency_overrides[get_public_folder_workflow_service] = lambda: service
    try:
        response = TestClient(app).post(
            "/api/projects/P1/public-folder-workflow/sync/execute",
            json={
                "preview_hash": "old",
                "confirmed": True,
                "confirm_directory_creation": True,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"] == "Public folder preview is stale."


def test_public_folder_workflow_auto_sync_api_returns_persisted_state() -> None:
    service = _FakeService(state=PublicFolderWorkflowState(project_id="P1", auto_sync_enabled=True))
    app.dependency_overrides[get_public_folder_workflow_service] = lambda: service
    try:
        response = TestClient(app).put(
            "/api/projects/P1/public-folder-workflow/auto-sync",
            json={"auto_sync_enabled": True},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["auto_sync_enabled"] is True


def _preview() -> PublicFolderWorkflowPreview:
    item = PublicFolderWorkflowItem(
        kind="file",
        relative_path=Path("Submitted Material/app.docx"),
        local_path=Path("local/app.docx"),
        public_path=Path("public/Open/2026/DL/app.docx"),
        action="add",
        status="ready",
        message="Will be copied.",
    )
    return PublicFolderWorkflowPreview(
        project_id="P1",
        operation_type="sync",
        status="ready",
        local_official_folder_path=Path("local/DL"),
        public_root=Path("public"),
        public_root_class="local_development_root",
        public_folder_year=2026,
        year_source="project_created_on",
        year_evidence="2026-06-30",
        public_open_path=Path("public/Open/2026/DL"),
        public_closed_path=Path("public/Closed/2026/DL"),
        target_path=None,
        items=(item,),
        blockers=tuple(),
        warnings=tuple(),
        conflicts=tuple(),
        required_confirmations=("create_missing_public_directories",),
        counts={"add": 1},
        preview_hash="hash",
        next_action="sync",
        auto_sync_enabled=False,
        sync_locked=False,
    )


class _FakeService:
    def __init__(
        self,
        *,
        preview: PublicFolderWorkflowPreview | None = None,
        state: PublicFolderWorkflowState | None = None,
        error: Exception | None = None,
    ) -> None:
        self._preview = preview or _preview()
        self._state = state or PublicFolderWorkflowState(project_id="P1")
        self._error = error

    def context(self, project_id: str) -> PublicFolderWorkflowContext:
        return PublicFolderWorkflowContext(
            project_id=project_id,
            auto_sync_enabled=False,
            sync_locked=False,
            submitted_at=None,
            public_root=Path("public"),
            public_root_class="local_development_root",
            public_folder_year=2026,
            year_source="project_created_on",
            year_evidence="2026-06-30",
            local_official_folder_path=Path("local/DL"),
            public_open_path=Path("public/Open/2026/DL"),
            public_closed_path=Path("public/Closed/2026/DL"),
            blockers=tuple(),
            warnings=tuple(),
        )

    def set_auto_sync(self, project_id: str, command) -> PublicFolderWorkflowState:
        return self._state

    def preview_sync(self, project_id: str) -> PublicFolderWorkflowPreview:
        return self._preview

    def execute_sync(self, project_id: str, command) -> PublicFolderWorkflowResult:
        if self._error:
            raise self._error
        return PublicFolderWorkflowResult(
            project_id=project_id,
            operation_id="operation-1",
            operation_type="sync",
            status="completed",
            counts={"add": 1},
            errors=tuple(),
            preview=self._preview,
        )

    def preview_submit(self, project_id: str) -> PublicFolderWorkflowPreview:
        return self._preview

    def execute_submit(self, project_id: str, command) -> PublicFolderWorkflowResult:
        return self.execute_sync(project_id, command)

    def preview_pull(self, project_id: str) -> PublicFolderWorkflowPreview:
        return self._preview

    def execute_pull(self, project_id: str, command) -> PublicFolderWorkflowResult:
        return self.execute_sync(project_id, command)
