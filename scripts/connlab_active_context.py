"""Bounded active-board maintenance with immutable, byte-verifiable history."""

from __future__ import annotations

import argparse
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
INDEX_PATH = Path("docs/archive/task_board_history/index.v1.jsonl")
INDEX_SCHEMA = "connlab.task-board-history-index"
INDEX_VERSION = 1
ARCHIVE_PATTERN = re.compile(r"docs/archive/task_board_history/generation-(\d{6})-([0-9a-f]{40})\.md")
TERMINAL = re.compile(r"^\s*- `(?:TASK_|RELEASE_|CONNLAB_).+?:.*\b(complete|completed|accepted|cancelled|superseded|closed|frozen|historical)\b", re.I)
ACTIVE_STATUS = re.compile(r"planned|proposed|queued|implementation_running|gate_running|paused_preempted|quick_fix_running|reconciling", re.I)
AUTHORITY_LINE = re.compile(r"\b(current|active|queue|paused|Quick Fix|parallel exception|residual|proposal)\b", re.I)
MAX_LINES = 400
MAX_BYTES = 65_536
MAX_TERMINAL = 24
FIRST_MIGRATION_TASK = "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF"
class Blocked(Exception):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail); self.code = code; self.detail = detail
@dataclass(frozen=True)
class Snapshot:
    raw: bytes
    text: str
    control: dict[str, Any]
    lines: int
    bytes: int
    terminal_records: int
@dataclass(frozen=True)
class MaintenancePlan:
    generation: int
    source_head: str
    source_blob: str
    source: Snapshot
    archive_path: str
    archive_bytes: bytes
    archive_mode: str
    archive_record_count: int
    compact: bytes
    previous_index_hash: str
    plan_digest: str
def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
def context_digest(control: dict[str, Any]) -> str:
    active = control.get("active") or {}; facts = {key: control.get(key) for key in ("execution_token_owner", "queue", "paused", "quick_fix", "residuals", "parallel_exception")}
    facts["active"] = {key: active.get(key) for key in ("task_id", "lane", "branch", "worktree", "base_sha", "locked_paths", "required_gates", "scope_contract_ref", "may_touch_digest", "locked_paths_digest")}
    return digest(json.dumps(facts, sort_keys=True, separators=(",", ":")).encode())
def transition_digest(entry: dict[str, Any], lane: str) -> str:
    facts = {"event": entry["event"], "task": entry["task_id"], "lane": lane, "primary": entry["primary_head"], "lane_head": entry["lane_head"], "evidence": entry["evidence_ref"], "status": entry["evidence_status"], "from_state": entry["from_state"], "from_role": entry["from_role"], "to_state": entry["to_state"], "to_role": entry["to_role"]}
    return digest(json.dumps(facts, sort_keys=True, separators=(",", ":")).encode())
def git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], check=False, capture_output=True, text=True)
    if done.returncode:
        raise Blocked("BLOCKED_GIT_FACTS_UNAVAILABLE", done.stderr.strip())
    return done.stdout.strip()
def ensure_primary(repo: Path) -> None:
    top = Path(git(repo, "rev-parse", "--show-toplevel")).resolve()
    if top != repo or git(repo, "branch", "--show-current") != "master":
        raise Blocked("BLOCKED_PRIMARY_ROOT_UNVERIFIED", "repo-root must be the main master worktree")
def ensure_safe_history_path(repo: Path, path: Path) -> None:
    root = repo / "docs" / "archive" / "task_board_history"
    if path.parent != root or repo not in path.parents or os.path.lexists(path) and (path.is_symlink() or getattr(path, "is_junction", lambda: False)()):
        raise Blocked("BLOCKED_ARCHIVE_PATH", "history target escaped its exact directory")
    current = repo
    for part in path.relative_to(repo).parts[:-1]:
        current = current / part
        if current.exists() and (current.is_symlink() or getattr(current, "is_junction", lambda: False)()):
            raise Blocked("BLOCKED_ARCHIVE_PATH", "history path traverses a link or junction")
def parse_snapshot(raw: bytes) -> Snapshot:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Blocked("BLOCKED_BOARD_ENCODING", str(exc)) from exc
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise Blocked("BLOCKED_MARKERS_INVALID", "execution-control markers must be unique")
    middle = text.split(BEGIN, 1)[1].split(END, 1)[0]
    match = re.fullmatch(r"\s*```json\s*(.*?)\s*```\s*", middle, re.S)
    if not match:
        raise Blocked("BLOCKED_JSON_INVALID", "control block must contain fenced JSON")
    try:
        control = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise Blocked("BLOCKED_JSON_INVALID", str(exc)) from exc
    if control.get("schema") != "connlab.execution-control" or control.get("version") != 1 or control.get("wip_limit") != 1:
        raise Blocked("BLOCKED_SCHEMA_UNSUPPORTED", "unsupported execution-control schema")
    terminal = sum(is_terminal_line(line) for line in text.splitlines())
    return Snapshot(raw, text, control, len(text.splitlines()), len(raw), terminal)
def is_terminal_line(line: str) -> bool:
    return bool(TERMINAL.search(line)) and not bool(ACTIVE_STATUS.search(line))
def load_snapshot(repo: Path) -> Snapshot:
    board = repo / "docs" / "task_board.md"
    if not board.is_file():
        raise Blocked("BLOCKED_BOARD_MISSING", "docs/task_board.md is missing")
    return parse_snapshot(board.read_bytes())
def threshold(snapshot: Snapshot) -> bool:
    return snapshot.lines > MAX_LINES or snapshot.bytes > MAX_BYTES or snapshot.terminal_records > MAX_TERMINAL
def index_records(repo: Path) -> tuple[list[dict[str, Any]], bytes]:
    path = repo / INDEX_PATH
    ensure_safe_history_path(repo, path)
    if not path.exists():
        return [], b""
    raw = path.read_bytes()
    try:
        lines = raw.decode("utf-8").splitlines()
        records = [json.loads(line) for line in lines if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Blocked("BLOCKED_INDEX_CORRUPT", str(exc)) from exc
    prefix = b""
    for number, record in enumerate(records, 1):
        required = {
            "schema", "version", "plan_digest",
            "generation", "source_commit", "source_blob_sha", "source_board_sha256",
            "source_bytes", "source_record_count", "archive_path", "archive_sha256",
            "archive_record_count", "archive_mode", "compact_board_sha256",
            "compact_bytes", "compact_record_count", "previous_index_sha256", "rollback_sha256",
            "moved_record_ids", "retained_authority_record_ids",
        }
        if set(record) != required or record["schema"] != INDEX_SCHEMA or record["version"] != INDEX_VERSION or record["generation"] != number:
            raise Blocked("BLOCKED_INDEX_CORRUPT", "index generation or fields are invalid")
        expected_previous = digest(prefix) if prefix else "0" * 64
        if record["previous_index_sha256"] != expected_previous:
            raise Blocked("BLOCKED_INDEX_CORRUPT", "previous-index hash chain differs")
        match = ARCHIVE_PATTERN.fullmatch(str(record["archive_path"]))
        if not match or int(match.group(1)) != number or match.group(2) != record["source_commit"]:
            raise Blocked("BLOCKED_ARCHIVE_PATH", "archive path escaped or differs from index")
        archive = repo / record["archive_path"]
        ensure_safe_history_path(repo, archive)
        if not archive.is_file() or digest(archive.read_bytes()) != record["archive_sha256"]:
            raise Blocked("BLOCKED_ARCHIVE_CORRUPT", "indexed archive bytes differ")
        validate_generation_record(repo, record, archive.read_bytes())
        line = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
        prefix += line
    if prefix != raw:
        raise Blocked("BLOCKED_INDEX_CORRUPT", "index is not canonical JSONL")
    return records, raw
def authority_ids(snapshot: Snapshot) -> list[str]:
    authority: set[str] = set()
    active = snapshot.control.get("active")
    if isinstance(active, dict): authority.add(str(active.get("task_id", "")))
    for item in snapshot.control.get("queue", []): authority.add(str(item.get("task_id", "")))
    for name in ("paused", "quick_fix", "parallel_exception"):
        item = snapshot.control.get(name)
        if isinstance(item, dict): authority.update(str(value) for key, value in item.items() if "task_id" in key)
    for item in snapshot.control.get("residuals", []): authority.add(str(item.get("task_id", "")))
    return sorted(value for value in authority if value)
def terminal_eligible(snapshot: Snapshot, line: str) -> bool:
    return is_terminal_line(line) and not AUTHORITY_LINE.search(line) and not any(identifier in line for identifier in authority_ids(snapshot))
def record_ids(snapshot: Snapshot) -> tuple[list[str], list[str]]:
    moved = []
    for line in snapshot.text.splitlines():
        match = re.match(r"^\s*- `((?:TASK_|RELEASE_|CONNLAB_)[^`]+)`", line)
        if match and terminal_eligible(snapshot, line): moved.append(match.group(1))
    return sorted(set(moved)), authority_ids(snapshot)
def moved_ids(mode: str, archive_raw: bytes, source: Snapshot) -> list[str]:
    if mode == "full_board": return record_ids(source)[0]
    payload = json.loads(archive_raw.decode("utf-8")); moved = []
    for item in payload["records"]:
        match = re.match(r"^\s*- `((?:TASK_|RELEASE_|CONNLAB_)[^`]+)`", item["text"])
        if match: moved.append(match.group(1))
    return sorted(set(moved))
def validate_generation_record(repo: Path, record: dict[str, Any], archive_raw: bytes) -> None:
    try:
        source_raw = indexed_source_bytes(repo, record)
        blob = git(repo, "rev-parse", f"{record['source_commit']}:docs/task_board.md")
        source = parse_snapshot(source_raw)
    except (subprocess.CalledProcessError, Blocked) as exc:
        raise Blocked("BLOCKED_INDEX_CORRUPT", f"source board object is unavailable: {exc}") from exc
    if (blob != record["source_blob_sha"] or source.terminal_records != record["source_record_count"] or record["rollback_sha256"] != digest(source_raw)):
        raise Blocked("BLOCKED_INDEX_CORRUPT", "source blob/hash/count/rollback facts differ")
    if record["archive_mode"] == "full_board":
        compact = first_compaction(source, record["archive_path"])
        archived_count = source.terminal_records
    elif record["archive_mode"] == "terminal_records":
        try: payload = json.loads(archive_raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc: raise Blocked("BLOCKED_ARCHIVE_CORRUPT", str(exc)) from exc
        if payload.get("schema") != INDEX_SCHEMA or payload.get("version") != INDEX_VERSION or payload.get("generation") != record["generation"] or not isinstance(payload.get("records"), list):
            raise Blocked("BLOCKED_ARCHIVE_CORRUPT", "incremental archive schema differs")
        lines = source.text.splitlines(keepends=True)
        seen: set[int] = set()
        for item in payload["records"]:
            if not isinstance(item, dict) or set(item) != {"line", "text"} or not isinstance(item["line"], int) or item["line"] in seen or item["line"] < 0 or item["line"] >= len(lines) or lines[item["line"]] != item["text"]:
                raise Blocked("BLOCKED_ARCHIVE_CORRUPT", "incremental archive record differs")
            if not terminal_eligible(source, item["text"].rstrip("\r\n")):
                raise Blocked("BLOCKED_ARCHIVE_CORRUPT", "incremental archive record carries non-terminal authority")
            seen.add(item["line"]); lines[item["line"]] = ""
        compact = "".join(lines).encode("utf-8"); archived_count = len(seen)
    else: raise Blocked("BLOCKED_INDEX_CORRUPT", "archive mode is invalid")
    compact_snapshot = parse_snapshot(compact)
    moved, retained = moved_ids(record["archive_mode"], archive_raw, source), record_ids(source)[1]
    facts = {"generation": record["generation"], "head": record["source_commit"], "source": record["source_board_sha256"],
             "archive": record["archive_sha256"], "compact": record["compact_board_sha256"], "previous": record["previous_index_sha256"]}
    if (record["archive_record_count"] != archived_count or record["compact_board_sha256"] != digest(compact) or record["compact_bytes"] != len(compact) or
            record["compact_record_count"] != compact_snapshot.terminal_records or record["moved_record_ids"] != moved or record["retained_authority_record_ids"] != retained or
            record["plan_digest"] != digest(json.dumps(facts, sort_keys=True, separators=(",", ":")).encode())):
        raise Blocked("BLOCKED_INDEX_CORRUPT", "archive/compact/count/authority facts differ")
def indexed_source_bytes(repo: Path, record: dict[str, Any]) -> bytes:
    blob_raw = subprocess.run(["git", "-C", str(repo), "show", f"{record['source_commit']}:docs/task_board.md"], check=True, capture_output=True).stdout
    candidates = [blob_raw, blob_raw.replace(b"\n", b"\r\n")]
    if record["archive_mode"] == "full_board":
        archive = repo / str(record["archive_path"])
        archive_raw = archive.read_bytes()
        if archive_raw.replace(b"\r\n", b"\n") == blob_raw:
            candidates.append(archive_raw)
    source = next((item for item in candidates if digest(item) == record["source_board_sha256"] and len(item) == record["source_bytes"]), b"")
    if not source: raise Blocked("BLOCKED_INDEX_CORRUPT", "source bytes cannot be reconstructed from the Git blob")
    return source
def first_compaction(snapshot: Snapshot, archive_path: str) -> bytes:
    prefix = snapshot.text.split(END, 1)[0] + END
    active = snapshot.control.get("active") or {}
    identifiers = {str(active.get("task_id", ""))}
    for item in snapshot.control.get("queue", []): identifiers.add(str(item.get("task_id", "")))
    for name in ("paused", "quick_fix", "parallel_exception"):
        value = snapshot.control.get(name)
        if isinstance(value, dict):
            identifiers.update(str(v) for k, v in value.items() if "task_id" in k)
    retained: list[str] = []
    for line in snapshot.text.split(END, 1)[1].splitlines():
        if line.lstrip().startswith("- `") and (ACTIVE_STATUS.search(line) or any(identifier and identifier in line for identifier in identifiers)):
            retained.append(line)
    compact = (
        prefix.rstrip() + "\n\n## Active Execution Model\n\n" +
        ("\n".join(dict.fromkeys(retained)) if retained else "- Active authority is fully represented by the execution-control JSON above.") +
        "\n\n## Immutable History\n\n" +
        f"- Generation 000001: `{archive_path}` (exact pre-maintenance board bytes).\n"
    ).encode("utf-8")
    candidate = parse_snapshot(compact)
    if threshold(candidate):
        raise Blocked("BLOCKED_COMPACTION_BUDGET", "protected active context cannot fit budgets")
    return compact

def incremental_compaction(snapshot: Snapshot, generation: int) -> tuple[bytes, bytes, int]:
    lines = snapshot.text.splitlines(keepends=True)
    eligible = [index for index, line in enumerate(lines) if terminal_eligible(snapshot, line.rstrip("\r\n"))]
    if not eligible:
        raise Blocked("BLOCKED_NO_ELIGIBLE_HISTORY", "budgets exceeded without terminal detail")
    removed: list[dict[str, Any]] = []
    working = list(lines)
    for index in eligible:
        removed.append({"line": index, "text": lines[index]})
        working[index] = ""
        candidate = parse_snapshot("".join(working).encode("utf-8"))
        if not threshold(candidate): break
    compact = "".join(working).encode("utf-8")
    if threshold(parse_snapshot(compact)):
        raise Blocked("BLOCKED_COMPACTION_BUDGET", "eligible terminal detail cannot restore budgets")
    payload = {"schema": INDEX_SCHEMA, "version": INDEX_VERSION, "generation": generation, "archive_mode": "terminal_records", "records": removed}
    archive = (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    return compact, archive, len(removed)
def build_plan(repo: Path, expected_head: str, expected_board_hash: str) -> MaintenancePlan | None:
    source = load_snapshot(repo)
    head = git(repo, "rev-parse", "HEAD")
    if head != expected_head:
        raise Blocked("BLOCKED_PRIMARY_HEAD_DRIFT", "expected HEAD differs")
    if digest(source.raw) != expected_board_hash:
        raise Blocked("BLOCKED_BOARD_HASH_DRIFT", "expected board SHA-256 differs")
    records, index_raw = index_records(repo)
    if not threshold(source): return None
    generation = len(records) + 1
    archive_path = f"docs/archive/task_board_history/generation-{generation:06d}-{head}.md"
    source_blob = git(repo, "rev-parse", "HEAD:docs/task_board.md")
    if generation == 1:
        archive_bytes = source.raw
        compact = first_compaction(source, archive_path)
        archive_mode = "full_board"
        archived_count = source.terminal_records
    else:
        compact, archive_bytes, archived_count = incremental_compaction(source, generation)
        archive_mode = "terminal_records"
    facts = {
        "generation": generation, "head": head, "source": digest(source.raw),
        "archive": digest(archive_bytes), "compact": digest(compact),
        "previous": digest(index_raw) if index_raw else "0" * 64,
    }
    plan_digest = digest(json.dumps(facts, sort_keys=True, separators=(",", ":")).encode())
    return MaintenancePlan(generation, head, source_blob, source, archive_path, archive_bytes, archive_mode, archived_count, compact, facts["previous"], plan_digest)

def plan_result(plan: MaintenancePlan | None, snapshot: Snapshot) -> dict[str, Any]:
    metrics = {"lines": snapshot.lines, "bytes": snapshot.bytes, "terminal_records": snapshot.terminal_records}
    if plan is None:
        return {"decision": "NO_MAINTENANCE_REQUIRED", "reason_codes": [], "zero_write": True, "generation": None, "plan_digest": None, "archive_path": None, "changed_paths": [], "metrics": metrics}
    return {"decision": "MAINTENANCE_REQUIRED", "reason_codes": [], "zero_write": True, "generation": plan.generation, "plan_digest": plan.plan_digest, "archive_path": plan.archive_path, "changed_paths": [], "metrics": metrics, "compact_metrics": {"lines": parse_snapshot(plan.compact).lines, "bytes": len(plan.compact), "terminal_records": parse_snapshot(plan.compact).terminal_records}}
def validate_apply_authority(repo: Path, plan: MaintenancePlan) -> None:
    control = plan.source.control
    active = control.get("active")
    if control.get("execution_state") != "gate_running" or not isinstance(active, dict) or active.get("role") != "Integrator" or control.get("execution_token_owner") != active.get("task_id"):
        raise Blocked("BLOCKED_MAINTENANCE_AUTHORITY", "only the sole gate_running/Integrator owner may apply")
    if plan.generation == 1 and active.get("task_id") != FIRST_MIGRATION_TASK:
        raise Blocked("BLOCKED_FIRST_MIGRATION_OWNER", "Task A must own the first production generation")
    if control.get("queue") or control.get("paused") is not None or control.get("quick_fix") is not None or control.get("parallel_exception") is not None:
        raise Blocked("BLOCKED_MAINTENANCE_CONTEXT", "queue/pause/Quick Fix/parallel state must be empty")
    required = {"DEVELOPER_READY", "REVIEWER_PASS"}
    if "QA" in active.get("required_gates", []): required.add("QA_PASS")
    history = [item for item in control.get("transition_history", []) if isinstance(item, dict)]
    selected: list[dict[str, Any]] = []
    for event in required:
        matches = [item for item in history if item.get("event") == event]
        if len(matches) != 1: raise Blocked("BLOCKED_MAINTENANCE_GATES", "required transition evidence is missing or ambiguous")
        selected.append(matches[0])
    order = {"DEVELOPER_READY": ("implementation_running", "Developer", "gate_running", "Reviewer", "ready_for_review"), "REVIEWER_PASS": ("gate_running", "Reviewer", "gate_running", "QA" if "QA" in active.get("required_gates", []) else "Integrator", "reviewer_pass"), "QA_PASS": ("gate_running", "QA", "gate_running", "Integrator", "qa_pass")}
    heads: dict[str, str] = {}
    current_helper = git(repo, "rev-parse", f"{plan.source_head}:scripts/connlab_active_context.py")
    required_fields = {"transition_id", "event", "task_id", "evidence_ref", "evidence_commit", "evidence_blob_sha", "evidence_sha256", "evidence_status", "lane_head", "primary_head", "helper_blob_sha", "retained_context_digest", "from_state", "from_role", "to_state", "to_role"}
    for entry in selected:
        if not required_fields.issubset(entry) or entry["task_id"] != active["task_id"]: raise Blocked("BLOCKED_MAINTENANCE_GATES", "transition entry is incomplete")
        path, commit, expected = parse_ref(str(entry["evidence_ref"])); raw = git_bytes(repo, commit, path)
        from_state, role, to_state, to_role, status = order[entry["event"]]
        if (commit != entry["evidence_commit"] or expected != entry["evidence_sha256"] or digest(raw) != expected or
                git(repo, "rev-parse", f"{commit}:{path}") != entry["evidence_blob_sha"] or entry["evidence_status"] != status or
                parse_machine(raw.decode("utf-8")) != (active["task_id"], role, status) or entry["lane_head"] != commit or
                (entry["from_state"], entry["from_role"], entry["to_state"], entry["to_role"]) != (from_state, role, to_state, to_role) or
                entry["transition_id"] != transition_digest(entry, active["lane"]) or entry["retained_context_digest"] != context_digest(control) or
                subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", entry["primary_head"], plan.source_head]).returncode):
            raise Blocked("BLOCKED_MAINTENANCE_GATES", "transition evidence facts differ")
        helper_blob = git(repo, "rev-parse", f"{entry['lane_head']}:scripts/connlab_active_context.py")
        if helper_blob != entry["helper_blob_sha"] or entry["event"] in {"REVIEWER_PASS", "QA_PASS"} and helper_blob != current_helper: raise Blocked("BLOCKED_HELPER_ANCESTRY", "accepted helper checkpoint differs")
        heads[entry["event"]] = entry["lane_head"]
    chain = [heads["DEVELOPER_READY"], heads["REVIEWER_PASS"]] + ([heads["QA_PASS"]] if "QA_PASS" in heads else [])
    if any(subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", prior, current]).returncode for prior, current in zip(chain, chain[1:])):
        raise Blocked("BLOCKED_MAINTENANCE_GATES", "gate evidence ancestry is invalid")

def parse_ref(value: str) -> tuple[str, str, str]:
    match = re.fullmatch(r"([^@#]+)@([0-9a-f]{40})#([0-9a-f]{64})", value)
    if not match or Path(match.group(1)).is_absolute() or ".." in Path(match.group(1)).parts: raise Blocked("BLOCKED_MAINTENANCE_GATES", "evidence ref is invalid")
    return match.groups()


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    done = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"], check=False, capture_output=True)
    if done.returncode: raise Blocked("BLOCKED_MAINTENANCE_GATES", "evidence blob is unavailable")
    return done.stdout


def parse_machine(text: str) -> tuple[str, str, str]:
    records = re.findall(r"(?m)^TASK_ID:\s*([^\r\n]+)\r?\nROLE:\s*([^\r\n]+)\r?\nSTATUS:\s*([^\r\n]+)$", text)
    if len(records) != 1: raise Blocked("BLOCKED_MAINTENANCE_GATES", "evidence record is ambiguous")
    return tuple(value.strip() for value in records[0])


def atomic_replace(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".connlab-maintenance-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def apply(repo: Path, plan: MaintenancePlan, expected_plan_digest: str) -> dict[str, Any]:
    if expected_plan_digest != plan.plan_digest:
        raise Blocked("BLOCKED_PLAN_STALE", "expected plan digest differs")
    validate_apply_authority(repo, plan)
    archive = repo / plan.archive_path
    index = repo / INDEX_PATH
    ensure_safe_history_path(repo, archive)
    ensure_safe_history_path(repo, index)
    if archive.exists():
        if archive.read_bytes() == plan.archive_bytes:
            raise Blocked("BLOCKED_ARCHIVE_UNINDEXED", "matching archive exists without indexed completion")
        raise Blocked("BLOCKED_ARCHIVE_CONFLICT", "archive path contains different bytes")
    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise Blocked("BLOCKED_PRIMARY_DIRTY", "primary worktree/index must be clean")
    _, old_index = index_records(repo)
    compact_snapshot = parse_snapshot(plan.compact)
    moved, retained = moved_ids(plan.archive_mode, plan.archive_bytes, plan.source), record_ids(plan.source)[1]
    record = {
        "schema": INDEX_SCHEMA, "version": INDEX_VERSION, "plan_digest": plan.plan_digest,
        "generation": plan.generation, "source_commit": plan.source_head,
        "source_blob_sha": plan.source_blob, "source_board_sha256": digest(plan.source.raw),
        "source_bytes": plan.source.bytes, "source_record_count": plan.source.terminal_records,
        "archive_path": plan.archive_path, "archive_sha256": digest(plan.archive_bytes),
        "archive_record_count": plan.archive_record_count, "archive_mode": plan.archive_mode,
        "compact_board_sha256": digest(plan.compact), "compact_bytes": len(plan.compact), "compact_record_count": compact_snapshot.terminal_records,
        "previous_index_sha256": plan.previous_index_hash, "rollback_sha256": digest(plan.source.raw),
        "moved_record_ids": moved, "retained_authority_record_ids": retained,
    }
    line = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    new_index = old_index + line
    board_path = repo / "docs" / "task_board.md"
    created_archive = False
    fault = os.environ.get("CONNLAB_MAINTENANCE_FAIL_AFTER")
    try:
        archive.parent.mkdir(parents=True, exist_ok=True)
        with archive.open("xb") as stream:
            stream.write(plan.archive_bytes); stream.flush(); os.fsync(stream.fileno())
        created_archive = True
        if fault == "archive": raise OSError("injected after archive")
        atomic_replace(index, new_index)
        if fault == "index": raise OSError("injected after index")
        atomic_replace(board_path, plan.compact)
        if fault == "board": raise OSError("injected after board")
    except Exception as exc:
        atomic_replace(board_path, plan.source.raw)
        if old_index: atomic_replace(index, old_index)
        elif index.exists(): index.unlink()
        if created_archive and archive.exists() and archive.read_bytes() == plan.archive_bytes: archive.unlink()
        raise Blocked("BLOCKED_MAINTENANCE_WRITE_FAILED", str(exc)) from exc
    return {"decision": "APPLIED_MAINTENANCE", "reason_codes": [], "zero_write": False, "generation": plan.generation, "plan_digest": plan.plan_digest, "archive_path": plan.archive_path, "changed_paths": [plan.archive_path, INDEX_PATH.as_posix(), "docs/task_board.md"], "before_sha256": digest(plan.source.raw), "after_sha256": digest(plan.compact)}


def safe_rollback_output(repo: Path, temp_root: Path, output: Path) -> Path:
    system_temp = Path(tempfile.gettempdir()).resolve()
    lexical_root = Path(os.path.abspath(temp_root))
    try: root = lexical_root.resolve(strict=True)
    except OSError as exc: raise Blocked("BLOCKED_ROLLBACK_OUTPUT_ROOT", "temporary root must already exist") from exc
    if lexical_root != root or not root.is_dir() or lexical_root.is_symlink() or getattr(lexical_root, "is_junction", lambda: False)() or root == repo or repo in root.parents or root in repo.parents or root != system_temp and system_temp not in root.parents:
        raise Blocked("BLOCKED_ROLLBACK_OUTPUT_ROOT", "temporary root is not independently proven")
    candidate = Path(os.path.abspath(output)); parent = candidate.parent
    try: resolved_parent = parent.resolve(strict=True)
    except OSError as exc: raise Blocked("BLOCKED_ROLLBACK_OUTPUT_PATH", "output parent must already exist") from exc
    if resolved_parent != root and root not in resolved_parent.parents:
        raise Blocked("BLOCKED_ROLLBACK_OUTPUT_PATH", "output escaped the temporary root")
    current = root
    for part in resolved_parent.relative_to(root).parts:
        current /= part
        if current.is_symlink() or getattr(current, "is_junction", lambda: False)(): raise Blocked("BLOCKED_ROLLBACK_OUTPUT_PATH", "output traverses a link or junction")
    if os.path.lexists(candidate): raise Blocked("BLOCKED_ROLLBACK_OUTPUT_EXISTS", "rollback proof never overwrites an existing target")
    return candidate


def prove_rollback(repo: Path, generation: int, temp_root: Path, output: Path) -> dict[str, Any]:
    records, _ = index_records(repo)
    if generation < 1 or generation > len(records):
        raise Blocked("BLOCKED_GENERATION_UNKNOWN", "generation is outside the index")
    current = (repo / "docs" / "task_board.md").read_bytes()
    if digest(current) != records[-1]["compact_board_sha256"]: raise Blocked("BLOCKED_ROLLBACK_CHAIN", "current board is not the last proven compact generation")
    current = indexed_source_bytes(repo, records[generation - 1])
    target = safe_rollback_output(repo, temp_root, output)
    with target.open("xb") as stream: stream.write(current); stream.flush(); os.fsync(stream.fileno())
    return {"decision": "ROLLBACK_PROVEN", "reason_codes": [], "zero_write": False, "generation": generation, "output": str(target), "sha256": digest(current), "changed_paths": [str(target)]}


def already_applied(repo: Path, records: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any] | None:
    if not records: return None
    last = records[-1]
    if last["source_commit"] != args.expected_head or last["source_board_sha256"] != args.expected_board_sha256: return None
    board = load_snapshot(repo)
    status = subprocess.run(["git", "-C", str(repo), "status", "--porcelain=v1", "--untracked-files=all"], check=True, capture_output=True, text=True).stdout
    paths = {line[3:].replace("\\", "/") for line in status.splitlines() if len(line) > 3}
    expected_paths = {"docs/task_board.md", INDEX_PATH.as_posix(), last["archive_path"]}
    if (args.expected_plan_digest != last["plan_digest"] or digest(board.raw) != last["compact_board_sha256"] or
            board.bytes != last["compact_bytes"] or board.terminal_records != last["compact_record_count"] or paths not in (set(), expected_paths)):
        raise Blocked("BLOCKED_ALREADY_APPLIED_DRIFT", "recorded maintenance result no longer matches current facts")
    return {"decision": "ALREADY_APPLIED", "reason_codes": [], "zero_write": True, "generation": last["generation"], "archive_path": last["archive_path"], "changed_paths": []}


def execute(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo_root).resolve(); ensure_primary(repo)
    snapshot = load_snapshot(repo)
    if args.command == "inspect":
        return {"decision": "ALLOW_INSPECT", "reason_codes": [], "zero_write": True, "metrics": {"lines": snapshot.lines, "bytes": snapshot.bytes, "terminal_records": snapshot.terminal_records}, "changed_paths": []}
    if args.command == "prove-rollback": return prove_rollback(repo, args.generation, Path(args.temp_root), Path(args.output))
    records, _ = index_records(repo)
    if args.command == "apply-maintenance":
        prior = already_applied(repo, records, args)
        if prior: return prior
    plan = build_plan(repo, args.expected_head, args.expected_board_sha256)
    if args.command == "plan-maintenance": return plan_result(plan, snapshot)
    if plan is None:
        return {"decision": "NO_MAINTENANCE_REQUIRED", "reason_codes": [], "zero_write": True, "generation": None, "changed_paths": []}
    return apply(repo, plan, args.expected_plan_digest)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(); sub = root.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect"); inspect.add_argument("--repo-root", required=True); inspect.add_argument("--json", action="store_true")
    for name in ("plan-maintenance", "apply-maintenance"):
        command = sub.add_parser(name); command.add_argument("--repo-root", required=True)
        command.add_argument("--expected-head", required=True); command.add_argument("--expected-board-sha256", required=True)
        if name == "apply-maintenance": command.add_argument("--expected-plan-digest", required=True)
        command.add_argument("--json", action="store_true")
    rollback = sub.add_parser("prove-rollback"); rollback.add_argument("--repo-root", required=True)
    rollback.add_argument("--generation", required=True, type=int); rollback.add_argument("--temp-root", required=True); rollback.add_argument("--output", required=True); rollback.add_argument("--json", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    try: payload = execute(args); code = 0
    except Blocked as exc:
        payload = {"decision": "BLOCKED", "reason_codes": [exc.code], "zero_write": True, "generation": None, "archive_path": None, "changed_paths": [], "detail": exc.detail}; code = 2
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


if __name__ == "__main__": sys.exit(main())
