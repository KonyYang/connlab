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
from backend.modules.runtime_projection.fake_fixture_builder import (
    build_fake_projection_fixture,
)
from backend.modules.runtime_projection.token_projection_builder import (
    build_step_token_projections,
    build_token_reference,
)

__all__ = [
    "DEFAULT_FAKE_PROJECTION_STATE",
    "GroupRuntimeProjection",
    "InteractiveStepTokenProjection",
    "MatrixRowTechnicalContext",
    "ProjectionAggregationSummary",
    "ProjectionState",
    "RuntimeProjectionSummary",
    "TokenReference",
    "build_fake_projection_fixture",
    "compose_runtime_projection_summary",
    "build_step_token_projections",
    "build_token_reference",
]
