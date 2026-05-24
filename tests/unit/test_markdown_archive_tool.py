from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "archive_completed_markdown.py"


spec = importlib.util.spec_from_file_location("archive_completed_markdown", SCRIPT_PATH)
archive_tool = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = archive_tool
spec.loader.exec_module(archive_tool)


def write_sample_repo(root: Path, *, board_status: str) -> None:
    (root / "docs").mkdir()
    (root / "tasks").mkdir()
    (root / "docs" / "task_board.md").write_text(board_status, encoding="utf-8")
    (root / "tasks" / "TASK_267_SAMPLE.md").write_text(
        "# TASK_267_SAMPLE\n\nStatus: complete\n",
        encoding="utf-8",
    )
    (root / "docs" / "task_267_sample_plan.md").write_text(
        "# TASK_267 Sample Plan\n\nStatus: complete\n",
        encoding="utf-8",
    )
    (root / "tasks" / "TASK_267A_FOLLOWUP.md").write_text(
        "# TASK_267A_FOLLOWUP\n\nStatus: complete\n",
        encoding="utf-8",
    )
    (root / "docs" / "task_267a_followup_plan.md").write_text(
        "# TASK_267A Followup Plan\n\nStatus: complete\n",
        encoding="utf-8",
    )


def test_archive_plan_dry_run_does_not_move_files(tmp_path: Path) -> None:
    write_sample_repo(
        tmp_path,
        board_status=(
            "> Status: TASK_267 complete\n"
            "> Current Active Task: none (`TASK_267_SAMPLE` complete; awaiting next approved task).\n"
        ),
    )

    plan = archive_tool.build_archive_plan(tmp_path, "TASK_267", year="2026")
    output = archive_tool.render_plan(plan, dry_run=True)

    assert "DRY RUN: archive TASK_267" in output
    assert "MOVE tasks/TASK_267_SAMPLE.md -> tasks/completed/2026/TASK_267_SAMPLE.md" in output
    assert "MOVE docs/task_267_sample_plan.md -> docs/completed_plans/2026/task_267_sample_plan.md" in output
    assert "TASK_267A_FOLLOWUP" not in output
    assert "task_267a_followup_plan" not in output
    assert (tmp_path / "tasks" / "TASK_267_SAMPLE.md").exists()
    assert (tmp_path / "docs" / "task_267_sample_plan.md").exists()


def test_archive_apply_moves_files_and_updates_indexes(tmp_path: Path) -> None:
    write_sample_repo(
        tmp_path,
        board_status=(
            "> Status: TASK_267 complete\n"
            "> Current Active Task: none (`TASK_267_SAMPLE` complete; awaiting next approved task).\n"
        ),
    )

    plan = archive_tool.build_archive_plan(tmp_path, "TASK_267", year="2026")
    archive_tool.apply_archive_plan(plan)

    assert not (tmp_path / "tasks" / "TASK_267_SAMPLE.md").exists()
    assert not (tmp_path / "docs" / "task_267_sample_plan.md").exists()
    assert (tmp_path / "tasks" / "completed" / "2026" / "TASK_267_SAMPLE.md").exists()
    assert (tmp_path / "docs" / "completed_plans" / "2026" / "task_267_sample_plan.md").exists()

    task_index = (tmp_path / "docs" / "task_archive_index.md").read_text(encoding="utf-8")
    plan_index = (tmp_path / "docs" / "plan_archive_index.md").read_text(encoding="utf-8")
    assert "| TASK_267 | TASK_267_SAMPLE | complete |" in task_index
    assert "docs/completed_plans/2026/task_267_sample_plan.md" in plan_index


def test_archive_refuses_incomplete_active_task(tmp_path: Path) -> None:
    write_sample_repo(
        tmp_path,
        board_status=(
            "> Status: TASK_267 planned\n"
            "> Current Active Task: TASK_267_SAMPLE planned; awaiting approval.\n"
        ),
    )

    with pytest.raises(archive_tool.ArchiveError, match="current active task"):
        archive_tool.build_archive_plan(tmp_path, "TASK_267", year="2026")


def test_all_completed_discovers_only_board_completed_root_files(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "tasks").mkdir()
    (tmp_path / "docs" / "task_board.md").write_text(
        (
            "> Status: TASK_267 complete\n"
            "> Current Active Task: none.\n"
            "| T | `TASK_268_FUTURE` | planned | not started |\n"
        ),
        encoding="utf-8",
    )
    (tmp_path / "tasks" / "TASK_267_SAMPLE.md").write_text("# TASK_267_SAMPLE\n", encoding="utf-8")
    (tmp_path / "docs" / "task_267_sample_plan.md").write_text("# TASK_267 plan\n", encoding="utf-8")
    (tmp_path / "tasks" / "TASK_268_FUTURE.md").write_text("# TASK_268_FUTURE\n", encoding="utf-8")
    (tmp_path / "docs" / "task_268_future_plan.md").write_text("# TASK_268 plan\n", encoding="utf-8")

    plans = archive_tool.build_all_completed_archive_plans(tmp_path, year="2026")
    output = archive_tool.render_plans(plans, dry_run=True)

    assert [plan.task_id for plan in plans] == ["TASK_267"]
    assert "TASK_267_SAMPLE" in output
    assert "TASK_268_FUTURE" not in output


def test_completed_board_status_accepts_task_id_followed_by_underscore() -> None:
    board_text = "- `TASK_001_REPOSITORY_SCAFFOLD` is complete.\n"

    assert archive_tool.task_has_completed_board_status(board_text, "TASK_001")


def test_archive_plan_accepts_completed_task_file_status_when_board_is_sparse(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "tasks").mkdir()
    (tmp_path / "docs" / "task_board.md").write_text(
        "> Current Active Task: none.\n",
        encoding="utf-8",
    )
    (tmp_path / "tasks" / "TASK_143_SAMPLE.md").write_text(
        "# TASK_143_SAMPLE\n\n## Status\n\ndone\n",
        encoding="utf-8",
    )

    plan = archive_tool.build_archive_plan(tmp_path, "TASK_143", year="2026")

    assert plan.task_id == "TASK_143"


def test_archive_plan_rejects_proposed_task_file_status(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "tasks").mkdir()
    (tmp_path / "docs" / "task_board.md").write_text(
        "> Current Active Task: none.\n",
        encoding="utf-8",
    )
    (tmp_path / "tasks" / "TASK_150_SAMPLE.md").write_text(
        "# TASK_150_SAMPLE\n\n> Status: proposed\n",
        encoding="utf-8",
    )

    with pytest.raises(archive_tool.ArchiveError, match="not marked complete"):
        archive_tool.build_archive_plan(tmp_path, "TASK_150", year="2026")
