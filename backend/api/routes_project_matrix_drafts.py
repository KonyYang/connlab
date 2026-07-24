"""Project Matrix draft working-copy persistence API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import (
    get_confirmed_matrix_authority_service,
    get_matrix_revision_flow_service,
    get_project_matrix_draft_persistence_service,
)
from backend.api.project_matrix_draft_dtos import *  # noqa: F403
from backend.api.project_matrix_draft_response_mappers import (
    to_confirmed_matrix_response,
    to_project_matrix_draft_response,
)
from backend.application.confirmed_matrix_authority_service import (
    ConfirmProjectMatrixDraftCommand,
    ConfirmedMatrixAuthorityConflictError,
    ConfirmedMatrixAuthorityError,
    ConfirmedMatrixAuthorityNotFoundError,
    ConfirmedMatrixAuthorityService,
)
from backend.application.matrix_revision_flow_service import (
    ConfirmMatrixRevisionDraftCommand,
    MatrixRevisionFlowConflictError,
    MatrixRevisionFlowError,
    MatrixRevisionFlowNotFoundError,
    MatrixRevisionFlowService,
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
    ProjectMatrixDurationAuthorityInput,
    UpdateProjectMatrixDraftCommand,
)


router = APIRouter(prefix="/api/projects/{project_id}/matrix-drafts", tags=["project-matrix-drafts"])


@router.post("", response_model=ProjectMatrixDraftResponse, status_code=201)  # noqa: F405
def create_project_matrix_draft(
    project_id: str,
    request: ProjectMatrixDraftCreateRequest,  # noqa: F405
    service: ProjectMatrixDraftPersistenceService = Depends(
        get_project_matrix_draft_persistence_service
    ),
) -> ProjectMatrixDraftResponse:  # noqa: F405
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
    return to_project_matrix_draft_response(draft)


@router.get("/{project_matrix_draft_id}", response_model=ProjectMatrixDraftResponse)  # noqa: F405
def get_project_matrix_draft(
    project_id: str,
    project_matrix_draft_id: str,
    service: ProjectMatrixDraftPersistenceService = Depends(
        get_project_matrix_draft_persistence_service
    ),
) -> ProjectMatrixDraftResponse:  # noqa: F405
    try:
        return to_project_matrix_draft_response(
            service.get_draft(
                project_id=project_id,
                project_matrix_draft_id=project_matrix_draft_id,
            )
        )
    except ProjectMatrixDraftPersistenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("", response_model=list[ProjectMatrixDraftSummaryResponse])  # noqa: F405
def list_project_matrix_drafts(
    project_id: str,
    service: ProjectMatrixDraftPersistenceService = Depends(
        get_project_matrix_draft_persistence_service
    ),
) -> list[ProjectMatrixDraftSummaryResponse]:  # noqa: F405
    try:
        records = service.list_drafts(project_id=project_id)
    except ProjectMatrixDraftPersistenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [
        ProjectMatrixDraftSummaryResponse(  # noqa: F405
            **{
                field: (
                    record.status.value
                    if field == "status"
                    else getattr(record, field)
                )
                for field in ProjectMatrixDraftSummaryResponse.model_fields  # noqa: F405
            }
        )
        for record in records
    ]


@router.put("/{project_matrix_draft_id}", response_model=ProjectMatrixDraftResponse)  # noqa: F405
def save_project_matrix_draft(
    project_id: str,
    project_matrix_draft_id: str,
    request: ProjectMatrixDraftSaveRequest,  # noqa: F405
    service: ProjectMatrixDraftPersistenceService = Depends(
        get_project_matrix_draft_persistence_service
    ),
) -> ProjectMatrixDraftResponse:  # noqa: F405
    try:
        updated = service.update_draft(
            UpdateProjectMatrixDraftCommand(
                project_id=project_id,
                project_matrix_draft_id=project_matrix_draft_id,
                groups=tuple(ProjectMatrixDraftGroupInput(**item.model_dump()) for item in request.groups),
                rows=tuple(ProjectMatrixDraftRowInput(**item.model_dump()) for item in request.rows),
                cells=tuple(ProjectMatrixDraftCellInput(**item.model_dump()) for item in request.cells),
                pre_test_buffer_days=request.pre_test_buffer_days,
                post_test_buffer_days=request.post_test_buffer_days,
                sample_received_date=request.sample_received_date,
                planned_test_start_date=request.planned_test_start_date,
                planned_test_complete_date=request.planned_test_complete_date,
                estimated_completion_date=request.estimated_completion_date,
                duration_authorities_present="duration_authorities" in request.model_fields_set,
                duration_authorities=(
                    tuple(
                        ProjectMatrixDurationAuthorityInput(**item.model_dump())
                        for item in request.duration_authorities
                    )
                    if request.duration_authorities is not None
                    else None
                ),
            )
        )
    except ProjectMatrixDraftPersistenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectMatrixDraftPersistenceConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProjectMatrixDraftPersistenceError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return to_project_matrix_draft_response(updated)


@router.post(
    "/{project_matrix_draft_id}/confirm",
    response_model=ConfirmedMatrixSnapshotResponse,  # noqa: F405
    status_code=201,
)
def confirm_project_matrix_draft(
    project_id: str,
    project_matrix_draft_id: str,
    request: ConfirmProjectMatrixDraftRequest,  # noqa: F405
    service: ConfirmedMatrixAuthorityService = Depends(get_confirmed_matrix_authority_service),
) -> ConfirmedMatrixSnapshotResponse:  # noqa: F405
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
    return to_confirmed_matrix_response(confirmed)


@router.post(
    "/{project_matrix_draft_id}/confirm-revision",
    response_model=ConfirmedMatrixSnapshotResponse,  # noqa: F405
    status_code=201,
)
def confirm_matrix_revision_draft(
    project_id: str,
    project_matrix_draft_id: str,
    request: ConfirmMatrixRevisionDraftRequest,  # noqa: F405
    service: MatrixRevisionFlowService = Depends(get_matrix_revision_flow_service),
) -> ConfirmedMatrixSnapshotResponse:  # noqa: F405
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
    return to_confirmed_matrix_response(confirmed)


# Compatibility aliases retained for existing internal imports and tests.
_to_response = to_project_matrix_draft_response
_to_confirmed_response = to_confirmed_matrix_response
