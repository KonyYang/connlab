from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import CtlError, canonical_digest

V2_CONTROLLER_TITLE = "ConnLab｜研发任务编排与集成主控 v2"
CONTROLLER_TITLE_ACTION_VERSION = "controller-title-v1"
CONTROLLER_ACTIONS = frozenset((
    "create_controller_task", "set_controller_title", "adopt_exact_controller_title"))
CONTROLLER_TITLE_ACTIONS = frozenset(
    action for action in CONTROLLER_ACTIONS if action != "create_controller_task"
)

_CREATE_CONFIG_FIELDS = (
    "native_mode", "saved_project_id", "project_path",
    "repository_fingerprint", "prompt_digest",
)
_CREATE_FIELDS = ("controller_title",) + _CREATE_CONFIG_FIELDS
_TITLE_FIELDS = (
    "thread_id", "expected_title", "host_id", "cwd",
    "saved_project_id", "project_path", "action_version",
)
_COMMON_FIELDS = (
    "task_id", "lane_id", "route_id", "operation_id",
    "payload_digest", "action_kind", "role")


def validate_controller_configuration(controller: Mapping[str, Any]) -> None:
    if controller.get("title") != V2_CONTROLLER_TITLE:
        raise CtlError("CTL_INVALID_REQUEST", "controller title is not canonical")
    if any(controller.get(field) in (None, "") for field in _CREATE_CONFIG_FIELDS):
        raise CtlError("CTL_INVALID_REQUEST", "controller target is incomplete")


def build_controller_create_target(controller: Mapping[str, Any]) -> dict[str, Any]:
    validate_controller_configuration(controller)
    return {
        "controller_title": controller["title"],
        **{field: controller[field] for field in _CREATE_CONFIG_FIELDS},
    }


def canonical_controller_title_ids(
    registry_id: str, lane_id: str, thread_id: str, action_kind: str,
) -> dict[str, str]:
    if action_kind not in CONTROLLER_TITLE_ACTIONS:
        raise CtlError("CTL_INVALID_REQUEST", "controller title action is invalid")
    identity = canonical_digest({
        "registry_id": registry_id,
        "lane_id": lane_id,
        "thread_id": thread_id,
        "action_kind": action_kind,
        "action_version": CONTROLLER_TITLE_ACTION_VERSION,
    })[:24]
    return {
        "route_id": f"ctl-controller-title-{identity}",
        "operation_id": f"ctl-controller-title-{CONTROLLER_TITLE_ACTION_VERSION}-{identity}",
    }


def select_controller_title_action(proof: Mapping[str, Any]) -> dict[str, Any]:
    if not proof.get("controller_thread_adopted"):
        raise CtlError(
            "CTL_INVALID_TRANSITION",
            "controller title requires an adopted thread",
        )
    kind = (
        "adopt_exact_controller_title"
        if proof.get("controller_title_exact")
        else "set_controller_title"
    )
    return {"kind": kind, "target_role": "Controller"}


def build_controller_title_target(
    registry: Mapping[str, Any], lane_id: str, action_kind: str,
) -> dict[str, Any]:
    controller = registry.get("bootstrap", {}).get("controller", {})
    thread_id = controller.get("thread_id")
    if not thread_id:
        raise CtlError(
            "CTL_THREAD_BINDING_MISMATCH",
            "controller thread identity is missing",
        )
    target = {
        "action_kind": action_kind,
        "thread_id": thread_id,
        "expected_title": V2_CONTROLLER_TITLE,
        "host_id": controller.get("host_id"),
        "cwd": controller.get("cwd"),
        "saved_project_id": controller.get("saved_project_id"),
        "project_path": controller.get("project_path"),
        "action_version": CONTROLLER_TITLE_ACTION_VERSION,
        **canonical_controller_title_ids(
            str(registry.get("registry_id", "")),
            lane_id,
            str(thread_id),
            action_kind,
        ),
    }
    if action_kind not in CONTROLLER_TITLE_ACTIONS or any(
        target.get(field) in (None, "") for field in _TITLE_FIELDS
    ):
        raise CtlError(
            "CTL_DISPATCH_ACK_MISMATCH",
            "controller title target is incomplete",
        )
    return target


def validate_controller_target_binding(
    binding: Any, action_kind: str, expected: Mapping[str, Any] | None = None,
) -> None:
    if not isinstance(binding, dict) or action_kind not in CONTROLLER_ACTIONS:
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "controller target is invalid")
    required = (
        _CREATE_FIELDS if action_kind == "create_controller_task" else _TITLE_FIELDS
    )
    if binding.get("action_kind") != action_kind or any(
        binding.get(field) in (None, "") for field in _COMMON_FIELDS + required
    ):
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "controller target is incomplete")
    for field, value in (expected or {}).items():
        if binding.get(field, object()) != value:
            code = (
                "CTL_THREAD_BINDING_MISMATCH"
                if field == "thread_id"
                else "CTL_DISPATCH_ACK_MISMATCH"
            )
            raise CtlError(code, f"controller target changed: {field}")


def _readback_binding(
    dispatch: Mapping[str, Any], payload: Mapping[str, Any],
) -> Mapping[str, Any]:
    matches = payload.get("readback_matches", 1)
    if payload.get("readback_readable", True) is False or matches == 0:
        raise CtlError("CTL_RECOVERY_REQUIRED", "controller read-back is unavailable")
    if not isinstance(matches, int) or matches != 1:
        raise CtlError(
            "CTL_NATIVE_READBACK_AMBIGUOUS",
            "controller read-back is ambiguous",
        )
    observed = payload.get("readback_binding")
    if not isinstance(observed, dict):
        raise CtlError("CTL_RECOVERY_REQUIRED", "controller read-back is missing")
    if payload.get("readback_digest") != canonical_digest(observed):
        raise CtlError(
            "CTL_DISPATCH_ACK_MISMATCH",
            "controller read-back digest changed",
        )
    validate_controller_target_binding(
        observed,
        str(dispatch.get("action_kind")),
        expected=dispatch.get("target_binding"),
    )
    return observed


def validate_controller_ack(
    dispatch: Mapping[str, Any], payload: Mapping[str, Any],
) -> Mapping[str, Any]:
    if not payload.get("receipt_digest"):
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "controller receipt is missing")
    observed = _readback_binding(dispatch, payload)
    action = dispatch.get("action_kind")
    if action == "create_controller_task":
        required = ("thread_id", "host_id", "cwd", "observed_initial_title")
    else:
        required = ("thread_id", "title")
    if any(observed.get(field) in (None, "") for field in required):
        raise CtlError(
            "CTL_DISPATCH_ACK_MISMATCH",
            "controller read-back identity is incomplete",
        )
    if not observed.get("project_binding_verified"):
        raise CtlError(
            "CTL_DISPATCH_ACK_MISMATCH",
            "controller project binding is unverified",
        )
    if action in CONTROLLER_TITLE_ACTIONS and observed.get("title") != V2_CONTROLLER_TITLE:
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "controller title is not exact")
    return observed


def adopt_controller_readback(
    registry: dict[str, Any],
    lane_id: str,
    dispatch: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> None:
    observed = validate_controller_ack(dispatch, payload)
    lane = registry["lanes"][lane_id]
    proof = lane.setdefault("proof", {})
    controller = registry.setdefault("bootstrap", {}).setdefault("controller", {})
    action = dispatch["action_kind"]
    if action == "create_controller_task":
        controller.update({
            field: deepcopy(observed[field])
            for field in ("thread_id", "host_id", "cwd", "observed_initial_title")
        })
        proof["controller_thread_adopted"] = True
        proof["controller_title_exact"] = (
            observed["observed_initial_title"] == V2_CONTROLLER_TITLE
        )
        status = "title_pending"
    else:
        controller["title"] = V2_CONTROLLER_TITLE
        controller["title_observation_digest"] = canonical_digest(observed)
        proof["controller_title_exact"] = True
        proof["controller_acknowledged"] = True
        status = "active"
    registry["role_bindings"][f"{lane_id}:Controller"] = {
        "lane_id": lane_id,
        "role": "Controller",
        "thread_id": controller["thread_id"],
        "status": status,
    }
