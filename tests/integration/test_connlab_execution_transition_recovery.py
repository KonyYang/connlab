from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from tests.unit.test_connlab_execution_transition import HELPER, commit_applied_transition, fixture, run


def test_stale_snapshot_and_dirty_primary_are_zero_write(tmp_path: Path) -> None:
    fx = fixture(tmp_path)
    board = Path(fx["repo"]) / "docs" / "task_board.md"
    before = board.read_bytes()
    (Path(fx["repo"]) / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    code, dirty = run(fx, "plan")
    assert code != 0 and "BLOCKED_PRIMARY_DIRTY" in dirty["reason_codes"]
    assert board.read_bytes() == before


def test_injected_pre_replace_failure_preserves_board(tmp_path: Path) -> None:
    fx = fixture(tmp_path)
    board = Path(fx["repo"]) / "docs" / "task_board.md"
    before = board.read_bytes()
    planned = run(fx, "plan")[1]
    args = [
        "py", str(HELPER), "apply", "--repo-root", str(fx["repo"]),
        "--event", "DEVELOPER_READY", "--task-id", "TASK_X", "--lane", "task-x",
        "--expected-primary-head", str(fx["primary_head"]),
        "--expected-lane-head", str(fx["lane_head"]), "--evidence-ref", str(fx["ref"]),
        "--evidence-status", "ready_for_review", "--expected-snapshot-digest",
        str(planned["before_digest"]), "--json",
    ]
    env = os.environ.copy()
    env["CONNLAB_TRANSITION_FAIL_BEFORE_REPLACE"] = "1"

    completed = subprocess.run(args, env=env, check=False, capture_output=True, text=True)
    result = json.loads(completed.stdout)

    assert completed.returncode != 0
    assert "BLOCKED_WRITE_FAILED" in result["reason_codes"]
    assert board.read_bytes() == before


def test_missing_evidence_blob_fails_closed(tmp_path: Path) -> None:
    fx = fixture(tmp_path)
    fx["ref"] = f"docs/lane_evidence/missing.md@{fx['lane_head']}#{'0' * 64}"

    code, result = run(fx, "plan")

    assert code != 0
    assert "BLOCKED_EVIDENCE_MISSING" in result["reason_codes"]


def test_duplicate_rejects_later_primary_commit_and_dirty_lane(tmp_path: Path) -> None:
    later = fixture(tmp_path / "later")
    assert run(later, "apply")[0] == 0
    commit_applied_transition(later)
    repo = Path(later["repo"])
    (repo / "later.txt").write_text("later primary fact\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "later.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "later primary commit"], check=True, capture_output=True)
    before = (repo / "docs/task_board.md").read_bytes()
    code, result = run(later, "apply")
    assert code != 0 and "BLOCKED_PRIMARY_HEAD_DRIFT" in result["reason_codes"]
    assert (repo / "docs/task_board.md").read_bytes() == before

    dirty = fixture(tmp_path / "dirty-lane")
    assert run(dirty, "apply")[0] == 0
    commit_applied_transition(dirty)
    lane = Path(dirty["lane"])
    (lane / "dirty.txt").write_text("dirty lane fact\n", encoding="utf-8")
    before = (Path(dirty["repo"]) / "docs/task_board.md").read_bytes()
    code, result = run(dirty, "apply")
    assert code != 0 and "BLOCKED_LANE_DIRTY" in result["reason_codes"]
    assert (Path(dirty["repo"]) / "docs/task_board.md").read_bytes() == before
