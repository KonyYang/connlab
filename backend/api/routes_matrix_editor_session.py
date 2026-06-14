"""Matrix Editor temporary session read/confirm routes."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException
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
    MatrixEditorSessionDraftConflictError,
    MatrixEditorSessionDraftDiscardCommand,
    MatrixEditorSessionDraftSaveCommand,
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
    day_expression: str | None
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
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None
    editor_draft_id: str | None = None
    draft_status: str = "missing"
    loaded_source: str = "authority"
    stale_draft_present: bool = False
    draft_updated_at: str | None = None
    saved_payload_signature: str | None = None


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
    day_expression: str | None = None
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
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None
    expected_editor_draft_id: str | None = None
    expected_saved_payload_signature: str | None = None


class MatrixEditorSessionDraftSaveRequest(BaseModel):
    """Session draft autosave request model."""

    expected_active_confirmed_matrix_id: str | None = None
    expected_active_confirmed_revision: int | None = None
    source_document_path: str | None = None
    source_document_name: str | None = None
    source_format: str | None = None
    source_import_id: str | None = None
    source_snapshot_id: str | None = None
    groups: list[MatrixEditorSessionGroupRequest]
    rows: list[MatrixEditorSessionRowRequest]
    cells: list[MatrixEditorSessionCellRequest]
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None


class MatrixEditorSessionDraftSaveResponse(BaseModel):
    """Session draft autosave response model."""

    editor_draft_id: str
    draft_status: str
    draft_updated_at: str
    saved_payload_signature: str
    active_confirmed_matrix_id: str
    active_confirmed_revision: int
    fee_rebase_status: str = "not_required"
    fee_rebase_summary: "MatrixFeeRebaseSummaryResponse | None" = None
    fee_rebase_error: str | None = None


class MatrixFeeRebaseSummaryResponse(BaseModel):
    """Pending Matrix-to-Fee rebase summary returned by autosave."""

    preserved_count: int
    added_count: int
    removed_count: int
    preserved_manual_count: int = 0
    removed_manual_count: int = 0


class MatrixEditorSessionDraftDiscardRequest(BaseModel):
    """Session draft discard request model."""

    expected_editor_draft_id: str | None = None
    expected_saved_payload_signature: str | None = None


class MatrixEditorSessionDraftDiscardResponse(BaseModel):
    """Session draft discard response model."""

    discarded: bool
    active_confirmed_matrix_id: str | None
    active_confirmed_revision: int | None


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
                        day_expression=row.day_expression,
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
        pre_test_buffer_days=seed.pre_test_buffer_days,
        post_test_buffer_days=seed.post_test_buffer_days,
        sample_received_date=seed.sample_received_date,
        planned_test_start_date=seed.planned_test_start_date,
        planned_test_complete_date=seed.planned_test_complete_date,
        estimated_completion_date=seed.estimated_completion_date,
        editor_draft_id=seed.editor_draft_id,
        draft_status=seed.draft_status,
        loaded_source=seed.loaded_source,
        stale_draft_present=seed.stale_draft_present,
        draft_updated_at=seed.draft_updated_at,
        saved_payload_signature=seed.saved_payload_signature,
    )


@router.put(
    "/api/projects/{project_id}/matrix-editor/session/draft",
    response_model=MatrixEditorSessionDraftSaveResponse,
)
def save_matrix_editor_session_draft(
    project_id: str,
    request: MatrixEditorSessionDraftSaveRequest,
    service: MatrixEditorSessionService = Depends(get_matrix_editor_session_service),
) -> MatrixEditorSessionDraftSaveResponse:
    """Autosave one Matrix Editor session draft in project scope."""
    try:
        result = service.save_editor_draft(
            MatrixEditorSessionDraftSaveCommand(
                project_id=project_id,
                expected_active_confirmed_matrix_id=request.expected_active_confirmed_matrix_id,
                expected_active_confirmed_revision=request.expected_active_confirmed_revision,
                source_document_path=request.source_document_path,
                source_document_name=request.source_document_name,
                source_format=request.source_format,
                source_import_id=request.source_import_id,
                source_snapshot_id=request.source_snapshot_id,
                groups=_to_session_groups(request.groups),
                rows=_to_session_rows(request.rows),
                cells=_to_session_cells(request.cells),
                pre_test_buffer_days=request.pre_test_buffer_days,
                post_test_buffer_days=request.post_test_buffer_days,
                sample_received_date=request.sample_received_date,
                planned_test_start_date=request.planned_test_start_date,
                planned_test_complete_date=request.planned_test_complete_date,
                estimated_completion_date=request.estimated_completion_date,
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
    return MatrixEditorSessionDraftSaveResponse(
        editor_draft_id=result.editor_draft_id,
        draft_status=result.draft_status,
        draft_updated_at=result.draft_updated_at,
        saved_payload_signature=result.saved_payload_signature,
        active_confirmed_matrix_id=result.active_confirmed_matrix_id,
        active_confirmed_revision=result.active_confirmed_revision,
        fee_rebase_status=result.fee_rebase_status,
        fee_rebase_summary=(
            MatrixFeeRebaseSummaryResponse(
                preserved_count=result.fee_rebase_summary.preserved_count,
                added_count=result.fee_rebase_summary.added_count,
                removed_count=result.fee_rebase_summary.removed_count,
                preserved_manual_count=(
                    result.fee_rebase_summary.preserved_manual_count
                ),
                removed_manual_count=result.fee_rebase_summary.removed_manual_count,
            )
            if result.fee_rebase_summary is not None
            else None
        ),
        fee_rebase_error=result.fee_rebase_error,
    )


@router.delete(
    "/api/projects/{project_id}/matrix-editor/session/draft",
    response_model=MatrixEditorSessionDraftDiscardResponse,
)
def discard_matrix_editor_session_draft(
    project_id: str,
    request: MatrixEditorSessionDraftDiscardRequest = Body(
        default_factory=MatrixEditorSessionDraftDiscardRequest
    ),
    service: MatrixEditorSessionService = Depends(get_matrix_editor_session_service),
) -> MatrixEditorSessionDraftDiscardResponse:
    """Discard the current Matrix Editor session draft in project scope."""
    try:
        result = service.discard_editor_draft(
            MatrixEditorSessionDraftDiscardCommand(
                project_id=project_id,
                expected_editor_draft_id=request.expected_editor_draft_id,
                expected_saved_payload_signature=request.expected_saved_payload_signature,
            )
        )
    except MatrixEditorSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MatrixEditorSessionDraftConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "matrix_editor_draft_conflict", "message": str(exc)},
        ) from exc
    return MatrixEditorSessionDraftDiscardResponse(
        discarded=result.discarded,
        active_confirmed_matrix_id=result.active_confirmed_matrix_id,
        active_confirmed_revision=result.active_confirmed_revision,
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
                groups=_to_session_groups(request.groups),
                rows=_to_session_rows(request.rows),
                cells=_to_session_cells(request.cells),
                pre_test_buffer_days=request.pre_test_buffer_days,
                post_test_buffer_days=request.post_test_buffer_days,
                sample_received_date=request.sample_received_date,
                planned_test_start_date=request.planned_test_start_date,
                planned_test_complete_date=request.planned_test_complete_date,
                estimated_completion_date=request.estimated_completion_date,
                expected_editor_draft_id=request.expected_editor_draft_id,
                expected_saved_payload_signature=request.expected_saved_payload_signature,
            )
        )
    except MatrixEditorSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MatrixEditorSessionActiveChangedError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "active_matrix_changed", "message": str(exc)},
        ) from exc
    except MatrixEditorSessionDraftConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "matrix_editor_draft_conflict", "message": str(exc)},
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


def _to_session_groups(
    groups: list[MatrixEditorSessionGroupRequest],
) -> tuple[MatrixEditorSessionGroup, ...]:
    return tuple(
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
        for item in groups
    )


def _to_session_rows(
    rows: list[MatrixEditorSessionRowRequest],
) -> tuple[MatrixEditorSessionRow, ...]:
    return tuple(
        MatrixEditorSessionRow(
            draft_row_id=item.draft_row_id,
            source_row_snapshot_id=item.source_row_snapshot_id,
            row_order=item.row_order,
            test_item=item.test_item,
            source_section=item.source_section,
            method=item.method,
            condition=item.condition,
            requirement=item.requirement,
            day_expression=item.day_expression,
            is_sample_row=item.is_sample_row,
        )
        for item in rows
    )


def _to_session_cells(
    cells: list[MatrixEditorSessionCellRequest],
) -> tuple[MatrixEditorSessionCell, ...]:
    return tuple(
        MatrixEditorSessionCell(
            draft_row_id=item.draft_row_id,
            draft_group_id=item.draft_group_id,
            cell_value=item.cell_value,
        )
        for item in cells
    )
