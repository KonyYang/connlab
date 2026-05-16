from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from backend.modules.runtime_projection.composition import compose_runtime_projection_summary
from backend.modules.runtime_projection.fake_fixture_builder import (
    build_fake_projection_fixture,
)
from backend.modules.runtime_projection.models import (
    MatrixRowTechnicalContext,
    ProjectionState,
)
from backend.modules.runtime_projection.token_projection_builder import (
    build_step_token_projections,
)


def test_compose_empty_projection_returns_zero_summary() -> None:
    summary = compose_runtime_projection_summary(())
    assert summary.total_tokens == 0
    assert summary.group_count == 0
    assert summary.groups == ()


def test_compose_preserves_group_separation_for_same_sequence() -> None:
    group_1, _ = build_fake_projection_fixture(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G1",
        group_label="Group 1",
        raw_step_token_value="2",
    )
    group_2, _ = build_fake_projection_fixture(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G2",
        group_label="Group 2",
        raw_step_token_value="2",
    )
    summary = compose_runtime_projection_summary(group_1 + group_2)
    assert summary.total_tokens == 2
    assert summary.group_count == 2
    assert summary.groups[0].group_identity == "G1"
    assert summary.groups[1].group_identity == "G2"


def test_compose_handles_missing_projection_dimensions() -> None:
    projections, _ = build_fake_projection_fixture(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        raw_step_token_value="2",
        projection_state=ProjectionState(),
    )
    summary = compose_runtime_projection_summary(projections)
    assert summary.total_tokens == 1
    assert summary.groups[0].unique_sequences == 1
    attention_counts = summary.groups[0].aggregation_summary.attention_counts
    assert len(attention_counts) == 1
    assert attention_counts[0][0] is None
    assert attention_counts[0][1] == 1


def test_compose_counts_projection_dimensions_without_runtime_inference() -> None:
    projections, _ = build_fake_projection_fixture(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        raw_step_token_value="2 5 7",
        projection_state=ProjectionState(
            lifecycle="in_progress",
            evidence="missing",
            report_sync="stale",
            stale="stale",
            attention="p1",
        ),
    )
    summary = compose_runtime_projection_summary(projections)
    dimensions = summary.groups[0].aggregation_summary
    assert dimensions.lifecycle_counts == (
        ("in_progress", 3),
    )
    assert dimensions.evidence_counts == (
        ("missing", 3),
    )
    assert dimensions.report_sync_counts == (
        ("stale", 3),
    )
    assert dimensions.stale_counts == (
        ("stale", 3),
    )
    assert dimensions.attention_counts == (
        ("p1", 3),
    )


def test_fake_fixture_builder_produces_explicit_fake_inputs() -> None:
    projections, warnings = build_fake_projection_fixture(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        raw_step_token_value="2",
    )
    assert warnings == ()
    assert projections[0].lifecycle_projection == "not_started"
    assert projections[0].evidence_projection == "unknown"
    assert projections[0].report_sync_projection == "unknown"
    assert projections[0].stale_projection == "unknown"
    assert projections[0].attention_projection == "none"


def test_compose_does_not_mutate_projection_input() -> None:
    projections, _ = build_fake_projection_fixture(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        raw_step_token_value="2",
    )
    _ = compose_runtime_projection_summary(projections)
    with pytest.raises(FrozenInstanceError):
        projections[0].sequence_number = 99  # type: ignore[misc]


def test_compose_does_not_call_parser() -> None:
    # Build projections once (parser allowed here by design).
    projections, _ = build_fake_projection_fixture(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        raw_step_token_value="2",
    )
    # Composition should only read projections, no raw token parsing.
    summary = compose_runtime_projection_summary(projections)
    assert summary.total_tokens == 1


def test_builder_and_composer_keep_identity_references_stable() -> None:
    projections, _ = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        row_context=MatrixRowTechnicalContext(
            test_item_label="LLCR",
            section="6.1",
            method="EIA-364-23E",
            condition="20mV max, 100mA max",
            requirement="Initial <= 0.40mΩ",
        ),
        raw_step_token_value="2",
    )
    summary = compose_runtime_projection_summary(projections)
    assert summary.groups[0].group_identity == "G3"
    assert summary.groups[0].group_label == "Group 3"
