"""Current-state Matrix Editor LLCR/CR workbook generation route."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.api.matrix_step_text_output_dtos import MatrixStepTextOutputOverrideRequest
from backend.api.matrix_editor_session_dtos import MatrixPointProfileDTO, MatrixStepPointOverrideDTO
from backend.api.matrix_editor_session_response_mappers import _to_point_profile, _to_point_overrides
from backend.application.matrix_step_text_output import MatrixStepTextOutputOverride

from backend.api.dependencies import (
    get_matrix_editor_llcr_cr_record_generation_service,
    get_matrix_editor_llcr_cr_record_publication_service,
)
from backend.api.project_folder_write_guard import require_project_folder_write_slot
from backend.application.confirmed_matrix_llcr_cr_record_generation_service import (
    MatrixEditorLlcrCrRecordPublicationService,
    PreviewMatrixEditorLlcrCrPublicationCommand,
    PublishMatrixEditorLlcrCrPublicationCommand,
)
from backend.application.matrix_editor_llcr_cr_record_generation_service import (
    GenerateMatrixEditorLlcrCrRecordCommand,
    MatrixEditorLlcrCrRecordGenerationError,
    MatrixEditorLlcrCrRecordGenerationService,
)
from backend.application.matrix_editor_llcr_cr_record_projection import (
    MatrixEditorLlcrCrRecordGroupInput,
    MatrixEditorLlcrCrRecordRowInput,
)

router = APIRouter(tags=["matrix-editor-llcr-cr-record-generation"])
_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class MatrixEditorLlcrCrRecordGroupRequest(BaseModel):
    group_key: str = Field(min_length=1)
    group_label: str = Field(min_length=1)
    sample_quantity_expression: str = ""
    sample_note: str | None = None
    draft_group_id: str | None = None


class MatrixEditorLlcrCrRecordRowRequest(BaseModel):
    test_item: str = ""
    section: str = ""
    method: str = ""
    condition: str = ""
    requirement: str = ""
    is_sample_row: bool = False
    group_values: dict[str, str] = Field(default_factory=dict)
    draft_row_id: str | None = None


class MatrixEditorLlcrCrRecordDraftRequest(BaseModel):
    source: Literal["matrix_editor_current_ui_state"]
    record_type: Literal["llcr", "cr"]
    groups: list[MatrixEditorLlcrCrRecordGroupRequest]
    rows: list[MatrixEditorLlcrCrRecordRowRequest]
    step_text_overrides: list[MatrixStepTextOutputOverrideRequest] = Field(default_factory=list)
    point_profile: MatrixPointProfileDTO | None = None
    point_overrides: list[MatrixStepPointOverrideDTO] = Field(default_factory=list)
    matrix_has_pending_changes: bool = False
    preview_token: str | None = None


class MatrixEditorLlcrCrRecordPublishRequest(MatrixEditorLlcrCrRecordDraftRequest):
    preview_token: str
    conflict_action: Literal["none", "archive"]


def _draft_command(project_id: str, request: MatrixEditorLlcrCrRecordDraftRequest) -> GenerateMatrixEditorLlcrCrRecordCommand:
    return GenerateMatrixEditorLlcrCrRecordCommand(
        step_text_overrides=tuple(MatrixStepTextOutputOverride(**item.model_dump())
                                  for item in request.step_text_overrides),
        project_id=project_id,
        record_type=request.record_type,
        point_profile=_to_point_profile(request.point_profile),
        point_overrides=_to_point_overrides(request.point_overrides) or (),
        groups=tuple(
            MatrixEditorLlcrCrRecordGroupInput(
                group_key=group.group_key, group_label=group.group_label,
                sample_quantity_expression=group.sample_quantity_expression,
                sample_note=group.sample_note, draft_group_id=group.draft_group_id,
            ) for group in request.groups
        ),
        rows=tuple(
            MatrixEditorLlcrCrRecordRowInput(
                test_item=row.test_item, section=row.section, method=row.method,
                condition=row.condition, requirement=row.requirement,
                is_sample_row=row.is_sample_row, group_values=row.group_values,
                draft_row_id=row.draft_row_id,
            ) for row in request.rows
        ),
    )


@router.post(
    "/api/projects/{project_id}/matrix-editor/llcr-cr-record-draft/generate"
)
def generate_matrix_editor_llcr_cr_record_draft(
    project_id: str,
    request: MatrixEditorLlcrCrRecordDraftRequest,
    service: MatrixEditorLlcrCrRecordGenerationService = Depends(
        get_matrix_editor_llcr_cr_record_generation_service
    ),
    publication: MatrixEditorLlcrCrRecordPublicationService = Depends(
        get_matrix_editor_llcr_cr_record_publication_service
    ),
) -> FileResponse:
    """Return one preview workbook generated only from current UI-state input."""
    try:
        draft = _draft_command(project_id, request)
        if request.preview_token is not None:
            publication.validate_download(
                PreviewMatrixEditorLlcrCrPublicationCommand(draft, request.matrix_has_pending_changes),
                request.preview_token,
            )
        result = service.generate(draft)
    except (MatrixEditorLlcrCrRecordGenerationError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return FileResponse(
        path=result.output_path,
        filename=result.file_name,
        media_type=_XLSX_MEDIA_TYPE,
    )


@router.post("/api/projects/{project_id}/matrix-editor/llcr-cr-record-publication/preview")
def preview_matrix_editor_llcr_cr_record_publication(
    project_id: str,
    request: MatrixEditorLlcrCrRecordDraftRequest,
    service: MatrixEditorLlcrCrRecordPublicationService = Depends(
        get_matrix_editor_llcr_cr_record_publication_service
    ),
) -> dict:
    try:
        result = service.preview(PreviewMatrixEditorLlcrCrPublicationCommand(
            _draft_command(project_id, request), request.matrix_has_pending_changes,
        ))
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "project_id": result.project_id, "mode": result.mode, "status": result.status,
        "authority_status": result.authority_status,
        "target_path": str(result.target_path) if result.target_path else None,
        "existing_file": result.existing_file, "blockers": result.blockers,
        "preview_token": result.preview_token,
    }


@router.post(
    "/api/projects/{project_id}/matrix-editor/llcr-cr-record-publication/publish",
    dependencies=[Depends(require_project_folder_write_slot)],
)
def publish_matrix_editor_llcr_cr_record(
    project_id: str,
    request: MatrixEditorLlcrCrRecordPublishRequest,
    service: MatrixEditorLlcrCrRecordPublicationService = Depends(
        get_matrix_editor_llcr_cr_record_publication_service
    ),
) -> dict:
    try:
        result = service.publish_under_folder_write_slot(PublishMatrixEditorLlcrCrPublicationCommand(
            _draft_command(project_id, request), request.preview_token,
            request.conflict_action, request.matrix_has_pending_changes,
        ))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=409,
            detail=(f"LLCR/CR file operation failed: {exc}. The previous form will not be overwritten "
                    "automatically. Retry this reviewed action for recovery or inspect History/Test results."),
        ) from exc
    return {
        "project_id": result.project_id, "file_name": result.file_name,
        "target_path": str(result.target_path),
        "archive_path": str(result.archive_path) if result.archive_path else None,
    }
