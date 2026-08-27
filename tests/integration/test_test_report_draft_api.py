from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import (
    get_settings,
    get_test_report_draft_service,
    get_test_report_template_resource_store,
)
from backend.api.main import app
from backend.application.test_report_draft_service import (
    TestReportDraftGenerationResult,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ExternalResourceValidationStatus,
)
from backend.shared.config import Settings


def test_test_report_draft_api_resolves_settings_template_and_downloads_new_file(
    tmp_path: Path,
) -> None:
    template_folder = tmp_path / "templates"
    template_folder.mkdir()
    template = template_folder / "E-3707_H Laboratory Test Report.docx"
    template.write_bytes(b"approved")
    generated = tmp_path / "data" / "generated_test_reports" / "P1" / "draft.docx"
    generated.parent.mkdir(parents=True)
    generated.write_bytes(b"generated-docx")
    service = _Service(generated)
    app.dependency_overrides[get_settings] = lambda: Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "unused",
        database_path=tmp_path / "connlab.sqlite3",
    )
    app.dependency_overrides[get_test_report_template_resource_store] = lambda: _Store(
        template_folder
    )
    app.dependency_overrides[get_test_report_draft_service] = lambda: service
    client = TestClient(app)
    try:
        response = client.post("/api/projects/P1/test-report-draft/generate")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.content == b"generated-docx"
    assert "Initialization%20Report_Rev_A_Draft.docx" in response.headers[
        "content-disposition"
    ]
    assert response.headers["x-connlab-basic-information-version"] == "4"
    assert response.headers["x-connlab-confirmed-matrix-id"] == "cmv-4"
    assert service.command.template_path == template
    assert service.command.output_dir == tmp_path / "data" / "generated_test_reports"


class _Service:
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.command = None

    def generate(self, command):
        self.command = command
        return TestReportDraftGenerationResult(
            project_id="P1",
            confirmed_matrix_id="cmv-4",
            output_path=self.output_path,
            file_name="DL-001 Initialization Report_Rev_A_Draft.docx",
            confirmed_basic_information_version=4,
            confirmed_basic_information_source_signature_hash="abc123",
        )


class _Store:
    def __init__(self, path: Path) -> None:
        self.path = path

    def get_by_type(self, resource_type: ExternalResourceType):
        if resource_type is not ExternalResourceType.PROJECT_FOLDER_TEMPLATE:
            return None
        return ExternalResource(
            resource_id="template-folder",
            resource_type=resource_type,
            path=self.path,
            active=True,
            validation_status=ExternalResourceValidationStatus.VALID,
        )
