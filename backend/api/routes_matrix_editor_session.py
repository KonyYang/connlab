"""Matrix Editor temporary session read/confirm routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_matrix_editor_session_service
from backend.api.routes_project_matrix_drafts import (
    ConfirmedMatrixSnapshotResponse,
    _to_confirmed_response,
)
from backend.application.matrix_editor_session_service import (
    MatrixEditorSessionActiveChangedError,
    MatrixEditorSessionConfirmCommand,
    MatrixEditorSessionCell,
    MatrixEditorSessionError,
    MatrixEditorSessionGroup,
    MatrixEditorSessionNotFoundError,
    MatrixEditorSessionRow,
    MatrixEditorSessionService,
)


router = APIRouter(tags=["matrix-editor-session"])


class MatrixEditorSessionGroupResponse(BaseModel):
    """Session editor group response model."""

    draft_group_id: str
    source_group_snapshot_id: str | None
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None
    sample_note: str | None


class MatrixEditorSessionRowResponse(BaseModel):
    """Session editor row response model."""

    draft_row_id: str
    source_row_snapshot_id: str | None
    row_order: int
    test_item: str
    source_section: str | None
    method: str | None
    condition: str | None
    requirement: str | None
    is_sample_row: bool


class MatrixEditorSessionCellResponse(BaseModel):
    """Session editor sparse cell response model."""

    draft_row_id: str
    draft_group_id: str
    cell_value: str


class MatrixEditorSessionDraftResponse(BaseModel):
    """Session editor snapshot response model."""

    groups: list[MatrixEditorSessionGroupResponse]
    rows: list[MatrixEditorSessionRowResponse]
    cells: list[MatrixEditorSessionCellResponse]


class MatrixEditorSessionSeedResponse(BaseModel):
    """Matrix Editor session seed response model."""

    project_id: str
    active_confirmed_matrix_id: str | None
    active_confirmed_revision: int | None
    active_source_import_id: str | None
    active_source_snapshot_id: str | None
    editor_draft: MatrixEditorSessionDraftResponse | None
    source_preview_payload: dict | None
    source_status: str
    source_unavailable_message: str | None


class MatrixEditorSessionGroupRequest(BaseModel):
    """Session editor group request model."""

    draft_group_id: str
    source_group_snapshot_id: str | None = None
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None = None
    sample_note: str | None = None


class MatrixEditorSessionRowRequest(BaseModel):
    """Session editor row request model."""

    draft_row_id: str
    source_row_snapshot_id: str | None = None
    row_order: int
    test_item: str
    source_section: str | None = None
    method: str | None = None
    condition: str | None = None
    requirement: str | None = None
    is_sample_row: bool = False


class MatrixEditorSessionCellRequest(BaseModel):
    """Session editor sparse cell request model."""

    draft_row_id: str
    draft_group_id: str
    cell_value: str


class MatrixEditorSessionConfirmRequest(BaseModel):
    """Session confirm request model."""

    expected_active_confirmed_matrix_id: str | None = None
    expected_active_confirmed_revision: int | None = None
    source_document_path: str | None = None
    source_document_name: str | None = None
    source_format: str | None = None
    source_import_id: str | None = None
    source_snapshot_id: str | None = None
    confirmed_by: str
    groups: list[MatrixEditorSessionGroupRequest]
    rows: list[MatrixEditorSessionRowRequest]
    cells: list[MatrixEditorSessionCellRequest]


class MatrixEditorSessionConfirmResponse(BaseModel):
    """Session confirm response model."""

    publish_status: str
    message: str
    confirmed_snapshot: ConfirmedMatrixSnapshotResponse | None


@router.get(
    "/api/projects/{project_id}/matrix-editor/session",
    response_model=MatrixEditorSessionSeedResponse,
)
def get_matrix_editor_session_seed(
    project_id: str,
    service: MatrixEditorSessionService = Depends(get_matrix_editor_session_service),
) -> MatrixEditorSessionSeedResponse:
    """Return one Matrix Editor temporary session seed in project scope."""
    try:
        seed = service.get_seed(project_id=project_id)
    except MatrixEditorSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return MatrixEditorSessionSeedResponse(
        project_id=seed.project_id,
        active_confirmed_matrix_id=seed.active_confirmed_matrix_id,
        active_confirmed_revision=seed.active_confirmed_revision,
        active_source_import_id=seed.active_source_import_id,
        active_source_snapshot_id=seed.active_source_snapshot_id,
        editor_draft=(
            MatrixEditorSessionDraftResponse(
                groups=[
                    MatrixEditorSessionGroupResponse(
                        draft_group_id=group.draft_group_id,
                        source_group_snapshot_id=group.source_group_snapshot_id,
                        group_order=group.group_order,
                        group_key=group.group_key,
                        group_label=group.group_label,
                        is_selected=group.is_selected,
                        sample_quantity_expression=group.sample_quantity_expression,
                        sample_note=group.sample_note,
                    )
                    for group in seed.editor_draft.groups
                ],
                rows=[
                    MatrixEditorSessionRowResponse(
                        draft_row_id=row.draft_row_id,
                        source_row_snapshot_id=row.source_row_snapshot_id,
                        row_order=row.row_order,
                        test_item=row.test_item,
                        source_section=row.source_section,
                        method=row.method,
                        condition=row.condition,
                        requirement=row.requirement,
                        is_sample_row=row.is_sample_row,
                    )
                    for row in seed.editor_draft.rows
                ],
                cells=[
                    MatrixEditorSessionCellResponse(
                        draft_row_id=cell.draft_row_id,
                        draft_group_id=cell.draft_group_id,
                        cell_value=cell.cell_value,
                    )
                    for cell in seed.editor_draft.cells
                ],
            )
            if seed.editor_draft is not None
            else None
        ),
        source_preview_payload=seed.source_preview_payload,
        source_status=seed.source_status,
        source_unavailable_message=seed.source_unavailable_message,
    )


@router.post(
    "/api/projects/{project_id}/matrix-editor/session/confirm",
    response_model=MatrixEditorSessionConfirmResponse,
)
def confirm_matrix_editor_session(
    project_id: str,
    request: MatrixEditorSessionConfirmRequest,
    service: MatrixEditorSessionService = Depends(get_matrix_editor_session_service),
) -> MatrixEditorSessionConfirmResponse:
    """Confirm one Matrix Editor temporary session into active authority."""
    try:
        result = service.confirm_session(
            MatrixEditorSessionConfirmCommand(
                project_id=project_id,
                expected_active_confirmed_matrix_id=request.expected_active_confirmed_matrix_id,
                expected_active_confirmed_revision=request.expected_active_confirmed_revision,
                source_document_path=request.source_document_path,
                source_document_name=request.source_document_name,
                source_format=request.source_format,
                source_import_id=request.source_import_id,
                source_snapshot_id=request.source_snapshot_id,
                confirmed_by=request.confirmed_by,
                groups=tuple(
                    MatrixEditorSessionGroup(
                        draft_group_id=item.draft_group_id,
                        source_group_snapshot_id=item.source_group_snapshot_id,
                        group_order=item.group_order,
                        group_key=item.group_key,
                        group_label=item.group_label,
                        is_selected=item.is_selected,
                        sample_quantity_expression=item.sample_quantity_expression,
                        sample_note=item.sample_note,
                    )
                    for item in request.groups
                ),
                rows=tuple(
                    MatrixEditorSessionRow(
                        draft_row_id=item.draft_row_id,
                        source_row_snapshot_id=item.source_row_snapshot_id,
                        row_order=item.row_order,
                        test_item=item.test_item,
                        source_section=item.source_section,
                        method=item.method,
                        condition=item.condition,
                        requirement=item.requirement,
                        is_sample_row=item.is_sample_row,
                    )
                    for item in request.rows
                ),
                cells=tuple(
                    MatrixEditorSessionCell(
                        draft_row_id=item.draft_row_id,
                        draft_group_id=item.draft_group_id,
                        cell_value=item.cell_value,
                    )
                    for item in request.cells
                ),
            )
        )
    except MatrixEditorSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MatrixEditorSessionActiveChangedError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "active_matrix_changed", "message": str(exc)},
        ) from exc
    except MatrixEditorSessionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return MatrixEditorSessionConfirmResponse(
        publish_status=result.publish_status,
        message=result.message,
        confirmed_snapshot=(
            _to_confirmed_response(result.confirmed_snapshot)
            if result.confirmed_snapshot is not None
            else None
        ),
    )
