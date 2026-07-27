from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from scripts.connlab_controlled_lane.callbacks import (
    callback_event_id,
    validate_completion_callback,
)
from scripts.connlab_controlled_lane.contracts import CtlError, canonical_digest
from scripts.connlab_controlled_lane.git_preflight import (
    inspect_git,
    preflight_adopt,
    preflight_create,
    preflight_retire,
    registry_closeout_gates,
)
from scripts.connlab_controlled_lane.registry import RegistryStore


def _git(path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "master")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "fixture")
    return repo


def test_disposable_git_create_preflight_is_read_only(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    branch = "lane/test"
    target = tmp_path / "worktrees" / "test"
    before = _git(repo, "show-ref")
    head = _git(repo, "rev-parse", "HEAD")

    result = preflight_create(
        repo,
        branch=branch,
        target=target,
        base_ref=head,
        expected_primary_head=head,
    )

    assert result["code"] == "CTL_OK"
    assert result["zero_write"] is True
    assert _git(repo, "show-ref") == before
    assert not target.exists()


def test_dirty_primary_fails_closed(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "README.md").write_text("dirty\n", encoding="utf-8")

    result = preflight_create(
        repo,
        branch="lane/test",
        target=tmp_path / "lane",
        base_ref="HEAD",
        expected_primary_head=_git(repo, "rev-parse", "HEAD"),
    )

    assert result["code"] == "CTL_PRIMARY_DIRTY"
    assert result["zero_write"] is True


def test_retire_preflight_rejects_unintegrated_head(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _git(repo, "checkout", "-b", "lane/test")
    (repo / "lane.txt").write_text("lane\n", encoding="utf-8")
    _git(repo, "add", "lane.txt")
    _git(repo, "commit", "-m", "lane")

    result = preflight_retire(
        repo,
        integration_ref="master",
        closeout_gates={
            "residuals_clear": True,
            "owners_released": True,
            "callbacks_clear": True,
            "recovery_clear": True,
            "active_tasks_clear": True,
            "primary_clean": True,
        },
    )

    assert result["code"] == "CTL_UNINTEGRATED_HEAD"
    assert inspect_git(repo)["branch"] == "lane/test"


def test_adopt_requires_common_dir_base_and_scope_binding(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    head = _git(repo, "rev-parse", "HEAD")
    facts = inspect_git(repo)

    result = preflight_adopt(
        repo,
        expected_branch="master",
        expected_head=head,
        expected_common_dir=facts["git_common_dir"],
        expected_base=head,
        expected_scope_fingerprint="scope-1",
        observed_scope_fingerprint="wrong",
    )

    assert result["code"] == "CTL_WORKTREE_MISMATCH"
    assert result["zero_write"] is True


def test_retire_requires_all_closeout_gates(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    result = preflight_retire(
        repo,
        integration_ref="master",
        closeout_gates={
            "residuals_clear": True,
            "owners_released": False,
            "callbacks_clear": True,
            "recovery_clear": True,
            "active_tasks_clear": True,
            "primary_clean": True,
        },
    )

    assert result["code"] == "CTL_RECOVERY_REQUIRED"
    assert result["zero_write"] is True


def test_retire_checks_actual_primary_worktree_cleanliness(tmp_path: Path) -> None:
    (tmp_path / "lane").mkdir()
    (tmp_path / "primary").mkdir()
    lane = _repo(tmp_path / "lane")
    primary = _repo(tmp_path / "primary")
    (primary / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    result = preflight_retire(
        lane, integration_ref="master", primary_repo=primary,
        closeout_gates={
            "residuals_clear": True, "owners_released": True,
            "callbacks_clear": True, "recovery_clear": True,
            "active_tasks_clear": True,
        })

    assert result["code"] == "CTL_RECOVERY_REQUIRED"
    assert result["facts"]["primary"]["status"]
    lane_facts = inspect_git(lane)
    topology = {
        "branch": "wrong", "head": lane_facts["head"],
        "git_common_dir": lane_facts["git_common_dir"],
        "base_commit": lane_facts["head"], "scope_fingerprint": "scope-1",
    }
    mismatch = preflight_retire(
        lane, integration_ref="master", primary_repo=lane,
        closeout_gates={
            "residuals_clear": True, "owners_released": True,
            "callbacks_clear": True, "recovery_clear": True,
            "active_tasks_clear": True,
        },
        expected_topology=topology)
    assert mismatch["code"] == "CTL_WORKTREE_MISMATCH"


def test_retire_gates_derive_from_registry_facts() -> None:
    registry = {
        "lanes": {"lane-1": {"closeout": {
            "residual_ledger_status": "resolved",
            "residual_ledger_digest": "ledger",
        }}},
        "shared_owners": {}, "callbacks": {}, "recovery_points": {},
        "role_bindings": {},
    }

    assert registry_closeout_gates(registry, "lane-1") == {
        "residuals_clear": True, "owners_released": True,
        "callbacks_clear": True, "recovery_clear": True,
        "active_tasks_clear": True,
    }
    registry["shared_owners"]["path:x"] = {"lane_id": "lane-1"}
    assert registry_closeout_gates(registry, "lane-1")["owners_released"] is False


def _callback_fixture(repo: Path, *, nullable: bool = False) -> tuple[dict, dict, dict]:
    evidence = repo / "docs" / "evidence.md"
    evidence.parent.mkdir(exist_ok=True)
    evidence.write_text("before\n", encoding="utf-8")
    _git(repo, "add", "docs/evidence.md")
    _git(repo, "commit", "-m", "evidence base")
    base = _git(repo, "rev-parse", "HEAD")
    evidence.write_text("reviewed\n", encoding="utf-8")
    _git(repo, "add", "docs/evidence.md")
    _git(repo, "commit", "-m", "reviewed")
    head = _git(repo, "rev-parse", "HEAD")
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    target = {
        "task_id": "TASK_1", "lane_id": "lane-1", "route_id": "route-1",
        "operation_id": "operation-1", "role": "Reviewer", "thread_id": "thread-1",
        "worktree_path": str(repo), "payload_digest": "payload-1",
        "completion_authority_nullable": nullable,
        "expected_evidence_path": None if nullable else "docs/evidence.md",
        "base_lane_head": None if nullable else base,
        "allowed_changed_paths": [] if nullable else ["docs/evidence.md"],
        "checkpoint_required": not nullable,
    }
    dispatch = {
        "task_id": "TASK_1", "lane_id": "lane-1", "route_id": "route-1",
        "operation_id": "operation-1", "target_binding": target,
        "state_advance_payload": {"to_state": "review_pending"},
    }
    registry = {"lanes": {"lane-1": {"state": "review_pending"}},
                "role_bindings": {"lane-1:Reviewer": {**target, "status": "active"}}}
    return registry, dispatch, target


def test_callback_binds_actual_evidence_digest_and_lane_head(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    registry, dispatch, target = _callback_fixture(repo)
    payload = {
        **target, "status": "reviewer_pass",
        "evidence_path": target["expected_evidence_path"],
        "evidence_sha256": hashlib.sha256(
            (repo / "docs" / "evidence.md").read_bytes()).hexdigest(),
        "lane_head": _git(repo, "rev-parse", "HEAD"),
    }
    payload["event_id"] = callback_event_id(payload)
    assert validate_completion_callback(registry, dispatch, payload) == "passed"

    for field, value in (
        ("evidence_path", "docs/wrong.md"),
        ("evidence_sha256", "0" * 64),
        ("lane_head", "f" * 40),
    ):
        with pytest.raises(CtlError) as exc_info:
            validate_completion_callback(registry, dispatch, {**payload, field: value})
        assert exc_info.value.code == "CTL_CALLBACK_CONFLICT"
    (repo / "docs" / "evidence.md").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(CtlError) as exc_info:
        validate_completion_callback(registry, dispatch, payload)
    assert exc_info.value.code == "CTL_CALLBACK_CONFLICT"


def test_user_approval_allows_only_explicit_null_completion_authority(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    registry, dispatch, target = _callback_fixture(repo, nullable=True)
    target["role"] = "User"
    registry["role_bindings"] = {"lane-1:User": {**target, "status": "active"}}
    payload = {**target, "status": "user_approved",
               "evidence_path": None, "evidence_sha256": None, "lane_head": None}
    assert validate_completion_callback(registry, dispatch, payload) == "approved"
    with pytest.raises(CtlError) as exc_info:
        validate_completion_callback(
            registry, dispatch, {**payload, "evidence_path": "docs/fake.md"})
    assert exc_info.value.code == "CTL_CALLBACK_CONFLICT"


@pytest.mark.parametrize(
    ("claim", "scope", "held"),
    [
        ({"key": "path:backend/api/x.py", "paths": ["backend/api/x.py"]},
         {"paths": ["backend/api/x.py"]},
         {"key": "path:backend/api/x.py", "paths": ["backend/api/x.py"]}),
        ({"key": "directory:backend/api", "directories": ["backend/api"]},
         {"directories": ["backend/api"]},
         {"key": "directory:backend", "directories": ["backend"]}),
        ({"key": "authority:matrix.method", "authorities": ["matrix.method"]},
         {"authorities": ["matrix.method"]},
         {"key": "authority:matrix", "authorities": ["matrix"]}),
    ],
)
def test_owner_acquisition_rechecks_interleaved_latest_registry(
    tmp_path: Path, claim: dict, scope: dict, held: dict
) -> None:
    store = RegistryStore(tmp_path / "registry", repository_fingerprint="repo-1")
    store.root.mkdir()
    registry = store.load()
    registry["lanes"]["lane-a"] = {
        "state": "authorized", "scope_fingerprint": "scope-a",
        "requested_scope": scope, "owner_claims": [claim],
        "proof": {"completion_authority": {
            "role": "Developer", "evidence_path": "docs/evidence.md",
            "base_lane_head": "base", "allowed_changed_paths": ["docs/evidence.md"],
            "checkpoint_required": True, "nullable": False,
        }},
    }
    store._atomic_write(registry)
    target = {
        "task_id": "TASK_A", "lane_id": "lane-a", "route_id": "route-a",
        "operation_id": "operation-a", "payload_digest": "payload-a",
        "action_kind": "create_developer_environment", "role": "Developer",
        "native_mode": "create_new", "saved_project_id": "project-a",
        "project_path": "C:/repo", "repository_fingerprint": "repo-1",
        "environment": "worktree", "starting_ref": "master",
        "expected_base_commit": "base", "expected_primary_head": "base",
        "scope_fingerprint": "scope-a", "prompt_digest": "prompt",
        "client_request_digest": "request",
        "owner_claims_digest": canonical_digest([claim]),
        "completion_authority_nullable": False,
        "expected_evidence_path": "docs/evidence.md", "base_lane_head": "base",
        "allowed_changed_paths": ["docs/evidence.md"], "checkpoint_required": True,
    }
    prepare_payload = {
        "current_state": "authorized", "action_kind": "create_developer_environment",
        "target_binding": target,
    }
    request = {
        "schema_version": 2, "command": "prepare-dispatch", "request_id": "prepare",
        "task_id": "TASK_A", "lane_id": "lane-a", "operation_id": "operation-a",
        "route_id": "route-a", "scope_fingerprint": "scope-a",
        "expected_registry_generation": 0, "idempotency_key": "prepare",
        "payload": prepare_payload, "payload_digest": canonical_digest(prepare_payload),
    }
    assert store.execute("prepare-dispatch", request)["code"] == "CTL_OK"
    latest = store.load()
    receipt = {"pendingWorktreeId": "pending-a"}
    dispatch = latest["dispatches"]["operation-a"]
    dispatch["stage"] = "result_recorded"
    dispatch["action_result_payload"] = {
        "receipt": receipt, "receipt_digest": canonical_digest(receipt)}
    latest["lanes"]["lane-a"]["state"] = "developer_environment_pending"
    latest["shared_owners"][held["key"]] = {**held, "lane_id": "lane-b"}
    latest["generation"] = 2
    store._atomic_write(latest)
    exact = {
        **target, "thread_id": "thread-a", "pending_worktree_id": "pending-a",
        "worktree_path": "C:/lane-a", "branch": "codex/lane-a",
        "base_commit": "base", "head": "base", "git_common_dir": "C:/repo/.git",
        "project_binding_verified": True, "prompt_markers_verified": True,
        "worktree_clean": True, "index_clean": True, "path_unique": True,
        "branch_unique": True,
    }
    ack_payload = {
        "receipt_digest": canonical_digest(receipt),
        "readback_binding": exact, "readback_digest": canonical_digest(exact),
        "readback_readable": True,
    }
    ack = {**request, "command": "ack-dispatch", "request_id": "ack",
           "idempotency_key": "ack", "payload": ack_payload,
           "payload_digest": canonical_digest(ack_payload)}
    assert store.execute("ack-dispatch", {**ack,
        "expected_registry_generation": 1})["code"] == "CTL_CAS_CONFLICT"
    result = store.execute("ack-dispatch", {**ack, "expected_registry_generation": 2})
    assert result["code"] == "CTL_OWNER_CONFLICT"
    assert store.load()["shared_owners"][held["key"]]["lane_id"] == "lane-b"
