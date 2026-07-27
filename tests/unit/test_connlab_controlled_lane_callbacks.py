from __future__ import annotations

import pytest

from scripts.connlab_controlled_lane.callbacks import (
    callback_event_id,
    callback_template,
    native_task_decision,
    parse_callback,
    recovery_decision,
    validate_completion_callback,
)
from scripts.connlab_controlled_lane.contracts import CtlError


def test_callback_round_trip_binds_route_operation_lane_worktree_and_thread() -> None:
    fields = {
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "role": "Developer",
        "status": "ready_for_review",
        "evidence_path": "docs/evidence.md",
        "evidence_sha256": "evidence",
        "lane_head": "abc123",
        "route_id": "route-1",
        "operation_id": "operation-1",
        "thread_id": "thread-1",
        "worktree_path": "C:/lane",
        "next_role_hint": "Reviewer",
        "blocker_code": None,
    }
    fields["event_id"] = callback_event_id(fields)

    parsed = parse_callback(callback_template(fields), expected=fields)

    assert parsed == fields


def test_callback_event_id_is_deterministic_and_tamper_evident() -> None:
    fields = {
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "role": "Developer",
        "status": "ready_for_review",
        "evidence_path": "docs/evidence.md",
        "evidence_sha256": "sha",
        "lane_head": "abc123",
    }

    assert callback_event_id(fields) == callback_event_id(dict(reversed(list(fields.items()))))
    message = callback_template(fields)
    parsed = parse_callback(message)
    assert parsed["event_id"] == callback_event_id(fields)

    with pytest.raises(CtlError) as exc_info:
        callback_template({**fields, "event_id": "wrong"})
    assert exc_info.value.code == "CTL_CALLBACK_CONFLICT"


def test_callback_wrong_binding_fails_closed() -> None:
    fields = {
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "role": "Developer",
        "status": "ready",
        "route_id": "route-1",
        "operation_id": "operation-1",
        "thread_id": "thread-1",
        "worktree_path": "C:/lane",
    }
    fields["event_id"] = callback_event_id(fields)

    with pytest.raises(CtlError) as exc_info:
        parse_callback(
            callback_template(fields),
            expected={**fields, "thread_id": "thread-2"},
        )

    assert exc_info.value.code == "CTL_THREAD_BINDING_MISMATCH"


@pytest.mark.parametrize("count", [0, 2])
def test_possible_start_never_resends_on_zero_or_multiple_readback(count: int) -> None:
    decision = recovery_decision(
        stage="invocation_started",
        invocation_may_have_started=True,
        readback_matches=count,
        readback_readable=True,
    )

    assert decision["code"] in {"CTL_RECOVERY_REQUIRED", "CTL_NATIVE_READBACK_AMBIGUOUS"}
    assert decision["resend"] is False


def test_durable_pre_invocation_proof_allows_same_id_retry() -> None:
    decision = recovery_decision(
        stage="prepared",
        invocation_may_have_started=False,
        readback_matches=0,
        readback_readable=True,
    )

    assert decision == {
        "code": "CTL_OK",
        "action": "retry_same_operation",
        "resend": True,
    }


@pytest.mark.parametrize("action", ["create", "send"])
def test_native_create_and_send_require_invocation_marker(action: str) -> None:
    binding = {
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "route_id": "route-1",
        "operation_id": "operation-1",
        "thread_id": "thread-1",
        "worktree_path": "C:/lane",
        "payload_digest": "payload",
        "action_kind": action,
    }
    with pytest.raises(CtlError) as exc_info:
        native_task_decision(
            action=action,
            stage="prepared",
            expected_binding=binding,
            observed_binding=binding,
        )

    assert exc_info.value.code == "CTL_DISPATCH_STAGE_MISMATCH"
    assert native_task_decision(
        action=action,
        stage="invocation_started",
        expected_binding=binding,
        observed_binding=binding,
    )["execute"] is True


def test_native_action_requires_exact_immutable_binding() -> None:
    expected = {
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "route_id": "route-1",
        "operation_id": "operation-1",
        "thread_id": "thread-1",
        "worktree_path": "C:/lane",
        "payload_digest": "payload",
        "action_kind": "send",
    }

    with pytest.raises(CtlError) as exc_info:
        native_task_decision(
            action="send",
            stage="invocation_started",
            expected_binding=expected,
            observed_binding={**expected, "thread_id": "wrong"},
        )

    assert exc_info.value.code == "CTL_THREAD_BINDING_MISMATCH"
    with pytest.raises(CtlError) as empty_error:
        native_task_decision(
            action="send",
            stage="invocation_started",
            expected_binding={},
            observed_binding={},
        )
    assert empty_error.value.code == "CTL_DISPATCH_ACK_MISMATCH"
    assert native_task_decision(
        action="send",
        stage="invocation_started",
        expected_binding=expected,
        observed_binding=expected,
    )["external_action_count"] == 1


def test_native_adopt_and_archive_fail_closed_without_exact_proof() -> None:
    with pytest.raises(CtlError) as adopt_error:
        native_task_decision(action="adopt", stage="invocation_started", matches=2)
    assert adopt_error.value.code == "CTL_NATIVE_READBACK_AMBIGUOUS"

    with pytest.raises(CtlError) as archive_error:
        native_task_decision(
            action="archive",
            stage="invocation_started",
            archive_authorized=False,
            retired=True,
        )
    assert archive_error.value.code == "CTL_AUTHORIZATION_REQUIRED"


def test_completion_callback_requires_frozen_binding_and_canonical_status(
    monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "scripts.connlab_controlled_lane.callbacks.observe_completion_authority",
        lambda _, payload: {} if all(payload.get(field) for field in (
            "evidence_path", "evidence_sha256", "lane_head")) else (_ for _ in ()).throw(
            CtlError("CTL_CALLBACK_CONFLICT", "missing authority")))
    target = {
        "task_id": "TASK_1", "lane_id": "lane-1", "route_id": "route-1",
        "operation_id": "operation-1", "role": "Reviewer", "thread_id": "thread-1",
        "worktree_path": "C:/lane", "payload_digest": "payload-1",
    }
    dispatch = {
        "task_id": "TASK_1", "lane_id": "lane-1", "route_id": "route-1",
        "operation_id": "operation-1", "target_binding": target,
        "state_advance_payload": {"to_state": "review_pending"},
    }
    payload = {
        **target, "status": "unknown-success", "evidence_path": "docs/evidence.md",
        "evidence_sha256": "evidence", "lane_head": "abc123",
    }
    registry = {
        "lanes": {"lane-1": {"state": "review_pending"}},
        "role_bindings": {"lane-1:Reviewer": {**target, "status": "active"}},
    }
    with pytest.raises(CtlError) as exc_info:
        validate_completion_callback(registry, dispatch, payload)
    assert exc_info.value.code == "CTL_CALLBACK_CONFLICT"
    for invalid in (
        {**payload, "status": "qa_pass"},
        {**payload, "status": "reviewer_pass", "evidence_path": ""},
    ):
        with pytest.raises(CtlError) as exc_info:
            validate_completion_callback(registry, dispatch, invalid)
        assert exc_info.value.code == "CTL_CALLBACK_CONFLICT"

    registry["lanes"]["lane-1"]["state"] = "qa_pending"
    payload["status"] = "reviewer_pass"
    with pytest.raises(CtlError) as exc_info:
        validate_completion_callback(registry, dispatch, payload)
    assert exc_info.value.code == "CTL_ROLE_CALLBACK_STATE_MISMATCH"
