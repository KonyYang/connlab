#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterator


BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"
BOARD_REL = "docs/task_board.md"
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
}
BLOCKER_CODES = {
    "VALIDATION_FAILED",
    "UNEXPECTED_PATHS",
    "SCOPE_EXPANDED",
    "IMPLEMENTATION_FAILED",
    "DIRTY_WORKTREE",
    "EXTERNAL_BLOCKER",
}


class Blocked(Exception):
    def __init__(self, code: str, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(reason)


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True, check=False)


def resolve_primary(value: str) -> Path:
    root = Path(value).resolve()
    top = run_git(root, "rev-parse", "--show-toplevel")
    branch = run_git(root, "branch", "--show-current")
    if (
        top.returncode != 0
        or Path(top.stdout.strip()).resolve() != root
        or branch.returncode != 0
        or branch.stdout.strip() != "master"
        or not (root / ".git").is_dir()
    ):
        raise Blocked("BLOCKED_PRIMARY_UNVERIFIED", "Primary master worktree could not be verified.")
    return root


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def exact_keys(value: dict[str, Any], expected: set[str], code: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise Blocked(code, "JSON keys do not match the frozen schema.")


def normalized_paths(value: Any, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise ValueError("A path list is required.")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item or "\\" in item:
            raise ValueError("Paths must be non-empty normalized repository-relative strings.")
        path = PurePosixPath(item)
        if path.is_absolute() or item != path.as_posix() or any(part in ("", ".", "..") for part in path.parts):
            raise ValueError("Paths must be normalized and repository-relative.")
        result.append(item)
    if len(result) != len(set(result)):
        raise ValueError("Paths must be unique.")
    return result


def nonempty_strings(value: Any, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise ValueError("A string list is required.")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError("Every list item must be non-empty text.")
    return value


def validate_forbidden(value: Any, *, simple: bool, code: str) -> dict[str, bool]:
    if not isinstance(value, dict) or set(value) != FORBIDDEN_KEYS:
        raise Blocked(code, "Forbidden-category checks are incomplete.")
    if any(type(item) is not bool for item in value.values()):
        raise Blocked(code, "Forbidden-category checks must be booleans.")
    if simple and any(value.values()):
        raise Blocked(code, "A simple task cannot include a forbidden category.")
    return value


def scope_from_payload(value: dict[str, Any], *, simple: bool, code: str) -> dict[str, Any]:
    try:
        paths = normalized_paths(value["may_touch"])
        count = value["expected_file_count"]
        if type(count) is not int or count != len(paths) or BOARD_REL not in paths:
            raise ValueError("File count must equal paths and include the board.")
        if simple and not 1 <= count <= 3:
            raise ValueError("Simple tasks allow one to three total paths.")
        reason = value["classification_reason"]
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Classification reason is required.")
        checks = nonempty_strings(value["targeted_validation"])
    except (KeyError, ValueError) as exc:
        raise Blocked(code, str(exc)) from exc
    forbidden = validate_forbidden(value.get("forbidden_categories"), simple=simple, code=code)
    return {
        "may_touch": paths,
        "expected_file_count": count,
        "classification_reason": reason,
        "targeted_validation": checks,
        "forbidden_categories": forbidden,
    }


def parse_json(raw: str | None, code: str) -> dict[str, Any]:
    try:
        value = json.loads(raw or "")
    except json.JSONDecodeError as exc:
        raise Blocked(code, "Input is not valid JSON.") from exc
    if not isinstance(value, dict):
        raise Blocked(code, "Input JSON must be an object.")
    return value


def request_payload(raw: str | None, task_id: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    value = parse_json(raw, "BLOCKED_CLASSIFICATION_INVALID")
    common = {"schema", "version", "task_id", "summary", "kind"}
    if value.get("kind") == "planned":
        exact_keys(value, common, "BLOCKED_CLASSIFICATION_INVALID")
        scope = None
    elif value.get("kind") == "simple":
        exact_keys(
            value,
            common | {"may_touch", "expected_file_count", "classification_reason", "targeted_validation", "forbidden_categories", "plan_ref"},
            "BLOCKED_CLASSIFICATION_INVALID",
        )
        if value.get("plan_ref") is not None:
            raise Blocked("BLOCKED_CLASSIFICATION_INVALID", "Simple intake plan_ref must be null.")
        scope = scope_from_payload(value, simple=True, code="BLOCKED_CLASSIFICATION_INVALID")
    else:
        raise Blocked("BLOCKED_CLASSIFICATION_INVALID", "Task kind must be simple or planned.")
    if value.get("schema") != "connlab.personal-task-request" or value.get("version") != 1:
        raise Blocked("BLOCKED_CLASSIFICATION_INVALID", "Request schema/version is invalid.")
    if value.get("task_id") != task_id:
        raise Blocked("BLOCKED_TASK_MISMATCH", "Request and command task IDs differ.")
    if not isinstance(value.get("summary"), str) or not value["summary"].strip():
        raise Blocked("BLOCKED_CLASSIFICATION_INVALID", "Task summary is required.")
    return value, scope


def approved_payload(raw: str | None, task_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    value = parse_json(raw, "BLOCKED_APPROVED_SCOPE_INVALID")
    exact_keys(value, {"schema", "version", "task_id", "summary", "kind", "may_touch", "expected_file_count", "classification_reason", "targeted_validation", "forbidden_categories"}, "BLOCKED_APPROVED_SCOPE_INVALID")
    if value.get("schema") != "connlab.personal-task-approved-request" or value.get("version") != 1 or value.get("kind") != "planned":
        raise Blocked("BLOCKED_APPROVED_SCOPE_INVALID", "Approved request schema/version/kind is invalid.")
    if value.get("task_id") != task_id:
        raise Blocked("BLOCKED_TASK_MISMATCH", "Approved request and command task IDs differ.")
    if not isinstance(value.get("summary"), str) or not value["summary"].strip():
        raise Blocked("BLOCKED_APPROVED_SCOPE_INVALID", "Approved summary is required.")
    return value, scope_from_payload(value, simple=False, code="BLOCKED_APPROVED_SCOPE_INVALID")


def validation_payload(raw: str | None, *, require_pass: bool) -> dict[str, Any]:
    value = parse_json(raw, "BLOCKED_VALIDATION_FAILED")
    exact_keys(value, {"schema", "version", "status", "checks", "observed_paths", "manual_checks", "recorded_at"}, "BLOCKED_VALIDATION_FAILED")
    if value.get("schema") != "connlab.personal-task-validation" or value.get("version") != 1 or value.get("status") not in {"passed", "failed"}:
        raise Blocked("BLOCKED_VALIDATION_FAILED", "Validation schema/version/status is invalid.")
    checks = value.get("checks")
    if not isinstance(checks, list) or not checks:
        raise Blocked("BLOCKED_VALIDATION_FAILED", "Validation checks are required.")
    for check in checks:
        if not isinstance(check, dict) or set(check) != {"command", "exit_code", "summary"} or not isinstance(check.get("command"), str) or not isinstance(check.get("summary"), str) or type(check.get("exit_code")) is not int:
            raise Blocked("BLOCKED_VALIDATION_FAILED", "Validation check is malformed.")
    try:
        normalized_paths(value.get("observed_paths"), allow_empty=True)
        nonempty_strings(value.get("manual_checks"), allow_empty=True)
    except ValueError as exc:
        raise Blocked("BLOCKED_VALIDATION_FAILED", str(exc)) from exc
    if not isinstance(value.get("recorded_at"), str) or not value["recorded_at"]:
        raise Blocked("BLOCKED_VALIDATION_FAILED", "Validation timestamp is required.")
    if require_pass and (value["status"] != "passed" or any(item["exit_code"] != 0 for item in checks)):
        raise Blocked("BLOCKED_VALIDATION_FAILED", "Validation has not passed.")
    return value


def blocker_payload(raw: str | None) -> dict[str, Any]:
    value = parse_json(raw, "BLOCKED_BLOCKER_INVALID")
    exact_keys(value, {"schema", "version", "code", "reason", "dirty_paths", "failed_validation", "recorded_at"}, "BLOCKED_BLOCKER_INVALID")
    if value.get("schema") != "connlab.personal-task-blocker" or value.get("version") != 1 or value.get("code") not in BLOCKER_CODES:
        raise Blocked("BLOCKED_BLOCKER_INVALID", "Blocker schema/version/code is invalid.")
    if not isinstance(value.get("reason"), str) or not value["reason"].strip() or not isinstance(value.get("recorded_at"), str) or not value["recorded_at"]:
        raise Blocked("BLOCKED_BLOCKER_INVALID", "Blocker reason and timestamp are required.")
    try:
        normalized_paths(value.get("dirty_paths"), allow_empty=True)
    except ValueError as exc:
        raise Blocked("BLOCKED_BLOCKER_INVALID", str(exc)) from exc
    if value["code"] == "VALIDATION_FAILED":
        nested = validation_payload(json.dumps(value.get("failed_validation")), require_pass=False)
        if nested["status"] != "failed":
            raise Blocked("BLOCKED_BLOCKER_INVALID", "Nested validation must be failed.")
    elif value.get("failed_validation") is not None:
        raise Blocked("BLOCKED_BLOCKER_INVALID", "Only VALIDATION_FAILED accepts failed_validation.")
    return value


def parse_board(data: bytes) -> tuple[str, dict[str, Any], str]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Board is not UTF-8.") from exc
    pattern = re.compile(re.escape(BEGIN) + r"\s*```json\s*(.*?)\s*```\s*" + re.escape(END), re.S)
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Board must contain exactly one control block.")
    try:
        value = json.loads(matches[0].group(1))
    except json.JSONDecodeError as exc:
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Board control JSON is malformed.") from exc
    validate_control(value)
    return text[: matches[0].start()], value, text[matches[0].end() :]


def validate_control(value: Any) -> None:
    if not isinstance(value, dict):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Board control must be an object.")
    if value.get("version") == 2:
        validate_v2_control(value)
        return
    validate_v1_control(value)


def validate_v1_control(value: Any) -> None:
    exact_keys(value, {"schema", "version", "mode", "wip_limit", "state", "active", "queue", "next_enqueue_sequence", "last_closed", "retained_history"}, "BLOCKED_SCHEMA_INVALID")
    if value.get("schema") != "connlab.personal-serial-control" or value.get("version") != 1 or value.get("mode") != "personal_serial" or value.get("wip_limit") != 1:
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Board control identity is invalid.")
    if value.get("state") not in {"idle", "running", "implemented_pending_human_review"}:
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Board state is invalid.")
    if not isinstance(value.get("queue"), list) or type(value.get("next_enqueue_sequence")) is not int or value["next_enqueue_sequence"] < 1 or not isinstance(value.get("retained_history"), list):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Board queue/history fields are invalid.")
    active = value.get("active")
    if value["state"] == "idle" and active is not None:
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Idle board cannot have an active task.")
    if value["state"] != "idle" and not isinstance(active, dict):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Occupied board requires an active task.")
    ids: list[str] = []
    if active is not None:
        required = {"task_id", "summary", "kind", "phase", "scope_contract", "plan_ref", "approval_ref", "activation_parent_sha", "activated_at", "updated_at", "blocker", "validation"}
        exact_keys(active, required, "BLOCKED_SCHEMA_INVALID")
        kind, phase, scope = active.get("kind"), active.get("phase"), active.get("scope_contract")
        if kind not in {"simple", "planned"} or phase not in {"planning", "implementation", "blocked", "human_review"} or not all(isinstance(active.get(key), str) and active[key] for key in ("task_id", "summary", "activated_at", "updated_at")) or not re.fullmatch(r"[0-9a-f]{40}", str(active.get("activation_parent_sha"))):
            raise Blocked("BLOCKED_SCHEMA_INVALID", "Active task fields are invalid.")
        if scope is None and (kind == "simple" or phase not in {"planning", "blocked"}):
            raise Blocked("BLOCKED_SCHEMA_INVALID", "Active scope is missing.")
        if scope is not None:
            exact_keys(scope, {"may_touch", "expected_file_count", "classification_reason", "targeted_validation", "forbidden_categories"}, "BLOCKED_SCHEMA_INVALID")
            scope_from_payload(scope, simple=kind == "simple", code="BLOCKED_SCHEMA_INVALID")
        if (value["state"] == "implemented_pending_human_review") != (phase == "human_review"):
            raise Blocked("BLOCKED_SCHEMA_INVALID", "Board state and active phase contradict.")
        if (phase == "blocked") != isinstance(active.get("blocker"), dict):
            raise Blocked("BLOCKED_SCHEMA_INVALID", "Blocked phase and blocker record contradict.")
        if active.get("blocker") is not None:
            blocker_payload(json.dumps(active["blocker"]))
        if active.get("validation") is not None:
            validation_payload(json.dumps(active["validation"]), require_pass=phase == "human_review")
        if kind == "planned" and scope is not None and not all(isinstance(active.get(key), str) and active[key] for key in ("plan_ref", "approval_ref")):
            raise Blocked("BLOCKED_SCHEMA_INVALID", "Approved planned task lacks evidence refs.")
        ids.append(active["task_id"])
    previous = 0
    for item in value["queue"]:
        if not isinstance(item, dict) or set(item) != {"task_id", "summary", "kind", "enqueue_sequence", "queued_at", "scope_contract"}:
            raise Blocked("BLOCKED_SCHEMA_INVALID", "Queue record is invalid.")
        if item.get("kind") not in {"simple", "planned"} or type(item.get("enqueue_sequence")) is not int or item["enqueue_sequence"] <= previous or not all(isinstance(item.get(key), str) and item[key] for key in ("task_id", "summary", "queued_at")):
            raise Blocked("BLOCKED_SCHEMA_INVALID", "Queue ordering is invalid.")
        if item["kind"] == "planned" and item["scope_contract"] is not None:
            raise Blocked("BLOCKED_SCHEMA_INVALID", "Queued planned scope must remain null.")
        if item["kind"] == "simple":
            exact_keys(item["scope_contract"], {"may_touch", "expected_file_count", "classification_reason", "targeted_validation", "forbidden_categories"}, "BLOCKED_SCHEMA_INVALID")
            scope_from_payload(item["scope_contract"], simple=True, code="BLOCKED_SCHEMA_INVALID")
        previous = item["enqueue_sequence"]
        ids.append(item.get("task_id"))
    if value["next_enqueue_sequence"] <= previous:
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Next enqueue sequence must exceed the queue tail.")
    if len(ids) != len(set(ids)):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Active and queued task IDs must be unique.")


V2_ACTIVE_KEYS = {
    "task_id", "summary", "kind", "classification", "phase", "scope_contract", "plan_ref",
    "approval_ref", "activation_parent_sha", "activated_at", "updated_at", "blocker", "validation",
    "complex_context",
}
COMPLEX_CONTEXT_KEYS = {
    "workflow_version", "task_branch", "task_worktree", "base_sha", "head_sha", "integration_target",
    "worktree_lifecycle", "current_role", "current_attempt", "role_invocations", "host_thread_id",
    "host_id", "approved_code_paths", "required_gates", "developer_subject_commit",
    "reviewer_subject_commit", "qa_subject_commit", "integrated_commit", "evidence_refs",
    "pending_callback", "closeout_disposition", "retained_resource_refs", "close_decision_ref",
}
V2_PHASES = {
    "planning", "awaiting_user_approval", "implementation", "development", "review", "qa",
    "integration", "blocked", "human_review", "closing",
}


def validate_v2_control(value: dict[str, Any]) -> None:
    top = {"schema", "version", "mode", "wip_limit", "state", "active", "queue", "next_enqueue_sequence", "last_closed", "retained_history"}
    exact_keys(value, top, "BLOCKED_SCHEMA_INVALID")
    if value.get("schema") != "connlab.personal-serial-control" or value.get("version") != 2 or value.get("mode") != "personal_serial" or value.get("wip_limit") != 1:
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Version-2 board identity is invalid.")
    if value.get("state") not in {"idle", "running", "implemented_pending_human_review"}:
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Version-2 board state is invalid.")
    if not isinstance(value.get("queue"), list) or type(value.get("next_enqueue_sequence")) is not int or not isinstance(value.get("retained_history"), list):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Version-2 queue/history fields are invalid.")
    active = value.get("active")
    if (value["state"] == "idle") != (active is None):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Version-2 occupancy is contradictory.")
    if active is None:
        return
    exact_keys(active, V2_ACTIVE_KEYS, "BLOCKED_SCHEMA_INVALID")
    if active.get("classification") not in {"simple", "complex", "needs_discovery"} or active.get("phase") not in V2_PHASES:
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Version-2 classification/phase is invalid.")
    if not all(isinstance(active.get(key), str) and active[key] for key in ("task_id", "summary", "activated_at", "updated_at")):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Version-2 active identity is incomplete.")
    if not re.fullmatch(r"[0-9a-f]{40}", str(active.get("activation_parent_sha"))):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Version-2 activation parent is invalid.")
    if (value["state"] == "implemented_pending_human_review") != (active["phase"] == "human_review"):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Version-2 state and phase contradict.")
    context = active.get("complex_context")
    if active["classification"] == "simple":
        if context is not None:
            raise Blocked("BLOCKED_SCHEMA_INVALID", "Simple task cannot have complex context.")
        return
    if not isinstance(context, dict):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Complex task requires durable context.")
    exact_keys(context, COMPLEX_CONTEXT_KEYS, "BLOCKED_SCHEMA_INVALID")
    if context.get("workflow_version") != 1 or type(context.get("current_attempt")) is not int:
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Complex workflow identity is invalid.")
    for key in ("role_invocations", "approved_code_paths", "required_gates", "evidence_refs", "retained_resource_refs"):
        if not isinstance(context.get(key), list):
            raise Blocked("BLOCKED_SCHEMA_INVALID", f"Complex context array is invalid: {key}.")
    if context.get("closeout_disposition") is not None and not isinstance(context["closeout_disposition"], dict):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Complex closeout disposition is invalid.")


def migrate_v1_to_v2(control: dict[str, Any], *, decision_ref: str, closed_at: str) -> dict[str, Any]:
    validate_v1_control(control)
    active = control.get("active")
    if control.get("state") != "implemented_pending_human_review" or not isinstance(active, dict) or active.get("phase") != "human_review":
        raise Blocked("BLOCKED_CUTOVER_NOT_AUTHORIZED", "Cutover source must be the validated governance task in human review.")
    if not decision_ref or not closed_at:
        raise Blocked("BLOCKED_CUTOVER_NOT_AUTHORIZED", "Cutover close evidence is required.")
    migrated = json.loads(json.dumps(control))
    migrated["version"] = 2
    migrated["state"] = "idle"
    migrated["active"] = None
    migrated["last_closed"] = {
        "task_id": active["task_id"],
        "disposition": "closed atomically by approved v2 cutover",
        "decision_ref": decision_ref,
        "closed_at": closed_at,
    }
    validate_v2_control(migrated)
    return migrated


def v2_submit(control: dict[str, Any], request: dict[str, Any], head: str) -> tuple[str, str]:
    from scripts.connlab_serial_complex import classify_request
    decision = classify_request(request); task_id = request["task_id"]
    active = control.get("active")
    if isinstance(active, dict) and active.get("task_id") == task_id: return "NOOP_ALREADY_ACTIVE", "Task is already active."
    if any(item.get("task_id") == task_id for item in control["queue"]): return "QUEUED_EXISTING", "Task is already queued."
    if control["state"] != "idle" or control["queue"]:
        sequence = control["next_enqueue_sequence"]
        control["queue"].append({"task_id": task_id, "summary": request["summary"], "classification": decision["classification"], "reason_codes": decision["reason_codes"], "enqueue_sequence": sequence, "queued_at": now()})
        control["next_enqueue_sequence"] = sequence + 1
        return "QUEUED_NEW", "Task appended to FIFO queue."
    classification = decision["classification"]; timestamp = now()
    context = None if classification == "simple" else {
        "workflow_version": 1, "task_branch": None, "task_worktree": None, "base_sha": head, "head_sha": head,
        "integration_target": "master", "worktree_lifecycle": "absent", "current_role": None, "current_attempt": 0,
        "role_invocations": [], "host_thread_id": None, "host_id": None, "approved_code_paths": request.get("may_touch", []),
        "required_gates": ["Reviewer", "QA", "Integrator"], "developer_subject_commit": None,
        "reviewer_subject_commit": None, "qa_subject_commit": None, "integrated_commit": None, "evidence_refs": [],
        "pending_callback": None, "closeout_disposition": None, "retained_resource_refs": [],
        "close_decision_ref": None,
    }
    control["active"] = {"task_id": task_id, "summary": request["summary"], "kind": "simple" if classification == "simple" else "planned", "classification": classification, "phase": "implementation" if classification == "simple" else "planning", "scope_contract": request if classification == "simple" else None, "plan_ref": None, "approval_ref": None, "activation_parent_sha": head, "activated_at": timestamp, "updated_at": timestamp, "blocker": None, "validation": None, "complex_context": context}
    control["state"] = "running"
    return "ALLOW_ACTIVATE", "Task activated under version-2 serial authority."


def v2_activate_next(control: dict[str, Any], request: dict[str, Any], head: str) -> tuple[str, str]:
    if control.get("state") != "idle": raise Blocked("BLOCKED_STATE", "Board must be idle before FIFO activation.")
    if not control["queue"]: return "NOOP_QUEUE_EMPTY", "FIFO queue is empty."
    if control["queue"][0].get("task_id") != request.get("task_id"): raise Blocked("BLOCKED_FIFO_ORDER", "Only the exact FIFO head may activate.")
    remainder = control["queue"][1:]; control["queue"] = []
    code, reason = v2_submit(control, request, head)
    if code != "ALLOW_ACTIVATE": raise Blocked("BLOCKED_STATE", "FIFO head reclassification did not activate.")
    control["queue"] = remainder
    return "ALLOW_ACTIVATE_NEXT", reason


def render_board(prefix: str, value: dict[str, Any], suffix: str) -> bytes:
    block = BEGIN + "\n```json\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n```\n" + END
    return (prefix + block + suffix).encode("utf-8")


def git_dirty(root: Path) -> list[str]:
    result = run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if result.returncode != 0:
        raise Blocked("BLOCKED_PRIMARY_UNVERIFIED", "Git status could not be read.")
    return [line[3:].replace("\\", "/") for line in result.stdout.splitlines() if len(line) >= 4]


def committed_board(root: Path) -> bool:
    return run_git(root, "diff", "--quiet", "HEAD", "--", BOARD_REL).returncode == 0


@contextmanager
def writer_lock(root: Path) -> Iterator[None]:
    tmp = root / "tmp"
    tmp.mkdir(exist_ok=True)
    lock = tmp / "connlab_personal_task.lock"
    if lock.resolve(strict=False).parent != tmp.resolve():
        raise Blocked("BLOCKED_LOCK_PATH", "Lock path escaped the primary tmp directory.")
    if run_git(root, "check-ignore", "-q", "tmp/connlab_personal_task.lock").returncode != 0:
        raise Blocked("BLOCKED_LOCK_PATH", "Lock path is not ignored by Git.")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise Blocked("BLOCKED_LOCKED", "Personal task lock already exists; inspect it manually.") from exc
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode())
        os.close(descriptor)
        yield
    finally:
        try:
            os.close(descriptor)
        except OSError:
            pass
        lock.unlink(missing_ok=True)


def write_board(root: Path, board: Path, prefix: str, value: dict[str, Any], suffix: str) -> str:
    output = render_board(prefix, value, suffix)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=board.parent, prefix=".task_board.", suffix=".tmp", delete=False) as handle:
            temporary = handle.name
            handle.write(output)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, board)
        data = board.read_bytes()
        parse_board(data)
        if data != output:
            raise OSError("Post-write bytes differ.")
        return sha(data)
    except (OSError, Blocked) as exc:
        raise Blocked("BLOCKED_WRITE_FAILED", f"Atomic board write failed: {exc}") from exc
    finally:
        if temporary:
            Path(temporary).unlink(missing_ok=True)
