from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.connlab_serial_board import Blocked, migrate_v1_to_v2, parse_board, render_board


ROOT = Path(__file__).resolve().parents[2]
CUTOVER_PARENT = "9e68eec0c547b0c028c417004fcdd7a83da9ba64"
CUTOVER_PATHS = (
    "AGENTS.md",
    ".agents/skills/connlab-lane-orchestrator/SKILL.md",
    "docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md",
    "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
    "scripts/run_task.ps1",
    "scripts/connlab_execution_gate.ps1",
    "scripts/connlab_personal_task.py",
    "scripts/connlab_serial_board.py",
    "scripts/connlab_serial_complex.py",
    "docs/task_board.md",
    "tasks/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION.md",
    "docs/task_governance_serial_complex_role_chain_automation_plan.md",
    "tests/unit/test_connlab_serial_complex_orchestrator_contract.py",
    "tests/unit/test_connlab_execution_gate_script.py",
    "tests/unit/test_task_scoped_role_thread_lifecycle_governance.py",
    "tests/integration/test_connlab_serial_complex_recovery.py",
)
CUTOVER_DECISION = (
    "User approved the exact pre-reviewed local atomic cutover commit in controller task "
    "019fc491-21b0-77b0-bf18-53f53a366a7c."
)
RUN_TASK = ROOT / "scripts/run_task.ps1"
PERSONAL_FORBIDDEN = {
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


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=check,
    )


def v1_parent_board() -> tuple[str, dict, str]:
    source = git(ROOT, "show", f"{CUTOVER_PARENT}:docs/task_board.md").stdout.encode("utf-8")
    return parse_board(source)


def board_hash(repo: Path) -> str:
    return hashlib.sha256((repo / "docs/task_board.md").read_bytes()).hexdigest()


def invoke_run_task(
    repo: Path,
    *arguments: str,
    expected_exit: int = 0,
    env: dict[str, str] | None = None,
) -> dict:
    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(RUN_TASK),
            *arguments,
        ],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        env=env,
    )
    assert completed.returncode == expected_exit, completed.stderr or completed.stdout
    return json.loads(completed.stdout)


def invoke_personal(
    repo: Path,
    command: str,
    *arguments: str,
    expected_exit: int = 0,
) -> dict:
    completed = subprocess.run(
        ["py", "-m", "scripts.connlab_personal_task", command, "--repo-root", str(repo), *arguments, "--json"],
        cwd=ROOT,
        text=True, encoding="utf-8", capture_output=True, check=False,
    )
    assert completed.returncode == expected_exit, completed.stderr or completed.stdout
    return json.loads(completed.stdout)


def init_v2_repo(repo: Path) -> None:
    repo.mkdir(); git(repo, "init", "-b", "master")
    git(repo, "config", "user.email", "test@example.invalid"); git(repo, "config", "user.name", "ConnLab Flow Test")
    (repo / ".gitignore").write_text("tmp/\n", encoding="utf-8"); (repo / "docs").mkdir()
    prefix, board, suffix = parse_board((ROOT / "docs/task_board.md").read_bytes())
    board.update(state="idle", active=None, queue=[], next_enqueue_sequence=1)
    (repo / "docs/task_board.md").write_bytes(render_board(prefix, board, suffix))
    git(repo, "add", ".gitignore", "docs/task_board.md"); git(repo, "commit", "-m", "fixture: v2 idle")


def commit_board(repo: Path, message: str) -> None:
    git(repo, "add", "docs/task_board.md"); git(repo, "commit", "-m", message)


def committed_evidence(repo: Path, name: str, content: str) -> str:
    relative = f"docs/lane_evidence/{name}.md"
    target = repo / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    data = content.encode("utf-8")
    target.write_bytes(data)
    git(repo, "add", relative)
    git(repo, "commit", "-m", f"evidence: {name}")
    commit = git(repo, "rev-parse", "HEAD").stdout.strip()
    return f"{relative}@{commit}#{hashlib.sha256(data).hexdigest()}"


def invoke_complex_role(
    repo: Path,
    task_id: str,
    role: str,
    subject_commit: str,
    status: str,
    next_role: str,
) -> None:
    action_names = {
        "Planner": "planner_dispatch",
        "Developer": "developer_dispatch",
        "Reviewer": "reviewer_dispatch",
        "QA": "qa_dispatch",
        "Integrator": "integrator_dispatch",
    }
    action_id = hashlib.sha256(f"{task_id}:{role}".encode()).hexdigest()
    action = {
        "schema": "connlab.serial-native-action",
        "version": 1,
        "action_id": action_id,
        "action": action_names[role],
        "role": role,
        "attempt": 1,
        "prompt_sha256": "3" * 64,
        "title": role,
        "recorded_at": "2026-08-07T00:00:00Z",
    }
    begun = invoke_personal(
        repo,
        "begin-role",
        "--expected-board-sha256", board_hash(repo),
        "--task-id", task_id,
        "--role", role,
        "--native-action-json", json.dumps(action, separators=(",", ":")),
    )
    assert begun["code"] == "ALLOW_BEGIN_ROLE"
    commit_board(repo, f"begin {role}")
    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    invocation = {
        "schema": "connlab.serial-invocation",
        "version": 1,
        "action_id": action_id,
        "role": role,
        "attempt": 1,
        "thread_id": None,
        "agent_id": f"agent-{role.lower()}",
        "host_id": board["active"]["complex_context"].get("host_id"),
        "status": "started",
        "recorded_at": "2026-08-07T00:00:01Z",
    }
    recorded = invoke_personal(
        repo,
        "record-invocation",
        "--expected-board-sha256", board_hash(repo),
        "--task-id", task_id,
        "--role", role,
        "--native-action-id", action_id,
        "--invocation-json", json.dumps(invocation, separators=(",", ":")),
    )
    assert recorded["code"] == "ALLOW_RECORD_INVOCATION"
    commit_board(repo, f"record {role} invocation")
    evidence = committed_evidence(repo, role.lower(), f"{role} evidence\n")
    callback = {
        "schema": "connlab.serial-callback",
        "version": 1,
        "task_id": task_id,
        "role": role,
        "status": status,
        "subject_commit": subject_commit,
        "evidence": evidence,
        "next": next_role,
        "blocker": None,
    }
    consumed = invoke_personal(
        repo,
        "consume-callback",
        "--expected-board-sha256", board_hash(repo),
        "--task-id", task_id,
        "--callback-json", json.dumps(callback, separators=(",", ":")),
    )
    assert consumed["code"] == "ALLOW_CONSUME_CALLBACK"
    commit_board(repo, f"consume {role} callback")


def prepare_complex_task_host(
    repo: Path,
    worktree: Path,
    *,
    task_id: str = "TASK_BLOCKED",
) -> str:
    init_v2_repo(repo)
    request = {
        "schema": "connlab.serial-task-request",
        "version": 1,
        "task_id": task_id,
        "summary": "exercise a typed complex blocker",
        "root_cause_clear": True,
        "expected_result_clear": True,
        "may_touch": ["docs/task_board.md", "a.py", "b.py", "c.py"],
        "targeted_validation": ["pytest blocker"],
        "requires_independent_review": True,
        "forbidden_categories": {**PERSONAL_FORBIDDEN, "push_or_release": False},
    }
    submitted = invoke_run_task(
        repo,
        "-Task", task_id,
        "-Action", "Submit",
        "-RepositoryRoot", str(repo),
        "-ExpectedBoardSha256", board_hash(repo),
        "-RequestJson", json.dumps(request, separators=(",", ":")),
        "-Json",
    )
    assert submitted["code"] == "ALLOW_ACTIVATE"
    commit_board(repo, "activate blocked task")
    invoke_complex_role(
        repo,
        task_id,
        "Planner",
        git(repo, "rev-parse", "HEAD").stdout.strip(),
        "ready",
        "User",
    )
    approved = {
        "schema": "connlab.personal-task-approved-request",
        "version": 1,
        "task_id": task_id,
        "summary": "approved blocker fixture",
        "kind": "planned",
        "may_touch": ["docs/task_board.md", "a.py"],
        "expected_file_count": 2,
        "classification_reason": "bounded complex recovery fixture",
        "targeted_validation": ["pytest blocker"],
        "forbidden_categories": PERSONAL_FORBIDDEN,
    }
    approval = invoke_run_task(
        repo,
        "-Task", task_id,
        "-Action", "Approve",
        "-RepositoryRoot", str(repo),
        "-ExpectedBoardSha256", board_hash(repo),
        "-ApprovedRequestJson", json.dumps(approved, separators=(",", ":")),
        "-PlanRef", "docs/plan.md@" + "a" * 40 + "#" + "b" * 64,
        "-ApprovalRef", "用户批准 blocker 恢复测试。",
        "-Json",
    )
    assert approval["code"] == "ALLOW_APPROVE"
    commit_board(repo, "approve blocked task")

    base = git(repo, "rev-parse", "HEAD").stdout.strip()
    branch = f"codex/{task_id.lower().replace('_', '-')}"
    git(repo, "worktree", "add", "-b", branch, str(worktree), base)
    action_id = hashlib.sha256(f"host:{task_id}".encode()).hexdigest()
    action = {
        "schema": "connlab.serial-native-action",
        "version": 1,
        "action_id": action_id,
        "action": "host_create",
        "role": "Host",
        "attempt": 1,
        "prompt_sha256": "3" * 64,
        "title": "Host",
        "recorded_at": "2026-08-07T00:00:02Z",
    }
    begun = invoke_personal(
        repo,
        "begin-host",
        "--expected-board-sha256", board_hash(repo),
        "--task-id", task_id,
        "--native-action-json", json.dumps(action, separators=(",", ":")),
    )
    assert begun["code"] == "ALLOW_BEGIN_HOST"
    commit_board(repo, "begin blocked task host")
    host = {
        "schema": "connlab.serial-worktree",
        "version": 1,
        "action_id": action_id,
        "thread_id": f"thread-{task_id.lower()}",
        "host_id": f"host-{task_id.lower()}",
        "branch": branch,
        "worktree": str(worktree.resolve()),
        "base_sha": base,
        "head_sha": base,
        "integration_target": "master",
        "clean": True,
        "recorded_at": "2026-08-07T00:00:03Z",
    }
    recorded = invoke_personal(
        repo,
        "record-host",
        "--expected-board-sha256", board_hash(repo),
        "--task-id", task_id,
        "--native-action-id", action_id,
        "--worktree-json", json.dumps(host, separators=(",", ":")),
    )
    assert recorded["code"] == "ALLOW_RECORD_HOST"
    commit_board(repo, "record blocked task host")
    (worktree / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
    git(worktree, "add", "a.py")
    git(worktree, "commit", "-m", "implement blocker fixture")
    return git(worktree, "rev-parse", "HEAD").stdout.strip()


def prepare_integration_ready(
    repo: Path,
    worktree: Path,
    *,
    task_id: str,
) -> tuple[str, dict]:
    subject = prepare_complex_task_host(repo, worktree, task_id=task_id)
    for role, status, next_role in (
        ("Developer", "ready", "Reviewer"),
        ("Reviewer", "pass", "QA"),
        ("QA", "pass", "Integrator"),
        ("Integrator", "pass", "User"),
    ):
        invoke_complex_role(repo, task_id, role, subject, status, next_role)
    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    context = board["active"]["complex_context"]
    primary_parent = git(repo, "rev-parse", "HEAD").stdout.strip()
    git(repo, "merge", "--no-ff", "--no-edit", context["task_branch"])
    merge_commit = git(repo, "rev-parse", "HEAD").stdout.strip()
    integration = {
        "schema": "connlab.serial-integration",
        "version": 1,
        "subject_commit": subject,
        "branch_head": subject,
        "primary_parent": primary_parent,
        "merge_commit": merge_commit,
        "merge_tree": git(repo, "rev-parse", "HEAD^{tree}").stdout.strip(),
        "parents": [primary_parent, subject],
        "evidence_refs": context["evidence_refs"],
        "command": ["git", "merge", "--no-ff", context["task_branch"]],
        "clean": True,
        "recorded_at": "2026-08-07T00:00:04Z",
    }
    return subject, integration


def test_candidate_board_human_summary_matches_v2_idle_authority() -> None:
    text = (ROOT / "docs/task_board.md").read_text(encoding="utf-8")
    active_work = text.split("## Active Work", 1)[1].split("## Queue", 1)[0]
    queue = text.split("## Queue", 1)[1].split("## Retained History", 1)[0]

    assert "No active task" in active_work
    assert "atomically closed by the cutover" in active_work
    assert "implemented_pending_human_review" not in active_work
    assert "unauthorized" not in active_work
    assert "Idle; ready to accept a newly submitted task" in queue
    assert "awaits explicit User" not in queue


@pytest.mark.parametrize(
    ("classification", "may_touch", "requires_independent_review"),
    (
        ("simple", ["docs/task_board.md"], False),
        ("complex", ["docs/task_board.md", "a.py", "b.py", "c.py"], True),
    ),
)
def test_v2_busy_submit_returns_wait_without_parsing_or_writing(
    tmp_path: Path,
    classification: str,
    may_touch: list[str],
    requires_independent_review: bool,
) -> None:
    repo = tmp_path / f"busy-{classification}"
    init_v2_repo(repo)
    active_request = {
        "schema": "connlab.serial-task-request",
        "version": 1,
        "task_id": f"TASK_ACTIVE_{classification.upper()}",
        "summary": f"keep one {classification} task active",
        "root_cause_clear": True,
        "expected_result_clear": True,
        "may_touch": may_touch,
        "targeted_validation": ["pytest busy"],
        "requires_independent_review": requires_independent_review,
        "forbidden_categories": {**PERSONAL_FORBIDDEN, "push_or_release": False},
    }

    activated = invoke_run_task(
        repo,
        "-Task", active_request["task_id"],
        "-Action", "Submit",
        "-RepositoryRoot", str(repo),
        "-ExpectedBoardSha256", board_hash(repo),
        "-RequestJson", json.dumps(active_request, separators=(",", ":")),
        "-Json",
    )
    assert activated["code"] == "ALLOW_ACTIVATE"
    commit_board(repo, f"activate {classification} owner")
    before_bytes = (repo / "docs/task_board.md").read_bytes()
    before_worktrees = git(repo, "worktree", "list", "--porcelain").stdout
    lock = repo / "tmp/connlab_personal_task.lock"
    lock.parent.mkdir(exist_ok=True)
    lock_bytes = b"pre-existing lock sentinel\n"
    lock.write_bytes(lock_bytes)
    git_marker = tmp_path / f"git-called-{classification}.txt"
    probe_env = os.environ.copy()
    probe_env["GIT_TRACE"] = str(git_marker)

    waiting = invoke_run_task(
        repo,
        "-Task", "TASK_MUST_WAIT",
        "-Action", "Submit",
        "-RepositoryRoot", str(repo),
        "-ExpectedBoardSha256", hashlib.sha256(before_bytes).hexdigest(),
        "-RequestJson", "{not-json",
        "-Json",
        expected_exit=2,
        env=probe_env,
    )

    assert waiting["code"] == "BLOCKED_ACTIVE_TASK_RUNNING"
    assert waiting["changed"] is False
    assert waiting["board_sha256_before"] == waiting["board_sha256_after"]
    assert (repo / "docs/task_board.md").read_bytes() == before_bytes
    assert git(repo, "status", "--porcelain=v1", "--untracked-files=all").stdout == ""
    assert git(repo, "worktree", "list", "--porcelain").stdout == before_worktrees
    assert not git_marker.exists()
    assert lock.read_bytes() == lock_bytes
    _, board, _ = parse_board(before_bytes)
    assert board["active"]["classification"] == classification
    assert board["queue"] == []
    assert board["next_enqueue_sequence"] == 1


def test_v2_user_resubmits_after_close_and_new_request_activates(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "resubmit-after-close"
    init_v2_repo(repo)
    first_request = {
        "schema": "connlab.serial-task-request",
        "version": 1,
        "task_id": "TASK_FIRST",
        "summary": "finish the current simple task",
        "root_cause_clear": True,
        "expected_result_clear": True,
        "may_touch": ["docs/task_board.md"],
        "targeted_validation": ["pytest current"],
        "requires_independent_review": False,
        "forbidden_categories": {**PERSONAL_FORBIDDEN, "push_or_release": False},
    }
    next_request = {
        "schema": "connlab.serial-task-request",
        "version": 1,
        "task_id": "TASK_NEXT",
        "summary": "classify this complex task only after the user resubmits",
        "root_cause_clear": True,
        "expected_result_clear": True,
        "may_touch": ["docs/task_board.md", "a.py", "b.py", "c.py"],
        "targeted_validation": ["pytest next"],
        "requires_independent_review": True,
        "forbidden_categories": {**PERSONAL_FORBIDDEN, "push_or_release": False},
    }

    first = invoke_run_task(
        repo,
        "-Task", "TASK_FIRST",
        "-Action", "Submit",
        "-RepositoryRoot", str(repo),
        "-ExpectedBoardSha256", board_hash(repo),
        "-RequestJson", json.dumps(first_request, separators=(",", ":")),
        "-Json",
    )
    assert first["code"] == "ALLOW_ACTIVATE"
    commit_board(repo, "activate current owner")

    validation = {
        "schema": "connlab.personal-task-validation",
        "version": 1,
        "status": "passed",
        "checks": [{"command": "pytest current", "exit_code": 0, "summary": "passed"}],
        "observed_paths": ["docs/task_board.md"],
        "manual_checks": [],
        "recorded_at": "2026-08-07T00:00:00Z",
    }
    reviewed = invoke_personal(
        repo,
        "mark-review",
        "--expected-board-sha256", board_hash(repo),
        "--task-id", "TASK_FIRST",
        "--validation-json", json.dumps(validation, separators=(",", ":")),
    )
    assert reviewed["code"] == "ALLOW_MARK_REVIEW"
    commit_board(repo, "mark current owner reviewed")
    closed = invoke_run_task(
        repo,
        "-Task", "TASK_FIRST",
        "-Action", "Close",
        "-RepositoryRoot", str(repo),
        "-ExpectedBoardSha256", board_hash(repo),
        "-DecisionRef", "关闭当前任务。",
        "-Json",
    )
    assert closed["code"] == "ALLOW_CLOSE"
    commit_board(repo, "close current owner")

    activated_next = invoke_run_task(
        repo,
        "-Task", "TASK_NEXT",
        "-Action", "Submit",
        "-RepositoryRoot", str(repo),
        "-ExpectedBoardSha256", board_hash(repo),
        "-RequestJson", json.dumps(next_request, separators=(",", ":")),
        "-Json",
    )
    assert activated_next["code"] == "ALLOW_ACTIVATE"
    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    assert board["queue"] == []
    assert board["next_enqueue_sequence"] == 1
    assert board["active"]["task_id"] == next_request["task_id"]
    assert board["active"]["summary"] == next_request["summary"]
    assert board["active"]["classification"] == "complex"
    assert board["active"]["phase"] == "planning"


def test_v2_legacy_activate_next_token_is_frozen_without_writing(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "legacy-token"
    init_v2_repo(repo)
    before = (repo / "docs/task_board.md").read_bytes()

    frozen = invoke_personal(
        repo,
        "activate-next",
        "--expected-board-sha256", hashlib.sha256(before).hexdigest(),
        "--task-id", "TASK_NOT_QUEUED",
        expected_exit=2,
    )

    assert frozen["code"] == "BLOCKED_LEGACY_MODE_FROZEN"
    assert frozen["changed"] is False
    assert (repo / "docs/task_board.md").read_bytes() == before


def test_real_complex_flow_uses_planner_approval_roles_and_atomic_retained_close(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "daily-entry"
    worktree = tmp_path / "task-host"
    subject, integration = prepare_integration_ready(
        repo,
        worktree,
        task_id="TASK_DAILY_COMPLEX",
    )
    integrated = invoke_personal(
        repo,
        "record-integration",
        "--expected-board-sha256", board_hash(repo),
        "--task-id", "TASK_DAILY_COMPLEX",
        "--integration-json", json.dumps(integration, separators=(",", ":")),
    )
    assert integrated["code"] == "ALLOW_RECORD_INTEGRATION"
    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    assert board["state"] == "implemented_pending_human_review"
    assert board["active"]["phase"] == "human_review"
    commit_board(repo, "record verified primary integration")

    decision_ref = "关闭：人工检查完成。"
    board_before_close = (repo / "docs/task_board.md").read_bytes()
    primary_dirty_path = repo / "primary-dirty.txt"
    primary_dirty_path.write_text("retain\n", encoding="utf-8")
    primary_dirty = invoke_run_task(
        repo,
        "-Task", "TASK_DAILY_COMPLEX",
        "-Action", "Close",
        "-RepositoryRoot", str(repo),
        "-ExpectedBoardSha256", board_hash(repo),
        "-DecisionRef", decision_ref,
        "-Json",
        expected_exit=2,
    )
    assert primary_dirty["code"] == "BLOCKED_WORKTREE_DIRTY"
    assert (repo / "docs/task_board.md").read_bytes() == board_before_close
    primary_dirty_path.unlink()

    host_dirty_path = worktree / "host-dirty.txt"
    host_dirty_path.write_text("retain\n", encoding="utf-8")
    host_dirty = invoke_run_task(
        repo,
        "-Task", "TASK_DAILY_COMPLEX",
        "-Action", "Close",
        "-RepositoryRoot", str(repo),
        "-ExpectedBoardSha256", board_hash(repo),
        "-DecisionRef", decision_ref,
        "-Json",
        expected_exit=2,
    )
    assert host_dirty["code"] == "BLOCKED_WORKTREE_FACTS"
    assert (repo / "docs/task_board.md").read_bytes() == board_before_close
    host_dirty_path.unlink()

    close_result = invoke_run_task(
        repo,
        "-Task",
        "TASK_DAILY_COMPLEX",
        "-Action",
        "Close",
        "-RepositoryRoot",
        str(repo),
        "-ExpectedBoardSha256",
        board_hash(repo),
        "-DecisionRef",
        decision_ref,
        "-Json",
    )
    assert close_result["code"] == "ALLOW_CLOSE"
    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    assert board["state"] == "idle" and board["active"] is None
    assert board["last_closed"] == {
        "task_id": "TASK_DAILY_COMPLEX",
        "disposition": "retained",
        "decision_ref": decision_ref,
        "integration_commit": integration["merge_commit"],
        "integrator_evidence_ref": integration["evidence_refs"][-1],
        "retained_resources": {
            "thread_id": f"thread-task_daily_complex",
            "worktree": str(worktree.resolve()),
            "branch": "codex/task-daily-complex",
            "head_sha": subject,
        },
        "closed_at": board["last_closed"]["closed_at"],
    }


def test_record_integration_verifies_git_worktree_evidence_and_committed_board(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "integration-proof"
    worktree = tmp_path / "integration-proof-host"
    subject, integration = prepare_integration_ready(
        repo,
        worktree,
        task_id="TASK_INTEGRATION_PROOF",
    )

    dirty_path = worktree / "unreviewed.txt"
    dirty_path.write_text("not reviewed\n", encoding="utf-8")
    before = board_hash(repo)
    dirty = invoke_personal(
        repo,
        "record-integration",
        "--expected-board-sha256", before,
        "--task-id", "TASK_INTEGRATION_PROOF",
        "--integration-json", json.dumps(integration, separators=(",", ":")),
        expected_exit=2,
    )
    assert dirty["code"] == "BLOCKED_WORKTREE_FACTS"
    assert board_hash(repo) == before
    dirty_path.unlink()

    tampered = copy.deepcopy(integration)
    tampered.update(
        primary_parent="e" * 40,
        merge_commit="0" * 40,
        merge_tree="f" * 40,
        parents=["e" * 40, subject],
        evidence_refs=["docs/lane_evidence/missing.md@" + "1" * 40 + "#" + "2" * 64],
    )
    unverified = invoke_personal(
        repo,
        "record-integration",
        "--expected-board-sha256", before,
        "--task-id", "TASK_INTEGRATION_PROOF",
        "--integration-json", json.dumps(tampered, separators=(",", ":")),
        expected_exit=2,
    )
    assert unverified["code"] == "BLOCKED_INTEGRATION_PROOF"
    assert board_hash(repo) == before

    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    evidence_ref = board["active"]["complex_context"]["evidence_refs"][-1]
    failure = {"schema": "connlab.serial-failure-proof", "version": 1, "operation": "integration", "command": ["git", "merge"], "exit_code": 1, "summary": "temporary integration failure", "recorded_at": "2026-08-07T00:00:00Z"}
    blocker = {"schema": "connlab.serial-task-blocker", "version": 1, "code": "INTEGRATION_BLOCKED", "stage": "integration", "reason": "exercise committed transition guard", "dirty_paths": [], "failed_validation": failure, "subject_commit": subject, "evidence_ref": evidence_ref, "native_action_id": None, "related_ids": [], "retryable": False, "requires_user": True, "resume_phase": "integration", "recorded_at": "2026-08-07T00:00:00Z"}
    blocked = invoke_personal(
        repo,
        "block",
        "--expected-board-sha256", board_hash(repo),
        "--task-id", "TASK_INTEGRATION_PROOF",
        "--blocker-json", json.dumps(blocker, separators=(",", ":")),
    )
    assert blocked["code"] == "ALLOW_BLOCK"
    resumed = invoke_personal(
        repo,
        "resume",
        "--expected-board-sha256", board_hash(repo),
        "--task-id", "TASK_INTEGRATION_PROOF",
        "--decision-ref", "用户决定：重新验证 integration。",
    )
    assert resumed["code"] == "ALLOW_RESUME"
    uncommitted_hash = board_hash(repo)
    uncommitted = invoke_personal(
        repo,
        "record-integration",
        "--expected-board-sha256", uncommitted_hash,
        "--task-id", "TASK_INTEGRATION_PROOF",
        "--integration-json", json.dumps(integration, separators=(",", ":")),
        expected_exit=2,
    )
    assert uncommitted["code"] == "BLOCKED_TRANSITION_UNCOMMITTED"
    assert board_hash(repo) == uncommitted_hash


@pytest.mark.parametrize(("code", "stage", "resume_phase", "retryable"), [("DEVELOPER_BLOCKED", "development", "development", True), ("INTEGRATION_BLOCKED", "integration", "integration", False)])
def test_complex_resume_uses_validated_blocker_resume_phase(tmp_path: Path, code: str, stage: str, resume_phase: str, retryable: bool) -> None:
    repo = tmp_path / code.lower()
    worktree = tmp_path / f"{code.lower()}-host"
    subject = prepare_complex_task_host(repo, worktree)
    if stage == "integration":
        for role, status, next_role in (
            ("Developer", "ready", "Reviewer"),
            ("Reviewer", "pass", "QA"),
            ("QA", "pass", "Integrator"),
            ("Integrator", "pass", "User"),
        ):
            invoke_complex_role(repo, "TASK_BLOCKED", role, subject, status, next_role)
    evidence_ref = committed_evidence(repo, f"{code.lower()}-blocker", f"{code} evidence\n")
    failure = {"schema": "connlab.serial-failure-proof", "version": 1, "operation": stage, "command": ["test"], "exit_code": 1, "summary": "failed", "recorded_at": "2026-08-07T00:00:00Z"}
    blocker = {"schema": "connlab.serial-task-blocker", "version": 1, "code": code, "stage": stage, "reason": "User-resolvable blocker", "dirty_paths": [], "failed_validation": failure, "subject_commit": subject, "evidence_ref": evidence_ref, "native_action_id": None, "related_ids": [], "retryable": retryable, "requires_user": True, "resume_phase": resume_phase, "recorded_at": "2026-08-07T00:00:00Z"}
    blocked = invoke_personal(
        repo,
        "block",
        "--expected-board-sha256", board_hash(repo),
        "--task-id", "TASK_BLOCKED",
        "--blocker-json", json.dumps(blocker, separators=(",", ":")),
    )
    assert blocked["code"] == "ALLOW_BLOCK"
    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    assert board["active"]["phase"] == "blocked"
    assert board["active"]["blocker"] == blocker
    commit_board(repo, "record typed complex blocker")
    resumed = invoke_personal(repo, "resume", "--expected-board-sha256", board_hash(repo), "--task-id", "TASK_BLOCKED", "--decision-ref", "用户决定：继续。")
    assert resumed["code"] == "ALLOW_RESUME"; _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes()); assert board["active"]["phase"] == resume_phase and board["active"]["blocker"] is None


def test_atomic_cutover_commit_migrates_v1_human_review_to_v2_idle_and_reverts(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "cutover-e2e"
    repo.mkdir()
    git(repo, "init", "-b", "master")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "ConnLab Cutover Test")

    for relative in CUTOVER_PATHS:
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        source = git(ROOT, "show", f"{CUTOVER_PARENT}:{relative}").stdout.encode("utf-8")
        target.write_bytes(source)
    git(repo, "add", "--", *CUTOVER_PATHS)
    git(repo, "commit", "-m", "fixture: v1 human-review baseline")
    _, source_board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    base_tree = git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    git(repo, "switch", "-c", "candidate")

    for relative in CUTOVER_PATHS:
        shutil.copyfile(ROOT / relative, repo / relative)
    git(repo, "add", "--", *CUTOVER_PATHS)
    cutover = git(repo, "commit", "-m", "governance: activate serial complex workflow", check=False)
    assert cutover.returncode == 0, cutover.stderr or cutover.stdout
    cutover_commit = git(repo, "rev-parse", "HEAD").stdout.strip()
    git(repo, "switch", "master")
    git(repo, "merge", "--ff-only", cutover_commit)

    changed = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", cutover_commit)
    assert set(changed.stdout.splitlines()) == set(CUTOVER_PATHS)
    _, expected_board, _ = parse_board((ROOT / "docs/task_board.md").read_bytes())
    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    assert board["version"] == 2
    assert board["state"] == expected_board["state"]
    assert board["active"] == expected_board["active"]
    assert board["queue"] == expected_board["queue"]
    assert board["next_enqueue_sequence"] == expected_board["next_enqueue_sequence"]
    assert board["retained_history"] == expected_board["retained_history"]
    assert board["last_closed"] is not None
    assert board["last_closed"]["task_id"]
    assert board["last_closed"]["decision_ref"]
    assert "serial complex workflow is active" in (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert "three User interactions" in (
        repo / "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md"
    ).read_text(encoding="utf-8")
    assert git(repo, "status", "--porcelain").stdout == ""

    git(repo, "revert", "--no-edit", cutover_commit)
    assert git(repo, "rev-parse", "HEAD^{tree}").stdout.strip() == base_tree


def test_cutover_migration_requires_inert_queue_and_closes_active_atomically() -> None:
    prefix, current, suffix = v1_parent_board()
    source = copy.deepcopy(current)
    source["state"] = "implemented_pending_human_review"
    source["active"]["phase"] = "human_review"
    source["active"]["blocker"] = None
    source["active"]["validation"] = {
        "schema": "connlab.personal-task-validation",
        "version": 1,
        "status": "passed",
        "checks": [{"command": "bounded", "exit_code": 0, "summary": "passed"}],
        "observed_paths": source["active"]["scope_contract"]["may_touch"],
        "manual_checks": [],
        "recorded_at": "2026-08-06T00:00:00Z",
    }
    retained = copy.deepcopy(source["retained_history"])
    migrated = migrate_v1_to_v2(
        source,
        decision_ref="User approved exact cutover manifest",
        closed_at="2026-08-06T00:00:01Z",
    )

    assert migrated["version"] == 2
    assert migrated["state"] == "idle"
    assert migrated["active"] is None
    assert migrated["queue"] == []
    assert migrated["next_enqueue_sequence"] == 1
    assert migrated["retained_history"] == retained
    assert migrated["last_closed"]["task_id"] == source["active"]["task_id"]

    encoded = render_board(prefix, migrated, suffix)
    _, recovered, _ = parse_board(encoded)
    assert json.loads(json.dumps(recovered)) == migrated


def test_cutover_migration_rejects_a_legacy_queued_request() -> None:
    _, source, _ = v1_parent_board()
    source = copy.deepcopy(source)
    source["state"] = "implemented_pending_human_review"
    source["active"]["phase"] = "human_review"
    source["active"]["blocker"] = None
    source["active"]["validation"] = {
        "schema": "connlab.personal-task-validation",
        "version": 1,
        "status": "passed",
        "checks": [{"command": "bounded", "exit_code": 0, "summary": "passed"}],
        "observed_paths": source["active"]["scope_contract"]["may_touch"],
        "manual_checks": [],
        "recorded_at": "2026-08-06T00:00:00Z",
    }
    source["queue"] = [{
        "task_id": "TASK_WAITING",
        "summary": "legacy queued task",
        "kind": "planned",
        "enqueue_sequence": 1,
        "queued_at": "2026-08-06T00:00:00Z",
        "scope_contract": None,
    }]
    source["next_enqueue_sequence"] = 2

    with pytest.raises(Blocked) as rejected:
        migrate_v1_to_v2(
            source,
            decision_ref="User approved exact cutover commit",
            closed_at="2026-08-06T00:00:01Z",
        )
    assert rejected.value.code == "BLOCKED_CUTOVER_NOT_AUTHORIZED"


def test_v2_complex_active_survives_byte_round_trip_without_conversation_memory() -> None:
    prefix, current, suffix = v1_parent_board()
    migrated = migrate_v1_to_v2(
        {**copy.deepcopy(current), "state": "implemented_pending_human_review", "active": {
            **copy.deepcopy(current["active"]),
            "phase": "human_review",
            "blocker": None,
            "validation": {
                "schema": "connlab.personal-task-validation", "version": 1, "status": "passed",
                "checks": [{"command": "bounded", "exit_code": 0, "summary": "passed"}],
                "observed_paths": current["active"]["scope_contract"]["may_touch"],
                "manual_checks": [], "recorded_at": "2026-08-06T00:00:00Z",
            },
        }},
        decision_ref="cutover",
        closed_at="2026-08-06T00:00:01Z",
    )
    migrated["state"] = "running"
    migrated["active"] = {
        "task_id": "TASK_RECOVERY",
        "summary": "recover entirely from durable refs",
        "kind": "planned",
        "classification": "complex",
        "phase": "review",
        "scope_contract": {"may_touch": ["backend/example.py"]},
        "plan_ref": "tasks/plan.md@" + "1" * 40 + "#" + "2" * 64,
        "approval_ref": "User approval",
        "activation_parent_sha": "3" * 40,
        "activated_at": "2026-08-06T00:00:00Z",
        "updated_at": "2026-08-06T00:00:02Z",
        "blocker": None,
        "validation": None,
        "complex_context": {
            "workflow_version": 1,
            "task_branch": "codex/task-recovery",
            "task_worktree": "D:/tmp/task-recovery",
            "base_sha": "3" * 40,
            "head_sha": "4" * 40,
            "integration_target": "master",
            "worktree_lifecycle": "ready",
            "current_role": "Reviewer",
            "current_attempt": 1,
            "role_invocations": [],
            "host_thread_id": "thread-1",
            "host_id": "host-1",
            "approved_code_paths": ["backend/example.py"],
            "required_gates": ["Reviewer", "QA", "Integrator"],
            "developer_subject_commit": "4" * 40,
            "reviewer_subject_commit": None,
            "qa_subject_commit": None,
            "integrated_commit": None,
            "evidence_refs": [],
            "pending_callback": None,
            "closeout_disposition": None,
            "retained_resource_refs": [],
            "close_decision_ref": None,
        },
    }

    _, recovered, _ = parse_board(render_board(prefix, migrated, suffix))
    assert recovered == migrated
    assert "conversation" not in json.dumps(recovered).lower()
