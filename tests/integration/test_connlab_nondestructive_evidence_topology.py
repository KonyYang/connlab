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


def snapshot(repo: Path, host: Path) -> tuple[bytes, str, str, dict[str, bytes], dict[str, bytes]]:
    def files(root: Path) -> dict[str, bytes]:
        names = git(root, "ls-files", "--cached", "--others", "--exclude-standard").splitlines()
        return {name: (root / name).read_bytes() for name in names}

    return (
        (repo / "docs/task_board.md").read_bytes(),
        git(repo, "rev-parse", "HEAD"),
        git(host, "rev-parse", "HEAD"),
        files(repo),
        files(host),
    )


def fixture(
    tmp_path: Path,
    *,
    mixed_evidence: bool = False,
    header_overrides: dict[str, str] | None = None,
    planner_drift: str | None = None,
) -> tuple[Path, Path, dict, dict, str]:
    repo, host = tmp_path / "repo", tmp_path / "host"
    repo.mkdir()
    git(repo, "init", "-b", "master")
    git(repo, "config", "user.name", "Topology Test")
    git(repo, "config", "user.email", "topology@example.invalid")
    (repo / "docs").mkdir()
    (repo / "docs/lane_evidence").mkdir()
    plan_path = repo / f"docs/{TASK_ID.lower()}_plan.md"
    plan_bytes = (
        "# Plan\n\nDeveloper, Reviewer, QA and Integrator are all "
        "`gpt-5.6-sol / medium / risk:authority`.\n"
    ).encode()
    plan_path.write_bytes(plan_bytes)
    _, template, suffix = parse_board((ROOT / "docs/task_board.md").read_bytes())
    template.update(state="running", active=None, queue=[], next_enqueue_sequence=1)
    (repo / "docs/task_board.md").write_bytes(render_board("", template, suffix))
    git(repo, "add", str(plan_path.relative_to(repo)), "docs/task_board.md")
    git(repo, "commit", "-m", "fixture base")
    plan_commit = git(repo, "rev-parse", "HEAD")
    plan_ref = f"{plan_path.relative_to(repo).as_posix()}@{plan_commit}#{hashlib.sha256(plan_bytes).hexdigest()}"
    planner_path = repo / f"docs/lane_evidence/{TASK_ID}_planner.md"
    planner_bytes = f"TASK_ID: {TASK_ID}\nROLE: Planner\nSTATUS: ready\n".encode()
    planner_path.write_bytes(planner_bytes)
    git(repo, "add", str(planner_path.relative_to(repo)))
    git(repo, "commit", "-m", "evidence: Planner")
    planner_commit = git(repo, "rev-parse", "HEAD")
    planner_ref = (
        f"docs/lane_evidence/{TASK_ID}_planner.md@{planner_commit}#"
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
    task_path = repo / f"tasks/{TASK_ID}.md"
    task_path.parent.mkdir()
    task_path.write_text("# Revised Task\n", encoding="utf-8")
    plan_bytes += b"\nPlanner revision.\n"
    plan_path.write_bytes(plan_bytes)
    planner_path.write_bytes(planner_bytes + b"REVISION: bounded\n")
    if planner_drift == "extra_path":
        (repo / "extra.txt").write_text("extra\n", encoding="utf-8")
        git(repo, "add", "extra.txt")
    if planner_drift == "board_change":
        (repo / "docs/task_board.md").write_bytes((repo / "docs/task_board.md").read_bytes() + b"\n")
        git(repo, "add", "docs/task_board.md")
    git(repo, "add", str(task_path.relative_to(repo)), str(plan_path.relative_to(repo)), str(planner_path.relative_to(repo)))
    git(repo, "commit", "-m", "governance: revise Planner bundle")
    bundle_commit = git(repo, "rev-parse", "HEAD")
    bound_ref = f"{plan_path.relative_to(repo).as_posix()}@{bundle_commit}#{hashlib.sha256(plan_bytes).hexdigest()}"
    if planner_drift not in {"unbound", "later_descendant"}:
        active["plan_ref"] = bound_ref if planner_drift != "wrong_digest" else bound_ref[:-1] + ("0" if bound_ref.endswith("f") else "f")
    template.update(state="running", active=active)
    board_bytes = render_board("", template, suffix)
    (repo / "docs/task_board.md").write_bytes(board_bytes)
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "record Developer invocation")
    if planner_drift == "later_descendant":
        active["plan_ref"] = bound_ref
        template["active"] = active
        (repo / "docs/task_board.md").write_bytes(render_board("", template, suffix))
        git(repo, "add", "docs/task_board.md")
        git(repo, "commit", "-m", "late Planner binding")

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


def append_role(
    repo: Path,
    active: dict,
    accepted_callback: dict,
    *,
    role: str,
    attempt: int,
    action_id: str,
) -> tuple[dict, dict]:
    active = copy.deepcopy(active)
    context = active["complex_context"]
    context["evidence_refs"].append(accepted_callback["evidence"])
    context.update(pending_callback=None, current_role=None)
    prefix, control, suffix = parse_board((repo / "docs/task_board.md").read_bytes())
    control["active"] = active
    (repo / "docs/task_board.md").write_bytes(render_board(prefix, control, suffix))
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", f"consume {accepted_callback['role']} callback")

    invocation = {
        "schema": "connlab.serial-invocation", "version": 1,
        "action_id": action_id, "role": role, "attempt": attempt,
        "thread_id": None, "agent_id": f"agent-{role.lower()}-{attempt}",
        "host_id": context["host_id"], "status": "started",
        "recorded_at": f"2026-08-15T00:00:0{attempt}Z",
    }
    context["role_invocations"].append(invocation)
    context.update(
        current_role=role,
        current_attempt=attempt,
        pending_callback={
            "state": "callback_pending", "action_id": action_id,
            "role": role, "attempt": attempt,
        },
    )
    control["active"] = active
    (repo / "docs/task_board.md").write_bytes(render_board(prefix, control, suffix))
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", f"record {role} invocation {attempt}")

    subject = accepted_callback["subject_commit"]
    path = f"docs/lane_evidence/{TASK_ID}_{role.lower()}.md"
    data = (
        f"TASK_ID: {TASK_ID}\nROLE: {role}\nSTATUS: ready\nSUBJECT: {subject}\n"
        f"MODEL: {ROUTE[0]}\nREASONING_EFFORT: {ROUTE[1]}\nMODEL_ROUTE_REASON: {ROUTE[2]}\n"
        f"ACTION_ID: {action_id}\nATTEMPT: {attempt}\nNEXT: Developer\nBLOCKER: none\n"
    ).encode()
    (repo / path).write_bytes(data)
    if role == "Planner":
        (repo / "tasks").mkdir(exist_ok=True)
        (repo / "tasks/amendment.md").write_text("approved scope amendment\n", encoding="utf-8")
        git(repo, "add", path, "tasks/amendment.md")
    else:
        git(repo, "add", path)
    git(repo, "commit", "-m", f"evidence: {role} {attempt}")
    commit = git(repo, "rev-parse", "HEAD")
    callback = {
        "schema": "connlab.serial-callback", "version": 1, "task_id": TASK_ID,
        "role": role, "status": "ready", "subject_commit": subject,
        "evidence": f"{path}@{commit}#{hashlib.sha256(data).hexdigest()}",
        "next": "Developer", "blocker": None,
    }
    return active, callback


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
    repo, host, active, callback, _ = fixture(tmp_path, mixed_evidence=True)
    before = snapshot(repo, host)

    with pytest.raises(Blocked) as blocked:
        verify_callback_evidence_topology(repo, active, callback)

    assert blocked.value.code == "BLOCKED_EVIDENCE_INVALID"
    assert snapshot(repo, host) == before


def test_multiparent_evidence_fails_before_authority_write(tmp_path: Path) -> None:
    repo, host, active, callback, _ = fixture(tmp_path)
    evidence_commit = git(repo, "rev-parse", "HEAD")
    git(repo, "switch", "-c", "evidence-side", f"{evidence_commit}^")
    (repo / "side.txt").write_text("side\n", encoding="utf-8")
    git(repo, "add", "side.txt")
    git(repo, "commit", "-m", "side parent")
    git(repo, "switch", "master")
    git(repo, "merge", "--no-ff", "--no-edit", "evidence-side")
    merge_commit = git(repo, "rev-parse", "HEAD")
    path, digest = callback["evidence"].split("@", 1)[0], callback["evidence"].rsplit("#", 1)[1]
    callback = dict(callback, evidence=f"{path}@{merge_commit}#{digest}")
    before = snapshot(repo, host)

    with pytest.raises(Blocked) as blocked:
        verify_callback_evidence_topology(repo, active, callback)

    assert blocked.value.code == "BLOCKED_EVIDENCE_INVALID"
    assert snapshot(repo, host) == before


@pytest.mark.parametrize(
    "header_overrides",
    ({"MODEL": "gpt-5.6-terra"}, {"ACTION_ID": "c" * 64}, {"ATTEMPT": "2"}, {"STATUS": "blocked"}),
)
def test_header_or_route_drift_fails_closed(tmp_path: Path, header_overrides: dict[str, str]) -> None:
    repo, host, active, callback, _ = fixture(tmp_path, header_overrides=header_overrides)
    before = snapshot(repo, host)

    with pytest.raises(Blocked) as blocked:
        verify_callback_evidence_topology(repo, active, callback)

    assert blocked.value.code == "BLOCKED_EVIDENCE_INVALID"
    assert snapshot(repo, host) == before


@pytest.mark.parametrize("planner_drift", (None, "unbound", "wrong_digest", "extra_path", "board_change", "later_descendant"))
def test_integration_revalidates_dynamic_primary_evidence_history(
    tmp_path: Path, planner_drift: str | None,
) -> None:
    repo, _, active, callback, _ = fixture(tmp_path, planner_drift=planner_drift)
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

    if planner_drift is None:
        verify_integration_evidence_topology(repo, accepted, integration)
    else:
        with pytest.raises(Blocked):
            verify_integration_evidence_topology(repo, accepted, integration)


def test_integration_pairs_interleaved_planner_and_repeated_developer_callbacks(tmp_path: Path) -> None:
    repo, _, active, developer_one, _ = fixture(tmp_path)
    active, planner_two = append_role(
        repo, active, developer_one, role="Planner", attempt=2, action_id="c" * 64,
    )
    active, developer_two = append_role(
        repo, active, planner_two, role="Developer", attempt=2, action_id="d" * 64,
    )
    accepted = copy.deepcopy(active)
    context = accepted["complex_context"]
    context["evidence_refs"].append(developer_two["evidence"])
    context.update(
        pending_callback=None, current_role=None,
        developer_subject_commit=developer_two["subject_commit"],
        reviewer_subject_commit=developer_two["subject_commit"],
        qa_subject_commit=developer_two["subject_commit"],
        worktree_lifecycle="integration_ready",
    )
    accepted["phase"] = "integration"
    prefix, control, suffix = parse_board((repo / "docs/task_board.md").read_bytes())
    control["active"] = accepted
    (repo / "docs/task_board.md").write_bytes(render_board(prefix, control, suffix))
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "consume repeated Developer callback")
    primary_parent = git(repo, "rev-parse", "HEAD")

    verify_integration_evidence_topology(
        repo,
        accepted,
        {
            "subject_commit": developer_two["subject_commit"],
            "primary_parent": primary_parent,
            "evidence_refs": context["evidence_refs"],
        },
    )

    assert [item["role"] for item in context["role_invocations"]] == [
        "Planner", "Developer", "Planner", "Developer",
    ]
    drifted = list(context["evidence_refs"])
    drifted[1], drifted[2] = drifted[2], drifted[1]
    before = snapshot(repo, Path(context["task_worktree"]))
    with pytest.raises(Blocked):
        verify_integration_evidence_topology(
            repo, accepted,
            {"subject_commit": developer_two["subject_commit"], "primary_parent": primary_parent, "evidence_refs": drifted},
        )
    assert snapshot(repo, Path(context["task_worktree"])) == before


def test_integration_rejects_unknown_primary_commit_without_writing(tmp_path: Path) -> None:
    repo, host, active, callback, _ = fixture(tmp_path)
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
    before = snapshot(repo, host)

    with pytest.raises(Blocked) as blocked:
        verify_integration_evidence_topology(repo, accepted, integration)

    assert blocked.value.code == "BLOCKED_INTEGRATION_PROOF"
    assert snapshot(repo, host) == before


def test_canonical_complex_flow_reaches_verified_human_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger: list[tuple[str, ...]] = []
    original_run = subprocess.run

    def tracked_run(command, *args, **kwargs):
        if isinstance(command, list) and command and command[0] == "git":
            ledger.append(tuple(str(item) for item in command[1:]))
        return original_run(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", tracked_run)
    repo, host = tmp_path / "formal-entry", tmp_path / "formal-entry-host"
    subject, integration = prepare_integration_ready(repo, host, task_id="TASK_FORMAL_TOPOLOGY")
    _, integration_ready, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    verify_integration_evidence_topology(repo, integration_ready["active"], integration)

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
    commands = [" ".join(command).lower() for command in ledger]
    assert not any(
        token in command
        for command in commands
        for token in (" reset ", " restore ", " stash", " rebase", " cherry-pick", "worktree remove", "branch -d", "--force")
    )


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
    before = snapshot(repo, host)

    with pytest.raises(Blocked) as blocked:
        verify_callback_evidence_topology(repo, active, callback)

    assert blocked.value.code == code
    assert snapshot(repo, host) == before
    assert (evidence_path in callback["evidence"]) is (mutation != "wrong_path")
