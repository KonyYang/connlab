"""Read-only runtime projection snapshot API adapter routes for TASK_206."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.modules.runtime_projection.models import MatrixRowTechnicalContext, ProjectionState
from backend.modules.runtime_projection.snapshot_adapter import (
    SnapshotBuildInput,
    SnapshotMatrixRowInput,
    build_runtime_projection_snapshot,
)


router = APIRouter(tags=["runtime-projection-read-only"])


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


class RuntimeProjectionReadOnlySnapshotResponse(BaseModel):
    """Read-only runtime projection snapshot response."""

    project_reference: str
    matrix_reference: str
    parser_warnings: list[str]
    runtime_projection_summary: "RuntimeProjectionSummaryResponse"
    matrix_overview: "MatrixOverviewConsumerResponse"
    step_workspace: "StepWorkspaceConsumerResponse | None"


class ValueCountItemResponse(BaseModel):
    value: str | None
    count: int


class ProjectionAggregationSummaryResponse(BaseModel):
    lifecycle_counts: list[ValueCountItemResponse]
    evidence_counts: list[ValueCountItemResponse]
    report_sync_counts: list[ValueCountItemResponse]
    stale_counts: list[ValueCountItemResponse]
    attention_counts: list[ValueCountItemResponse]


class GroupRuntimeProjectionResponse(BaseModel):
    group_identity: str
    group_label: str
    total_tokens: int
    unique_sequences: int
    aggregation_summary: ProjectionAggregationSummaryResponse


class RuntimeProjectionSummaryResponse(BaseModel):
    total_tokens: int
    group_count: int
    groups: list[GroupRuntimeProjectionResponse]


class MatrixOverviewTokenResponse(BaseModel):
    token_reference: str
    raw_token: str
    sequence_number: int
    suffix_note: str | None
    lifecycle_projection: str | None
    evidence_projection: str | None
    report_sync_projection: str | None
    stale_projection: str | None
    attention_projection: str | None


class MatrixOverviewGroupResponse(BaseModel):
    group_identity: str
    group_label: str
    total_tokens: int
    unique_sequences: int
    tokens: list[MatrixOverviewTokenResponse]


class MatrixOverviewConsumerResponse(BaseModel):
    total_tokens: int
    group_count: int
    groups: list[MatrixOverviewGroupResponse]


class SelectedStepTokenResponse(BaseModel):
    token_reference: str
    raw_token: str
    sequence_number: int
    suffix_note: str | None
    lifecycle_projection: str | None
    evidence_projection: str | None
    report_sync_projection: str | None
    stale_projection: str | None
    attention_projection: str | None
    test_item_label: str
    section: str
    method: str
    condition: str
    requirement: str


class StepWorkspaceConsumerResponse(BaseModel):
    selected_token_reference: str
    found: bool
    group_identity: str | None
    group_label: str | None
    group_token_references: list[str]
    previous_token_reference: str | None
    next_token_reference: str | None
    selected_token: SelectedStepTokenResponse | None


@router.post(
    "/api/runtime-projection/read-only-snapshot",
    response_model=RuntimeProjectionReadOnlySnapshotResponse,
)
def runtime_projection_read_only_snapshot(
    request: RuntimeProjectionReadOnlySnapshotRequest,
) -> RuntimeProjectionReadOnlySnapshotResponse:
    """Return one deterministic read-only runtime projection snapshot."""
    build_input = _to_build_input(request)
    snapshot = build_runtime_projection_snapshot(build_input)
    return _snapshot_response(snapshot)


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


def _snapshot_response(snapshot) -> RuntimeProjectionReadOnlySnapshotResponse:
    snapshot_data = asdict(snapshot)
    return RuntimeProjectionReadOnlySnapshotResponse(
        project_reference=snapshot_data["project_reference"],
        matrix_reference=snapshot_data["matrix_reference"],
        parser_warnings=list(snapshot_data["parser_warnings"]),
        runtime_projection_summary=_runtime_summary_response(
            snapshot_data["runtime_projection_summary"]
        ),
        matrix_overview=_matrix_overview_response(snapshot_data["matrix_overview"]),
        step_workspace=_step_workspace_response(snapshot_data["step_workspace"]),
    )


def _value_count_items(values: list[list[str | None | int]] | tuple[tuple[str | None, int], ...]) -> list[ValueCountItemResponse]:
    return [ValueCountItemResponse(value=item[0], count=item[1]) for item in values]


def _runtime_summary_response(summary_data: dict) -> RuntimeProjectionSummaryResponse:
    groups: list[GroupRuntimeProjectionResponse] = []
    for group in summary_data["groups"]:
        aggregation = group["aggregation_summary"]
        groups.append(
            GroupRuntimeProjectionResponse(
                group_identity=group["group_identity"],
                group_label=group["group_label"],
                total_tokens=group["total_tokens"],
                unique_sequences=group["unique_sequences"],
                aggregation_summary=ProjectionAggregationSummaryResponse(
                    lifecycle_counts=_value_count_items(aggregation["lifecycle_counts"]),
                    evidence_counts=_value_count_items(aggregation["evidence_counts"]),
                    report_sync_counts=_value_count_items(aggregation["report_sync_counts"]),
                    stale_counts=_value_count_items(aggregation["stale_counts"]),
                    attention_counts=_value_count_items(aggregation["attention_counts"]),
                ),
            )
        )
    return RuntimeProjectionSummaryResponse(
        total_tokens=summary_data["total_tokens"],
        group_count=summary_data["group_count"],
        groups=groups,
    )


def _matrix_overview_response(overview_data: dict) -> MatrixOverviewConsumerResponse:
    groups: list[MatrixOverviewGroupResponse] = []
    for group in overview_data["groups"]:
        tokens = [
            MatrixOverviewTokenResponse(
                token_reference=token["token_reference"],
                raw_token=token["raw_token"],
                sequence_number=token["sequence_number"],
                suffix_note=token["suffix_note"],
                lifecycle_projection=token["lifecycle_projection"],
                evidence_projection=token["evidence_projection"],
                report_sync_projection=token["report_sync_projection"],
                stale_projection=token["stale_projection"],
                attention_projection=token["attention_projection"],
            )
            for token in group["tokens"]
        ]
        groups.append(
            MatrixOverviewGroupResponse(
                group_identity=group["group_identity"],
                group_label=group["group_label"],
                total_tokens=group["total_tokens"],
                unique_sequences=group["unique_sequences"],
                tokens=tokens,
            )
        )
    return MatrixOverviewConsumerResponse(
        total_tokens=overview_data["total_tokens"],
        group_count=overview_data["group_count"],
        groups=groups,
    )


def _step_workspace_response(workspace_data: dict | None) -> StepWorkspaceConsumerResponse | None:
    if workspace_data is None:
        return None

    selected = workspace_data["selected_token"]
    selected_token = None
    if selected is not None:
        selected_token = SelectedStepTokenResponse(
            token_reference=selected["token_reference"],
            raw_token=selected["raw_token"],
            sequence_number=selected["sequence_number"],
            suffix_note=selected["suffix_note"],
            lifecycle_projection=selected["lifecycle_projection"],
            evidence_projection=selected["evidence_projection"],
            report_sync_projection=selected["report_sync_projection"],
            stale_projection=selected["stale_projection"],
            attention_projection=selected["attention_projection"],
            test_item_label=selected["test_item_label"],
            section=selected["section"],
            method=selected["method"],
            condition=selected["condition"],
            requirement=selected["requirement"],
        )

    return StepWorkspaceConsumerResponse(
        selected_token_reference=workspace_data["selected_token_reference"],
        found=workspace_data["found"],
        group_identity=workspace_data["group_identity"],
        group_label=workspace_data["group_label"],
        group_token_references=list(workspace_data["group_token_references"]),
        previous_token_reference=workspace_data["previous_token_reference"],
        next_token_reference=workspace_data["next_token_reference"],
        selected_token=selected_token,
    )
