from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

from scripts.connlab_serial_complex import (
    SerialContractError,
    apply_cutover_payload,
    intrinsic_permission_probe,
    validate_invocation,
    validate_native_action,
)
from scripts.connlab_serial_board import Blocked
from scripts import connlab_personal_task


ZERO64 = "0" * 64
ROOT = Path(__file__).resolve().parents[2]


def canonical_hash(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def test_native_action_and_invocation_use_exact_schemas() -> None:
    action = {
        "schema": "connlab.serial-native-action",
        "version": 1,
        "action_id": ZERO64,
        "action": "reviewer_dispatch",
        "role": "Reviewer",
        "attempt": 1,
        "prompt_sha256": ZERO64,
        "title": "ConnLab Reviewer",
        "recorded_at": "2026-08-06T00:00:00Z",
    }
    assert validate_native_action(action) == action
    invocation = {
        "schema": "connlab.serial-invocation",
        "version": 1,
        "action_id": ZERO64,
        "role": "Reviewer",
        "attempt": 1,
        "thread_id": None,
        "agent_id": "agent-1",
        "host_id": "host-1",
        "status": "started",
        "recorded_at": "2026-08-06T00:00:01Z",
    }
    assert validate_invocation(invocation) == invocation
    invocation["thread_id"] = "thread-1"
    with pytest.raises(SerialContractError, match="BLOCKED_ARGUMENT_COMBINATION"):
        validate_invocation(invocation)


def test_permission_probe_uses_nonwriting_rdwr_handle_and_receipt(tmp_path: Path) -> None:
    paths = []
    calls: list[tuple[str, int]] = []
    for number in range(8):
        path = tmp_path / f"target-{number}.txt"
        path.write_bytes(f"value-{number}".encode())
        paths.append(path.name)
    original_open = os.open

    def recording_open(path: str | bytes | os.PathLike[str] | os.PathLike[bytes], flags: int, *args: object) -> int:
        calls.append((os.fspath(path), flags))
        return original_open(path, flags, *args)

    proof = intrinsic_permission_probe(tmp_path, "TASK_EXAMPLE", "a" * 40, paths, opener=recording_open)

    assert proof["observation_source"] == "same_process_write_handle_probe"
    assert proof["algorithm"] == "python_os_open_rdwr_binary_no_write_v1"
    assert len(calls) == 8
    assert all(flags == os.O_RDWR | getattr(os, "O_BINARY", 0) for _, flags in calls)
    receipt_source = {key: value for key, value in proof.items() if key != "probe_receipt_sha256"}
    assert proof["probe_receipt_sha256"] == canonical_hash(receipt_source)
    assert all(record["unchanged"] and record["handle_opened"] for record in proof["paths"])
    assert [path.read_bytes() for path in map(tmp_path.__truediv__, paths)] == [f"value-{n}".encode() for n in range(8)]


def test_manifest_permission_drift_blocks_before_any_materialization(tmp_path: Path) -> None:
    """Revision-5 bounded drift test: one apply denial causes zero target/index/HEAD writes."""
    paths = []
    for number in range(8):
        path = tmp_path / f"target-{number}.txt"
        path.write_bytes(f"source-{number}".encode())
        paths.append(path.name)
    source_bytes = {path: (tmp_path / path).read_bytes() for path in paths}
    original_open = os.open
    first_proof = intrinsic_permission_probe(tmp_path, "TASK_EXAMPLE", "b" * 40, paths)
    manifest = {
        "task_id": "TASK_EXAMPLE",
        "source_head": "b" * 40,
        "paths": paths,
        "permission_proof": first_proof,
    }
    materialized: list[str] = []

    def drifted_open(path: str | bytes | os.PathLike[str] | os.PathLike[bytes], flags: int, *args: object) -> int:
        if Path(path).name == "target-3.txt":
            raise PermissionError("simulated permission drift")
        return original_open(path, flags, *args)

    with pytest.raises(SerialContractError, match="BLOCKED_CUTOVER_PATH_READ_ONLY"):
        apply_cutover_payload(
            tmp_path,
            manifest,
            opener=drifted_open,
            materializer=lambda path: materialized.append(path),
        )

    assert materialized == []
    assert {path: (tmp_path / path).read_bytes() for path in paths} == source_bytes


def test_retained_repository_verifier_proves_identity_cleanliness_ancestry_and_evidence(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    worktree = tmp_path / "task-worktree"
    primary.mkdir()
    git(primary, "init", "-b", "master")
    git(primary, "config", "user.email", "test@example.invalid")
    git(primary, "config", "user.name", "Test")
    (primary / "README.md").write_text("base\n", encoding="utf-8")
    git(primary, "add", "README.md")
    git(primary, "commit", "-m", "base")
    git(primary, "worktree", "add", "-b", "codex/task-example", str(worktree), "HEAD")
    (worktree / "subject.txt").write_text("subject\n", encoding="utf-8")
    git(worktree, "add", "subject.txt")
    git(worktree, "commit", "-m", "subject")
    branch_head = git(worktree, "rev-parse", "HEAD")
    git(primary, "merge", "--no-ff", "--no-edit", "codex/task-example")
    integrated_commit = git(primary, "rev-parse", "HEAD")
    evidence_path = primary / "docs" / "lane_evidence" / "closeout.md"
    evidence_path.parent.mkdir(parents=True)
    evidence_bytes = b"retained closeout proof\n"
    evidence_path.write_bytes(evidence_bytes)
    git(primary, "add", "docs/lane_evidence/closeout.md")
    git(primary, "commit", "-m", "evidence")
    evidence_commit = git(primary, "rev-parse", "HEAD")
    evidence_ref = (
        f"docs/lane_evidence/closeout.md@{evidence_commit}#"
        f"{hashlib.sha256(evidence_bytes).hexdigest()}"
    )
    active = {
        "task_id": "TASK_EXAMPLE",
        "complex_context": {
            "host_thread_id": "thread-1",
            "task_worktree": str(worktree.resolve()),
            "task_branch": "codex/task-example",
            "head_sha": branch_head,
            "integrated_commit": integrated_commit,
            "worktree_lifecycle": "integrated",
            "current_role": None,
            "pending_callback": None,
        },
    }
    closeout = {
        "schema": "connlab.serial-closeout",
        "version": 1,
        "action_id": ZERO64,
        "disposition": "retained",
        "task_id": "TASK_EXAMPLE",
        "thread_id": "thread-1",
        "worktree": str(worktree.resolve()),
        "branch": "codex/task-example",
        "head_sha": branch_head,
        "clean": True,
        "integrated_commit": integrated_commit,
        "evidence_ref": evidence_ref,
        "reason": "retained_nonblocking_manual_maintenance",
        "recorded_at": "2026-08-06T00:00:00Z",
    }

    assert connlab_personal_task.verify_retained_repository(primary, active, closeout) == closeout
    (worktree / "dirty.txt").write_text("dirty", encoding="utf-8")
    with pytest.raises(Blocked, match="clean"):
        connlab_personal_task.verify_retained_repository(primary, active, closeout)


def test_public_writer_freezes_complex_commands_on_v1_and_rejects_permission_assertion() -> None:
    board = ROOT / "docs/task_board.md"
    before = board.read_bytes()
    board_hash = hashlib.sha256(before).hexdigest()
    action = {
        "schema": "connlab.serial-native-action", "version": 1, "action_id": ZERO64,
        "action": "planner_dispatch", "role": "Planner", "attempt": 1,
        "prompt_sha256": ZERO64, "title": "Planner", "recorded_at": "2026-08-06T00:00:00Z",
    }
    frozen = subprocess.run(
        ["py", str(ROOT / "scripts/connlab_personal_task.py"), "begin-role", "--repo-root", str(ROOT),
         "--expected-board-sha256", board_hash, "--task-id", "TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION",
         "--role", "Planner", "--native-action-json", json.dumps(action), "--json"],
        text=True, encoding="utf-8", capture_output=True, check=False,
    )
    assert json.loads(frozen.stdout)["code"] == "BLOCKED_LEGACY_MODE_FROZEN"

    rejected = subprocess.run(
        ["py", str(ROOT / "scripts/connlab_personal_task.py"), "classify", "--repo-root", str(ROOT),
         "--request-json", "{}", "--permission-preflight-json", "{}", "--json"],
        text=True, encoding="utf-8", capture_output=True, check=False,
    )
    assert json.loads(rejected.stdout)["code"] == "BLOCKED_ARGUMENT_COMBINATION"

    rejected_order = subprocess.run(
        ["py", str(ROOT / "scripts/connlab_personal_task.py"), "plan-cutover", "--repo-root", str(ROOT),
         "--task-id", "TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION",
         "--expected-primary-head", "a" * 40, "--closeout-order", "retire_then_archive", "--json"],
        text=True, encoding="utf-8", capture_output=True, check=False,
    )
    assert json.loads(rejected_order.stdout)["code"] == "BLOCKED_ARGUMENT_COMBINATION"
    assert board.read_bytes() == before
