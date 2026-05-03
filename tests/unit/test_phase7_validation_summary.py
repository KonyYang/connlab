from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_phase7_validation_summary_closes_phase_without_future_scope() -> None:
    """TASK_051 records Phase 7 closeout without activating future work."""
    summary = (ROOT / "docs" / "phase7_validation_summary.md").read_text(
        encoding="utf-8"
    )
    board = (ROOT / "docs" / "task_board.md").read_text(encoding="utf-8")

    for term in [
        "Status: Phase 7 complete",
        "Manual Smoke Checklist",
        "Workbook Write Mode",
        "Write mode is disabled by default",
        "configuration-driven",
        "Do not activate either candidate automatically",
    ]:
        assert term in summary

    assert (
        "Current Active Task: None - pending user approval for next phase"
        in board
    )
    assert "| T7-16 | `TASK_051_PHASE7_VALIDATION_AND_DOCS_SYNC` | done |" in board
    assert "Current recommendation:" in board
    assert "Phase 10A has been explicitly approved by the user" in board


def test_phase7_task_file_is_done() -> None:
    """The TASK_051 file must match the closed board state."""
    task = (
        ROOT / "tasks" / "TASK_051_PHASE7_VALIDATION_AND_DOCS_SYNC.md"
    ).read_text(encoding="utf-8")

    assert "## Status\n\ndone" in task
