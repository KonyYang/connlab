#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from scripts.connlab_serial_board import BOARD_REL, Blocked, git_dirty, parse_board, run_git


EXECUTION_ROLES = {"Developer", "Reviewer", "QA", "Integrator"}
EVIDENCE_RE = re.compile(
    r"(docs/lane_evidence/[A-Za-z0-9_./-]+)@([0-9a-f]{40})#([0-9a-f]{64})"
)
PLAN_RE = re.compile(r"([A-Za-z0-9_./-]+)@([0-9a-f]{40})#([0-9a-f]{64})")
HEADER_FIELDS = (
    "TASK_ID", "ROLE", "STATUS", "SUBJECT", "MODEL", "REASONING_EFFORT",
    "MODEL_ROUTE_REASON", "ACTION_ID", "ATTEMPT",
)


def _blocked(code: str, reason: str) -> None:
    raise Blocked(code, reason)


def _git_bytes(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=False
    )


def _ref(value: Any, *, code: str = "BLOCKED_EVIDENCE_INVALID") -> tuple[str, str, str]:
    match = EVIDENCE_RE.fullmatch(str(value))
    if not match or ".." in Path(match.group(1)).parts:
        _blocked(code, "Evidence reference is invalid.")
    return match.group(1), match.group(2), match.group(3)


def _committed_bytes(root: Path, commit: str, path: str, *, code: str) -> bytes:
    result = _git_bytes(root, "show", f"{commit}:{path}")
    if result.returncode != 0:
        _blocked(code, f"Committed path is unavailable: {path}.")
    return result.stdout


def _committed_plan_bytes(root: Path, plan_ref: Any, *, code: str) -> bytes:
    match = PLAN_RE.fullmatch(str(plan_ref))
    if not match or ".." in Path(match.group(1)).parts:
        _blocked(code, "Committed Plan reference is invalid.")
    path, commit, digest = match.groups()
    plan = _committed_bytes(root, commit, path, code=code)
    if hashlib.sha256(plan).hexdigest() != digest:
        _blocked(code, "Committed Plan bytes do not match its frozen reference.")
    return plan


def _route_from_plan_text(text: str, role: str, *, code: str) -> tuple[str, str, str]:
    shared = re.search(
        r"Developer,\s*Reviewer,\s*QA\s+and\s+Integrator\s+are\s+all\s+"
        r"`([^`/]+?)\s*/\s*([^`/]+?)\s*/\s*([^`]+?)`",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if shared:
        return tuple(item.strip() for item in shared.groups())  # type: ignore[return-value]
    row = re.search(
        rf"(?mi)^\|\s*{re.escape(role)}\s*\|\s*`?([^|`/]+?)\s*/\s*"
        r"([^|`/]+?)\s*/\s*([^|`]+?)`?\s*\|",
        text,
    )
    if row:
        return tuple(item.strip() for item in row.groups())  # type: ignore[return-value]
    _blocked(code, "Committed Plan does not freeze the execution-role route.")


def validate_approved_plan(
    root: Path, plan_ref: str, approved_request: dict[str, Any]
) -> dict[str, tuple[str, str, str]]:
    """Validate every machine-consumed Plan fact before approval can mutate the board."""
    code = "BLOCKED_PLAN_INVALID"
    plan = _committed_plan_bytes(root, plan_ref, code=code)
    try:
        text = plan.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        _blocked(code, "Committed Plan must be UTF-8 text.")
    embedded: list[dict[str, Any]] = []
    for raw in re.findall(r"```json\s*(\{.*?\})\s*```", text, re.IGNORECASE | re.DOTALL):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get("schema") == "connlab.personal-task-approved-request":
            embedded.append(value)
    if embedded != [approved_request]:
        _blocked(code, "Committed Plan must contain exactly the approved request object.")
    return {
        role: _route_from_plan_text(text, role, code=code)
        for role in sorted(EXECUTION_ROLES)
    }


def _plan_route(root: Path, active: dict[str, Any], role: str) -> tuple[str, str, str]:
    """Return the structured approved route, with a Plan fallback for legacy active tasks."""
    context = active.get("complex_context")
    routes = context.get("execution_routes") if isinstance(context, dict) else None
    if routes is not None:
        from scripts.connlab_serial_complex import SerialContractError, validate_execution_routes
        try:
            route = validate_execution_routes(routes)[role]
        except (KeyError, SerialContractError) as exc:
            _blocked("BLOCKED_EVIDENCE_INVALID", "Structured execution routes are invalid.")
        return route["model"], route["reasoning_effort"], route["reason"]
    plan = _committed_plan_bytes(
        root, active.get("plan_ref"), code="BLOCKED_EVIDENCE_INVALID"
    )
    try:
        text = plan.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        _blocked("BLOCKED_EVIDENCE_INVALID", "Committed Plan must be UTF-8 text.")
    return _route_from_plan_text(text, role, code="BLOCKED_EVIDENCE_INVALID")


def _headers(data: bytes) -> dict[str, str]:
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        _blocked("BLOCKED_EVIDENCE_INVALID", "Evidence must be UTF-8 text.")
    result: dict[str, str] = {}
    for field in HEADER_FIELDS:
        matches = re.findall(rf"(?m)^{field}:\s*(\S(?:.*\S)?)\s*$", text)
        if len(matches) != 1:
            _blocked("BLOCKED_EVIDENCE_INVALID", f"Evidence must contain exactly one {field} header.")
        result[field] = matches[0]
    return result


def _changed_paths(root: Path, parent: str, commit: str) -> list[str]:
    result = run_git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", parent, commit)
    if result.returncode != 0:
        _blocked("BLOCKED_EVIDENCE_INVALID", "Evidence commit diff cannot be inspected.")
    return [line for line in result.stdout.splitlines() if line]


def _single_parent(root: Path, commit: str) -> str:
    result = run_git(root, "rev-list", "--parents", "-n", "1", commit)
    parts = result.stdout.strip().split() if result.returncode == 0 else []
    if len(parts) != 2 or parts[0] != commit:
        _blocked("BLOCKED_EVIDENCE_INVALID", "Evidence commit must have exactly one parent.")
    return parts[1]


def _planner_paths(active: dict[str, Any]) -> tuple[str, str, str]:
    task_id = active["task_id"]
    return (
        f"tasks/{task_id}.md",
        f"docs/{task_id.lower()}_plan.md",
        f"docs/lane_evidence/{task_id}_planner.md",
    )


def _planner_revision_bundle(
    root: Path,
    active: dict[str, Any],
    commit: str,
    following_commit: str | None,
) -> bool:
    task_path, plan_path, planner_path = _planner_paths(active)
    parent = _single_parent(root, commit)
    if _changed_paths(root, parent, commit) != sorted((task_path, plan_path, planner_path)):
        return False
    if _committed_bytes(root, commit, BOARD_REL, code="BLOCKED_INTEGRATION_PROOF") != _committed_bytes(
        root, parent, BOARD_REL, code="BLOCKED_INTEGRATION_PROOF"
    ):
        return False
    if following_commit is None or _single_parent(root, following_commit) != commit:
        return False
    if _changed_paths(root, commit, following_commit) != [BOARD_REL]:
        return False
    plan = _committed_bytes(root, commit, plan_path, code="BLOCKED_INTEGRATION_PROOF")
    expected_ref = f"{plan_path}@{commit}#{hashlib.sha256(plan).hexdigest()}"
    authority_board = _committed_bytes(
        root, following_commit, BOARD_REL, code="BLOCKED_INTEGRATION_PROOF"
    )
    try:
        _, control, _ = parse_board(authority_board)
        authority_active = control["active"]
    except (KeyError, TypeError, ValueError):
        return False
    return (
        isinstance(authority_active, dict)
        and authority_active.get("task_id") == active.get("task_id")
        and authority_active.get("plan_ref") == expected_ref
    )


def _invocation_board(
    root: Path, parent: str, active: dict[str, Any], invocation: dict[str, Any]
) -> bytes:
    board = _committed_bytes(root, parent, BOARD_REL, code="BLOCKED_CALLBACK_INVALID")
    try:
        _, control, _ = parse_board(board)
        parent_active = control["active"]
        context = parent_active["complex_context"]
    except (KeyError, TypeError, ValueError) as exc:
        _blocked("BLOCKED_CALLBACK_INVALID", f"Evidence parent board is invalid: {exc}.")
    pending = context.get("pending_callback")
    identity = (invocation["action_id"], invocation["role"], invocation["attempt"])
    if (
        parent_active.get("task_id") != active.get("task_id")
        or not isinstance(pending, dict)
        or pending.get("state") != "callback_pending"
        or (pending.get("action_id"), pending.get("role"), pending.get("attempt")) != identity
        or not context.get("role_invocations")
        or context["role_invocations"][-1] != invocation
    ):
        _blocked("BLOCKED_CALLBACK_INVALID", "Evidence parent is not the matching record-invocation state.")
    grandparent = _single_parent(root, parent)
    if _changed_paths(root, grandparent, parent) != [BOARD_REL]:
        _blocked("BLOCKED_CALLBACK_INVALID", "Evidence parent is not a board-only authority commit.")
    return board


def _worktree_matches(root: Path, active: dict[str, Any], subject: str) -> None:
    context = active["complex_context"]
    worktree = Path(context["task_worktree"]).resolve()
    records = run_git(root, "worktree", "list", "--porcelain").stdout.strip().split("\n\n")
    record = next(
        (item for item in records if item.splitlines() and Path(item.splitlines()[0][9:]).resolve() == worktree),
        None,
    )
    lines = set(record.splitlines()) if record else set()
    if (
        not record
        or f"HEAD {subject}" not in lines
        or f"branch refs/heads/{context['task_branch']}" not in lines
        or run_git(worktree, "rev-parse", "HEAD").stdout.strip() != subject
        or bool(run_git(worktree, "status", "--porcelain=v1", "--untracked-files=all").stdout)
    ):
        _blocked("BLOCKED_WORKTREE_FACTS", "Task worktree branch, subject or clean state drifted.")


def _verify_execution_evidence(
    root: Path,
    active: dict[str, Any],
    evidence_ref: str,
    invocation: dict[str, Any],
    *,
    callback: dict[str, Any] | None = None,
    require_head: bool = False,
) -> tuple[str, str]:
    role = invocation.get("role")
    if role not in EXECUTION_ROLES:
        _blocked("BLOCKED_CALLBACK_INVALID", "Evidence does not bind an execution-role invocation.")
    path, commit, digest = _ref(evidence_ref, code="BLOCKED_CALLBACK_INVALID")
    expected_path = f"docs/lane_evidence/{active['task_id']}_{role.lower()}.md"
    if path != expected_path:
        _blocked("BLOCKED_EVIDENCE_INVALID", "Evidence path does not match the Task-derived role path.")
    if require_head and run_git(root, "rev-parse", "HEAD").stdout.strip() != commit:
        _blocked("BLOCKED_CALLBACK_INVALID", "Primary HEAD is not the supplied evidence commit.")
    parent = _single_parent(root, commit)
    if _changed_paths(root, parent, commit) != [path]:
        _blocked("BLOCKED_EVIDENCE_INVALID", "Evidence commit must change exactly its fixed evidence path.")
    parent_board = _invocation_board(root, parent, active, invocation)
    if _committed_bytes(root, commit, BOARD_REL, code="BLOCKED_CALLBACK_INVALID") != parent_board:
        _blocked("BLOCKED_CALLBACK_INVALID", "Evidence commit changed the authority board bytes.")
    data = _committed_bytes(root, commit, path, code="BLOCKED_EVIDENCE_INVALID")
    if hashlib.sha256(data).hexdigest() != digest:
        _blocked("BLOCKED_EVIDENCE_INVALID", "Evidence bytes do not match the supplied SHA-256.")
    headers = _headers(data)
    expected = {
        "TASK_ID": active["task_id"], "ROLE": role,
        "ACTION_ID": invocation["action_id"], "ATTEMPT": str(invocation["attempt"]),
    }
    if callback is not None:
        expected.update(STATUS=callback["status"], SUBJECT=callback["subject_commit"])
    route = _plan_route(root, active, role)
    expected.update(MODEL=route[0], REASONING_EFFORT=route[1], MODEL_ROUTE_REASON=route[2])
    if any(headers.get(key) != value for key, value in expected.items()):
        _blocked("BLOCKED_EVIDENCE_INVALID", "Evidence identity, callback or frozen model route drifted.")
    subject = headers["SUBJECT"]
    if not re.fullmatch(r"[0-9a-f]{40}", subject):
        _blocked("BLOCKED_SUBJECT_MISMATCH", "Evidence subject is not a commit identity.")
    if run_git(root, "merge-base", "--is-ancestor", commit, subject).returncode == 0:
        _blocked("BLOCKED_SUBJECT_MISMATCH", "Execution evidence entered task-subject ancestry.")
    return commit, subject


def verify_callback_evidence_topology(
    root: Path, active: dict[str, Any], callback: dict[str, Any]
) -> None:
    if not isinstance(callback, dict):
        _blocked("BLOCKED_CALLBACK_INVALID", "Callback must be an object.")
    if callback.get("role") not in EXECUTION_ROLES:
        return
    _plan_route(root, active, callback["role"])
    if git_dirty(root):
        _blocked("BLOCKED_WORKTREE_FACTS", "Primary must be clean at callback verification.")
    context = active["complex_context"]
    pending = context.get("pending_callback")
    invocations = context.get("role_invocations", [])
    if not isinstance(pending, dict) or not invocations:
        _blocked("BLOCKED_CALLBACK_INVALID", "Callback has no durable invocation.")
    invocation = invocations[-1]
    identity = (invocation.get("action_id"), invocation.get("role"), invocation.get("attempt"))
    if identity != (pending.get("action_id"), pending.get("role"), pending.get("attempt")):
        _blocked("BLOCKED_CALLBACK_INVALID", "Callback invocation identity drifted.")
    _, subject = _verify_execution_evidence(
        root, active, callback["evidence"], invocation, callback=callback, require_head=True
    )
    if subject != callback["subject_commit"]:
        _blocked("BLOCKED_SUBJECT_MISMATCH", "Evidence and callback subjects differ.")
    _worktree_matches(root, active, callback["subject_commit"])


def verify_integration_evidence_topology(
    root: Path, active: dict[str, Any], integration: dict[str, Any]
) -> None:
    role_invocations = active["complex_context"].get("role_invocations", [])
    evidence_refs = integration.get("evidence_refs", [])
    if not role_invocations:
        return
    if len(evidence_refs) != len(role_invocations):
        _blocked("BLOCKED_INTEGRATION_PROOF", "Evidence does not map one-to-one to durable invocations.")
    commits: list[str] = []
    evidence_paths: list[str] = []
    for evidence_ref, invocation in zip(evidence_refs, role_invocations, strict=True):
        path, commit, digest = _ref(evidence_ref)
        if invocation.get("role") in EXECUTION_ROLES:
            commit, _ = _verify_execution_evidence(root, active, evidence_ref, invocation)
        elif invocation.get("role") != "Planner":
            _blocked("BLOCKED_INTEGRATION_PROOF", "Evidence binds an unknown callback role.")
        else:
            planner_path = _planner_paths(active)[2]
            if path != planner_path:
                _blocked("BLOCKED_EVIDENCE_INVALID", "Planner evidence path does not match the Task-derived path.")
            if hashlib.sha256(
                _committed_bytes(root, commit, path, code="BLOCKED_EVIDENCE_INVALID")
            ).hexdigest() != digest:
                _blocked("BLOCKED_EVIDENCE_INVALID", "Planner evidence bytes do not match the supplied SHA-256.")
        if run_git(root, "merge-base", "--is-ancestor", commit, integration["primary_parent"]).returncode != 0:
            _blocked("BLOCKED_INTEGRATION_PROOF", "Callback evidence is outside the accepted primary ancestry.")
        commits.append(commit)
        evidence_paths.append(path)
    if any(
        run_git(root, "merge-base", "--is-ancestor", older, newer).returncode != 0
        for older, newer in zip(commits, commits[1:])
    ):
        _blocked("BLOCKED_INTEGRATION_PROOF", "Evidence order differs from durable invocation order.")
    start = _single_parent(root, commits[0])
    history = run_git(root, "rev-list", "--first-parent", "--reverse", f"{start}..{integration['primary_parent']}")
    if history.returncode != 0:
        _blocked("BLOCKED_INTEGRATION_PROOF", "Primary evidence history cannot be inspected.")
    evidence_by_commit = {
        commit: (path, invocation["role"])
        for commit, path, invocation in zip(commits, evidence_paths, role_invocations, strict=True)
    }
    history_commits = history.stdout.splitlines()
    for index, commit in enumerate(history_commits):
        parent = _single_parent(root, commit)
        evidence = evidence_by_commit.get(commit)
        if evidence is not None and evidence[1] == "Planner":
            continue
        if evidence is None and _planner_revision_bundle(
            root,
            active,
            commit,
            history_commits[index + 1] if index + 1 < len(history_commits) else None,
        ):
            continue
        expected = [evidence[0]] if evidence is not None else [BOARD_REL]
        if _changed_paths(root, parent, commit) != expected:
            _blocked("BLOCKED_INTEGRATION_PROOF", "Primary history contains an unknown or code-mixed commit.")
    _worktree_matches(root, active, integration["subject_commit"])
