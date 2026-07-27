from __future__ import annotations

import json
import os
import socket
import subprocess
import tempfile
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .bootstrap import (BOOTSTRAP_ACTIONS, adopt_bootstrap_readback,
                         apply_admin_mutation, validate_bootstrap_ack,
                         validate_bootstrap_request)
from .completion_authority import record_completion_callback
from .contracts import (ADMIN_COMMANDS, CtlError, canonical_digest, canonical_json,
                        convert_v1_to_v2, initial_registry, result,
                         validate_common_request)
from .git_preflight import inspect_git, verify_authority_files
from .ownership import (
    adopt_and_materialize_native_owner, apply_advance_effects, reset_gate_proof,
    validate_dispatch_binding, validate_owner_acquisition,
)
from .native_environment import record_native_environment_receipt
from .state_machine import (
    validate_advance_authority, validate_authoritative_dispatch, validate_transition)

_STAGE_REQUIREMENTS = {
    "mark-invocation-started": "prepared",
    "record-action-result": "invocation_started",
    "ack-dispatch": ("sent", "result_recorded"),
    "advance-state": "acknowledged",
}
_FINGERPRINT_FIELDS = ("task_id", "lane_id", "operation_id", "route_id",
                       "idempotency_key", "scope_fingerprint", "payload")
_REGISTRY_FIELDS = (
    "registry_id", "git_common_dir_fingerprint", "generation", "created_at",
    "updated_at", "migration", "lanes", "worktrees", "shared_owners",
    "role_bindings", "dispatches", "callbacks", "recovery_points", "idempotency",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RegistryStore:
    def __init__(self, root: Path, *, repository_fingerprint: str) -> None:
        self.root = Path(root)
        self.path = self.root / "registry-v2.json"
        self.lock_path = self.root / "registry-v2.lock"
        self.recovery_path = self.root / "registry-v2.recovery.json"
        self.repository_fingerprint = repository_fingerprint

    def load(self) -> dict[str, Any]:
        if self.recovery_path.exists():
            raise CtlError("CTL_RECOVERY_REQUIRED", "registry recovery marker unresolved")
        if not self.path.exists():
            return initial_registry(self.repository_fingerprint)
        try:
            registry = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CtlError("CTL_REGISTRY_SCHEMA_MISMATCH", "registry is unreadable") from exc
        if registry.get("schema_version") != 2:
            raise CtlError("CTL_REGISTRY_SCHEMA_MISMATCH", "registry schema must be v2")
        if registry.get("repository_fingerprint") != self.repository_fingerprint:
            raise CtlError("CTL_REGISTRY_SCHEMA_MISMATCH", "repository fingerprint mismatch")
        if any(field not in registry for field in _REGISTRY_FIELDS):
            raise CtlError("CTL_REGISTRY_SCHEMA_MISMATCH", "registry is partial")
        if any(not isinstance(registry[field], dict) for field in _REGISTRY_FIELDS[6:]):
            raise CtlError("CTL_REGISTRY_SCHEMA_MISMATCH", "registry maps are invalid")
        return registry
    def execute(self, command: str, request: Mapping[str, Any]) -> dict[str, Any]:
        try:
            validate_common_request(request, command)
            if command == "bootstrap-registry":
                self._preflight_bootstrap(request)
            if request.get("dry_run"):
                if command in ADMIN_COMMANDS:
                    validate_bootstrap_request(command, request)
                return result(
                    code="CTL_DRY_RUN", request=request,
                    message="validated without registry write", zero_write=True,
                    facts={"external_action_count": 0},
                )
            return self._execute_locked(command, request)
        except CtlError as exc:
            return result(
                code=exc.code, request=request, message=exc.message,
                zero_write=exc.code != "CTL_POST_WRITE_VERIFY_FAILED",
                facts=dict(exc.facts or {}),
            )
    def _preflight_bootstrap(self, request: Mapping[str, Any]) -> None:
        validate_bootstrap_request("bootstrap-registry", request)
        if self.recovery_path.exists():
            raise CtlError("CTL_RECOVERY_REQUIRED", "registry recovery marker unresolved")
        if self.lock_path.exists():
            raise CtlError("CTL_LOCK_BUSY", "registry lock is already held")
        payload = request["payload"]
        repo_value = request.get("repo_root")
        if not repo_value:
            raise CtlError("CTL_INVALID_REQUEST", "repo_root is required")
        try:
            repo = Path(str(repo_value)).resolve(strict=True)
            facts = inspect_git(repo)
        except (OSError, subprocess.SubprocessError) as exc:
            raise CtlError("CTL_TOPOLOGY_STALE", "bootstrap repository is unreadable") from exc
        fingerprint = canonical_digest({"git_common_dir": facts["git_common_dir"]})
        controller = payload["controller"]
        if (
            Path(str(payload["primary_repo_root"])).resolve() != repo
            or Path(str(controller["project_path"])).resolve() != repo
            or request.get("repository_fingerprint") != fingerprint
            or self.repository_fingerprint != fingerprint
            or controller.get("repository_fingerprint") != fingerprint
        ):
            raise CtlError("CTL_TOPOLOGY_STALE", "bootstrap repository identity changed")
        if facts["status"]:
            raise CtlError("CTL_PRIMARY_DIRTY", "bootstrap repository is dirty")
        if facts["index"]:
            raise CtlError("CTL_INDEX_NOT_EMPTY", "bootstrap index is not empty")
        verify_authority_files(repo, payload["authority_files"])
        legacy = payload["legacy_inventory"]
        verify_authority_files(repo, {str(legacy.get("source")):
                                      str(legacy.get("source_digest"))})
    def _execute_locked(self, command: str, request: Mapping[str, Any]) -> dict[str, Any]:
        self.root.mkdir(parents=True, exist_ok=True)
        token = str(uuid.uuid4())
        try:
            self._acquire_lock(token)
        except FileExistsError:
            raise CtlError("CTL_LOCK_BUSY", "registry lock is already held")
        try:
            registry = self.load()
            return self._apply_and_write(registry, command, request)
        finally:
            self._release_lock(token)
    def _acquire_lock(self, token: str) -> None:
        descriptor = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        body = canonical_json({
            "token": token, "pid": os.getpid(),
            "host": socket.gethostname(), "created_at": _utc_now(),
        })
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(f"{body}\n")
            handle.flush()
            os.fsync(handle.fileno())
    def _release_lock(self, token: str) -> None:
        if not self.lock_path.exists():
            return
        try:
            current = json.loads(self.lock_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if current.get("token") == token:
            self.lock_path.unlink()
    def _apply_and_write(self, registry: dict[str, Any], command: str, request: Mapping[str, Any]) -> dict[str, Any]:
        fingerprint = canonical_digest({
            field: request[field] for field in _FINGERPRINT_FIELDS
        } | {"command": command})
        ledger_key = f"{command}:{request['idempotency_key']}"
        existing = registry["idempotency"].get(ledger_key)
        if existing:
            if existing["fingerprint"] != fingerprint:
                raise CtlError("CTL_IDEMPOTENCY_CONFLICT",
                               "idempotency key reused with different input")
            stored = deepcopy(existing["result"])
            stored.update(code="CTL_ALREADY_APPLIED", ok=True,
                          message="canonical mutation already applied", zero_write=True)
            return stored
        current_generation = int(registry["generation"])
        if request["expected_registry_generation"] != current_generation:
            raise CtlError("CTL_CAS_CONFLICT", "expected registry generation is stale",
                           {"registry_generation": current_generation})
        durable_stage = (
            apply_admin_mutation(
                registry, command, request, registry_exists=self.path.exists()
            )
            if command in ADMIN_COMMANDS
            else self._apply_mutation(registry, command, request)
        )
        next_generation = current_generation + 1
        registry["generation"] = next_generation
        registry["updated_at"] = _utc_now()
        record_digest = canonical_digest({
            "command": command, "operation_id": request["operation_id"],
            "generation": next_generation, "stage": durable_stage,
            "fingerprint": fingerprint,
        })
        output = result(
            code="CTL_OK", request=request, message="registry mutation recorded",
            zero_write=False, old_generation=current_generation,
            new_generation=next_generation, durable_stage=durable_stage,
            record_digest=record_digest,
            facts={"external_action_count": 0},
            state=registry["lanes"].get(request["lane_id"], {}).get("state"),
        )
        registry["idempotency"][ledger_key] = {
            "fingerprint": fingerprint, "result": deepcopy(output)}
        self._atomic_write(registry)
        return output
    def _apply_mutation(self, registry: dict[str, Any], command: str, request: Mapping[str, Any]) -> str:
        operation_id = str(request["operation_id"])
        payload = request["payload"]
        dispatches = registry["dispatches"]
        if command == "prepare-dispatch":
            state, _ = validate_authoritative_dispatch(registry, request, payload)
            target = payload.get("target_binding")
            if operation_id in dispatches:
                raise CtlError("CTL_DISPATCH_STAGE_MISMATCH", "dispatch already exists")
            dispatches[operation_id] = {
                "task_id": request["task_id"], "lane_id": request["lane_id"],
                "route_id": request["route_id"], "operation_id": operation_id,
                "scope_fingerprint": request["scope_fingerprint"],
                "payload_digest": request["payload_digest"],
                "current_state": state,
                "action_kind": payload.get("action_kind"),
                "target_binding": deepcopy(target),
                "stage": "prepared", "events": ["dispatch_prepare"],
            }
            return "prepared"
        if command == "record-callback":
            dispatch_operation = str(payload.get("dispatch_operation_id", ""))
            dispatch = dispatches.get(dispatch_operation)
            if not dispatch or dispatch.get("stage") != "advanced":
                raise CtlError("CTL_ROLE_CALLBACK_STATE_MISMATCH",
                               "completion requires an advanced dispatch")
            validate_dispatch_binding(dispatch, request, command)
            record_completion_callback(
                registry, dispatch, payload, str(request["lane_id"]))
            return "completion_recorded"
        dispatch = dispatches.get(operation_id)
        if not dispatch:
            raise CtlError("CTL_DISPATCH_STAGE_MISMATCH", "prepared dispatch is missing")
        if command == "ack-dispatch" and dispatch.get("action_kind") in BOOTSTRAP_ACTIONS:
            if any(dispatch.get(field) != request.get(field) for field in (
                "task_id", "lane_id", "route_id", "scope_fingerprint")):
                raise CtlError("CTL_DISPATCH_ACK_MISMATCH",
                               "ack-dispatch does not match prepared dispatch")
            validate_bootstrap_ack(dispatch, payload)
        else:
            validate_dispatch_binding(dispatch, request, command)
        if command == "ack-dispatch":
            recorded = dispatch.get("action_result_payload", {})
            changed = [field for field in ("receipt_digest", "git_observation_digest")
                       if recorded.get(field) and payload.get(field) != recorded.get(field)]
            if changed:
                raise CtlError("CTL_DISPATCH_ACK_MISMATCH",
                               f"acknowledgement {changed[0]} changed")
            if dispatch.get("action_kind") == "create_developer_environment":
                adopt_and_materialize_native_owner(
                    registry, str(request["lane_id"]), dispatch, payload)
            elif dispatch.get("action_kind") in BOOTSTRAP_ACTIONS:
                adopt_bootstrap_readback(
                    registry, str(request["lane_id"]), dispatch, payload)
        required_stage = _STAGE_REQUIREMENTS[command]
        allowed = required_stage if isinstance(required_stage, tuple) else (required_stage,)
        if dispatch.get("stage") not in allowed:
            raise CtlError("CTL_DISPATCH_STAGE_MISMATCH",
                           f"{command} requires stage {'/'.join(allowed)}")
        if command == "mark-invocation-started":
            stage = "invocation_started"
            event = "invocation_start"
        elif command == "record-action-result":
            stage = str(payload.get("result_stage", ""))
            if stage not in ("sent", "result_recorded"):
                raise CtlError("CTL_INVALID_REQUEST", "result_stage is invalid")
            if dispatch.get("action_kind") == "create_developer_environment":
                record_native_environment_receipt(
                    registry, dispatch, payload, str(request["lane_id"]))
            event = "action_result"
        elif command == "ack-dispatch":
            stage = "acknowledged"
            event = "dispatch_ack"
        else:
            if dispatch.get("action_kind") == "create_developer_environment" and (
                payload.get("from_state")
                != registry["lanes"][str(request["lane_id"])].get("state")
            ):
                raise CtlError("CTL_DISPATCH_ACK_MISMATCH",
                               "state advance does not start from active lane state")
            validate_advance_authority(
                registry, str(request["lane_id"]), str(payload.get("from_state")),
                str(request["scope_fingerprint"]))
            validate_transition(str(payload.get("from_state")), str(payload.get("to_state")))
            if payload.get("to_state") in ("worktree_ready", "developer_active"):
                validate_owner_acquisition(registry, str(request["lane_id"]), dispatch)
            stage = "advanced"
            event = "state_advance"
            lane = registry["lanes"].setdefault(str(request["lane_id"]), {})
            lane["state"] = payload.get("to_state")
            lane["scope_fingerprint"] = request["scope_fingerprint"]
            reset_gate_proof(lane, str(payload.get("to_state")))
            apply_advance_effects(
                registry, str(request["lane_id"]), dispatch, str(payload.get("to_state")))
        dispatch["stage"] = stage
        dispatch["events"].append(event)
        dispatch[f"{event}_payload"] = deepcopy(payload)
        return stage
    def _atomic_write(self, registry: Mapping[str, Any]) -> None:
        temporary_path: Path | None = None
        replaced = False
        try:
            descriptor, temporary_name = tempfile.mkstemp(
                prefix="registry-v2.", suffix=".tmp", dir=self.root)
            temporary_path = Path(temporary_name)
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(f"{canonical_json(registry)}\n")
                handle.flush()
                os.fsync(handle.fileno())
            self._write_recovery_intent(registry)
            os.replace(temporary_path, self.path)
            replaced = True
            try:
                verified = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise CtlError("CTL_POST_WRITE_VERIFY_FAILED", "post-replace verify failed") from exc
            if canonical_digest(verified) != canonical_digest(registry):
                raise CtlError("CTL_POST_WRITE_VERIFY_FAILED", "registry digest mismatch")
            self.recovery_path.unlink()
        except CtlError:
            raise
        except OSError as exc:
            code = "CTL_POST_WRITE_VERIFY_FAILED" if replaced else "CTL_ATOMIC_WRITE_FAILED"
            if not replaced and self.recovery_path.exists():
                try:
                    self.recovery_path.unlink()
                except OSError:
                    pass
            raise CtlError(code, "registry write failed") from exc
        finally:
            if temporary_path and temporary_path.exists():
                temporary_path.unlink()
    def _write_recovery_intent(self, registry: Mapping[str, Any]) -> None:
        marker = {"generation": registry.get("generation"),
                  "registry_digest": canonical_digest(registry), "recorded_at": _utc_now()}
        descriptor = os.open(
            self.recovery_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(f"{canonical_json(marker)}\n")
            handle.flush()
            os.fsync(handle.fileno())
