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
ARCHIVE_PATTERN = re.compile(r"docs/archive/task_board_history/generation-(\d{6})-([0-9a-f]{40})\.md")
TERMINAL = re.compile(r"^\s*- `(?:TASK_|RELEASE_|CONNLAB_).+?:.*\b(complete|completed|accepted|cancelled|superseded|closed|frozen|historical)\b", re.I)
ACTIVE_STATUS = re.compile(r"planned|proposed|queued|implementation_running|gate_running|paused_preempted|quick_fix_running|reconciling", re.I)
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
    if path.parent != root or repo not in path.parents:
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
            "generation", "source_commit", "source_blob_sha", "source_board_sha256",
            "source_bytes", "source_record_count", "archive_path", "archive_sha256",
            "archive_record_count", "archive_mode", "compact_board_sha256",
            "compact_record_count", "previous_index_sha256", "rollback_sha256",
        }
        if not required.issubset(record) or record["generation"] != number:
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
        line = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
        prefix += line
    if prefix != raw:
        raise Blocked("BLOCKED_INDEX_CORRUPT", "index is not canonical JSONL")
    return records, raw


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


def incremental_compaction(snapshot: Snapshot) -> tuple[bytes, bytes, int]:
    lines = snapshot.text.splitlines(keepends=True)
    eligible = [index for index, line in enumerate(lines) if is_terminal_line(line.rstrip("\r\n"))]
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
    payload = {"archive_mode": "terminal_records", "records": removed}
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
        compact, archive_bytes, archived_count = incremental_compaction(source)
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
    events = {item.get("event") for item in control.get("transition_history", []) if isinstance(item, dict)}
    required = {"DEVELOPER_READY", "REVIEWER_PASS"}
    if "QA" in active.get("required_gates", []): required.add("QA_PASS")
    if not required.issubset(events):
        raise Blocked("BLOCKED_MAINTENANCE_GATES", "required transition evidence is incomplete")
    try: git(repo, "cat-file", "-e", "HEAD:scripts/connlab_active_context.py")
    except Blocked as exc: raise Blocked("BLOCKED_HELPER_ANCESTRY", exc.detail) from exc


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
    record = {
        "generation": plan.generation, "source_commit": plan.source_head,
        "source_blob_sha": plan.source_blob, "source_board_sha256": digest(plan.source.raw),
        "source_bytes": plan.source.bytes, "source_record_count": plan.source.terminal_records,
        "archive_path": plan.archive_path, "archive_sha256": digest(plan.archive_bytes),
        "archive_record_count": plan.archive_record_count, "archive_mode": plan.archive_mode,
        "compact_board_sha256": digest(plan.compact), "compact_record_count": compact_snapshot.terminal_records,
        "previous_index_sha256": plan.previous_index_hash, "rollback_sha256": digest(plan.source.raw),
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


def prove_rollback(repo: Path, generation: int, output: Path) -> dict[str, Any]:
    records, _ = index_records(repo)
    if generation < 1 or generation > len(records):
        raise Blocked("BLOCKED_GENERATION_UNKNOWN", "generation is outside the index")
    current = (repo / "docs" / "task_board.md").read_bytes()
    for record in reversed(records[generation - 1 :]):
        if digest(current) != record["compact_board_sha256"]:
            raise Blocked("BLOCKED_ROLLBACK_CHAIN", "compact board hash differs")
        archive = (repo / record["archive_path"]).read_bytes()
        if record["archive_mode"] == "full_board":
            current = archive
        else:
            payload = json.loads(archive.decode("utf-8"))
            lines = current.decode("utf-8").splitlines(keepends=True)
            for item in sorted(payload["records"], key=lambda value: value["line"]):
                lines.insert(int(item["line"]), item["text"])
            current = "".join(lines).encode("utf-8")
        if digest(current) != record["source_board_sha256"]:
            raise Blocked("BLOCKED_ROLLBACK_CHAIN", "reconstructed source hash differs")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(current)
    return {"decision": "ROLLBACK_PROVEN", "reason_codes": [], "zero_write": False, "generation": generation, "output": str(output), "sha256": digest(current), "changed_paths": [str(output)]}


def execute(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo_root).resolve(); ensure_primary(repo)
    snapshot = load_snapshot(repo)
    if args.command == "inspect":
        return {"decision": "ALLOW_INSPECT", "reason_codes": [], "zero_write": True, "metrics": {"lines": snapshot.lines, "bytes": snapshot.bytes, "terminal_records": snapshot.terminal_records}, "changed_paths": []}
    if args.command == "prove-rollback": return prove_rollback(repo, args.generation, Path(args.output).resolve())
    records, _ = index_records(repo)
    if args.command == "apply-maintenance" and records:
        last = records[-1]
        if last["source_commit"] == args.expected_head and last["source_board_sha256"] == args.expected_board_sha256:
            return {"decision": "ALREADY_APPLIED", "reason_codes": [], "zero_write": True, "generation": last["generation"], "archive_path": last["archive_path"], "changed_paths": []}
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
    rollback.add_argument("--generation", required=True, type=int); rollback.add_argument("--output", required=True); rollback.add_argument("--json", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    try: payload = execute(args); code = 0
    except Blocked as exc:
        payload = {"decision": "BLOCKED", "reason_codes": [exc.code], "zero_write": True, "generation": None, "archive_path": None, "changed_paths": [], "detail": exc.detail}; code = 2
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


if __name__ == "__main__": sys.exit(main())
