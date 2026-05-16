"""Runtime projection module for minimal token projection slices."""

from backend.modules.runtime_projection.models import (
    DEFAULT_FAKE_PROJECTION_STATE,
    GroupRuntimeProjection,
    InteractiveStepTokenProjection,
    MatrixRowTechnicalContext,
    ProjectionAggregationSummary,
    ProjectionState,
    RuntimeProjectionSummary,
    TokenReference,
)
from backend.modules.runtime_projection.composition import (
    compose_runtime_projection_summary,
)
from backend.modules.runtime_projection.consumer_views import (
    MatrixOverviewConsumerView,
    MatrixOverviewGroupView,
    MatrixOverviewTokenView,
    SelectedStepTokenView,
    StepWorkspaceConsumerView,
    build_matrix_overview_consumer_view,
    build_step_workspace_consumer_view,
)
from backend.modules.runtime_projection.fake_fixture_builder import (
    build_fake_projection_fixture,
)
from backend.modules.runtime_projection.snapshot_adapter import (
    RuntimeProjectionSnapshot,
    SnapshotBuildInput,
    SnapshotMatrixRowInput,
    build_runtime_projection_snapshot,
)
from backend.modules.runtime_projection.token_projection_builder import (
    build_step_token_projections,
    build_token_reference,
)

__all__ = [
    "DEFAULT_FAKE_PROJECTION_STATE",
    "GroupRuntimeProjection",
    "InteractiveStepTokenProjection",
    "MatrixOverviewConsumerView",
    "MatrixOverviewGroupView",
    "MatrixOverviewTokenView",
    "MatrixRowTechnicalContext",
    "ProjectionAggregationSummary",
    "ProjectionState",
    "RuntimeProjectionSummary",
    "RuntimeProjectionSnapshot",
    "SelectedStepTokenView",
    "SnapshotBuildInput",
    "SnapshotMatrixRowInput",
    "StepWorkspaceConsumerView",
    "TokenReference",
    "build_matrix_overview_consumer_view",
    "build_runtime_projection_snapshot",
    "build_step_workspace_consumer_view",
    "build_fake_projection_fixture",
    "compose_runtime_projection_summary",
    "build_step_token_projections",
    "build_token_reference",
]
