from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "connlab_personal_task.py"
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"
FORBIDDEN = {
    "api_contract": False,
    "database": False,
    "schema_or_migration": False,
    "persistence": False,
    "authority": False,
    "public_drive_workflow": False,
    "business_rule_semantics": False,
    "destructive_action": False,
    "external_mutation": False,
}


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], text=True, capture_output=True, check=True
    )
    return result.stdout.strip()


def board_bytes(repo: Path) -> bytes:
    return (repo / "docs" / "task_board.md").read_bytes()


def board_hash(repo: Path) -> str:
    return hashlib.sha256(board_bytes(repo)).hexdigest()


def control(repo: Path) -> dict:
    text = board_bytes(repo).decode("utf-8")
    payload = text.split(f"{BEGIN}\n```json\n", 1)[1].split(f"\n```\n{END}", 1)[0]
    return json.loads(payload)


def invoke(repo: Path, command: str, *args: str, expected_exit: int = 0) -> dict:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), command, "--repo-root", str(repo), "--json", *args],
        text=True,
        capture_output=True,
    )
    assert completed.returncode == expected_exit, completed.stderr or completed.stdout
    result = json.loads(completed.stdout)
    assert list(result) == [
        "schema",
        "version",
        "code",
        "allowed",
        "changed",
        "command",
        "task_id",
        "state",
        "active_task_id",
        "queue_position",
        "board_sha256_before",
        "board_sha256_after",
        "primary_root",
        "reason",
    ]
    return result


def request(task_id: str, *, kind: str = "simple") -> str:
    base = {
        "schema": "connlab.personal-task-request",
        "version": 1,
        "task_id": task_id,
        "summary": f"Summary for {task_id}",
        "kind": kind,
    }
    if kind == "simple":
        base.update(
            may_touch=["docs/task_board.md", "impl.py"],
            expected_file_count=2,
            classification_reason="The root cause and expected result are known.",
            targeted_validation=["pytest targeted"],
            forbidden_categories=FORBIDDEN,
            plan_ref=None,
        )
    return json.dumps(base)


def validation(*paths: str, status: str = "passed", exit_code: int = 0) -> str:
    return json.dumps(
        {
            "schema": "connlab.personal-task-validation",
            "version": 1,
            "status": status,
            "checks": [
                {"command": "pytest targeted", "exit_code": exit_code, "summary": status}
            ],
            "observed_paths": list(paths),
            "manual_checks": [],
            "recorded_at": "2026-08-06T02:00:00+08:00",
        }
    )


def write_board(repo: Path) -> None:
    value = {
        "schema": "connlab.personal-serial-control",
        "version": 1,
        "mode": "personal_serial",
        "wip_limit": 1,
        "state": "idle",
        "active": None,
        "queue": [],
        "next_enqueue_sequence": 1,
        "last_closed": None,
        "retained_history": [],
    }
    board = repo / "docs" / "task_board.md"
    board.parent.mkdir()
    board.write_text(
        "# Board\n\n" + BEGIN + "\n```json\n" + json.dumps(value, indent=2) + "\n```\n" + END + "\n",
        encoding="utf-8",
        newline="\n",
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    write_board(tmp_path)
    (tmp_path / ".gitignore").write_text("tmp/\n", encoding="utf-8")
    git(tmp_path, "init", "-b", "master")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test User")
    git(tmp_path, "add", "docs/task_board.md", ".gitignore")
    git(tmp_path, "commit", "-m", "baseline")
    return tmp_path


def commit_board(repo: Path, message: str) -> None:
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", message)


def test_inspect_reports_authoritative_idle_snapshot(repo: Path) -> None:
    result = invoke(repo, "inspect")

    assert result["code"] == "ALLOW_INSPECT"
    assert result["allowed"] is True
    assert result["changed"] is False
    assert result["state"] == "idle"
    assert result["board_sha256_before"] == board_hash(repo)
    assert result["board_sha256_after"] == board_hash(repo)


def test_submit_activates_one_simple_task_and_queues_the_next(repo: Path) -> None:
    first = invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_ONE",
        "--request-json",
        request("TASK_ONE"),
    )
    second = invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_TWO",
        "--request-json",
        request("TASK_TWO", kind="planned"),
    )
    duplicate = invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_TWO",
        "--request-json",
        request("TASK_TWO", kind="planned"),
    )

    assert first["code"] == "ALLOW_ACTIVATE"
    assert second["code"] == "QUEUED_NEW" and second["queue_position"] == 1
    assert duplicate["code"] == "QUEUED_EXISTING" and duplicate["changed"] is False
    value = control(repo)
    assert value["active"]["task_id"] == "TASK_ONE"
    assert value["active"]["phase"] == "implementation"
    assert [item["task_id"] for item in value["queue"]] == ["TASK_TWO"]


def test_writer_rejects_stale_board_hash_without_changing_bytes(repo: Path) -> None:
    before = board_bytes(repo)

    result = invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        "0" * 64,
        "--task-id",
        "TASK_ONE",
        "--request-json",
        request("TASK_ONE"),
        expected_exit=2,
    )

    assert result["code"] == "BLOCKED_BOARD_HASH_MISMATCH"
    assert board_bytes(repo) == before


def test_simple_request_rejects_any_forbidden_category(repo: Path) -> None:
    payload = json.loads(request("TASK_ONE"))
    payload["forbidden_categories"]["persistence"] = True

    result = invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_ONE",
        "--request-json",
        json.dumps(payload),
        expected_exit=2,
    )

    assert result["code"] == "BLOCKED_CLASSIFICATION_INVALID"
    assert control(repo)["active"] is None


def test_planned_task_requires_approved_scope_before_implementation(repo: Path) -> None:
    invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_PLAN",
        "--request-json",
        request("TASK_PLAN", kind="planned"),
    )
    commit_board(repo, "activate planning")
    denied = invoke(
        repo,
        "check",
        "--intent",
        "Implementation",
        "--task-id",
        "TASK_PLAN",
        expected_exit=2,
    )
    approved = {
        "schema": "connlab.personal-task-approved-request",
        "version": 1,
        "task_id": "TASK_PLAN",
        "summary": "Approved bounded summary",
        "kind": "planned",
        "may_touch": ["docs/task_board.md", "impl.py", "test_impl.py"],
        "expected_file_count": 3,
        "classification_reason": "Approved governance scope.",
        "targeted_validation": ["pytest targeted"],
        "forbidden_categories": {**FORBIDDEN, "persistence": True},
    }
    result = invoke(
        repo,
        "approve",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_PLAN",
        "--approved-request-json",
        json.dumps(approved),
        "--plan-ref",
        "docs/plan.md@" + "a" * 40 + "#" + "b" * 64,
        "--approval-ref",
        "User approved this plan.",
    )

    assert denied["code"] == "BLOCKED_APPROVAL_REQUIRED"
    assert result["code"] == "ALLOW_APPROVE"
    assert control(repo)["active"]["scope_contract"]["forbidden_categories"]["persistence"] is True


def test_scope_expansion_reapproval_preserves_blocker_until_explicit_resume(repo: Path) -> None:
    invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_PLAN",
        "--request-json",
        request("TASK_PLAN", kind="planned"),
    )
    commit_board(repo, "activate planning")
    approved = {
        "schema": "connlab.personal-task-approved-request",
        "version": 1,
        "task_id": "TASK_PLAN",
        "summary": "Approved bounded summary",
        "kind": "planned",
        "may_touch": ["docs/task_board.md", "impl.py", "test_impl.py"],
        "expected_file_count": 3,
        "classification_reason": "Approved governance scope.",
        "targeted_validation": ["pytest targeted"],
        "forbidden_categories": {**FORBIDDEN, "persistence": True},
    }
    invoke(
        repo,
        "approve",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_PLAN",
        "--approved-request-json",
        json.dumps(approved),
        "--plan-ref",
        "docs/plan.md@" + "a" * 40 + "#" + "b" * 64,
        "--approval-ref",
        "User approved the original plan.",
    )
    commit_board(repo, "approve original scope")
    blocker = {
        "schema": "connlab.personal-task-blocker",
        "version": 1,
        "code": "SCOPE_EXPANDED",
        "reason": "One compatibility path must be added.",
        "dirty_paths": ["scripts/compat.py"],
        "failed_validation": None,
        "recorded_at": "2026-08-06T02:10:00+08:00",
    }
    invoke(
        repo,
        "block",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_PLAN",
        "--blocker-json",
        json.dumps(blocker),
    )
    commit_board(repo, "record scope blocker")
    expanded = {
        **approved,
        "may_touch": [*approved["may_touch"], "scripts/compat.py"],
        "expected_file_count": 4,
        "classification_reason": "User approved one read-only compatibility path.",
    }

    result = invoke(
        repo,
        "approve",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_PLAN",
        "--approved-request-json",
        json.dumps(expanded),
        "--plan-ref",
        "docs/plan.md@" + "c" * 40 + "#" + "d" * 64,
        "--approval-ref",
        "User approved the exact scope expansion.",
    )

    active = control(repo)["active"]
    assert result["code"] == "ALLOW_SCOPE_AMEND"
    assert active["scope_contract"]["may_touch"] == expanded["may_touch"]
    assert active["phase"] == "blocked"
    assert active["blocker"] == blocker


def test_block_and_resume_preserve_the_active_slot(repo: Path) -> None:
    invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_ONE",
        "--request-json",
        request("TASK_ONE"),
    )
    blocker = {
        "schema": "connlab.personal-task-blocker",
        "version": 1,
        "code": "IMPLEMENTATION_FAILED",
        "reason": "A bounded implementation step failed.",
        "dirty_paths": ["impl.py"],
        "failed_validation": None,
        "recorded_at": "2026-08-06T02:10:00+08:00",
    }
    blocked = invoke(
        repo,
        "block",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_ONE",
        "--blocker-json",
        json.dumps(blocker),
    )
    resumed = invoke(
        repo,
        "resume",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_ONE",
        "--decision-ref",
        "User directed continuation.",
    )

    assert blocked["code"] == "ALLOW_BLOCK"
    assert resumed["code"] == "ALLOW_RESUME"
    assert control(repo)["state"] == "running"
    assert control(repo)["active"]["phase"] == "implementation"
    assert control(repo)["active"]["blocker"] is None


def test_review_close_and_fifo_activation_require_committed_transitions(repo: Path) -> None:
    invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_ONE",
        "--request-json",
        request("TASK_ONE"),
    )
    commit_board(repo, "activate one")
    invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_TWO",
        "--request-json",
        request("TASK_TWO", kind="planned"),
    )
    (repo / "impl.py").write_text("VALUE = 1\n", encoding="utf-8")
    review = invoke(
        repo,
        "mark-review",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_ONE",
        "--validation-json",
        validation("docs/task_board.md", "impl.py"),
    )
    dirty_close = invoke(
        repo,
        "close",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_ONE",
        "--decision-ref",
        "User said close.",
        expected_exit=2,
    )
    git(repo, "add", "docs/task_board.md", "impl.py")
    git(repo, "commit", "-m", "implement one")
    closed = invoke(
        repo,
        "close",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_ONE",
        "--decision-ref",
        "User said close.",
    )
    commit_board(repo, "close one")
    wrong_head = invoke(
        repo,
        "activate-next",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_THREE",
        expected_exit=2,
    )
    next_task = invoke(
        repo,
        "activate-next",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_TWO",
    )

    assert review["code"] == "ALLOW_MARK_REVIEW"
    assert dirty_close["code"] == "BLOCKED_WORKTREE_DIRTY"
    assert closed["code"] == "ALLOW_CLOSE"
    assert wrong_head["code"] == "BLOCKED_FIFO_ORDER"
    assert next_task["code"] == "ALLOW_ACTIVATE_NEXT"
    assert control(repo)["active"]["phase"] == "planning"


def test_lock_collision_fails_closed_without_board_write(repo: Path) -> None:
    lock = repo / "tmp" / "connlab_personal_task.lock"
    lock.parent.mkdir()
    lock.write_text("held", encoding="utf-8")
    before = board_bytes(repo)

    result = invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_ONE",
        "--request-json",
        request("TASK_ONE"),
        expected_exit=2,
    )

    assert result["code"] == "BLOCKED_LOCKED"
    assert board_bytes(repo) == before
