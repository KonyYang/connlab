"""TASK_261 matrix import group-selection commit API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_matrix_import_commit_service
from backend.application.matrix_import_commit_service import (
    MatrixImportCommitCommand,
    MatrixImportCommitConflictError,
    MatrixImportCommitError,
    MatrixImportCommitNotFoundError,
    MatrixImportCommitResult,
    MatrixImportCommitService,
)
from backend.domain import ProjectMatrixDraftSnapshot


router = APIRouter(prefix="/api/projects/{project_id}/matrix-import", tags=["matrix-import-commit"])


class MatrixImportCommitRequest(BaseModel):
    """Request payload for matrix import commit."""

    source_document_path: str = Field(min_length=1)
    source_document_name: str = Field(min_length=1)
    source_format: str = Field(min_length=1)
    preview_payload: dict
    selected_group_keys: list[str]


class ProjectMatrixDraftRecordResponse(BaseModel):
    """Draft record response model."""

    project_matrix_draft_id: str
    project_id: str
    source_import_id: str | None
    source_snapshot_id: str
    base_confirmed_matrix_id: str | None
    status: str
    created_at: str
    updated_at: str
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None


class ProjectMatrixDraftGroupResponse(BaseModel):
    """Draft group response model."""

    draft_group_id: str
    source_group_snapshot_id: str | None
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None
    sample_note: str | None


class ProjectMatrixDraftRowResponse(BaseModel):
    """Draft row response model."""

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


class ProjectMatrixDraftCellResponse(BaseModel):
    """Draft cell response model."""

    draft_cell_id: str
    draft_row_id: str
    draft_group_id: str
    cell_value: str


class ProjectMatrixDraftResponse(BaseModel):
    """Draft aggregate response model."""

    record: ProjectMatrixDraftRecordResponse
    groups: list[ProjectMatrixDraftGroupResponse]
    rows: list[ProjectMatrixDraftRowResponse]
    cells: list[ProjectMatrixDraftCellResponse]


class MatrixImportMethodAuthorityRowResponse(BaseModel):
    """One row-level Method authority result."""

    stable_source_row_key: str
    row_order: int
    test_item: str
    current_method: str | None
    status: str
    resulting_method: str | None
    matched_standard_code: str | None
    source_row_number: int | None
    reason: str | None
    applied: bool


class MatrixImportMethodAuthoritySummaryResponse(BaseModel):
    """Server-derived Method synchronization summary."""

    status: str
    updated_count: int
    current_count: int
    review_count: int
    standard_resource_id: str
    effective_worksheet_name: str
    catalog_fingerprint: str
    context_fingerprint: str
    rows: list[MatrixImportMethodAuthorityRowResponse]


class MatrixImportCommitResponse(BaseModel):
    """Matrix import commit response model."""

    source_import_id: str
    source_snapshot_id: str
    selected_group_keys_committed: list[str]
    commit_status: str
    project_matrix_draft: ProjectMatrixDraftResponse
    method_authority_sync: MatrixImportMethodAuthoritySummaryResponse


@router.post("/commit", response_model=MatrixImportCommitResponse, status_code=201)
def commit_matrix_import(
    project_id: str,
    request: MatrixImportCommitRequest,
    service: MatrixImportCommitService = Depends(get_matrix_import_commit_service),
) -> MatrixImportCommitResponse:
    """Commit one matrix preview payload with selected groups into source+draft lineage."""
    try:
        result = service.commit(
            MatrixImportCommitCommand(
                project_id=project_id,
                source_document_path=request.source_document_path,
                source_document_name=request.source_document_name,
                source_format=request.source_format,
                preview_payload=request.preview_payload,
                selected_group_keys=tuple(request.selected_group_keys),
            )
        )
    except MatrixImportCommitNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MatrixImportCommitConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except MatrixImportCommitError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_response(result)


def _to_response(result: MatrixImportCommitResult) -> MatrixImportCommitResponse:
    return MatrixImportCommitResponse(
        source_import_id=result.source_import_id,
        source_snapshot_id=result.source_snapshot_id,
        selected_group_keys_committed=list(result.selected_group_keys_committed),
        commit_status=result.commit_status,
        project_matrix_draft=_to_draft_response(result.project_matrix_draft),
        method_authority_sync=MatrixImportMethodAuthoritySummaryResponse(
            status=result.method_authority_sync.status,
            updated_count=result.method_authority_sync.updated_count,
            current_count=result.method_authority_sync.current_count,
            review_count=result.method_authority_sync.review_count,
            standard_resource_id=result.method_authority_sync.standard_resource_id,
            effective_worksheet_name=(
                result.method_authority_sync.effective_worksheet_name
            ),
            catalog_fingerprint=result.method_authority_sync.catalog_fingerprint,
            context_fingerprint=result.method_authority_sync.context_fingerprint,
            rows=[
                MatrixImportMethodAuthorityRowResponse(
                    stable_source_row_key=row.stable_source_row_key,
                    row_order=row.row_order,
                    test_item=row.test_item,
                    current_method=row.current_method,
                    status=row.status,
                    resulting_method=row.resulting_method,
                    matched_standard_code=row.matched_standard_code,
                    source_row_number=row.source_row_number,
                    reason=row.reason,
                    applied=row.applied,
                )
                for row in result.method_authority_sync.rows
            ],
        ),
    )


def _to_draft_response(snapshot: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftResponse:
    return ProjectMatrixDraftResponse(
        record=ProjectMatrixDraftRecordResponse(
            project_matrix_draft_id=snapshot.record.project_matrix_draft_id,
            project_id=snapshot.record.project_id,
            source_import_id=snapshot.record.source_import_id,
            source_snapshot_id=snapshot.record.source_snapshot_id,
            base_confirmed_matrix_id=snapshot.record.base_confirmed_matrix_id,
            status=snapshot.record.status.value,
            created_at=snapshot.record.created_at,
            updated_at=snapshot.record.updated_at,
            pre_test_buffer_days=snapshot.record.pre_test_buffer_days,
            post_test_buffer_days=snapshot.record.post_test_buffer_days,
            sample_received_date=snapshot.record.sample_received_date,
            planned_test_start_date=snapshot.record.planned_test_start_date,
            planned_test_complete_date=snapshot.record.planned_test_complete_date,
            estimated_completion_date=snapshot.record.estimated_completion_date,
        ),
        groups=[
            ProjectMatrixDraftGroupResponse(
                draft_group_id=group.draft_group_id,
                source_group_snapshot_id=group.source_group_snapshot_id,
                group_order=group.group_order,
                group_key=group.group_key,
                group_label=group.group_label,
                is_selected=group.is_selected,
                sample_quantity_expression=group.sample_quantity_expression,
                sample_note=group.sample_note,
            )
            for group in snapshot.groups
        ],
        rows=[
            ProjectMatrixDraftRowResponse(
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
            for row in snapshot.rows
        ],
        cells=[
            ProjectMatrixDraftCellResponse(
                draft_cell_id=cell.draft_cell_id,
                draft_row_id=cell.draft_row_id,
                draft_group_id=cell.draft_group_id,
                cell_value=cell.cell_value,
            )
            for cell in snapshot.cells
        ],
    )
