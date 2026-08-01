from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from tests.unit.test_connlab_execution_transition import HELPER, fixture, run


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
