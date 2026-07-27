from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.connlab_controlled_lane.callbacks import callback_event_id
from scripts.connlab_controlled_lane.contracts import CtlError, canonical_digest
from scripts.connlab_controlled_lane.registry import RegistryStore

_AUTHORITY = {
    "role": "Developer", "evidence_path": "docs/evidence.md",
    "base_lane_head": "base", "allowed_changed_paths": ["docs/evidence.md"],
    "checkpoint_required": True, "nullable": False,
}
_TARGET = {
    "task_id": "TASK_1", "lane_id": "lane-1", "route_id": "route-1",
    "operation_id": "operation-1", "payload_digest": "external-payload",
    "action_kind": "create_developer_environment", "role": "Developer",
    "native_mode": "create_new", "saved_project_id": "project-1",
    "project_path": "C:/repo", "repository_fingerprint": "repo-1",
    "environment": "worktree", "starting_ref": "master",
    "expected_base_commit": "base", "expected_primary_head": "base",
    "scope_fingerprint": "scope-1", "owner_claims_digest": canonical_digest([]),
    "prompt_digest": "prompt", "client_request_digest": "request",
    "completion_authority_nullable": False,
    "expected_evidence_path": "docs/evidence.md", "base_lane_head": "base",
    "allowed_changed_paths": ["docs/evidence.md"], "checkpoint_required": True,
}
_RECEIPT = {"pendingWorktreeId": "pending-1"}
_EXACT = {
    **_TARGET, "thread_id": "thread-1", "pending_worktree_id": "pending-1",
    "worktree_path": "C:/lane", "branch": "codex/lane-1",
    "base_commit": "base", "head": "base", "git_common_dir": "C:/repo/.git",
    "project_binding_verified": True, "prompt_markers_verified": True,
    "worktree_clean": True, "index_clean": True,
    "path_unique": True, "branch_unique": True,
}


def _request(command: str, *, generation: int, key: str, operation: str = "operation-1",
             payload: dict[str, object] | None = None) -> dict[str, object]:
    body = payload or {
        "action_kind": "create_developer_environment",
        "current_state": "authorized",
        "expected_stage": "none",
        "target_binding": _TARGET,
    }
    return {
        "schema_version": 2, "command": command, "request_id": f"request-{key}",
        "task_id": "TASK_1", "lane_id": "lane-1",
        "expected_registry_generation": generation, "idempotency_key": key,
        "operation_id": operation, "route_id": "route-1",
        "scope_fingerprint": "scope-1", "payload": body,
        "payload_digest": canonical_digest(body),
    }


def test_partial_v2_registry_fails_closed(tmp_path: Path) -> None:
    root = tmp_path / "registry"
    root.mkdir()
    (root / "registry-v2.json").write_text(
        json.dumps({
            "schema_version": 2,
            "repository_fingerprint": "repo-1",
            "generation": 1,
        }),
        encoding="utf-8",
    )
    store = RegistryStore(root, repository_fingerprint="repo-1")

    with pytest.raises(CtlError) as exc_info:
        store.load()

    assert exc_info.value.code == "CTL_REGISTRY_SCHEMA_MISMATCH"


def _prepare(store: RegistryStore) -> dict[str, object]:
    _seed_lane(store)
    request = _request("prepare-dispatch", generation=0, key="prepare")
    return store.execute("prepare-dispatch", request)


def _seed_lane(
    store: RegistryStore, *, state: str = "authorized",
    proof: dict[str, object] | None = None,
) -> None:
    store.root.mkdir(parents=True, exist_ok=True)
    registry = store.load()
    registry["lanes"]["lane-1"] = {
        "state": state,
        "proof": {"completion_authority": _AUTHORITY, **(proof or {})},
        "scope_fingerprint": "scope-1", "requested_scope": {}, "owner_claims": [],
    }
    store._atomic_write(registry)


def _start(
    store: RegistryStore,
    *,
    generation: int = 1,
    key: str = "start",
    changed: bool = False,
) -> dict[str, object]:
    payload: dict[str, object] = {"expected_stage": "prepared"}
    if changed:
        payload["changed"] = True
    return store.execute(
        "mark-invocation-started",
        _request("mark-invocation-started", generation=generation, key=key, payload=payload),
    )


def _ack_payload(receipt: str | None = None) -> dict[str, object]:
    return {
        "expected_stage": "result_recorded",
        "receipt_digest": receipt or canonical_digest(_RECEIPT),
        "readback_binding": _EXACT, "readback_digest": canonical_digest(_EXACT),
        "readback_readable": True,
    }


def _acknowledge(store: RegistryStore) -> None:
    _prepare(store)
    _start(store)
    store.execute(
        "record-action-result",
        _request(
            "record-action-result", generation=2, key="result",
            payload={
                "expected_stage": "invocation_started",
                "result_stage": "result_recorded", "receipt": _RECEIPT,
                "receipt_digest": canonical_digest(_RECEIPT),
            },
        ),
    )
    store.execute(
        "ack-dispatch",
        _request(
            "ack-dispatch", generation=3, key="ack",
            payload=_ack_payload(),
        ),
    )


def _callback() -> dict[str, object]:
    payload = {
        "dispatch_operation_id": "operation-1",
        "task_id": "TASK_1", "lane_id": "lane-1", "route_id": "route-1",
        "operation_id": "operation-1", "role": "Developer", "thread_id": "thread-1",
        "worktree_path": "C:/lane", "payload_digest": "external-payload",
        "status": "ready_for_review", "evidence_path": "docs/evidence.md",
        "evidence_sha256": "evidence", "lane_head": "head",
    }
    payload["event_id"] = callback_event_id(payload)
    return payload


def test_mark_invocation_started_first_write_replay_and_zero_external_action(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[object] = []
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: calls.append(args))
    store = RegistryStore(tmp_path, repository_fingerprint="repo-1")
    _prepare(store)
    request = _request(
        "mark-invocation-started",
        generation=1,
        key="start",
        payload={"expected_stage": "prepared"},
    )

    first = store.execute("mark-invocation-started", request)
    replay = store.execute("mark-invocation-started", request)

    assert first["code"] == "CTL_OK"
    assert first["old_generation"] == 1
    assert first["new_generation"] == 2
    assert first["durable_stage"] == "invocation_started"
    assert replay["code"] == "CTL_ALREADY_APPLIED"
    assert store.load()["generation"] == 2
    assert first["facts"]["external_action_count"] == 0
    assert calls == []


@pytest.mark.parametrize(
    ("mode", "code", "generation"),
    [
        ("stale", "CTL_CAS_CONFLICT", 1),
        ("changed", "CTL_IDEMPOTENCY_CONFLICT", 2),
        ("wrong-stage", "CTL_DISPATCH_STAGE_MISMATCH", 2),
        ("cross-lane", "CTL_DISPATCH_ACK_MISMATCH", 1),
    ],
)
def test_mark_invocation_started_rejects_invalid_replay(
    tmp_path: Path, mode: str, code: str, generation: int
) -> None:
    store = RegistryStore(tmp_path, repository_fingerprint="repo-1")
    _prepare(store)
    if mode not in ("stale", "cross-lane"):
        _start(store)
    if mode == "stale":
        result = _start(store, generation=0)
    elif mode == "changed":
        result = _start(store, generation=2, changed=True)
    elif mode == "cross-lane":
        request = _request(
            "mark-invocation-started", generation=1, key="cross-lane")
        request["lane_id"] = "lane-2"
        result = store.execute("mark-invocation-started", request)
    else:
        result = _start(store, generation=2, key="start-again")

    assert result["code"] == code
    assert result["zero_write"] is True
    assert store.load()["generation"] == generation


def test_all_six_mutation_commands_have_direct_stage_and_replay_contracts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "scripts.connlab_controlled_lane.callbacks.completion_callback_result",
        lambda *_: ("complete", {"evidence_sha256": "evidence", "lane_head": "head"}),
    )
    store = RegistryStore(tmp_path, repository_fingerprint="repo-1")
    _seed_lane(store, proof={"developer_status": "complete"})
    callback = _callback()
    requests = [
        _request("prepare-dispatch", generation=0, key="prepare"),
        _request(
            "mark-invocation-started",
            generation=1,
            key="start",
            payload={"expected_stage": "prepared"},
        ),
        _request(
            "record-action-result",
            generation=2,
            key="result",
            payload={
                "expected_stage": "invocation_started",
                "result_stage": "result_recorded", "receipt": _RECEIPT,
                "receipt_digest": canonical_digest(_RECEIPT),
            },
        ),
        _request(
            "ack-dispatch",
            generation=3,
            key="ack",
            payload=_ack_payload(),
        ),
        _request(
            "advance-state",
            generation=4,
            key="advance",
            payload={
                "expected_stage": "acknowledged",
                "from_state": "developer_environment_pending",
                "to_state": "developer_active",
            },
        ),
        _request(
            "record-callback",
            generation=5,
            key="callback",
            operation="completion-1",
            payload=callback,
        ),
    ]

    for request in requests:
        first = store.execute(str(request["command"]), request)
        replay = store.execute(str(request["command"]), request)
        assert first["code"] == "CTL_OK"
        assert replay["code"] == "CTL_ALREADY_APPLIED"
        if request["command"] == "advance-state":
            assert "developer_status" not in store.load()["lanes"]["lane-1"]["proof"]
        if request["command"] == "record-action-result":
            assert store.load()["lanes"]["lane-1"]["state"] == (
                "developer_environment_pending")
        if request["command"] == "ack-dispatch":
            assert store.load()["dispatches"]["operation-1"]["target_binding"][
                "thread_id"] == "thread-1"

    final = store.load()
    assert final["generation"] == 6
    assert final["lanes"]["lane-1"]["state"] == "developer_active"
    assert final["callbacks"][callback["event_id"]]["completion_observation"][
        "lane_head"] == "head"


@pytest.mark.parametrize(
    ("mode", "code"),
    [
        ("late", "CTL_ROLE_CALLBACK_STATE_MISMATCH"),
        ("cross-gate", "CTL_ROLE_CALLBACK_STATE_MISMATCH"),
        ("cross-role", "CTL_ROLE_CALLBACK_STATE_MISMATCH"),
        ("cross-lane", "CTL_ROLE_CALLBACK_STATE_MISMATCH"),
        ("stale-generation", "CTL_CAS_CONFLICT"),
    ],
)
def test_record_callback_rejects_stale_or_cross_gate_attribution_zero_write(
    tmp_path: Path, mode: str, code: str
) -> None:
    store = RegistryStore(tmp_path, repository_fingerprint="repo-1")
    _acknowledge(store)
    advance = {"from_state": "developer_environment_pending",
               "to_state": "developer_active"}
    assert store.execute("advance-state", _request(
        "advance-state", generation=4, key="advance", payload=advance))["code"] == "CTL_OK"
    registry = store.load()
    callback = _callback()
    if mode == "late":
        registry["role_bindings"]["lane-1:Developer"]["status"] = "completion_recorded"
    elif mode == "cross-gate":
        registry["lanes"]["lane-1"]["state"] = "review_pending"
    elif mode == "cross-role":
        callback["role"] = "Reviewer"
    elif mode == "cross-lane":
        callback["lane_id"] = "lane-2"
    store._atomic_write(registry)
    callback["event_id"] = callback_event_id(callback)
    generation = 4 if mode == "stale-generation" else 5
    request = _request("record-callback", generation=generation, key=mode,
                       operation="completion-1", payload=callback)

    result = store.execute("record-callback", request)

    assert result["code"] == code
    assert result["zero_write"] is True
    assert store.load()["generation"] == 5
    assert store.load()["callbacks"] == {}
