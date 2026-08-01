"""Reference-only ConnLab role handoff, callback, and cadence validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


CALLBACK_FIELDS = ("TASK_ID", "ROLE", "STATUS", "EVIDENCE", "COMMIT", "NEXT", "BLOCKER")
REQUIRED_CAPSULE = (
    "schema", "task_id", "role", "status", "next", "blocker", "board_ref",
    "task_ref", "plan_ref", "evidence_ref", "direct_dependencies", "omissions",
    "transition_count", "dispatch_count", "dispatch_template",
)
REF_PATTERN = re.compile(r"([^@#]+)@([0-9a-f]{40})#([0-9a-f]{64})")
ROUTINE_STATUSES = {
    "developer_dispatch_ready", "ready_for_review", "reviewer_blocked",
    "reviewer_pass", "qa_pass",
}


class Blocked(Exception):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail); self.code = code; self.detail = detail


class FullRead(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(detail); self.detail = detail


def load_text(value: str) -> str:
    if "\n" not in value and "\r" not in value:
        path = Path(value)
        try:
            if path.is_file(): return path.read_text(encoding="utf-8")
        except OSError:
            pass
    return value


def load_json(value: str) -> tuple[dict[str, Any], int]:
    raw = load_text(value)
    try: payload = json.loads(raw)
    except json.JSONDecodeError as exc: raise FullRead(f"invalid capsule JSON: {exc}") from exc
    if not isinstance(payload, dict): raise FullRead("capsule must be an object")
    return payload, len(raw.encode("utf-8"))


def git_blob(repo: Path, reference: str) -> tuple[str, bytes]:
    match = REF_PATTERN.fullmatch(reference)
    if not match or Path(match.group(1)).is_absolute() or ".." in Path(match.group(1)).parts:
        raise FullRead("reference must be safe path@commit#sha256")
    path, commit, expected = match.groups()
    done = subprocess.run(
        ["git", "-C", str(repo), "show", f"{commit}:{path}"],
        check=False, capture_output=True,
    )
    if done.returncode or hashlib.sha256(done.stdout).hexdigest() != expected:
        raise FullRead(f"reference cannot be proven: {path}")
    return path, done.stdout


def validate_repo(repo: Path) -> None:
    done = subprocess.run(["git", "-C", str(repo), "rev-parse", "--show-toplevel"], check=False, capture_output=True, text=True)
    branch = subprocess.run(["git", "-C", str(repo), "branch", "--show-current"], check=False, capture_output=True, text=True)
    if done.returncode or Path(done.stdout.strip()).resolve() != repo or branch.returncode or branch.stdout.strip() != "master":
        raise FullRead("primary repository root cannot be proven")


def references(capsule: dict[str, Any]) -> list[str]:
    refs = [capsule.get("board_ref"), capsule.get("task_ref"), capsule.get("plan_ref"), capsule.get("evidence_ref")]
    direct = capsule.get("direct_dependencies")
    if not isinstance(direct, list): raise FullRead("direct_dependencies must be an array")
    refs.extend(direct)
    if not all(isinstance(item, str) and item for item in refs): raise FullRead("required references are incomplete")
    return refs


def validate_omissions(capsule: dict[str, Any], ref_paths: set[str]) -> None:
    omissions = capsule.get("omissions")
    if not isinstance(omissions, list): raise FullRead("omissions must be an array")
    for item in omissions:
        if not isinstance(item, dict) or item.get("reason") != "immutable_history" or not str(item.get("path", "")).replace("\\", "/").startswith("docs/archive/task_board_history"):
            raise FullRead("an omission is not proven safe")
    changed = capsule.get("changed_paths", [])
    if not isinstance(changed, list): raise FullRead("changed_paths must be an array")
    omitted_archive = bool(omissions)
    for path in changed:
        if not isinstance(path, str): raise FullRead("changed path must be a string")
        normalized = path.replace("\\", "/")
        if normalized in ref_paths:
            continue
        if normalized.startswith("docs/archive/task_board_history/") and omitted_archive:
            continue
        raise FullRead(f"changed path is neither referenced nor safely omitted: {normalized}")


def validate_capsule(capsule: dict[str, Any], source_bytes: int, repo: Path) -> tuple[list[str], int]:
    missing = [field for field in REQUIRED_CAPSULE if field not in capsule or capsule[field] in (None, "")]
    if missing: raise FullRead("capsule fields are missing: " + ",".join(missing))
    if capsule["schema"] != "connlab.handoff.v1": raise FullRead("unsupported handoff schema")
    if source_bytes > 4096: raise Blocked("BLOCKED_CAPSULE_BUDGET", "complete dispatch capsule exceeds 4096 bytes")
    template_bytes = len(str(capsule["dispatch_template"]).encode("utf-8"))
    if template_bytes > 2048: raise Blocked("BLOCKED_TEMPLATE_BUDGET", "dispatch template exceeds 2048 bytes")
    if not isinstance(capsule["transition_count"], int) or not isinstance(capsule["dispatch_count"], int) or capsule["transition_count"] > 1 or capsule["dispatch_count"] > 1 or capsule["transition_count"] < 0 or capsule["dispatch_count"] < 0:
        raise Blocked("BLOCKED_TURN_BUDGET", "a turn permits at most one transition and one dispatch")
    if capsule["status"] in ROUTINE_STATUSES and capsule["next"] == "Planner":
        raise Blocked("BLOCKED_ROUTINE_PLANNER", "routine transitions cannot launch Planner")
    validate_repo(repo)
    refs = references(capsule)
    proven = [git_blob(repo, reference) for reference in refs]
    validate_omissions(capsule, {path for path, _ in proven})
    board_match = REF_PATTERN.fullmatch(str(capsule["board_ref"]))
    assert board_match
    if board_match.group(1) != "docs/task_board.md": raise FullRead("board_ref must name primary docs/task_board.md")
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    if board_match.group(2) != head: raise FullRead("board_ref is not pinned to current primary HEAD")
    board_path = repo / "docs" / "task_board.md"
    worktree_diff = subprocess.run(["git", "-C", str(repo), "diff", "--quiet", "HEAD", "--", "docs/task_board.md"]).returncode
    index_diff = subprocess.run(["git", "-C", str(repo), "diff", "--cached", "--quiet", "HEAD", "--", "docs/task_board.md"]).returncode
    if not board_path.is_file() or worktree_diff or index_diff:
        raise FullRead("working primary board differs from its referenced Git blob")
    return refs, template_bytes


def dispatch(args: argparse.Namespace, resolve: bool) -> dict[str, Any]:
    capsule, source_bytes = load_json(args.input)
    refs, template_bytes = validate_capsule(capsule, source_bytes, Path(args.repo_root).resolve())
    if resolve:
        read_set = {"task_id": capsule["task_id"], "role": capsule["next"], "references": refs}
        size = len(json.dumps(read_set, sort_keys=True, separators=(",", ":")).encode())
        if size > 4096: raise FullRead("minimal read capsule exceeds 4096 bytes")
        return {"decision": "ALLOW_MINIMAL_READ_SET", "reason_codes": [], "zero_write": True, "references": refs, "read_set_bytes": size}
    return {"decision": "ALLOW_DISPATCH_CAPSULE", "reason_codes": [], "zero_write": True, "capsule_bytes": source_bytes, "dispatch_template_bytes": template_bytes, "transition_count": capsule["transition_count"], "dispatch_count": capsule["dispatch_count"]}


def callback(value: str) -> dict[str, Any]:
    raw = load_text(value)
    size = len(raw.encode("utf-8"))
    if size > 1024: raise Blocked("BLOCKED_CALLBACK_BUDGET", "callback exceeds 1024 bytes")
    lines = raw.splitlines()
    if len(lines) != 7: raise Blocked("BLOCKED_CALLBACK_SHAPE", "callback must contain exactly seven lines")
    values: dict[str, str] = {}
    for expected, line in zip(CALLBACK_FIELDS, lines, strict=True):
        prefix = expected + ":"
        if not line.startswith(prefix) or not line[len(prefix):].strip():
            raise Blocked("BLOCKED_CALLBACK_SHAPE", "callback fields must be ordered and non-empty")
        values[expected] = line[len(prefix):].strip()
    if not re.fullmatch(r"[0-9a-f]{40}", values["COMMIT"]):
        raise Blocked("BLOCKED_CALLBACK_COMMIT", "COMMIT must be a full SHA")
    return {"decision": "ALLOW_CALLBACK", "reason_codes": [], "zero_write": True, "callback_bytes": size, "fields": values}


def timestamp(value: str) -> datetime:
    try: return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc: raise Blocked("BLOCKED_CADENCE_TIMESTAMP", "event timestamp is invalid") from exc


def cadence(value: str) -> dict[str, Any]:
    raw = load_text(value)
    try: events = [json.loads(line) for line in raw.splitlines() if line.strip()]
    except json.JSONDecodeError as exc: raise Blocked("BLOCKED_CADENCE_SHAPE", str(exc)) from exc
    if not events: raise Blocked("BLOCKED_CADENCE_SHAPE", "events are empty")
    allowed = {"role_start", "role_end", "blocker", "direction", "heartbeat", "transition", "dispatch"}
    if any(not isinstance(item, dict) or item.get("kind") not in allowed or "timestamp" not in item for item in events):
        raise Blocked("BLOCKED_CADENCE_SHAPE", "event kind/timestamp is invalid")
    transition_count = sum(item["kind"] == "transition" for item in events)
    dispatch_count = sum(item["kind"] == "dispatch" for item in events)
    if transition_count > 1 or dispatch_count > 1:
        raise Blocked("BLOCKED_TURN_BUDGET", "a turn permits at most one transition and one dispatch")
    heartbeats = [item for item in events if item["kind"] == "heartbeat"]
    for prior, current in zip(heartbeats, heartbeats[1:]):
        if (timestamp(current["timestamp"]) - timestamp(prior["timestamp"])).total_seconds() < 60:
            raise Blocked("BLOCKED_CADENCE_HEARTBEAT", "heartbeats must be at least 60 seconds apart")
        if prior.get("state") == current.get("state"):
            raise Blocked("BLOCKED_UNCHANGED_WAIT", "unchanged waits must be suppressed")
    role_end = next((item for item in events if item["kind"] == "role_end"), None)
    dispatched = next((item for item in events if item["kind"] == "dispatch"), None)
    latency = None
    if role_end and dispatched:
        latency = int((timestamp(dispatched["timestamp"]) - timestamp(role_end["timestamp"])).total_seconds())
        if latency < 0 or latency > 90:
            raise Blocked("BLOCKED_PILOT_LATENCY", "callback-to-dispatch exceeds 90 seconds")
    return {"decision": "ALLOW_CADENCE", "reason_codes": [], "zero_write": True, "transition_count": transition_count, "dispatch_count": dispatch_count, "callback_to_dispatch_seconds": latency}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(); sub = root.add_subparsers(dest="command", required=True)
    for name in ("validate-dispatch", "resolve-read-set"):
        command = sub.add_parser(name); command.add_argument("--input", required=True); command.add_argument("--repo-root", required=True); command.add_argument("--json", action="store_true")
    callback_parser = sub.add_parser("validate-callback"); callback_parser.add_argument("--input", required=True); callback_parser.add_argument("--json", action="store_true")
    cadence_parser = sub.add_parser("validate-cadence"); cadence_parser.add_argument("--events", required=True); cadence_parser.add_argument("--json", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "validate-dispatch": payload = dispatch(args, False)
        elif args.command == "resolve-read-set": payload = dispatch(args, True)
        elif args.command == "validate-callback": payload = callback(args.input)
        else: payload = cadence(args.events)
        code = 0
    except FullRead as exc:
        payload = {"decision": "FULL_READ_REQUIRED", "reason_codes": ["FULL_READ_REQUIRED"], "zero_write": True, "detail": exc.detail}; code = 0
    except Blocked as exc:
        payload = {"decision": "BLOCKED", "reason_codes": [exc.code], "zero_write": True, "detail": exc.detail}; code = 2
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


if __name__ == "__main__": sys.exit(main())
