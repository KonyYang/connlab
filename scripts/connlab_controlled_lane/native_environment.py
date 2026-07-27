from __future__ import annotations

from typing import Any, Mapping, NoReturn, Sequence

from .contracts import CtlError

_PROVISIONAL_REQUIRED = (
    "task_id", "lane_id", "route_id", "operation_id",
    "payload_digest", "role", "saved_project_id", "project_path",
    "repository_fingerprint", "starting_ref", "expected_base_commit",
    "expected_primary_head", "scope_fingerprint", "owner_claims_digest",
    "prompt_digest", "client_request_digest",
)
_UNKNOWN_AT_PREPARE = (
    "thread_id",
    "pending_worktree_id",
    "worktree_path",
    "branch",
    "base_commit",
    "head",
    "git_common_dir",
)
_OBSERVED_REQUIRED = (
    "thread_id",
    "worktree_path",
    "branch",
    "base_commit",
    "head",
    "git_common_dir",
)


def _fail(code: str, message: str) -> NoReturn:
    raise CtlError(code, message)


def _receipt_identity(receipt: Mapping[str, Any]) -> tuple[str, Any]:
    thread_id = receipt.get("threadId")
    pending_id = receipt.get("pendingWorktreeId")
    if bool(thread_id) == bool(pending_id):
        _fail("CTL_DISPATCH_ACK_MISMATCH",
              "native receipt requires exactly one identity")
    return ("thread_id", thread_id) if thread_id else (
        "pending_worktree_id", pending_id)


def validate_native_create_binding(
    binding: Mapping[str, Any],
    *,
    expected: Mapping[str, Any] | None = None,
) -> None:
    """Validate the pre-invocation Option A request without invented identity."""
    if any(not binding.get(field) for field in _PROVISIONAL_REQUIRED):
        _fail("CTL_DISPATCH_ACK_MISMATCH",
              "native environment request binding is incomplete")
    if (
        binding.get("action_kind") != "create_developer_environment"
        or binding.get("role") != "Developer"
        or binding.get("native_mode") != "create_new"
        or binding.get("environment") != "worktree"
    ):
        _fail("CTL_DISPATCH_ACK_MISMATCH",
              "native environment request contract changed")
    if any(field in binding for field in _UNKNOWN_AT_PREPARE):
        _fail("CTL_DISPATCH_ACK_MISMATCH",
              "native identity cannot be frozen before create")
    missing = object()
    for field, value in (expected or {}).items():
        if binding.get(field, missing) != value:
            _fail("CTL_DISPATCH_ACK_MISMATCH",
                  f"native environment target {field} changed")


def native_create_decision(
    *,
    stage: str,
    binding: Mapping[str, Any],
    capability: Mapping[str, Any],
) -> dict[str, Any]:
    """Return the single native create request without performing it."""
    validate_native_create_binding(binding)
    if stage != "invocation_started":
        _fail("CTL_DISPATCH_STAGE_MISMATCH",
              "native environment create requires invocation_started")
    if (
        capability.get("tool") != "create_thread"
        or capability.get("project_worktree_supported") is not True
        or capability.get("saved_project_id") != binding.get("saved_project_id")
    ):
        _fail("CTL_AUTHORIZATION_REQUIRED",
              "native project worktree capability is not proven")
    return {
        "code": "CTL_OK",
        "execute": True,
        "external_action_count": 1,
        "request": {
            "projectId": binding["saved_project_id"],
            "environment": {
                "type": "worktree",
                "startingState": {
                    "type": "branch",
                    "branchName": binding["starting_ref"],
                },
            },
        },
    }


def observe_pending_environment(
    binding: Mapping[str, Any],
    *,
    receipt: Mapping[str, Any],
    readback: Mapping[str, Any],
) -> dict[str, Any]:
    """Describe an acknowledged pending worktree without granting resend."""
    validate_native_create_binding(binding)
    receipt_field, pending_id = _receipt_identity(receipt)
    if (
        receipt_field != "pending_worktree_id"
        or readback.get("status") != "pending"
        or readback.get("pendingWorktreeId") != pending_id
    ):
        _fail("CTL_RECOVERY_REQUIRED",
              "pending native worktree receipt cannot be proven")
    return {
        "code": "CTL_NO_ACTION",
        "external_action_count": 0,
        "native_worktree_status": "pending",
        "pending_worktree_id": pending_id,
        "route_id": binding["route_id"],
        "operation_id": binding["operation_id"],
        "retry_allowed": False,
        "adopted": False,
    }


def record_native_environment_receipt(
    registry: dict[str, Any],
    dispatch: Mapping[str, Any],
    payload: Mapping[str, Any],
    lane_id: str,
) -> None:
    """Persist only a proven native receipt and pending lane state."""
    receipt = payload.get("receipt")
    if not isinstance(receipt, dict):
        _fail("CTL_DISPATCH_ACK_MISMATCH", "native environment receipt is invalid")
    _receipt_identity(receipt)
    from .contracts import canonical_digest

    if payload.get("receipt_digest") != canonical_digest(receipt):
        _fail("CTL_DISPATCH_ACK_MISMATCH", "native environment receipt is invalid")
    registry["lanes"][lane_id]["state"] = "developer_environment_pending"


def adopt_native_environment(
    binding: Mapping[str, Any],
    *,
    receipt: Mapping[str, Any],
    matches: Sequence[Mapping[str, Any]],
    readable: bool,
) -> dict[str, Any]:
    """Validate one complete native identity and return its exact binding."""
    validate_native_create_binding(binding)
    if not readable:
        _fail("CTL_RECOVERY_REQUIRED",
              "native environment read-back is unreadable")
    if len(matches) != 1:
        code = (
            "CTL_NATIVE_READBACK_AMBIGUOUS"
            if len(matches) > 1
            else "CTL_RECOVERY_REQUIRED"
        )
        _fail(code, "native environment adoption requires one match")
    observed = dict(matches[0])
    missing = object()
    for field, expected in binding.items():
        if observed.get(field, missing) != expected:
            _fail("CTL_DISPATCH_ACK_MISMATCH",
                  f"native environment {field} changed")
    if any(not observed.get(field) for field in _OBSERVED_REQUIRED):
        _fail("CTL_DISPATCH_ACK_MISMATCH",
              "native environment identity is incomplete")
    receipt_field, receipt_id = _receipt_identity(receipt)
    if observed.get(receipt_field) != receipt_id:
        _fail("CTL_DISPATCH_ACK_MISMATCH",
              "native receipt identity changed")
    branch = str(observed["branch"])
    if not branch.startswith(("codex/", "lane/")) or branch == binding["starting_ref"]:
        _fail("CTL_WORKTREE_MISMATCH", "native branch policy mismatch")
    if observed["base_commit"] != binding["expected_base_commit"] or (
        observed["head"] != binding["expected_primary_head"]
    ):
        _fail("CTL_WORKTREE_MISMATCH", "native base or HEAD changed")
    proofs = (
        "project_binding_verified",
        "prompt_markers_verified",
        "worktree_clean",
        "index_clean",
        "path_unique",
        "branch_unique",
    )
    if any(observed.get(field) is not True for field in proofs):
        _fail("CTL_WORKTREE_MISMATCH",
              "native environment topology is not exact and clean")
    return observed
