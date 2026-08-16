#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

from scripts.connlab_serial_complex import (
    ACTION_ROLES,
    SerialContractError,
    validate_complex_blocker,
    validate_native_action,
)
from scripts.connlab_serial_board import Blocked, committed_board, git_dirty, run_git


BOUNDED_FIX_CODES = {"REVIEWER_BLOCKED", "QA_BLOCKED", "INTEGRATION_BLOCKED"}
COMMAND_ARGUMENTS = {
    "inspect": set(),
    "check": {"task_id", "intent"},
    "classify": {"request_json"},
    "submit": {"expected_board_sha256", "task_id", "request_json"},
    "activate-next": {"expected_board_sha256", "task_id"},
    "approve": {"expected_board_sha256", "task_id", "approved_request_json", "plan_ref", "approval_ref"},
    "amend-plan": {"expected_board_sha256", "task_id", "plan_ref", "approval_ref", "callback_json"},
    "mark-review": {"expected_board_sha256", "task_id", "validation_json"},
    "block": {"expected_board_sha256", "task_id", "blocker_json"},
    "resume": {"expected_board_sha256", "task_id", "decision_ref"},
    "cancel": {"expected_board_sha256", "task_id", "decision_ref", "disposition"},
    "close": {"expected_board_sha256", "task_id", "decision_ref"},
    "begin-role": {"expected_board_sha256", "task_id", "role", "native_action_json"},
    "record-invocation": {"expected_board_sha256", "task_id", "role", "native_action_id", "invocation_json"},
    "consume-callback": {"expected_board_sha256", "task_id", "callback_json"},
    "begin-host": {"expected_board_sha256", "task_id", "native_action_json"},
    "record-host": {"expected_board_sha256", "task_id", "native_action_id", "worktree_json"},
    "record-integration": {"expected_board_sha256", "task_id", "integration_json"},
    "request-close": {"expected_board_sha256", "task_id", "decision_ref"},
    "record-closeout": {"expected_board_sha256", "task_id", "closeout_json"},
    "finalize-close": {"expected_board_sha256", "task_id", "decision_ref"},
    "reenter-development": {"expected_board_sha256", "task_id", "decision_ref", "native_action_json"},
}
COMMAND_JSON_SCHEMAS = {
    "submit": {"request_json": "connlab.serial-task-request/v1"},
    "approve": {"approved_request_json": "connlab.personal-task-approved-request/v1"},
    "amend-plan": {"callback_json": "connlab.serial-callback/v1"},
    "mark-review": {"validation_json": "connlab.personal-task-validation/v1"},
    "block": {"blocker_json": "connlab.serial-task-blocker/v1"},
    "begin-role": {"native_action_json": "connlab.serial-native-action/v1"},
    "record-invocation": {"invocation_json": "connlab.serial-invocation/v1"},
    "consume-callback": {"callback_json": "connlab.serial-callback/v1"},
    "begin-host": {"native_action_json": "connlab.serial-native-action/v1"},
    "record-host": {"worktree_json": "connlab.serial-worktree/v1"},
    "record-integration": {"integration_json": "connlab.serial-integration/v1"},
    "record-closeout": {"closeout_json": "connlab.serial-closeout/v1"},
    "reenter-development": {"native_action_json": "connlab.serial-native-action/v1"},
}
SUBJECT_BY_BLOCKER = {
    "REVIEWER_BLOCKED": "developer_subject_commit",
    "QA_BLOCKED": "reviewer_subject_commit",
    "INTEGRATION_BLOCKED": "qa_subject_commit",
}


def command_contract(command: str) -> dict[str, Any]:
    accepted = COMMAND_ARGUMENTS.get(command)
    if accepted is None:
        _fail("BLOCKED_ARGUMENT_COMBINATION", "Unknown writer command contract.")
    return {
        "accepted_arguments": sorted(accepted),
        "json_schemas": dict(COMMAND_JSON_SCHEMAS.get(command, {})),
    }


def _fail(code: str, reason: str) -> None:
    raise SerialContractError(code, reason)


def _complex_context(active: dict[str, Any]) -> dict[str, Any]:
    context = active.get("complex_context")
    if not isinstance(context, dict):
        _fail("BLOCKED_STATE", "A durable complex context is required.")
    return context


def _record_resolution(
    context: dict[str, Any],
    blocker: dict[str, Any],
    decision_ref: str,
    resolution: str,
    resolved_at: str,
) -> None:
    history = context.setdefault("blocker_history", [])
    if not isinstance(history, list):
        _fail("BLOCKED_SCHEMA_INVALID", "Durable blocker history is missing.")
    history.append({
        "blocker": json.loads(json.dumps(blocker)),
        "decision_ref": decision_ref,
        "resolution": resolution,
        "resolved_at": resolved_at,
    })


def build_native_action(
    active: dict[str, Any],
    action_name: str,
    prompt_bytes: bytes,
    title: str,
    recorded_at: str,
) -> dict[str, Any]:
    context = _complex_context(active)
    role = ACTION_ROLES.get(action_name)
    if role is None or not prompt_bytes or not title.strip() or not recorded_at:
        _fail("BLOCKED_ARGUMENT_COMBINATION", "Native action inputs are incomplete.")
    blocker = active.get("blocker")
    blocker_code = blocker.get("code") if isinstance(blocker, dict) else None
    phase = active.get("phase")
    expected_action = {
        "planning": "planner_dispatch",
        "review": "reviewer_dispatch",
        "qa": "qa_dispatch",
        "integration": "integrator_dispatch",
    }.get(phase)
    if phase == "development":
        expected_action = "developer_dispatch" if context.get("host_id") else "host_create"
    if blocker_code in BOUNDED_FIX_CODES:
        expected_action = "developer_dispatch"
    if action_name != expected_action:
        _fail("BLOCKED_ROLE_ORDER", "Native action does not match the durable next phase.")
    current_attempt = context.get("current_attempt", 0)
    if action_name == "planner_dispatch" or (
        action_name == "developer_dispatch" and blocker_code in BOUNDED_FIX_CODES
    ):
        attempt = current_attempt + 1
    else:
        attempt = max(current_attempt, 1)
    prompt_sha = hashlib.sha256(prompt_bytes).hexdigest()
    identity = {
        "task_id": active.get("task_id"),
        "action": action_name,
        "role": role,
        "attempt": attempt,
        "prompt_sha256": prompt_sha,
        "title": title,
        "plan_ref": active.get("plan_ref"),
        "approval_ref": active.get("approval_ref"),
        "host_id": context.get("host_id"),
        "head_sha": context.get("head_sha"),
    }
    action_id = hashlib.sha256(
        json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "schema": "connlab.serial-native-action",
        "version": 1,
        "action_id": action_id,
        "action": action_name,
        "role": role,
        "attempt": attempt,
        "prompt_sha256": prompt_sha,
        "title": title,
        "recorded_at": recorded_at,
    }


def apply_bounded_fix_reentry(
    active: dict[str, Any],
    native_action: dict[str, Any],
    decision_ref: str,
    timestamp: str,
) -> None:
    context = _complex_context(active)
    blocker = active.get("blocker")
    if not isinstance(blocker, dict):
        _fail("BLOCKED_STATE", "A typed bounded-fix blocker is required.")
    blocker = validate_complex_blocker(blocker)
    code = blocker["code"]
    if code not in BOUNDED_FIX_CODES or active.get("phase") not in {"blocked", "development"}:
        _fail("BLOCKED_STATE", "The blocker is not eligible for bounded-fix reentry.")
    if not isinstance(decision_ref, str) or not decision_ref.strip():
        _fail("BLOCKED_STATE", "A durable bounded-fix decision reference is required.")
    if code in {"REVIEWER_BLOCKED", "QA_BLOCKED"} and decision_ref != active.get("approval_ref"):
        _fail("BLOCKED_APPROVAL_REQUIRED", "Reviewer/QA bounded fixes must reuse the existing User approval reference.")
    scope = active.get("scope_contract")
    if (
        not isinstance(scope, dict)
        or scope.get("may_touch") != context.get("approved_code_paths")
        or not active.get("plan_ref")
        or not active.get("approval_ref")
    ):
        _fail("BLOCKED_APPROVED_SCOPE_INVALID", "Approved scope or approval identity drifted.")
    identity_fields = ("host_thread_id", "host_id", "task_branch", "task_worktree", "base_sha", "head_sha")
    if any(not isinstance(context.get(key), str) or not context[key] for key in identity_fields):
        _fail("BLOCKED_HOST_REQUIRED", "The exact recorded host identity is incomplete.")
    if context.get("pending_callback") is not None or context.get("current_role") is not None:
        _fail("BLOCKED_NATIVE_ACTION_PENDING", "A role or callback is already active.")
    expected_subject = context.get(SUBJECT_BY_BLOCKER[code])
    if blocker.get("subject_commit") != expected_subject:
        _fail("BLOCKED_SUBJECT_MISMATCH", "Blocker subject differs from the durable exact subject.")
    action = validate_native_action(native_action)
    expected_attempt = context.get("current_attempt") + 1
    if (
        action["action"] != "developer_dispatch"
        or action["role"] != "Developer"
        or action["attempt"] != expected_attempt
    ):
        _fail("BLOCKED_NATIVE_ID_MISMATCH", "Developer action does not bind the next durable attempt.")
    invocations = context.get("role_invocations")
    if not isinstance(invocations, list) or any(not isinstance(item, dict) for item in invocations):
        _fail("BLOCKED_SCHEMA_INVALID", "Durable role invocation history is invalid.")
    if any(item.get("action_id") == action["action_id"] for item in invocations):
        _fail("BLOCKED_NATIVE_ID_MISMATCH", "Developer action identity was already invoked.")

    _record_resolution(context, blocker, decision_ref, "bounded_fix", timestamp)
    active.update(phase="development", blocker=None, updated_at=timestamp)
    context.update(
        current_role="Developer",
        current_attempt=expected_attempt,
        pending_callback={
            "state": "dispatch_pending",
            "action_id": action["action_id"],
            "role": "Developer",
            "attempt": expected_attempt,
        },
    )


def apply_scope_amendment(
    active: dict[str, Any],
    approved: dict[str, Any],
    scope: dict[str, Any],
    plan_ref: str,
    approval_ref: str,
    timestamp: str,
) -> None:
    context = _complex_context(active)
    blocker = active.get("blocker")
    if active.get("phase") != "blocked" or not isinstance(blocker, dict):
        _fail("BLOCKED_STATE", "A blocked scope amendment is required.")
    blocker = validate_complex_blocker(blocker)
    if blocker["code"] != "SCOPE_EXPANDED":
        _fail("BLOCKED_APPROVED_SCOPE_INVALID", "Only SCOPE_EXPANDED permits an amendment.")
    previous = active.get("scope_contract")
    if not isinstance(previous, dict):
        _fail("BLOCKED_APPROVED_SCOPE_INVALID", "Previous approved scope is missing.")
    if previous.get("may_touch") != context.get("approved_code_paths"):
        _fail("BLOCKED_APPROVED_SCOPE_INVALID", "Stored approved code paths drifted before amendment.")
    old_paths, new_paths = set(previous.get("may_touch", [])), set(scope.get("may_touch", []))
    if not old_paths < new_paths:
        _fail("BLOCKED_APPROVED_SCOPE_INVALID", "A scope amendment must be a strict path superset.")
    if scope.get("forbidden_categories") != previous.get("forbidden_categories"):
        _fail("BLOCKED_APPROVED_SCOPE_INVALID", "A scope amendment cannot change risk-category facts.")
    if context.get("pending_callback") is not None or context.get("current_role") is not None:
        _fail("BLOCKED_NATIVE_ACTION_PENDING", "A role or callback is already active.")
    if not all(isinstance(value, str) and value.strip() for value in (plan_ref, approval_ref)):
        _fail("BLOCKED_APPROVAL_REQUIRED", "Amended Plan and User approval references are required.")

    _record_resolution(context, blocker, approval_ref, "scope_amendment", timestamp)
    active.update(
        summary=approved["summary"],
        scope_contract=scope,
        plan_ref=plan_ref,
        approval_ref=approval_ref,
        blocker=None,
        phase="development",
        updated_at=timestamp,
    )
    context["approved_code_paths"] = list(scope["may_touch"])


def apply_exact_plan_amendment(
    active: dict[str, Any],
    plan_ref: str,
    approval_ref: str,
    callback: dict[str, Any],
    execution_routes: dict[str, dict[str, str]],
    timestamp: str,
) -> None:
    context = _complex_context(active)
    pending = context.get("pending_callback")
    if active.get("blocker") is not None or active.get("phase") not in {"development", "review", "qa", "integration"}:
        _fail("BLOCKED_STATE", "Exact Plan amendment requires an unblocked execution phase.")
    if not isinstance(pending, dict) or pending.get("state") != "callback_pending":
        _fail("BLOCKED_CALLBACK_PENDING", "Exact Plan amendment requires the existing pending callback.")
    if callback.get("role") != pending.get("role"):
        _fail("BLOCKED_CALLBACK_INVALID", "Plan amendment callback role differs from the pending action.")
    identity = (pending.get("action_id"), pending.get("role"), pending.get("attempt"))
    invocations = context.get("role_invocations")
    invocation = invocations[-1] if isinstance(invocations, list) and invocations else None
    if not isinstance(invocation, dict) or identity != (
        invocation.get("action_id"), invocation.get("role"), invocation.get("attempt")
    ):
        _fail("BLOCKED_CALLBACK_INVALID", "Plan amendment invocation identity drifted.")
    old_plan_ref = active.get("plan_ref")
    old_approval_ref = active.get("approval_ref")
    if not all(isinstance(value, str) and value.strip() for value in (
        old_plan_ref, old_approval_ref, plan_ref, approval_ref,
    )) or old_plan_ref == plan_ref:
        _fail("BLOCKED_PLAN_INVALID", "Exact old/new Plan and approval references are required.")
    history = context.setdefault("plan_amendments", [])
    if not isinstance(history, list):
        _fail("BLOCKED_SCHEMA_INVALID", "Plan amendment history is invalid.")
    if any(item.get("new_plan_ref") == plan_ref for item in history if isinstance(item, dict)):
        _fail("BLOCKED_PLAN_INVALID", "The corrected Plan reference was already applied.")
    history.append({
        "old_plan_ref": old_plan_ref,
        "new_plan_ref": plan_ref,
        "old_approval_ref": old_approval_ref,
        "approval_ref": approval_ref,
        "evidence_ref": callback["evidence"],
        "action_id": pending["action_id"],
        "role": pending["role"],
        "attempt": pending["attempt"],
        "amended_at": timestamp,
    })
    active.update(plan_ref=plan_ref, approval_ref=approval_ref, updated_at=timestamp)
    context["execution_routes"] = execution_routes


def verify_transition_repository(root: Path, active: dict[str, Any], *, require_host: bool) -> None:
    if not committed_board(root):
        raise Blocked("BLOCKED_TRANSITION_UNCOMMITTED", "The blocker transition must be committed first.")
    if git_dirty(root):
        raise Blocked("BLOCKED_WORKTREE_DIRTY", "Primary must be clean before a recovery transition.")
    context = _complex_context(active)
    if not context.get("host_id"):
        if require_host:
            raise Blocked("BLOCKED_HOST_REQUIRED", "A recorded task host is required for bounded-fix reentry.")
        return
    worktree_value = context.get("task_worktree")
    if not isinstance(worktree_value, str) or not worktree_value:
        raise Blocked("BLOCKED_WORKTREE_FACTS", "Recorded task worktree is missing.")
    worktree = Path(worktree_value).resolve()
    records = run_git(root, "worktree", "list", "--porcelain").stdout.strip().split("\n\n")
    record = next(
        (item for item in records if item.splitlines() and Path(item.splitlines()[0][9:]).resolve() == worktree),
        None,
    )
    lines = set(record.splitlines()) if record else set()
    expected_head = context.get("head_sha")
    expected_branch = context.get("task_branch")
    if (
        not record
        or f"HEAD {expected_head}" not in lines
        or f"branch refs/heads/{expected_branch}" not in lines
        or run_git(worktree, "rev-parse", "HEAD").stdout.strip() != expected_head
        or run_git(worktree, "branch", "--show-current").stdout.strip() != expected_branch
        or bool(run_git(worktree, "status", "--porcelain=v1", "--untracked-files=all").stdout)
    ):
        raise Blocked("BLOCKED_WORKTREE_FACTS", "Recorded host branch, HEAD, or cleanliness drifted.")


def active_snapshot(control: dict[str, Any] | None, primary_head: str | None = None) -> dict[str, Any] | None:
    active = control.get("active") if isinstance(control, dict) else None
    if not isinstance(active, dict):
        return None
    context = active.get("complex_context")
    context = context if isinstance(context, dict) else {}
    pending = context.get("pending_callback")
    pending = pending if isinstance(pending, dict) else {}
    blocker = active.get("blocker")
    blocker = blocker if isinstance(blocker, dict) else {}
    history = context.get("blocker_history")
    evidence = context.get("evidence_refs")
    scope = active.get("scope_contract")
    approved_paths = context.get("approved_code_paths")
    validation_manifest = context.get("validation_manifest")
    if approved_paths is None and isinstance(scope, dict):
        approved_paths = scope.get("may_touch")
    return {
        "task_id": active.get("task_id"),
        "phase": active.get("phase"),
        "classification": active.get("classification", active.get("kind")),
        "plan_ref": active.get("plan_ref"),
        "approval_ref": active.get("approval_ref"),
        "primary_head": primary_head,
        "approved_base_sha": context.get("base_sha", active.get("activation_parent_sha")),
        "task_branch": context.get("task_branch"),
        "task_worktree": context.get("task_worktree"),
        "head_sha": context.get("head_sha"),
        "host_thread_id": context.get("host_thread_id"),
        "host_id": context.get("host_id"),
        "current_role": context.get("current_role"),
        "current_attempt": context.get("current_attempt"),
        "pending_action_id": pending.get("action_id"),
        "pending_state": pending.get("state"),
        "blocker_code": blocker.get("code"),
        "approved_code_paths": approved_paths or [],
        "execution_routes": context.get("execution_routes"),
        "plan_amendment_count": len(context.get("plan_amendments", [])) if isinstance(context.get("plan_amendments", []), list) else 0,
        "validation_check_ids": [
            check.get("id") for check in validation_manifest.get("checks", []) if isinstance(check, dict)
        ] if isinstance(validation_manifest, dict) else [],
        "validation_permissions": {
            role: sorted({
                check.get("permission")
                for check in validation_manifest.get("checks", [])
                if isinstance(check, dict) and role in check.get("run_for", [])
            })
            for role in ("Developer", "Reviewer", "QA", "Integrator")
        } if isinstance(validation_manifest, dict) else {},
        "developer_subject_commit": context.get("developer_subject_commit"),
        "reviewer_subject_commit": context.get("reviewer_subject_commit"),
        "qa_subject_commit": context.get("qa_subject_commit"),
        "evidence_count": len(evidence) if isinstance(evidence, list) else 0,
        "blocker_history_count": len(history) if isinstance(history, list) else 0,
    }


def next_action(control: dict[str, Any] | None) -> dict[str, Any]:
    active = control.get("active") if isinstance(control, dict) else None
    if not isinstance(active, dict):
        return {"command": "submit", "role": "User", "requires_user": True}
    context = active.get("complex_context")
    context = context if isinstance(context, dict) else {}
    pending = context.get("pending_callback")
    if isinstance(pending, dict):
        command = {
            "dispatch_pending": "record-invocation",
            "callback_pending": "consume-callback",
            "host_creation_pending": "record-host",
        }.get(pending.get("state"), "inspect")
        return {"command": command, "role": pending.get("role"), "requires_user": False}
    blocker = active.get("blocker")
    blocker_code = blocker.get("code") if isinstance(blocker, dict) else None
    if blocker_code in BOUNDED_FIX_CODES:
        return {"command": "reenter-development", "role": "Developer", "requires_user": blocker_code == "INTEGRATION_BLOCKED"}
    if blocker_code == "SCOPE_EXPANDED":
        return {"command": "approve", "role": "User", "requires_user": True}
    if blocker_code:
        return {"command": "resume", "role": "User", "requires_user": True}
    phase = active.get("phase")
    if phase == "planning":
        return {"command": "begin-role", "role": "Planner", "requires_user": False}
    if phase == "awaiting_user_approval":
        return {"command": "approve", "role": "User", "requires_user": True}
    if phase == "development" and not context.get("host_id"):
        return {"command": "begin-host", "role": "Host", "requires_user": False}
    role = {"development": "Developer", "review": "Reviewer", "qa": "QA", "integration": "Integrator"}.get(phase)
    if role:
        command = "record-integration" if phase == "integration" and context.get("worktree_lifecycle") == "integration_ready" else "begin-role"
        return {"command": command, "role": role, "requires_user": False}
    if phase == "human_review":
        return {"command": "close", "role": "User", "requires_user": True}
    if phase == "closing":
        command = "finalize-close" if context.get("worktree_lifecycle") == "retained" else "record-closeout"
        return {"command": command, "role": "Integrator", "requires_user": False}
    return {"command": "inspect", "role": None, "requires_user": False}


def prompt_bytes(path: str) -> bytes:
    value = Path(path).resolve()
    try:
        data = value.read_bytes()
    except OSError as exc:
        _fail("BLOCKED_ARGUMENT_COMBINATION", f"Prompt file could not be read: {exc}")
    if not data:
        _fail("BLOCKED_ARGUMENT_COMBINATION", "Prompt file must not be empty.")
    return data


def build_git_reference(root: Path, relative: str, commit: str = "HEAD") -> str:
    path = PurePosixPath(relative)
    if (
        not relative
        or "\\" in relative
        or path.is_absolute()
        or path.as_posix() != relative
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        _fail("BLOCKED_ARGUMENT_COMBINATION", "Reference path must be normalized and repository-relative.")
    resolved = run_git(root, "rev-parse", commit)
    commit_sha = resolved.stdout.strip()
    if resolved.returncode != 0 or re.fullmatch(r"[0-9a-f]{40}", commit_sha) is None:
        _fail("BLOCKED_ARGUMENT_COMBINATION", "Reference commit could not be resolved exactly.")
    shown = subprocess.run(
        ["git", "-C", str(root), "show", f"{commit_sha}:{relative}"],
        capture_output=True,
        check=False,
    )
    if shown.returncode != 0:
        _fail("BLOCKED_ARGUMENT_COMBINATION", "Reference bytes are not committed at the requested path.")
    return f"{relative}@{commit_sha}#{hashlib.sha256(shown.stdout).hexdigest()}"
