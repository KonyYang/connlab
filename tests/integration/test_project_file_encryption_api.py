from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import get_project_file_encryption_service
from backend.api.main import app
from backend.application.project_file_encryption_service import (
    ProjectFileEncryptionItemResult,
    ProjectFileEncryptionPlanItem,
    ProjectFileEncryptionPreview,
    ProjectFileEncryptionResult,
)


def test_preview_exposes_names_and_actions_without_absolute_paths() -> None:
    service = _EncryptionService()
    app.dependency_overrides[get_project_file_encryption_service] = lambda: service
    try:
        response = TestClient(app).post("/api/projects/P1/file-encryption/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert service.preview_project_ids == ["P1"]
    assert body["status"] == "conflict"
    assert body["conflict_count"] == 1
    assert body["items"] == [
        {
            "file_name": "record.docx",
            "location": "test_results",
            "office_kind": "word",
            "mode": "secured_copy",
            "conflict": True,
        }
    ]
    assert "D:\\Secret" not in response.text


def test_execute_accepts_only_plan_token_and_conflict_action() -> None:
    service = _EncryptionService()
    app.dependency_overrides[get_project_file_encryption_service] = lambda: service
    try:
        response = TestClient(app).post(
            "/api/projects/P1/file-encryption/execute",
            json={"expected_plan_token": "token-1", "conflict_action": "skip"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert service.commands == [("P1", "token-1", "skip")]
    assert response.json()["skipped_count"] == 1


class _EncryptionService:
    def __init__(self) -> None:
        self.preview_project_ids: list[str] = []
        self.commands: list[tuple[str, str, str]] = []

    def preview(self, project_id: str) -> ProjectFileEncryptionPreview:
        self.preview_project_ids.append(project_id)
        return ProjectFileEncryptionPreview(
            project_id=project_id,
            status="conflict",
            plan_token="token-1",
            items=(
                ProjectFileEncryptionPlanItem(
                    source_path=Path("D:/Secret/record.docx"),
                    target_path=Path("D:/Secret/record_Secured.docx"),
                    file_name="record.docx",
                    location="test_results",
                    office_kind="word",
                    mode="secured_copy",
                    conflict=True,
                    source_fingerprint="source",
                    target_fingerprint="target",
                ),
            ),
            blockers=(),
            warnings=("Nonrecursive scan.",),
        )

    def execute(self, command) -> ProjectFileEncryptionResult:
        self.commands.append(
            (command.project_id, command.expected_plan_token, command.conflict_action)
        )
        return ProjectFileEncryptionResult(
            project_id=command.project_id,
            encrypted_count=0,
            skipped_count=1,
            failed_count=0,
            items=(
                ProjectFileEncryptionItemResult(
                    file_name="record.docx",
                    location="test_results",
                    status="skipped",
                    message="Existing secured file was kept; source was not changed.",
                ),
            ),
        )

