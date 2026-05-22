"""Project Matrix draft working-copy persistence API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import (
    get_confirmed_matrix_authority_service,
    get_matrix_revision_flow_service,
    get_project_matrix_draft_persistence_service,
)
from backend.application.confirmed_matrix_authority_service import (
    ConfirmProjectMatrixDraftCommand,
    ConfirmedMatrixAuthorityConflictError,
    ConfirmedMatrixAuthorityError,
    ConfirmedMatrixAuthorityNotFoundError,
    ConfirmedMatrixAuthorityService,
)
from backend.application.project_matrix_draft_persistence_service import (
    CreateProjectMatrixDraftFromSourceImportCommand,
    ProjectMatrixDraftCellInput,
    ProjectMatrixDraftGroupInput,
    ProjectMatrixDraftPersistenceConflictError,
    ProjectMatrixDraftPersistenceError,
    ProjectMatrixDraftPersistenceNotFoundError,
    ProjectMatrixDraftPersistenceService,
    ProjectMatrixDraftRowInput,
    UpdateProjectMatrixDraftCommand,
)
from backend.application.matrix_revision_flow_service import (
    ConfirmMatrixRevisionDraftCommand,
    MatrixRevisionFlowConflictError,
    MatrixRevisionFlowError,
    MatrixRevisionFlowNotFoundError,
    MatrixRevisionFlowService,
)
from backend.domain import ConfirmedMatrixSnapshot, ProjectMatrixDraftSnapshot


router = APIRouter(prefix="/api/projects/{project_id}/matrix-drafts", tags=["project-matrix-drafts"])


class ProjectMatrixDraftCreateRequest(BaseModel):
    """Request body for creating Project Matrix draft from source import."""

    source_import_id: str
    selected_group_keys: list[str] | None = None


class ProjectMatrixDraftRecordResponse(BaseModel):
    """Draft root response model."""

    project_matrix_draft_id: str
    project_id: str
    source_import_id: str | None
    source_snapshot_id: str
    base_confirmed_matrix_id: str | None
    status: str
    created_at: str
    updated_at: str


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


class ProjectMatrixDraftSummaryResponse(BaseModel):
    """Project-scoped matrix draft summary list item."""

    project_matrix_draft_id: str
    project_id: str
    source_import_id: str | None
    source_snapshot_id: str
    base_confirmed_matrix_id: str | None
    status: str
    created_at: str
    updated_at: str


class ProjectMatrixDraftGroupSaveRequest(BaseModel):
    """Draft group payload used by save/update request."""

    draft_group_id: str | None = None
    source_group_snapshot_id: str | None = None
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None = None
    sample_note: str | None = None


class ProjectMatrixDraftRowSaveRequest(BaseModel):
    """Draft row payload used by save/update request."""

    draft_row_id: str | None = None
    source_row_snapshot_id: str | None = None
    row_order: int
    test_item: str
    source_section: str | None = None
    method: str | None = None
    condition: str | None = None
    requirement: str | None = None
    is_sample_row: bool = False


class ProjectMatrixDraftCellSaveRequest(BaseModel):
    """Draft sparse cell payload used by save/update request."""

    draft_row_id: str
    draft_group_id: str
    cell_value: str


class ProjectMatrixDraftSaveRequest(BaseModel):
    """Request body for replacing one matrix draft working copy."""

    groups: list[ProjectMatrixDraftGroupSaveRequest]
    rows: list[ProjectMatrixDraftRowSaveRequest]
    cells: list[ProjectMatrixDraftCellSaveRequest]


class ConfirmProjectMatrixDraftRequest(BaseModel):
    """Request body for confirming one saved Project Matrix draft."""

    confirmed_by: str


class ConfirmMatrixRevisionDraftRequest(BaseModel):
    """Request body for confirming one matrix revision draft."""

    confirmed_by: str
    superseded_reason: str | None = None


class ConfirmedMatrixVersionResponse(BaseModel):
    """Confirmed Matrix authority root response."""

    confirmed_matrix_id: str
    project_id: str
    project_matrix_draft_id: str
    source_import_id: str
    source_snapshot_id: str
    confirmed_revision: int
    is_active_authority: bool
    status: str
    confirmed_by: str
    confirmed_at: str
    superseded_by_confirmed_matrix_id: str | None
    superseded_at: str | None
    superseded_reason: str | None


class ConfirmedMatrixGroupResponse(BaseModel):
    """Confirmed selected group response."""

    confirmed_group_id: str
    draft_group_id: str
    source_group_snapshot_id: str | None
    group_order: int
    group_key: str
    group_label: str
    sample_quantity_expression: str
    sample_note: str | None


class ConfirmedMatrixRowResponse(BaseModel):
    """Confirmed non-sample row response."""

    confirmed_row_id: str
    draft_row_id: str
    source_row_snapshot_id: str | None
    row_order: int
    test_item: str
    source_section: str | None
    method: str | None
    condition: str | None
    requirement: str | None


class ConfirmedMatrixCellResponse(BaseModel):
    """Confirmed sparse cell response."""

    confirmed_cell_id: str
    confirmed_row_id: str
    confirmed_group_id: str
    draft_row_id: str
    draft_group_id: str
    cell_value: str


class ConfirmedMatrixSnapshotResponse(BaseModel):
    """Confirmed Matrix authority aggregate response."""

    version: ConfirmedMatrixVersionResponse
    groups: list[ConfirmedMatrixGroupResponse]
    rows: list[ConfirmedMatrixRowResponse]
    cells: list[ConfirmedMatrixCellResponse]


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


@router.get("", response_model=list[ProjectMatrixDraftSummaryResponse])
def list_project_matrix_drafts(
    project_id: str,
    service: ProjectMatrixDraftPersistenceService = Depends(
        get_project_matrix_draft_persistence_service
    ),
) -> list[ProjectMatrixDraftSummaryResponse]:
    """List matrix drafts in one project scope."""
    try:
        records = service.list_drafts(project_id=project_id)
    except ProjectMatrixDraftPersistenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [
        ProjectMatrixDraftSummaryResponse(
            project_matrix_draft_id=record.project_matrix_draft_id,
            project_id=record.project_id,
            source_import_id=record.source_import_id,
            source_snapshot_id=record.source_snapshot_id,
            base_confirmed_matrix_id=record.base_confirmed_matrix_id,
            status=record.status.value,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
        for record in records
    ]


@router.put("/{project_matrix_draft_id}", response_model=ProjectMatrixDraftResponse)
def save_project_matrix_draft(
    project_id: str,
    project_matrix_draft_id: str,
    request: ProjectMatrixDraftSaveRequest,
    service: ProjectMatrixDraftPersistenceService = Depends(
        get_project_matrix_draft_persistence_service
    ),
) -> ProjectMatrixDraftResponse:
    """Replace one matrix draft working copy aggregate."""
    try:
        updated = service.update_draft(
            UpdateProjectMatrixDraftCommand(
                project_id=project_id,
                project_matrix_draft_id=project_matrix_draft_id,
                groups=tuple(
                    ProjectMatrixDraftGroupInput(
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
                    ProjectMatrixDraftRowInput(
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
                    ProjectMatrixDraftCellInput(
                        draft_row_id=item.draft_row_id,
                        draft_group_id=item.draft_group_id,
                        cell_value=item.cell_value,
                    )
                    for item in request.cells
                ),
            )
        )
    except ProjectMatrixDraftPersistenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectMatrixDraftPersistenceConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProjectMatrixDraftPersistenceError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_response(updated)


@router.post(
    "/{project_matrix_draft_id}/confirm",
    response_model=ConfirmedMatrixSnapshotResponse,
    status_code=201,
)
def confirm_project_matrix_draft(
    project_id: str,
    project_matrix_draft_id: str,
    request: ConfirmProjectMatrixDraftRequest,
    service: ConfirmedMatrixAuthorityService = Depends(get_confirmed_matrix_authority_service),
) -> ConfirmedMatrixSnapshotResponse:
    """Confirm one saved draft into immutable active Matrix authority."""
    try:
        confirmed = service.confirm_draft(
            ConfirmProjectMatrixDraftCommand(
                project_id=project_id,
                project_matrix_draft_id=project_matrix_draft_id,
                confirmed_by=request.confirmed_by,
            )
        )
    except ConfirmedMatrixAuthorityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConfirmedMatrixAuthorityConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ConfirmedMatrixAuthorityError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_confirmed_response(confirmed)


@router.post(
    "/{project_matrix_draft_id}/confirm-revision",
    response_model=ConfirmedMatrixSnapshotResponse,
    status_code=201,
)
def confirm_matrix_revision_draft(
    project_id: str,
    project_matrix_draft_id: str,
    request: ConfirmMatrixRevisionDraftRequest,
    service: MatrixRevisionFlowService = Depends(get_matrix_revision_flow_service),
) -> ConfirmedMatrixSnapshotResponse:
    """Confirm one revision draft and supersede previous active authority."""
    try:
        confirmed = service.confirm_revision_draft(
            ConfirmMatrixRevisionDraftCommand(
                project_id=project_id,
                project_matrix_draft_id=project_matrix_draft_id,
                confirmed_by=request.confirmed_by,
                superseded_reason=request.superseded_reason,
            )
        )
    except MatrixRevisionFlowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MatrixRevisionFlowConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except MatrixRevisionFlowError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_confirmed_response(confirmed)


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


def _to_confirmed_response(
    snapshot: ConfirmedMatrixSnapshot,
) -> ConfirmedMatrixSnapshotResponse:
    return ConfirmedMatrixSnapshotResponse(
        version=ConfirmedMatrixVersionResponse(
            confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
            project_id=snapshot.version.project_id,
            project_matrix_draft_id=snapshot.version.project_matrix_draft_id,
            source_import_id=snapshot.version.source_import_id,
            source_snapshot_id=snapshot.version.source_snapshot_id,
            confirmed_revision=snapshot.version.confirmed_revision,
            is_active_authority=snapshot.version.is_active_authority,
            status=snapshot.version.status.value,
            confirmed_by=snapshot.version.confirmed_by,
            confirmed_at=snapshot.version.confirmed_at,
            superseded_by_confirmed_matrix_id=snapshot.version.superseded_by_confirmed_matrix_id,
            superseded_at=snapshot.version.superseded_at,
            superseded_reason=snapshot.version.superseded_reason,
        ),
        groups=[
            ConfirmedMatrixGroupResponse(
                confirmed_group_id=group.confirmed_group_id,
                draft_group_id=group.draft_group_id,
                source_group_snapshot_id=group.source_group_snapshot_id,
                group_order=group.group_order,
                group_key=group.group_key,
                group_label=group.group_label,
                sample_quantity_expression=group.sample_quantity_expression,
                sample_note=group.sample_note,
            )
            for group in snapshot.groups
        ],
        rows=[
            ConfirmedMatrixRowResponse(
                confirmed_row_id=row.confirmed_row_id,
                draft_row_id=row.draft_row_id,
                source_row_snapshot_id=row.source_row_snapshot_id,
                row_order=row.row_order,
                test_item=row.test_item,
                source_section=row.source_section,
                method=row.method,
                condition=row.condition,
                requirement=row.requirement,
            )
            for row in snapshot.rows
        ],
        cells=[
            ConfirmedMatrixCellResponse(
                confirmed_cell_id=cell.confirmed_cell_id,
                confirmed_row_id=cell.confirmed_row_id,
                confirmed_group_id=cell.confirmed_group_id,
                draft_row_id=cell.draft_row_id,
                draft_group_id=cell.draft_group_id,
                cell_value=cell.cell_value,
            )
            for cell in snapshot.cells
        ],
    )
