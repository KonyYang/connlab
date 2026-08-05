#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterator


BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"
BOARD_REL = "docs/task_board.md"
COMMANDS = ("inspect", "check", "submit", "activate-next", "approve", "mark-review", "block", "resume", "cancel", "close")
FORBIDDEN_KEYS = {"api_contract", "database", "schema_or_migration", "persistence", "authority", "public_drive_workflow", "business_rule_semantics", "destructive_action", "external_mutation"}
BLOCKER_CODES = {"VALIDATION_FAILED", "UNEXPECTED_PATHS", "SCOPE_EXPANDED", "IMPLEMENTATION_FAILED", "DIRTY_WORKTREE", "EXTERNAL_BLOCKER"}
RESULT_FIELDS = ("schema", "version", "code", "allowed", "changed", "command", "task_id", "state", "active_task_id", "queue_position", "board_sha256_before", "board_sha256_after", "primary_root", "reason")
class Blocked(Exception):
    def __init__(self, code: str, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(reason)
def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args], text=True, capture_output=True, check=False
    )
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
def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
def exact_keys(value: dict[str, Any], expected: set[str], code: str) -> None:
    if set(value) != expected:
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
    exact_keys(
        value,
        {"schema", "version", "task_id", "summary", "kind", "may_touch", "expected_file_count", "classification_reason", "targeted_validation", "forbidden_categories"},
        "BLOCKED_APPROVED_SCOPE_INVALID",
    )
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
        if active.get("kind") not in {"simple", "planned"} or active.get("phase") not in {"planning", "implementation", "blocked", "human_review"} or not isinstance(active.get("task_id"), str):
            raise Blocked("BLOCKED_SCHEMA_INVALID", "Active task fields are invalid.")
        ids.append(active["task_id"])
    previous = 0
    for item in value["queue"]:
        if not isinstance(item, dict) or set(item) != {"task_id", "summary", "kind", "enqueue_sequence", "queued_at", "scope_contract"}:
            raise Blocked("BLOCKED_SCHEMA_INVALID", "Queue record is invalid.")
        if item.get("kind") not in {"simple", "planned"} or type(item.get("enqueue_sequence")) is not int or item["enqueue_sequence"] <= previous:
            raise Blocked("BLOCKED_SCHEMA_INVALID", "Queue ordering is invalid.")
        previous = item["enqueue_sequence"]
        ids.append(item.get("task_id"))
    if len(ids) != len(set(ids)):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "Active and queued task IDs must be unique.")
def render_board(prefix: str, value: dict[str, Any], suffix: str) -> bytes:
    block = BEGIN + "\n```json\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n```\n" + END
    return (prefix + block + suffix).encode("utf-8")
def git_dirty(root: Path) -> list[str]:
    result = run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if result.returncode != 0:
        raise Blocked("BLOCKED_PRIMARY_UNVERIFIED", "Git status could not be read.")
    return [line[3:].replace("\\", "/") for line in result.stdout.splitlines() if len(line) >= 4]
def committed_board(root: Path) -> bool:
    result = run_git(root, "diff", "--quiet", "HEAD", "--", BOARD_REL)
    return result.returncode == 0
@contextmanager
def writer_lock(root: Path) -> Iterator[None]:
    tmp = root / "tmp"
    tmp.mkdir(exist_ok=True)
    expected_parent = tmp.resolve()
    lock = tmp / "connlab_personal_task.lock"
    if lock.resolve(strict=False).parent != expected_parent:
        raise Blocked("BLOCKED_LOCK_PATH", "Lock path escaped the primary tmp directory.")
    ignored = run_git(root, "check-ignore", "-q", "tmp/connlab_personal_task.lock")
    if ignored.returncode != 0:
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
def result(code: str, command: str, root: Path | None, before: str | None, after: str | None, control: dict[str, Any] | None, *, task_id: str | None = None, changed: bool = False, reason: str = "") -> dict[str, Any]:
    active = control.get("active") if control else None
    queue_position = None
    if control and task_id:
        for position, item in enumerate(control.get("queue", []), 1):
            if item.get("task_id") == task_id:
                queue_position = position
                break
    return dict(zip(RESULT_FIELDS, (
        "connlab.personal-task-result", 1, code, not code.startswith("BLOCKED_"), changed,
        command, task_id, control.get("state") if control else None,
        active.get("task_id") if isinstance(active, dict) else None, queue_position, before, after,
        str(root) if root else None, reason,
    )))
def require_active(control: dict[str, Any], task_id: str) -> dict[str, Any]:
    active = control.get("active")
    if not isinstance(active, dict) or active.get("task_id") != task_id:
        raise Blocked("BLOCKED_TASK_MISMATCH", "The requested task is not active.")
    return active
def active_from_request(request: dict[str, Any], scope: dict[str, Any] | None, head: str) -> dict[str, Any]:
    timestamp = now()
    return {
        "task_id": request["task_id"], "summary": request["summary"], "kind": request["kind"],
        "phase": "implementation" if request["kind"] == "simple" else "planning",
        "scope_contract": scope, "plan_ref": None, "approval_ref": None,
        "activation_parent_sha": head, "activated_at": timestamp, "updated_at": timestamp,
        "blocker": None, "validation": None,
    }
def transition(args: argparse.Namespace, root: Path, control: dict[str, Any]) -> tuple[str, bool, str]:
    command, task_id = args.command, args.task_id
    active = control.get("active")
    if command == "submit":
        request, scope = request_payload(args.request_json, task_id)
        if isinstance(active, dict) and active.get("task_id") == task_id:
            return "NOOP_ALREADY_ACTIVE", False, "Task is already active."
        for item in control["queue"]:
            if item["task_id"] == task_id:
                return "QUEUED_EXISTING", False, "Task is already queued."
        if control["state"] == "idle":
            if git_dirty(root):
                raise Blocked("BLOCKED_WORKTREE_DIRTY", "A clean primary worktree is required for activation.")
            head = run_git(root, "rev-parse", "HEAD").stdout.strip()
            control["active"] = active_from_request(request, scope, head)
            control["state"] = "running"
            return "ALLOW_ACTIVATE", True, "Task activated."
        sequence = control["next_enqueue_sequence"]
        control["queue"].append({
            "task_id": task_id, "summary": request["summary"], "kind": request["kind"],
            "enqueue_sequence": sequence, "queued_at": now(), "scope_contract": scope,
        })
        control["next_enqueue_sequence"] = sequence + 1
        return "QUEUED_NEW", True, "Task appended to FIFO queue."
    if command == "activate-next":
        if control["state"] != "idle":
            raise Blocked("BLOCKED_STATE", "Board must be idle before activating the queue head.")
        if not control["queue"]:
            return "NOOP_QUEUE_EMPTY", False, "FIFO queue is empty."
        if control["queue"][0]["task_id"] != task_id:
            raise Blocked("BLOCKED_FIFO_ORDER", "Only the exact FIFO head may activate.")
        if git_dirty(root):
            raise Blocked("BLOCKED_WORKTREE_DIRTY", "A clean primary worktree is required for activation.")
        item = control["queue"].pop(0)
        request = {"task_id": item["task_id"], "summary": item["summary"], "kind": item["kind"]}
        control["active"] = active_from_request(request, item["scope_contract"], run_git(root, "rev-parse", "HEAD").stdout.strip())
        control["state"] = "running"
        return "ALLOW_ACTIVATE_NEXT", True, "FIFO head activated."
    active = require_active(control, task_id)
    if command == "approve":
        if active["kind"] != "planned":
            raise Blocked("BLOCKED_STATE", "Only a planned task can be approved.")
        if active["phase"] == "implementation" and active["approval_ref"]:
            return "NOOP_ALREADY_APPROVED", False, "Task is already approved."
        scope_amend = active["phase"] == "blocked" and isinstance(active.get("blocker"), dict) and active["blocker"].get("code") == "SCOPE_EXPANDED" and isinstance(active.get("scope_contract"), dict)
        if active["phase"] != "planning" and not scope_amend:
            raise Blocked("BLOCKED_STATE", "Planned task is not in planning phase.")
        if not committed_board(root):
            raise Blocked("BLOCKED_TRANSITION_UNCOMMITTED", "The preceding board transition must be committed first.")
        approved, scope = approved_payload(args.approved_request_json, task_id)
        if not args.plan_ref:
            raise Blocked("BLOCKED_PLAN_REQUIRED", "A committed plan reference is required.")
        if not re.fullmatch(r".+@[0-9a-f]{40}#[0-9a-f]{64}", args.plan_ref):
            raise Blocked("BLOCKED_PLAN_REQUIRED", "Plan reference format is invalid.")
        if not args.approval_ref:
            raise Blocked("BLOCKED_APPROVAL_REQUIRED", "Explicit User approval is required.")
        if scope_amend:
            previous = active["scope_contract"]; old_paths, new_paths = set(previous["may_touch"]), set(scope["may_touch"])
            if not old_paths < new_paths: raise Blocked("BLOCKED_APPROVED_SCOPE_INVALID", "A scope amendment must be a strict path superset.")
            if scope["forbidden_categories"] != previous["forbidden_categories"]: raise Blocked("BLOCKED_APPROVED_SCOPE_INVALID", "A scope amendment cannot change risk-category facts.")
            active.update(summary=approved["summary"], scope_contract=scope, plan_ref=args.plan_ref, approval_ref=args.approval_ref, updated_at=now())
            return "ALLOW_SCOPE_AMEND", True, "User-approved scope expansion recorded; blocker remains until explicit resume."
        active.update(summary=approved["summary"], scope_contract=scope, plan_ref=args.plan_ref, approval_ref=args.approval_ref, phase="implementation", updated_at=now())
        return "ALLOW_APPROVE", True, "Approved scope bound to active task."
    if command == "mark-review":
        if control["state"] == "implemented_pending_human_review":
            return "NOOP_ALREADY_PENDING_REVIEW", False, "Task already awaits human review."
        if active["phase"] != "implementation" or active["blocker"] is not None or active["scope_contract"] is None:
            raise Blocked("BLOCKED_STATE", "Task is not eligible for human review.")
        value = validation_payload(args.validation_json, require_pass=True)
        allowed = set(active["scope_contract"]["may_touch"])
        unexpected = set(value["observed_paths"]) - allowed
        if unexpected:
            raise Blocked("BLOCKED_UNEXPECTED_PATHS", "Validation reports paths outside approved scope.")
        active.update(phase="human_review", validation=value, updated_at=now())
        control["state"] = "implemented_pending_human_review"
        return "ALLOW_MARK_REVIEW", True, "Implementation awaits human review."
    if command == "block":
        value = blocker_payload(args.blocker_json)
        if active["blocker"] == value and active["phase"] == "blocked":
            return "NOOP_ALREADY_BLOCKED", False, "Identical blocker is already recorded."
        active.update(blocker=value, phase="blocked", updated_at=now())
        control["state"] = "running"
        return "ALLOW_BLOCK", True, "Blocker recorded; active slot retained."
    if command == "resume":
        if active["phase"] != "blocked" or active["blocker"] is None:
            raise Blocked("BLOCKED_STATE", "Task is not blocked.")
        if not args.decision_ref:
            raise Blocked("BLOCKED_STATE", "Explicit User decision reference is required.")
        active.update(blocker=None, phase="implementation" if active["scope_contract"] else "planning", updated_at=now())
        return "ALLOW_RESUME", True, "Blocker cleared by explicit User direction."
    if command in {"cancel", "close"}:
        if git_dirty(root):
            raise Blocked("BLOCKED_WORKTREE_DIRTY", "A clean primary worktree is required.")
        if not args.decision_ref:
            raise Blocked("BLOCKED_STATE", "Explicit User decision reference is required.")
        if command == "close":
            if control["state"] != "implemented_pending_human_review" or active["phase"] != "human_review" or not active["validation"] or active["validation"].get("status") != "passed":
                raise Blocked("BLOCKED_STATE", "Only a validated task awaiting human review can close.")
            code, disposition = "ALLOW_CLOSE", "closed after human review"
        else:
            if not args.disposition:
                raise Blocked("BLOCKED_STATE", "Cancellation disposition is required.")
            code, disposition = "ALLOW_CANCEL", args.disposition
        control["last_closed"] = {"task_id": task_id, "disposition": disposition, "decision_ref": args.decision_ref, "closed_at": now()}
        control["active"] = None
        control["state"] = "idle"
        return code, True, disposition
    raise Blocked("BLOCKED_STATE", "Unsupported transition.")
def check(args: argparse.Namespace, root: Path, control: dict[str, Any]) -> tuple[str, str]:
    if args.intent == "Inspect":
        return "ALLOW_INSPECT", "Personal serial board is readable."
    active = require_active(control, args.task_id)
    if args.intent == "Implementation":
        if active["phase"] == "planning":
            raise Blocked("BLOCKED_APPROVAL_REQUIRED", "Planned task requires approved scope.")
        if active["phase"] != "implementation" or active["blocker"] is not None or control["state"] != "running":
            raise Blocked("BLOCKED_STATE", "Task is not eligible for implementation.")
        return "ALLOW_IMPLEMENTATION", "Active task may be implemented."
    if control["state"] != "implemented_pending_human_review" or active["phase"] != "human_review":
        raise Blocked("BLOCKED_STATE", "Task is not eligible to close.")
    if git_dirty(root):
        raise Blocked("BLOCKED_WORKTREE_DIRTY", "Primary worktree must be clean to close.")
    return "ALLOW_CLOSE", "Task is eligible to close after explicit User direction."
def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("command", choices=COMMANDS)
    value.add_argument("--repo-root", required=True)
    value.add_argument("--json", action="store_true")
    value.add_argument("--expected-board-sha256")
    value.add_argument("--task-id")
    value.add_argument("--request-json")
    value.add_argument("--approved-request-json")
    value.add_argument("--plan-ref")
    value.add_argument("--approval-ref")
    value.add_argument("--validation-json")
    value.add_argument("--blocker-json")
    value.add_argument("--decision-ref")
    value.add_argument("--disposition")
    value.add_argument("--intent", choices=("Inspect", "Implementation", "Close"))
    return value
def main() -> int:
    args = parser().parse_args()
    root: Path | None = None
    control: dict[str, Any] | None = None
    before: str | None = None
    try:
        root = resolve_primary(args.repo_root)
        board = root / BOARD_REL
        data = board.read_bytes()
        before = sha(data)
        prefix, control, suffix = parse_board(data)
        if args.command == "inspect":
            output = result("ALLOW_INSPECT", args.command, root, before, before, control, reason=f"Git dirty paths: {len(git_dirty(root))}.")
        elif args.command == "check":
            if not args.intent or (args.intent != "Inspect" and not args.task_id):
                raise Blocked("BLOCKED_STATE", "Check intent/task arguments are incomplete.")
            code, reason = check(args, root, control)
            output = result(code, args.command, root, before, before, control, task_id=args.task_id, reason=reason)
        else:
            if not args.task_id or not re.fullmatch(r"[A-Z][A-Z0-9_\-]+", args.task_id):
                raise Blocked("BLOCKED_TASK_MISMATCH", "A valid task ID is required.")
            if not args.expected_board_sha256 or not re.fullmatch(r"[0-9a-f]{64}", args.expected_board_sha256):
                raise Blocked("BLOCKED_BOARD_HASH_MISMATCH", "Expected board SHA-256 is required.")
            with writer_lock(root):
                data = board.read_bytes()
                before = sha(data)
                prefix, control, suffix = parse_board(data)
                if before != args.expected_board_sha256:
                    raise Blocked("BLOCKED_BOARD_HASH_MISMATCH", "Board changed since caller inspection.")
                code, changed, reason = transition(args, root, control)
                after = write_board(root, board, prefix, control, suffix) if changed else before
            output = result(code, args.command, root, before, after, control, task_id=args.task_id, changed=changed, reason=reason)
    except (Blocked, OSError) as exc:
        blocked = exc if isinstance(exc, Blocked) else Blocked("BLOCKED_PRIMARY_UNVERIFIED", str(exc))
        output = result(blocked.code, args.command, root, before, before, control, task_id=getattr(args, "task_id", None), reason=blocked.reason)
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")) if args.json else "\n".join(f"{key}: {value}" for key, value in output.items()))
    return 2 if output["code"].startswith("BLOCKED_") else 0
if __name__ == "__main__":
    sys.exit(main())
