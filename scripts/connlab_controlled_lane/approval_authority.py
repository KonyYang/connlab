from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import CtlError, canonical_digest

_GATES = {
    "plan_review_pending": ("planning_first", "user_planning_approval_pending"),
    "implementation_readiness_pending": (
        "tests_only_implementation", "user_implementation_approval_pending"),
}
_FORBIDDEN = frozenset((
    "worktree_path", "completion_authority_nullable", "expected_evidence_path",
    "base_lane_head", "allowed_changed_paths", "checkpoint_required"))
_CALLBACK_TARGET_FIELDS = (
    "thread_id", "controller_thread_id", "scope_fingerprint",
    "approval_gate", "approval_scope_digest")


def approval_gate_for_state(state: str) -> tuple[str, str]:
    """Return the exact gate and pending state for an approval request."""
    try:
        return _GATES[state]
    except KeyError as exc:
        raise CtlError(
            "CTL_INVALID_TRANSITION", f"{state} has no User approval gate") from exc


def _controller_thread(registry: Mapping[str, Any]) -> str:
    bootstrap = registry.get("bootstrap", {}).get("controller", {})
    thread_id = bootstrap.get("thread_id")
    bindings = [
        binding for binding in registry.get("role_bindings", {}).values()
        if binding.get("role") == "Controller"
        and binding.get("status") == "active"
        and binding.get("thread_id") == thread_id
    ]
    if not thread_id or len(bindings) != 1:
        raise CtlError(
            "CTL_THREAD_BINDING_MISMATCH",
            "active Controller thread authority is missing or changed")
    return str(thread_id)


def build_approval_target(
    registry: Mapping[str, Any], lane_id: str, request: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the canonical Controller-bound approval request target."""
    lane = registry.get("lanes", {}).get(lane_id)
    if not isinstance(lane, dict) or request.get("lane_id") != lane_id or any(
        request.get(field) != lane.get(field)
        for field in ("task_id", "scope_fingerprint")
    ):
        raise CtlError(
            "CTL_DISPATCH_ACK_MISMATCH",
            "approval request does not match lane authority")
    state = str(lane.get("state"))
    gate, pending = approval_gate_for_state(state)
    thread_id = _controller_thread(registry)
    target = {field: request[field] for field in (
        "task_id", "lane_id", "route_id", "operation_id")}
    target.update({
        "role": "User", "thread_id": thread_id,
        "controller_thread_id": thread_id,
        "action_kind": "request_user_approval", "approval_gate": gate,
        "scope_fingerprint": lane["scope_fingerprint"],
        "approval_scope_digest": canonical_digest(lane.get("requested_scope", {})),
        "expected_from_state": state, "expected_pending_state": pending,
    })
    target["request_payload_digest"] = canonical_digest(target)
    target["payload_digest"] = target["request_payload_digest"]
    target["approval_contract_digest"] = canonical_digest(target)
    return target


def validate_approval_target(
    binding: Any, *, expected: Mapping[str, Any] | None = None,
) -> None:
    """Validate one complete approval target without worktree authority."""
    if not isinstance(binding, dict) or _FORBIDDEN.intersection(binding):
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "approval target is invalid")
    required = {
        "task_id", "lane_id", "route_id", "operation_id", "role", "thread_id",
        "controller_thread_id", "action_kind", "approval_gate", "scope_fingerprint",
        "approval_scope_digest", "expected_from_state", "expected_pending_state",
        "request_payload_digest", "payload_digest", "approval_contract_digest",
    }
    if set(binding) != required or any(
        not isinstance(binding[key], str) or not binding[key] for key in required
    ):
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "approval target is incomplete")
    if binding["thread_id"] != binding["controller_thread_id"] or (
        expected and any(binding[field] != expected.get(field)
                         for field in ("thread_id", "controller_thread_id"))
    ):
        raise CtlError("CTL_THREAD_BINDING_MISMATCH", "Controller thread changed")
    if expected is not None and dict(binding) != dict(expected):
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "approval target changed")
    gate, pending = approval_gate_for_state(binding["expected_from_state"])
    digest_source = dict(binding)
    digest_source.pop("approval_contract_digest")
    if (
        binding["role"] != "User"
        or binding["action_kind"] != "request_user_approval"
        or (binding["approval_gate"], binding["expected_pending_state"]) != (gate, pending)
        or binding["payload_digest"] != binding["request_payload_digest"]
        or binding["approval_contract_digest"] != canonical_digest(digest_source)
    ):
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "approval contract changed")


def record_bound_callback(
    registry: dict[str, Any], dispatch: Mapping[str, Any],
    payload: Mapping[str, Any], lane_id: str,
) -> str:
    """Route callbacks without treating approval as role completion."""
    if dispatch.get("action_kind") == "request_user_approval":
        record_approval_callback(registry, dispatch, payload, lane_id)
        return "approval_recorded"
    from .completion_authority import record_completion_callback

    record_completion_callback(registry, dispatch, payload, lane_id)
    return "completion_recorded"


def record_approval_callback(
    registry: dict[str, Any], dispatch: Mapping[str, Any],
    payload: Mapping[str, Any], lane_id: str,
) -> None:
    """Atomically persist a later User decision for one acknowledged request."""
    from .callbacks import callback_event_id

    target = dispatch.get("target_binding", {})
    validate_approval_target(target, expected=target)
    lane = registry.get("lanes", {}).get(lane_id, {})
    expected = {field: target.get(field) for field in _CALLBACK_TARGET_FIELDS}
    expected.update({
        "dispatch_operation_id": dispatch.get("operation_id"),
        "task_id": dispatch.get("task_id"), "lane_id": lane_id,
        "role": "User", "status": "user_approved",
        "route_id": dispatch.get("route_id"),
        "operation_id": dispatch.get("operation_id"),
        "payload_digest": target.get("request_payload_digest"),
        "evidence_path": None, "evidence_sha256": None, "lane_head": None,
    })
    changed = [field for field, value in expected.items()
               if payload.get(field) != value]
    if changed:
        code = ("CTL_THREAD_BINDING_MISMATCH" if set(changed).intersection(
            ("thread_id", "controller_thread_id")) else "CTL_CALLBACK_CONFLICT")
        raise CtlError(code, "User approval callback binding changed")
    event_id = str(payload.get("event_id", ""))
    if not event_id or event_id != callback_event_id(payload):
        raise CtlError("CTL_CALLBACK_CONFLICT", "approval callback event is not canonical")
    advance = dispatch.get("state_advance_payload", {})
    if (
        dispatch.get("stage") != "advanced"
        or lane.get("state") != target.get("expected_pending_state")
        or advance.get("from_state") != target.get("expected_from_state")
        or advance.get("to_state") != target.get("expected_pending_state")
        or event_id in registry.get("callbacks", {})
        or dispatch.get("approval_callback_event_id")
    ):
        raise CtlError(
            "CTL_ROLE_CALLBACK_STATE_MISMATCH",
            "approval callback does not match the pending gate")
    observation = {field: expected[field] for field in (
        "task_id", "lane_id", "approval_gate", "approval_scope_digest",
        "route_id", "operation_id", "thread_id")}
    registry["callbacks"][event_id] = {
        **deepcopy(payload), "approval_observation": observation}
    lane.setdefault("proof", {})["user_approved"] = True
    lane["proof"]["user_approval"] = observation
    dispatch["approval_callback_event_id"] = event_id
