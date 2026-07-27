from __future__ import annotations

import hashlib
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from .contracts import CtlError


def frozen_completion_contract(
    authority: Mapping[str, Any], *, role: str
) -> dict[str, Any]:
    """Translate governance proof into the pre-role target contract."""
    if authority.get("role") != role:
        raise CtlError(
            "CTL_DISPATCH_ACK_MISMATCH",
            "completion authority role changed",
        )
    nullable = authority.get("nullable") is True
    frozen = {
        "completion_authority_nullable": nullable,
        "expected_evidence_path": authority.get("evidence_path"),
        "base_lane_head": authority.get("base_lane_head"),
        "allowed_changed_paths": list(authority.get("allowed_changed_paths", ())),
        "checkpoint_required": authority.get("checkpoint_required", not nullable),
    }
    try:
        validate_completion_contract({"role": role, "worktree_path": "pending", **frozen})
    except CtlError as exc:
        raise CtlError(
            "CTL_DISPATCH_ACK_MISMATCH",
            "completion authority contract is incomplete",
        ) from exc
    return frozen


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def validate_completion_contract(binding: Mapping[str, Any]) -> None:
    """Validate only facts that can exist before the role runs."""
    nullable = binding.get("completion_authority_nullable") is True
    if nullable:
        if (
            binding.get("role") != "User"
            or binding.get("expected_evidence_path") is not None
            or binding.get("base_lane_head") is not None
            or binding.get("checkpoint_required") is not False
            or binding.get("allowed_changed_paths") not in ([], ())
        ):
            raise CtlError(
                "CTL_CALLBACK_CONFLICT",
                "null completion authority is not permitted",
            )
        return
    required = (
        "worktree_path",
        "expected_evidence_path",
        "base_lane_head",
        "allowed_changed_paths",
    )
    if any(not binding.get(field) for field in required) or (
        binding.get("checkpoint_required") is not True
    ):
        raise CtlError(
            "CTL_CALLBACK_CONFLICT",
            "completion authority contract is incomplete",
        )
    if "expected_evidence_sha256" in binding or "expected_lane_head" in binding:
        raise CtlError(
            "CTL_CALLBACK_CONFLICT",
            "final completion authority cannot be frozen before dispatch",
        )


def observe_completion_authority(
    binding: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Read and attest post-role evidence and Git HEAD from the bound worktree."""
    validate_completion_contract(binding)
    if binding.get("completion_authority_nullable") is True:
        if any(
            payload.get(field) is not None
            for field in ("evidence_path", "evidence_sha256", "lane_head")
        ):
            raise CtlError(
                "CTL_CALLBACK_CONFLICT",
                "callback null authority changed",
            )
        return {
            "evidence_path": None,
            "evidence_sha256": None,
            "lane_head": None, "base_lane_head": None, "changed_paths": [],
        }
    expected_path = str(binding["expected_evidence_path"])
    if payload.get("evidence_path") != expected_path:
        raise CtlError("CTL_CALLBACK_CONFLICT", "callback evidence path changed")
    repo = Path(str(binding["worktree_path"])).resolve()
    relative = Path(expected_path)
    try:
        evidence = (repo / relative).resolve()
        evidence.relative_to(repo)
        if relative.is_absolute():
            raise ValueError("absolute evidence path")
        status = _git(repo, "status", "--porcelain=v1").stdout.splitlines()
        index = _git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
        actual_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
        base_head = str(binding["base_lane_head"])
        ancestry = _git(
            repo,
            "merge-base",
            "--is-ancestor",
            base_head,
            actual_head,
            check=False,
        )
        changed = _git(
            repo, "diff", "--name-only", f"{base_head}..{actual_head}"
        ).stdout.splitlines()
        actual_digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise CtlError(
            "CTL_CALLBACK_CONFLICT",
            "completion authority is unreadable",
        ) from exc
    allowed = {str(path).replace("\\", "/") for path in binding["allowed_changed_paths"]}
    changed_normalized = {path.replace("\\", "/") for path in changed}
    if (
        status
        or index
        or ancestry.returncode != 0
        or actual_head == base_head
        or not changed_normalized.issubset(allowed)
        or expected_path.replace("\\", "/") not in changed_normalized
        or payload.get("evidence_sha256") != actual_digest
        or payload.get("lane_head") != actual_head
    ):
        raise CtlError(
            "CTL_CALLBACK_CONFLICT",
            "completion authority does not match the bound role result",
        )
    return {
        "evidence_path": expected_path,
        "evidence_sha256": actual_digest,
        "lane_head": actual_head,
        "base_lane_head": base_head,
        "changed_paths": sorted(changed_normalized),
    }


def record_completion_callback(
    registry: dict[str, Any],
    dispatch: Mapping[str, Any],
    payload: Mapping[str, Any],
    lane_id: str,
) -> None:
    """Validate and atomically stage a callback plus observed authority."""
    from .callbacks import callback_event_id, completion_callback_result
    from .state_machine import apply_callback_proof

    event_id = str(payload.get("event_id", ""))
    if not event_id or event_id != callback_event_id(payload):
        raise CtlError("CTL_CALLBACK_CONFLICT", "callback event_id is not canonical")
    outcome, observation = completion_callback_result(registry, dispatch, payload)
    registry["callbacks"][event_id] = {
        **deepcopy(payload), "lane_id": lane_id, "completion_observation": observation}
    apply_callback_proof(registry, lane_id, payload, outcome)
    role_key = f"{lane_id}:{payload.get('role')}"
    if role_key in registry["role_bindings"]:
        registry["role_bindings"][role_key]["status"] = "completion_recorded"
