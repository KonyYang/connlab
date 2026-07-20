"""Preview and apply Standard catalog Method revisions to an editable Matrix draft."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_matrix_method_version_sync_service
from backend.application.matrix_method_version_sync_service import (
    ApplyMatrixMethodVersionSyncCommand,
    MatrixMethodVersionSyncConflictError,
    MatrixMethodVersionSyncError,
    MatrixMethodVersionSyncNotFoundError,
    MatrixMethodVersionSyncPreview,
    MatrixMethodVersionSyncService,
    PreviewMatrixMethodVersionSyncCommand,
)


router = APIRouter(tags=["matrix-method-version-sync"])


class MatrixMethodVersionSyncPreviewRequest(BaseModel):
    project_matrix_draft_id: str
    expected_saved_payload_signature: str


class MatrixMethodVersionSyncApplyRequest(MatrixMethodVersionSyncPreviewRequest):
    preview_fingerprint: str
    selected_draft_row_ids: list[str]
    applied_by: str


class MatrixMethodVersionSyncRowResponse(BaseModel):
    draft_row_id: str
    row_order: int
    test_item: str
    current_method: str | None
    method_core: str | None
    matched_standard_code: str | None
    catalog_revision: str | None
    catalog_year: int | None
    source_row_number: int | None
    proposed_method: str | None
    status: str
    reason: str | None
    selectable: bool


class MatrixMethodVersionSyncPreviewResponse(BaseModel):
    project_id: str
    project_matrix_draft_id: str
    base_confirmed_matrix_id: str | None
    resource_id: str
    resource_path: str
    worksheet_name: str
    catalog_fingerprint: str
    target_fingerprint: str
    preview_fingerprint: str
    generated_at: str
    rows: list[MatrixMethodVersionSyncRowResponse]


class MatrixMethodVersionSyncApplyResponse(BaseModel):
    project_matrix_draft_id: str
    saved_payload_signature: str
    applied_row_ids: list[str]


@router.post(
    "/api/projects/{project_id}/matrix-method-version-sync/preview",
    response_model=MatrixMethodVersionSyncPreviewResponse,
)
def preview_matrix_method_versions(
    project_id: str,
    request: MatrixMethodVersionSyncPreviewRequest,
    service: MatrixMethodVersionSyncService = Depends(
        get_matrix_method_version_sync_service
    ),
) -> MatrixMethodVersionSyncPreviewResponse:
    try:
        result = service.preview(
            PreviewMatrixMethodVersionSyncCommand(
                project_id=project_id,
                project_matrix_draft_id=request.project_matrix_draft_id,
                expected_saved_payload_signature=request.expected_saved_payload_signature,
            )
        )
    except MatrixMethodVersionSyncNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MatrixMethodVersionSyncConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except MatrixMethodVersionSyncError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _preview_response(result)


@router.post(
    "/api/projects/{project_id}/matrix-method-version-sync/apply",
    response_model=MatrixMethodVersionSyncApplyResponse,
)
def apply_matrix_method_versions(
    project_id: str,
    request: MatrixMethodVersionSyncApplyRequest,
    service: MatrixMethodVersionSyncService = Depends(
        get_matrix_method_version_sync_service
    ),
) -> MatrixMethodVersionSyncApplyResponse:
    try:
        result = service.apply(
            ApplyMatrixMethodVersionSyncCommand(
                project_id=project_id,
                project_matrix_draft_id=request.project_matrix_draft_id,
                expected_saved_payload_signature=request.expected_saved_payload_signature,
                preview_fingerprint=request.preview_fingerprint,
                selected_draft_row_ids=tuple(request.selected_draft_row_ids),
                applied_by=request.applied_by,
            )
        )
    except MatrixMethodVersionSyncNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MatrixMethodVersionSyncConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except MatrixMethodVersionSyncError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MatrixMethodVersionSyncApplyResponse(
        project_matrix_draft_id=result.project_matrix_draft_id,
        saved_payload_signature=result.saved_payload_signature,
        applied_row_ids=list(result.applied_row_ids),
    )


def _preview_response(
    result: MatrixMethodVersionSyncPreview,
) -> MatrixMethodVersionSyncPreviewResponse:
    return MatrixMethodVersionSyncPreviewResponse(
        project_id=result.project_id,
        project_matrix_draft_id=result.project_matrix_draft_id,
        base_confirmed_matrix_id=result.base_confirmed_matrix_id,
        resource_id=result.resource_id,
        resource_path=result.resource_path,
        worksheet_name=result.worksheet_name,
        catalog_fingerprint=result.catalog_fingerprint,
        target_fingerprint=result.target_fingerprint,
        preview_fingerprint=result.preview_fingerprint,
        generated_at=result.generated_at,
        rows=[MatrixMethodVersionSyncRowResponse(**asdict(row)) for row in result.rows],
    )
