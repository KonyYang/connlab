from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from scripts.connlab_serial_board import parse_board, render_board


ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = {key: False for key in (
    "api_contract", "database", "schema_or_migration", "persistence", "authority",
    "public_drive_workflow", "business_rule_semantics", "destructive_action", "external_mutation",
)}


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], text=True, encoding="utf-8",
        capture_output=True, check=True,
    ).stdout.strip()


def git_bytes(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=True,
    ).stdout


def invoke(repo: Path, command: str, *args: str, expected_exit: int = 0) -> dict:
    completed = subprocess.run(
        ["py", "-m", "scripts.connlab_personal_task", command, "--repo-root", str(repo), *args, "--json"],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
    )
    assert completed.returncode == expected_exit, completed.stderr or completed.stdout
    return json.loads(completed.stdout)


def board_hash(repo: Path) -> str:
    return hashlib.sha256((repo / "docs/task_board.md").read_bytes()).hexdigest()


def approved_request() -> dict:
    return {
        "schema": "connlab.personal-task-approved-request",
        "version": 1,
        "task_id": "TASK_PLAN_PREFLIGHT",
        "summary": "Verify the committed Plan before approval",
        "kind": "planned",
        "may_touch": ["docs/task_board.md"],
        "expected_file_count": 1,
        "classification_reason": "governance contract",
        "targeted_validation": ["py -m pytest"],
        "forbidden_categories": FORBIDDEN,
    }


def init_awaiting_repo(repo: Path, route_sentence: str) -> tuple[dict, str]:
    repo.mkdir()
    git(repo, "init", "-b", "master")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Approval Preflight Test")
    (repo / ".gitignore").write_text("tmp/\n", encoding="utf-8")
    (repo / "docs").mkdir()
    prefix, board, suffix = parse_board((ROOT / "docs/task_board.md").read_bytes())
    approved = approved_request()
    active = {
        "task_id": approved["task_id"],
        "summary": approved["summary"],
        "kind": "planned",
        "classification": "needs_discovery",
        "phase": "awaiting_user_approval",
        "scope_contract": None,
        "plan_ref": None,
        "approval_ref": None,
        "activation_parent_sha": "0" * 40,
        "activated_at": "2026-08-16T00:00:00Z",
        "updated_at": "2026-08-16T00:00:00Z",
        "blocker": None,
        "validation": None,
        "complex_context": {
            "workflow_version": 1,
            "task_branch": None,
            "task_worktree": None,
            "base_sha": "0" * 40,
            "head_sha": "0" * 40,
            "integration_target": "master",
            "worktree_lifecycle": "absent",
            "current_role": None,
            "current_attempt": 1,
            "role_invocations": [],
            "host_thread_id": None,
            "host_id": None,
            "approved_code_paths": [],
            "required_gates": ["Reviewer", "QA", "Integrator"],
            "developer_subject_commit": None,
            "reviewer_subject_commit": None,
            "qa_subject_commit": None,
            "integrated_commit": None,
            "evidence_refs": [],
            "blocker_history": [],
            "pending_callback": None,
            "closeout_disposition": None,
            "retained_resource_refs": [],
            "close_decision_ref": None,
        },
    }
    board.update(state="running", active=active, queue=[], next_enqueue_sequence=1)
    (repo / "docs/task_board.md").write_bytes(render_board(prefix, board, suffix))
    compact = json.dumps(approved, ensure_ascii=False, separators=(",", ":"))
    (repo / "docs/plan.md").write_text(
        f"# Plan\n\n{route_sentence}\n\n```json\n{compact}\n```\n",
        encoding="utf-8",
    )
    git(repo, "add", ".gitignore", "docs/task_board.md", "docs/plan.md")
    git(repo, "commit", "-m", "await approval")
    plan = git_bytes(repo, "show", "HEAD:docs/plan.md")
    plan_ref = f"docs/plan.md@{git(repo, 'rev-parse', 'HEAD')}#{hashlib.sha256(plan).hexdigest()}"
    return approved, plan_ref


def approve(repo: Path, approved: dict, plan_ref: str, *, expected_exit: int = 0) -> dict:
    return invoke(
        repo,
        "approve",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        approved["task_id"],
        "--approved-request-json",
        json.dumps(approved, ensure_ascii=False, separators=(",", ":")),
        "--plan-ref",
        plan_ref,
        "--approval-ref",
        "user:approved exact plan",
        expected_exit=expected_exit,
    )


def test_approve_rejects_unparseable_execution_route_before_board_write(tmp_path: Path) -> None:
    repo = tmp_path / "invalid-route"
    approved, plan_ref = init_awaiting_repo(
        repo,
        "Developer, Reviewer, QA and Integrator are each using `gpt-5.6-sol / medium / risk:authority`.",
    )
    before = (repo / "docs/task_board.md").read_bytes()

    result = approve(repo, approved, plan_ref, expected_exit=2)

    assert result["code"] == "BLOCKED_PLAN_INVALID"
    assert result["changed"] is False
    assert (repo / "docs/task_board.md").read_bytes() == before


def test_approve_accepts_a_fully_preflighted_committed_plan(tmp_path: Path) -> None:
    repo = tmp_path / "valid-route"
    approved, plan_ref = init_awaiting_repo(
        repo,
        "Developer, Reviewer, QA and Integrator are all `gpt-5.6-sol / medium / risk:authority`.",
    )

    result = approve(repo, approved, plan_ref)

    assert result["code"] == "ALLOW_APPROVE"
    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    assert board["active"]["plan_ref"] == plan_ref
    assert board["active"]["phase"] == "development"


def test_inspect_exposes_the_exact_next_command_contract(tmp_path: Path) -> None:
    repo = tmp_path / "contract"
    init_awaiting_repo(
        repo,
        "Developer, Reviewer, QA and Integrator are all `gpt-5.6-sol / medium / risk:authority`.",
    )

    result = invoke(repo, "inspect")

    assert result["next_action"]["command"] == "approve"
    assert result["next_action"]["command_contract"] == {
        "accepted_arguments": [
            "approval_ref",
            "approved_request_json",
            "expected_board_sha256",
            "plan_ref",
            "task_id",
        ],
        "json_schemas": {
            "approved_request_json": "connlab.personal-task-approved-request/v1",
        },
    }


def test_payload_cli_reports_the_same_approve_contract() -> None:
    completed = subprocess.run(
        ["py", "-m", "scripts.connlab_serial_payload", "contract", "--command", "approve"],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert json.loads(completed.stdout) == {
        "accepted_arguments": [
            "approval_ref",
            "approved_request_json",
            "expected_board_sha256",
            "plan_ref",
            "task_id",
        ],
        "json_schemas": {
            "approved_request_json": "connlab.personal-task-approved-request/v1",
        },
    }
