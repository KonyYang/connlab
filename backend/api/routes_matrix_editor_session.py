"""Matrix Editor temporary session read/confirm routes."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException

from backend.api.dependencies import get_matrix_editor_session_service
from backend.api.lifecycle_errors import (
    lifecycle_guard_not_found,
    lifecycle_readonly_conflict,
)
from backend.api.routes_project_matrix_drafts import (
    ConfirmedMatrixSnapshotResponse,
    _to_confirmed_response,
)
from backend.application.project_lifecycle_write_guard import (
    ProjectLifecycleReadonlyError,
    ProjectLifecycleWriteGuardNotFoundError,
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


from backend.api.matrix_editor_session_dtos import *
from backend.api.matrix_editor_session_response_mappers import (
    _to_session_cells,
    _to_session_groups,
    _to_session_rows,
    _to_session_duration_authorities,
)

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
        editor_source_import_id=seed.editor_source_import_id,
        editor_source_snapshot_id=seed.editor_source_snapshot_id,
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
                duration_authorities=[
                    MatrixEditorSessionDurationAuthorityResponse(
                        **{
                            field: getattr(item, field)
                            for field in MatrixEditorSessionDurationAuthorityResponse.model_fields
                        }
                    )
                    for item in seed.editor_draft.duration_authorities
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
                duration_authorities=_to_session_duration_authorities(
                    request.duration_authorities
                ),
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
    except ProjectLifecycleWriteGuardNotFoundError as exc:
        raise lifecycle_guard_not_found(exc) from exc
    except ProjectLifecycleReadonlyError as exc:
        raise lifecycle_readonly_conflict(exc) from exc
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
    except ProjectLifecycleWriteGuardNotFoundError as exc:
        raise lifecycle_guard_not_found(exc) from exc
    except ProjectLifecycleReadonlyError as exc:
        raise lifecycle_readonly_conflict(exc) from exc
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
                duration_authorities=_to_session_duration_authorities(
                    request.duration_authorities
                ),
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
    except ProjectLifecycleWriteGuardNotFoundError as exc:
        raise lifecycle_guard_not_found(exc) from exc
    except ProjectLifecycleReadonlyError as exc:
        raise lifecycle_readonly_conflict(exc) from exc
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
        fee_rebase_promotion_status=result.fee_rebase_promotion_status,
        fee_rebase_promotion_summary=(
            MatrixFeeRebaseSummaryResponse(
                preserved_count=result.fee_rebase_promotion_summary.preserved_count,
                added_count=result.fee_rebase_promotion_summary.added_count,
                removed_count=result.fee_rebase_promotion_summary.removed_count,
                preserved_manual_count=(
                    result.fee_rebase_promotion_summary.preserved_manual_count
                ),
                removed_manual_count=(
                    result.fee_rebase_promotion_summary.removed_manual_count
                ),
            )
            if result.fee_rebase_promotion_summary is not None
            else None
        ),
        fee_rebase_promotion_error=result.fee_rebase_promotion_error,
    )
