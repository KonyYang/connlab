from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_phase9_board_closes_after_task059_completion() -> None:
    """TASK_059 closes Phase 9 while later approved phases may advance."""
    board = (ROOT / "docs" / "task_board.md").read_text(encoding="utf-8")

    assert "Current Phase: `Phase 10A - Intake Entry Completion`" in board
    assert "Current Active Task: None - pending user approval for next phase" in board
    assert "> Status: Phase 10A complete" in board
    assert "| T9-1 | `TASK_053_PHASE9_SCOPE_AND_BOARD_ACTIVATION` | done |" in board
    assert (
        "| T9-2 | `TASK_054_LTR_READINESS_PREVIEW_COMMIT_FRONTEND_WIRING` | done |"
        in board
    )
    assert "| T9-3 | `TASK_055_INTAKE_EXCEPTION_WORKFLOW_FRONTEND_WIRING` | done |" in board
    assert "| T9-4 | `TASK_056_FOLDER_EVIDENCE_PLACEMENT_FRONTEND_WIRING` | done |" in board
    assert "| T9-5 | `TASK_057_PROJECT_LOOKUP_SAMPLE_TESTING_SUMMARY_FRONTEND_PANEL` | done |" in board
    assert "| T9-6 | `TASK_058_LIFECYCLE_GUARDS_DISABLED_REASON_UI` | done |" in board
    assert "| T9-7 | `TASK_059_PHASE9_BROWSER_SMOKE_AND_DOCS_SYNC` | done |" in board
    assert "Phase 9 validation summary" in board


def test_phase9_task_files_exist_and_preserve_scope() -> None:
    """Phase 9 tasks exist and keep future scope blocked."""
    expected_tasks = [
        "TASK_053_PHASE9_SCOPE_AND_BOARD_ACTIVATION.md",
        "TASK_054_LTR_READINESS_PREVIEW_COMMIT_FRONTEND_WIRING.md",
        "TASK_055_INTAKE_EXCEPTION_WORKFLOW_FRONTEND_WIRING.md",
        "TASK_056_FOLDER_EVIDENCE_PLACEMENT_FRONTEND_WIRING.md",
        "TASK_057_PROJECT_LOOKUP_SAMPLE_TESTING_SUMMARY_FRONTEND_PANEL.md",
        "TASK_058_LIFECYCLE_GUARDS_DISABLED_REASON_UI.md",
        "TASK_059_PHASE9_BROWSER_SMOKE_AND_DOCS_SYNC.md",
    ]

    for filename in expected_tasks:
        task = ROOT / "tasks" / filename
        assert task.is_file()
        source = task.read_text(encoding="utf-8")
        assert "Matrix" in source
        assert "Report" in source
        assert "AI review" in source


def test_task054_defines_ltr_ui_wiring_without_workbook_write() -> None:
    """The first Phase 9 implementation task is LTR UI wiring only."""
    task = (
        ROOT
        / "tasks"
        / "TASK_054_LTR_READINESS_PREVIEW_COMMIT_FRONTEND_WIRING.md"
    ).read_text(encoding="utf-8")

    for term in [
        "Show LTR readiness fields",
        "Add no-write LTR preview action",
        "Add local commit action",
        "No external workbook write",
        "$impeccable",
    ]:
        assert term in task


def test_phase9_validation_summary_closes_phase_without_future_scope() -> None:
    """TASK_059 records Phase 9 closeout without future scope."""
    summary = (ROOT / "docs" / "phase9_validation_summary.md").read_text(
        encoding="utf-8"
    )
    checklist = (ROOT / "docs" / "frontend_smoke_checklist.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "Status: Phase 9 complete",
        "Manual Browser Smoke Checklist",
        "LTR readiness",
        "Evidence placement",
        "lifecycle guard",
        "Do not activate either candidate automatically",
    ]:
        assert term in summary

    for term in [
        "Phase 9 Operator Workflow Wiring",
        "Read-only lookup",
        "No-overwrite",
        "Lifecycle guards",
    ]:
        assert term in checklist
