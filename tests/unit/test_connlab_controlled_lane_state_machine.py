from __future__ import annotations

import pytest

from scripts.connlab_controlled_lane.contracts import CtlError
from scripts.connlab_controlled_lane.state_machine import (
    classify_manual_smoke,
    select_next_action,
    validate_advance_authority,
    validate_authoritative_dispatch,
    validate_action,
    validate_transition,
)


def test_prepare_action_is_recomputed_from_registry_authority() -> None:
    registry = {"dispatches": {}, "lanes": {"lane-1": {
        "state": "planned", "proof": {}, "scope_fingerprint": "scope-1"}}}
    request = {
        "task_id": "TASK_1", "lane_id": "lane-1", "route_id": "route-1",
        "operation_id": "operation-1", "scope_fingerprint": "scope-1",
    }
    with pytest.raises(CtlError) as exc_info:
        validate_authoritative_dispatch(
            registry, request,
            {"current_state": "planned", "action_kind": "create_or_adopt_worktree"})
    assert exc_info.value.code == "CTL_INVALID_TRANSITION"
    registry["dispatches"]["active"] = {"lane_id": "lane-1", "stage": "prepared"}
    with pytest.raises(CtlError) as active_error:
        validate_authoritative_dispatch(registry, request, {})
    assert active_error.value.code == "CTL_DISPATCH_STAGE_MISMATCH"
    with pytest.raises(CtlError) as stale_error:
        validate_advance_authority(registry, "lane-1", "authorized")
    assert stale_error.value.code == "CTL_CAS_CONFLICT"


@pytest.mark.parametrize(
    ("state", "proof", "kind", "role"),
    [
        ("plan_review_pending", {"review_status": "blocked",
         "planner_thread_id": "plan-1", "planner_worktree_path": "C:/primary"},
         "send_existing_task", "Planner"),
        ("implementation_readiness_pending", {"readiness_status": "blocked",
         "developer_thread_id": "dev-1", "developer_worktree_path": "C:/primary"},
         "send_existing_task", "Developer"),
        ("developer_fix_active", {"developer_status": "complete",
         "reviewer_thread_id": "review-1", "reviewer_worktree_path": "C:/lane"},
         "dispatch_role", "Reviewer"),
        ("review_pending", {"review_status": "passed",
         "qa_thread_id": "qa-1", "qa_worktree_path": "C:/lane"},
         "dispatch_role", "QA"),
        ("qa_pending", {"qa_status": "passed",
         "integrator_thread_id": "int-1", "integrator_worktree_path": "C:/lane"},
         "dispatch_role", "Integrator"),
        ("review_pending", {"review_status": "blocked",
         "developer_thread_id": "dev-1", "developer_worktree_path": "C:/lane"},
         "send_existing_task", "Developer"),
    ],
)
def test_prepare_rejects_wrong_existing_role_target(
    state: str, proof: dict[str, object], kind: str, role: str
) -> None:
    proof["completion_authority"] = {
        "role": role, "evidence_path": "docs/evidence.md",
        "base_lane_head": "abc123",
        "allowed_changed_paths": ["docs/evidence.md"],
        "checkpoint_required": True, "nullable": False,
    }
    registry = {"dispatches": {}, "lanes": {"lane-1": {
        "state": state, "proof": proof, "scope_fingerprint": "scope-1"}}}
    request = {"task_id": "TASK_1", "lane_id": "lane-1", "route_id": "route-1",
               "operation_id": "operation-1", "scope_fingerprint": "scope-1"}
    target = {
        "task_id": "TASK_1", "lane_id": "lane-1", "route_id": "route-1",
        "operation_id": "operation-1", "payload_digest": "payload",
        "action_kind": kind, "role": role, "thread_id": "wrong-thread",
        "worktree_path": "C:/wrong-worktree",
        "completion_authority_nullable": False,
        "expected_evidence_path": "docs/evidence.md",
        "base_lane_head": "abc123",
        "allowed_changed_paths": ["docs/evidence.md"],
        "checkpoint_required": True,
    }
    with pytest.raises(CtlError) as exc_info:
        validate_authoritative_dispatch(
            registry, request,
            {"current_state": state, "action_kind": kind, "target_binding": target})
    assert exc_info.value.code == "CTL_DISPATCH_ACK_MISMATCH"
    selected = select_next_action(state, proof)
    target.update(thread_id=selected["thread_id"], worktree_path=selected["worktree_path"])
    proof["completion_authority"]["base_lane_head"] = None
    target["base_lane_head"] = None
    with pytest.raises(CtlError) as authority_error:
        validate_authoritative_dispatch(
            registry, request,
            {"current_state": state, "action_kind": kind, "target_binding": target})
    assert authority_error.value.code == "CTL_DISPATCH_ACK_MISMATCH"
    proof["completion_authority"]["base_lane_head"] = target["base_lane_head"] = "abc123"
    for field in tuple(proof):
        if field.endswith(("_thread_id", "_worktree_path")):
            proof.pop(field)
    with pytest.raises(CtlError) as missing_error:
        validate_authoritative_dispatch(
            registry, request,
            {"current_state": state, "action_kind": kind, "target_binding": target})
    assert missing_error.value.code == "CTL_DISPATCH_ACK_MISMATCH"


@pytest.mark.parametrize(
    ("state", "proof", "kind", "role"),
    [
        ("planned", {}, "dispatch_role", "Reviewer"),
        (
            "planner_fix_pending",
            {"planner_status": "complete"},
            "dispatch_role",
            "Reviewer",
        ),
        (
            "user_planning_approval_pending",
            {"user_approved": True},
            "dispatch_role",
            "Developer",
        ),
        (
            "developer_planning_active",
            {"developer_status": "complete"},
            "dispatch_role",
            "Planner",
        ),
        (
            "planner_reconciliation_pending",
            {"planner_status": "complete"},
            "dispatch_role",
            "Reviewer",
        ),
        (
            "implementation_readiness_pending",
            {"readiness_status": "passed"},
            "request_user_approval",
            "User",
        ),
        (
            "user_implementation_approval_pending",
            {"user_approved": True},
            "dispatch_role",
            "Planner",
        ),
        (
            "developer_fix_active",
            {"developer_status": "complete"},
            "dispatch_role",
            "Reviewer",
        ),
        (
            "review_pending",
            {"review_status": "blocked", "developer_thread_id": "dev-1"},
            "send_existing_task",
            "Developer",
        ),
        ("qa_pending", {"qa_status": "passed"}, "dispatch_role", "Integrator"),
        (
            "integration_pending",
            {"integrator_status": "accepted"},
            "governance_closeout",
            "Integrator",
        ),
        (
            "closeout_pending",
            {"clean_closeout": True},
            "retire_worktree",
            None,
        ),
        (
            "retired",
            {"archive_authorized": True},
            "archive_one_task",
            None,
        ),
    ],
)
def test_unique_next_action_table(
    state: str, proof: dict[str, object], kind: str, role: str | None
) -> None:
    action = select_next_action(state, proof)

    assert action["kind"] == kind
    assert action.get("target_role") == role


def test_reviewer_pass_defaults_to_qa_and_no_qa_needs_double_proof() -> None:
    default = select_next_action("review_pending", {"review_status": "passed"})
    bypass = select_next_action(
        "review_pending",
        {
            "review_status": "passed",
            "qa_required": False,
            "user_no_qa_digest": "user",
            "reviewer_no_qa_digest": "reviewer",
        },
    )

    assert default["target_role"] == "QA"
    assert bypass["target_role"] == "Integrator"
    with pytest.raises(CtlError) as exc_info:
        select_next_action(
            "review_pending",
            {"review_status": "passed", "qa_required": False},
        )
    assert exc_info.value.code == "CTL_AUTHORIZATION_REQUIRED"


def test_qa_blocker_routes_only_attributed_bounded_fix_to_same_developer() -> None:
    action = select_next_action(
        "qa_pending",
        {
            "qa_status": "blocked",
            "attributed": True,
            "in_scope": True,
            "bounded": True,
            "developer_thread_id": "dev-1",
            "worktree_path": "C:/lane",
        },
    )

    assert action["kind"] == "send_existing_task"
    assert action["thread_id"] == "dev-1"
    assert action["worktree_path"] == "C:/lane"


def test_qa_scope_expansion_routes_planner_but_unattributed_fails_closed() -> None:
    reconcile = select_next_action(
        "qa_pending",
        {
            "qa_status": "blocked",
            "attributed": True,
            "in_scope": False,
            "scope_expanded": True,
        },
    )

    assert reconcile == {"kind": "planner_reconciliation", "target_role": "Planner"}
    with pytest.raises(CtlError) as exc_info:
        select_next_action(
            "qa_pending",
            {"qa_status": "blocked", "attributed": False, "in_scope": True},
        )
    assert exc_info.value.code == "CTL_RECOVERY_REQUIRED"


def test_integrator_blocker_routes_exact_attributed_owner_only() -> None:
    action = select_next_action(
        "integration_pending",
        {
            "integrator_status": "blocked",
            "attributed": True,
            "owner_role": "Developer",
            "owner_thread_id": "dev-1",
        },
    )

    assert action == {
        "kind": "send_existing_task",
        "target_role": "Developer",
        "thread_id": "dev-1",
    }
    with pytest.raises(CtlError) as exc_info:
        select_next_action(
            "integration_pending",
            {"integrator_status": "blocked", "attributed": False},
        )
    assert exc_info.value.code == "CTL_RECOVERY_REQUIRED"


def test_readiness_blocker_reuses_developer_for_docs_only_fix() -> None:
    action = select_next_action(
        "implementation_readiness_pending",
        {
            "readiness_status": "blocked",
            "developer_thread_id": "dev-1",
        },
    )

    assert action == {
        "kind": "send_existing_task",
        "target_role": "Developer",
        "thread_id": "dev-1",
    }


def test_state_action_and_transition_validation_fail_closed() -> None:
    validate_action("authorized", "create_developer_environment")
    validate_transition("developer_environment_pending", "developer_active")

    with pytest.raises(CtlError):
        validate_action("planned", "create_or_adopt_worktree")
    with pytest.raises(CtlError):
        validate_transition("planned", "archived")


def test_manual_smoke_has_three_top_level_classifications() -> None:
    cases = (
        (False, False, True, "active_lane_bounded_fix"),
        (False, True, True, "planner_reconciliation_required"),
        (False, False, False, "planner_reconciliation_required"),
        (True, False, True, "corrective_lane_required"),
    )
    for integrated, changed, attributed, expected in cases:
        assert classify_manual_smoke(
            integrated=integrated, scope_changed=changed, attributed=attributed) == expected
