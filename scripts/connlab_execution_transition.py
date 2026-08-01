"""Fail-closed, deterministic execution-role transitions for ConnLab's primary board."""

from __future__ import annotations

import argparse
import copy
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"
SUMMARY_PREFIX = "> Current Active Task:"
EVENTS = {
    "DEVELOPER_READY": ("implementation_running", "Developer", "ready_for_review", "gate_running", "Reviewer"),
    "REVIEWER_BLOCKED": ("gate_running", "Reviewer", "reviewer_blocked", "implementation_running", "Developer"),
    "REVIEWER_PASS": ("gate_running", "Reviewer", "reviewer_pass", "gate_running", None),
    "QA_PASS": ("gate_running", "QA", "qa_pass", "gate_running", "Integrator"),
}


class Blocked(Exception):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class Board:
    path: Path
    raw: bytes
    text: str
    control: dict[str, Any]
    payload_digest: str
    payload_span: tuple[int, int]
    newline: str


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(repo: Path, *args: str, binary: bool = False) -> bytes | str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args], check=False, capture_output=True,
        text=not binary,
    )
    if completed.returncode:
        message = completed.stderr if not binary else completed.stderr.decode(errors="replace")
        raise Blocked("BLOCKED_GIT_FACTS_UNAVAILABLE", str(message).strip())
    return completed.stdout


def exact_head(repo: Path) -> str:
    return str(git(repo, "rev-parse", "HEAD")).strip()


def ensure_primary(repo: Path) -> None:
    top = Path(str(git(repo, "rev-parse", "--show-toplevel")).strip()).resolve()
    if top != repo or str(git(repo, "branch", "--show-current")).strip() != "master":
        raise Blocked("BLOCKED_PRIMARY_ROOT_UNVERIFIED", "repo-root must be the main master worktree")


def load_board(repo: Path) -> Board:
    path = repo / "docs" / "task_board.md"
    if not path.is_file():
        raise Blocked("BLOCKED_BOARD_MISSING", "docs/task_board.md is missing")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Blocked("BLOCKED_BOARD_ENCODING", str(exc)) from exc
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise Blocked("BLOCKED_MARKERS_INVALID", "execution-control markers must be unique")
    middle_start = text.index(BEGIN) + len(BEGIN)
    middle_end = text.index(END)
    match = re.fullmatch(r"\s*```json\s*(.*?)\s*```\s*", text[middle_start:middle_end], re.S)
    if not match:
        raise Blocked("BLOCKED_JSON_INVALID", "control block must contain one fenced JSON object")
    payload = match.group(1)
    payload_start = middle_start + match.start(1)
    payload_end = middle_start + match.end(1)
    try:
        control = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise Blocked("BLOCKED_JSON_INVALID", str(exc)) from exc
    board = Board(path, raw, text, control, sha256(payload.encode()), (payload_start, payload_end), "\r\n" if b"\r\n" in raw else "\n")
    validate_control(board)
    return board


def required(record: Any, fields: tuple[str, ...], code: str) -> None:
    if not isinstance(record, dict):
        raise Blocked(code, "record must be an object")
    for field in fields:
        if field not in record or record[field] is None or record[field] == "":
            raise Blocked(code, f"missing required field: {field}")


def validate_control(board: Board) -> None:
    c = board.control
    for field in ("schema", "version", "wip_limit", "execution_token_owner", "execution_state", "active", "queue", "paused", "quick_fix", "residuals", "parallel_exception"):
        if field not in c:
            raise Blocked("BLOCKED_SCHEMA_INVALID", f"missing required field: {field}")
    if c["schema"] != "connlab.execution-control" or c["version"] != 1 or c["wip_limit"] != 1:
        raise Blocked("BLOCKED_SCHEMA_UNSUPPORTED", "execution schema/version/WIP is unsupported")
    state = c["execution_state"]
    if state not in {"idle", "queued", "implementation_running", "gate_running", "paused_preempted", "quick_fix_running", "reconciling", "complete", "cancelled"}:
        raise Blocked("BLOCKED_STATE_INVALID", "execution state is unknown")
    active = c.get("active")
    if state in {"implementation_running", "gate_running", "reconciling"}:
        required(active, ("task_id", "lane", "role", "branch", "worktree", "base_sha", "head_sha", "locked_paths", "required_gates", "evidence"), "BLOCKED_ACTIVE_RECORD_INCOMPLETE")
        if c["execution_token_owner"] != active["task_id"]:
            raise Blocked("BLOCKED_ACTIVE_OWNER_MISMATCH", "token owner differs from active task")
        if not isinstance(active["locked_paths"], list) or not active["locked_paths"]:
            raise Blocked("BLOCKED_LOCKS_INVALID", "active locked_paths must be non-empty")
        if not isinstance(active["required_gates"], list) or "Reviewer" not in active["required_gates"] or "Integrator" not in active["required_gates"]:
            raise Blocked("BLOCKED_GATE_METADATA", "required_gates are incomplete")
        if state == "implementation_running" and active["role"] != "Developer":
            raise Blocked("BLOCKED_ACTIVE_ROLE_MISMATCH", "implementation requires Developer")
        if state == "gate_running" and active["role"] not in {"Reviewer", "QA", "Integrator"}:
            raise Blocked("BLOCKED_ACTIVE_ROLE_MISMATCH", "gate role is invalid")
    elif state in {"idle", "paused_preempted", "complete", "cancelled"} and c["execution_token_owner"] is not None:
        raise Blocked("BLOCKED_OWNER_STATE_CONTRADICTION", "ownerless state retains a token")
    queue = c.get("queue")
    if not isinstance(queue, list) or not isinstance(c.get("residuals"), list):
        raise Blocked("BLOCKED_SCHEMA_INVALID", "queue/residuals must be arrays")
    for residual in c["residuals"]:
        required(residual, ("task_id", "residual_owner", "disposition", "evidence"), "BLOCKED_RESIDUAL_INCOMPLETE")
    tasks: set[str] = set()
    positions: set[int] = set()
    qfields = ("task_id", "lane", "enqueue_sequence", "enqueued_at", "dependencies", "locked_paths", "requested_priority", "queue_position", "evidence")
    for item in queue:
        required(item, qfields, "BLOCKED_QUEUE_INVALID")
        if item["task_id"] in tasks or item["queue_position"] in positions:
            raise Blocked("BLOCKED_QUEUE_DUPLICATE", "queue task identities and positions must be unique")
        tasks.add(item["task_id"]); positions.add(item["queue_position"])
    if positions and positions != set(range(1, len(positions) + 1)):
        raise Blocked("BLOCKED_QUEUE_FIFO_INVALID", "queue positions must be contiguous")
    if state == "queued" and (not c["execution_token_owner"] or c["execution_token_owner"] not in tasks):
        raise Blocked("BLOCKED_QUEUE_OWNER", "queued token owner must have one queue record")
    paused = c.get("paused")
    if paused is not None:
        required(paused, ("task_id", "lane", "branch", "worktree", "previous_owner", "paused_reason", "preempted_by", "checkpoint_sha", "pause_master_sha", "resume_condition", "unfinished_items", "locked_paths", "evidence"), "BLOCKED_PAUSE_INCOMPLETE")
    quick_fix = c.get("quick_fix")
    if quick_fix is not None:
        required(quick_fix, ("task_id", "lane", "role", "risk_gate", "goal", "why_safe", "may_touch", "must_not_touch", "locked_paths", "targeted_validation", "required_gates", "branch", "worktree", "base_sha", "head_sha", "evidence"), "BLOCKED_QUICK_FIX_INCOMPLETE")
    if state == "quick_fix_running" and (not isinstance(quick_fix, dict) or c["execution_token_owner"] != quick_fix["task_id"] or quick_fix["role"] != "Quick Fixer"):
        raise Blocked("BLOCKED_QUICK_FIX_OWNER", "Quick Fix owner/role differs")
    if state in {"paused_preempted", "reconciling"} and not isinstance(paused, dict):
        raise Blocked("BLOCKED_PAUSE_INCOMPLETE", "paused/reconciling state requires pause facts")
    if state == "reconciling" and not isinstance(quick_fix, dict):
        raise Blocked("BLOCKED_QUICK_FIX_INCOMPLETE", "reconciling state requires accepted Quick Fix facts")
    if state in {"complete", "cancelled"} and not c["residuals"]:
        raise Blocked("BLOCKED_TERMINAL_RESIDUAL_REQUIRED", "terminal state requires residual ownership")
    parallel = c.get("parallel_exception")
    if parallel is not None:
        required(parallel, ("primary_task_id", "secondary_execution_token_owner", "secondary_task_id", "secondary_lane", "secondary_role", "secondary_branch", "secondary_worktree", "secondary_head_sha", "user_approval_evidence", "scope_proof", "independence_proof", "locked_paths", "end_condition"), "BLOCKED_PARALLEL_INCOMPLETE")
        if not isinstance(active, dict) or parallel["primary_task_id"] != active["task_id"] or parallel["secondary_task_id"] != parallel["secondary_execution_token_owner"]:
            raise Blocked("BLOCKED_PARALLEL_OWNER_MISMATCH", "parallel owner facts differ")
    lines = [line for line in board.text.splitlines() if line.startswith(SUMMARY_PREFIX)]
    if len(lines) != 1:
        raise Blocked("BLOCKED_SUMMARY_INVALID", "active summary must be unique")
    summary = lines[0]
    # Pre-migration summaries did not always repeat the lane slug; task/state/role are the
    # compatibility projection. Every helper-written summary adds the lane deterministically.
    if isinstance(active, dict):
        facts = (active["task_id"], f"{state}/{active['role']}")
    elif state == "quick_fix_running" and isinstance(quick_fix, dict):
        facts = (quick_fix["task_id"], f"{state}/{quick_fix['role']}")
    else:
        facts = ("None", str(state))
    for fact in facts:
        if str(fact) not in summary:
            raise Blocked("BLOCKED_SUMMARY_MISMATCH", f"active summary omits {fact}")


def clean(repo: Path, code: str) -> None:
    if str(git(repo, "status", "--porcelain=v1", "--untracked-files=all")).strip():
        raise Blocked(code, f"worktree is dirty: {repo}")


def parse_evidence_ref(value: str) -> tuple[str, str, str]:
    match = re.fullmatch(r"([^@#]+)@([0-9a-f]{40})#([0-9a-f]{64})", value)
    if not match or Path(match.group(1)).is_absolute() or ".." in Path(match.group(1)).parts:
        raise Blocked("BLOCKED_EVIDENCE_REF_INVALID", "evidence ref must be path@commit#sha256")
    return match.group(1), match.group(2), match.group(3)


def allowed_path(path: str, locks: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    return any(fnmatch.fnmatchcase(normalized, lock.replace("\\", "/")) or normalized.startswith(lock.rstrip("/") + "/") for lock in locks)


def next_role(event: str, active: dict[str, Any]) -> str:
    configured = EVENTS[event][4]
    if configured:
        return configured
    return "QA" if "QA" in active["required_gates"] else "Integrator"


def transition_id(args: argparse.Namespace, before: str, target_role: str) -> str:
    facts = {"event": args.event, "task": args.task_id, "lane": args.lane, "primary": args.expected_primary_head, "lane_head": args.expected_lane_head, "evidence": args.evidence_ref, "status": args.evidence_status, "before": before, "next": target_role}
    return sha256(json.dumps(facts, sort_keys=True, separators=(",", ":")).encode())


def already_applied(board: Board, args: argparse.Namespace) -> dict[str, Any] | None:
    last = board.control.get("last_transition")
    if not isinstance(last, dict) or last.get("event") != args.event:
        return None
    if last.get("evidence_ref") != args.evidence_ref or last.get("lane_head") != args.expected_lane_head:
        raise Blocked("BLOCKED_DUPLICATE_CONFLICT", "the same event has divergent durable facts")
    return result("ALREADY_APPLIED", [], board.payload_digest, board.payload_digest, str(last.get("transition_id")), board.control["active"]["role"], [])


def validate_plan(board: Board, repo: Path, args: argparse.Namespace) -> tuple[str, str]:
    if args.event not in EVENTS:
        raise Blocked("BLOCKED_EVENT_UNKNOWN", "unsupported transition event")
    prior = already_applied(board, args)
    if prior:
        raise Already(prior)
    current_state, current_role, expected_status, _, _ = EVENTS[args.event]
    active = board.control["active"]
    if args.evidence_status != expected_status:
        raise Blocked("BLOCKED_EVENT_STATUS_MISMATCH", "event and evidence status differ")
    if board.control["execution_state"] != current_state or active["role"] != current_role:
        raise Blocked("BLOCKED_ILLEGAL_TRANSITION", "current state/role cannot consume this event")
    if board.control["execution_token_owner"] != args.task_id or active["task_id"] != args.task_id or active["lane"] != args.lane:
        raise Blocked("BLOCKED_AUTHORITY_MISMATCH", "task/lane/token facts differ")
    task_path = repo / "tasks" / f"{args.task_id}.md"
    if not task_path.is_file():
        raise Blocked("BLOCKED_TASK_METADATA", "the exact task file is missing")
    task_text = task_path.read_text(encoding="utf-8")
    if "Status: `approved`" not in task_text or any(str(gate) not in task_text for gate in active["required_gates"]):
        raise Blocked("BLOCKED_TASK_METADATA", "approved task gate metadata differs")
    if "QA" not in active["required_gates"] and "QA is not required" not in task_text:
        raise Blocked("BLOCKED_TASK_METADATA", "QA omission lacks immutable approved-task proof")
    if exact_head(repo) != args.expected_primary_head:
        raise Blocked("BLOCKED_PRIMARY_HEAD_DRIFT", "primary HEAD differs")
    if active["head_sha"] != args.expected_lane_head:
        raise Blocked("BLOCKED_ACTIVE_HEAD_DRIFT", "board lane HEAD differs")
    lane = Path(active["worktree"]).resolve()
    if not lane.is_dir() or exact_head(lane) != args.expected_lane_head or str(git(lane, "branch", "--show-current")).strip() != active["branch"]:
        raise Blocked("BLOCKED_LANE_GIT_FACTS", "lane branch/worktree/HEAD differs")
    clean(repo, "BLOCKED_PRIMARY_DIRTY"); clean(lane, "BLOCKED_LANE_DIRTY")
    if subprocess.run(["git", "-C", str(lane), "merge-base", "--is-ancestor", active["base_sha"], args.expected_lane_head]).returncode:
        raise Blocked("BLOCKED_ANCESTRY", "lane HEAD does not descend from base")
    changed = str(git(lane, "diff", "--name-only", f"{active['base_sha']}..{args.expected_lane_head}")).splitlines()
    if any(not allowed_path(path, active["locked_paths"]) for path in changed):
        raise Blocked("BLOCKED_SCOPE_DRIFT", "lane contains a path outside locked scope")
    path, commit, expected_hash = parse_evidence_ref(args.evidence_ref)
    if commit != args.expected_lane_head:
        raise Blocked("BLOCKED_EVIDENCE_COMMIT_MISMATCH", "evidence commit must equal lane HEAD")
    shown = subprocess.run(["git", "-C", str(lane), "show", f"{commit}:{path}"], check=False, capture_output=True)
    if shown.returncode:
        raise Blocked("BLOCKED_EVIDENCE_MISSING", "evidence Git blob is unavailable")
    if sha256(shown.stdout) != expected_hash:
        raise Blocked("BLOCKED_EVIDENCE_HASH_MISMATCH", "evidence SHA-256 differs")
    evidence_text = shown.stdout.decode("utf-8")
    expected_evidence_role = current_role
    if f"STATUS: {expected_status}" not in evidence_text or f"ROLE: {expected_evidence_role}" not in evidence_text or f"TASK_ID: {args.task_id}" not in evidence_text:
        raise Blocked("BLOCKED_EVIDENCE_CONTENT", "evidence callback facts differ")
    target = next_role(args.event, active)
    return target, transition_id(args, board.payload_digest, target)


class Already(Exception):
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload


def render(board: Board, control: dict[str, Any]) -> bytes:
    nl = board.newline
    payload = json.dumps(control, indent=2, ensure_ascii=False).replace("\n", nl)
    text = board.text[: board.payload_span[0]] + payload + board.text[board.payload_span[1] :]
    active = control["active"]
    summary = f"> Current Active Task: `{active['task_id']}` is the sole WIP=`1` token owner in `{control['execution_state']}/{active['role']}` on lane `{active['lane']}`."
    text, count = re.subn(r"(?m)^> Current Active Task:.*$", summary, text)
    if count != 1:
        raise Blocked("BLOCKED_SUMMARY_INVALID", "active summary replacement was ambiguous")
    return text.encode("utf-8")


def result(decision: str, reasons: list[str], before: str | None, after: str | None, tid: str | None, role: str | None, paths: list[str], detail: str | None = None) -> dict[str, Any]:
    return {"decision": decision, "reason_codes": reasons, "before_digest": before, "after_digest": after, "transition_id": tid, "next_role": role, "changed_paths": paths, "zero_write": not paths, "detail": detail}


def execute(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo_root).resolve()
    ensure_primary(repo)
    board = load_board(repo)
    if args.command == "inspect":
        active = board.control.get("active")
        role = active.get("role") if isinstance(active, dict) else None
        return result("ALLOW_INSPECT", [], board.payload_digest, board.payload_digest, None, role, [])
    try:
        target, tid = validate_plan(board, repo, args)
    except Already as prior:
        return prior.payload
    if args.command == "plan":
        return result("ALLOW_TRANSITION", [], board.payload_digest, None, tid, target, [])
    if args.expected_snapshot_digest != board.payload_digest:
        raise Blocked("BLOCKED_SNAPSHOT_STALE", "expected snapshot digest differs")
    control = copy.deepcopy(board.control)
    target_state = EVENTS[args.event][3]
    control["execution_state"] = target_state
    control["active"]["role"] = target
    control["active"]["head_sha"] = args.expected_lane_head
    control["active"]["evidence"] = args.evidence_ref
    control["evidence"] = args.evidence_ref
    entry = {"transition_id": tid, "event": args.event, "evidence_ref": args.evidence_ref, "evidence_status": args.evidence_status, "lane_head": args.expected_lane_head, "from_state": board.control["execution_state"], "from_role": board.control["active"]["role"], "to_state": target_state, "to_role": target}
    control["last_transition"] = entry
    control.setdefault("transition_history", []).append(entry)
    rendered = render(board, control)
    after_board = load_rendered(rendered)
    validate_control(after_board)
    if os.environ.get("CONNLAB_TRANSITION_FAIL_BEFORE_REPLACE"):
        raise Blocked("BLOCKED_WRITE_FAILED", "injected pre-replace failure")
    fd, temporary = tempfile.mkstemp(prefix=".connlab-transition-", dir=board.path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(rendered); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, board.path)
    except Exception as exc:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise Blocked("BLOCKED_WRITE_FAILED", str(exc)) from exc
    return result("APPLIED", [], board.payload_digest, after_board.payload_digest, tid, target, ["docs/task_board.md"])


def load_rendered(raw: bytes) -> Board:
    text = raw.decode("utf-8")
    middle = text.split(BEGIN, 1)[1].split(END, 1)[0]
    match = re.search(r"```json\s*(.*?)\s*```", middle, re.S)
    assert match
    payload = match.group(1)
    return Board(Path(), raw, text, json.loads(payload), sha256(payload.encode()), (0, 0), "\r\n" if b"\r\n" in raw else "\n")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect"); inspect.add_argument("--repo-root", required=True); inspect.add_argument("--json", action="store_true")
    for name in ("plan", "apply"):
        command = sub.add_parser(name)
        for option in ("event", "task-id", "lane", "expected-primary-head", "expected-lane-head", "evidence-ref", "evidence-status"):
            command.add_argument(f"--{option}", required=True)
        command.add_argument("--repo-root", required=True)
        if name == "apply": command.add_argument("--expected-snapshot-digest", required=True)
        command.add_argument("--json", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        payload = execute(args); code = 0
    except Blocked as exc:
        payload = result("BLOCKED", [exc.code], None, None, None, None, [], exc.detail); code = 2
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


if __name__ == "__main__":
    sys.exit(main())
