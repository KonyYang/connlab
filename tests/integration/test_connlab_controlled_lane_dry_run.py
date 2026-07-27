from __future__ import annotations

import json
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.connlab_controlled_lane.contracts import CtlError, MUTATION_COMMANDS, canonical_digest
from scripts.connlab_controlled_lane.registry import RegistryStore

_AUTHORITY = {"role": "Developer", "evidence_path": "docs/evidence.md",
              "base_lane_head": "base", "allowed_changed_paths": ["docs/evidence.md"],
              "checkpoint_required": True, "nullable": False}
_TARGET = {"task_id": "TASK_1", "lane_id": "lane-1", "route_id": "route-1",
           "operation_id": "operation-1", "payload_digest": "external-payload",
           "action_kind": "create_developer_environment", "role": "Developer",
           "native_mode": "create_new", "saved_project_id": "project-1",
           "project_path": "C:/repo", "repository_fingerprint": "scope-1",
           "environment": "worktree", "starting_ref": "master",
           "expected_base_commit": "base", "expected_primary_head": "base",
           "scope_fingerprint": "scope-1", "owner_claims_digest": canonical_digest([]),
           "prompt_digest": "prompt", "client_request_digest": "request",
           "completion_authority_nullable": False,
           "expected_evidence_path": "docs/evidence.md",
           "base_lane_head": "base", "allowed_changed_paths": ["docs/evidence.md"],
           "checkpoint_required": True}
_RECEIPT = {"pendingWorktreeId": "pending-1"}
_EXACT = {
    **_TARGET, "thread_id": "thread-1", "pending_worktree_id": "pending-1",
    "worktree_path": "C:/lane", "branch": "codex/lane",
    "base_commit": "base", "head": "base", "git_common_dir": "C:/.git",
    "project_binding_verified": True, "prompt_markers_verified": True,
    "worktree_clean": True, "index_clean": True,
    "path_unique": True, "branch_unique": True,
}


def _request(command: str) -> dict[str, object]:
    payload = {
        "action_kind": "create_developer_environment",
        "current_state": "authorized",
        "expected_stage": "none",
        "target_binding": _TARGET,
    }
    return {
        "schema_version": 2, "command": command, "request_id": "request-1",
        "repo_root": "fixture", "task_id": "TASK_1", "lane_id": "lane-1",
        "expected_registry_generation": 0, "idempotency_key": "key-1",
        "operation_id": "operation-1", "route_id": "route-1",
        "scope_fingerprint": "scope-1", "payload": payload,
        "payload_digest": canonical_digest(payload), "dry_run": command in MUTATION_COMMANDS,
    }


def _mutation(
    command: str, generation: int, key: str, payload: dict[str, object]
) -> dict[str, object]:
    request = _request(command)
    request.update(
        dry_run=False, expected_registry_generation=generation,
        idempotency_key=key, payload=payload, payload_digest=canonical_digest(payload))
    return request


def _git(path: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(path), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "master")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "fixture")
    return repo


def _run_cli(tmp_path: Path, request: dict[str, object]) -> subprocess.CompletedProcess[str]:
    request_path = tmp_path / f"{request['command']}.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.connlab_controlled_lane.cli",
            str(request["command"]),
            "--request-json",
            str(request_path),
            "--registry-root",
            str(tmp_path / "registry"),
            "--allow-test-registry-root",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def _seed_lane(tmp_path: Path, *, state: str = "authorized",
    proof: dict[str, object] | None = None,
    authority_files: dict[str, str] | None = None,
    primary_repo_root: str = "fixture") -> RegistryStore:
    root = tmp_path / "registry"
    root.mkdir(exist_ok=True)
    store = RegistryStore(root, repository_fingerprint="scope-1")
    registry = store.load()
    registry["lanes"]["lane-1"] = {
        "state": state, "proof": {"completion_authority": _AUTHORITY, **(proof or {})},
        "scope_fingerprint": "scope-1",
        "authority_files": authority_files or {}, "requested_scope": {},
        "owner_claims": [],
        "primary_repo_root": primary_repo_root,
    }
    store._atomic_write(registry)
    return store


@pytest.mark.parametrize("command", MUTATION_COMMANDS)
def test_each_mutation_dry_run_has_stable_json_and_zero_writes(
    tmp_path: Path, command: str) -> None:
    request_path = tmp_path / "request.json"
    registry_root = tmp_path / "registry"
    request_path.write_text(
        json.dumps(_request(command)),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.connlab_controlled_lane.cli",
            command,
            "--request-json",
            str(request_path),
            "--registry-root",
            str(registry_root),
            "--allow-test-registry-root",
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert completed.stderr == ""
    assert completed.stdout.strip() == json.dumps(
        output,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    assert output["code"] == "CTL_DRY_RUN"
    assert not registry_root.exists()


def test_cli_rejects_request_command_mismatch(tmp_path: Path) -> None:
    request = _request("prepare-dispatch")
    request_path = tmp_path / "request.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.connlab_controlled_lane.cli",
            "mark-invocation-started",
            "--request-json",
            str(request_path),
            "--registry-root",
            str(tmp_path / "registry"),
            "--allow-test-registry-root",
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = json.loads(completed.stdout)
    assert completed.returncode == 2
    assert output["code"] == "CTL_INVALID_REQUEST"
    assert not (tmp_path / "registry").exists()


def test_recovery_uses_durable_journal_stage_not_caller_claim(tmp_path: Path) -> None:
    root = tmp_path / "registry"
    store = _seed_lane(tmp_path, state="authorized")
    prepared = _request("prepare-dispatch")
    expected_binding = _TARGET
    prepared["payload"] = {
        "action_kind": "create_developer_environment",
        "current_state": "authorized",
        "target_binding": expected_binding,
    }
    prepared["payload_digest"] = canonical_digest(prepared["payload"])
    prepared["dry_run"] = False
    assert store.execute("prepare-dispatch", prepared)["code"] == "CTL_OK"
    started = _request("mark-invocation-started")
    started["dry_run"] = False
    started["expected_registry_generation"] = 1
    started["idempotency_key"] = "key-start"
    assert store.execute("mark-invocation-started", started)["code"] == "CTL_OK"

    request = _request("recover")
    request["payload"] = {
        "stage": "prepared",
        "invocation_may_have_started": False,
        "readback_matches": 1,
        "readback_readable": True,
        "readback_binding": {
            **expected_binding, "thread_id": "thread-1",
            "pending_worktree_id": "pending-1", "worktree_path": "C:/lane",
            "branch": "codex/lane", "base_commit": "base", "head": "wrong",
            "git_common_dir": "C:/.git",
        },
    }
    request["payload"]["readback_digest"] = canonical_digest(
        request["payload"]["readback_binding"]
    )
    request["payload_digest"] = canonical_digest(request["payload"])
    completed = _run_cli(tmp_path, request)
    output = json.loads(completed.stdout)

    assert output["code"] == "CTL_RECOVERY_REQUIRED"
    assert output["recovery"]["resend"] is False


def _acknowledged_option_a_store(tmp_path: Path) -> RegistryStore:
    store = _seed_lane(tmp_path)
    assert store.execute(
        "prepare-dispatch",
        _mutation("prepare-dispatch", 0, "prepare", {
            "action_kind": "create_developer_environment",
            "current_state": "authorized", "target_binding": _TARGET,
        }),
    )["code"] == "CTL_OK"
    assert store.execute(
        "mark-invocation-started",
        _mutation("mark-invocation-started", 1, "start", {
            "expected_stage": "prepared"}),
    )["code"] == "CTL_OK"
    assert store.execute(
        "record-action-result",
        _mutation("record-action-result", 2, "result", {
            "expected_stage": "invocation_started",
            "result_stage": "result_recorded", "receipt": _RECEIPT,
            "receipt_digest": canonical_digest(_RECEIPT),
        }),
    )["code"] == "CTL_OK"
    return store


def test_option_a_ack_rejects_changed_receipt_without_identity_write(
    tmp_path: Path,
) -> None:
    repo = _git_repo(tmp_path)
    store = _acknowledged_option_a_store(tmp_path)
    registry = store.load()
    registry["lanes"]["lane-1"].update(
        primary_repo_root=str(repo),
        authority_files={"README.md": hashlib.sha256(
            (repo / "README.md").read_bytes()).hexdigest()})
    store._atomic_write(registry)
    scan = _request("scan")
    scan["payload"]["native_environment_readback"] = {
        "status": "pending", "pendingWorktreeId": "pending-1"}
    scan["payload_digest"] = canonical_digest(scan["payload"])

    completed = _run_cli(tmp_path, scan)
    pending = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert pending["code"] == "CTL_NO_ACTION"
    assert pending["native_worktree_status"] == "pending"
    assert pending["route_id"] == "route-1"
    assert pending["operation_id"] == "operation-1"
    assert (pending["retry_allowed"], pending["adopted"]) == (False, False)
    assert store.load()["generation"] == 3
    payload = {
        "receipt_digest": "changed", "readback_binding": _EXACT,
        "readback_digest": canonical_digest(_EXACT), "readback_readable": True,
    }

    result = store.execute(
        "ack-dispatch", _mutation("ack-dispatch", 3, "ack", payload))

    assert result["code"] == "CTL_DISPATCH_ACK_MISMATCH"
    assert store.load()["generation"] == 3
    assert store.load()["role_bindings"] == {}


@pytest.mark.parametrize(
    ("from_state", "to_state", "code"),
    [
        ("developer_environment_pending", "archived", "CTL_INVALID_TRANSITION"),
        ("planned", "plan_review_pending", "CTL_DISPATCH_ACK_MISMATCH"),
    ],
)
def test_option_a_advance_rejects_illegal_or_unrelated_transition(
    tmp_path: Path, from_state: str, to_state: str, code: str
) -> None:
    store = _acknowledged_option_a_store(tmp_path)
    ack = {
        "receipt_digest": canonical_digest(_RECEIPT),
        "readback_binding": _EXACT, "readback_digest": canonical_digest(_EXACT),
        "readback_readable": True,
    }
    assert store.execute(
        "ack-dispatch", _mutation("ack-dispatch", 3, "ack", ack)
    )["code"] == "CTL_OK"
    advance = {"from_state": from_state, "to_state": to_state}

    result = store.execute(
        "advance-state", _mutation("advance-state", 4, "advance", advance))

    assert result["code"] == code
    assert store.load()["generation"] == 4


def test_registry_lock_and_pre_replace_failure_are_zero_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "registry"
    store = _seed_lane(tmp_path)
    store.lock_path.write_text('{"token":"other"}\n', encoding="utf-8")
    request = _request("prepare-dispatch")
    request["dry_run"] = False
    assert store.execute("prepare-dispatch", request)["code"] == "CTL_LOCK_BUSY"
    store.lock_path.unlink()
    assert store.execute("prepare-dispatch", request)["code"] == "CTL_OK"
    before = store.path.read_bytes()
    monkeypatch.setattr(os, "replace", lambda *args: (_ for _ in ()).throw(OSError()))
    started = _request("mark-invocation-started")
    started.update(dry_run=False, expected_registry_generation=1, idempotency_key="start")
    result = store.execute("mark-invocation-started", started)
    assert result["code"] == "CTL_ATOMIC_WRITE_FAILED"
    assert result["zero_write"] is True
    assert store.path.read_bytes() == before


def test_post_replace_verify_failure_records_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = _seed_lane(tmp_path)
    request = _request("prepare-dispatch")
    request["dry_run"] = False
    assert store.execute("prepare-dispatch", request)["code"] == "CTL_OK"
    original_read = Path.read_text
    reads = 0

    def fail_verify(path: Path, *args: object, **kwargs: object) -> str:
        nonlocal reads
        if path == store.path:
            reads += 1
            if reads == 2:
                raise OSError("verify")
        return original_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_verify)
    started = _request("mark-invocation-started")
    started.update(dry_run=False, expected_registry_generation=1, idempotency_key="start")
    result = store.execute("mark-invocation-started", started)
    assert result["code"] == "CTL_POST_WRITE_VERIFY_FAILED"
    assert result["zero_write"] is False
    assert store.recovery_path.exists()
    monkeypatch.setattr(Path, "read_text", original_read)
    with pytest.raises(CtlError) as exc_info:
        store.load()
    assert exc_info.value.code == "CTL_RECOVERY_REQUIRED"


def test_route_plan_returns_exactly_one_action_without_registry_write(
    tmp_path: Path,
) -> None:
    request = _request("route-plan")
    request["payload"] = {"state": "developer_environment_pending", "proof": {}}
    request["payload_digest"] = canonical_digest(request["payload"])

    completed = _run_cli(tmp_path, request)
    output = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert output["next_action"] == {
        "kind": "observe_developer_environment",
        "target_role": "Developer",
    }
    assert not (tmp_path / "registry").exists()


def test_prepare_runs_authoritative_scan_and_fails_closed_on_dirty_primary(tmp_path: Path) -> None:
    repo = _git_repo(tmp_path)
    (repo / "README.md").write_text("dirty\n", encoding="utf-8")
    _seed_lane(tmp_path, state="authorized", primary_repo_root=str(repo))
    request = _request("prepare-dispatch")
    request.update(dry_run=False, repo_root=str(tmp_path))
    request["payload"] = {"state": "authorized", "proof": {}}
    request["payload_digest"] = canonical_digest(request["payload"])

    completed = _run_cli(tmp_path, request)
    output = json.loads(completed.stdout)

    assert output["code"] == "CTL_PRIMARY_DIRTY"
    assert output["next_action"] is None
    assert output["zero_write"] is True


def test_scan_rereads_frozen_authority_before_returning_one_action(
    tmp_path: Path,
) -> None:
    repo = _git_repo(tmp_path)
    authority = repo / "task.md"
    authority.write_text("authorized\n", encoding="utf-8")
    _git(repo, "add", "task.md")
    _git(repo, "commit", "-m", "authority")
    digest = hashlib.sha256(authority.read_bytes()).hexdigest()
    _seed_lane(
        tmp_path, state="authorized", authority_files={"task.md": digest},
        primary_repo_root=str(repo))
    request = _request("scan")
    request["repo_root"] = str(repo)
    request["payload"] = {
        "state": "planned", "proof": {"forged": True},
    }
    request["payload_digest"] = canonical_digest(request["payload"])

    completed = _run_cli(tmp_path, request)
    assert json.loads(completed.stdout)["next_action"]["kind"] == "create_developer_environment"

    authority.write_text("changed\n", encoding="utf-8")
    _git(repo, "add", "task.md")
    _git(repo, "commit", "-m", "changed authority")
    request["payload_digest"] = canonical_digest(request["payload"])
    stale = _run_cli(tmp_path, request)
    assert json.loads(stale.stdout)["code"] == "CTL_EVIDENCE_STALE"
