from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .completion_authority import observe_completion_authority
from .contracts import CtlError, canonical_digest
from .ownership import validate_recovery_binding


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def production_registry_root(repo_root: str) -> Path:
    common_dir = Path(
        _git(Path(repo_root), "rev-parse", "--git-common-dir").stdout.strip())
    if not common_dir.is_absolute():
        common_dir = Path(repo_root) / common_dir
    return common_dir.resolve() / "connlab-controlled-lane"


def verify_authority_files(repo: Path, files: Mapping[str, str]) -> dict[str, str]:
    if not files:
        raise CtlError("CTL_EVIDENCE_STALE", "scan requires frozen authority files")
    verified: dict[str, str] = {}
    root = repo.resolve()
    for relative, expected in sorted(files.items()):
        path = (root / relative).resolve()
        if root not in path.parents or not path.is_file():
            raise CtlError("CTL_EVIDENCE_STALE", f"authority file missing: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise CtlError("CTL_EVIDENCE_STALE", f"authority digest changed: {relative}")
        verified[relative] = actual
    return verified


def validate_exact_native_binding(
    expected: Mapping[str, Any] | None,
    observed: Mapping[str, Any] | None,
) -> None:
    if expected is None or observed is None:
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "native binding proof is required")
    required = (
        "task_id", "lane_id", "route_id", "operation_id",
        "payload_digest", "action_kind", "thread_id", "worktree_path",
    )
    if any(not expected.get(field) for field in required):
        raise CtlError(
            "CTL_DISPATCH_ACK_MISMATCH", "native target binding is incomplete")
    if dict(expected) != dict(observed):
        code = (
            "CTL_THREAD_BINDING_MISMATCH"
            if expected.get("thread_id") != observed.get("thread_id")
            else "CTL_DISPATCH_ACK_MISMATCH"
        )
        raise CtlError(code, "native target binding mismatch")


def inspect_git(repo: Path) -> dict[str, Any]:
    branch = _git(repo, "branch", "--show-current").stdout.strip()
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    status = _git(repo, "status", "--porcelain=v1").stdout.splitlines()
    index = _git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
    common_dir = Path(_git(repo, "rev-parse", "--git-common-dir").stdout.strip())
    if not common_dir.is_absolute():
        common_dir = repo / common_dir
    return {
        "branch": branch,
        "head": head,
        "status": status,
        "index": index,
        "git_common_dir": str(common_dir.resolve()),
    }


def preflight_create(
    repo: Path,
    *,
    branch: str,
    target: Path,
    base_ref: str,
    expected_primary_head: str,
) -> dict[str, Any]:
    facts = inspect_git(repo)
    if facts["status"]:
        return {"code": "CTL_PRIMARY_DIRTY", "zero_write": True, "facts": facts}
    if facts["index"]:
        return {"code": "CTL_INDEX_NOT_EMPTY", "zero_write": True, "facts": facts}
    if facts["head"] != expected_primary_head:
        return {"code": "CTL_HEAD_MISMATCH", "zero_write": True, "facts": facts}
    branch_result = _git(
        repo,
        "show-ref",
        "--verify",
        "--quiet",
        f"refs/heads/{branch}",
        check=False,
    )
    if branch_result.returncode == 0 or target.exists():
        return {
            "code": "CTL_WORKTREE_MISMATCH",
            "zero_write": True,
            "facts": facts,
        }
    if branch_result.returncode != 1:
        return {"code": "CTL_GIT_FAILED", "zero_write": True, "facts": facts}
    base = _git(repo, "rev-parse", base_ref).stdout.strip()
    return {
        "code": "CTL_OK",
        "zero_write": True,
        "facts": {**facts, "branch": branch, "target": str(target), "base": base},
    }


def preflight_adopt(
    repo: Path,
    *,
    expected_branch: str,
    expected_head: str,
    expected_common_dir: str,
    expected_base: str,
    expected_scope_fingerprint: str,
    observed_scope_fingerprint: str,
) -> dict[str, Any]:
    facts = inspect_git(repo)
    if (
        facts["branch"] != expected_branch
        or facts["head"] != expected_head
        or facts["git_common_dir"] != expected_common_dir
        or observed_scope_fingerprint != expected_scope_fingerprint
    ):
        return {"code": "CTL_WORKTREE_MISMATCH", "zero_write": True, "facts": facts}
    if facts["status"] or facts["index"]:
        return {"code": "CTL_WORKTREE_DIRTY", "zero_write": True, "facts": facts}
    ancestry = _git(
        repo, "merge-base", "--is-ancestor", expected_base, expected_head, check=False
    )
    if ancestry.returncode != 0:
        code = "CTL_WORKTREE_MISMATCH" if ancestry.returncode == 1 else "CTL_GIT_FAILED"
        return {"code": code, "zero_write": True, "facts": facts}
    return {"code": "CTL_OK", "zero_write": True, "facts": facts}


def preflight_retire(
    repo: Path,
    *,
    integration_ref: str,
    closeout_gates: dict[str, bool],
    primary_repo: Path | None = None,
    expected_topology: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    if expected_topology:
        adopted = preflight_adopt(
            repo,
            expected_branch=expected_topology["branch"],
            expected_head=expected_topology["head"],
            expected_common_dir=expected_topology["git_common_dir"],
            expected_base=expected_topology["base_commit"],
            expected_scope_fingerprint=expected_topology["scope_fingerprint"],
            observed_scope_fingerprint=expected_topology["scope_fingerprint"],
        )
        if adopted["code"] != "CTL_OK":
            return adopted
        facts = adopted["facts"]
    else:
        facts = inspect_git(repo)
    primary_facts = inspect_git(primary_repo or repo)
    gates = {
        **closeout_gates,
        "primary_clean": not primary_facts["status"] and not primary_facts["index"],
    }
    facts["primary"] = primary_facts
    required = (
        "residuals_clear",
        "owners_released",
        "callbacks_clear",
        "recovery_clear",
        "active_tasks_clear",
        "primary_clean",
    )
    if not all(gates.get(gate) is True for gate in required):
        return {"code": "CTL_RECOVERY_REQUIRED", "zero_write": True, "facts": facts}
    if facts["status"] or facts["index"]:
        return {"code": "CTL_WORKTREE_DIRTY", "zero_write": True, "facts": facts}
    ancestry = _git(
        repo,
        "merge-base",
        "--is-ancestor",
        facts["head"],
        integration_ref,
        check=False,
    )
    if ancestry.returncode == 1:
        return {"code": "CTL_UNINTEGRATED_HEAD", "zero_write": True, "facts": facts}
    if ancestry.returncode != 0:
        return {"code": "CTL_GIT_FAILED", "zero_write": True, "facts": facts}
    return {"code": "CTL_OK", "zero_write": True, "facts": facts}


def registry_closeout_gates(
    registry: dict[str, Any], lane_id: str
) -> dict[str, bool]:
    lane = registry["lanes"].get(lane_id, {})
    closeout = lane.get("closeout", {})
    active_owner = any(
        item.get("lane_id") == lane_id for item in registry["shared_owners"].values())
    pending_callback = any(
        item.get("lane_id") == lane_id and not item.get("consumed_at")
        for item in registry["callbacks"].values())
    active_task = any(
        item.get("lane_id") == lane_id and item.get("status") in ("active", "dispatching")
        for item in registry["role_bindings"].values())
    return {
        "residuals_clear": (
            closeout.get("residual_ledger_status") == "resolved"
            and bool(closeout.get("residual_ledger_digest"))
        ),
        "owners_released": not active_owner,
        "callbacks_clear": not pending_callback,
        "recovery_clear": not registry["recovery_points"],
        "active_tasks_clear": not active_task,
    }


def registry_retire_facts(
    registry: dict[str, Any], lane_id: str
) -> tuple[Path, Path, str, dict[str, bool], dict[str, str]]:
    lane = registry["lanes"].get(lane_id, {})
    worktree = registry["worktrees"].get(lane_id, {})
    required = {
        "worktree_path": worktree.get("worktree_path"),
        "primary_repo_root": lane.get("primary_repo_root"),
        "integration_ref": lane.get("integration_ref"),
    }
    if any(not value for value in required.values()):
        raise CtlError("CTL_TOPOLOGY_STALE", "retirement topology is incomplete")
    return (
        Path(str(required["worktree_path"])),
        Path(str(required["primary_repo_root"])),
        str(required["integration_ref"]),
        registry_closeout_gates(registry, lane_id),
        {field: str(worktree.get(field, "")) for field in (
            "branch", "head", "git_common_dir", "base_commit", "scope_fingerprint")},
    )


def verify_callback_authority(
    binding: Mapping[str, Any], payload: Mapping[str, Any]
) -> dict[str, Any]:
    return observe_completion_authority(binding, payload)


def recovery_decision(
    *, stage: str, invocation_may_have_started: bool,
    readback_matches: int, readback_readable: bool,
) -> dict[str, Any]:
    if stage == "prepared" and not invocation_may_have_started:
        return {"code": "CTL_OK", "action": "retry_same_operation", "resend": True}
    if invocation_may_have_started:
        if not readback_readable:
            return {"code": "CTL_RECOVERY_REQUIRED",
                    "action": "manual_recovery", "resend": False}
        if readback_matches == 1:
            return {"code": "CTL_OK", "action": "adopt_exact_match", "resend": False}
        code = "CTL_NATIVE_READBACK_AMBIGUOUS" if readback_matches > 1 else (
            "CTL_RECOVERY_REQUIRED")
        return {"code": code, "action": "manual_recovery", "resend": False}
    return {"code": "CTL_RECOVERY_REQUIRED",
            "action": "manual_recovery", "resend": False}


def verified_recovery_decision(
    dispatch: Mapping[str, Any], payload: Mapping[str, Any]
) -> dict[str, Any]:
    stage = str(dispatch.get("stage"))
    matches = int(payload.get("readback_matches", 0))
    if matches == 1:
        observed = payload.get("readback_binding")
        if not isinstance(observed, dict) or (
            payload.get("readback_digest") != canonical_digest(observed)
        ):
            matches = 0
        else:
            try:
                validate_recovery_binding(dispatch, observed)
            except CtlError:
                matches = 0
    return recovery_decision(
        stage=stage, invocation_may_have_started=stage != "prepared",
        readback_matches=matches,
        readback_readable=bool(payload.get("readback_readable")))
