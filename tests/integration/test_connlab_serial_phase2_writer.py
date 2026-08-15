from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from scripts.connlab_serial_board import parse_board, render_board


ROOT = Path(__file__).resolve().parents[2]
ZERO64 = "0" * 64
FORBIDDEN = {key: False for key in (
    "api_contract", "database", "schema_or_migration", "persistence", "authority",
    "public_drive_workflow", "business_rule_semantics", "destructive_action", "external_mutation",
)}


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], text=True, encoding="utf-8",
        capture_output=True, check=True,
    ).stdout.strip()


def invoke(repo: Path, command: str, *args: str, expected_exit: int = 0) -> dict:
    completed = subprocess.run(
        ["py", "-m", "scripts.connlab_personal_task", command, "--repo-root", str(repo), *args, "--json"],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
    )
    assert completed.returncode == expected_exit, completed.stderr or completed.stdout
    return json.loads(completed.stdout)


def board_hash(repo: Path) -> str:
    return hashlib.sha256((repo / "docs/task_board.md").read_bytes()).hexdigest()


def build_action(repo: Path) -> dict:
    completed = subprocess.run(
        ["py", "-m", "scripts.connlab_serial_payload", "native-action", "--repo-root", str(repo),
         "--action", "developer_dispatch", "--prompt-file", str(repo / "docs/prompt.md"),
         "--title", "Bounded fix"],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    return json.loads(completed.stdout)


def build_reference(repo: Path, relative: str) -> str:
    completed = subprocess.run(
        ["py", "-m", "scripts.connlab_serial_payload", "git-reference", "--repo-root", str(repo),
         "--path", relative],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    return completed.stdout.strip()


def scope(paths: list[str]) -> dict:
    return {
        "may_touch": paths,
        "expected_file_count": len(paths),
        "classification_reason": "approved complex task",
        "targeted_validation": ["py -m pytest"],
        "forbidden_categories": FORBIDDEN,
    }


def blocker(code: str, evidence: str, subject: str | None) -> dict:
    stage = "review" if code == "REVIEWER_BLOCKED" else "development"
    return {
        "schema": "connlab.serial-task-blocker", "version": 1, "code": code, "stage": stage,
        "reason": "bounded fixture blocker", "dirty_paths": ["scripts/new.py"] if code == "SCOPE_EXPANDED" else [],
        "failed_validation": None, "subject_commit": subject, "evidence_ref": evidence,
        "native_action_id": None, "related_ids": ["finding-1"] if code == "REVIEWER_BLOCKED" else [],
        "retryable": True, "requires_user": code != "REVIEWER_BLOCKED",
        "resume_phase": "development" if code == "REVIEWER_BLOCKED" else "planning",
        "recorded_at": "2026-08-15T00:00:00Z",
    }


def context(base: str, *, worktree: Path | None = None, head: str | None = None) -> dict:
    hosted = worktree is not None
    return {
        "workflow_version": 1,
        "task_branch": "codex/task-phase2" if hosted else None,
        "task_worktree": str(worktree.resolve()) if hosted else None,
        "base_sha": base,
        "head_sha": head or base,
        "integration_target": "master",
        "worktree_lifecycle": "ready" if hosted else "absent",
        "current_role": None,
        "current_attempt": 2,
        "role_invocations": [],
        "host_thread_id": "thread-1" if hosted else None,
        "host_id": "host-1" if hosted else None,
        "approved_code_paths": ["docs/task_board.md", "scripts/current.py"],
        "required_gates": ["Reviewer", "QA", "Integrator"],
        "developer_subject_commit": head if hosted else None,
        "reviewer_subject_commit": None,
        "qa_subject_commit": None,
        "integrated_commit": None,
        "evidence_refs": [],
        "blocker_history": [],
        "pending_callback": None,
        "closeout_disposition": None,
        "retained_resource_refs": [],
        "close_decision_ref": None,
    }


def init_repo(repo: Path) -> str:
    repo.mkdir()
    git(repo, "init", "-b", "master")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Phase 2 Test")
    (repo / ".gitignore").write_text("tmp/\n", encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs/prompt.md").write_text("Exact Developer prompt.\n", encoding="utf-8")
    prefix, board, suffix = parse_board((ROOT / "docs/task_board.md").read_bytes())
    board.update(state="idle", active=None, queue=[], next_enqueue_sequence=1)
    (repo / "docs/task_board.md").write_bytes(render_board(prefix, board, suffix))
    git(repo, "add", ".gitignore", "docs/prompt.md", "docs/task_board.md")
    git(repo, "commit", "-m", "fixture base")
    return git(repo, "rev-parse", "HEAD")


def commit_evidence(repo: Path) -> str:
    path = repo / "docs/lane_evidence/blocker.md"
    path.parent.mkdir(parents=True)
    data = b"typed blocker evidence\n"
    path.write_bytes(data)
    git(repo, "add", "docs/lane_evidence/blocker.md")
    git(repo, "commit", "-m", "fixture evidence")
    return f"docs/lane_evidence/blocker.md@{git(repo, 'rev-parse', 'HEAD')}#{hashlib.sha256(data).hexdigest()}"


def write_active(repo: Path, value: dict) -> None:
    path = repo / "docs/task_board.md"
    prefix, board, suffix = parse_board(path.read_bytes())
    board.update(state="running", active=value)
    path.write_bytes(render_board(prefix, board, suffix))
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "record blocked state")


def active_value(base: str, current_blocker: dict, current_context: dict) -> dict:
    return {
        "task_id": "TASK_PHASE2", "summary": "Phase 2", "kind": "planned", "classification": "complex",
        "phase": "development" if current_blocker["code"] == "REVIEWER_BLOCKED" else "blocked",
        "scope_contract": scope(["docs/task_board.md", "scripts/current.py"]),
        "plan_ref": f"docs/plan.md@{base}#{ZERO64}", "approval_ref": "用户：初始批准",
        "activation_parent_sha": base, "activated_at": "2026-08-15T00:00:00Z",
        "updated_at": "2026-08-15T00:00:00Z", "blocker": current_blocker,
        "validation": None, "complex_context": current_context,
    }


def test_public_writer_atomically_reenters_developer_and_changes_only_board(tmp_path: Path) -> None:
    repo, host = tmp_path / "primary", tmp_path / "host"
    base = init_repo(repo)
    git(repo, "worktree", "add", "-b", "codex/task-phase2", str(host), base)
    (host / "subject.txt").write_text("subject\n", encoding="utf-8")
    git(host, "add", "subject.txt"); git(host, "commit", "-m", "subject")
    subject = git(host, "rev-parse", "HEAD")
    evidence = commit_evidence(repo)
    value = active_value(base, blocker("REVIEWER_BLOCKED", evidence, subject), context(base, worktree=host, head=subject))
    value["complex_context"]["evidence_refs"] = [evidence]
    write_active(repo, value)
    action = build_action(repo)
    prompt_ref = build_reference(repo, "docs/prompt.md")
    prompt_digest = hashlib.sha256(b"Exact Developer prompt.\n").hexdigest()
    assert prompt_ref == (
        f"docs/prompt.md@{git(repo, 'rev-parse', 'HEAD')}#"
        f"{prompt_digest}"
    )

    before = (repo / "docs/task_board.md").read_bytes()
    bypass = invoke(
        repo, "resume", "--expected-board-sha256", board_hash(repo), "--task-id", "TASK_PHASE2",
        "--decision-ref", "user:bounded-fix-approved", expected_exit=2,
    )
    assert bypass["code"] == "BLOCKED_STATE"
    assert (repo / "docs/task_board.md").read_bytes() == before

    result = invoke(
        repo, "reenter-development", "--expected-board-sha256", board_hash(repo),
        "--task-id", "TASK_PHASE2", "--decision-ref", "user:bounded-fix-approved",
        "--native-action-json", json.dumps(action, separators=(",", ":")),
    )

    assert result["code"] == "ALLOW_REENTER_DEVELOPMENT"
    assert result["active_snapshot"]["approval_ref"] == "用户：初始批准"
    assert git(repo, "diff", "--name-only") == "docs/task_board.md"
    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    active = board["active"]; context_value = active["complex_context"]
    assert active["phase"] == "development" and active["blocker"] is None
    assert context_value["current_attempt"] == 3
    assert context_value["pending_callback"]["action_id"] == action["action_id"]
    assert context_value["blocker_history"][0]["blocker"]["code"] == "REVIEWER_BLOCKED"


def test_public_approve_atomically_applies_scope_amendment(tmp_path: Path) -> None:
    repo = tmp_path / "amendment"
    base = init_repo(repo)
    evidence = commit_evidence(repo)
    value = active_value(base, blocker("SCOPE_EXPANDED", evidence, None), context(base))
    write_active(repo, value)
    amended = scope(["docs/task_board.md", "scripts/current.py", "scripts/new.py"])
    approved = {
        "schema": "connlab.personal-task-approved-request", "version": 1,
        "task_id": "TASK_PHASE2", "summary": "Approved amendment", "kind": "planned", **amended,
    }

    result = invoke(
        repo, "approve", "--expected-board-sha256", board_hash(repo), "--task-id", "TASK_PHASE2",
        "--approved-request-json", json.dumps(approved, separators=(",", ":")),
        "--plan-ref", f"docs/amended-plan.md@{base}#{'4' * 64}",
        "--approval-ref", "user:scope-amendment-approved",
    )

    assert result["code"] == "ALLOW_SCOPE_AMEND"
    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    active = board["active"]
    assert active["phase"] == "development" and active["blocker"] is None
    assert active["scope_contract"] == amended
    assert active["complex_context"]["approved_code_paths"] == amended["may_touch"]
    assert active["complex_context"]["blocker_history"][0]["resolution"] == "scope_amendment"
