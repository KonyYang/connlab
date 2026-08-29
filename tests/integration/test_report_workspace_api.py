from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import (
    get_llcr_result_dataset_service,
    get_report_workspace_service,
    get_settings,
    get_test_report_template_resource_store,
)
from backend.api.main import app
from backend.application.report_workspace_service import ReportWorkspaceState
from backend.domain import ExternalResource, ExternalResourceType, ExternalResourceValidationStatus
from backend.domain.result_dataset_models import LlcrImportPreview, ReportDraftRevision
from backend.shared.config import Settings
from tests.unit.test_result_dataset_repository import _dataset


def test_report_workspace_llcr_preview_confirm_generate_and_download(tmp_path: Path) -> None:
    dataset = _dataset("dataset-1", 1)
    preview = LlcrImportPreview(
        preview_id="preview-1",
        project_id="P1",
        confirmed_matrix_id="matrix-1",
        confirmed_matrix_revision=3,
        source=dataset.source,
        parser_profile_version=dataset.parser_profile_version,
        detected_sheets=("Summary", "SIG"),
        entries=tuple(replace(entry, confirmed_outcome=None) for entry in dataset.payload.entries),
    )
    report_file = tmp_path / "report.docx"
    report_file.write_bytes(b"report-docx")
    report = ReportDraftRevision(
        report_revision_id="report-1",
        project_id="P1",
        revision=1,
        file_name="report.docx",
        file_path=str(report_file),
        file_sha256="b" * 64,
        size_bytes=11,
        confirmed_matrix_id="matrix-1",
        result_dataset_id="dataset-1",
        base_report_revision_id=None,
        created_at="2026-08-29T09:00:00Z",
        created_by="Even Yang",
    )
    llcr_service = _LlcrService(preview, dataset)
    workspace_service = _WorkspaceService(report, dataset)
    templates = tmp_path / "templates"
    templates.mkdir()
    (templates / "E-3707_H Laboratory Test Report.docx").write_bytes(b"template")
    app.dependency_overrides[get_llcr_result_dataset_service] = lambda: llcr_service
    app.dependency_overrides[get_report_workspace_service] = lambda: workspace_service
    app.dependency_overrides[get_settings] = lambda: Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=templates,
        database_path=tmp_path / "db.sqlite3",
    )
    app.dependency_overrides[get_test_report_template_resource_store] = lambda: _Store(templates)
    client = TestClient(app)
    try:
        inspected = client.post(
            "/api/projects/P1/report-workspace/llcr/inspect",
            files={"file": ("LLCR.xlsx", b"workbook", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"imported_by": "Even Yang"},
        )
        cancelled = client.delete(
            "/api/projects/P1/report-workspace/llcr/previews/preview-1"
        )
        confirmed = client.post(
            "/api/projects/P1/report-workspace/llcr/confirm",
            json={
                "preview_id": "preview-1",
                "confirmed_by": "Even Yang",
                "decisions": [{"result_id": "group-1:row-1:2", "outcome": "pass"}],
            },
        )
        generated = client.post(
            "/api/projects/P1/report-workspace/llcr-drafts",
            json={"dataset_id": "dataset-1", "created_by": "Even Yang"},
        )
        state = client.get("/api/projects/P1/report-workspace")
        downloaded = client.get(
            "/api/projects/P1/report-workspace/drafts/report-1/download"
        )
    finally:
        app.dependency_overrides.clear()

    assert inspected.status_code == 200
    assert inspected.json()["can_confirm"] is True
    assert inspected.json()["entries"][0]["report_target"] == "Group 1 / Step 2 / Result + Comment"
    assert cancelled.status_code == 204
    assert llcr_service.cancelled == ("P1", "preview-1")
    assert confirmed.status_code == 200
    assert confirmed.json()["revision"] == 1
    assert generated.status_code == 200
    assert generated.json()["report_revision_id"] == "report-1"
    assert workspace_service.llcr_command.template_path == (
        templates / "E-3707_H Laboratory Test Report.docx"
    )
    assert state.json()["basic_information_status"] == "confirmed"
    assert downloaded.content == b"report-docx"


class _LlcrService:
    def __init__(self, preview, dataset):
        self.preview = preview
        self.dataset = dataset

    def inspect(self, command):
        self.inspect_command = command
        return self.preview

    def confirm(self, command):
        self.confirm_command = command
        return self.dataset

    def cancel(self, *, project_id, preview_id):
        self.cancelled = (project_id, preview_id)


class _WorkspaceService:
    def __init__(self, report, dataset):
        self.report = report
        self.dataset = dataset

    def get_state(self, project_id):
        return ReportWorkspaceState(
            project_id=project_id,
            basic_information_status="confirmed",
            confirmed_basic_information_version=2,
            active_confirmed_matrix_id="matrix-1",
            active_confirmed_matrix_revision=3,
            datasets=(self.dataset,),
            report_revisions=(),
            latest_report_revision=None,
        )

    def generate_initial(self, command):
        return self.report

    def generate_llcr_report(self, command):
        self.llcr_command = command
        return self.report

    def get_report_revision(self, project_id, report_revision_id):
        return self.report


class _Store:
    def __init__(self, path):
        self.path = path

    def get_by_type(self, resource_type):
        if resource_type is not ExternalResourceType.PROJECT_FOLDER_TEMPLATE:
            return None
        return ExternalResource(
            resource_id="template-folder",
            resource_type=resource_type,
            path=self.path,
            active=True,
            validation_status=ExternalResourceValidationStatus.VALID,
        )
