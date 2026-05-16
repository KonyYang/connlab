from __future__ import annotations

from backend.api.routes_runtime_projection_read_only import (
    MatrixRowContextRequest,
    ProjectionStateRequest,
    RuntimeProjectionReadOnlySnapshotRequest,
    SnapshotRowRequest,
    _to_build_input,
)


def test_to_build_input_maps_request_without_mutation() -> None:
    request = RuntimeProjectionReadOnlySnapshotRequest(
        project_reference="P-001",
        matrix_reference="M-001",
        selected_token_reference="token-1",
        rows=[
            SnapshotRowRequest(
                group_identity="G1",
                group_label="Group 1",
                row_context=MatrixRowContextRequest(
                    test_item_label="LLCR",
                    section="6.1",
                    method="EIA-364-23E",
                    condition="20mV max",
                    requirement="Initial <= 0.40mO",
                ),
                raw_step_token_value="2,3(a)",
                projection_state=ProjectionStateRequest(
                    lifecycle="in_progress",
                    evidence="missing",
                    report_sync="stale",
                    stale="stale",
                    attention="p1",
                ),
            )
        ],
    )

    build_input = _to_build_input(request)
    assert build_input.project_reference == "P-001"
    assert build_input.matrix_reference == "M-001"
    assert build_input.selected_token_reference == "token-1"
    assert len(build_input.rows) == 1
    assert build_input.rows[0].group_identity == "G1"
    assert build_input.rows[0].row_context.test_item_label == "LLCR"
    assert build_input.rows[0].projection_state is not None
    assert build_input.rows[0].projection_state.lifecycle == "in_progress"
    assert request.project_reference == "P-001"


def test_to_build_input_handles_missing_projection_state() -> None:
    request = RuntimeProjectionReadOnlySnapshotRequest(
        project_reference="P-001",
        matrix_reference="M-001",
        rows=[
            SnapshotRowRequest(
                group_identity="G1",
                group_label="Group 1",
                row_context=MatrixRowContextRequest(
                    test_item_label="LLCR",
                    section="6.1",
                    method="EIA-364-23E",
                    condition="20mV max",
                    requirement="Initial <= 0.40mO",
                ),
                raw_step_token_value="2",
            )
        ],
    )

    build_input = _to_build_input(request)
    assert build_input.selected_token_reference is None
    assert build_input.rows[0].projection_state is None
