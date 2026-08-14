from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from scripts.connlab_serial_complex import (
    SerialContractError,
    validate_invocation,
    validate_native_action,
)
from scripts.connlab_serial_board import Blocked
from scripts import connlab_personal_task


ZERO64 = "0" * 64
ROOT = Path(__file__).resolve().parents[2]


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def test_native_action_and_invocation_use_exact_schemas() -> None:
    action = {
        "schema": "connlab.serial-native-action",
        "version": 1,
        "action_id": ZERO64,
        "action": "reviewer_dispatch",
        "role": "Reviewer",
        "attempt": 1,
        "prompt_sha256": ZERO64,
        "title": "ConnLab Reviewer",
        "recorded_at": "2026-08-06T00:00:00Z",
    }
    assert validate_native_action(action) == action
    invocation = {
        "schema": "connlab.serial-invocation",
        "version": 1,
        "action_id": ZERO64,
        "role": "Reviewer",
        "attempt": 1,
        "thread_id": None,
        "agent_id": "agent-1",
        "host_id": "host-1",
        "status": "started",
        "recorded_at": "2026-08-06T00:00:01Z",
    }
    assert validate_invocation(invocation) == invocation
    invocation["thread_id"] = "thread-1"
    with pytest.raises(SerialContractError, match="BLOCKED_ARGUMENT_COMBINATION"):
        validate_invocation(invocation)


def test_retained_repository_verifier_proves_identity_cleanliness_ancestry_and_evidence(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    worktree = tmp_path / "task-worktree"
    primary.mkdir()
    git(primary, "init", "-b", "master")
    git(primary, "config", "user.email", "test@example.invalid")
    git(primary, "config", "user.name", "Test")
    (primary / "README.md").write_text("base\n", encoding="utf-8")
    git(primary, "add", "README.md")
    git(primary, "commit", "-m", "base")
    git(primary, "worktree", "add", "-b", "codex/task-example", str(worktree), "HEAD")
    (worktree / "subject.txt").write_text("subject\n", encoding="utf-8")
    git(worktree, "add", "subject.txt")
    git(worktree, "commit", "-m", "subject")
    branch_head = git(worktree, "rev-parse", "HEAD")
    git(primary, "merge", "--no-ff", "--no-edit", "codex/task-example")
    integrated_commit = git(primary, "rev-parse", "HEAD")
    evidence_path = primary / "docs" / "lane_evidence" / "closeout.md"
    evidence_path.parent.mkdir(parents=True)
    evidence_bytes = b"retained closeout proof\n"
    evidence_path.write_bytes(evidence_bytes)
    git(primary, "add", "docs/lane_evidence/closeout.md")
    git(primary, "commit", "-m", "evidence")
    evidence_commit = git(primary, "rev-parse", "HEAD")
    evidence_ref = (
        f"docs/lane_evidence/closeout.md@{evidence_commit}#"
        f"{hashlib.sha256(evidence_bytes).hexdigest()}"
    )
    active = {
        "task_id": "TASK_EXAMPLE",
        "complex_context": {
            "host_thread_id": "thread-1",
            "task_worktree": str(worktree.resolve()),
            "task_branch": "codex/task-example",
            "head_sha": branch_head,
            "integrated_commit": integrated_commit,
            "worktree_lifecycle": "integrated",
            "current_role": None,
            "pending_callback": None,
        },
    }
    closeout = {
        "schema": "connlab.serial-closeout",
        "version": 1,
        "action_id": ZERO64,
        "disposition": "retained",
        "task_id": "TASK_EXAMPLE",
        "thread_id": "thread-1",
        "worktree": str(worktree.resolve()),
        "branch": "codex/task-example",
        "head_sha": branch_head,
        "clean": True,
        "integrated_commit": integrated_commit,
        "evidence_ref": evidence_ref,
        "reason": "retained_nonblocking_manual_maintenance",
        "recorded_at": "2026-08-06T00:00:00Z",
    }

    assert connlab_personal_task.verify_retained_repository(primary, active, closeout) == closeout
    (worktree / "dirty.txt").write_text("dirty", encoding="utf-8")
    with pytest.raises(Blocked, match="clean"):
        connlab_personal_task.verify_retained_repository(primary, active, closeout)


def test_public_writer_rejects_role_transition_without_active_v2_task() -> None:
    worktrees = subprocess.run(
        ["git", "-C", str(ROOT), "worktree", "list", "--porcelain"],
        text=True, encoding="utf-8", capture_output=True, check=True,
    ).stdout.splitlines()
    primary = Path(worktrees[0].removeprefix("worktree ")).resolve()
    board = primary / "docs/task_board.md"
    before = board.read_bytes()
    board_hash = hashlib.sha256(before).hexdigest()
    action = {
        "schema": "connlab.serial-native-action", "version": 1, "action_id": ZERO64,
        "action": "planner_dispatch", "role": "Planner", "attempt": 1,
        "prompt_sha256": ZERO64, "title": "Planner", "recorded_at": "2026-08-06T00:00:00Z",
    }
    frozen = subprocess.run(
        ["py", str(ROOT / "scripts/connlab_personal_task.py"), "begin-role", "--repo-root", str(primary),
         "--expected-board-sha256", board_hash, "--task-id", "TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION",
         "--role", "Planner", "--native-action-json", json.dumps(action), "--json"],
        text=True, encoding="utf-8", capture_output=True, check=False,
    )
    assert json.loads(frozen.stdout)["code"] == "BLOCKED_TASK_MISMATCH"

    assert board.read_bytes() == before


def test_removed_cutover_command_is_rejected_by_argument_parser_without_board_write() -> None:
    board = ROOT / "docs/task_board.md"
    before = board.read_bytes()

    completed = subprocess.run(
        [
            "py",
            str(ROOT / "scripts/connlab_personal_task.py"),
            "plan-cutover",
            "--repo-root",
            str(ROOT),
            "--json",
        ],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    assert completed.returncode != 0
    assert completed.stdout == ""
    assert "invalid choice" in completed.stderr
    assert board.read_bytes() == before
