from __future__ import annotations

import hashlib
import json
import uuid
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

SCHEMA_VERSION = 2

READ_ONLY_COMMANDS = frozenset({
    "scan", "route-plan", "registry-status", "recover", "worktree-preflight",
    "integration-preflight", "retire-preflight",
})
MUTATION_COMMANDS = (
    "prepare-dispatch",
    "mark-invocation-started",
    "record-action-result",
    "record-callback",
    "ack-dispatch",
    "advance-state",
)
ADMIN_COMMANDS = ("bootstrap-registry", "register-lane")

EXIT_CODES: dict[int, tuple[str, ...]] = {
    0: ("CTL_OK", "CTL_DRY_RUN", "CTL_NO_ACTION", "CTL_ALREADY_APPLIED"),
    2: (
        "CTL_INVALID_REQUEST",
        "CTL_SCHEMA_UNSUPPORTED",
        "CTL_REGISTRY_SCHEMA_MISMATCH",
        "CTL_PAYLOAD_DIGEST_MISMATCH",
    ),
    3: (
        "CTL_CAS_CONFLICT",
        "CTL_IDEMPOTENCY_CONFLICT",
        "CTL_DISPATCH_STAGE_MISMATCH",
        "CTL_CALLBACK_CONFLICT",
        "CTL_ROLE_CALLBACK_STATE_MISMATCH",
    ),
    4: (
        "CTL_AUTHORIZATION_REQUIRED",
        "CTL_LANE_NOT_AUTHORIZED",
        "CTL_INVALID_TRANSITION",
        "CTL_SCOPE_CONFLICT",
        "CTL_SCOPE_VIOLATION",
        "CTL_OWNER_CONFLICT",
        "CTL_EVIDENCE_STALE",
        "CTL_THREAD_BINDING_MISMATCH",
        "CTL_GIT_PRECONDITION_FAILED",
        "CTL_PRIMARY_DIRTY",
        "CTL_INDEX_NOT_EMPTY",
        "CTL_HEAD_MISMATCH",
        "CTL_WORKTREE_MISMATCH",
        "CTL_WORKTREE_DIRTY",
        "CTL_UNINTEGRATED_HEAD",
    ),
    5: (
        "CTL_RECOVERY_REQUIRED",
        "CTL_TOPOLOGY_STALE",
        "CTL_DISPATCH_ACK_MISMATCH",
        "CTL_NATIVE_READBACK_AMBIGUOUS",
    ),
    6: (
        "CTL_REGISTRY_LOCKED",
        "CTL_LOCK_BUSY",
        "CTL_ATOMIC_WRITE_FAILED",
        "CTL_POST_WRITE_VERIFY_FAILED",
        "CTL_GIT_FAILED",
    ),
    7: ("CTL_REMOTE_FORBIDDEN", "CTL_DESTRUCTIVE_FORBIDDEN"),
}
ALL_CODES = frozenset(code for codes in EXIT_CODES.values() for code in codes)
CODE_TO_EXIT = {code: exit_code for exit_code, codes in EXIT_CODES.items() for code in codes}
GIT_ACTIONS = frozenset(("create_or_adopt_worktree", "governance_closeout", "retire_worktree"))


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def initial_registry(repository_fingerprint: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    registry = {
        "schema_version": 2, "registry_id": str(uuid.uuid4()),
        "repository_fingerprint": repository_fingerprint,
        "git_common_dir_fingerprint": repository_fingerprint,
        "generation": 0, "created_at": now, "updated_at": now, "migration": None,
    }
    fields = (
        "lanes", "worktrees", "shared_owners", "role_bindings",
        "dispatches", "callbacks", "recovery_points", "idempotency",
    )
    registry.update({field: {} for field in fields})
    return registry


def convert_v1_to_v2(source: Mapping[str, Any], *, source_digest: str) -> dict[str, Any]:
    if source.get("schema_version") != 1:
        raise CtlError("CTL_REGISTRY_SCHEMA_MISMATCH", "source registry is not v1")
    converted = initial_registry(str(source.get("repository_fingerprint", "legacy")))
    for field in ("lanes", "worktrees", "shared_owners", "role_bindings"):
        converted[field] = deepcopy(source.get(field, {}))
    generation = int(source.get("generation", 0))
    converted["generation"] = generation
    converted["migration"] = {
        "source_schema_version": 1, "source_digest": source_digest,
        "source_generation": generation, "converter_version": 1,
        "migration_id": canonical_digest(
            {"source_digest": source_digest, "generation": generation}),
        "status": "committed",
    }
    return converted


def exit_code_for(code: str) -> int:
    return CODE_TO_EXIT.get(code, 2)


@dataclass
class CtlError(Exception):
    code: str
    message: str
    facts: Mapping[str, Any] | None = None

    def __str__(self) -> str:
        return self.message


def _binding_error(message: str) -> None:
    raise CtlError("CTL_DISPATCH_ACK_MISMATCH", message)


def validate_common_request(request: Mapping[str, Any], command: str) -> None:
    if request.get("schema_version") != SCHEMA_VERSION:
        raise CtlError("CTL_SCHEMA_UNSUPPORTED", "schema_version must be 2")
    if request.get("command") != command:
        raise CtlError("CTL_INVALID_REQUEST", "request command does not match CLI command")
    required = (
        "request_id",
        "task_id",
        "lane_id",
        "operation_id",
        "route_id",
        "scope_fingerprint",
        "payload",
        "payload_digest",
    )
    missing = [field for field in required if not request.get(field)]
    if missing:
        raise CtlError(
            "CTL_INVALID_REQUEST",
            f"missing required fields: {', '.join(missing)}",
        )
    if canonical_digest(request["payload"]) != request["payload_digest"]:
        raise CtlError("CTL_PAYLOAD_DIGEST_MISMATCH", "payload_digest does not match payload")
    if command in MUTATION_COMMANDS + ADMIN_COMMANDS:
        for field in ("expected_registry_generation", "idempotency_key"):
            if field not in request or request[field] in (None, ""):
                raise CtlError("CTL_INVALID_REQUEST", f"{field} is required")


def validate_target_binding(
    binding: Any, *, action_kind: str, expected: Mapping[str, Any] | None = None
) -> None:
    """Validate a canonical prepared or observed external target."""
    if not isinstance(binding, dict):
        _binding_error("target binding must be an object")
    if action_kind == "create_developer_environment":
        from .native_environment import validate_native_create_binding

        validate_native_create_binding(binding, expected=expected)
        return
    required = [
        "task_id", "lane_id", "route_id", "operation_id",
        "payload_digest", "action_kind", "worktree_path",
    ]
    required += (["repo_root", "branch", "base_commit", "head", "git_common_dir",
                  "scope_fingerprint"] if action_kind in GIT_ACTIONS else ["thread_id"])
    if any(not binding.get(field) for field in required) or (
        binding["action_kind"] != action_kind
    ):
        _binding_error("target binding is incomplete")
    missing = object()
    if any(binding.get(field, missing) != value
           for field, value in (expected or {}).items()):
        _binding_error("target binding changed")
    if "completion_authority_nullable" in (expected or {}):
        from .completion_authority import validate_completion_contract

        validate_completion_contract(binding)


def validate_dispatch_binding(
    dispatch: Mapping[str, Any], request: Mapping[str, Any], command: str
) -> None:
    """Bind a mutation to the exact prepared dispatch."""
    if any(dispatch.get(field) != request.get(field)
           for field in ("task_id", "lane_id", "route_id", "scope_fingerprint")):
        _binding_error(f"{command} does not match prepared dispatch")
    payload = request["payload"]
    if command == "record-action-result" and not (
        payload.get("receipt_digest") or payload.get("git_observation_digest")
    ):
        _binding_error("action result requires native receipt or Git observation")
    if command == "ack-dispatch":
        if dispatch.get("action_kind") == "create_developer_environment":
            if not payload.get("receipt_digest"):
                _binding_error("native acknowledgement requires receipt")
            return
        observed = payload.get("readback_binding")
        validate_target_binding(
            observed, action_kind=str(dispatch.get("action_kind")),
            expected=dispatch.get("target_binding"))
        if dispatch.get("target_binding") != observed or (
            payload.get("readback_digest") != canonical_digest(observed)
        ):
            _binding_error("dispatch read-back does not match frozen target binding")
        required = "git_observation_digest" if dispatch.get(
            "action_kind") in GIT_ACTIONS else "receipt_digest"
        if not payload.get(required):
            _binding_error("acknowledgement authority is missing")
    if command == "advance-state" and (
        dispatch.get("action_kind") != "create_developer_environment"
        and payload.get("from_state") != dispatch.get("current_state")
    ):
        _binding_error("state advance does not start from prepared state")


def validate_recovery_binding(
    dispatch: Mapping[str, Any], observed: Mapping[str, Any]
) -> None:
    """Prove one recovery read-back belongs to the prepared operation."""
    action = str(dispatch.get("action_kind"))
    expected = dispatch.get("target_binding", {})
    from .bootstrap import BOOTSTRAP_ACTIONS, validate_bootstrap_ack
    if action in BOOTSTRAP_ACTIONS:
        validate_bootstrap_ack(dispatch, {
            "readback_binding": observed,
            "readback_digest": canonical_digest(observed),
            "receipt_digest": "recovery", "git_observation_digest": "recovery"})
        return
    if action == "create_developer_environment":
        from .native_environment import adopt_native_environment

        receipt = dispatch.get("action_result_payload", {}).get("receipt", {})
        adopt_native_environment(
            expected, receipt=receipt, matches=[observed], readable=True)
        return
    validate_target_binding(observed, action_kind=action, expected=expected)
    if expected != observed:
        code = "CTL_WORKTREE_MISMATCH" if action in GIT_ACTIONS else (
            "CTL_THREAD_BINDING_MISMATCH")
        raise CtlError(code, "recovery target binding changed")


def result(
    *,
    code: str,
    request: Mapping[str, Any] | None = None,
    message: str = "",
    zero_write: bool,
    **fields: Any,
) -> dict[str, Any]:
    request = request or {}
    output: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "ok": code in EXIT_CODES[0],
        "code": code,
        "message": message,
        "request_id": request.get("request_id"),
        "command": request.get("command"),
        "task_id": request.get("task_id"),
        "lane_id": request.get("lane_id"),
        "zero_write": zero_write,
        "old_generation": fields.pop("old_generation", None),
        "new_generation": fields.pop("new_generation", None),
        "operation_id": request.get("operation_id"),
        "route_id": request.get("route_id"),
        "state": fields.pop("state", None),
        "durable_stage": fields.pop("durable_stage", None),
        "record_digest": fields.pop("record_digest", None),
        "facts": fields.pop("facts", {}),
        "conflicts": fields.pop("conflicts", []),
        "recovery": fields.pop("recovery", None),
        "next_action": fields.pop("next_action", None),
    }
    output.update(fields)
    return output
