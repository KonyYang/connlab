from __future__ import annotations

from backend.modules.runtime_projection.models import MatrixRowTechnicalContext, ProjectionState
from backend.modules.runtime_projection.snapshot_adapter import (
    SnapshotBuildInput,
    SnapshotMatrixRowInput,
    build_runtime_projection_snapshot,
)


def _row_context(label: str) -> MatrixRowTechnicalContext:
    return MatrixRowTechnicalContext(
        test_item_label=label,
        section="6.1",
        method="EIA-364-23E",
        condition="20mV max, 100mA max",
        requirement="Initial <= 0.40mO",
    )


def test_snapshot_includes_project_and_matrix_references() -> None:
    build_input = SnapshotBuildInput(
        project_reference="P-001",
        matrix_reference="M-001",
        rows=(),
    )
    snapshot = build_runtime_projection_snapshot(build_input)
    assert snapshot.project_reference == "P-001"
    assert snapshot.matrix_reference == "M-001"


def test_snapshot_builds_matrix_overview_from_multiple_rows() -> None:
    build_input = SnapshotBuildInput(
        project_reference="P-001",
        matrix_reference="M-001",
        rows=(
            SnapshotMatrixRowInput(
                group_identity="G1",
                group_label="Group 1",
                row_context=_row_context("LLCR"),
                raw_step_token_value="2,3(a)",
            ),
            SnapshotMatrixRowInput(
                group_identity="G2",
                group_label="Group 2",
                row_context=_row_context("CR"),
                raw_step_token_value="2",
            ),
        ),
    )
    snapshot = build_runtime_projection_snapshot(build_input)
    assert snapshot.matrix_overview.total_tokens == 3
    assert snapshot.matrix_overview.group_count == 2
    assert snapshot.runtime_projection_summary.total_tokens == 3


def test_snapshot_builds_step_workspace_when_selected_reference_exists() -> None:
    seed_snapshot = build_runtime_projection_snapshot(
        SnapshotBuildInput(
            project_reference="P-001",
            matrix_reference="M-001",
            rows=(
                SnapshotMatrixRowInput(
                    group_identity="G1",
                    group_label="Group 1",
                    row_context=_row_context("LLCR"),
                    raw_step_token_value="2,3",
                ),
            ),
        )
    )
    selected_reference = seed_snapshot.matrix_overview.groups[0].tokens[1].token_reference
    snapshot = build_runtime_projection_snapshot(
        SnapshotBuildInput(
            project_reference="P-001",
            matrix_reference="M-001",
            rows=(
                SnapshotMatrixRowInput(
                    group_identity="G1",
                    group_label="Group 1",
                    row_context=_row_context("LLCR"),
                    raw_step_token_value="2,3",
                ),
            ),
            selected_token_reference=selected_reference,
        )
    )
    assert snapshot.step_workspace is not None
    assert snapshot.step_workspace.found is True
    assert snapshot.step_workspace.selected_token is not None
    assert snapshot.step_workspace.selected_token.token_reference == selected_reference


def test_snapshot_not_found_selected_token_is_deterministic() -> None:
    snapshot = build_runtime_projection_snapshot(
        SnapshotBuildInput(
            project_reference="P-001",
            matrix_reference="M-001",
            rows=(
                SnapshotMatrixRowInput(
                    group_identity="G1",
                    group_label="Group 1",
                    row_context=_row_context("LLCR"),
                    raw_step_token_value="2",
                ),
            ),
            selected_token_reference="missing-token",
        )
    )
    assert snapshot.step_workspace is not None
    assert snapshot.step_workspace.found is False
    assert snapshot.step_workspace.selected_token is None


def test_snapshot_parser_warnings_remain_visible() -> None:
    snapshot = build_runtime_projection_snapshot(
        SnapshotBuildInput(
            project_reference="P-001",
            matrix_reference="M-001",
            rows=(
                SnapshotMatrixRowInput(
                    group_identity="G1",
                    group_label="Group 1",
                    row_context=_row_context("LLCR"),
                    raw_step_token_value="2, A",
                ),
            ),
        )
    )
    assert "Unrecognized step token: 'A'." in snapshot.parser_warnings


def test_same_sequence_in_different_groups_remains_distinct() -> None:
    snapshot = build_runtime_projection_snapshot(
        SnapshotBuildInput(
            project_reference="P-001",
            matrix_reference="M-001",
            rows=(
                SnapshotMatrixRowInput(
                    group_identity="G1",
                    group_label="Group 1",
                    row_context=_row_context("LLCR"),
                    raw_step_token_value="2",
                ),
                SnapshotMatrixRowInput(
                    group_identity="G2",
                    group_label="Group 2",
                    row_context=_row_context("CR"),
                    raw_step_token_value="2",
                ),
            ),
        )
    )
    g1_token = snapshot.matrix_overview.groups[0].tokens[0].token_reference
    g2_token = snapshot.matrix_overview.groups[1].tokens[0].token_reference
    assert g1_token != g2_token


def test_fake_projection_dimensions_pass_through_as_projection_fields() -> None:
    snapshot = build_runtime_projection_snapshot(
        SnapshotBuildInput(
            project_reference="P-001",
            matrix_reference="M-001",
            rows=(
                SnapshotMatrixRowInput(
                    group_identity="G1",
                    group_label="Group 1",
                    row_context=_row_context("LLCR"),
                    raw_step_token_value="2",
                    projection_state=ProjectionState(
                        lifecycle="in_progress",
                        evidence="missing",
                        report_sync="stale",
                        stale="stale",
                        attention="p1",
                    ),
                ),
            ),
        )
    )
    token = snapshot.matrix_overview.groups[0].tokens[0]
    assert token.lifecycle_projection == "in_progress"
    assert token.evidence_projection == "missing"
    assert token.report_sync_projection == "stale"
    assert token.stale_projection == "stale"
    assert token.attention_projection == "p1"


def test_snapshot_adapter_does_not_mutate_input_rows() -> None:
    rows = (
        SnapshotMatrixRowInput(
            group_identity="G1",
            group_label="Group 1",
            row_context=_row_context("LLCR"),
            raw_step_token_value="2",
        ),
    )
    before = rows[0].raw_step_token_value
    _ = build_runtime_projection_snapshot(
        SnapshotBuildInput(
            project_reference="P-001",
            matrix_reference="M-001",
            rows=rows,
        )
    )
    assert rows[0].raw_step_token_value == before


def test_no_matrix_authority_mutation() -> None:
    matrix_reference = "M-001"
    _ = build_runtime_projection_snapshot(
        SnapshotBuildInput(
            project_reference="P-001",
            matrix_reference=matrix_reference,
            rows=(),
        )
    )
    assert matrix_reference == "M-001"


def test_no_project_lifecycle_mutation() -> None:
    project_reference = "P-001"
    _ = build_runtime_projection_snapshot(
        SnapshotBuildInput(
            project_reference=project_reference,
            matrix_reference="M-001",
            rows=(),
        )
    )
    assert project_reference == "P-001"
