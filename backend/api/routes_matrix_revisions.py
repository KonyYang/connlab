"""Matrix revision flow API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_matrix_revision_flow_service
from backend.application.matrix_revision_flow_service import (
    CreateMatrixRevisionDraftCommand,
    MatrixRevisionFlowConflictError,
    MatrixRevisionFlowError,
    MatrixRevisionFlowNotFoundError,
    MatrixRevisionFlowService,
)
from backend.domain import ProjectMatrixDraftSnapshot


router = APIRouter(prefix="/api/projects/{project_id}/matrix-revisions", tags=["matrix-revisions"])


class ProjectMatrixDraftRecordResponse(BaseModel):
    """Draft root response model for matrix revision flow."""

    project_matrix_draft_id: str
    project_id: str
    source_import_id: str | None
    source_snapshot_id: str
    base_confirmed_matrix_id: str | None
    status: str
    created_at: str
    updated_at: str


class ProjectMatrixDraftGroupResponse(BaseModel):
    """Draft group response model for matrix revision flow."""

    draft_group_id: str
    source_group_snapshot_id: str | None
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None
    sample_note: str | None


class ProjectMatrixDraftRowResponse(BaseModel):
    """Draft row response model for matrix revision flow."""

    draft_row_id: str
    source_row_snapshot_id: str | None
    row_order: int
    test_item: str
    source_section: str | None
    method: str | None
    condition: str | None
    requirement: str | None
    is_sample_row: bool


class ProjectMatrixDraftCellResponse(BaseModel):
    """Draft cell response model for matrix revision flow."""

    draft_cell_id: str
    draft_row_id: str
    draft_group_id: str
    cell_value: str


class ProjectMatrixDraftResponse(BaseModel):
    """Full matrix revision draft aggregate response."""

    record: ProjectMatrixDraftRecordResponse
    groups: list[ProjectMatrixDraftGroupResponse]
    rows: list[ProjectMatrixDraftRowResponse]
    cells: list[ProjectMatrixDraftCellResponse]


@router.post("", response_model=ProjectMatrixDraftResponse, status_code=201)
def create_matrix_revision_draft(
    project_id: str,
    service: MatrixRevisionFlowService = Depends(get_matrix_revision_flow_service),
) -> ProjectMatrixDraftResponse:
    """Create one revision draft from the project's active confirmed matrix."""
    try:
        draft = service.create_revision_draft(
            CreateMatrixRevisionDraftCommand(project_id=project_id)
        )
    except MatrixRevisionFlowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MatrixRevisionFlowConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except MatrixRevisionFlowError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_response(draft)


def _to_response(draft: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftResponse:
    return ProjectMatrixDraftResponse(
        record=ProjectMatrixDraftRecordResponse(
            project_matrix_draft_id=draft.record.project_matrix_draft_id,
            project_id=draft.record.project_id,
            source_import_id=draft.record.source_import_id,
            source_snapshot_id=draft.record.source_snapshot_id,
            base_confirmed_matrix_id=draft.record.base_confirmed_matrix_id,
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
                method=row.method,
                condition=row.condition,
                requirement=row.requirement,
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
