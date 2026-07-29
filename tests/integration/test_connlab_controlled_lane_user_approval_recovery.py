from __future__ import annotations

from pathlib import Path

import pytest

from scripts.connlab_controlled_lane.approval_authority import build_approval_target
from scripts.connlab_controlled_lane.callbacks import callback_event_id
from scripts.connlab_controlled_lane.contracts import ALL_CODES, MUTATION_COMMANDS, canonical_digest
from scripts.connlab_controlled_lane.registry import RegistryStore
from scripts.connlab_controlled_lane.state_machine import select_next_action


class ApprovalScenario:
    def __init__(self, tmp_path: Path, state: str = "plan_review_pending",
                 generation: int = 0) -> None:
        self.store = RegistryStore(tmp_path / "registry", repository_fingerprint="repo-1")
        self.store.root.mkdir(parents=True)
        registry = self.store.load()
        registry["generation"] = generation
        registry["bootstrap"] = {"controller": {"thread_id": "controller-1"}}
        registry["role_bindings"]["bootstrap-lane:Controller"] = {
            "lane_id": "bootstrap-lane", "role": "Controller",
            "thread_id": "controller-1", "status": "active",
        }
        proof = {
            "review_status": "passed", "readiness_status": "passed",
            "developer_thread_id": "developer-1", "developer_worktree_path": "C:/lane",
            "planner_thread_id": "planner-1", "planner_worktree_path": "C:/primary",
        }
        registry["lanes"]["lane-1"] = {
            "task_id": "TASK_1", "state": state, "scope_fingerprint": "scope-1",
            "requested_scope": {"paths": ["tests/unit/approval.py"]},
            "authority_files": {"task.md": "sha-1"}, "owner_claims": [], "proof": proof,
        }
        self.store._atomic_write(registry)
        self.target = build_approval_target(
            registry,
            "lane-1",
            {
                "task_id": "TASK_1", "lane_id": "lane-1",
                "route_id": "route-1", "operation_id": "approval-1",
                "scope_fingerprint": "scope-1",
            },
        )

    def write(self, command: str, payload: dict[str, object], *,
              operation: str = "approval-1",
              key: str | None = None,
              expected_generation: int | None = None) -> dict[str, object]:
        current = self.store.load()["generation"]
        generation = current if expected_generation is None else expected_generation
        idempotency_key = key or f"{command}-{generation}"
        request = {
            "schema_version": 2, "command": command,
            "request_id": f"request-{idempotency_key}",
            "task_id": "TASK_1", "lane_id": "lane-1",
            "expected_registry_generation": generation,
            "idempotency_key": idempotency_key,
            "operation_id": operation, "route_id": "route-1",
            "scope_fingerprint": "scope-1",
            "payload": payload, "payload_digest": canonical_digest(payload),
        }
        return self.store.execute(command, request)

    def prepare(self) -> dict[str, object]:
        return self.write(
            "prepare-dispatch",
            {
                "current_state": self.target["expected_from_state"],
                "action_kind": "request_user_approval",
                "target_binding": self.target,
            },
        )

    def start(self) -> dict[str, object]:
        return self.write("mark-invocation-started", {"expected_stage": "prepared"})

    def result(self) -> dict[str, object]:
        return self.write(
            "record-action-result",
            {"expected_stage": "invocation_started",
             "result_stage": "result_recorded",
             "receipt_digest": "receipt-1"})

    def ack(self) -> dict[str, object]:
        return self.write(
            "ack-dispatch",
            {"receipt_digest": "receipt-1",
             "readback_binding": self.target,
             "readback_digest": canonical_digest(self.target)})

    def advance(self) -> dict[str, object]:
        return self.write(
            "advance-state",
            {"from_state": self.target["expected_from_state"],
             "to_state": self.target["expected_pending_state"]})

    def callback(self, *, key: str = "approval-callback",
                 expected_generation: int | None = None,
                 **changed: object) -> dict[str, object]:
        payload: dict[str, object] = {
            "dispatch_operation_id": "approval-1",
            "task_id": "TASK_1",
            "lane_id": "lane-1",
            "role": "User",
            "status": "user_approved",
            "route_id": "route-1",
            "operation_id": "approval-1",
            "thread_id": "controller-1",
            "controller_thread_id": "controller-1",
            "scope_fingerprint": "scope-1",
            "approval_gate": self.target["approval_gate"],
            "approval_scope_digest": self.target["approval_scope_digest"],
            "payload_digest": self.target["request_payload_digest"],
            "evidence_path": None,
            "evidence_sha256": None,
            "lane_head": None,
            **changed,
        }
        payload["event_id"] = callback_event_id(payload)
        return self.write(
            "record-callback",
            payload,
            operation="approval-callback-1",
            key=key,
            expected_generation=expected_generation,
        )

    def reach_pending(self) -> None:
        for output in (
            self.prepare(),
            self.start(),
            self.result(),
            self.ack(),
            self.advance(),
        ):
            assert output["code"] == "CTL_OK"


@pytest.mark.parametrize(
    ("state", "pending", "next_role"),
    (
        ("plan_review_pending", "user_planning_approval_pending", "Developer"),
        ("implementation_readiness_pending", "user_implementation_approval_pending", "Planner"),
    ),
)
def test_full_journal_callback_and_next_scan_are_separate(
    tmp_path: Path,
    state: str,
    pending: str,
    next_role: str,
) -> None:
    scenario = ApprovalScenario(tmp_path, state, generation=28)
    scenario.reach_pending()
    before_callback = scenario.store.load()

    assert before_callback["lanes"]["lane-1"]["state"] == pending
    assert "user_approved" not in before_callback["lanes"]["lane-1"]["proof"]
    assert "lane-1:User" not in before_callback["role_bindings"]

    first = scenario.callback()
    replay = scenario.callback()
    conflict = scenario.callback(status="reviewer_pass")
    stale = scenario.callback(key="stale", expected_generation=5)
    registry = scenario.store.load()

    assert first["code"] == "CTL_OK"
    assert replay["code"] == "CTL_ALREADY_APPLIED"
    assert conflict["code"] == "CTL_IDEMPOTENCY_CONFLICT"
    assert stale["code"] == "CTL_CAS_CONFLICT"
    assert registry["generation"] == 34
    assert registry["lanes"]["lane-1"]["proof"]["user_approved"] is True
    assert select_next_action(
        pending,
        registry["lanes"]["lane-1"]["proof"],
    )["target_role"] == next_role


@pytest.mark.parametrize(
    ("field", "value", "code"),
    (
        ("thread_id", "wrong", "CTL_THREAD_BINDING_MISMATCH"),
        ("controller_thread_id", "wrong", "CTL_THREAD_BINDING_MISMATCH"),
        ("approval_gate", "wrong", "CTL_CALLBACK_CONFLICT"),
        ("approval_scope_digest", "wrong", "CTL_CALLBACK_CONFLICT"),
        ("scope_fingerprint", "wrong", "CTL_CALLBACK_CONFLICT"),
        ("task_id", "wrong", "CTL_CALLBACK_CONFLICT"),
        ("lane_id", "wrong", "CTL_CALLBACK_CONFLICT"),
        ("route_id", "wrong", "CTL_CALLBACK_CONFLICT"),
        ("operation_id", "wrong", "CTL_CALLBACK_CONFLICT"),
        ("status", "reviewer_pass", "CTL_CALLBACK_CONFLICT"),
    ),
)
def test_wrong_callback_binding_is_zero_write(
    tmp_path: Path,
    field: str,
    value: str,
    code: str,
) -> None:
    scenario = ApprovalScenario(tmp_path)
    scenario.reach_pending()

    output = scenario.callback(**{field: value})

    assert output["code"] == code
    assert output["zero_write"] is True
    assert scenario.store.load()["generation"] == 5
    assert scenario.store.load()["callbacks"] == {}


def test_callback_before_ack_and_after_consumption_fail_closed(tmp_path: Path) -> None:
    early = ApprovalScenario(tmp_path / "early")
    early.prepare()
    assert early.callback()["code"] == "CTL_ROLE_CALLBACK_STATE_MISMATCH"
    assert early.store.load()["generation"] == 1

    late = ApprovalScenario(tmp_path / "late")
    late.reach_pending()
    registry = late.store.load()
    registry["lanes"]["lane-1"]["state"] = "developer_planning_active"
    late.store._atomic_write(registry)
    assert late.callback()["code"] == "CTL_ROLE_CALLBACK_STATE_MISMATCH"
    assert late.store.load()["generation"] == 5


@pytest.mark.parametrize("checkpoint", ("prepare", "start", "result", "ack"))
def test_request_resumes_every_journal_checkpoint(
    tmp_path: Path,
    checkpoint: str,
) -> None:
    scenario = ApprovalScenario(tmp_path)
    steps = ("prepare", "start", "result", "ack")
    for name in steps[:steps.index(checkpoint) + 1]:
        assert getattr(scenario, name)()["code"] == "CTL_OK"
    scenario.store = RegistryStore(
        scenario.store.root, repository_fingerprint="repo-1")
    for name in steps[steps.index(checkpoint) + 1:]:
        assert getattr(scenario, name)()["code"] == "CTL_OK"
    assert scenario.advance()["code"] == "CTL_OK"
    registry = scenario.store.load()

    assert registry["generation"] == 5
    assert registry["dispatches"]["approval-1"]["stage"] == "advanced"
    assert registry["lanes"]["lane-1"]["state"] == "user_planning_approval_pending"
    assert "user_approved" not in registry["lanes"]["lane-1"]["proof"]


def test_catalog_and_mutation_surface_remain_exact() -> None:
    assert len(ALL_CODES) == 39
    assert MUTATION_COMMANDS == (
        "prepare-dispatch",
        "mark-invocation-started",
        "record-action-result",
        "record-callback",
        "ack-dispatch",
        "advance-state",
    )
