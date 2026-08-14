from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from scripts.connlab_serial_board import Blocked, parse_board, render_board
from scripts.connlab_serial_evidence_topology import (
    verify_callback_evidence_topology,
    verify_integration_evidence_topology,
)
from tests.integration.test_connlab_serial_complex_recovery import (
    board_hash,
    invoke_personal,
    prepare_integration_ready,
)


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "TASK_TOPOLOGY"
ACTION_ID = "a" * 64
ROUTE = ("gpt-5.6-sol", "medium", "risk:authority")


def git(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=check,
    )
    return result.stdout.strip()


def fixture(
    tmp_path: Path,
    *,
    mixed_evidence: bool = False,
    header_overrides: dict[str, str] | None = None,
) -> tuple[Path, Path, dict, dict, str]:
    repo, host = tmp_path / "repo", tmp_path / "host"
    repo.mkdir()
    git(repo, "init", "-b", "master")
    git(repo, "config", "user.name", "Topology Test")
    git(repo, "config", "user.email", "topology@example.invalid")
    (repo / "docs").mkdir()
    (repo / "docs/lane_evidence").mkdir()
    plan_path = repo / "docs/plan.md"
    plan_bytes = (
        "# Plan\n\nDeveloper, Reviewer, QA and Integrator are all "
        "`gpt-5.6-sol / medium / risk:authority`.\n"
    ).encode()
    plan_path.write_bytes(plan_bytes)
    planner_path = repo / f"docs/lane_evidence/{TASK_ID}_planner.md"
    planner_bytes = f"TASK_ID: {TASK_ID}\nROLE: Planner\nSTATUS: ready\n".encode()
    planner_path.write_bytes(planner_bytes)
    _, template, suffix = parse_board((ROOT / "docs/task_board.md").read_bytes())
    template.update(state="running", active=None, queue=[], next_enqueue_sequence=1)
    (repo / "docs/task_board.md").write_bytes(render_board("", template, suffix))
    git(repo, "add", "docs/plan.md", str(planner_path.relative_to(repo)), "docs/task_board.md")
    git(repo, "commit", "-m", "fixture base")
    plan_commit = git(repo, "rev-parse", "HEAD")
    plan_ref = f"docs/plan.md@{plan_commit}#{hashlib.sha256(plan_bytes).hexdigest()}"
    planner_ref = (
        f"docs/lane_evidence/{TASK_ID}_planner.md@{plan_commit}#"
        f"{hashlib.sha256(planner_bytes).hexdigest()}"
    )

    git(repo, "worktree", "add", "-b", "codex/task-topology", str(host), plan_commit)
    (host / "implementation.py").write_text("VALUE = 1\n", encoding="utf-8")
    git(host, "add", "implementation.py")
    git(host, "commit", "-m", "implementation subject")
    subject = git(host, "rev-parse", "HEAD")

    invocation = {
        "schema": "connlab.serial-invocation", "version": 1,
        "action_id": ACTION_ID, "role": "Developer", "attempt": 1,
        "thread_id": None, "agent_id": "agent-developer", "host_id": "host-1",
        "status": "started", "recorded_at": "2026-08-15T00:00:00Z",
    }
    planner_invocation = {
        **invocation, "action_id": "b" * 64, "role": "Planner",
        "agent_id": "agent-planner", "host_id": None,
    }
    context = {
        "workflow_version": 1, "task_branch": "codex/task-topology",
        "task_worktree": str(host.resolve()), "base_sha": plan_commit, "head_sha": plan_commit,
        "integration_target": "master", "worktree_lifecycle": "ready",
        "current_role": "Developer", "current_attempt": 1,
        "role_invocations": [planner_invocation, invocation], "host_thread_id": "thread-1", "host_id": "host-1",
        "approved_code_paths": ["implementation.py"], "required_gates": ["Reviewer", "QA", "Integrator"],
        "developer_subject_commit": None, "reviewer_subject_commit": None,
        "qa_subject_commit": None, "integrated_commit": None, "evidence_refs": [planner_ref],
        "pending_callback": {"state": "callback_pending", "action_id": ACTION_ID, "role": "Developer", "attempt": 1},
        "closeout_disposition": None, "retained_resource_refs": [], "close_decision_ref": None,
    }
    active = {
        "task_id": TASK_ID, "summary": "topology", "kind": "planned", "classification": "complex",
        "phase": "development", "scope_contract": {"may_touch": ["implementation.py"]},
        "plan_ref": plan_ref, "approval_ref": "approved", "activation_parent_sha": plan_commit,
        "activated_at": "2026-08-15T00:00:00Z", "updated_at": "2026-08-15T00:00:00Z",
        "blocker": None, "validation": None, "complex_context": context,
    }
    template.update(state="running", active=active)
    board_bytes = render_board("", template, suffix)
    (repo / "docs/task_board.md").write_bytes(board_bytes)
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "record Developer invocation")

    evidence_path = f"docs/lane_evidence/{TASK_ID}_developer.md"
    headers = {
        "TASK_ID": TASK_ID, "ROLE": "Developer", "STATUS": "ready", "SUBJECT": subject,
        "MODEL": ROUTE[0], "REASONING_EFFORT": ROUTE[1], "MODEL_ROUTE_REASON": ROUTE[2],
        "ACTION_ID": ACTION_ID, "ATTEMPT": "1",
    }
    headers.update(header_overrides or {})
    evidence = ("".join(f"{key}: {value}\n" for key, value in headers.items()) + "NEXT: Reviewer\nBLOCKER: none\n").encode()
    (repo / evidence_path).write_bytes(evidence)
    if mixed_evidence:
        (repo / "mixed.py").write_text("MIXED = True\n", encoding="utf-8")
        git(repo, "add", evidence_path, "mixed.py")
    else:
        git(repo, "add", evidence_path)
    git(repo, "commit", "-m", "evidence: Developer")
    evidence_commit = git(repo, "rev-parse", "HEAD")
    callback = {
        "schema": "connlab.serial-callback", "version": 1, "task_id": TASK_ID,
        "role": "Developer", "status": "ready", "subject_commit": subject,
        "evidence": f"{evidence_path}@{evidence_commit}#{hashlib.sha256(evidence).hexdigest()}",
        "next": "Reviewer", "blocker": None,
    }
    return repo, host, active, callback, evidence_path


def test_callback_accepts_primary_evidence_only_commit_and_stable_subject(tmp_path: Path) -> None:
    repo, host, active, callback, _ = fixture(tmp_path)

    verify_callback_evidence_topology(repo, active, callback)

    assert git(host, "rev-parse", "HEAD") == callback["subject_commit"]
    evidence_commit = callback["evidence"].split("@", 1)[1].split("#", 1)[0]
    assert subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", evidence_commit, callback["subject_commit"]],
        check=False,
    ).returncode == 1


def test_code_mixed_evidence_fails_before_authority_write(tmp_path: Path) -> None:
    repo, _, active, callback, _ = fixture(tmp_path, mixed_evidence=True)
    board_before = (repo / "docs/task_board.md").read_bytes()

    with pytest.raises(Blocked) as blocked:
        verify_callback_evidence_topology(repo, active, callback)

    assert blocked.value.code == "BLOCKED_EVIDENCE_INVALID"
    assert (repo / "docs/task_board.md").read_bytes() == board_before


@pytest.mark.parametrize(
    "header_overrides",
    ({"MODEL": "gpt-5.6-terra"}, {"ACTION_ID": "c" * 64}, {"ATTEMPT": "2"}, {"STATUS": "blocked"}),
)
def test_header_or_route_drift_fails_closed(tmp_path: Path, header_overrides: dict[str, str]) -> None:
    repo, _, active, callback, _ = fixture(tmp_path, header_overrides=header_overrides)
    board_before = (repo / "docs/task_board.md").read_bytes()

    with pytest.raises(Blocked) as blocked:
        verify_callback_evidence_topology(repo, active, callback)

    assert blocked.value.code == "BLOCKED_EVIDENCE_INVALID"
    assert (repo / "docs/task_board.md").read_bytes() == board_before


def test_integration_revalidates_dynamic_primary_evidence_history(tmp_path: Path) -> None:
    repo, _, active, callback, _ = fixture(tmp_path)
    accepted = copy.deepcopy(active)
    context = accepted["complex_context"]
    context["evidence_refs"].append(callback["evidence"])
    context["pending_callback"] = None
    context["current_role"] = None
    context["developer_subject_commit"] = callback["subject_commit"]
    context["reviewer_subject_commit"] = callback["subject_commit"]
    context["qa_subject_commit"] = callback["subject_commit"]
    context["worktree_lifecycle"] = "integration_ready"
    accepted["phase"] = "integration"
    prefix, control, suffix = parse_board((repo / "docs/task_board.md").read_bytes())
    control["active"] = accepted
    (repo / "docs/task_board.md").write_bytes(render_board(prefix, control, suffix))
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "consume Developer callback")
    primary_parent = git(repo, "rev-parse", "HEAD")
    git(repo, "merge", "--no-ff", "--no-edit", context["task_branch"])
    integration = {
        "subject_commit": callback["subject_commit"],
        "primary_parent": primary_parent,
        "evidence_refs": context["evidence_refs"],
    }

    verify_integration_evidence_topology(repo, accepted, integration)


def test_integration_rejects_unknown_primary_commit_without_writing(tmp_path: Path) -> None:
    repo, _, active, callback, _ = fixture(tmp_path)
    (repo / "unknown.txt").write_text("not authority\n", encoding="utf-8")
    git(repo, "add", "unknown.txt")
    git(repo, "commit", "-m", "unknown commit")
    accepted = copy.deepcopy(active)
    context = accepted["complex_context"]
    context.update(
        evidence_refs=[*context["evidence_refs"], callback["evidence"]],
        pending_callback=None, current_role=None,
        developer_subject_commit=callback["subject_commit"],
        reviewer_subject_commit=callback["subject_commit"],
        qa_subject_commit=callback["subject_commit"],
        worktree_lifecycle="integration_ready",
    )
    accepted["phase"] = "integration"
    prefix, control, suffix = parse_board((repo / "docs/task_board.md").read_bytes())
    control["active"] = accepted
    (repo / "docs/task_board.md").write_bytes(render_board(prefix, control, suffix))
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "consume Developer callback")
    primary_parent = git(repo, "rev-parse", "HEAD")
    git(repo, "merge", "--no-ff", "--no-edit", context["task_branch"])
    integration = {
        "subject_commit": callback["subject_commit"], "primary_parent": primary_parent,
        "evidence_refs": context["evidence_refs"],
    }
    board_before = (repo / "docs/task_board.md").read_bytes()

    with pytest.raises(Blocked) as blocked:
        verify_integration_evidence_topology(repo, accepted, integration)

    assert blocked.value.code == "BLOCKED_INTEGRATION_PROOF"
    assert (repo / "docs/task_board.md").read_bytes() == board_before


def test_canonical_complex_flow_reaches_verified_human_review(tmp_path: Path) -> None:
    repo, host = tmp_path / "formal-entry", tmp_path / "formal-entry-host"
    subject, integration = prepare_integration_ready(repo, host, task_id="TASK_FORMAL_TOPOLOGY")

    recorded = invoke_personal(
        repo,
        "record-integration",
        "--expected-board-sha256", board_hash(repo),
        "--task-id", "TASK_FORMAL_TOPOLOGY",
        "--integration-json", json.dumps(integration, separators=(",", ":")),
    )

    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    assert recorded["code"] == "ALLOW_RECORD_INTEGRATION"
    assert board["state"] == "implemented_pending_human_review"
    assert board["active"]["phase"] == "human_review"
    assert git(host, "rev-parse", "HEAD") == subject


@pytest.mark.parametrize(
    ("mutation", "code"),
    (
        ("header", "BLOCKED_EVIDENCE_INVALID"),
        ("wrong_digest", "BLOCKED_EVIDENCE_INVALID"),
        ("wrong_path", "BLOCKED_EVIDENCE_INVALID"),
        ("primary_dirty", "BLOCKED_WORKTREE_FACTS"),
        ("task_dirty", "BLOCKED_WORKTREE_FACTS"),
    ),
)
def test_callback_topology_drift_is_zero_write(tmp_path: Path, mutation: str, code: str) -> None:
    repo, host, active, callback, evidence_path = fixture(tmp_path)
    board_before = (repo / "docs/task_board.md").read_bytes()
    head_before = git(repo, "rev-parse", "HEAD")
    if mutation == "header":
        callback = dict(callback, subject_commit="f" * 40)
    elif mutation == "wrong_digest":
        callback = dict(callback, evidence=callback["evidence"].rsplit("#", 1)[0] + "#" + "f" * 64)
    elif mutation == "wrong_path":
        callback = dict(callback, evidence=callback["evidence"].replace(evidence_path, "docs/lane_evidence/wrong.md"))
    elif mutation == "primary_dirty":
        (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    else:
        (host / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    with pytest.raises(Blocked) as blocked:
        verify_callback_evidence_topology(repo, active, callback)

    assert blocked.value.code == code
    assert (repo / "docs/task_board.md").read_bytes() == board_before
    assert git(repo, "rev-parse", "HEAD") == head_before
    assert (evidence_path in callback["evidence"]) is (mutation != "wrong_path")
