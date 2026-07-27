from __future__ import annotations

import json
from typing import Any, Mapping

from .completion_authority import observe_completion_authority
from .contracts import CtlError, canonical_digest, canonical_json
from .git_preflight import (
    recovery_decision, validate_exact_native_binding, verified_recovery_decision,
)
from .native_environment import native_create_decision

CALLBACK_PREFIX = "CONNLAB_CALLBACK_V2 "
_BINDING_FIELDS = (
    "task_id",
    "lane_id",
    "role",
    "route_id",
    "operation_id",
    "thread_id",
    "worktree_path",
    "payload_digest",
)
_EVENT_ID_FIELDS = (*_BINDING_FIELDS,
    "evidence_path",
    "evidence_sha256",
    "status",
    "lane_head",
)
_ROLE_OUTCOMES = {
    "planner": {"planner_complete": "complete"},
    "developer": {"ready_for_review": "complete"},
    "reviewer": {"reviewer_pass": "passed", "reviewer_blocked": "blocked"},
    "qa": {"qa_pass": "passed", "qa_fail": "blocked", "qa_blocked": "blocked"},
    "integrator": {"integrator_accepted": "accepted", "integrator_blocked": "blocked"},
    "user": {"user_approved": "approved"},
}


def callback_event_id(fields: Mapping[str, Any]) -> str:
    return canonical_digest({field: fields.get(field) for field in _EVENT_ID_FIELDS})


def callback_template(fields: Mapping[str, Any]) -> str:
    payload = dict(fields)
    expected_id = callback_event_id(payload)
    if payload.get("event_id") not in (None, expected_id):
        raise CtlError("CTL_CALLBACK_CONFLICT", "callback event_id is not canonical")
    payload["event_id"] = expected_id
    return f"{CALLBACK_PREFIX}{canonical_json(payload)}"


def parse_callback(
    text: str,
    *,
    expected: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not text.startswith(CALLBACK_PREFIX):
        raise CtlError("CTL_INVALID_REQUEST", "callback prefix is missing")
    try:
        payload = json.loads(text[len(CALLBACK_PREFIX) :])
    except json.JSONDecodeError as exc:
        raise CtlError("CTL_INVALID_REQUEST", "callback JSON is invalid") from exc
    if not isinstance(payload, dict):
        raise CtlError("CTL_INVALID_REQUEST", "callback must be a JSON object")
    for field in ("event_id", "task_id", "lane_id", "role", "status"):
        if not payload.get(field):
            raise CtlError("CTL_INVALID_REQUEST", f"callback {field} is required")
    if payload["event_id"] != callback_event_id(payload):
        raise CtlError("CTL_CALLBACK_CONFLICT", "callback event_id is not canonical")
    if expected:
        for field in _BINDING_FIELDS:
            if field in expected and payload.get(field) != expected.get(field):
                code = (
                    "CTL_THREAD_BINDING_MISMATCH"
                    if field == "thread_id"
                    else "CTL_CALLBACK_CONFLICT"
                )
                raise CtlError(code, f"callback {field} does not match binding")
    return payload


def validate_completion_callback(
    registry: Mapping[str, Any], dispatch: Mapping[str, Any], payload: Mapping[str, Any]
) -> str:
    return completion_callback_result(registry, dispatch, payload)[0]


def completion_callback_result(
    registry: Mapping[str, Any], dispatch: Mapping[str, Any], payload: Mapping[str, Any]
) -> tuple[str, dict[str, Any]]:
    target = dispatch.get("target_binding", {})
    expected = {
        "task_id": dispatch.get("task_id"), "lane_id": dispatch.get("lane_id"),
        "route_id": dispatch.get("route_id"), "operation_id": dispatch.get("operation_id"),
        "role": target.get("role"), "thread_id": target.get("thread_id"),
        "worktree_path": target.get("worktree_path"),
        "payload_digest": target.get("payload_digest"),
    }
    if any(not expected.get(field) or payload.get(field) != value
           for field, value in expected.items()):
        raise CtlError("CTL_ROLE_CALLBACK_STATE_MISMATCH",
                       "callback does not match frozen role binding")
    lane = registry.get("lanes", {}).get(dispatch.get("lane_id"))
    to_state = dispatch.get("state_advance_payload", {}).get("to_state")
    binding = registry.get("role_bindings", {}).get(
        f"{dispatch.get('lane_id')}:{target.get('role')}")
    if not lane or lane.get("state") != to_state or not binding or (
        binding.get("status") != "active" or any(
            binding.get(field) != target.get(field) for field in target)
    ):
        raise CtlError("CTL_ROLE_CALLBACK_STATE_MISMATCH",
                       "callback does not match the active gate")
    observation = observe_completion_authority(target, payload)
    outcomes = _ROLE_OUTCOMES.get(str(payload.get("role", "")).casefold(), {})
    outcome = outcomes.get(str(payload.get("status", "")).casefold())
    if not outcome:
        raise CtlError("CTL_CALLBACK_CONFLICT", "callback status is not canonical")
    return outcome, observation


def native_task_decision(
    *, action: str, stage: str, matches: int = 0,
    archive_authorized: bool = False, retired: bool = False,
    expected_binding: Mapping[str, Any] | None = None,
    observed_binding: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if action == "dry-run":
        return {"code": "CTL_DRY_RUN", "execute": False, "external_action_count": 0}
    if action in ("create", "send"):
        if stage != "invocation_started":
            raise CtlError("CTL_DISPATCH_STAGE_MISMATCH",
                           f"{action} requires invocation_started")
        if action == "create" and expected_binding and (
            expected_binding.get("action_kind") == "create_developer_environment"
        ):
            return native_create_decision(
                stage=stage, binding=expected_binding,
                capability=observed_binding or {})
        validate_exact_native_binding(expected_binding, observed_binding)
        return {"code": "CTL_OK", "execute": True, "external_action_count": 1}
    if action == "adopt":
        if matches != 1:
            code = "CTL_NATIVE_READBACK_AMBIGUOUS" if matches > 1 else (
                "CTL_RECOVERY_REQUIRED")
            raise CtlError(code, "adoption requires exactly one read-back match")
        validate_exact_native_binding(expected_binding, observed_binding)
        return {"code": "CTL_OK", "execute": False, "external_action_count": 0}
    if action == "archive":
        if not archive_authorized or not retired:
            raise CtlError("CTL_AUTHORIZATION_REQUIRED",
                           "archive requires authorization and retired lane")
        if stage != "invocation_started":
            raise CtlError("CTL_DISPATCH_STAGE_MISMATCH",
                           "archive requires invocation_started")
        validate_exact_native_binding(expected_binding, observed_binding)
        return {"code": "CTL_OK", "execute": True, "external_action_count": 1}
    raise CtlError("CTL_INVALID_REQUEST", f"unsupported native action: {action}")
