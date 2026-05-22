"""Read-only runtime projection snapshot API adapter routes for TASK_206."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.runtime_projection_response_mapper import (
    MatrixOverviewConsumerResponse,
    RuntimeProjectionReadOnlySnapshotResponse,
    RuntimeProjectionSummaryResponse,
    StepWorkspaceConsumerResponse,
    to_runtime_projection_read_only_snapshot_response,
)
from backend.application.runtime_projection_read_only_service import (
    RuntimeProjectionReadOnlyService,
)
from backend.modules.runtime_projection.models import MatrixRowTechnicalContext, ProjectionState
from backend.modules.runtime_projection.snapshot_adapter import (
    SnapshotBuildInput,
    SnapshotMatrixRowInput,
)


router = APIRouter(tags=["runtime-projection-read-only"])
_runtime_projection_read_only_service = RuntimeProjectionReadOnlyService()


class ProjectionStateRequest(BaseModel):
    """Optional projection dimensions for read-only snapshot building."""

    lifecycle: str | None = None
    evidence: str | None = None
    report_sync: str | None = None
    stale: str | None = None
    attention: str | None = None


class MatrixRowContextRequest(BaseModel):
    """Matrix row technical context for snapshot build input."""

    test_item_label: str = Field(min_length=1)
    section: str = ""
    method: str = ""
    condition: str = ""
    requirement: str = ""


class SnapshotRowRequest(BaseModel):
    """One Matrix row request item for snapshot building."""

    group_identity: str = Field(min_length=1)
    group_label: str = Field(min_length=1)
    row_context: MatrixRowContextRequest
    raw_step_token_value: str | None = None
    projection_state: ProjectionStateRequest | None = None


class RuntimeProjectionReadOnlySnapshotRequest(BaseModel):
    """Read-only runtime projection snapshot build request."""

    project_reference: str = Field(min_length=1)
    matrix_reference: str = Field(min_length=1)
    rows: list[SnapshotRowRequest]
    selected_token_reference: str | None = None


@router.post(
    "/api/runtime-projection/read-only-snapshot",
    response_model=RuntimeProjectionReadOnlySnapshotResponse,
)
def runtime_projection_read_only_snapshot(
    request: RuntimeProjectionReadOnlySnapshotRequest,
) -> RuntimeProjectionReadOnlySnapshotResponse:
    """Return one deterministic read-only runtime projection snapshot."""
    build_input = _to_build_input(request)
    snapshot = _runtime_projection_read_only_service.build_snapshot(build_input)
    return to_runtime_projection_read_only_snapshot_response(snapshot)


def _to_build_input(
    request: RuntimeProjectionReadOnlySnapshotRequest,
) -> SnapshotBuildInput:
    rows = tuple(
        SnapshotMatrixRowInput(
            group_identity=row.group_identity,
            group_label=row.group_label,
            row_context=MatrixRowTechnicalContext(
                test_item_label=row.row_context.test_item_label,
                section=row.row_context.section,
                method=row.row_context.method,
                condition=row.row_context.condition,
                requirement=row.row_context.requirement,
            ),
            raw_step_token_value=row.raw_step_token_value,
            projection_state=(
                ProjectionState(
                    lifecycle=row.projection_state.lifecycle,
                    evidence=row.projection_state.evidence,
                    report_sync=row.projection_state.report_sync,
                    stale=row.projection_state.stale,
                    attention=row.projection_state.attention,
                )
                if row.projection_state is not None
                else None
            ),
        )
        for row in request.rows
    )
    return SnapshotBuildInput(
        project_reference=request.project_reference,
        matrix_reference=request.matrix_reference,
        rows=rows,
        selected_token_reference=request.selected_token_reference,
    )
