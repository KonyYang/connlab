from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from backend.modules.runtime_projection.models import (
    DEFAULT_FAKE_PROJECTION_STATE,
    MatrixRowTechnicalContext,
    ProjectionState,
)
from backend.modules.runtime_projection.token_projection_builder import (
    build_step_token_projections,
    build_token_reference,
)


def _row_context() -> MatrixRowTechnicalContext:
    return MatrixRowTechnicalContext(
        test_item_label="LLCR",
        section="6.1",
        method="EIA-364-23E",
        condition="20mV max, 100mA max",
        requirement="Initial <= 0.40mΩ",
    )


def test_token_reference_preserves_project_matrix_group_sequence() -> None:
    reference = build_token_reference(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        raw_token="2",
        sequence_number=2,
        suffix_note=None,
    )
    assert reference.project_reference == "P-001"
    assert reference.matrix_reference == "M-001"
    assert reference.group_identity == "G3"
    assert reference.sequence_number == 2


def test_same_sequence_in_different_groups_remains_distinct() -> None:
    row = _row_context()
    group_1, _ = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G1",
        group_label="Group 1",
        row_context=row,
        raw_step_token_value="2",
    )
    group_2, _ = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G2",
        group_label="Group 2",
        row_context=row,
        raw_step_token_value="2",
    )
    assert group_1[0].token_reference != group_2[0].token_reference


def test_raw_token_is_preserved() -> None:
    row = _row_context()
    projections, _ = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        row_context=row,
        raw_step_token_value="2",
    )
    assert projections[0].raw_token == "2"


def test_suffix_note_is_preserved_from_parser_output() -> None:
    row = _row_context()
    projections, _ = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        row_context=row,
        raw_step_token_value="3(a)",
    )
    assert projections[0].suffix_note == "(a)"


def test_parser_warnings_remain_visible() -> None:
    row = _row_context()
    projections, warnings = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        row_context=row,
        raw_step_token_value="2, A",
    )
    assert len(projections) == 1
    assert "Unrecognized step token: 'A'." in warnings


def test_projection_dimensions_do_not_redefine_identity() -> None:
    row = _row_context()
    projections_a, _ = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        row_context=row,
        raw_step_token_value="2",
        projection_state=ProjectionState(
            lifecycle="in_progress",
            evidence="missing",
            report_sync="stale",
            stale="stale",
            attention="p1",
        ),
    )
    projections_b, _ = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        row_context=row,
        raw_step_token_value="2",
        projection_state=ProjectionState(
            lifecycle="pass",
            evidence="present",
            report_sync="current",
            stale="current",
            attention="none",
        ),
    )
    assert projections_a[0].token_reference == projections_b[0].token_reference


def test_missing_projection_dimensions_do_not_invalidate_identity() -> None:
    row = _row_context()
    projections, _ = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        row_context=row,
        raw_step_token_value="2",
        projection_state=ProjectionState(),
    )
    assert projections[0].token_reference
    assert projections[0].lifecycle_projection is None
    assert projections[0].evidence_projection is None


def test_fake_projection_defaults_are_optional_projection_dimensions() -> None:
    row = _row_context()
    projections, _ = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        row_context=row,
        raw_step_token_value="2",
    )
    assert projections[0].lifecycle_projection == DEFAULT_FAKE_PROJECTION_STATE.lifecycle
    assert projections[0].evidence_projection == DEFAULT_FAKE_PROJECTION_STATE.evidence
    assert projections[0].report_sync_projection == DEFAULT_FAKE_PROJECTION_STATE.report_sync
    assert projections[0].stale_projection == DEFAULT_FAKE_PROJECTION_STATE.stale
    assert projections[0].attention_projection == DEFAULT_FAKE_PROJECTION_STATE.attention


def test_no_matrix_authority_mutation() -> None:
    row = _row_context()
    matrix_reference = "M-001"
    _ = build_step_token_projections(
        project_reference="P-001",
        matrix_reference=matrix_reference,
        group_identity="G3",
        group_label="Group 3",
        row_context=row,
        raw_step_token_value="2",
    )
    assert matrix_reference == "M-001"


def test_no_project_lifecycle_mutation() -> None:
    row = _row_context()
    project_reference = "P-001"
    _ = build_step_token_projections(
        project_reference=project_reference,
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        row_context=row,
        raw_step_token_value="2",
    )
    assert project_reference == "P-001"


def test_multi_token_cell_produces_multiple_projection_tokens() -> None:
    row = _row_context()
    projections, warnings = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        row_context=row,
        raw_step_token_value="2,5,7",
    )
    assert warnings == ()
    assert [item.sequence_number for item in projections] == [2, 5, 7]


@pytest.mark.parametrize(
    "raw_step_token_value, expected_warning",
    [
        (None, "Step token is missing."),
        ("", "Step token is missing."),
        ("A, B", "No valid numeric step token was found."),
    ],
)
def test_empty_or_invalid_token_input_matches_existing_parser_behavior(
    raw_step_token_value: str | None,
    expected_warning: str,
) -> None:
    row = _row_context()
    projections, warnings = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        row_context=row,
        raw_step_token_value=raw_step_token_value,
    )
    assert projections == ()
    assert expected_warning in warnings


def test_projection_output_is_immutable() -> None:
    row = _row_context()
    projections, _ = build_step_token_projections(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G3",
        group_label="Group 3",
        row_context=row,
        raw_step_token_value="2",
    )
    with pytest.raises(FrozenInstanceError):
        projections[0].sequence_number = 3  # type: ignore[misc]
