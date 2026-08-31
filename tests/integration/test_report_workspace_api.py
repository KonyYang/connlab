from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend.api.dependencies import (
    get_customer_report_projection_service,
    get_current_report_update_service,
    get_equipment_report_update_service,
    get_llcr_result_dataset_service,
    get_report_workspace_service,
    get_settings,
    get_test_report_template_resource_store,
)
from backend.application.customer_report_projection_service import (
    CustomerReportGenerationResult,
    CustomerReportProjectionState,
)
from backend.api.main import app
from backend.application.report_workspace_service import ReportWorkspaceState
from backend.application.current_report_update_service import (
    CurrentReportArtifact,
    CurrentEquipmentListUpdateResult,
    CurrentReportUpdatePreview,
    CurrentReportUpdateResult,
)
from backend.application.equipment_report_update_service import (
    EquipmentListPreview,
    EquipmentListReportRow,
)
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
    (templates / "E-4515_F Customer Test Report.docx").write_bytes(b"customer-template")
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
        customer = client.get(
            "/api/projects/P1/report-workspace/drafts/report-1/customer-report"
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
    assert customer.status_code == 200
    assert customer.content == b"customer-report"
    assert customer.headers["content-disposition"].endswith(
        'filename="report-CR_Customer.docx"'
    )
    assert workspace_service.customer_command.report_revision_id == "report-1"
    assert workspace_service.customer_command.template_path == (
        templates / "E-4515_F Customer Test Report.docx"
    )


def test_current_report_llcr_preview_update_and_download(tmp_path: Path) -> None:
    report_path = tmp_path / "DL-001 Qualification Testing Report_Rev_A.docx"
    report_path.write_bytes(b"current-report")
    current_service = _CurrentReportUpdateService(report_path)
    app.dependency_overrides[get_current_report_update_service] = lambda: current_service
    client = TestClient(app)
    try:
        current = client.get("/api/projects/P1/report-workspace/current-report")
        preview = client.post(
            "/api/projects/P1/report-workspace/current-report/llcr/preview",
            json={"dataset_id": "dataset-1"},
        )
        updated = client.post(
            "/api/projects/P1/report-workspace/current-report/llcr",
            json={
                "dataset_id": "dataset-1",
                "expected_report_sha256": "a" * 64,
                "updated_by": "Even Yang",
            },
        )
        downloaded = client.get(
            "/api/projects/P1/report-workspace/current-report/download"
        )
    finally:
        app.dependency_overrides.clear()

    assert current.status_code == 200
    assert current.json()["mode"] == "official"
    assert current.json()["download_url"].endswith("/current-report/download")
    assert preview.status_code == 200
    assert preview.json()["status"] == "ready"
    assert preview.json()["current_report"]["file_sha256"] == "a" * 64
    assert updated.status_code == 200
    assert updated.json() == {
        "project_id": "P1",
        "dataset_id": "dataset-1",
        "file_name": report_path.name,
        "mode": "official",
        "changed": True,
        "current_sha256": "b" * 64,
        "archive_path": str(tmp_path / "History" / "Report" / "old.docx"),
        "updated_by": "Even Yang",
    }
    assert downloaded.content == b"current-report"
    assert current_service.command.expected_report_sha256 == "a" * 64


def test_current_managed_report_can_be_published_to_official_project_folder(
    tmp_path: Path,
) -> None:
    managed = tmp_path / "managed" / "DL-001 Report_Rev_A_Draft (9).docx"
    managed.parent.mkdir()
    managed.write_bytes(b"managed")
    official_folder = tmp_path / "official"
    official_folder.mkdir()
    current_service = _CurrentReportUpdateService(managed)
    current_service.report = CurrentReportArtifact(
        status="ready",
        mode="managed_draft",
        file_name=managed.name,
        file_path=managed,
        file_sha256="a" * 64,
        history_root=managed.parent / "History" / "Report",
        folder_path=managed.parent,
        official_folder_path=official_folder,
        can_publish_to_official=True,
    )
    app.dependency_overrides[get_current_report_update_service] = lambda: current_service
    client = TestClient(app)
    try:
        current = client.get("/api/projects/P1/report-workspace/current-report")
        published = client.post(
            "/api/projects/P1/report-workspace/current-report/publish",
            json={"expected_report_sha256": "a" * 64},
        )
    finally:
        app.dependency_overrides.clear()

    assert current.json()["can_publish_to_official"] is True
    assert current.json()["folder_path"] == str(managed.parent)
    assert current.json()["official_folder_path"] == str(official_folder)
    assert published.status_code == 200
    assert published.json()["mode"] == "official"
    assert published.json()["file_name"] == "DL-001 Report_Rev_A.docx"
    assert current_service.publish_command.expected_report_sha256 == "a" * 64


def test_equipment_list_preview_and_controlled_update(tmp_path: Path) -> None:
    report_path = tmp_path / "DL-001 Qualification Testing Report_Rev_A.docx"
    report_path.write_bytes(b"current-report")
    report = CurrentReportArtifact(
        status="ready",
        mode="official",
        file_name=report_path.name,
        file_path=report_path,
        file_sha256="a" * 64,
        history_root=tmp_path / "History" / "Report",
    )
    equipment_service = _EquipmentService(report, tmp_path)
    app.dependency_overrides[get_equipment_report_update_service] = lambda: equipment_service
    client = TestClient(app)
    try:
        preview = client.post(
            "/api/projects/P1/report-workspace/current-report/equipment/preview",
            json={"external_overrides": []},
        )
        updated = client.post(
            "/api/projects/P1/report-workspace/current-report/equipment",
            json={
                "expected_report_sha256": "a" * 64,
                "expected_source_sha256": "b" * 64,
                "expected_catalog_sha256": "c" * 64,
                "acknowledge_expired": True,
                "external_overrides": [],
                "updated_by": "Lab User",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert preview.status_code == 200
    assert preview.json()["rows"][0]["id_number"] == "DG-Q-0033"
    assert preview.json()["requires_expired_acknowledgement"] is True
    assert updated.status_code == 200
    assert updated.json()["file_name"] == report_path.name
    assert equipment_service.command.acknowledge_expired is True


def test_current_customer_report_state_generate_and_download(tmp_path: Path) -> None:
    customer_path = tmp_path / "DL-001-CR Qualification Testing Report_Rev_A.docx"
    customer_path.write_bytes(b"customer-report")
    customer_service = _CustomerProjectionService(customer_path, mode="official")
    templates = tmp_path / "templates"
    templates.mkdir()
    (templates / "E-4515_F Customer Test Report.docx").write_bytes(b"template")
    app.dependency_overrides[get_customer_report_projection_service] = (
        lambda: customer_service
    )
    app.dependency_overrides[get_test_report_template_resource_store] = lambda: _Store(
        templates
    )
    client = TestClient(app)
    try:
        state = client.get(
            "/api/projects/P1/report-workspace/current-customer-report"
        )
        generated = client.post(
            "/api/projects/P1/report-workspace/current-customer-report",
            json={
                "expected_internal_report_sha256": "a" * 64,
                "expected_customer_report_sha256": "b" * 64,
            },
        )
        downloaded = client.get(
            "/api/projects/P1/report-workspace/current-customer-report/download"
        )
    finally:
        app.dependency_overrides.clear()

    assert state.status_code == 200
    assert state.json()["status"] == "stale"
    assert state.json()["download_url"].endswith(
        "/current-customer-report/download"
    )
    assert generated.status_code == 200
    assert generated.json()["file_name"] == customer_path.name
    assert generated.json()["archive_path"].endswith("old.docx")
    assert customer_service.command.expected_internal_report_sha256 == "a" * 64
    assert customer_service.command.expected_customer_report_sha256 == "b" * 64
    assert downloaded.content == b"customer-report"


def test_managed_customer_report_generation_returns_browser_download(
    tmp_path: Path,
) -> None:
    customer_path = tmp_path / "DL-001-CR Qualification Testing Report_Rev_A_Draft.docx"
    customer_path.write_bytes(b"customer-download")
    customer_service = _CustomerProjectionService(
        customer_path,
        mode="managed_download",
    )
    templates = tmp_path / "templates"
    templates.mkdir()
    (templates / "E-4515_F Customer Test Report.docx").write_bytes(b"template")
    app.dependency_overrides[get_customer_report_projection_service] = (
        lambda: customer_service
    )
    app.dependency_overrides[get_test_report_template_resource_store] = lambda: _Store(
        templates
    )
    client = TestClient(app)
    try:
        generated = client.post(
            "/api/projects/P1/report-workspace/current-customer-report",
            json={
                "expected_internal_report_sha256": "a" * 64,
                "expected_customer_report_sha256": None,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert generated.status_code == 200
    assert generated.content == b"customer-download"
    assert "attachment" in generated.headers["content-disposition"]


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

    def generate_customer_report(self, command):
        self.customer_command = command
        path = command.output_dir / "P1" / "report-CR_Customer.docx"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"customer-report")
        return SimpleNamespace(
            source_report_revision_id=command.report_revision_id,
            file_name=path.name,
            file_path=str(path),
        )


class _CurrentReportUpdateService:
    def __init__(self, report_path: Path):
        self.report = CurrentReportArtifact(
            status="ready",
            mode="official",
            file_name=report_path.name,
            file_path=report_path,
            file_sha256="a" * 64,
            history_root=report_path.parent / "History" / "Report",
        )

    def get_current_report(self, project_id):
        return self.report

    def preview_llcr_update(self, *, project_id, dataset_id):
        return CurrentReportUpdatePreview(
            project_id=project_id,
            dataset_id=dataset_id,
            status="ready",
            current_report=self.report,
            blockers=tuple(),
            warnings=tuple(),
        )

    def update_llcr(self, command):
        self.command = command
        return CurrentReportUpdateResult(
            project_id=command.project_id,
            dataset_id=command.dataset_id,
            file_name=self.report.file_name or "",
            mode=self.report.mode or "",
            changed=True,
            current_sha256="b" * 64,
            archive_path=self.report.file_path.parent / "History" / "Report" / "old.docx",
            updated_by=command.updated_by,
        )

    def publish_managed_report(self, command):
        self.publish_command = command
        assert self.report.official_folder_path is not None
        target = self.report.official_folder_path / "DL-001 Report_Rev_A.docx"
        target.write_bytes(self.report.file_path.read_bytes())
        return CurrentReportArtifact(
            status="ready",
            mode="official",
            file_name=target.name,
            file_path=target,
            file_sha256="a" * 64,
            history_root=target.parent / "History" / "Report",
            folder_path=target.parent,
            official_folder_path=target.parent,
        )


class _EquipmentService:
    def __init__(self, report: CurrentReportArtifact, tmp_path: Path) -> None:
        self.report = report
        self.tmp_path = tmp_path

    def preview(self, *, project_id, external_overrides=tuple()):
        self.overrides = external_overrides
        return EquipmentListPreview(
            project_id=project_id,
            status="ready",
            current_report=self.report,
            source_file_name="EquipmentID.docx",
            source_sha256="b" * 64,
            catalog_file_name="equipment.xlsx",
            catalog_sha256="c" * 64,
            rows=(
                EquipmentListReportRow(
                    source_reference="DG-Q-0033",
                    status="matched",
                    item="Digital multimeter",
                    manufacturer="Keysight",
                    id_number="DG-Q-0033",
                    last_calibration="01 Jan 2025",
                    calibration_due="01 Jan 2026",
                    source_sheet="All Equip.",
                    expired=True,
                ),
            ),
            blockers=tuple(),
            warnings=("Calibration is expired for DG-Q-0033 (01 Jan 2026).",),
            requires_expired_acknowledgement=True,
        )

    def update(self, command):
        self.command = command
        return CurrentEquipmentListUpdateResult(
            project_id=command.project_id,
            file_name=self.report.file_name or "",
            mode="official",
            changed=True,
            current_sha256="d" * 64,
            archive_path=self.tmp_path / "History" / "Report" / "old.docx",
            updated_by=command.updated_by,
        )


class _CustomerProjectionService:
    def __init__(self, path: Path, *, mode: str) -> None:
        self.path = path
        self.mode = mode

    def get_state(self, project_id: str):
        return CustomerReportProjectionState(
            project_id=project_id,
            status="stale" if self.mode == "official" else "missing",
            mode=self.mode,
            file_name=self.path.name if self.mode == "official" else None,
            file_path=self.path if self.mode == "official" else None,
            file_sha256="b" * 64 if self.mode == "official" else None,
            internal_report_sha256="a" * 64,
            generated_from_internal_sha256="c" * 64 if self.mode == "official" else None,
            can_generate=True,
            download_url_available=self.mode == "official",
            blockers=tuple(),
            warnings=("The Internal Report changed.",) if self.mode == "official" else tuple(),
        )

    def generate(self, command):
        self.command = command
        return CustomerReportGenerationResult(
            project_id=command.project_id,
            mode=self.mode,
            file_name=self.path.name,
            file_path=self.path,
            file_sha256="d" * 64,
            source_report_sha256="a" * 64,
            changed=True,
            archive_path=(self.path.parent / "History" / "Report" / "old.docx")
            if self.mode == "official"
            else None,
        )


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
