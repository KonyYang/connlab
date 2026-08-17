from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

import scripts.connlab_serial_board as board_module
from scripts.connlab_serial_board import Blocked, parse_board, render_board


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


def validation_manifest() -> dict:
    return {
        "schema": "connlab.validation-manifest", "version": 1, "task_id": "TASK_PHASE2",
        "checks": [{
            "id": "phase2", "kind": "targeted", "run_for": ["Developer", "QA"],
            "cwd": ".", "argv": ["py", "-m", "pytest"], "timeout_seconds": 30,
            "permission": "workspace", "required": True,
        }],
    }


def commit_plan(repo: Path, approved: dict, manifest: dict | None, *, duplicate_manifest: bool = False) -> str:
    path = repo / "docs/amended-plan.md"
    blocks = [json.dumps(approved, ensure_ascii=False, separators=(",", ":"))]
    if manifest is not None:
        blocks.append(json.dumps(manifest, ensure_ascii=False, separators=(",", ":")))
        if duplicate_manifest:
            blocks.append(json.dumps(manifest, ensure_ascii=False, separators=(",", ":")))
    text = (
        "# Amended Plan\n\n"
        "Developer, Reviewer, QA and Integrator are all `gpt-5.6-sol / high / exact route`.\n\n"
        + "\n\n".join(f"```json\n{block}\n```" for block in blocks) + "\n"
    )
    path.write_text(text, encoding="utf-8")
    git(repo, "add", "docs/amended-plan.md")
    git(repo, "commit", "-m", "commit amended plan")
    head = git(repo, "rev-parse", "HEAD")
    data = subprocess.run(
        ["git", "-C", str(repo), "show", f"{head}:docs/amended-plan.md"],
        capture_output=True, check=True,
    ).stdout
    return f"docs/amended-plan.md@{head}#{hashlib.sha256(data).hexdigest()}"


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
    value["complex_context"]["role_invocations"] = [
        {"action_id": "developer-1", "role": "Developer", "attempt": 1},
        {"action_id": "developer-2", "role": "Developer", "attempt": 2},
    ]
    value["complex_context"]["timing_facts"] = {
        "host": None,
        "roles": [
            {"role": "Developer", "attempt": attempt, "started_at": "2026-08-15T00:00:00Z", "completed_at": "2026-08-15T00:00:01Z"}
            for attempt in (1, 2)
        ],
        "integration_completed_at": None,
    }
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
        "--task-id", "TASK_PHASE2", "--decision-ref", "用户：初始批准",
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
    manifest = validation_manifest()
    plan_ref = commit_plan(repo, approved, manifest)

    result = invoke(
        repo, "approve", "--expected-board-sha256", board_hash(repo), "--task-id", "TASK_PHASE2",
        "--approved-request-json", json.dumps(approved, separators=(",", ":")),
        "--plan-ref", plan_ref,
        "--approval-ref", "user:scope-amendment-approved",
    )

    assert result["code"] == "ALLOW_SCOPE_AMEND"
    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    active = board["active"]
    assert active["phase"] == "development" and active["blocker"] is None
    assert active["scope_contract"] == amended
    assert active["complex_context"]["approved_code_paths"] == amended["may_touch"]
    assert active["complex_context"]["validation_manifest"] == manifest
    assert set(active["complex_context"]["execution_routes"]) == {"Developer", "Reviewer", "QA", "Integrator"}
    assert active["complex_context"]["blocker_history"][0]["resolution"] == "scope_amendment"


@pytest.mark.parametrize("fault", ["missing_manifest", "wrong_manifest", "duplicate_manifest", "mismatched_request", "stale_digest", "route_drift"])
def test_blocked_scope_reapproval_with_invalid_plan_facts_is_zero_write(tmp_path: Path, fault: str) -> None:
    repo = tmp_path / fault
    base = init_repo(repo)
    evidence = commit_evidence(repo)
    current = context(base)
    if fault == "route_drift":
        current["execution_routes"] = {
            role: {"model": "gpt-5.6-sol", "reasoning_effort": "high", "reason": "original route"}
            for role in ("Developer", "Reviewer", "QA", "Integrator")
        }
    value = active_value(base, blocker("SCOPE_EXPANDED", evidence, None), current)
    write_active(repo, value)
    amended = scope(["docs/task_board.md", "scripts/current.py", "scripts/new.py"])
    approved = {
        "schema": "connlab.personal-task-approved-request", "version": 1,
        "task_id": "TASK_PHASE2", "summary": "Approved amendment", "kind": "planned", **amended,
    }
    plan_approved = approved if fault != "mismatched_request" else {**approved, "summary": "Stale"}
    manifest = None if fault == "missing_manifest" else validation_manifest()
    if fault == "wrong_manifest": manifest = {**manifest, "task_id": "WRONG_TASK"}
    plan_ref = commit_plan(repo, plan_approved, manifest, duplicate_manifest=fault == "duplicate_manifest")
    if fault == "stale_digest":
        plan_ref = plan_ref.rsplit("#", 1)[0] + "#" + "0" * 64
    before = {
        "board": (repo / "docs/task_board.md").read_bytes(),
        "head": git(repo, "rev-parse", "HEAD"),
        "index": git(repo, "diff", "--cached", "--name-only"),
        "status": git(repo, "status", "--porcelain=v1", "--untracked-files=all"),
    }

    failure = invoke(
        repo, "approve", "--expected-board-sha256", board_hash(repo), "--task-id", "TASK_PHASE2",
        "--approved-request-json", json.dumps(approved, separators=(",", ":")),
        "--plan-ref", plan_ref, "--approval-ref", "user:scope-amendment-approved",
        expected_exit=2,
    )

    assert failure["code"] == "BLOCKED_PLAN_INVALID"
    assert (repo / "docs/task_board.md").read_bytes() == before["board"]
    assert git(repo, "rev-parse", "HEAD") == before["head"]
    assert git(repo, "diff", "--cached", "--name-only") == before["index"]
    assert git(repo, "status", "--porcelain=v1", "--untracked-files=all") == before["status"]


def test_invalid_rendered_candidate_never_replaces_board(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "atomic-board"
    init_repo(repo)
    path = repo / "docs/task_board.md"
    prefix, value, suffix = parse_board(path.read_bytes())
    before = path.read_bytes()
    git_before = (git(repo, "rev-parse", "HEAD"), git(repo, "diff", "--cached", "--name-only"), git(repo, "status", "--porcelain=v1", "--untracked-files=all"))
    monkeypatch.setattr(board_module, "render_board", lambda *_args: b"invalid candidate")

    with pytest.raises(Blocked) as caught:
        board_module.write_board(repo, path, prefix, value, suffix)

    assert caught.value.code == "BLOCKED_WRITE_FAILED"
    assert path.read_bytes() == before
    assert (git(repo, "rev-parse", "HEAD"), git(repo, "diff", "--cached", "--name-only"), git(repo, "status", "--porcelain=v1", "--untracked-files=all")) == git_before
    assert not list(path.parent.glob(".task_board.*.tmp"))


def test_duplicate_timing_identity_is_blocked_before_board_replacement(tmp_path: Path) -> None:
    repo = tmp_path / "duplicate-timing"
    base = init_repo(repo)
    evidence = commit_evidence(repo)
    path = repo / "docs/task_board.md"
    prefix, control, suffix = parse_board(path.read_bytes())
    current = context(base)
    timing = {"role": "Developer", "attempt": 1, "started_at": "2026-08-15T00:00:00Z", "completed_at": None}
    current["timing_facts"] = {"host": None, "roles": [timing, dict(timing)], "integration_completed_at": None}
    control.update(state="running", active=active_value(base, blocker("REVIEWER_BLOCKED", evidence, base), current))
    before = path.read_bytes()

    with pytest.raises(Blocked) as caught:
        board_module.write_board(repo, path, prefix, control, suffix)

    assert caught.value.code == "BLOCKED_WRITE_FAILED"
    assert "timing identity is duplicated" in caught.value.reason
    assert path.read_bytes() == before
    assert not list(path.parent.glob(".task_board.*.tmp"))
