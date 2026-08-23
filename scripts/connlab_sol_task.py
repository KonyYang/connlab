#!/usr/bin/env python3
"""Compact task-state interface for ConnLab's GPT-5.6 Sol workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterator


BOARD_REL = Path("docs/task_board.md")
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"
CONTROL_SCHEMA = "connlab.sol-task-control"
REQUEST_SCHEMA = "connlab.sol-task-request"
CHECKPOINT_SCHEMA = "connlab.sol-task-checkpoint"
REPORT_SCHEMA = "connlab.sol-task-report"
TIERS = {"micro", "standard", "high_risk"}
ROUTES = {
    "micro": "sol_direct",
    "standard": "sol_build_review_qa",
    "high_risk": "full_chain",
}
REQUIRED_ROLES = {
    "micro": {"developer"},
    "standard": {"developer", "reviewer", "qa"},
    "high_risk": {"planner", "developer", "reviewer", "qa", "integrator"},
}
COMMANDS = ("inspect", "submit", "checkpoint", "finish", "revise", "close", "close-and-submit")


class Blocked(RuntimeError):
    def __init__(self, code: str, reason: str) -> None:
        super().__init__(reason)
        self.code = code
        self.reason = reason


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def current_head(root: Path) -> str:
    result = run_git(root, "rev-parse", "HEAD")
    if result.returncode != 0:
        raise Blocked("BLOCKED_GIT_INVALID", "Repository HEAD cannot be resolved.")
    return result.stdout.strip()


def require_clean(root: Path, reason: str) -> None:
    result = run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if result.returncode != 0:
        raise Blocked("BLOCKED_GIT_INVALID", "Repository status cannot be inspected.")
    if result.stdout:
        raise Blocked("BLOCKED_WORKTREE_DIRTY", reason)


def repository_path(value: Any, *, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Blocked(code, "Repository paths must be non-empty strings.")
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise Blocked(code, "Repository paths must be relative and cannot traverse parents.")
    return path.as_posix()


def exact_json(raw: str | None, *, schema: str, fields: set[str], code: str) -> dict[str, Any]:
    try:
        value = json.loads(raw or "")
    except json.JSONDecodeError as exc:
        raise Blocked(code, "JSON payload is invalid.") from exc
    if not isinstance(value, dict) or set(value) != fields:
        raise Blocked(code, "Payload fields do not match the compact schema.")
    if value.get("schema") != schema or value.get("version") != 1:
        raise Blocked(code, "Payload schema or version is unsupported.")
    return value


def validate_control(control: Any) -> None:
    fields = {
        "schema",
        "version",
        "mode",
        "wip_limit",
        "state",
        "active",
        "last_closed",
        "retained_history",
    }
    if not isinstance(control, dict) or set(control) != fields:
        raise Blocked("BLOCKED_BOARD_INVALID", "Board fields do not match the Sol-native schema.")
    if (
        control["schema"] != CONTROL_SCHEMA
        or control["version"] != 1
        or control["mode"] != "sol_native"
        or control["wip_limit"] != 1
        or control["state"] not in {"idle", "running", "ready_for_close"}
        or not isinstance(control["retained_history"], list)
    ):
        raise Blocked("BLOCKED_BOARD_INVALID", "Board authority values are invalid.")
    active = control["active"]
    if control["state"] == "idle":
        if active is not None:
            raise Blocked("BLOCKED_BOARD_INVALID", "Idle board cannot contain an active task.")
        return
    active_fields = {
        "task_id",
        "summary",
        "tier",
        "route",
        "scope",
        "scope_paths",
        "risk_reasons",
        "activation_head",
        "started_at",
        "updated_at",
        "checkpoint",
        "report",
    }
    if not isinstance(active, dict) or set(active) != active_fields:
        raise Blocked("BLOCKED_BOARD_INVALID", "Active task fields are invalid.")
    if active["tier"] not in TIERS or active["route"] != ROUTES[active["tier"]]:
        raise Blocked("BLOCKED_BOARD_INVALID", "Active task route is invalid.")
    if control["state"] == "running" and active["report"] is not None:
        raise Blocked("BLOCKED_BOARD_INVALID", "Running task cannot contain a final report.")
    if control["state"] == "ready_for_close" and not isinstance(active["report"], dict):
        raise Blocked("BLOCKED_BOARD_INVALID", "Ready task requires a final report.")


def read_board(root: Path) -> tuple[str, dict[str, Any], str, bytes]:
    try:
        raw = (root / BOARD_REL).read_bytes()
        text = raw.decode("utf-8")
        prefix, remainder = text.split(BEGIN, 1)
        block, suffix = remainder.split(END, 1)
        payload = block.split("```json", 1)[1].rsplit("```", 1)[0]
        control = json.loads(payload)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, IndexError) as exc:
        raise Blocked("BLOCKED_BOARD_INVALID", "Board control block cannot be parsed.") from exc
    validate_control(control)
    return prefix, control, suffix, raw


def render_board(prefix: str, control: dict[str, Any], suffix: str) -> bytes:
    return (
        prefix
        + BEGIN
        + "\n```json\n"
        + json.dumps(control, ensure_ascii=False, indent=2)
        + "\n```\n"
        + END
        + suffix
    ).encode("utf-8")


@contextmanager
def board_lock(root: Path) -> Iterator[None]:
    lock = root / "tmp/connlab_sol_task.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(lock, os.O_CREAT | os.O_RDWR)
    locked = False
    try:
        if os.name == "nt":
            import msvcrt

            if os.fstat(descriptor).st_size == 0:
                os.write(descriptor, b"\0")
            os.lseek(descriptor, 0, os.SEEK_SET)
            try:
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise Blocked("BLOCKED_LOCKED", "Another board write is active.") from exc
        else:
            import fcntl

            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise Blocked("BLOCKED_LOCKED", "Another board write is active.") from exc
        locked = True
        yield
    finally:
        if locked:
            if os.name == "nt":
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def update_board(
    root: Path,
    expected_hash: str | None,
    mutate: Callable[[dict[str, Any]], None],
) -> tuple[str, str, dict[str, Any]]:
    if not expected_hash:
        raise Blocked("BLOCKED_BOARD_HASH_REQUIRED", "Expected board SHA-256 is required.")
    with board_lock(root):
        prefix, control, suffix, raw = read_board(root)
        before = sha256(raw)
        if expected_hash != before:
            raise Blocked("BLOCKED_BOARD_HASH_MISMATCH", "Board changed; inspect before retrying.")
        mutate(control)
        validate_control(control)
        updated = render_board(prefix, control, suffix)
        temporary = (root / BOARD_REL).with_name(f"{BOARD_REL.name}.tmp.{os.getpid()}")
        temporary.write_bytes(updated)
        os.replace(temporary, root / BOARD_REL)
        if (root / BOARD_REL).read_bytes() != updated:
            raise Blocked("BLOCKED_BOARD_WRITE_FAILED", "Board readback differs from written bytes.")
        return before, sha256(updated), control


def active_snapshot(control: dict[str, Any]) -> dict[str, Any] | None:
    active = control["active"]
    if not isinstance(active, dict):
        return None
    report = active.get("report")
    return {
        "task_id": active["task_id"],
        "summary": active["summary"],
        "tier": active["tier"],
        "route": active["route"],
        "checkpoint": active["checkpoint"],
        "subject": report.get("subject") if isinstance(report, dict) else None,
    }


def next_action(control: dict[str, Any]) -> dict[str, Any]:
    if control["state"] == "idle":
        return {"command": "submit", "requires_user": True}
    if control["state"] == "ready_for_close":
        return {"command": "close", "requires_user": True}
    checkpoint = control["active"].get("checkpoint")
    if isinstance(checkpoint, dict) and checkpoint.get("status") == "blocked" and checkpoint.get("requires_user"):
        return {"command": "user_decision", "requires_user": True}
    return {"command": "execute", "requires_user": False}


def result(
    code: str,
    command: str,
    root: Path,
    control: dict[str, Any] | None,
    before: str | None,
    after: str | None,
    *,
    task_id: str | None = None,
    changed: bool = False,
    reason: str = "",
) -> dict[str, Any]:
    active = control.get("active") if isinstance(control, dict) else None
    return {
        "schema": "connlab.sol-task-result",
        "version": 1,
        "code": code,
        "allowed": not code.startswith("BLOCKED_"),
        "changed": changed,
        "command": command,
        "task_id": task_id,
        "state": control.get("state") if isinstance(control, dict) else None,
        "active_task_id": active.get("task_id") if isinstance(active, dict) else None,
        "board_sha256_before": before,
        "board_sha256_after": after,
        "primary_root": str(root),
        "reason": reason,
        "active_snapshot": active_snapshot(control) if isinstance(control, dict) else None,
        "next_action": next_action(control) if isinstance(control, dict) else {"command": "inspect", "requires_user": False},
    }


def require_active(control: dict[str, Any], task_id: str | None, state: str | None = None) -> dict[str, Any]:
    active = control.get("active")
    if not isinstance(active, dict) or active.get("task_id") != task_id:
        raise Blocked("BLOCKED_TASK_MISMATCH", "Requested task is not active.")
    if state and control["state"] != state:
        raise Blocked("BLOCKED_STATE", f"Task must be in {state} state.")
    return active


def request_payload(raw: str | None, task_id: str | None) -> dict[str, Any]:
    payload = exact_json(
        raw,
        schema=REQUEST_SCHEMA,
        fields={"schema", "version", "task_id", "summary", "tier", "scope", "scope_paths", "risk_reasons"},
        code="BLOCKED_REQUEST_INVALID",
    )
    if payload["task_id"] != task_id or not isinstance(task_id, str) or not task_id.strip():
        raise Blocked("BLOCKED_REQUEST_INVALID", "Request task identity does not match the command.")
    if not isinstance(payload["summary"], str) or not payload["summary"].strip():
        raise Blocked("BLOCKED_REQUEST_INVALID", "Request summary is required.")
    if not isinstance(payload["scope"], str) or not payload["scope"].strip():
        raise Blocked("BLOCKED_REQUEST_INVALID", "Request scope is required.")
    if payload["tier"] not in TIERS:
        raise Blocked("BLOCKED_REQUEST_INVALID", "Tier must be micro, standard, or high_risk.")
    paths = payload["scope_paths"]
    if not isinstance(paths, list) or any(not isinstance(path, str) for path in paths):
        raise Blocked("BLOCKED_REQUEST_INVALID", "Scope paths must be a unique list.")
    normalized_paths = [repository_path(path, code="BLOCKED_REQUEST_INVALID") for path in paths]
    if len(normalized_paths) != len(set(normalized_paths)):
        raise Blocked("BLOCKED_REQUEST_INVALID", "Scope paths must be a unique list.")
    payload["scope_paths"] = normalized_paths
    risks = payload["risk_reasons"]
    if not isinstance(risks, list) or any(not isinstance(item, str) or not item.strip() for item in risks):
        raise Blocked("BLOCKED_REQUEST_INVALID", "Risk reasons must be non-empty strings.")
    if risks and payload["tier"] != "high_risk":
        raise Blocked("BLOCKED_TIER_UNSAFE", "Recorded risk requires the high_risk tier.")
    return payload


def activated_task(payload: dict[str, Any], head: str, timestamp: str) -> dict[str, Any]:
    return {
        "task_id": payload["task_id"],
        "summary": payload["summary"],
        "tier": payload["tier"],
        "route": ROUTES[payload["tier"]],
        "scope": payload["scope"],
        "scope_paths": payload["scope_paths"],
        "risk_reasons": payload["risk_reasons"],
        "activation_head": head,
        "started_at": timestamp,
        "updated_at": timestamp,
        "checkpoint": None,
        "report": None,
    }


def submit(args: argparse.Namespace, root: Path) -> tuple[str, str, dict[str, Any]]:
    payload = request_payload(args.request_json, args.task_id)
    _, snapshot, _, _ = read_board(root)
    if snapshot["state"] != "idle" or snapshot["active"] is not None:
        raise Blocked("BLOCKED_ACTIVE_TASK_RUNNING", "Close the active task before submitting another.")
    require_clean(root, "Primary must be clean before task submission.")
    head = current_head(root)

    def mutate(control: dict[str, Any]) -> None:
        if control["state"] != "idle" or control["active"] is not None:
            raise Blocked("BLOCKED_ACTIVE_TASK_RUNNING", "Close the active task before submitting another.")
        timestamp = utc_now()
        control["state"] = "running"
        control["active"] = activated_task(payload, head, timestamp)

    return update_board(root, args.expected_board_sha256, mutate)


def checkpoint_payload(raw: str | None, task_id: str | None) -> dict[str, Any]:
    payload = exact_json(
        raw,
        schema=CHECKPOINT_SCHEMA,
        fields={"schema", "version", "task_id", "stage", "status", "summary", "requires_user"},
        code="BLOCKED_CHECKPOINT_INVALID",
    )
    if payload["task_id"] != task_id:
        raise Blocked("BLOCKED_TASK_MISMATCH", "Checkpoint task identity does not match the command.")
    if payload["status"] not in {"running", "blocked"} or not isinstance(payload["requires_user"], bool):
        raise Blocked("BLOCKED_CHECKPOINT_INVALID", "Checkpoint status is invalid.")
    if any(not isinstance(payload[key], str) or not payload[key].strip() for key in ("stage", "summary")):
        raise Blocked("BLOCKED_CHECKPOINT_INVALID", "Checkpoint stage and summary are required.")
    return payload


def checkpoint(args: argparse.Namespace, root: Path) -> tuple[str, str, dict[str, Any]]:
    payload = checkpoint_payload(args.checkpoint_json, args.task_id)

    def mutate(control: dict[str, Any]) -> None:
        active = require_active(control, args.task_id, "running")
        active["checkpoint"] = payload
        active["updated_at"] = utc_now()

    return update_board(root, args.expected_board_sha256, mutate)


def report_payload(raw: str | None, task_id: str | None) -> dict[str, Any]:
    payload = exact_json(
        raw,
        schema=REPORT_SCHEMA,
        fields={
            "schema",
            "version",
            "task_id",
            "subject",
            "summary",
            "scope_ok",
            "changed_paths",
            "validation",
            "roles",
            "integration",
        },
        code="BLOCKED_REPORT_INVALID",
    )
    if payload["task_id"] != task_id:
        raise Blocked("BLOCKED_TASK_MISMATCH", "Report task identity does not match the command.")
    if not isinstance(payload["subject"], str) or len(payload["subject"]) != 40:
        raise Blocked("BLOCKED_REPORT_INVALID", "Report subject must be a full Git commit.")
    if not isinstance(payload["summary"], str) or not payload["summary"].strip() or payload["scope_ok"] is not True:
        raise Blocked("BLOCKED_REPORT_INCOMPLETE", "Report must attest an in-scope completed result.")
    paths = payload["changed_paths"]
    if not isinstance(paths, list) or any(not isinstance(path, str) for path in paths):
        raise Blocked("BLOCKED_REPORT_INVALID", "Changed paths must be a unique list.")
    normalized_paths = [repository_path(path, code="BLOCKED_REPORT_INVALID") for path in paths]
    if len(normalized_paths) != len(set(normalized_paths)):
        raise Blocked("BLOCKED_REPORT_INVALID", "Changed paths must be a unique list.")
    payload["changed_paths"] = normalized_paths
    validation = payload["validation"]
    if not isinstance(validation, list) or not validation or any(
        not isinstance(item, dict) or item.get("status") != "passed" for item in validation
    ):
        raise Blocked("BLOCKED_REPORT_INCOMPLETE", "At least one passing validation result is required.")
    if not isinstance(payload["roles"], dict):
        raise Blocked("BLOCKED_REPORT_INCOMPLETE", "Role results are required.")
    if not isinstance(payload["integration"], dict) or payload["integration"].get("status") != "passed":
        raise Blocked("BLOCKED_REPORT_INCOMPLETE", "Successful integration facts are required.")
    return payload


def changed_paths(root: Path, base: str, subject: str) -> list[str]:
    result = run_git(root, "diff", "--name-only", f"{base}..{subject}", "--")
    if result.returncode != 0:
        raise Blocked("BLOCKED_GIT_INVALID", "Task diff cannot be inspected.")
    return sorted(
        path.replace("\\", "/")
        for path in result.stdout.splitlines()
        if path.strip() and path.replace("\\", "/") != BOARD_REL.as_posix()
    )


def finish(args: argparse.Namespace, root: Path) -> tuple[str, str, dict[str, Any]]:
    payload = report_payload(args.result_json, args.task_id)
    require_clean(root, "Primary must be clean before final task recording.")
    head = current_head(root)
    if payload["subject"] != head:
        raise Blocked("BLOCKED_SUBJECT_MISMATCH", "Report subject is not the current clean HEAD.")

    def mutate(control: dict[str, Any]) -> None:
        active = require_active(control, args.task_id, "running")
        roles = payload["roles"]
        if any(
            not isinstance(roles.get(role), dict) or roles[role].get("status") != "passed"
            for role in REQUIRED_ROLES[active["tier"]]
        ):
            raise Blocked("BLOCKED_REPORT_INCOMPLETE", "Report lacks a passing result for this task tier.")
        observed = changed_paths(root, active["activation_head"], head)
        if sorted(payload["changed_paths"]) != observed:
            raise Blocked("BLOCKED_SCOPE_DRIFT", "Reported paths differ from the exact Git diff.")
        if (
            active["tier"] == "high_risk"
            and active["scope_paths"]
            and not set(observed).issubset(set(active["scope_paths"]))
        ):
            raise Blocked("BLOCKED_SCOPE_DRIFT", "Exact Git diff exceeds the recorded scope.")
        active["report"] = payload
        active["checkpoint"] = {
            "schema": CHECKPOINT_SCHEMA,
            "version": 1,
            "task_id": active["task_id"],
            "stage": "delivery",
            "status": "running",
            "summary": "Implementation, review, validation, and integration are complete.",
            "requires_user": False,
        }
        active["updated_at"] = utc_now()
        control["state"] = "ready_for_close"

    return update_board(root, args.expected_board_sha256, mutate)


def closed_task(
    active: dict[str, Any],
    *,
    disposition: str,
    decision_ref: str,
    fallback_subject: str,
    timestamp: str,
) -> dict[str, Any]:
    report = active.get("report")
    return {
        "task_id": active["task_id"],
        "tier": active["tier"],
        "subject": report.get("subject") if isinstance(report, dict) else fallback_subject,
        "summary": active["summary"],
        "disposition": disposition,
        "decision_ref": decision_ref,
        "closed_at": timestamp,
    }


def required_decision_ref(value: str | None, reason: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Blocked("BLOCKED_DECISION_REQUIRED", reason)
    return value


def revise(args: argparse.Namespace, root: Path) -> tuple[str, str, dict[str, Any]]:
    feedback = required_decision_ref(args.decision_ref, "User feedback requiring revision is required.")

    def mutate(control: dict[str, Any]) -> None:
        active = require_active(control, args.task_id, "ready_for_close")
        active["report"] = None
        active["checkpoint"] = {
            "schema": CHECKPOINT_SCHEMA,
            "version": 1,
            "task_id": active["task_id"],
            "stage": "revision",
            "status": "running",
            "summary": feedback.strip(),
            "requires_user": False,
        }
        active["updated_at"] = utc_now()
        control["state"] = "running"

    return update_board(root, args.expected_board_sha256, mutate)


def close(args: argparse.Namespace, root: Path) -> tuple[str, str, dict[str, Any]]:
    decision_ref = required_decision_ref(args.decision_ref, "Explicit User close or cancel decision is required.")
    require_clean(root, "Primary must be clean before WIP is released.")
    head = current_head(root)

    def mutate(control: dict[str, Any]) -> None:
        active = require_active(control, args.task_id)
        cancelled = args.disposition == "cancelled"
        if not cancelled and control["state"] != "ready_for_close":
            raise Blocked("BLOCKED_STATE", "Only a completed task can be closed normally.")
        control["last_closed"] = closed_task(
            active,
            disposition=args.disposition,
            decision_ref=decision_ref,
            fallback_subject=head,
            timestamp=utc_now(),
        )
        control["active"] = None
        control["state"] = "idle"

    return update_board(root, args.expected_board_sha256, mutate)


def close_and_submit(args: argparse.Namespace, root: Path) -> tuple[str, str, dict[str, Any]]:
    decision_ref = required_decision_ref(args.decision_ref, "Explicit User close or cancel decision is required.")
    payload = request_payload(args.request_json, args.next_task_id)
    require_clean(root, "Primary must be clean before completed WIP is replaced.")
    head = current_head(root)

    def mutate(control: dict[str, Any]) -> None:
        active = require_active(control, args.task_id)
        cancelled = args.disposition == "cancelled"
        if not cancelled and control["state"] != "ready_for_close":
            raise Blocked("BLOCKED_STATE", "Only a completed task can be closed normally.")
        timestamp = utc_now()
        control["last_closed"] = closed_task(
            active,
            disposition=args.disposition,
            decision_ref=decision_ref,
            fallback_subject=head,
            timestamp=timestamp,
        )
        control["active"] = activated_task(payload, head, timestamp)
        control["state"] = "running"

    return update_board(root, args.expected_board_sha256, mutate)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("command", choices=COMMANDS)
    value.add_argument("--repo-root", required=True)
    value.add_argument("--expected-board-sha256")
    value.add_argument("--task-id")
    value.add_argument("--next-task-id")
    value.add_argument("--request-json")
    value.add_argument("--checkpoint-json")
    value.add_argument("--result-json")
    value.add_argument("--decision-ref")
    value.add_argument("--disposition", choices=("completed", "cancelled"), default="completed")
    value.add_argument("--json", action="store_true")
    return value


def main() -> int:
    args = parser().parse_args()
    root = Path(args.repo_root).resolve()
    control: dict[str, Any] | None = None
    before: str | None = None
    try:
        _, control, _, raw = read_board(root)
        before = sha256(raw)
        if args.command == "inspect":
            payload = result("ALLOW_INSPECT", "inspect", root, control, before, before, reason="Compact task state inspected.")
        else:
            handlers: dict[str, tuple[Callable[..., tuple[str, str, dict[str, Any]]], str]] = {
                "submit": (submit, "ALLOW_SUBMIT"),
                "checkpoint": (checkpoint, "ALLOW_CHECKPOINT"),
                "finish": (finish, "ALLOW_FINISH"),
                "revise": (revise, "ALLOW_REVISE"),
                "close": (close, "ALLOW_CLOSE"),
                "close-and-submit": (close_and_submit, "ALLOW_CLOSE_AND_SUBMIT"),
            }
            handler, code = handlers[args.command]
            before, after, control = handler(args, root)
            payload = result(
                code,
                args.command,
                root,
                control,
                before,
                after,
                task_id=args.task_id,
                changed=True,
                reason=f"{args.command.title()} completed.",
            )
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        return 0
    except Blocked as exc:
        try:
            _, control, _, raw = read_board(root)
            after = sha256(raw)
        except Blocked:
            after = before
        payload = result(
            exc.code,
            args.command,
            root,
            control,
            before,
            after,
            task_id=args.task_id,
            reason=exc.reason,
        )
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
