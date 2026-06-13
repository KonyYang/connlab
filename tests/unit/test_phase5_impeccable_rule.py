from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_phase5_plan_and_board_require_impeccable() -> None:
    """Phase 5 docs require impeccable for UX/UI work."""
    plan = (
        ROOT
        / "docs"
        / "archive"
        / "historical_plans"
        / "ConnLab_Phase5_Workbench_UX_Plan.md"
    ).read_text(
        encoding="utf-8"
    )
    board = (ROOT / "docs" / "task_board.md").read_text(encoding="utf-8")

    for source in (plan, board):
        assert "$impeccable" in source
        assert "PRODUCT.md" in source
        assert "DESIGN.md" in source
        assert "DESIGN.json" in source
        assert "register: product" in source


def test_phase5_task_files_require_impeccable_for_ui_work() -> None:
    """Every remaining Phase 5 UX task carries the impeccable precondition."""
    task_names = [
        "TASK_017_APP_SHELL_LEFT_NAV.md",
        "TASK_018_PROJECT_DASHBOARD.md",
        "TASK_019_PROJECT_WORKBENCH_STEPPER.md",
        "TASK_020_PRECHECK_ISSUE_EXPERIENCE.md",
        "TASK_021_INTAKE_LTR_FOLDER_UX.md",
        "TASK_022_FRONTEND_STATE_AND_API_CLEANUP.md",
        "TASK_023_FRONTEND_TEST_AND_BUILD_GUARD.md",
        "TASK_024_PHASE5_DOCS_AND_BOARD_SYNC.md",
    ]

    for task_name in task_names:
        task_path = ROOT / "tasks" / task_name
        if not task_path.exists():
            task_path = ROOT / "tasks" / "completed" / "2026" / task_name
        source = task_path.read_text(encoding="utf-8")
        assert "$impeccable" in source
        assert "PRODUCT.md" in source
        assert "DESIGN.md" in source
