"""Runtime projection snapshot adapter for TASK_205."""

from __future__ import annotations

from dataclasses import dataclass

from backend.modules.runtime_projection.composition import compose_runtime_projection_summary
from backend.modules.runtime_projection.consumer_views import (
    MatrixOverviewConsumerView,
    StepWorkspaceConsumerView,
    build_matrix_overview_consumer_view,
    build_step_workspace_consumer_view,
)
from backend.modules.runtime_projection.models import (
    MatrixRowTechnicalContext,
    ProjectionState,
    RuntimeProjectionSummary,
)
from backend.modules.runtime_projection.token_projection_builder import (
    build_step_token_projections,
)


@dataclass(frozen=True, slots=True)
class SnapshotMatrixRowInput:
    """One Matrix row input used to build runtime token projections."""

    group_identity: str
    group_label: str
    row_context: MatrixRowTechnicalContext
    raw_step_token_value: str | None
    projection_state: ProjectionState | None = None


@dataclass(frozen=True, slots=True)
class SnapshotBuildInput:
    """Input payload for runtime projection snapshot building."""

    project_reference: str
    matrix_reference: str
    rows: tuple[SnapshotMatrixRowInput, ...]
    selected_token_reference: str | None = None


@dataclass(frozen=True, slots=True)
class RuntimeProjectionSnapshot:
    """Read-only runtime projection snapshot for downstream consumption."""

    project_reference: str
    matrix_reference: str
    parser_warnings: tuple[str, ...]
    runtime_projection_summary: RuntimeProjectionSummary
    matrix_overview: MatrixOverviewConsumerView
    step_workspace: StepWorkspaceConsumerView | None


def build_runtime_projection_snapshot(build_input: SnapshotBuildInput) -> RuntimeProjectionSnapshot:
    """Compose existing runtime projection outputs into one immutable snapshot."""
    projections = []
    warnings: list[str] = []
    for row in build_input.rows:
        row_projections, row_warnings = build_step_token_projections(
            project_reference=build_input.project_reference,
            matrix_reference=build_input.matrix_reference,
            group_identity=row.group_identity,
            group_label=row.group_label,
            row_context=row.row_context,
            raw_step_token_value=row.raw_step_token_value,
            projection_state=row.projection_state,
        )
        projections.extend(row_projections)
        warnings.extend(row_warnings)

    projection_tuple = tuple(projections)
    runtime_summary = compose_runtime_projection_summary(projection_tuple)
    matrix_overview = build_matrix_overview_consumer_view(projection_tuple)
    step_workspace = None
    if build_input.selected_token_reference is not None:
        step_workspace = build_step_workspace_consumer_view(
            projection_tuple,
            build_input.selected_token_reference,
        )

    return RuntimeProjectionSnapshot(
        project_reference=build_input.project_reference,
        matrix_reference=build_input.matrix_reference,
        parser_warnings=tuple(warnings),
        runtime_projection_summary=runtime_summary,
        matrix_overview=matrix_overview,
        step_workspace=step_workspace,
    )
