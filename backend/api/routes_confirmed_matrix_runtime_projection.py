"""Confirmed-Matrix-backed runtime projection read-only API route."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_confirmed_matrix_runtime_projection_service
from backend.api.runtime_projection_response_mapper import (
    RuntimeProjectionReadOnlySnapshotResponse,
    to_runtime_projection_read_only_snapshot_response,
)
from backend.application.confirmed_matrix_runtime_projection_service import (
    BuildConfirmedMatrixRuntimeProjectionCommand,
    ConfirmedMatrixRuntimeProjectionError,
    ConfirmedMatrixRuntimeProjectionNotFoundError,
    ConfirmedMatrixRuntimeProjectionService,
)


router = APIRouter(tags=["runtime-projection-read-only"])


@router.get(
    "/api/projects/{project_id}/runtime-projection/confirmed-matrix-snapshot",
    response_model=RuntimeProjectionReadOnlySnapshotResponse,
)
def get_confirmed_matrix_runtime_projection_snapshot(
    project_id: str,
    selected_token_reference: str | None = None,
    service: ConfirmedMatrixRuntimeProjectionService = Depends(
        get_confirmed_matrix_runtime_projection_service
    ),
) -> RuntimeProjectionReadOnlySnapshotResponse:
    """Return one projection snapshot built from active confirmed Matrix authority."""
    try:
        snapshot = service.build_snapshot(
            BuildConfirmedMatrixRuntimeProjectionCommand(
                project_id=project_id,
                selected_token_reference=selected_token_reference,
            )
        )
    except ConfirmedMatrixRuntimeProjectionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConfirmedMatrixRuntimeProjectionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return to_runtime_projection_read_only_snapshot_response(snapshot)
