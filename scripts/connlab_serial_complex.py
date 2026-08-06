#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable


REQUEST_KEYS = {
    "schema",
    "version",
    "task_id",
    "summary",
    "root_cause_clear",
    "expected_result_clear",
    "may_touch",
    "targeted_validation",
    "requires_independent_review",
    "forbidden_categories",
}
FORBIDDEN_KEYS = {
    "api_contract",
    "database",
    "schema_or_migration",
    "persistence",
    "authority",
    "public_drive_workflow",
    "business_rule_semantics",
    "destructive_action",
    "external_mutation",
    "push_or_release",
}
DECISION_KEYS = REQUEST_KEYS - {"schema", "version", "task_id", "summary"}


class SerialContractError(ValueError):
    def __init__(self, code: str, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(f"{code}: {reason}")


CALLBACK_TRANSITIONS = {
    ("Planner", "ready", "User"): ("awaiting_user_approval", None, False),
    ("Planner", "discovery_required", "User"): ("blocked", "DISCOVERY_REQUIRED", False),
    ("Developer", "ready", "Reviewer"): ("review", None, False),
    ("Developer", "blocked", "User"): ("blocked", "DEVELOPER_BLOCKED", False),
    ("Reviewer", "pass", "QA"): ("qa", None, False),
    ("Reviewer", "blocked", "Developer"): ("development", "REVIEWER_BLOCKED", False),
    ("QA", "pass", "Integrator"): ("integration", None, False),
    ("QA", "blocked", "Developer"): ("development", "QA_BLOCKED", False),
    ("Integrator", "pass", "User"): ("integration", None, True),
    ("Integrator", "blocked", "User"): ("blocked", "INTEGRATION_BLOCKED", False),
}
BLOCKER_KEYS = {
    "schema", "version", "code", "stage", "reason", "dirty_paths", "failed_validation",
    "subject_commit", "evidence_ref", "native_action_id", "related_ids", "retryable",
    "requires_user", "resume_phase", "recorded_at",
}
FAILURE_KEYS = {"schema", "version", "operation", "command", "exit_code", "summary", "recorded_at"}
BLOCKER_POLICIES = {
    "DISCOVERY_REQUIRED": ({"evidence_ref", "related_ids"}, True, True, "planning"),
    "APPROVAL_REQUIRED": ({"related_ids"}, True, True, "awaiting_user_approval"),
    "DEVELOPER_BLOCKED": ({"evidence_ref", "subject_commit", "failed_validation"}, True, True, "development"),
    "REVIEWER_BLOCKED": ({"evidence_ref", "subject_commit", "related_ids"}, True, False, "development"),
    "QA_BLOCKED": ({"evidence_ref", "subject_commit", "failed_validation", "related_ids"}, True, False, "development"),
    "INTEGRATION_BLOCKED": ({"evidence_ref", "subject_commit", "failed_validation"}, False, True, "integration"),
    "DIRTY_WORKTREE": ({"dirty_paths", "subject_commit"}, True, True, "same"),
    "CALLBACK_PENDING": ({"native_action_id", "related_ids"}, True, False, "same"),
    "ARCHIVE_PENDING": ({"native_action_id", "related_ids"}, True, True, "closing"),
    "ARCHIVE_PENDING_UNVERIFIABLE": ({"native_action_id", "evidence_ref", "related_ids"}, True, True, "closing"),
    "WORKTREE_RETIREMENT_PENDING": ({"dirty_paths", "related_ids"}, True, True, "closing"),
    "SCOPE_EXPANDED": ({"dirty_paths", "evidence_ref"}, True, True, "planning"),
    "VALIDATION_FAILED": ({"subject_commit", "failed_validation"}, True, True, "same"),
    "NATIVE_ACTION_FAILED": ({"native_action_id", "failed_validation", "related_ids"}, True, True, "same"),
    "CUTOVER_FAILED": ({"subject_commit", "failed_validation", "evidence_ref", "related_ids"}, False, True, "human_review"),
}
LEGAL_PHASES = {
    "planning", "awaiting_user_approval", "implementation", "development", "review", "qa",
    "integration", "blocked", "human_review", "closing",
}
OPTIONAL_SCALARS = {"failed_validation", "subject_commit", "evidence_ref", "native_action_id"}
def _contract_error(code: str, reason: str) -> None:
    raise SerialContractError(code, reason)
def _is_sha(value: Any, length: int) -> bool:
    return isinstance(value, str) and re.fullmatch(rf"[0-9a-f]{{{length}}}", value) is not None
def _is_evidence(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[^@#]+@[0-9a-f]{40}#[0-9a-f]{64}", value) is not None
def validate_failure_proof(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != FAILURE_KEYS:
        _contract_error("BLOCKED_BLOCKER_INVALID", "Failure proof keys are invalid.")
    if value.get("schema") != "connlab.serial-failure-proof" or value.get("version") != 1:
        _contract_error("BLOCKED_BLOCKER_INVALID", "Failure proof identity is invalid.")
    if not all(isinstance(value.get(key), str) and value[key].strip() for key in ("operation", "summary", "recorded_at")):
        _contract_error("BLOCKED_BLOCKER_INVALID", "Failure proof text is incomplete.")
    command = value.get("command")
    if not isinstance(command, list) or any(not isinstance(item, str) or not item for item in command):
        _contract_error("BLOCKED_BLOCKER_INVALID", "Failure proof command is invalid.")
    exit_code = value.get("exit_code")
    if exit_code is not None and type(exit_code) is not int:
        _contract_error("BLOCKED_BLOCKER_INVALID", "Failure proof exit code is invalid.")
    if not command and exit_code is not None:
        _contract_error("BLOCKED_BLOCKER_INVALID", "Native failure proof must use a null exit code.")
    return value
def validate_complex_blocker(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != BLOCKER_KEYS:
        _contract_error("BLOCKED_BLOCKER_INVALID", "Complex blocker keys are invalid.")
    code = value.get("code")
    if value.get("schema") != "connlab.serial-task-blocker" or value.get("version") != 1 or code not in BLOCKER_POLICIES:
        _contract_error("BLOCKED_BLOCKER_INVALID", "Complex blocker identity is invalid.")
    if value.get("stage") not in LEGAL_PHASES or not all(
        isinstance(value.get(key), str) and value[key].strip() for key in ("reason", "recorded_at")
    ):
        _contract_error("BLOCKED_BLOCKER_INVALID", "Complex blocker stage or text is invalid.")
    dirty = value.get("dirty_paths")
    related = value.get("related_ids")
    if not isinstance(dirty, list) or not isinstance(related, list):
        _contract_error("BLOCKED_BLOCKER_INVALID", "Blocker arrays are invalid.")
    if dirty:
        try:
            _normalized_paths(dirty)
        except SerialContractError as exc:
            raise SerialContractError("BLOCKED_BLOCKER_INVALID", exc.reason) from exc
    if any(not isinstance(item, str) or not item.strip() for item in related):
        _contract_error("BLOCKED_BLOCKER_INVALID", "Related IDs are invalid.")
    required, retryable, requires_user, resume_policy = BLOCKER_POLICIES[code]
    resume = value.get("stage") if resume_policy == "same" else resume_policy
    if value.get("retryable") is not retryable or value.get("requires_user") is not requires_user or value.get("resume_phase") != resume:
        _contract_error("BLOCKED_BLOCKER_INVALID", "Blocker policy fields do not match the frozen table.")
    populated = {
        "dirty_paths": bool(dirty),
        "related_ids": bool(related),
        **{key: value.get(key) is not None for key in OPTIONAL_SCALARS},
    }
    if any(not populated[key] for key in required) or any(populated[key] for key in populated if key not in required):
        _contract_error("BLOCKED_BLOCKER_INVALID", "Required or forbidden blocker fields do not match policy.")
    if value.get("subject_commit") is not None and not _is_sha(value["subject_commit"], 40):
        _contract_error("BLOCKED_BLOCKER_INVALID", "Blocker subject commit is invalid.")
    if value.get("evidence_ref") is not None and not _is_evidence(value["evidence_ref"]):
        _contract_error("BLOCKED_BLOCKER_INVALID", "Blocker evidence reference is invalid.")
    if value.get("native_action_id") is not None and not _is_sha(value["native_action_id"], 64):
        _contract_error("BLOCKED_BLOCKER_INVALID", "Blocker native action ID is invalid.")
    if value.get("failed_validation") is not None:
        validate_failure_proof(value["failed_validation"])
    return value
def callback_transition(value: Any) -> dict[str, Any]:
    keys = {"schema", "version", "task_id", "role", "status", "subject_commit", "evidence", "next", "blocker"}
    if not isinstance(value, dict) or set(value) != keys:
        _contract_error("BLOCKED_CALLBACK_INVALID", "Callback keys are invalid.")
    if value.get("schema") != "connlab.serial-callback" or value.get("version") != 1:
        _contract_error("BLOCKED_CALLBACK_INVALID", "Callback identity is invalid.")
    if not isinstance(value.get("task_id"), str) or not value["task_id"] or not _is_sha(value.get("subject_commit"), 40) or not _is_evidence(value.get("evidence")):
        _contract_error("BLOCKED_CALLBACK_INVALID", "Callback authority references are invalid.")
    transition = CALLBACK_TRANSITIONS.get((value.get("role"), value.get("status"), value.get("next")))
    if transition is None:
        _contract_error("BLOCKED_CALLBACK_INVALID", "Role, status and next are not a frozen combination.")
    target_phase, blocker_code, integration_ready = transition
    supplied = value.get("blocker")
    if blocker_code is None:
        if supplied is not None:
            _contract_error("BLOCKED_CALLBACK_INVALID", "Successful callback must not contain a blocker.")
    else:
        if not isinstance(supplied, dict) or supplied.get("code") != blocker_code:
            _contract_error("BLOCKED_CALLBACK_INVALID", "Callback blocker does not match the frozen combination.")
        try:
            validate_complex_blocker(supplied)
        except SerialContractError as exc:
            raise SerialContractError("BLOCKED_CALLBACK_INVALID", exc.reason) from exc
    return {
        "target_phase": target_phase,
        "blocker_code": blocker_code,
        "integration_ready": integration_ready,
    }


NATIVE_ACTION_KEYS = {
    "schema", "version", "action_id", "action", "role", "attempt", "prompt_sha256", "title", "recorded_at",
}
INVOCATION_KEYS = {
    "schema", "version", "action_id", "role", "attempt", "thread_id", "agent_id", "host_id", "status", "recorded_at",
}
ACTION_ROLES = {
    "planner_dispatch": "Planner",
    "host_create": "Host",
    "developer_dispatch": "Developer",
    "reviewer_dispatch": "Reviewer",
    "qa_dispatch": "QA",
    "integrator_dispatch": "Integrator",
}
def validate_native_action(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != NATIVE_ACTION_KEYS:
        _contract_error("BLOCKED_ARGUMENT_COMBINATION", "Native action keys are invalid.")
    if value.get("schema") != "connlab.serial-native-action" or value.get("version") != 1:
        _contract_error("BLOCKED_ARGUMENT_COMBINATION", "Native action identity is invalid.")
    if ACTION_ROLES.get(value.get("action")) != value.get("role"):
        _contract_error("BLOCKED_ROLE_ORDER", "Native action and role do not match.")
    if not _is_sha(value.get("action_id"), 64) or not _is_sha(value.get("prompt_sha256"), 64):
        _contract_error("BLOCKED_ARGUMENT_COMBINATION", "Native action hashes are invalid.")
    if type(value.get("attempt")) is not int or value["attempt"] < 1:
        _contract_error("BLOCKED_ARGUMENT_COMBINATION", "Native action attempt is invalid.")
    if not all(isinstance(value.get(key), str) and value[key].strip() for key in ("title", "recorded_at")):
        _contract_error("BLOCKED_ARGUMENT_COMBINATION", "Native action text is incomplete.")
    return value
def validate_invocation(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != INVOCATION_KEYS:
        _contract_error("BLOCKED_ARGUMENT_COMBINATION", "Invocation keys are invalid.")
    if value.get("schema") != "connlab.serial-invocation" or value.get("version") != 1:
        _contract_error("BLOCKED_ARGUMENT_COMBINATION", "Invocation identity is invalid.")
    if not _is_sha(value.get("action_id"), 64) or value.get("role") not in ACTION_ROLES.values():
        _contract_error("BLOCKED_ARGUMENT_COMBINATION", "Invocation action or role is invalid.")
    if type(value.get("attempt")) is not int or value["attempt"] < 1 or value.get("status") not in {"started", "completed", "unavailable"}:
        _contract_error("BLOCKED_ARGUMENT_COMBINATION", "Invocation attempt or status is invalid.")
    identities = [value.get("thread_id"), value.get("agent_id")]
    if sum(isinstance(item, str) and bool(item.strip()) for item in identities) != 1:
        _contract_error("BLOCKED_ARGUMENT_COMBINATION", "Exactly one invocation identity is required.")
    if any(item is not None and (not isinstance(item, str) or not item.strip()) for item in (*identities, value.get("host_id"))):
        _contract_error("BLOCKED_ARGUMENT_COMBINATION", "Invocation IDs are invalid.")
    if not isinstance(value.get("recorded_at"), str) or not value["recorded_at"]:
        _contract_error("BLOCKED_ARGUMENT_COMBINATION", "Invocation timestamp is required.")
    return value
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
def _bytes_sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
def _git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()
def _canonical_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
def intrinsic_permission_probe(
    root: Path,
    task_id: str,
    source_head: str,
    paths: list[str],
    *,
    opener: Callable[..., int] = os.open,
) -> dict[str, Any]:
    resolved_root = root.resolve(strict=True)
    if len(paths) != 8 or len(set(paths)) != 8:
        _contract_error("BLOCKED_CUTOVER_PERMISSION_PROBE", "Exactly eight unique cutover paths are required.")
    started = _utc_now()
    records: list[dict[str, Any]] = []
    flags = os.O_RDWR | getattr(os, "O_BINARY", 0)
    root_case = os.path.normcase(str(resolved_root))
    for relative in paths:
        try:
            normalized = _normalized_paths([relative])[0]
            candidate = (resolved_root / normalized).resolve(strict=True)
            common = os.path.commonpath([root_case, os.path.normcase(str(candidate))])
            if common != root_case:
                _contract_error("BLOCKED_CUTOVER_PERMISSION_PROBE", "Cutover path is outside the repository.")
            if not candidate.is_file():
                _contract_error("BLOCKED_CUTOVER_PERMISSION_PROBE", "Cutover path is not a regular file.")
            before = candidate.read_bytes()
            descriptor = opener(candidate, flags)
            os.close(descriptor)
            after = candidate.read_bytes()
        except PermissionError as exc:
            raise SerialContractError("BLOCKED_CUTOVER_PATH_READ_ONLY", f"Cutover path is read-only: {relative}") from exc
        except FileNotFoundError as exc:
            raise SerialContractError("BLOCKED_CUTOVER_PERMISSION_PROBE", f"Cutover path was not found: {relative}") from exc
        except SerialContractError:
            raise
        except OSError as exc:
            raise SerialContractError("BLOCKED_CUTOVER_PERMISSION_PROBE", f"Permission probe failed: {relative}") from exc
        unchanged = before == after
        if not unchanged:
            _contract_error("BLOCKED_CUTOVER_PERMISSION_PROBE", f"Permission probe observed content drift: {relative}")
        records.append({
            "path": relative,
            "resolved_path": str(candidate),
            "existed": True,
            "regular_file": True,
            "open_flags": flags,
            "handle_opened": True,
            "pre_bytes": len(before),
            "pre_sha256": _bytes_sha(before),
            "pre_blob": _git_blob(before),
            "post_bytes": len(after),
            "post_sha256": _bytes_sha(after),
            "post_blob": _git_blob(after),
            "unchanged": True,
            "error_code": None,
        })
    proof = {
        "schema": "connlab.serial-cutover-permission-proof",
        "version": 1,
        "task_id": task_id,
        "source_head": source_head,
        "observation_source": "same_process_write_handle_probe",
        "algorithm": "python_os_open_rdwr_binary_no_write_v1",
        "process_id": os.getpid(),
        "started_at": started,
        "finished_at": _utc_now(),
        "paths": records,
    }
    proof["probe_receipt_sha256"] = _canonical_hash(proof)
    return proof
def apply_cutover_payload(
    root: Path,
    manifest: dict[str, Any],
    *,
    opener: Callable[..., int] = os.open,
    materializer: Callable[[str], None],
) -> dict[str, Any]:
    required = {"task_id", "source_head", "paths", "permission_proof"}
    if not isinstance(manifest, dict) or set(manifest) != required:
        _contract_error("BLOCKED_CUTOVER_MANIFEST", "Cutover manifest fixture is invalid.")
    proof = intrinsic_permission_probe(
        root,
        manifest["task_id"],
        manifest["source_head"],
        manifest["paths"],
        opener=opener,
    )
    for relative in manifest["paths"]:
        materializer(relative)
    return proof
PHASE_ROLE = {"planning": "Planner", "development": "Developer", "review": "Reviewer", "qa": "QA", "integration": "Integrator"}
def complex_transition(active: dict[str, Any], command: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Apply one durable v2 transition; repository/evidence proofs remain the writer's precondition."""
    context = active.get("complex_context")
    if not isinstance(context, dict): _contract_error("BLOCKED_STATE", "Complex context is required.")
    phase, pending = active.get("phase"), context.get("pending_callback")
    if command == "begin-role":
        role, action = payload.get("role"), validate_native_action(payload.get("native_action"))
        if PHASE_ROLE.get(phase) != role or action["role"] != role: _contract_error("BLOCKED_ROLE_ORDER", "Role is not legal for the current phase.")
        if role != "Planner" and not context.get("host_id"): _contract_error("BLOCKED_HOST_REQUIRED", "Execution roles require the recorded host.")
        if pending is not None: _contract_error("BLOCKED_NATIVE_ACTION_PENDING", "A native action is already pending.")
        context["current_role"], context["current_attempt"] = role, action["attempt"]
        context["pending_callback"] = {"state": "dispatch_pending", "action_id": action["action_id"], "role": role, "attempt": action["attempt"]}
    elif command == "record-invocation":
        invocation = validate_invocation(payload.get("invocation"))
        if not isinstance(pending, dict) or pending.get("state") != "dispatch_pending": _contract_error("BLOCKED_NATIVE_ACTION_PENDING", "No matching dispatch is pending.")
        if (invocation["action_id"], invocation["role"], invocation["attempt"]) != (pending["action_id"], pending["role"], pending["attempt"]): _contract_error("BLOCKED_NATIVE_ID_MISMATCH", "Invocation does not bind the pending action.")
        context["role_invocations"].append(invocation); pending["state"] = "callback_pending"
    elif command == "consume-callback":
        callback = payload.get("callback"); decision = callback_transition(callback)
        if not isinstance(pending, dict) or pending.get("state") != "callback_pending" or callback["role"] != pending.get("role"): _contract_error("BLOCKED_CALLBACK_STALE", "Callback does not bind the pending invocation.")
        if callback["task_id"] != active.get("task_id") or PHASE_ROLE.get(phase) != callback["role"]: _contract_error("BLOCKED_ROLE_ORDER", "Callback role or task is stale.")
        expected = {"Reviewer": context.get("developer_subject_commit"), "QA": context.get("reviewer_subject_commit"), "Integrator": context.get("qa_subject_commit")}.get(callback["role"])
        if expected and callback["subject_commit"] != expected: _contract_error("BLOCKED_SUBJECT_MISMATCH", "Callback subject differs from the reviewed code commit.")
        if callback["role"] == "Developer" and callback["status"] == "ready": context["developer_subject_commit"] = callback["subject_commit"]
        if callback["role"] == "Reviewer" and callback["status"] == "pass": context["reviewer_subject_commit"] = callback["subject_commit"]
        if callback["role"] == "QA" and callback["status"] == "pass": context["qa_subject_commit"] = callback["subject_commit"]
        context["evidence_refs"].append(callback["evidence"]); context["pending_callback"] = None
        active["phase"], active["blocker"] = decision["target_phase"], callback["blocker"]
        if decision["integration_ready"]: context["worktree_lifecycle"] = "integration_ready"
    elif command == "begin-host":
        action = validate_native_action(payload.get("native_action"))
        if phase != "development" or action["action"] != "host_create" or context.get("host_id"): _contract_error("BLOCKED_HOST_DUPLICATE", "Host creation is not legal.")
        if pending is not None: _contract_error("BLOCKED_NATIVE_ACTION_PENDING", "A native action is already pending.")
        context["pending_callback"] = {"state": "host_creation_pending", "action_id": action["action_id"], "role": "Host", "attempt": action["attempt"]}
    elif command == "record-host":
        worktree = payload.get("worktree"); keys = {"schema", "version", "action_id", "thread_id", "host_id", "branch", "worktree", "base_sha", "head_sha", "integration_target", "clean", "recorded_at"}
        if not isinstance(worktree, dict) or set(worktree) != keys or worktree.get("schema") != "connlab.serial-worktree" or worktree.get("version") != 1: _contract_error("BLOCKED_WORKTREE_FACTS", "Worktree schema is invalid.")
        if not isinstance(pending, dict) or pending.get("state") != "host_creation_pending" or pending.get("action_id") != worktree.get("action_id"): _contract_error("BLOCKED_NATIVE_ID_MISMATCH", "Worktree does not bind the host action.")
        if worktree.get("clean") is not True or not _is_sha(worktree.get("base_sha"), 40) or not _is_sha(worktree.get("head_sha"), 40): _contract_error("BLOCKED_WORKTREE_FACTS", "Worktree Git facts are invalid.")
        context.update(host_thread_id=worktree["thread_id"], host_id=worktree["host_id"], task_branch=worktree["branch"], task_worktree=worktree["worktree"], base_sha=worktree["base_sha"], head_sha=worktree["head_sha"], integration_target=worktree["integration_target"], worktree_lifecycle="ready", pending_callback=None)
    elif command == "record-integration":
        value = payload.get("integration"); keys = {"schema", "version", "subject_commit", "branch_head", "primary_parent", "merge_commit", "merge_tree", "parents", "evidence_refs", "command", "clean", "recorded_at"}
        if phase != "integration" or context.get("worktree_lifecycle") != "integration_ready" or not isinstance(value, dict) or set(value) != keys: _contract_error("BLOCKED_INTEGRATION_PRECONDITION", "Integration is not ready.")
        if value.get("subject_commit") != context.get("qa_subject_commit") or value.get("parents") != [value.get("primary_parent"), value.get("branch_head")] or value.get("clean") is not True: _contract_error("BLOCKED_INTEGRATION_PROOF", "Integration proof is inconsistent.")
        context["integrated_commit"] = value["merge_commit"]; context["worktree_lifecycle"] = "integrated"; active["phase"] = "human_review"
    elif command == "request-close":
        if phase != "human_review" or not payload.get("decision_ref"): _contract_error("BLOCKED_STATE", "Human review close evidence is required.")
        active["phase"] = "closing"; context["close_decision_ref"] = payload["decision_ref"]
    elif command == "record-closeout":
        value = payload.get("closeout"); order = context.get("probe_approved_closeout_order")
        if phase != "closing" or not isinstance(value, dict) or value.get("order") != order or value.get("status") != "completed": _contract_error("BLOCKED_CLOSEOUT_ORDER", "Closeout proof does not match the approved order.")
        if value.get("step") == "archived": context["archived_ids"].append(value.get("thread_id"))
        elif value.get("step") in {"retired", "retained"}: context["worktree_lifecycle"] = value["step"]
        else: _contract_error("BLOCKED_CLOSEOUT_ORDER", "Closeout step is invalid.")
        context["archive_attempts"].append(value)
    elif command == "finalize-close":
        if phase != "closing" or payload.get("decision_ref") != context.get("close_decision_ref") or context.get("worktree_lifecycle") not in {"retired", "retained"}: _contract_error("BLOCKED_RETIREMENT_PENDING", "Closeout is incomplete.")
        if context.get("archive_target_ids") != context.get("archived_ids"): _contract_error("BLOCKED_ARCHIVE_PENDING", "Archive receipts are incomplete.")
        active["_release_active"] = True
    else: _contract_error("BLOCKED_STATE", "Command is not a legal pure complex transition.")
    return active


def _normalized_paths(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "may_touch must be a non-empty list.")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item or "\\" in item:
            raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "may_touch paths must be normalized.")
        path = PurePosixPath(item)
        if path.is_absolute() or path.as_posix() != item or any(part in {"", ".", ".."} for part in path.parts):
            raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "may_touch paths must be repository-relative.")
        result.append(item)
    if len(result) != len(set(result)):
        raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "may_touch paths must be unique.")
    return result


def classify_request(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "Request must be an object.")
    unknown = set(value) - REQUEST_KEYS
    if unknown:
        raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "Unknown request fields are forbidden.")
    common = {"schema", "version", "task_id", "summary"}
    if not common <= set(value):
        raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "Request identity is incomplete.")
    if value.get("schema") != "connlab.serial-task-request" or value.get("version") != 1:
        raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "Request schema/version is invalid.")
    if not all(isinstance(value.get(key), str) and value[key].strip() for key in ("task_id", "summary")):
        raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "Task identity and summary are required.")
    missing = sorted(DECISION_KEYS - set(value))
    if missing:
        return {
            "classification": "needs_discovery",
            "reason_codes": [f"MISSING_{name.upper()}" for name in missing],
        }
    if type(value["root_cause_clear"]) is not bool or type(value["expected_result_clear"]) is not bool:
        raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "Clarity facts must be booleans.")
    if type(value["requires_independent_review"]) is not bool:
        raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "Review fact must be boolean.")
    paths = _normalized_paths(value["may_touch"])
    checks = value["targeted_validation"]
    if not isinstance(checks, list) or not checks or any(not isinstance(item, str) or not item.strip() for item in checks):
        raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "Targeted validation is required.")
    forbidden = value["forbidden_categories"]
    if not isinstance(forbidden, dict) or set(forbidden) != FORBIDDEN_KEYS or any(type(item) is not bool for item in forbidden.values()):
        raise SerialContractError("BLOCKED_CLASSIFICATION_INVALID", "Forbidden categories are incomplete.")

    reasons: list[str] = []
    if not value["root_cause_clear"]:
        reasons.append("ROOT_CAUSE_UNCLEAR")
    if not value["expected_result_clear"]:
        reasons.append("EXPECTED_RESULT_UNCLEAR")
    if len(paths) > 3:
        reasons.append("PATH_COUNT_EXCEEDS_SIMPLE")
    if "docs/task_board.md" not in paths:
        reasons.append("BOARD_PATH_MISSING")
    if value["requires_independent_review"]:
        reasons.append("INDEPENDENT_REVIEW_REQUIRED")
    reasons.extend(f"FORBIDDEN_{key.upper()}" for key, enabled in forbidden.items() if enabled)
    if reasons:
        return {"classification": "complex", "reason_codes": reasons}
    return {"classification": "simple", "reason_codes": ["SIMPLE_PREDICATES_PASS"]}


def classification_result(
    request: Any,
    *,
    command: str,
    primary_root: str,
    primary_head: str,
    board_sha256: str,
) -> dict[str, Any]:
    decision = classify_request(request)
    classification = decision["classification"]
    return {
        "schema": "connlab.serial-task-result",
        "version": 1,
        "code": f"ALLOW_CLASSIFY_{classification.upper()}",
        "allowed": True,
        "changed": False,
        "command": command,
        "task_id": request["task_id"],
        "classification": classification,
        "state": None,
        "phase": None,
        "active_task_id": None,
        "queue_position": None,
        "next_action": "submit" if classification != "needs_discovery" else "Planner",
        "native_action_id": None,
        "board_sha256_before": board_sha256,
        "board_sha256_after": board_sha256,
        "primary_head": primary_head,
        "primary_root": primary_root,
        "changed_paths": [],
        "reason_codes": decision["reason_codes"],
        "payload": None,
        "reason": "Request classified without changing repository content.",
    }
