"""HTTP boundary for a zero-write live Matrix Editor XLSX export."""

from __future__ import annotations

from typing import Literal
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from backend.api.dependencies_matrix_editor_live_xlsx_export import (
    get_matrix_editor_live_xlsx_export_service,
    get_matrix_editor_live_xlsx_publication_service,
)
from backend.api.dependencies import get_settings
from backend.api.lifecycle_errors import lifecycle_readonly_conflict
from backend.application.matrix_editor_live_xlsx_export_service import (
    MatrixEditorLiveXlsxExportCell,
    MatrixEditorLiveXlsxExportError,
    MatrixEditorLiveXlsxExportGroup,
    MatrixEditorLiveXlsxExportRequest,
    MatrixEditorLiveXlsxExportRow,
    MatrixEditorLiveXlsxExportSchedule,
    MatrixEditorLiveXlsxExportService,
)
from backend.application.matrix_editor_live_xlsx_publication_service import (
    ExecuteMatrixEditorLiveXlsxPublicationCommand,
    MatrixEditorLiveXlsxPublicationBlockedError,
    MatrixEditorLiveXlsxPublicationConflictError,
    MatrixEditorLiveXlsxPublicationError,
    MatrixEditorLiveXlsxPublicationService,
    PreviewMatrixEditorLiveXlsxPublicationCommand,
)
from backend.application.project_lifecycle_write_guard import ProjectLifecycleReadonlyError
from backend.infrastructure.files.test_record_publication_gateway import (
    TestRecordPublicationTargetChangedError,
)
from backend.shared.config import Settings

router = APIRouter(tags=["matrix-editor-live-xlsx-export"])
MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class CellRequest(BaseModel):
    group_id: str = Field(min_length=1, max_length=128)
    step_text: str = Field(default="", max_length=255)


class GroupRequest(BaseModel):
    group_id: str = Field(min_length=1, max_length=128)
    group_key: str = Field(min_length=1, max_length=128)
    group_label: str = Field(min_length=1, max_length=255)
    sample_size: str = Field(default="", max_length=255)
    time_display: str = Field(default="", max_length=32)
    sample_note: str = Field(default="", max_length=2048)


class RowRequest(BaseModel):
    row_id: str = Field(min_length=1, max_length=128)
    test_item: str = Field(default="", max_length=2048)
    section: str = Field(default="", max_length=2048)
    test_method: str = Field(default="", max_length=2048)
    condition: str = Field(default="", max_length=2048)
    requirement: str = Field(default="", max_length=2048)
    cells: list[CellRequest]
    day_expression: str = Field(default="", max_length=64)


class ScheduleRequest(BaseModel):
    post_test_buffer_days: str = Field(default="", max_length=64)
    sample_received_date: str = Field(default="", max_length=64)
    planned_test_start_date: str = Field(default="", max_length=64)
    planned_test_complete_date: str = Field(default="", max_length=64)
    estimated_completion_date: str = Field(default="", max_length=64)


class LiveXlsxExportRequest(BaseModel):
    source: Literal["matrix_editor_current_ui_state"]
    project_reference: str = Field(min_length=1, max_length=255)
    groups: list[GroupRequest]
    rows: list[RowRequest]
    schedule: ScheduleRequest | None = None


class LiveXlsxPublicationExecuteRequest(LiveXlsxExportRequest):
    preview_token: str = Field(min_length=1)
    conflict_action: str = Field(pattern="^(none|archive|recycle)$")


class LiveXlsxPublicationPreviewResponse(BaseModel):
    mode: str
    status: str
    existing_file: bool
    existing_modified_at: str | None
    blockers: list[str]
    preview_token: str


class LiveXlsxPublicationResultResponse(BaseModel):
    file_name: str
    archive_path: str | None


@router.post("/api/projects/{project_id}/matrix-editor/live-xlsx-export")
def export_live_matrix_xlsx(
    project_id: str,
    request: LiveXlsxExportRequest,
    service: MatrixEditorLiveXlsxExportService = Depends(
        get_matrix_editor_live_xlsx_export_service
    ),
) -> Response:
    """Return an immutable current-UI snapshot as XLSX bytes."""
    del project_id
    try:
        result = service.export(_to_application_request(request))
    except MatrixEditorLiveXlsxExportError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "matrix_editor_live_xlsx_export_blocked",
                "message": str(exc),
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "matrix_editor_live_xlsx_export_failed",
                "message": "Matrix export could not be created.",
            },
        ) from exc
    disposition = (
        'attachment; filename="Matrix-Draft.xlsx"; '
        f"filename*=UTF-8''{quote(result.file_name)}"
    )
    return Response(
        result.content,
        media_type=MEDIA_TYPE,
        headers={"Content-Disposition": disposition},
    )


@router.post(
    "/api/projects/{project_id}/matrix-editor/live-xlsx-export/publication/preview",
    response_model=LiveXlsxPublicationPreviewResponse,
)
def preview_live_matrix_xlsx_publication(
    project_id: str,
    request: LiveXlsxExportRequest,
    service: MatrixEditorLiveXlsxPublicationService = Depends(
        get_matrix_editor_live_xlsx_publication_service
    ),
) -> LiveXlsxPublicationPreviewResponse:
    preview = service.preview(
        PreviewMatrixEditorLiveXlsxPublicationCommand(
            project_id,
            _to_application_request(request),
        )
    )
    return LiveXlsxPublicationPreviewResponse(
        mode=preview.mode,
        status=preview.status,
        existing_file=preview.existing_file,
        existing_modified_at=preview.existing_modified_at,
        blockers=list(preview.blockers),
        preview_token=preview.preview_token,
    )


@router.post(
    "/api/projects/{project_id}/matrix-editor/live-xlsx-export/publication/publish",
    response_model=LiveXlsxPublicationResultResponse,
)
def publish_live_matrix_xlsx(
    project_id: str,
    request: LiveXlsxPublicationExecuteRequest,
    service: MatrixEditorLiveXlsxPublicationService = Depends(
        get_matrix_editor_live_xlsx_publication_service
    ),
    settings: Settings = Depends(get_settings),
) -> LiveXlsxPublicationResultResponse:
    try:
        result = service.execute(
            ExecuteMatrixEditorLiveXlsxPublicationCommand(
                project_id=project_id,
                request=_to_application_request(request),
                preview_token=request.preview_token,
                conflict_action=request.conflict_action,
                staging_dir=settings.data_dir / "generated_matrix_publications",
            )
        )
    except ProjectLifecycleReadonlyError as exc:
        raise lifecycle_readonly_conflict(exc) from exc
    except (
        MatrixEditorLiveXlsxPublicationConflictError,
        TestRecordPublicationTargetChangedError,
    ) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except MatrixEditorLiveXlsxPublicationBlockedError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except (MatrixEditorLiveXlsxPublicationError, OSError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return LiveXlsxPublicationResultResponse(
        file_name=result.file_name,
        archive_path=str(result.archive_path) if result.archive_path else None,
    )


def _to_application_request(
    request: LiveXlsxExportRequest,
) -> MatrixEditorLiveXlsxExportRequest:
    return MatrixEditorLiveXlsxExportRequest(
        source=request.source,
        project_reference=request.project_reference,
        groups=tuple(
            MatrixEditorLiveXlsxExportGroup(
                item.group_id,
                item.group_key,
                item.group_label,
                item.sample_size,
                item.time_display,
                item.sample_note,
            )
            for item in request.groups
        ),
        rows=tuple(
            MatrixEditorLiveXlsxExportRow(
                item.row_id,
                item.test_item,
                item.section,
                item.test_method,
                item.condition,
                item.requirement,
                tuple(
                    MatrixEditorLiveXlsxExportCell(cell.group_id, cell.step_text)
                    for cell in item.cells
                ),
                item.day_expression,
            )
            for item in request.rows
        ),
        schedule=(
            MatrixEditorLiveXlsxExportSchedule(**request.schedule.model_dump())
            if request.schedule is not None
            else None
        ),
    )
