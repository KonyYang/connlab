"""Optional fake/static fixture builders for runtime projection unit tests."""

from __future__ import annotations

from backend.modules.runtime_projection.models import (
    MatrixRowTechnicalContext,
    ProjectionState,
)
from backend.modules.runtime_projection.token_projection_builder import (
    build_step_token_projections,
)


def build_fake_projection_fixture(
    *,
    project_reference: str,
    matrix_reference: str,
    group_identity: str,
    group_label: str,
    raw_step_token_value: str | None,
    row_context: MatrixRowTechnicalContext | None = None,
    projection_state: ProjectionState | None = None,
):
    """Build fake/static projection fixtures for tests using existing builders."""
    default_context = row_context or MatrixRowTechnicalContext(
        test_item_label="LLCR",
        section="6.1",
        method="EIA-364-23E",
        condition="20mV max, 100mA max",
        requirement="Initial <= 0.40mΩ",
    )
    return build_step_token_projections(
        project_reference=project_reference,
        matrix_reference=matrix_reference,
        group_identity=group_identity,
        group_label=group_label,
        row_context=default_context,
        raw_step_token_value=raw_step_token_value,
        projection_state=projection_state,
    )

