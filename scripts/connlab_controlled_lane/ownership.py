from __future__ import annotations

import posixpath
import re
from copy import deepcopy
from typing import Any, Iterable, Mapping

from .contracts import (
    CtlError, canonical_digest, validate_dispatch_binding,
    validate_recovery_binding, validate_target_binding,
)
from .native_environment import adopt_native_environment

_GLOB_RE = re.compile(r"[*?\[\]{}]")
_GATE_PROOF_KEYS = {
    "plan_review_pending": "review_status", "planner_fix_pending": "planner_status",
    "user_planning_approval_pending": "user_approved", "developer_planning_active": "developer_status",
    "planner_reconciliation_pending": "planner_status", "review_pending": "review_status",
    "implementation_readiness_pending": "readiness_status",
    "user_implementation_approval_pending": "user_approved",
    "developer_active": "developer_status", "developer_fix_active": "developer_status",
    "qa_pending": "qa_status", "integration_pending": "integrator_status",
}


def normalize_repo_path(value: str) -> str:
    raw = value.strip().replace("\\", "/")
    if not raw or raw.startswith("/") or re.match(r"^[A-Za-z]:", raw):
        raise CtlError("CTL_SCOPE_VIOLATION", f"path is not repository-relative: {value}")
    if _GLOB_RE.search(raw):
        raise CtlError("CTL_SCOPE_VIOLATION", f"globs are not lockable: {value}")
    normalized = posixpath.normpath(raw)
    if normalized in (".", "..") or normalized.startswith("../"):
        raise CtlError("CTL_SCOPE_VIOLATION", f"path escapes repository: {value}")
    return normalized.casefold()


def normalize_authority(value: str) -> str:
    segments = [segment.strip().casefold() for segment in value.split(".")]
    if not segments or any(not segment for segment in segments):
        raise CtlError("CTL_SCOPE_VIOLATION", f"invalid authority key: {value}")
    return ".".join(segments)


def validate_governance_owner(path: str, *, role: str) -> None:
    normalized = normalize_repo_path(path)
    if normalized == "docs/task_board.md" and role not in ("Planner", "Integrator"):
        raise CtlError("CTL_OWNER_CONFLICT",
                       "task board mutation is reserved for Planner or Integrator")


def validate_owner_acquisition(registry: Mapping[str, Any], lane_id: str, dispatch: Mapping[str, Any]) -> None:
    lane = registry["lanes"][lane_id]
    claims = lane.get("owner_claims", [])
    target = dispatch.get("target_binding", {})
    if target.get("owner_claims_digest") != canonical_digest(claims):
        raise CtlError("CTL_SCOPE_VIOLATION", "prepared owner claims changed")
    requested = lane.get("requested_scope", {})
    claimed = {kind: [value for claim in claims for value in claim.get(kind, ())]
               for kind in ("paths", "directories", "authorities")}
    normalizers = {"paths": normalize_repo_path, "directories": normalize_repo_path,
                   "authorities": normalize_authority}
    if any({normalizers[kind](value) for value in requested.get(kind, ())} !=
           {normalizers[kind](value) for value in claimed[kind]} for kind in claimed):
        raise CtlError("CTL_SCOPE_VIOLATION", "owner claims do not match lane scope")
    expected = {
        claim["key"]: _materialized_owner(claim, lane_id, target)
        for claim in claims
    }
    for key, owner in registry["shared_owners"].items():
        overlaps = find_owner_conflicts(requested, [owner])
        if owner.get("lane_id") != lane_id:
            if overlaps:
                raise CtlError("CTL_OWNER_CONFLICT", "requested ownership is already held",
                               {"conflicts": overlaps})
            continue
        expected_owner = expected.get(key)
        if expected_owner is None or _canonical_owner(owner) != _canonical_owner(expected_owner):
            raise CtlError("CTL_OWNER_CONFLICT",
                           "same-lane owner identity is not canonical")


def _materialized_owner(
    claim: Mapping[str, Any], lane_id: str, target: Mapping[str, Any]
) -> dict[str, Any]:
    identity = {field: target.get(field) for field in (
        "scope_fingerprint", "worktree_path", "branch", "thread_id", "operation_id")}
    return {**deepcopy(claim), **identity, "lane_id": lane_id}


def _canonical_owner(owner: Mapping[str, Any]) -> str:
    value = dict(owner)
    for key in ("paths", "directories"):
        value[key] = sorted(normalize_repo_path(item) for item in owner.get(key, ()))
    value["authorities"] = sorted(
        normalize_authority(item) for item in owner.get("authorities", ()))
    return canonical_digest(value)


def materialize_owner_acquisition(
    registry: dict[str, Any], lane_id: str, target: Mapping[str, Any]
) -> None:
    lane = registry["lanes"][lane_id]
    registry.setdefault("worktrees", {})[lane_id] = deepcopy(target)
    for claim in lane.get("owner_claims", []):
        owner = _materialized_owner(claim, lane_id, target)
        current = registry["shared_owners"].get(claim["key"])
        if current is None:
            registry["shared_owners"][claim["key"]] = owner
        elif _canonical_owner(current) != _canonical_owner(owner):
            raise CtlError("CTL_OWNER_CONFLICT", "owner changed during materialization")


def adopt_and_materialize_native_owner(
    registry: dict[str, Any],
    lane_id: str,
    dispatch: dict[str, Any],
    payload: Mapping[str, Any],
) -> None:
    observed = payload.get("readback_binding")
    if not isinstance(observed, dict) or payload.get(
        "readback_digest") != canonical_digest(observed):
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH",
                       "native read-back digest changed")
    recorded = dispatch.get("action_result_payload", {})
    exact = adopt_native_environment(
        dispatch["target_binding"], receipt=recorded.get("receipt", {}),
        matches=[observed], readable=payload.get("readback_readable") is True)
    exact_dispatch = {**dispatch, "target_binding": exact}
    validate_owner_acquisition(registry, lane_id, exact_dispatch)
    materialize_owner_acquisition(registry, lane_id, exact)
    dispatch["target_binding"] = exact


def apply_advance_effects(
    registry: dict[str, Any], lane_id: str,
    dispatch: Mapping[str, Any], to_state: str,
) -> None:
    lane = registry["lanes"][lane_id]
    target = deepcopy(dispatch["target_binding"])
    action = dispatch.get("action_kind")
    if (to_state, action) in (
        ("worktree_ready", "create_or_adopt_worktree"),
        ("developer_active", "create_developer_environment"),
    ):
        materialize_owner_acquisition(registry, lane_id, target)
    if action in (
        "dispatch_role", "create_developer_environment",
        "send_existing_task", "request_user_approval",
    ):
        role = target.get("role")
        registry.setdefault("role_bindings", {})[f"{lane_id}:{role}"] = {
            **target, "lane_id": lane_id, "status": "active"}
    if to_state == "closeout_pending" and action == "governance_closeout":
        closeout = target.get("closeout")
        if not isinstance(closeout, dict):
            raise CtlError("CTL_RECOVERY_REQUIRED", "closeout evidence is missing")
        lane["closeout"] = closeout
        for key in set(closeout.get("released_owner_keys", [])):
            owner = registry["shared_owners"].get(key)
            if owner and owner.get("lane_id") == lane_id:
                del registry["shared_owners"][key]
        for event_id in closeout.get("consumed_callback_ids", []):
            callback = registry["callbacks"].get(event_id)
            if callback and callback.get("lane_id") == lane_id:
                callback["consumed_at"] = "closeout"
    if to_state == "retired":
        registry["worktrees"].pop(lane_id, None)
        for binding in registry["role_bindings"].values():
            if binding.get("lane_id") == lane_id:
                binding["status"] = "retired"


def reset_gate_proof(lane: dict[str, Any], to_state: str) -> None:
    key = _GATE_PROOF_KEYS.get(to_state)
    if key:
        lane.setdefault("proof", {}).pop(key, None)


def _path_overlaps(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(f"{prefix}/") or prefix.startswith(f"{path}/")


def _authority_overlaps(left: str, right: str) -> bool:
    return left == right or left.startswith(f"{right}.") or right.startswith(f"{left}.")


def find_owner_conflicts(
    requested: Mapping[str, Iterable[str]],
    owners: Iterable[Mapping[str, Any]],
) -> list[dict[str, str]]:
    requested_paths = {normalize_repo_path(value) for value in (
        *requested.get("paths", ()), *requested.get("directories", ()))}
    requested_authorities = {normalize_authority(value)
                             for value in requested.get("authorities", ())}
    conflicts: list[dict[str, str]] = []
    for owner in owners:
        owner_paths = {normalize_repo_path(value) for value in (
            *owner.get("paths", ()), *owner.get("directories", ()))}
        owner_authorities = {normalize_authority(value)
                             for value in owner.get("authorities", ())}
        for requested_path in sorted(requested_paths):
            for owner_path in sorted(owner_paths):
                if _path_overlaps(requested_path, owner_path):
                    conflicts.append({
                        "kind": "path", "lane_id": str(owner.get("lane_id", "")),
                        "requested": requested_path, "owned": owner_path})
        for requested_key in sorted(requested_authorities):
            for owner_key in sorted(owner_authorities):
                if _authority_overlaps(requested_key, owner_key):
                    conflicts.append({
                        "kind": "authority", "lane_id": str(owner.get("lane_id", "")),
                        "requested": requested_key, "owned": owner_key})
    return conflicts


def scope_fingerprint(*, task_id: str, lane_id: str, base_commit: str,
                      may_touch: Iterable[str], locked_paths: Iterable[str],
                      authorities: Iterable[str]) -> str:
    payload = {
        "task_id": task_id, "lane_id": lane_id, "base_commit": base_commit,
        "may_touch": sorted({normalize_repo_path(path) for path in may_touch}),
        "locked_paths": sorted({normalize_repo_path(path) for path in locked_paths}),
        "authorities": sorted({normalize_authority(key) for key in authorities}),
    }
    return canonical_digest(payload)
