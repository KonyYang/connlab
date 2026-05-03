from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_phase5_ux_decision_record_exists_and_sets_workbench_direction() -> None:
    """TASK_016 decision record defines the approved workbench direction."""
    source = (ROOT / "docs" / "phase5_workbench_ux_decision.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "Left navigation + top context bar + main work area",
        "Application Form -> Precheck -> LTR -> Project Folder",
        "not_started",
        "blockingReason",
        "AppShell.tsx",
        "LIMS Failure Modes To Avoid",
    ]:
        assert term in source


def test_phase5_ux_decision_record_keeps_future_scope_blocked() -> None:
    """TASK_016 explicitly blocks future non-MVP modules."""
    source = (ROOT / "docs" / "phase5_workbench_ux_decision.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "Matrix generation",
        "Report generation",
        "AI review",
        "Real email import",
        "Real Word parser hardening",
    ]:
        assert term in source


def test_phase5_decision_record_closes_phase_and_recommends_next_phase() -> None:
    """TASK_024 records Phase 5 completion state and next phase options."""
    source = (ROOT / "docs" / "phase5_workbench_ux_decision.md").read_text(
        encoding="utf-8"
    )
    board = (ROOT / "docs" / "task_board.md").read_text(encoding="utf-8")

    for term in [
        "Implemented Phase 5 Result",
        "manual execution -> pending human confirmation",
        "Phase 6A - Real Email/Word Intake And Human Confirmation",
        "explicit user approval",
    ]:
        assert term in source

    assert "Current Active Task: None - pending user approval for next phase" in board
    assert "TASK_024_PHASE5_DOCS_AND_BOARD_SYNC` | done" in board
    assert "Phase 6A - Outlook Email Package Intake" in board
