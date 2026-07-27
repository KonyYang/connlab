from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import CtlError, canonical_digest

V2_CONTROLLER_TITLE = "ConnLab｜研发任务编排与集成主控 v2"
HEARTBEAT_NAME = "ConnLab v2 controlled-lane scan"
HEARTBEAT_RRULE = "FREQ=MINUTELY;INTERVAL=5"

BOOTSTRAP_STATES = frozenset((
    "bootstrap_controller_pending", "bootstrap_heartbeat_pending",
    "bootstrap_dry_run_pending", "bootstrap_ready"))
BOOTSTRAP_ACTIONS = frozenset((
    "create_controller_task", "create_paused_heartbeat", "run_zero_write_dry_run"))
BOOTSTRAP_TRANSITIONS = frozenset({
    ("bootstrap_controller_pending", "bootstrap_heartbeat_pending"),
    ("bootstrap_heartbeat_pending", "bootstrap_dry_run_pending"),
    ("bootstrap_dry_run_pending", "bootstrap_ready")})


def _require_mapping(payload: Mapping[str, Any], field: str) -> Mapping[str, Any]:
    value = payload.get(field)
    if not isinstance(value, dict):
        raise CtlError("CTL_INVALID_REQUEST", f"{field} must be an object")
    return value


def validate_bootstrap_request(
    command: str, request: Mapping[str, Any], *, registry_exists: bool | None = None
) -> None:
    payload = _require_mapping(request, "payload")
    if command == "bootstrap-registry":
        if registry_exists is True:
            raise CtlError("CTL_REGISTRY_SCHEMA_MISMATCH",
                           "bootstrap requires an absent registry")
        _validate_genesis_payload(payload)
        return
    if command == "register-lane":
        if registry_exists is False:
            raise CtlError(
                "CTL_LANE_NOT_AUTHORIZED",
                "registry must be bootstrapped before lane registration",
            )
        _validate_lane_payload(payload)
        return
    raise CtlError("CTL_INVALID_REQUEST", "unsupported administrative command")


def _validate_genesis_payload(payload: Mapping[str, Any]) -> None:
    if payload.get("state") != "bootstrap_controller_pending":
        raise CtlError("CTL_INVALID_TRANSITION",
                       "bootstrap must start at bootstrap_controller_pending")
    if not payload.get("primary_repo_root"):
        raise CtlError("CTL_INVALID_REQUEST", "primary_repo_root is required")
    legacy = _require_mapping(payload, "legacy_inventory")
    if canonical_digest(legacy) != payload.get("legacy_inventory_digest"):
        raise CtlError("CTL_PAYLOAD_DIGEST_MISMATCH", "legacy inventory digest changed")
    migration = _require_mapping(payload, "migration")
    if (
        migration.get("status") != "not_required"
        or migration.get("source_digest") != legacy.get("source_digest")
    ):
        raise CtlError("CTL_REGISTRY_SCHEMA_MISMATCH", "migration must be not_required")
    controller = _require_mapping(payload, "controller")
    heartbeat = _require_mapping(payload, "heartbeat")
    if controller.get("title") != V2_CONTROLLER_TITLE:
        raise CtlError("CTL_INVALID_REQUEST", "controller title is not canonical")
    controller_fields = ("native_mode", "saved_project_id", "project_path",
        "repository_fingerprint", "prompt_digest")
    if any(controller.get(field) in (None, "") for field in controller_fields):
        raise CtlError("CTL_INVALID_REQUEST", "controller target is incomplete")
    if heartbeat != {
        "name": HEARTBEAT_NAME,
        "rrule": HEARTBEAT_RRULE,
        "status": "PAUSED",
    }:
        raise CtlError("CTL_INVALID_REQUEST", "heartbeat contract is not canonical")
    authority = _require_mapping(payload, "authority_files")
    if canonical_digest(authority) != payload.get("authority_digest"):
        raise CtlError("CTL_EVIDENCE_STALE", "bootstrap authority digest changed")
    _require_mapping(payload, "requested_scope")
    if not isinstance(payload.get("owner_claims"), list):
        raise CtlError("CTL_INVALID_REQUEST", "owner_claims must be an array")


def _validate_lane_payload(payload: Mapping[str, Any]) -> None:
    if payload.get("state") != "planned":
        raise CtlError("CTL_AUTHORIZATION_REQUIRED",
                       "register-lane can only create a planned lane")
    for field in ("base_commit", "primary_repo_root"):
        if not payload.get(field):
            raise CtlError("CTL_INVALID_REQUEST", f"{field} is required")
    scope = _require_mapping(payload, "requested_scope")
    if canonical_digest(scope) != payload.get("scope_digest"):
        raise CtlError("CTL_SCOPE_CONFLICT", "scope digest changed")
    owners = payload.get("owner_claims")
    if not isinstance(owners, list):
        raise CtlError("CTL_INVALID_REQUEST", "owner_claims must be an array")
    if canonical_digest(owners) != payload.get("owner_claims_digest"):
        raise CtlError("CTL_OWNER_CONFLICT", "owner claims digest changed")
    authority = _require_mapping(payload, "authority_files")
    if canonical_digest(authority) != payload.get("authority_digest"):
        raise CtlError("CTL_EVIDENCE_STALE", "authority digest changed")
    _require_mapping(payload, "proof")


def apply_admin_mutation(
    registry: dict[str, Any], command: str, request: Mapping[str, Any],
    *, registry_exists: bool,
) -> str:
    validate_bootstrap_request(command, request, registry_exists=registry_exists)
    payload = request["payload"]
    lane_id = str(request["lane_id"])
    if command == "bootstrap-registry":
        legacy = deepcopy(payload["legacy_inventory"])
        legacy["status"] = "legacy_retained"
        registry["migration"] = deepcopy(payload["migration"])
        registry["legacy_inventory"] = legacy
        registry["bootstrap"] = {
            "controller": deepcopy(payload["controller"]),
            "heartbeat": deepcopy(payload["heartbeat"]),
        }
        registry["lanes"][lane_id] = _lane_record(request, payload)
        return "bootstrap_registry_created"
    if lane_id in registry["lanes"]:
        raise CtlError("CTL_SCOPE_CONFLICT", "lane already exists")
    from .ownership import find_owner_conflicts
    conflicts = find_owner_conflicts(
        payload["requested_scope"], registry["shared_owners"].values())
    if conflicts:
        raise CtlError("CTL_OWNER_CONFLICT", "planned lane conflicts with active owner")
    registry["lanes"][lane_id] = _lane_record(request, payload)
    registry["lanes"][lane_id]["implementation_authorized"] = False
    return "lane_registered"


def _lane_record(request: Mapping[str, Any], payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "task_id": request["task_id"],
        "state": payload["state"],
        "base_commit": payload.get("base_commit"),
        "primary_repo_root": payload["primary_repo_root"],
        "scope_fingerprint": request["scope_fingerprint"],
        "requested_scope": deepcopy(payload["requested_scope"]),
        "owner_claims": deepcopy(payload["owner_claims"]),
        "authority_files": deepcopy(payload["authority_files"]),
        "proof": deepcopy(payload.get("proof", {})),
    }


def select_bootstrap_action(state: str, proof: Mapping[str, Any]) -> dict[str, Any]:
    if state == "bootstrap_controller_pending":
        return {"kind": "create_controller_task", "target_role": "Controller"}
    if state == "bootstrap_heartbeat_pending" and proof.get("controller_acknowledged"):
        return {"kind": "create_paused_heartbeat", "target_role": "Controller"}
    if state == "bootstrap_dry_run_pending" and proof.get("heartbeat_acknowledged"):
        return {"kind": "run_zero_write_dry_run", "target_role": "Controller"}
    if state == "bootstrap_ready" and proof.get("dry_run_passed"):
        return {"kind": "no_action", "target_role": None}
    raise CtlError("CTL_INVALID_TRANSITION", f"no legal bootstrap action from {state}")


def validate_bootstrap_action(state: str, action_kind: str) -> None:
    selected = select_bootstrap_action(
        state,
        {
            "controller_acknowledged": True,
            "heartbeat_acknowledged": True,
            "dry_run_passed": True,
        },
    )
    if selected["kind"] != action_kind:
        raise CtlError("CTL_INVALID_TRANSITION",
                       f"action {action_kind} is not legal from {state}")


def validate_bootstrap_transition(from_state: str, to_state: str) -> None:
    if (from_state, to_state) not in BOOTSTRAP_TRANSITIONS:
        raise CtlError("CTL_INVALID_TRANSITION",
                       f"transition {from_state} -> {to_state} is not legal")


def validate_bootstrap_target_binding(
    binding: Any, *, action_kind: str,
    expected: Mapping[str, Any] | None = None,
) -> None:
    if not isinstance(binding, dict) or action_kind not in BOOTSTRAP_ACTIONS:
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "bootstrap target is invalid")
    required = {
        "create_controller_task": (
            "controller_title",
            "native_mode",
            "saved_project_id",
            "project_path",
            "repository_fingerprint",
            "prompt_digest",
        ),
        "create_paused_heartbeat": (
            "controller_thread_id",
            "heartbeat_name",
            "rrule",
            "status",
        ),
        "run_zero_write_dry_run": (
            "validation_scope_digest",
            "expected_external_action_count",
        ),
    }[action_kind]
    common = (
        "task_id",
        "lane_id",
        "route_id",
        "operation_id",
        "payload_digest",
        "action_kind",
        "role",
    )
    if binding.get("action_kind") != action_kind or any(
        binding.get(field) in (None, "") for field in common + required
    ):
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "bootstrap target is incomplete")
    if any(binding.get(field, object()) != value
           for field, value in (expected or {}).items()):
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "bootstrap target changed")


def validate_bootstrap_ack(
    dispatch: Mapping[str, Any], payload: Mapping[str, Any]
) -> Mapping[str, Any]:
    observed = payload.get("readback_binding")
    action = str(dispatch.get("action_kind"))
    authority_field = (
        "git_observation_digest"
        if action == "run_zero_write_dry_run"
        else "receipt_digest"
    )
    if not payload.get(authority_field):
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "bootstrap authority is missing")
    validate_bootstrap_target_binding(
        observed, action_kind=action, expected=dispatch.get("target_binding")
    )
    if payload.get("readback_digest") != canonical_digest(observed):
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "bootstrap read-back digest changed")
    output_requirements = {
        "create_controller_task": (
            ("thread_id", None),
            ("project_binding_verified", True),
            ("title_verified", True),
        ),
        "create_paused_heartbeat": (
            ("automation_id", None),
            ("controller_binding_verified", True),
            ("status_verified", True),
        ),
        "run_zero_write_dry_run": (
            ("passed", True),
            ("actual_external_action_count", 0),
        ),
    }[action]
    for field, exact in output_requirements:
        value = observed.get(field)
        if value in (None, "") or (exact is not None and value != exact):
            raise CtlError(
                "CTL_DISPATCH_ACK_MISMATCH",
                f"bootstrap read-back field is invalid: {field}",
            )
    return observed


def adopt_bootstrap_readback(
    registry: dict[str, Any],
    lane_id: str,
    dispatch: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> None:
    observed = validate_bootstrap_ack(dispatch, payload)
    lane = registry["lanes"][lane_id]
    proof = lane.setdefault("proof", {})
    bootstrap = registry.setdefault("bootstrap", {})
    action = dispatch["action_kind"]
    if action == "create_controller_task":
        bootstrap.setdefault("controller", {})["thread_id"] = observed["thread_id"]
        registry["role_bindings"][f"{lane_id}:Controller"] = {
            "lane_id": lane_id, "role": "Controller",
            "thread_id": observed["thread_id"], "status": "active"}
        proof["controller_acknowledged"] = True
    elif action == "create_paused_heartbeat":
        heartbeat = bootstrap.setdefault("heartbeat", {})
        heartbeat["automation_id"] = observed["automation_id"]
        heartbeat["status"] = "PAUSED"
        proof["heartbeat_acknowledged"] = True
    else:
        bootstrap["dry_run"] = {
            "passed": True,
            "external_action_count": 0,
            "observation_digest": canonical_digest(observed),
        }
        proof["dry_run_passed"] = True
