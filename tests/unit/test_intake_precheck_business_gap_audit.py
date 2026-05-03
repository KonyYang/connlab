from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_intake_precheck_gap_audit_documents_required_findings() -> None:
    """TASK_077 records the key Intake/Precheck business gaps."""
    source = (ROOT / "docs" / "intake_precheck_business_gap_audit.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "Precheck UI Required Fields Do Not Match Backend Confirmation Rules",
        "Precheck UI Contains Reference/Mock Business Content In Real Data Areas",
        "Several Visible Controls Are Not Wired To Backend Behavior",
        "Direct Word And Manual Intake Entry Are Conceptually Mixed",
        "Lab Test Request Number Blocker Is Display-Only",
        "Parser Extracts More Fields Than Confirmation Persists Meaningfully",
        "Precheck Page Is Not Running The Deterministic Precheck Engine",
        "Information Needed From User",
    ]:
        assert term in source


def test_task077_board_and_task_file_keep_scope_documentation_only() -> None:
    """TASK_077 stays audit-only and blocks future scope."""
    board = (ROOT / "docs" / "task_board.md").read_text(encoding="utf-8")
    task = (
        ROOT / "tasks" / "TASK_077_INTAKE_PRECHECK_BUSINESS_GAP_AUDIT.md"
    ).read_text(encoding="utf-8")

    assert "`TASK_077_INTAKE_PRECHECK_BUSINESS_GAP_AUDIT` is complete" in board
    assert "No frontend code refactor" in task
    assert "No backend behavior changes" in task
    assert "No copied-workbook LTR write hardening" in task

