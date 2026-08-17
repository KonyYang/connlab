#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from typing import Any

from scripts.connlab_serial_complex import ACTION_ROLES, SerialContractError


BOUNDED_FIX_CODES = {"REVIEWER_BLOCKED", "QA_BLOCKED", "INTEGRATION_BLOCKED"}
HISTORY_ROLES = {"Planner", "Developer", "Reviewer", "QA", "Integrator"}


def _fail(code: str, reason: str) -> None:
    raise SerialContractError(code, reason)


def _context(active: dict[str, Any]) -> dict[str, Any]:
    value = active.get("complex_context")
    if not isinstance(value, dict):
        _fail("BLOCKED_STATE", "A durable complex context is required.")
    return value


def _history_attempts(context: dict[str, Any], role: str) -> list[int]:
    invocations = context.get("role_invocations")
    if not isinstance(invocations, list) or any(not isinstance(item, dict) for item in invocations):
        _fail("BLOCKED_ATTEMPT_HISTORY_INVALID", "Durable role invocation history is invalid.")
    timing = context.get("timing_facts")
    timing_roles = [] if timing is None else timing.get("roles") if isinstance(timing, dict) else None
    if not isinstance(timing_roles, list) or any(not isinstance(item, dict) for item in timing_roles):
        _fail("BLOCKED_ATTEMPT_HISTORY_INVALID", "Durable role timing history is invalid.")

    def collect(items: list[dict[str, Any]], source: str) -> dict[str, list[int]]:
        result = {name: [] for name in HISTORY_ROLES}
        for item in items:
            item_role, attempt = item.get("role"), item.get("attempt")
            if item_role not in HISTORY_ROLES or type(attempt) is not int or attempt < 1:
                _fail("BLOCKED_ATTEMPT_HISTORY_INVALID", f"{source} role attempt is invalid.")
            result[item_role].append(attempt)
        for item_role, attempts in result.items():
            if attempts and sorted(attempts) != list(range(1, len(attempts) + 1)):
                _fail(
                    "BLOCKED_ATTEMPT_HISTORY_INVALID",
                    f"{source} {item_role} attempts are duplicated or non-contiguous.",
                )
        return result

    invocation_attempts = collect(invocations, "Invocation")
    timing_attempts = collect(timing_roles, "Timing")
    invoked, timed = invocation_attempts[role], timing_attempts[role]
    if invoked and timed and invoked != timed:
        _fail("BLOCKED_ATTEMPT_HISTORY_INVALID", f"{role} invocation and timing attempts differ.")
    return invoked or timed


def next_role_attempt(context: dict[str, Any], role: str) -> int:
    if role not in HISTORY_ROLES:
        _fail("BLOCKED_ROLE_ORDER", "Native action role is not attempt-tracked.")
    attempts = _history_attempts(context, role)
    return len(attempts) + 1


def build_native_action(
    active: dict[str, Any],
    action_name: str,
    prompt_bytes: bytes,
    title: str,
    recorded_at: str,
) -> dict[str, Any]:
    context = _context(active)
    role = ACTION_ROLES.get(action_name)
    if role is None or not prompt_bytes or not title.strip() or not recorded_at:
        _fail("BLOCKED_ARGUMENT_COMBINATION", "Native action inputs are incomplete.")
    if context.get("pending_callback") is not None or context.get("current_role") is not None:
        _fail("BLOCKED_NATIVE_ACTION_PENDING", "A role or callback is already active.")
    blocker = active.get("blocker")
    blocker_code = blocker.get("code") if isinstance(blocker, dict) else None
    expected_action = {
        "planning": "planner_dispatch", "review": "reviewer_dispatch",
        "qa": "qa_dispatch", "integration": "integrator_dispatch",
    }.get(active.get("phase"))
    if active.get("phase") == "development":
        expected_action = "developer_dispatch" if context.get("host_id") else "host_create"
    if blocker_code in BOUNDED_FIX_CODES:
        expected_action = "developer_dispatch"
    if action_name != expected_action:
        _fail("BLOCKED_ROLE_ORDER", "Native action does not match the durable next phase.")
    attempt = 1 if role == "Host" else next_role_attempt(context, role)
    prompt_sha = hashlib.sha256(prompt_bytes).hexdigest()
    identity = {
        "task_id": active.get("task_id"), "action": action_name, "role": role,
        "attempt": attempt, "prompt_sha256": prompt_sha, "title": title,
        "plan_ref": active.get("plan_ref"), "approval_ref": active.get("approval_ref"),
        "host_id": context.get("host_id"), "head_sha": context.get("head_sha"),
    }
    action_id = hashlib.sha256(
        json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "schema": "connlab.serial-native-action", "version": 1, "action_id": action_id,
        "action": action_name, "role": role, "attempt": attempt,
        "prompt_sha256": prompt_sha, "title": title, "recorded_at": recorded_at,
    }
