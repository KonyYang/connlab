"""Project Matrix draft working-copy persistence API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_project_matrix_draft_persistence_service
from backend.application.project_matrix_draft_persistence_service import (
    CreateProjectMatrixDraftFromSourceImportCommand,
    ProjectMatrixDraftPersistenceConflictError,
    ProjectMatrixDraftPersistenceError,
    ProjectMatrixDraftPersistenceNotFoundError,
    ProjectMatrixDraftPersistenceService,
)
from backend.domain import ProjectMatrixDraftSnapshot


router = APIRouter(prefix="/api/projects/{project_id}/matrix-drafts", tags=["project-matrix-drafts"])


class ProjectMatrixDraftCreateRequest(BaseModel):
    """Request body for creating Project Matrix draft from source import."""

    source_import_id: str
    selected_group_keys: list[str] | None = None


class ProjectMatrixDraftRecordResponse(BaseModel):
    """Draft root response model."""

    project_matrix_draft_id: str
    project_id: str
    source_import_id: str
    source_snapshot_id: str
    status: str
    created_at: str
    updated_at: str


class ProjectMatrixDraftGroupResponse(BaseModel):
    """Draft group response model."""

    draft_group_id: str
    source_group_snapshot_id: str
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None
    sample_note: str | None


class ProjectMatrixDraftRowResponse(BaseModel):
    """Draft row response model."""

    draft_row_id: str
    source_row_snapshot_id: str
    row_order: int
    test_item: str
    source_section: str | None
    is_sample_row: bool


class ProjectMatrixDraftCellResponse(BaseModel):
    """Draft cell response model."""

    draft_cell_id: str
    draft_row_id: str
    draft_group_id: str
    cell_value: str


class ProjectMatrixDraftResponse(BaseModel):
    """Full draft aggregate response."""

    record: ProjectMatrixDraftRecordResponse
    groups: list[ProjectMatrixDraftGroupResponse]
    rows: list[ProjectMatrixDraftRowResponse]
    cells: list[ProjectMatrixDraftCellResponse]


@router.post("", response_model=ProjectMatrixDraftResponse, status_code=201)
def create_project_matrix_draft(
    project_id: str,
    request: ProjectMatrixDraftCreateRequest,
    service: ProjectMatrixDraftPersistenceService = Depends(
        get_project_matrix_draft_persistence_service
    ),
) -> ProjectMatrixDraftResponse:
    """Create one structured Project Matrix draft from source import lineage."""
    try:
        draft = service.create_from_source_import(
            CreateProjectMatrixDraftFromSourceImportCommand(
                project_id=project_id,
                source_import_id=request.source_import_id,
                selected_group_keys=tuple(request.selected_group_keys)
                if request.selected_group_keys is not None
                else None,
            )
        )
    except ProjectMatrixDraftPersistenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectMatrixDraftPersistenceConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProjectMatrixDraftPersistenceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(draft)


@router.get("/{project_matrix_draft_id}", response_model=ProjectMatrixDraftResponse)
def get_project_matrix_draft(
    project_id: str,
    project_matrix_draft_id: str,
    service: ProjectMatrixDraftPersistenceService = Depends(
        get_project_matrix_draft_persistence_service
    ),
) -> ProjectMatrixDraftResponse:
    """Fetch one draft by id within project scope."""
    try:
        return _to_response(
            service.get_draft(
                project_id=project_id,
                project_matrix_draft_id=project_matrix_draft_id,
            )
        )
    except ProjectMatrixDraftPersistenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _to_response(draft: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftResponse:
    return ProjectMatrixDraftResponse(
        record=ProjectMatrixDraftRecordResponse(
            project_matrix_draft_id=draft.record.project_matrix_draft_id,
            project_id=draft.record.project_id,
            source_import_id=draft.record.source_import_id,
            source_snapshot_id=draft.record.source_snapshot_id,
            status=draft.record.status.value,
            created_at=draft.record.created_at,
            updated_at=draft.record.updated_at,
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
            for group in draft.groups
        ],
        rows=[
            ProjectMatrixDraftRowResponse(
                draft_row_id=row.draft_row_id,
                source_row_snapshot_id=row.source_row_snapshot_id,
                row_order=row.row_order,
                test_item=row.test_item,
                source_section=row.source_section,
                is_sample_row=row.is_sample_row,
            )
            for row in draft.rows
        ],
        cells=[
            ProjectMatrixDraftCellResponse(
                draft_cell_id=cell.draft_cell_id,
                draft_row_id=cell.draft_row_id,
                draft_group_id=cell.draft_group_id,
                cell_value=cell.cell_value,
            )
            for cell in draft.cells
        ],
    )
