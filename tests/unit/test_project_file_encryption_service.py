from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.project_file_encryption_service import (
    ProjectFileEncryptionCommand,
    ProjectFileEncryptionPlanStaleError,
    ProjectFileEncryptionService,
)


@dataclass
class _WorkspaceRepository:
    record: OfficialWorkspaceRecord | None

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        return self.record if self.record and self.record.project_id == project_id else None


class _RecordingGateway:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str, bool]] = []

    def encrypt(self, *, item, password: str, history_root: Path, overwrite: bool):
        self.calls.append((item.source_path.name, password, str(history_root), overwrite))
        return item.target_path


def _workspace(tmp_path: Path) -> OfficialWorkspaceRecord:
    local = tmp_path / "DL-2026-08-007"
    official = local / "DL-2026-08-007 Example project"
    test_results = official / "Test results"
    test_results.mkdir(parents=True)
    return OfficialWorkspaceRecord(
        workspace_id="workspace-1",
        project_id="project-1",
        dl_number="DL-2026-08-007",
        local_workspace_path=local,
        source_book_path=local / "Source Book",
        official_folder_path=official,
        manifest_path=local / "manifest.json",
        template_source_path=tmp_path / "template",
        created_at="2026-08-31T10:00:00+08:00",
    )


def _touch(path: Path, content: str = "source") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_preview_scans_only_two_current_layers_and_applies_file_rules(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    official = workspace.official_folder_path
    results = official / "Test results"
    for name in ("report.doc", "report.docx", "slides.pptx"):
        _touch(official / name)
    for name in ("Fee Form.xlsx", "Customer Feedback.xls", "macro.docm", "deck.pptm"):
        _touch(official / name)
    for name in ("record.docx", "measurements.xlsx", "legacy.xls", "slides.pptx"):
        _touch(results / name)
    _touch(results / "record_Secured.docx", "existing secured")
    _touch(results / "nested" / "ignored.docx")
    _touch(official / "nested" / "ignored.pptx")

    service = ProjectFileEncryptionService(
        workspace_repository=_WorkspaceRepository(workspace),
        gateway=_RecordingGateway(),
    )

    preview = service.preview("project-1")

    assert preview.status == "conflict"
    assert [(item.location, item.file_name, item.conflict) for item in preview.items] == [
        ("official_root", "report.doc", False),
        ("official_root", "report.docx", False),
        ("official_root", "slides.pptx", False),
        ("test_results", "legacy.xls", False),
        ("test_results", "measurements.xlsx", False),
        ("test_results", "record.docx", True),
        ("test_results", "slides.pptx", False),
    ]
    assert all("nested" not in item.file_name for item in preview.items)
    assert preview.plan_token


def test_execute_uses_fixed_document_password_and_dl_excel_password(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    _touch(workspace.official_folder_path / "report.docx")
    _touch(workspace.official_folder_path / "Test results" / "measurements.xlsx")
    gateway = _RecordingGateway()
    service = ProjectFileEncryptionService(
        workspace_repository=_WorkspaceRepository(workspace),
        gateway=gateway,
    )
    preview = service.preview("project-1")

    result = service.execute(
        ProjectFileEncryptionCommand(
            project_id="project-1",
            expected_plan_token=preview.plan_token,
            conflict_action="overwrite",
        )
    )

    assert result.encrypted_count == 2
    assert result.skipped_count == 0
    assert [(name, password) for name, password, _, _ in gateway.calls] == [
        ("report.docx", "DGLAB"),
        ("measurements.xlsx", "202608007"),
    ]
    assert all("History\\Encryption" in history for _, _, history, _ in gateway.calls)


def test_execute_skip_leaves_conflicting_source_out_of_gateway(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    results = workspace.official_folder_path / "Test results"
    _touch(results / "a.docx")
    _touch(results / "a_Secured.docx")
    _touch(results / "b.docx")
    gateway = _RecordingGateway()
    service = ProjectFileEncryptionService(
        workspace_repository=_WorkspaceRepository(workspace),
        gateway=gateway,
    )
    preview = service.preview("project-1")

    result = service.execute(
        ProjectFileEncryptionCommand(
            project_id="project-1",
            expected_plan_token=preview.plan_token,
            conflict_action="skip",
        )
    )

    assert result.encrypted_count == 1
    assert result.skipped_count == 1
    assert [call[0] for call in gateway.calls] == ["b.docx"]


def test_execute_rejects_changed_plan_before_mutation(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    source = workspace.official_folder_path / "report.docx"
    _touch(source)
    gateway = _RecordingGateway()
    service = ProjectFileEncryptionService(
        workspace_repository=_WorkspaceRepository(workspace),
        gateway=gateway,
    )
    preview = service.preview("project-1")
    source.write_text("changed after preview", encoding="utf-8")

    with pytest.raises(ProjectFileEncryptionPlanStaleError):
        service.execute(
            ProjectFileEncryptionCommand(
                project_id="project-1",
                expected_plan_token=preview.plan_token,
                conflict_action="overwrite",
            )
        )

    assert gateway.calls == []

