"""Report Workspace routes for LLCR datasets and Internal Report revisions."""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

from backend.api.dependencies import (
    get_current_report_update_service,
    get_equipment_report_update_service,
    get_llcr_result_dataset_service,
    get_report_workspace_service,
    get_settings,
    get_test_report_template_resource_store,
)
from backend.application.current_report_update_service import (
    CurrentReportArtifact,
    CurrentReportFileConflictError,
    CurrentReportUpdateError,
    CurrentReportUpdatePreview,
    CurrentReportUpdateResult,
    CurrentReportUpdateService,
    PublishManagedReportCommand,
    UpdateCurrentLlcrReportCommand,
)
from backend.application.equipment_report_update_service import (
    EquipmentListExternalOverride,
    EquipmentListPreview,
    EquipmentListUpdateCommand,
    EquipmentReportUpdateError,
    EquipmentReportUpdateService,
)
from backend.application.llcr_result_dataset_service import (
    ConfirmLlcrImportCommand,
    InspectLlcrImportCommand,
    LlcrImportConflictError,
    LlcrResultDatasetService,
)
from backend.application.report_workspace_service import (
    GenerateCustomerReportCommand,
    GenerateInitialReportCommand,
    GenerateLlcrReportCommand,
    ReportWorkspaceError,
    ReportWorkspaceService,
)
from backend.application.test_report_template_resource import (
    TestReportTemplateResourceError,
    TestReportTemplateResourceStore,
    resolve_customer_report_template_path,
    resolve_test_report_template_path,
)
from backend.domain.result_dataset_models import (
    LlcrConfirmationDecision,
    LlcrImportPreview,
    ReportDraftRevision,
    ResultDatasetRevision,
)
from backend.shared.config import Settings


router = APIRouter(tags=["report-workspace"])


class LlcrDecisionRequest(BaseModel):
    result_id: str
    outcome: str
    override_reason: str | None = None


class ConfirmLlcrImportRequest(BaseModel):
    preview_id: str
    confirmed_by: str = "Lab User"
    decisions: list[LlcrDecisionRequest]


class GenerateInitialReportRequest(BaseModel):
    created_by: str = "Lab User"


class GenerateLlcrReportRequest(BaseModel):
    dataset_id: str
    created_by: str = "Lab User"


class PreviewCurrentLlcrReportRequest(BaseModel):
    dataset_id: str


class UpdateCurrentLlcrReportRequest(BaseModel):
    dataset_id: str
    expected_report_sha256: str = Field(min_length=64, max_length=64)
    updated_by: str = "Lab User"


class PublishManagedReportRequest(BaseModel):
    expected_report_sha256: str = Field(min_length=64, max_length=64)


class EquipmentExternalOverrideRequest(BaseModel):
    source_reference: str
    item: str
    manufacturer: str
    id_number: str
    last_calibration: str
    calibration_due: str
    reason: str


class PreviewEquipmentListRequest(BaseModel):
    external_overrides: list[EquipmentExternalOverrideRequest] = Field(default_factory=list)


class UpdateEquipmentListRequest(PreviewEquipmentListRequest):
    expected_report_sha256: str = Field(min_length=64, max_length=64)
    expected_source_sha256: str = Field(min_length=64, max_length=64)
    expected_catalog_sha256: str = Field(min_length=64, max_length=64)
    acknowledge_expired: bool = False
    updated_by: str = "Lab User"


@router.get("/api/projects/{project_id}/report-workspace")
def get_report_workspace(
    project_id: str,
    service: ReportWorkspaceService = Depends(get_report_workspace_service),
) -> dict:
    state = service.get_state(project_id)
    return {
        "project_id": state.project_id,
        "basic_information_status": state.basic_information_status,
        "confirmed_basic_information_version": state.confirmed_basic_information_version,
        "active_confirmed_matrix_id": state.active_confirmed_matrix_id,
        "active_confirmed_matrix_revision": state.active_confirmed_matrix_revision,
        "latest_report_revision": (
            _report_response(state.latest_report_revision)
            if state.latest_report_revision is not None
            else None
        ),
        "datasets": [_dataset_response(item) for item in state.datasets],
        "report_revisions": [_report_response(item) for item in state.report_revisions],
    }


@router.get("/api/projects/{project_id}/report-workspace/current-report")
def get_current_report(
    project_id: str,
    service: CurrentReportUpdateService = Depends(get_current_report_update_service),
) -> dict:
    try:
        report = service.get_current_report(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    return _current_report_response(project_id, report)


@router.post("/api/projects/{project_id}/report-workspace/current-report/publish")
def publish_managed_report(
    project_id: str,
    request: PublishManagedReportRequest,
    service: CurrentReportUpdateService = Depends(get_current_report_update_service),
) -> dict:
    try:
        report = service.publish_managed_report(
            PublishManagedReportCommand(
                project_id=project_id,
                expected_report_sha256=request.expected_report_sha256,
            )
        )
    except (CurrentReportUpdateError, CurrentReportFileConflictError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    return _current_report_response(project_id, report)


@router.post(
    "/api/projects/{project_id}/report-workspace/current-report/llcr/preview"
)
def preview_current_report_llcr_update(
    project_id: str,
    request: PreviewCurrentLlcrReportRequest,
    service: CurrentReportUpdateService = Depends(get_current_report_update_service),
) -> dict:
    try:
        preview = service.preview_llcr_update(
            project_id=project_id,
            dataset_id=request.dataset_id,
        )
    except CurrentReportUpdateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    return _current_report_preview_response(project_id, preview)


@router.post("/api/projects/{project_id}/report-workspace/current-report/llcr")
def update_current_report_llcr(
    project_id: str,
    request: UpdateCurrentLlcrReportRequest,
    service: CurrentReportUpdateService = Depends(get_current_report_update_service),
) -> dict:
    try:
        result = service.update_llcr(
            UpdateCurrentLlcrReportCommand(
                project_id=project_id,
                dataset_id=request.dataset_id,
                expected_report_sha256=request.expected_report_sha256,
                updated_by=request.updated_by,
            )
        )
    except (CurrentReportUpdateError, CurrentReportFileConflictError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    return _current_report_update_response(result)


@router.get("/api/projects/{project_id}/report-workspace/current-report/download")
def download_current_report(
    project_id: str,
    service: CurrentReportUpdateService = Depends(get_current_report_update_service),
) -> FileResponse:
    try:
        report = service.get_current_report(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    if report.status != "ready" or report.file_path is None or report.file_name is None:
        raise HTTPException(status_code=409, detail="The current internal report is unavailable.")
    return FileResponse(
        report.file_path,
        filename=report.file_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.post(
    "/api/projects/{project_id}/report-workspace/current-report/equipment/preview"
)
def preview_current_report_equipment_update(
    project_id: str,
    request: PreviewEquipmentListRequest,
    service: EquipmentReportUpdateService = Depends(get_equipment_report_update_service),
) -> dict:
    try:
        preview = service.preview(
            project_id=project_id,
            external_overrides=_equipment_overrides(request.external_overrides),
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    return _equipment_preview_response(project_id, preview)


@router.post("/api/projects/{project_id}/report-workspace/current-report/equipment")
def update_current_report_equipment_list(
    project_id: str,
    request: UpdateEquipmentListRequest,
    service: EquipmentReportUpdateService = Depends(get_equipment_report_update_service),
) -> dict:
    try:
        result = service.update(
            EquipmentListUpdateCommand(
                project_id=project_id,
                expected_report_sha256=request.expected_report_sha256,
                expected_source_sha256=request.expected_source_sha256,
                expected_catalog_sha256=request.expected_catalog_sha256,
                acknowledge_expired=request.acknowledge_expired,
                external_overrides=_equipment_overrides(request.external_overrides),
                updated_by=request.updated_by,
            )
        )
    except (EquipmentReportUpdateError, CurrentReportFileConflictError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    return {
        "project_id": result.project_id,
        "file_name": result.file_name,
        "mode": result.mode,
        "changed": result.changed,
        "current_sha256": result.current_sha256,
        "archive_path": (
            str(result.archive_path) if result.archive_path is not None else None
        ),
        "updated_by": result.updated_by,
    }


@router.post("/api/projects/{project_id}/report-workspace/llcr/inspect")
async def inspect_llcr_result(
    project_id: str,
    file: UploadFile = File(...),
    imported_by: str = Form("Lab User"),
    service: LlcrResultDatasetService = Depends(get_llcr_result_dataset_service),
) -> dict:
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="LLCR workbook exceeds the 50 MB limit.")
    try:
        preview = service.inspect(
            InspectLlcrImportCommand(
                project_id=project_id,
                file_name=file.filename or "LLCR.xlsx",
                content=content,
                imported_by=imported_by,
            )
        )
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _preview_response(preview)


@router.post("/api/projects/{project_id}/report-workspace/llcr/confirm")
def confirm_llcr_result(
    project_id: str,
    request: ConfirmLlcrImportRequest = Body(...),
    service: LlcrResultDatasetService = Depends(get_llcr_result_dataset_service),
) -> dict:
    try:
        dataset = service.confirm(
            ConfirmLlcrImportCommand(
                project_id=project_id,
                preview_id=request.preview_id,
                confirmed_by=request.confirmed_by,
                decisions=tuple(
                    LlcrConfirmationDecision(
                        item.result_id,
                        item.outcome,
                        item.override_reason,
                    )
                    for item in request.decisions
                ),
            )
        )
    except LlcrImportConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _dataset_response(dataset)


@router.delete(
    "/api/projects/{project_id}/report-workspace/llcr/previews/{preview_id}",
    status_code=204,
)
def cancel_llcr_preview(
    project_id: str,
    preview_id: str,
    service: LlcrResultDatasetService = Depends(get_llcr_result_dataset_service),
) -> Response:
    try:
        service.cancel(project_id=project_id, preview_id=preview_id)
    except LlcrImportConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return Response(status_code=204)


@router.post("/api/projects/{project_id}/report-workspace/initial-drafts")
def generate_initial_report(
    project_id: str,
    request: GenerateInitialReportRequest = Body(default=GenerateInitialReportRequest()),
    service: ReportWorkspaceService = Depends(get_report_workspace_service),
    settings: Settings = Depends(get_settings),
    template_store: TestReportTemplateResourceStore = Depends(
        get_test_report_template_resource_store
    ),
) -> dict:
    try:
        template = resolve_test_report_template_path(template_store)
        revision = service.generate_initial(
            GenerateInitialReportCommand(
                project_id,
                template,
                settings.data_dir / "generated_test_reports",
                request.created_by,
            )
        )
    except (TestReportTemplateResourceError, ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _report_response(revision)


@router.post("/api/projects/{project_id}/report-workspace/llcr-drafts")
def generate_llcr_report(
    project_id: str,
    request: GenerateLlcrReportRequest,
    service: ReportWorkspaceService = Depends(get_report_workspace_service),
    settings: Settings = Depends(get_settings),
    template_store: TestReportTemplateResourceStore = Depends(
        get_test_report_template_resource_store
    ),
) -> dict:
    try:
        template_path = None
        if service.get_state(project_id).latest_report_revision is None:
            template_path = resolve_test_report_template_path(template_store)
        revision = service.generate_llcr_report(
            GenerateLlcrReportCommand(
                project_id=project_id,
                dataset_id=request.dataset_id,
                output_dir=settings.data_dir / "generated_test_reports",
                created_by=request.created_by,
                template_path=template_path,
            )
        )
    except ReportWorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (TestReportTemplateResourceError, ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _report_response(revision)


@router.get(
    "/api/projects/{project_id}/report-workspace/drafts/{report_revision_id}/download"
)
def download_report_revision(
    project_id: str,
    report_revision_id: str,
    service: ReportWorkspaceService = Depends(get_report_workspace_service),
) -> FileResponse:
    try:
        revision = service.get_report_revision(project_id, report_revision_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    return FileResponse(
        revision.file_path,
        filename=revision.file_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.api_route(
    "/api/projects/{project_id}/report-workspace/drafts/"
    "{report_revision_id}/customer-report",
    methods=["GET", "POST"],
)
def generate_customer_report(
    project_id: str,
    report_revision_id: str,
    service: ReportWorkspaceService = Depends(get_report_workspace_service),
    settings: Settings = Depends(get_settings),
    template_store: TestReportTemplateResourceStore = Depends(
        get_test_report_template_resource_store
    ),
) -> FileResponse:
    download_root = settings.data_dir / "customer_report_downloads"
    download_root.mkdir(parents=True, exist_ok=True)
    temporary_root = Path(tempfile.mkdtemp(prefix="customer-report-", dir=download_root))
    try:
        template_path = resolve_customer_report_template_path(template_store)
        result = service.generate_customer_report(
            GenerateCustomerReportCommand(
                project_id=project_id,
                report_revision_id=report_revision_id,
                template_path=template_path,
                output_dir=temporary_root,
            )
        )
    except LookupError as exc:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    except (TestReportTemplateResourceError, ReportWorkspaceError, ValueError) as exc:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise
    return FileResponse(
        result.file_path,
        filename=result.file_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        background=BackgroundTask(shutil.rmtree, temporary_root, ignore_errors=True),
    )


def _preview_response(preview: LlcrImportPreview) -> dict:
    return {
        "preview_id": preview.preview_id,
        "project_id": preview.project_id,
        "confirmed_matrix_id": preview.confirmed_matrix_id,
        "confirmed_matrix_revision": preview.confirmed_matrix_revision,
        "source": {
            "file_name": preview.source.file_name,
            "sha256": preview.source.sha256,
            "size_bytes": preview.source.size_bytes,
        },
        "parser_profile_version": preview.parser_profile_version,
        "detected_sheets": list(preview.detected_sheets),
        "can_confirm": preview.can_confirm,
        "sample_count": len({
            (entry.confirmed_group_id, measurement.sample_index)
            for entry in preview.entries
            for measurement in entry.measurements
        }),
        "test_point_count": len({
            (entry.confirmed_group_id, measurement.position)
            for entry in preview.entries
            for measurement in entry.measurements
        }),
        "result_count": len(preview.entries),
        "entries": [_entry_response(item) for item in preview.entries],
        "diagnostics": [
            {
                "code": item.code,
                "severity": item.severity,
                "message": item.message,
                "group_label": item.group_label,
                "step_token": item.step_token,
            }
            for item in preview.diagnostics
        ],
    }


def _entry_response(item) -> dict:
    return {
        "result_id": item.result_id,
        "group_label": item.group_label,
        "matrix_step_token": item.matrix_step_token,
        "stage": item.stage,
        "stage_label": item.stage_label,
        "requirement": item.requirement,
        "unit": item.requirement_unit,
        "measurement_count": len(item.measurements),
        "summary_min": str(item.summary_min),
        "summary_max": str(item.summary_max),
        "summary_average": str(item.summary_average),
        "provisional_outcome": item.provisional_outcome,
        "confirmed_outcome": item.confirmed_outcome,
        "override_reason": item.override_reason,
        "source_range": item.source_range,
        "report_target": f"Group {item.group_label} / Step {item.matrix_step_token} / Result + Comment",
    }


def _dataset_response(item: ResultDatasetRevision) -> dict:
    return {
        "dataset_id": item.dataset_id,
        "dataset_type": item.dataset_type,
        "revision": item.revision,
        "project_id": item.project_id,
        "confirmed_matrix_id": item.confirmed_matrix_id,
        "confirmed_matrix_revision": item.confirmed_matrix_revision,
        "source_file_name": item.source.file_name,
        "source_sha256": item.source.sha256,
        "parser_profile_version": item.parser_profile_version,
        "validation_status": item.validation_status,
        "confirmed_at": item.confirmed_at,
        "confirmed_by": item.confirmed_by,
        "entries": [_entry_response(entry) for entry in item.payload.entries],
    }


def _report_response(item: ReportDraftRevision) -> dict:
    return {
        "report_revision_id": item.report_revision_id,
        "revision": item.revision,
        "file_name": item.file_name,
        "file_sha256": item.file_sha256,
        "size_bytes": item.size_bytes,
        "confirmed_matrix_id": item.confirmed_matrix_id,
        "result_dataset_id": item.result_dataset_id,
        "base_report_revision_id": item.base_report_revision_id,
        "created_at": item.created_at,
        "created_by": item.created_by,
        "download_url": (
            f"/api/projects/{item.project_id}/report-workspace/drafts/"
            f"{item.report_revision_id}/download"
        ),
    }


def _current_report_response(project_id: str, item: CurrentReportArtifact) -> dict:
    return {
        "status": item.status,
        "mode": item.mode,
        "file_name": item.file_name,
        "file_sha256": item.file_sha256,
        "report_revision_id": item.report_revision_id,
        "folder_path": str(item.folder_path) if item.folder_path is not None else None,
        "official_folder_path": (
            str(item.official_folder_path)
            if item.official_folder_path is not None
            else None
        ),
        "can_publish_to_official": item.can_publish_to_official,
        "download_url": (
            f"/api/projects/{project_id}/report-workspace/current-report/download"
            if item.status == "ready"
            else None
        ),
    }


def _current_report_preview_response(
    project_id: str,
    preview: CurrentReportUpdatePreview,
) -> dict:
    return {
        "project_id": preview.project_id,
        "dataset_id": preview.dataset_id,
        "status": preview.status,
        "current_report": _current_report_response(project_id, preview.current_report),
        "blockers": list(preview.blockers),
        "warnings": list(preview.warnings),
    }


def _current_report_update_response(result: CurrentReportUpdateResult) -> dict:
    return {
        "project_id": result.project_id,
        "dataset_id": result.dataset_id,
        "file_name": result.file_name,
        "mode": result.mode,
        "changed": result.changed,
        "current_sha256": result.current_sha256,
        "archive_path": str(result.archive_path) if result.archive_path is not None else None,
        "updated_by": result.updated_by,
    }


def _equipment_overrides(
    items: list[EquipmentExternalOverrideRequest],
) -> tuple[EquipmentListExternalOverride, ...]:
    return tuple(
        EquipmentListExternalOverride(
            source_reference=item.source_reference,
            item=item.item,
            manufacturer=item.manufacturer,
            id_number=item.id_number,
            last_calibration=item.last_calibration,
            calibration_due=item.calibration_due,
            reason=item.reason,
        )
        for item in items
    )


def _equipment_preview_response(project_id: str, preview: EquipmentListPreview) -> dict:
    return {
        "project_id": preview.project_id,
        "status": preview.status,
        "current_report": _current_report_response(project_id, preview.current_report),
        "source_file_name": preview.source_file_name,
        "source_sha256": preview.source_sha256,
        "catalog_file_name": preview.catalog_file_name,
        "catalog_sha256": preview.catalog_sha256,
        "rows": [
            {
                "source_reference": row.source_reference,
                "status": row.status,
                "item": row.item,
                "manufacturer": row.manufacturer,
                "id_number": row.id_number,
                "last_calibration": row.last_calibration,
                "calibration_due": row.calibration_due,
                "source_sheet": row.source_sheet,
                "expired": row.expired,
                "external_reason": row.external_reason,
            }
            for row in preview.rows
        ],
        "blockers": list(preview.blockers),
        "warnings": list(preview.warnings),
        "requires_expired_acknowledgement": preview.requires_expired_acknowledgement,
    }
