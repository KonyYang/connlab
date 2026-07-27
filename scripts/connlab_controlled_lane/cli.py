from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .callbacks import verified_recovery_decision
from .contracts import (
    MUTATION_COMMANDS, READ_ONLY_COMMANDS, CtlError, canonical_json,
    exit_code_for, result, validate_common_request)
from .git_preflight import (
    inspect_git, preflight_adopt, preflight_create, preflight_retire,
    production_registry_root, registry_retire_facts, verify_authority_files)
from .native_environment import observe_pending_environment
from .ownership import find_owner_conflicts
from .registry import RegistryStore
from .state_machine import select_next_action


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=sorted(READ_ONLY_COMMANDS | set(MUTATION_COMMANDS)))
    parser.add_argument("--request-json", required=True)
    parser.add_argument("--registry-root")
    parser.add_argument("--allow-test-registry-root", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def _read_request(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    if not isinstance(value, dict):
        raise CtlError("CTL_INVALID_REQUEST", "request must be a JSON object")
    return value


def _store(root: Path, request: dict[str, Any]) -> RegistryStore:
    fingerprint = request.get("repository_fingerprint", request["scope_fingerprint"])
    return RegistryStore(root, repository_fingerprint=str(fingerprint))


def _read_only(command: str, request: dict[str, Any], root: Path) -> dict[str, Any]:
    if command == "recover":
        store = _store(root, request)
        dispatch = store.load()["dispatches"].get(request["operation_id"])
        if not dispatch:
            decision = {
                "code": "CTL_RECOVERY_REQUIRED",
                "action": "manual_recovery",
                "resend": False,
            }
            return result(
                code=decision["code"], request=request,
                message="durable dispatch is missing", zero_write=True,
                recovery=decision,
            )
        decision = verified_recovery_decision(dispatch, request["payload"])
        return result(
            code=decision["code"],
            request=request,
            message="recovery decision",
            zero_write=True,
            recovery=decision,
        )
    if command == "scan":
        registry = _store(root, request).load()
        lane = registry["lanes"].get(request["lane_id"])
        if not lane:
            raise CtlError("CTL_LANE_NOT_AUTHORIZED", "lane is absent from registry")
        if lane.get("scope_fingerprint") != request["scope_fingerprint"]:
            raise CtlError("CTL_SCOPE_VIOLATION", "lane scope fingerprint changed")
        if not lane.get("primary_repo_root"):
            raise CtlError("CTL_TOPOLOGY_STALE", "primary repository binding is missing")
        repo = Path(str(lane["primary_repo_root"]))
        git_facts = inspect_git(repo)
        if git_facts["status"]:
            return result(
                code="CTL_PRIMARY_DIRTY", request=request,
                message="primary worktree is dirty", zero_write=True, facts=git_facts,
            )
        if git_facts["index"]:
            return result(
                code="CTL_INDEX_NOT_EMPTY", request=request,
                message="primary index is not empty", zero_write=True, facts=git_facts,
            )
        authority = verify_authority_files(
            repo, dict(lane.get("authority_files", {})))
        if registry["recovery_points"]:
            raise CtlError("CTL_RECOVERY_REQUIRED", "registry has unresolved recovery points")
        active = [dispatch for dispatch in registry["dispatches"].values()
                  if dispatch.get("lane_id") == request["lane_id"]
                  and dispatch.get("stage") != "advanced"]
        if active:
            if (
                len(active) == 1
                and lane.get("state") == "developer_environment_pending"
                and active[0].get("action_kind") == "create_developer_environment"
                and active[0].get("stage") == "result_recorded"
            ):
                dispatch = active[0]
                recorded = dispatch.get("action_result_payload", {})
                pending = observe_pending_environment(
                    dispatch.get("target_binding", {}),
                    receipt=recorded.get("receipt", {}),
                    readback=request["payload"].get("native_environment_readback", {}),
                )
                return result(
                    code=pending.pop("code"), request=request,
                    message="native worktree creation remains pending",
                    zero_write=True, state=lane.get("state"), **pending)
            raise CtlError("CTL_RECOVERY_REQUIRED", "lane has an unfinished dispatch")
        owners = [owner for owner in registry["shared_owners"].values()
                  if owner.get("lane_id") != request["lane_id"]]
        conflicts = find_owner_conflicts(
            lane.get("requested_scope", {}), owners
        )
        if conflicts:
            return result(
                code="CTL_OWNER_CONFLICT", request=request,
                message="requested scope conflicts with active owner",
                zero_write=True, conflicts=conflicts,
            )
        state = lane.get("state")
        action = select_next_action(str(state), lane.get("proof", {}))
        return result(
            code="CTL_OK", request=request, message="one legal next action selected",
            zero_write=True, state=state,
            facts={**git_facts, "authority_files": authority}, next_action=action,
        )
    if command == "route-plan":
        action = select_next_action(
            str(request["payload"]["state"]),
            request["payload"].get("proof", {}),
        )
        return result(
            code="CTL_OK",
            request=request,
            message="one legal next action selected",
            zero_write=True,
            next_action=action,
        )
    if command == "worktree-preflight":
        payload = request["payload"]
        repo = Path(str(request.get("repo_root", ".")))
        if payload.get("action") == "create":
            decision = preflight_create(
                repo,
                branch=str(payload["branch"]),
                target=Path(str(payload["target"])),
                base_ref=str(payload["base_ref"]),
                expected_primary_head=str(payload["expected_primary_head"]),
            )
        elif payload.get("action") == "adopt":
            decision = preflight_adopt(
                Path(str(payload["target"])),
                expected_branch=str(payload["branch"]),
                expected_head=str(payload["expected_head"]),
                expected_common_dir=str(payload["expected_common_dir"]),
                expected_base=str(payload["expected_base"]),
                expected_scope_fingerprint=str(payload["expected_scope_fingerprint"]),
                observed_scope_fingerprint=str(payload["observed_scope_fingerprint"]),
            )
        else:
            raise CtlError("CTL_INVALID_REQUEST", "unsupported worktree preflight action")
        return result(
            code=str(decision["code"]),
            request=request,
            message="worktree preflight",
            zero_write=True,
            facts=decision.get("facts", {}),
        )
    if command in ("integration-preflight", "retire-preflight"):
        payload = request["payload"]
        gates = dict(payload.get("closeout_gates", {}))
        repo_path = Path(str(request.get("repo_root", ".")))
        integration_ref = str(payload["integration_ref"])
        primary_repo = repo_path
        topology = None
        if command == "retire-preflight":
            facts = registry_retire_facts(_store(root, request).load(), request["lane_id"])
            repo_path, primary_repo, integration_ref, gates, topology = facts
        decision = preflight_retire(
            repo_path, integration_ref=integration_ref,
            closeout_gates=gates, primary_repo=primary_repo, expected_topology=topology,
        )
        return result(
            code=str(decision["code"]),
            request=request,
            message=command,
            zero_write=True,
            facts=decision.get("facts", {}),
        )
    if command == "registry-status":
        store = _store(root, request)
        registry = store.load()
        return result(
            code="CTL_OK",
            request=request,
            message="registry status",
            zero_write=True,
            facts={
                "registry_generation": registry["generation"],
                "registry_exists": store.path.exists(),
            },
        )
    return result(
        code="CTL_NO_ACTION",
        request=request,
        message="read-only preflight produced no external action",
        zero_write=True,
    )


def run(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    request: dict[str, Any] = {}
    try:
        request = _read_request(args.request_json)
        request.setdefault("command", args.command)
        if args.dry_run:
            request["dry_run"] = True
        validate_common_request(request, args.command)
        if args.registry_root:
            if not args.allow_test_registry_root:
                raise CtlError(
                    "CTL_SCOPE_VIOLATION",
                    "custom registry root requires --allow-test-registry-root",
                )
            root = Path(args.registry_root)
        else:
            root = production_registry_root(str(request.get("repo_root", ".")))
        if args.command in MUTATION_COMMANDS:
            if args.command == "prepare-dispatch" and not request.get("dry_run"):
                preflight = _read_only("scan", request, root)
                if preflight["code"] != "CTL_OK":
                    output = preflight
                elif preflight["next_action"]["kind"] != request["payload"].get("action_kind"):
                    raise CtlError("CTL_INVALID_TRANSITION",
                                   "prepare action differs from authoritative scan")
                else:
                    output = _store(root, request).execute(args.command, request)
            else:
                output = _store(root, request).execute(args.command, request)
        else:
            output = _read_only(args.command, request, root)
    except (CtlError, json.JSONDecodeError, OSError, subprocess.SubprocessError) as exc:
        if isinstance(exc, CtlError):
            code = exc.code
            message = exc.message
        else:
            code = "CTL_INVALID_REQUEST"
            message = str(exc)
        output = result(
            code=code,
            request=request,
            message=message,
            zero_write=True,
        )
    sys.stdout.write(f"{canonical_json(output)}\n")
    return exit_code_for(output["code"])


if __name__ == "__main__":
    raise SystemExit(run())
