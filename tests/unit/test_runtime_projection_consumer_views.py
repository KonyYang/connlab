from __future__ import annotations

from backend.modules.runtime_projection.consumer_views import (
    build_matrix_overview_consumer_view,
    build_step_workspace_consumer_view,
)
from backend.modules.runtime_projection.fake_fixture_builder import (
    build_fake_projection_fixture,
)
from backend.modules.runtime_projection.models import ProjectionState


def _multi_group_projections():
    group_1, _ = build_fake_projection_fixture(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G1",
        group_label="Group 1",
        raw_step_token_value="2,3(a)",
        projection_state=ProjectionState(
            lifecycle="in_progress",
            evidence="missing",
            report_sync="stale",
            stale="stale",
            attention="p1",
        ),
    )
    group_2, _ = build_fake_projection_fixture(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G2",
        group_label="Group 2",
        raw_step_token_value="2",
        projection_state=ProjectionState(
            lifecycle=None,
            evidence=None,
            report_sync=None,
            stale=None,
            attention=None,
        ),
    )
    return group_1 + group_2


def test_matrix_overview_groups_tokens_by_stable_group_identity() -> None:
    projections = _multi_group_projections()
    view = build_matrix_overview_consumer_view(projections)
    assert view.total_tokens == 3
    assert view.group_count == 2
    assert view.groups[0].group_identity == "G1"
    assert view.groups[1].group_identity == "G2"


def test_matrix_overview_exposes_token_references_without_redefining_identity() -> None:
    projections = _multi_group_projections()
    view = build_matrix_overview_consumer_view(projections)
    projection_reference = projections[0].token_reference
    assert view.groups[0].tokens[0].token_reference == projection_reference


def test_same_sequence_in_different_groups_remains_distinct() -> None:
    projections = _multi_group_projections()
    view = build_matrix_overview_consumer_view(projections)
    g1_token = view.groups[0].tokens[0]
    g2_token = view.groups[1].tokens[0]
    assert g1_token.sequence_number == g2_token.sequence_number == 2
    assert g1_token.token_reference != g2_token.token_reference


def test_projection_markers_remain_read_only_consumer_fields() -> None:
    projections = _multi_group_projections()
    view = build_matrix_overview_consumer_view(projections)
    token = view.groups[0].tokens[0]
    assert token.lifecycle_projection == "in_progress"
    assert token.evidence_projection == "missing"
    assert token.report_sync_projection == "stale"
    assert token.stale_projection == "stale"
    assert token.attention_projection == "p1"


def test_step_workspace_selects_token_by_stable_reference() -> None:
    projections = _multi_group_projections()
    selected_reference = projections[1].token_reference
    view = build_step_workspace_consumer_view(projections, selected_reference)
    assert view.found is True
    assert view.selected_token is not None
    assert view.selected_token.token_reference == selected_reference


def test_step_workspace_not_found_result_is_deterministic() -> None:
    projections = _multi_group_projections()
    view = build_step_workspace_consumer_view(projections, "unknown-token")
    assert view.found is False
    assert view.selected_token is None
    assert view.group_token_references == ()
    assert view.group_identity is None
    assert view.group_label is None


def test_missing_projection_dimensions_do_not_invalidate_identity() -> None:
    projections = _multi_group_projections()
    g2_reference = projections[2].token_reference
    view = build_step_workspace_consumer_view(projections, g2_reference)
    assert view.found is True
    assert view.selected_token is not None
    assert view.selected_token.token_reference == g2_reference
    assert view.selected_token.lifecycle_projection is None
    assert view.selected_token.evidence_projection is None
    assert view.selected_token.report_sync_projection is None
    assert view.selected_token.stale_projection is None
    assert view.selected_token.attention_projection is None


def test_consumer_view_functions_do_not_mutate_projection_input() -> None:
    projections = _multi_group_projections()
    before = tuple(item.token_reference for item in projections)
    _ = build_matrix_overview_consumer_view(projections)
    _ = build_step_workspace_consumer_view(projections, projections[0].token_reference)
    after = tuple(item.token_reference for item in projections)
    assert before == after


def test_no_matrix_authority_mutation() -> None:
    matrix_reference = "M-001"
    projections, _ = build_fake_projection_fixture(
        project_reference="P-001",
        matrix_reference=matrix_reference,
        group_identity="G1",
        group_label="Group 1",
        raw_step_token_value="2",
    )
    _ = build_matrix_overview_consumer_view(projections)
    assert matrix_reference == "M-001"


def test_no_project_lifecycle_mutation() -> None:
    project_reference = "P-001"
    projections, _ = build_fake_projection_fixture(
        project_reference=project_reference,
        matrix_reference="M-001",
        group_identity="G1",
        group_label="Group 1",
        raw_step_token_value="2",
    )
    _ = build_matrix_overview_consumer_view(projections)
    assert project_reference == "P-001"


def test_multi_token_cell_produces_multiple_consumer_tokens() -> None:
    projections, _ = build_fake_projection_fixture(
        project_reference="P-001",
        matrix_reference="M-001",
        group_identity="G1",
        group_label="Group 1",
        raw_step_token_value="2,5,7",
    )
    view = build_matrix_overview_consumer_view(projections)
    assert [item.sequence_number for item in view.groups[0].tokens] == [2, 5, 7]


def test_empty_projection_input_returns_deterministic_empty_view() -> None:
    matrix_view = build_matrix_overview_consumer_view(())
    workspace_view = build_step_workspace_consumer_view((), "missing")
    assert matrix_view.total_tokens == 0
    assert matrix_view.group_count == 0
    assert matrix_view.groups == ()
    assert workspace_view.found is False
    assert workspace_view.selected_token is None
