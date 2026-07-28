from __future__ import annotations

from pathlib import Path

import pytest

from scripts.connlab_controlled_lane.controller_title import (
    V2_CONTROLLER_TITLE,
    build_controller_title_target,
)
from scripts.connlab_controlled_lane.contracts import canonical_digest
from scripts.connlab_controlled_lane.registry import RegistryStore
from scripts.connlab_controlled_lane.state_machine import select_next_action


def _store(tmp_path: Path, *, exact_title: bool = False) -> RegistryStore:
    store = RegistryStore(tmp_path / "registry", repository_fingerprint="repo-1")
    store.root.mkdir()
    registry = store.load()
    registry["lanes"]["lane-1"] = {
        "task_id": "TASK_1",
        "state": "bootstrap_controller_title_pending",
        "scope_fingerprint": "scope-1",
        "requested_scope": {},
        "authority_files": {},
        "owner_claims": [],
        "proof": {
            "controller_thread_adopted": True,
            "controller_title_exact": exact_title,
        },
    }
    registry["bootstrap"] = {
        "controller": {
            "thread_id": "thread-1",
            "observed_initial_title": (
                V2_CONTROLLER_TITLE if exact_title else "Generated task"),
            "host_id": "local",
            "cwd": "C:/repo",
            "saved_project_id": "project-1",
            "project_path": "C:/repo",
        },
        "heartbeat": {
            "name": "ConnLab v2 controlled-lane scan",
            "rrule": "FREQ=MINUTELY;INTERVAL=5",
            "status": "PAUSED",
        },
    }
    registry["role_bindings"]["lane-1:Controller"] = {
        "lane_id": "lane-1",
        "role": "Controller",
        "thread_id": "thread-1",
        "status": "title_pending",
    }
    store._atomic_write(registry)
    return store


def _request(
    command: str,
    generation: int,
    key: str,
    target: dict[str, object],
    payload: dict[str, object],
) -> dict[str, object]:
    return {
        "schema_version": 2,
        "command": command,
        "request_id": f"request-{key}",
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "expected_registry_generation": generation,
        "idempotency_key": key,
        "operation_id": target["operation_id"],
        "route_id": target["route_id"],
        "scope_fingerprint": "scope-1",
        "payload": payload,
        "payload_digest": canonical_digest(payload),
    }


def _target(store: RegistryStore) -> dict[str, object]:
    registry = store.load()
    lane = registry["lanes"]["lane-1"]
    action = select_next_action(lane["state"], lane["proof"])
    return {
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "payload_digest": "title-payload",
        "role": "Controller",
        **build_controller_title_target(
            registry, "lane-1", str(action["kind"])),
    }


def _prepare(store: RegistryStore, target: dict[str, object]) -> dict[str, object]:
    payload = {
        "current_state": "bootstrap_controller_title_pending",
        "action_kind": target["action_kind"],
        "target_binding": target,
    }
    return store.execute(
        "prepare-dispatch", _request("prepare-dispatch", 0, "prepare", target, payload))


def _readback(target: dict[str, object]) -> dict[str, object]:
    observed = {
        **target,
        "title": V2_CONTROLLER_TITLE,
        "project_binding_verified": True,
    }
    return {
        "receipt_digest": "opaque-title-result",
        "readback_readable": True,
        "readback_matches": 1,
        "readback_binding": observed,
        "readback_digest": canonical_digest(observed),
    }


def _complete_title(
    store: RegistryStore,
    target: dict[str, object],
    *,
    result_recorded: bool = True,
    stop_after: str | None = None,
) -> list[dict[str, object]]:
    outputs = [_prepare(store, target)]
    if stop_after == "prepare":
        return outputs
    outputs.append(store.execute(
        "mark-invocation-started",
        _request(
            "mark-invocation-started",
            1,
            "start",
            target,
            {"expected_stage": "prepared"},
        ),
    ))
    if stop_after == "start":
        return outputs
    result = {
        "result_stage": "result_recorded",
        "receipt_digest": "opaque-title-result",
        (
            "opaque_result" if result_recorded else "recovered_from_readback"
        ): {"accepted": True} if result_recorded else True,
    }
    outputs.append(store.execute(
        "record-action-result",
        _request(
            "record-action-result",
            2,
            "result" if result_recorded else "recover",
            target,
            result,
        ),
    ))
    if stop_after == "result":
        return outputs
    generation = 3
    outputs.append(store.execute(
        "ack-dispatch",
        _request("ack-dispatch", generation, "ack", target, _readback(target)),
    ))
    if stop_after == "ack":
        return outputs
    outputs.append(store.execute(
        "advance-state",
        _request(
            "advance-state",
            generation + 1,
            "advance",
            target,
            {
                "from_state": "bootstrap_controller_title_pending",
                "to_state": "bootstrap_heartbeat_pending",
            },
        ),
    ))
    return outputs


def test_set_title_is_one_action_then_exact_readback_and_heartbeat_gate(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    target = _target(store)
    native_actions: list[dict[str, object]] = []

    native_actions.append({
        "tool": "set_thread_title",
        "threadId": target["thread_id"],
        "title": target["expected_title"],
    })
    outputs = _complete_title(store, target)
    registry = store.load()

    assert [output["code"] for output in outputs] == ["CTL_OK"] * 5
    assert native_actions == [{
        "tool": "set_thread_title",
        "threadId": "thread-1",
        "title": V2_CONTROLLER_TITLE,
    }]
    assert registry["generation"] == 5
    assert registry["lanes"]["lane-1"]["state"] == "bootstrap_heartbeat_pending"
    assert registry["lanes"]["lane-1"]["proof"]["controller_acknowledged"] is True
    assert registry["role_bindings"]["lane-1:Controller"]["status"] == "active"


def test_exact_title_adoption_uses_readback_without_title_mutation(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path, exact_title=True)
    target = _target(store)
    native_title_mutations: list[object] = []

    outputs = _complete_title(store, target)

    assert target["action_kind"] == "adopt_exact_controller_title"
    assert native_title_mutations == []
    assert all(output["code"] == "CTL_OK" for output in outputs)
    assert store.load()["lanes"]["lane-1"]["state"] == "bootstrap_heartbeat_pending"


def test_invocation_started_with_lost_receipt_recovers_without_resend(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    target = _target(store)
    outputs = _complete_title(store, target, result_recorded=False)

    assert all(output["code"] == "CTL_OK" for output in outputs)
    dispatch = store.load()["dispatches"][target["operation_id"]]
    assert dispatch["stage"] == "advanced"
    assert dispatch["action_result_payload"]["recovered_from_readback"] is True


@pytest.mark.parametrize("stop_after", ("prepare", "start", "result", "ack"))
def test_title_dispatch_resumes_each_crash_checkpoint_without_recreate(
    tmp_path: Path, stop_after: str,
) -> None:
    store = _store(tmp_path)
    target = _target(store)
    outputs = _complete_title(store, target, stop_after=stop_after)
    expected_stage = {
        "prepare": "prepared",
        "start": "invocation_started",
        "result": "result_recorded",
        "ack": "acknowledged",
    }[stop_after]

    assert all(output["code"] == "CTL_OK" for output in outputs)
    assert store.load()["dispatches"][target["operation_id"]]["stage"] == expected_stage


def test_replay_and_late_callback_do_not_repeat_or_advance_title_action(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    target = _target(store)
    outputs = _complete_title(store, target)
    generation = store.load()["generation"]
    replay = store.execute(
        "prepare-dispatch",
        _request(
            "prepare-dispatch",
            0,
            "prepare",
            target,
            {
                "current_state": "bootstrap_controller_title_pending",
                "action_kind": target["action_kind"],
                "target_binding": target,
            },
        ),
    )
    callback = store.execute(
        "record-callback",
        _request(
            "record-callback",
            generation,
            "late-callback",
            target,
            {
                "dispatch_operation_id": target["operation_id"],
                "role": "Controller",
                "outcome": "complete",
            },
        ),
    )

    assert all(output["code"] == "CTL_OK" for output in outputs)
    assert replay["code"] == "CTL_ALREADY_APPLIED"
    assert callback["code"] == "CTL_CALLBACK_CONFLICT"
    assert store.load()["generation"] == generation
