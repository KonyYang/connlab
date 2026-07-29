from __future__ import annotations

from copy import deepcopy

import pytest

from scripts.connlab_controlled_lane.approval_authority import (
    approval_gate_for_state,
    build_approval_target,
    validate_approval_target,
)
from scripts.connlab_controlled_lane.contracts import (
    CtlError,
    canonical_digest,
    validate_recovery_binding,
)
from scripts.connlab_controlled_lane.git_preflight import verified_recovery_decision


def _registry(state: str = "plan_review_pending") -> dict[str, object]:
    return {
        "bootstrap": {"controller": {"thread_id": "controller-1"}},
        "role_bindings": {
            "bootstrap-lane:Controller": {
                "lane_id": "bootstrap-lane",
                "role": "Controller",
                "thread_id": "controller-1",
                "status": "active",
            }
        },
        "lanes": {
            "lane-1": {
                "task_id": "TASK_1",
                "state": state,
                "scope_fingerprint": "scope-1",
                "requested_scope": {"paths": ["tests/unit/approval.py"]},
                "authority_files": {"task.md": "sha-1"},
                "proof": {},
            }
        },
    }


def _request() -> dict[str, str]:
    return {
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "route_id": "route-1",
        "operation_id": "approval-1",
        "scope_fingerprint": "scope-1",
    }


@pytest.mark.parametrize(
    ("state", "gate", "pending"),
    (
        ("plan_review_pending", "planning_first", "user_planning_approval_pending"),
        (
            "implementation_readiness_pending",
            "tests_only_implementation",
            "user_implementation_approval_pending",
        ),
    ),
)
def test_controller_only_target_is_canonical_and_has_no_worktree_authority(
    state: str,
    gate: str,
    pending: str,
) -> None:
    registry = _registry(state)
    target = build_approval_target(registry, "lane-1", _request())

    validate_approval_target(target, expected=target)

    assert approval_gate_for_state(state) == (gate, pending)
    assert target["role"] == "User"
    assert target["thread_id"] == target["controller_thread_id"] == "controller-1"
    assert target["approval_gate"] == gate
    assert target["expected_from_state"] == state
    assert target["expected_pending_state"] == pending
    assert target["approval_scope_digest"] == canonical_digest(
        registry["lanes"]["lane-1"]["requested_scope"])
    assert target["payload_digest"] == target["request_payload_digest"]
    assert target["approval_contract_digest"] == canonical_digest(
        {key: value for key, value in target.items() if key != "approval_contract_digest"}
    )
    assert not {
        "worktree_path",
        "completion_authority_nullable",
        "expected_evidence_path",
        "base_lane_head",
    }.intersection(target)


@pytest.mark.parametrize(
    ("mutation", "code"),
    (
        ({"thread_id": "wrong"}, "CTL_THREAD_BINDING_MISMATCH"),
        ({"controller_thread_id": "wrong"}, "CTL_THREAD_BINDING_MISMATCH"),
        ({"approval_gate": "wrong"}, "CTL_DISPATCH_ACK_MISMATCH"),
        ({"scope_fingerprint": "wrong"}, "CTL_DISPATCH_ACK_MISMATCH"),
        ({"route_id": "wrong"}, "CTL_DISPATCH_ACK_MISMATCH"),
        ({"operation_id": "wrong"}, "CTL_DISPATCH_ACK_MISMATCH"),
        ({"worktree_path": "C:/wrong"}, "CTL_DISPATCH_ACK_MISMATCH"),
    ),
)
def test_target_changes_fail_closed(
    mutation: dict[str, str],
    code: str,
) -> None:
    target = build_approval_target(_registry(), "lane-1", _request())
    changed = {**target, **mutation}

    with pytest.raises(CtlError) as exc_info:
        validate_approval_target(changed, expected=target)

    assert exc_info.value.code == code


def test_missing_or_ambient_controller_binding_is_rejected() -> None:
    registry = _registry()
    del registry["role_bindings"]["bootstrap-lane:Controller"]

    with pytest.raises(CtlError) as missing:
        build_approval_target(registry, "lane-1", _request())
    assert missing.value.code == "CTL_THREAD_BINDING_MISMATCH"

    registry = _registry()
    registry["role_bindings"]["bootstrap-lane:Controller"]["thread_id"] = "ambient"
    with pytest.raises(CtlError) as changed:
        build_approval_target(registry, "lane-1", _request())
    assert changed.value.code == "CTL_THREAD_BINDING_MISMATCH"


def test_recovery_requires_exact_controller_readback() -> None:
    target = build_approval_target(_registry(), "lane-1", _request())
    dispatch = {
        "action_kind": "request_user_approval",
        "target_binding": target,
        "action_result_payload": {"receipt_digest": "receipt-1"},
    }
    validate_recovery_binding(dispatch, target)

    wrong = deepcopy(target)
    wrong["thread_id"] = "wrong"
    with pytest.raises(CtlError) as recovery_error:
        validate_recovery_binding(dispatch, wrong)
    assert recovery_error.value.code == "CTL_THREAD_BINDING_MISMATCH"


@pytest.mark.parametrize(
    ("readable", "matches", "binding", "code"),
    (
        (True, 1, "exact", "CTL_OK"),
        (True, 0, "exact", "CTL_RECOVERY_REQUIRED"),
        (True, 2, "exact", "CTL_NATIVE_READBACK_AMBIGUOUS"),
        (False, 1, "exact", "CTL_RECOVERY_REQUIRED"),
        (True, 1, "wrong", "CTL_RECOVERY_REQUIRED"),
    ),
)
def test_possible_start_recovery_never_resends(
    readable: bool,
    matches: int,
    binding: str,
    code: str,
) -> None:
    target = build_approval_target(_registry(), "lane-1", _request())
    observed = dict(target)
    if binding == "wrong":
        observed["thread_id"] = "wrong"
    decision = verified_recovery_decision(
        {
            "stage": "invocation_started",
            "action_kind": "request_user_approval",
            "target_binding": target,
        },
        {
            "readback_readable": readable,
            "readback_matches": matches,
            "readback_binding": observed,
            "readback_digest": canonical_digest(observed),
        },
    )

    assert decision["code"] == code
    assert decision["resend"] is False
