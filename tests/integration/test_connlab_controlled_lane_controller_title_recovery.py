from __future__ import annotations

from pathlib import Path

import pytest

from scripts.connlab_controlled_lane.controller_title import (
    V2_CONTROLLER_TITLE,
    build_controller_title_target,
)
from scripts.connlab_controlled_lane.contracts import canonical_digest
from scripts.connlab_controlled_lane.git_preflight import verified_recovery_decision
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
        "requested_scope": {}, "authority_files": {}, "owner_claims": [],
        "proof": {
            "controller_thread_adopted": True,
            "controller_title_exact": exact_title},
    }
    registry["bootstrap"] = {
        "controller": {
            "thread_id": "thread-1",
            "observed_initial_title": (
                V2_CONTROLLER_TITLE if exact_title else "Generated task"),
            "host_id": "local", "cwd": "C:/repo",
            "saved_project_id": "project-1", "project_path": "C:/repo",
        },
        "heartbeat": {
            "name": "ConnLab v2 controlled-lane scan",
            "rrule": "FREQ=MINUTELY;INTERVAL=5",
            "status": "PAUSED"},
    }
    registry["role_bindings"]["lane-1:Controller"] = {
        "lane_id": "lane-1", "role": "Controller",
        "thread_id": "thread-1",
        "status": "title_pending"}
    store._atomic_write(registry)
    return store


def _request(
    command: str, generation: int, key: str,
    target: dict[str, object], payload: dict[str, object],
) -> dict[str, object]:
    return {
        "schema_version": 2, "command": command,
        "request_id": f"request-{key}",
        "task_id": "TASK_1", "lane_id": "lane-1",
        "expected_registry_generation": generation,
        "idempotency_key": key,
        "operation_id": target["operation_id"],
        "route_id": target["route_id"],
        "scope_fingerprint": "scope-1",
        "payload": payload, "payload_digest": canonical_digest(payload),
    }


def _target(store: RegistryStore) -> dict[str, object]:
    registry = store.load()
    lane = registry["lanes"]["lane-1"]
    action = select_next_action(lane["state"], lane["proof"])
    return {
        "task_id": "TASK_1", "lane_id": "lane-1",
        "payload_digest": "title-payload", "role": "Controller",
        **build_controller_title_target(registry, "lane-1", str(action["kind"])),
    }


class _Scenario:
    def __init__(self, tmp_path: Path, *, exact_title: bool = False) -> None:
        self.store = _store(tmp_path, exact_title=exact_title)
        self.target = _target(self.store)
        self.native_scans: list[list[dict[str, object]]] = []
        self.last_recovery: dict[str, object] | None = None

    def reopen(self) -> None:
        self.store = RegistryStore(
            self.store.root, repository_fingerprint="repo-1")

    def _write(self, command: str, payload: dict[str, object]) -> dict[str, object]:
        generation = self.store.load()["generation"]
        output = self.store.execute(command, _request(
            command, generation, f"{command}-{generation}", self.target, payload))
        assert output["code"] == "CTL_OK"
        assert output["old_generation"] == generation
        assert output["new_generation"] == generation + 1
        return output

    def prepare_payload(self) -> dict[str, object]:
        return {
            "current_state": "bootstrap_controller_title_pending",
            "action_kind": self.target["action_kind"],
            "target_binding": self.target,
        }

    def prepare(self) -> None:
        self._write("prepare-dispatch", self.prepare_payload())

    def start(self) -> None:
        self._write(
            "mark-invocation-started", {"expected_stage": "prepared"})

    def set_title(self, *, receipt_lost: bool = False) -> str | None:
        action = {
            "tool": "set_thread_title",
            "threadId": self.target["thread_id"],
            "title": self.target["expected_title"],
        }
        self.native_scans.append([action])
        return None if receipt_lost else canonical_digest(action)

    def read_thread(self, receipt: str | None = None) -> dict[str, object]:
        self.native_scans.append([{
            "tool": "read_thread", "threadId": self.target["thread_id"]}])
        observed = {
            **self.target,
            "title": V2_CONTROLLER_TITLE,
            "project_binding_verified": True,
        }
        digest = canonical_digest(observed)
        return {
            "receipt_digest": receipt or digest,
            "readback_readable": True,
            "readback_matches": 1,
            "readback_binding": observed,
            "readback_digest": digest,
        }

    def result(self, receipt: str, *, recovered: bool = False) -> None:
        payload: dict[str, object] = {
            "result_stage": "result_recorded",
            "receipt_digest": receipt,
        }
        payload["recovered_from_readback" if recovered else "opaque_result"] = (
            True if recovered else {"accepted": True})
        self._write("record-action-result", payload)

    def ack(self, readback: dict[str, object]) -> None:
        self._write("ack-dispatch", readback)

    def advance(self) -> None:
        self._write("advance-state", {
            "from_state": "bootstrap_controller_title_pending",
            "to_state": "bootstrap_heartbeat_pending",
        })

    def reach(self, checkpoint: str) -> None:
        self.prepare()
        if checkpoint == "prepare":
            return
        self.start()
        receipt = self.set_title(receipt_lost=checkpoint == "start")
        if checkpoint == "start":
            return
        assert receipt is not None
        self.result(receipt)
        if checkpoint == "result":
            return
        self.ack(self.read_thread(receipt))

    def resume(self, checkpoint: str) -> None:
        dispatch = self.store.load()["dispatches"][self.target["operation_id"]]
        if checkpoint == "ack":
            self.advance()
            return
        if checkpoint == "prepare":
            self.start()
            receipt = self.set_title()
            assert receipt is not None
            self.result(receipt)
        elif checkpoint == "start":
            readback = self.read_thread()
            self.last_recovery = verified_recovery_decision(dispatch, readback)
            assert self.last_recovery == {
                "code": "CTL_OK", "action": "adopt_exact_match", "resend": False}
            self.result(str(readback["receipt_digest"]), recovered=True)
        receipt = self.store.load()["dispatches"][self.target["operation_id"]].get(
            "action_result_payload", {}).get("receipt_digest")
        readback = locals().get("readback") or self.read_thread(str(receipt))
        self.ack(readback)
        self.advance()


def test_exact_title_adoption_uses_readback_without_title_mutation(
    tmp_path: Path,
) -> None:
    scenario = _Scenario(tmp_path, exact_title=True)
    scenario.prepare()
    scenario.start()
    readback = scenario.read_thread()
    scenario.result(str(readback["receipt_digest"]))
    scenario.ack(readback)
    scenario.advance()

    assert scenario.target["action_kind"] == "adopt_exact_controller_title"
    assert scenario.native_scans == [[{
        "tool": "read_thread", "threadId": "thread-1"}]]
    assert scenario.store.load()["generation"] == 5
    assert scenario.store.load()["lanes"]["lane-1"]["state"] == (
        "bootstrap_heartbeat_pending")


def test_invocation_started_with_lost_receipt_recovers_without_resend(
    tmp_path: Path,
) -> None:
    scenario = _Scenario(tmp_path)
    scenario.reach("start")
    assert scenario.store.load()["generation"] == 2
    assert "action_result_payload" not in scenario.store.load()["dispatches"][
        scenario.target["operation_id"]]
    scenario.reopen()
    scenario.resume("start")
    dispatch = scenario.store.load()["dispatches"][scenario.target["operation_id"]]

    assert scenario.last_recovery == {
        "code": "CTL_OK", "action": "adopt_exact_match", "resend": False}
    assert [scan[0]["tool"] for scan in scenario.native_scans] == [
        "set_thread_title", "read_thread"]
    assert scenario.store.load()["generation"] == 5
    assert dispatch["stage"] == "advanced"
    assert dispatch["action_result_payload"]["recovered_from_readback"] is True


@pytest.mark.parametrize("stop_after", ("prepare", "start", "result", "ack"))
def test_title_dispatch_resumes_each_crash_checkpoint_without_recreate(
    tmp_path: Path, stop_after: str,
) -> None:
    scenario = _Scenario(tmp_path)
    scenario.reach(stop_after)
    expected_stage = {
        "prepare": "prepared",
        "start": "invocation_started",
        "result": "result_recorded",
        "ack": "acknowledged",
    }[stop_after]
    expected_generation = {"prepare": 1, "start": 2, "result": 3, "ack": 4}
    assert scenario.store.load()["dispatches"][
        scenario.target["operation_id"]]["stage"] == expected_stage
    assert scenario.store.load()["generation"] == expected_generation[stop_after]

    scenario.reopen()
    scenario.resume(stop_after)
    registry = scenario.store.load()
    tools = [scan[0]["tool"] for scan in scenario.native_scans]

    assert registry["generation"] == 5
    assert registry["lanes"]["lane-1"]["state"] == "bootstrap_heartbeat_pending"
    assert registry["bootstrap"]["controller"]["thread_id"] == "thread-1"
    assert tools.count("create_thread") == 0
    assert tools.count("set_thread_title") == 1
    assert tools.count("read_thread") == 1
    assert all(len(scan) <= 1 for scan in scenario.native_scans)


def test_replay_and_late_callback_do_not_repeat_or_advance_title_action(
    tmp_path: Path,
) -> None:
    scenario = _Scenario(tmp_path)
    scenario.reach("ack")
    scenario.reopen()
    scenario.resume("ack")
    generation = scenario.store.load()["generation"]
    replay = scenario.store.execute(
        "prepare-dispatch",
        _request(
            "prepare-dispatch",
            0,
            "prepare-dispatch-0",
            scenario.target,
            scenario.prepare_payload(),
        ),
    )
    callback = scenario.store.execute(
        "record-callback",
        _request(
            "record-callback",
            generation,
            "late-callback",
            scenario.target,
            {
                "dispatch_operation_id": scenario.target["operation_id"],
                "role": "Controller",
                "outcome": "complete",
            },
        ),
    )

    assert replay["code"] == "CTL_ALREADY_APPLIED"
    assert callback["code"] == "CTL_CALLBACK_CONFLICT"
    assert scenario.store.load()["generation"] == generation
