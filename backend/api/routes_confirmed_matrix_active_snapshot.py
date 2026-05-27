"""Read-only active Confirmed Matrix snapshot route for frontend authority baseline checks."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_confirmed_matrix_authority_service
from backend.api.routes_project_matrix_drafts import (
    ConfirmedMatrixSnapshotResponse,
    _to_confirmed_response,
)
from backend.application.confirmed_matrix_authority_service import (
    ConfirmedMatrixAuthorityNotFoundError,
    ConfirmedMatrixAuthorityService,
)


router = APIRouter(tags=["confirmed-matrix-active-snapshot"])


@router.get(
    "/api/projects/{project_id}/confirmed-matrix/active-snapshot",
    response_model=ConfirmedMatrixSnapshotResponse,
)
def get_active_confirmed_matrix_snapshot(
    project_id: str,
    service: ConfirmedMatrixAuthorityService = Depends(
        get_confirmed_matrix_authority_service
    ),
) -> ConfirmedMatrixSnapshotResponse:
    """Return the current active Confirmed Matrix authority snapshot for one project."""
    try:
        snapshot = service.get_active_snapshot(project_id)
    except ConfirmedMatrixAuthorityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_confirmed_response(snapshot)

