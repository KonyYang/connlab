from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import get_project_folder_open_service
from backend.api.main import app
from backend.application.project_folder_open_service import ProjectFolderOpenResult


def test_open_local_project_folder_uses_backend_resolved_project_id() -> None:
    service = _OpenService()
    app.dependency_overrides[get_project_folder_open_service] = lambda: service
    try:
        response = TestClient(app).post("/api/projects/P1/folder/open-local")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert service.project_ids == ["P1"]
    assert response.json() == {
        "project_id": "P1",
        "status": "unsupported",
        "message": "Project folder path copied. Open it in File Explorer.",
        "local_official_folder_path": str(Path("D:/Projects/P1")),
    }


class _OpenService:
    def __init__(self) -> None:
        self.project_ids: list[str] = []

    def open_local_project_folder(self, project_id: str) -> ProjectFolderOpenResult:
        self.project_ids.append(project_id)
        return ProjectFolderOpenResult(
            project_id=project_id,
            status="unsupported",
            message="Project folder path copied. Open it in File Explorer.",
            local_official_folder_path=Path("D:/Projects/P1"),
        )
