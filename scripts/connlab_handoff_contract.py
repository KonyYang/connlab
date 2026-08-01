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
    "execution_token_owner", "execution_state", "lane", "branch", "worktree",
    "base_sha", "head_sha", "scope_contract_ref", "may_touch_digest",
    "locked_paths_digest", "required_gates", "gate_snapshot_digest", "evidence_status",
    "next_action", "stop_conditions", "changed_paths", "transition_count",
    "dispatch_count", "dispatch_template",
)
REF_PATTERN = re.compile(r"([^@#]+)@([0-9a-f]{40})#([0-9a-f]{64})")
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"
STOP_CONDITIONS = ["scope_expansion", "authority_drift", "unexplained_test_failure", "destructive_action_required"]
ROUTINE_STATUSES = {
    "developer_dispatch_ready", "ready_for_review", "reviewer_blocked",
    "reviewer_pass", "qa_pass", "bounded_reviewer_fix_dispatch_ready",
    "reviewer_dispatch_ready", "qa_dispatch_ready", "integrator_dispatch_ready",
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


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def git_blob(repo: Path, reference: str) -> tuple[str, str, bytes, str]:
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
    blob = subprocess.run(["git", "-C", str(repo), "rev-parse", f"{commit}:{path}"], check=False, capture_output=True, text=True)
    if blob.returncode: raise FullRead(f"blob identity cannot be proven: {path}")
    return path, commit, done.stdout, blob.stdout.strip()


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


def parse_board(raw: bytes) -> dict[str, Any]:
    try: text = raw.decode("utf-8")
    except UnicodeDecodeError as exc: raise FullRead("board encoding is invalid") from exc
    if text.count(BEGIN) != 1 or text.count(END) != 1: raise FullRead("board markers are ambiguous")
    middle = text.split(BEGIN, 1)[1].split(END, 1)[0]
    match = re.fullmatch(r"\s*```json\s*(.*?)\s*```\s*", middle, re.S)
    if not match: raise FullRead("board control block is invalid")
    try: control = json.loads(match.group(1))
    except json.JSONDecodeError as exc: raise FullRead("board JSON is invalid") from exc
    if control.get("schema") != "connlab.execution-control" or control.get("version") != 1 or control.get("wip_limit") != 1: raise FullRead("board schema is unsupported")
    return control


def machine_record(raw: bytes) -> tuple[str, str, str]:
    try: text = raw.decode("utf-8")
    except UnicodeDecodeError as exc: raise FullRead("evidence encoding is invalid") from exc
    records = re.findall(r"(?m)^TASK_ID:\s*([^\r\n]+)\r?\nROLE:\s*([^\r\n]+)\r?\nSTATUS:\s*([^\r\n]+)$", text)
    if len(records) != 1: raise FullRead("evidence machine record is ambiguous")
    return tuple(value.strip() for value in records[0])


def may_touch(task_raw: bytes) -> list[str]:
    text = task_raw.decode("utf-8")
    match = re.search(r"(?ms)^## Exact May Touch\s*$\s*(.*?)(?=^## Must Not Touch\s*$)", text)
    paths = re.findall(r"(?m)^\s*\d+\.\s+`([^`]+)`", match.group(1)) if match else []
    if not paths or len(paths) != len(set(paths)): raise FullRead("task scope is unavailable or ambiguous")
    return paths


def lane_facts(capsule: dict[str, Any]) -> None:
    lane = Path(capsule["worktree"]).resolve()
    commands = (("rev-parse", "--show-toplevel"), ("branch", "--show-current"), ("rev-parse", "HEAD"))
    values = []
    for command in commands:
        done = subprocess.run(["git", "-C", str(lane), *command], check=False, capture_output=True, text=True)
        if done.returncode: raise FullRead("lane Git facts are unavailable")
        values.append(done.stdout.strip())
    if Path(values[0]).resolve() != lane or values[1] != capsule["branch"] or values[2] != capsule["head_sha"]: raise FullRead("lane branch/worktree/HEAD drifted")
    if subprocess.run(["git", "-C", str(lane), "merge-base", "--is-ancestor", capsule["base_sha"], capsule["head_sha"]]).returncode: raise FullRead("lane ancestry differs")
    if subprocess.run(["git", "-C", str(lane), "status", "--porcelain=v1", "--untracked-files=all"], capture_output=True, text=True).stdout.strip(): raise FullRead("lane worktree/index is dirty")


def bind_authority(capsule: dict[str, Any], proven: dict[str, tuple[str, str, bytes, str]], repo: Path) -> None:
    board_path, board_commit, board_raw, _ = proven["board_ref"]
    if board_path != "docs/task_board.md": raise FullRead("board_ref must name primary docs/task_board.md")
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    if board_commit != head: raise FullRead("board_ref is not current primary authority")
    control = parse_board(board_raw); active = control.get("active")
    if not isinstance(active, dict): raise FullRead("active execution record is unavailable")
    exact = {"task_id": active.get("task_id"), "execution_token_owner": control.get("execution_token_owner"), "execution_state": control.get("execution_state"),
             "lane": active.get("lane"), "branch": active.get("branch"), "worktree": active.get("worktree"), "base_sha": active.get("base_sha"), "head_sha": active.get("head_sha")}
    if any(capsule[key] != value for key, value in exact.items()) or capsule["next"] != active.get("role") or capsule["role"] != "Orchestrator": raise FullRead("capsule task/token/state/role/lane facts contradict the board")
    task_path, task_commit, task_raw, _ = proven["task_ref"]; plan_path, plan_commit, plan_raw, _ = proven["plan_ref"]
    expected_task = f"tasks/{capsule['task_id']}.md"; expected_plan = "docs/" + capsule["task_id"].lower() + "_plan.md"
    if task_path != expected_task or plan_path != expected_plan or task_commit != plan_commit or capsule["scope_contract_ref"] != capsule["task_ref"]: raise FullRead("task/plan/scope refs are cross-bound or stale")
    if subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", task_commit, board_commit]).returncode: raise FullRead("task/plan commit is unrelated to primary authority")
    if b"Status: `approved`" not in task_raw or b"Status: `approved`" not in plan_raw or capsule["task_id"].encode() not in plan_raw: raise FullRead("task/plan approval facts differ")
    locks = active.get("locked_paths"); gates = active.get("required_gates"); scope = may_touch(task_raw)
    if (not isinstance(locks, list) or not isinstance(gates, list) or capsule["required_gates"] != gates or capsule["scope_contract_ref"] != active.get("scope_contract_ref") or
            capsule["may_touch_digest"] != active.get("may_touch_digest") or capsule["may_touch_digest"] != canonical_digest(scope) or
            capsule["locked_paths_digest"] != active.get("locked_paths_digest") or capsule["locked_paths_digest"] != canonical_digest(locks) or locks != scope or
            capsule["gate_snapshot_digest"] != canonical_digest(gates)):
        raise FullRead("scope/lock/gate snapshot drifted")
    evidence = proven["evidence_ref"]; evidence_task, evidence_role, evidence_status = machine_record(evidence[2])
    if subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", evidence[1], board_commit]).returncode and subprocess.run(["git", "-C", capsule["worktree"], "merge-base", "--is-ancestor", evidence[1], capsule["head_sha"]]).returncode:
        raise FullRead("evidence commit is unrelated to primary and lane authority")
    route = {("Developer", "developer_dispatch_ready"): ("developer_dispatch_ready", "implement_approved_scope", "Planner"),
             ("Developer", "reviewer_blocked"): ("bounded_reviewer_fix_dispatch_ready", "bounded_reviewer_fix", "Reviewer"),
             ("Reviewer", "ready_for_review"): ("reviewer_dispatch_ready", "review", "Developer"),
             ("QA", "reviewer_pass"): ("qa_dispatch_ready", "qa", "Reviewer"),
             ("Integrator", "qa_pass"): ("integrator_dispatch_ready", "integrate", "QA"),
             ("Integrator", "reviewer_pass"): ("integrator_dispatch_ready", "integrate", "Reviewer")}.get((active.get("role"), evidence_status))
    if not route or evidence_task != capsule["task_id"] or evidence_role != route[2] or capsule["evidence_status"] != evidence_status or capsule["status"] != route[0] or capsule["next_action"] != route[1] or capsule["evidence_ref"] != active.get("evidence"):
        raise FullRead("evidence status/role/next action contradicts durable authority")
    if capsule["stop_conditions"] != STOP_CONDITIONS: raise FullRead("stop conditions are incomplete")
    lane_facts(capsule)


def validate_capsule(capsule: dict[str, Any], source_bytes: int, repo: Path) -> tuple[list[str], int]:
    missing = [field for field in REQUIRED_CAPSULE if field not in capsule or capsule[field] in (None, "")]
    if missing: raise FullRead("capsule fields are missing: " + ",".join(missing))
    if capsule["schema"] != "connlab.handoff.v1": raise FullRead("unsupported handoff schema")
    text_fields = ("task_id", "role", "status", "next", "blocker", "execution_token_owner", "execution_state", "lane", "branch", "worktree", "base_sha", "head_sha", "scope_contract_ref", "may_touch_digest", "locked_paths_digest", "gate_snapshot_digest", "evidence_status", "next_action", "dispatch_template")
    if any(not isinstance(capsule[field], str) or not capsule[field] for field in text_fields): raise FullRead("capsule scalar types are invalid")
    for field, size in (("base_sha", 40), ("head_sha", 40), ("may_touch_digest", 64), ("locked_paths_digest", 64), ("gate_snapshot_digest", 64)):
        if not re.fullmatch(f"[0-9a-f]{{{size}}}", capsule[field]): raise FullRead(f"{field} is invalid")
    if not isinstance(capsule["required_gates"], list) or not capsule["required_gates"] or not all(isinstance(item, str) and item for item in capsule["required_gates"]): raise FullRead("required_gates are invalid")
    if not isinstance(capsule["stop_conditions"], list) or not all(isinstance(item, str) for item in capsule["stop_conditions"]): raise FullRead("stop_conditions are invalid")
    if source_bytes > 4096: raise Blocked("BLOCKED_CAPSULE_BUDGET", "complete dispatch capsule exceeds 4096 bytes")
    template_bytes = len(str(capsule["dispatch_template"]).encode("utf-8"))
    if template_bytes > 2048: raise Blocked("BLOCKED_TEMPLATE_BUDGET", "dispatch template exceeds 2048 bytes")
    if type(capsule["transition_count"]) is not int or type(capsule["dispatch_count"]) is not int or capsule["transition_count"] > 1 or capsule["dispatch_count"] > 1 or capsule["transition_count"] < 0 or capsule["dispatch_count"] < 0:
        raise Blocked("BLOCKED_TURN_BUDGET", "a turn permits at most one transition and one dispatch")
    if capsule["status"] in ROUTINE_STATUSES and capsule["next"] == "Planner":
        raise Blocked("BLOCKED_ROUTINE_PLANNER", "routine transitions cannot launch Planner")
    validate_repo(repo)
    refs = references(capsule)
    proven_list = [git_blob(repo, reference) for reference in refs]
    validate_omissions(capsule, {item[0] for item in proven_list})
    proven = {field: git_blob(repo, str(capsule[field])) for field in ("board_ref", "task_ref", "plan_ref", "evidence_ref")}
    board_path = repo / "docs" / "task_board.md"
    worktree_diff = subprocess.run(["git", "-C", str(repo), "diff", "--quiet", "HEAD", "--", "docs/task_board.md"]).returncode
    index_diff = subprocess.run(["git", "-C", str(repo), "diff", "--cached", "--quiet", "HEAD", "--", "docs/task_board.md"]).returncode
    if not board_path.is_file() or worktree_diff or index_diff:
        raise FullRead("working primary board differs from its referenced Git blob")
    if subprocess.run(["git", "-C", str(repo), "status", "--porcelain=v1", "--untracked-files=all"], capture_output=True, text=True).stdout.strip():
        raise FullRead("primary worktree/index is dirty")
    bind_authority(capsule, proven, repo)
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
    moments = [timestamp(item["timestamp"]) for item in events]
    try:
        if any(current < prior for prior, current in zip(moments, moments[1:])):
            raise Blocked("BLOCKED_CADENCE_ORDER", "event timestamps are not monotonic")
    except TypeError as exc:
        raise Blocked("BLOCKED_CADENCE_ORDER", "timestamp awareness is mixed") from exc
    transition_count = sum(item["kind"] == "transition" for item in events)
    dispatch_count = sum(item["kind"] == "dispatch" for item in events)
    if transition_count > 1 or dispatch_count > 1:
        raise Blocked("BLOCKED_TURN_BUDGET", "a turn permits at most one transition and one dispatch")
    if sum(item["kind"] == "role_start" for item in events) > 1 or sum(item["kind"] == "role_end" for item in events) > 1:
        raise Blocked("BLOCKED_CADENCE_ORDER", "role lifecycle events are duplicated")
    for index, current in enumerate(events):
        if current["kind"] != "heartbeat": continue
        if index == 0 or not isinstance(current.get("state"), str) or not current["state"]:
            raise Blocked("BLOCKED_CADENCE_HEARTBEAT", "a heartbeat requires a preceding material event and state")
        prior = events[index - 1]
        if (moments[index] - moments[index - 1]).total_seconds() < 60:
            raise Blocked("BLOCKED_CADENCE_HEARTBEAT", "heartbeats must be at least 60 seconds apart")
        if prior.get("state") == current.get("state"):
            raise Blocked("BLOCKED_UNCHANGED_WAIT", "unchanged waits must be suppressed")
    starts = [index for index, item in enumerate(events) if item["kind"] == "role_start"]
    ends = [index for index, item in enumerate(events) if item["kind"] == "role_end"]
    if starts and ends and starts[0] > ends[0]: raise Blocked("BLOCKED_CADENCE_ORDER", "role_end precedes role_start")
    transition_indexes = [index for index, item in enumerate(events) if item["kind"] == "transition"]
    dispatch_indexes = [index for index, item in enumerate(events) if item["kind"] == "dispatch"]
    if transition_indexes and dispatch_indexes and transition_indexes[0] > dispatch_indexes[0]: raise Blocked("BLOCKED_CADENCE_ORDER", "dispatch precedes transition")
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
