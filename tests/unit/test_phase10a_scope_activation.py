from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_phase10a_board_closes_after_task065_completion() -> None:
    """TASK_065 closes Phase 10A without activating later work."""
    board = (ROOT / "docs" / "task_board.md").read_text(encoding="utf-8")

    assert "> Status: Phase 10A complete" in board
    assert "Current Phase: `Phase 10A - Intake Entry Completion`" in board
    assert "Current Active Task: None - pending user approval for next phase" in board
    assert "### Phase 10A - Intake Entry Completion" in board
    assert "| T10A-1 | `TASK_060_PHASE10A_SCOPE_AND_BOARD_ACTIVATION` | done |" in board
    assert "| T10A-2 | `TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY` | done |" in board
    assert "| T10A-3 | `TASK_062_INTAKE_PACKAGE_DETAIL_REAL_DATA_WIRING` | done |" in board
    assert "| T10A-4 | `TASK_063_DIRECT_MANUAL_INTAKE_ENTRY` | done |" in board
    assert "| T10A-5 | `TASK_064_UNIFIED_INTAKE_CASE_REVIEW_AND_CONFIRMATION_UI` | done |" in board
    assert "| T10A-6 | `TASK_065_INTAKE_ENTRY_BROWSER_SMOKE_AND_DOCS_SYNC` | done |" in board
    assert "Phase 10A validation summary" in board
    assert (
        "copied-workbook LTR write hardening is deferred until explicit user approval"
        in board
    )


def test_phase10a_plan_documents_email_first_and_manual_exception() -> None:
    """The Phase 10A plan preserves the corrected intake-entry priority."""
    plan = (ROOT / "docs" / "phase10a_intake_entry_completion_plan.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "Manual `.msg` package import",
        "Direct manual intake",
        "No Outlook inbox auto-scan",
        "No email sending",
        "No copied-workbook LTR write hardening in Phase 10A",
        "Operators can start from a `.msg` file without creating a project first",
        "Operators can start from manual intake when no email exists",
    ]:
        assert term in plan


def test_phase10a_task_files_exist_and_preserve_scope() -> None:
    """Phase 10A tasks exist and keep future scope blocked."""
    expected_tasks = [
        "TASK_060_PHASE10A_SCOPE_AND_BOARD_ACTIVATION.md",
        "TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY.md",
        "TASK_062_INTAKE_PACKAGE_DETAIL_REAL_DATA_WIRING.md",
        "TASK_063_DIRECT_MANUAL_INTAKE_ENTRY.md",
        "TASK_064_UNIFIED_INTAKE_CASE_REVIEW_AND_CONFIRMATION_UI.md",
        "TASK_065_INTAKE_ENTRY_BROWSER_SMOKE_AND_DOCS_SYNC.md",
    ]

    for filename in expected_tasks:
        task = ROOT / "tasks" / filename
        assert task.is_file()
        source = task.read_text(encoding="utf-8")
        for forbidden in [
            "Outlook inbox auto-scan",
            "email sending",
            "Matrix",
            "Report",
            "AI review",
            "external LTR workbook mutation",
        ]:
            assert forbidden in source

    done_task = (
        ROOT / "tasks" / "TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY.md"
    ).read_text(encoding="utf-8")
    completed_task = (
        ROOT / "tasks" / "TASK_062_INTAKE_PACKAGE_DETAIL_REAL_DATA_WIRING.md"
    ).read_text(encoding="utf-8")
    manual_task = (
        ROOT / "tasks" / "TASK_063_DIRECT_MANUAL_INTAKE_ENTRY.md"
    ).read_text(encoding="utf-8")
    review_task = (
        ROOT / "tasks" / "TASK_064_UNIFIED_INTAKE_CASE_REVIEW_AND_CONFIRMATION_UI.md"
    ).read_text(encoding="utf-8")
    closeout_task = (
        ROOT / "tasks" / "TASK_065_INTAKE_ENTRY_BROWSER_SMOKE_AND_DOCS_SYNC.md"
    ).read_text(encoding="utf-8")
    assert "## Status\n\ndone" in done_task
    assert "manual `.msg` email package import entry point" in done_task
    assert "## Status\n\ndone" in completed_task
    assert "real backend package, asset, and candidate state" in completed_task
    assert "## Status\n\ndone" in manual_task
    assert "no-email exception path" in manual_task
    assert "## Status\n\ndone" in review_task
    assert "## Status\n\ndone" in closeout_task


def test_phase10a_validation_summary_closes_scope_without_future_work() -> None:
    """TASK_065 records validation and manual smoke guidance for Phase 10A."""
    summary = (ROOT / "docs" / "phase10a_validation_summary.md").read_text(
        encoding="utf-8"
    )
    checklist = (ROOT / "docs" / "frontend_smoke_checklist.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "Status: Phase 10A complete",
        "Manual Browser Smoke Checklist",
        "manual `.msg` package import",
        "direct manual intake",
        "unified email-import and manual-intake case review",
        "explicit operator confirmation",
        "Do not activate the candidate automatically",
    ]:
        assert term in summary

    for term in [
        "Phase 10A Intake Entry Completion",
        ".msg` import control",
        "no-email manual intake",
        "same review page",
        "operator confirmation checkbox",
        "copied-workbook LTR write hardening",
    ]:
        assert term in checklist
