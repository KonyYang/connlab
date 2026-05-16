from __future__ import annotations

from backend.api.routes_runtime_projection_read_only import (
    MatrixOverviewConsumerResponse,
    RuntimeProjectionReadOnlySnapshotResponse,
    RuntimeProjectionSummaryResponse,
    StepWorkspaceConsumerResponse,
)


def test_runtime_projection_response_contract_models_validate() -> None:
    summary = RuntimeProjectionSummaryResponse(
        total_tokens=1,
        group_count=1,
        groups=[],
    )
    overview = MatrixOverviewConsumerResponse(
        total_tokens=1,
        group_count=1,
        groups=[],
    )
    workspace = StepWorkspaceConsumerResponse(
        selected_token_reference="P|M|G1|2|",
        found=False,
        group_identity=None,
        group_label=None,
        group_token_references=[],
        previous_token_reference=None,
        next_token_reference=None,
        selected_token=None,
    )
    response = RuntimeProjectionReadOnlySnapshotResponse(
        project_reference="P-001",
        matrix_reference="M-001",
        parser_warnings=[],
        runtime_projection_summary=summary,
        matrix_overview=overview,
        step_workspace=workspace,
    )
    dumped = response.model_dump()
    assert dumped["project_reference"] == "P-001"
    assert dumped["runtime_projection_summary"]["total_tokens"] == 1
    assert dumped["matrix_overview"]["group_count"] == 1
    assert dumped["step_workspace"]["found"] is False


def test_runtime_projection_response_contract_allows_null_workspace() -> None:
    response = RuntimeProjectionReadOnlySnapshotResponse(
        project_reference="P-001",
        matrix_reference="M-001",
        parser_warnings=["Step token is missing."],
        runtime_projection_summary=RuntimeProjectionSummaryResponse(
            total_tokens=0,
            group_count=0,
            groups=[],
        ),
        matrix_overview=MatrixOverviewConsumerResponse(
            total_tokens=0,
            group_count=0,
            groups=[],
        ),
        step_workspace=None,
    )
    dumped = response.model_dump()
    assert dumped["step_workspace"] is None
    assert dumped["parser_warnings"] == ["Step token is missing."]
