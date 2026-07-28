from __future__ import annotations

from typing import Any, Mapping

from .bootstrap import (
    BOOTSTRAP_ACTIONS, BOOTSTRAP_STATES, select_bootstrap_action,
    validate_bootstrap_action, validate_bootstrap_target_binding,
    validate_bootstrap_transition,
)
from .completion_authority import frozen_completion_contract
from . import controller_title
from .contracts import CtlError, canonical_digest
from .ownership import validate_target_binding

_ALLOWED_ACTIONS = {
    "planned": {"dispatch_role"},
    "plan_review_pending": {"send_existing_task", "request_user_approval"},
    "planner_fix_pending": {"dispatch_role"},
    "user_planning_approval_pending": {"dispatch_role"},
    "developer_planning_active": {"dispatch_role"},
    "planner_reconciliation_pending": {"dispatch_role"},
    "implementation_readiness_pending": {"send_existing_task", "request_user_approval"},
    "user_implementation_approval_pending": {"dispatch_role"},
    "authorized": {"create_developer_environment"},
    "developer_environment_pending": {"observe_developer_environment"},
    "developer_active": {"dispatch_role"},
    "developer_fix_active": {"dispatch_role"},
    "review_pending": {"send_existing_task", "dispatch_role"},
    "qa_pending": {"send_existing_task", "dispatch_role", "planner_reconciliation"},
    "integration_pending": {"governance_closeout"},
    "closeout_pending": {"retire_worktree"},
    "retired": {"archive_one_task"},
}
_ALLOWED_TRANSITIONS = {
    ("planned", "plan_review_pending"), ("plan_review_pending", "planner_fix_pending"),
    ("planner_fix_pending", "plan_review_pending"),
    ("plan_review_pending", "user_planning_approval_pending"), ("user_planning_approval_pending", "developer_planning_active"),
    ("developer_planning_active", "planner_reconciliation_pending"), ("planner_reconciliation_pending", "implementation_readiness_pending"),
    ("implementation_readiness_pending", "developer_planning_active"),
    ("implementation_readiness_pending", "user_implementation_approval_pending"),
    ("user_implementation_approval_pending", "planner_reconciliation_pending"),
    ("planner_reconciliation_pending", "authorized"), ("authorized", "developer_environment_pending"),
    ("developer_environment_pending", "developer_active"), ("developer_active", "review_pending"),
    ("review_pending", "developer_fix_active"),
    ("developer_fix_active", "review_pending"), ("review_pending", "qa_pending"),
    ("review_pending", "integration_pending"), ("qa_pending", "developer_fix_active"),
    ("qa_pending", "integration_pending"), ("integration_pending", "closeout_pending"),
    ("closeout_pending", "retired"), ("retired", "archived"),
}


def validate_action(state: str, action_kind: str) -> None:
    if state in BOOTSTRAP_STATES:
        validate_bootstrap_action(state, action_kind)
        return
    if action_kind not in _ALLOWED_ACTIONS.get(state, set()):
        raise CtlError(
            "CTL_INVALID_TRANSITION",
            f"action {action_kind} is not legal from {state}",
        )


def validate_transition(from_state: str, to_state: str) -> None:
    if from_state in BOOTSTRAP_STATES or to_state in BOOTSTRAP_STATES:
        validate_bootstrap_transition(from_state, to_state)
        return
    if (from_state, to_state) not in _ALLOWED_TRANSITIONS:
        raise CtlError(
            "CTL_INVALID_TRANSITION",
            f"transition {from_state} -> {to_state} is not legal",
        )


def validate_authoritative_dispatch(
    registry: Mapping[str, Any], request: Mapping[str, Any], payload: Mapping[str, Any]
) -> tuple[str, Mapping[str, Any]]:
    lane = registry["lanes"].get(request["lane_id"])
    if not lane:
        raise CtlError("CTL_LANE_NOT_AUTHORIZED", "lane is absent from registry")
    if lane.get("scope_fingerprint") != request["scope_fingerprint"]:
        raise CtlError("CTL_SCOPE_VIOLATION", "lane scope fingerprint changed")
    if any(
        item.get("lane_id") == request["lane_id"] and item.get("stage") != "advanced"
        for item in registry["dispatches"].values()
    ):
        raise CtlError("CTL_DISPATCH_STAGE_MISMATCH",
                       "lane already has an unfinished dispatch")
    state = str(lane.get("state"))
    action = select_next_action(state, lane.get("proof", {}))
    if payload.get("current_state") != state or payload.get("action_kind") != action.get("kind"):
        raise CtlError("CTL_INVALID_TRANSITION",
                       "dispatch does not match authoritative lane action")
    if action.get("target_role") and action.get("kind") not in (
        "governance_closeout", "create_developer_environment",
    ) + tuple(BOOTSTRAP_ACTIONS) and not all(
        action.get(field) for field in ("thread_id", "worktree_path")):
        raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "selected role identity is incomplete")
    expected = {
        "task_id": request["task_id"], "lane_id": request["lane_id"],
        "route_id": request["route_id"], "operation_id": request["operation_id"],
    }
    expected.update({"role": action["target_role"]} if action.get("target_role") else {})
    expected.update({key: action[key] for key in ("thread_id", "worktree_path")
                     if action.get(key)})
    if action.get("kind") in BOOTSTRAP_ACTIONS:
        bootstrap = registry.get("bootstrap", {})
        if action["kind"] == "create_controller_task":
            expected.update(controller_title.build_controller_create_target(
                bootstrap.get("controller", {})))
        elif action["kind"] in controller_title.CONTROLLER_TITLE_ACTIONS:
            expected.update(controller_title.build_controller_title_target(
                registry, str(request["lane_id"]), str(action["kind"])))
        elif action["kind"] == "create_paused_heartbeat":
            heartbeat = bootstrap.get("heartbeat", {})
            expected.update({
                "controller_thread_id": bootstrap.get("controller", {}).get("thread_id"),
                "heartbeat_name": heartbeat.get("name"),
                "rrule": heartbeat.get("rrule"),
                "status": heartbeat.get("status"),
            })
        else:
            expected.update({
                "validation_scope_digest": canonical_digest({
                    "scope_fingerprint": lane.get("scope_fingerprint"),
                    "requested_scope": lane.get("requested_scope"),
                    "authority_files": lane.get("authority_files"),
                }),
                "expected_external_action_count": 0,
            })
    if action.get("kind") in ("dispatch_role", "create_developer_environment",
                              "send_existing_task", "request_user_approval"):
        authority = lane.get("proof", {}).get("completion_authority")
        if not isinstance(authority, dict):
            raise CtlError("CTL_DISPATCH_ACK_MISMATCH", "completion authority is missing")
        expected.update(frozen_completion_contract(
            authority, role=str(action.get("target_role"))))
    validator = (
        validate_bootstrap_target_binding
        if action.get("kind") in BOOTSTRAP_ACTIONS
        else validate_target_binding
    )
    validator(
        payload.get("target_binding"),
        action_kind=str(payload["action_kind"]),
        expected=expected,
    )
    return state, action


def validate_advance_authority(registry: Mapping[str, Any], lane_id: str, from_state: str,
                               expected_scope: str | None = None) -> None:
    lane = registry["lanes"].get(lane_id)
    if not lane or lane.get("state") != from_state or (
        expected_scope is not None and lane.get("scope_fingerprint") != expected_scope
    ):
        raise CtlError("CTL_CAS_CONFLICT", "lane state changed after dispatch prepare")


def _dispatch(role: str, proof: Mapping[str, Any], kind: str = "dispatch_role",
              identity: str | None = None) -> dict[str, Any]:
    prefix = (identity or role).casefold()
    action = {"kind": kind, "target_role": role}
    thread = proof.get(f"{prefix}_thread_id")
    worktree = proof.get(f"{prefix}_worktree_path") or proof.get("worktree_path")
    if thread:
        action["thread_id"] = thread
    if worktree:
        action["worktree_path"] = worktree
    return action


def select_next_action(state: str, proof: Mapping[str, Any]) -> dict[str, Any]:
    if state in BOOTSTRAP_STATES:
        return select_bootstrap_action(state, proof)
    if state == "planned":
        return _dispatch("Reviewer", proof)
    if state == "plan_review_pending":
        if proof.get("review_status") == "blocked":
            return _dispatch("Planner", proof, "send_existing_task")
        if proof.get("review_status") == "passed":
            return _dispatch("User", proof, "request_user_approval")
    if state == "planner_fix_pending" and proof.get("planner_status") == "complete":
        return _dispatch("Reviewer", proof)
    if state == "user_planning_approval_pending" and proof.get("user_approved"):
        return _dispatch("Developer", proof)
    if state == "developer_planning_active" and proof.get("developer_status") == "complete":
        return _dispatch("Planner", proof)
    if state == "planner_reconciliation_pending" and proof.get("planner_status") == "complete":
        return _dispatch("Reviewer", proof)
    if state == "implementation_readiness_pending":
        if proof.get("readiness_status") == "blocked":
            return _dispatch("Developer", proof, "send_existing_task")
        if proof.get("readiness_status") == "passed":
            return _dispatch("User", proof, "request_user_approval")
    if state == "user_implementation_approval_pending" and proof.get("user_approved"):
        return _dispatch("Planner", proof)
    if state == "authorized":
        return {"kind": "create_developer_environment", "target_role": "Developer"}
    if state == "developer_environment_pending":
        return {"kind": "observe_developer_environment", "target_role": "Developer"}
    if state in ("developer_active", "developer_fix_active") and (
        proof.get("developer_status") == "complete"
    ):
        return _dispatch("Reviewer", proof)
    if state == "review_pending":
        if proof.get("review_status") == "blocked":
            return _dispatch("Developer", proof, "send_existing_task")
        if proof.get("review_status") == "passed":
            if proof.get("qa_required", True) is not False:
                return _dispatch("QA", proof)
            if not (
                proof.get("user_no_qa_digest")
                and proof.get("reviewer_no_qa_digest")
            ):
                raise CtlError(
                    "CTL_AUTHORIZATION_REQUIRED",
                    "QA bypass requires User and Reviewer proof",
                )
            return _dispatch("Integrator", proof)
    if state == "qa_pending":
        if proof.get("qa_status") == "passed":
            return _dispatch("Integrator", proof)
        if proof.get("qa_status") == "blocked":
            if all(
                proof.get(field) for field in ("attributed", "in_scope", "bounded")
            ):
                return _dispatch("Developer", proof, "send_existing_task")
            if proof.get("attributed") and proof.get("scope_expanded"):
                return _dispatch("Planner", proof, "planner_reconciliation")
            raise CtlError(
                "CTL_RECOVERY_REQUIRED",
                "QA blocker is external, unattributed, or ambiguous",
            )
    if state == "integration_pending":
        if proof.get("integrator_status") == "accepted":
            return {"kind": "governance_closeout", "target_role": "Integrator"}
        if proof.get("integrator_status") == "blocked" and proof.get("attributed"):
            role = proof.get("owner_role")
            thread_id = proof.get("owner_thread_id")
            if role and thread_id:
                return _dispatch(str(role), proof, "send_existing_task", "owner")
        if proof.get("integrator_status") == "blocked":
            raise CtlError(
                "CTL_RECOVERY_REQUIRED",
                "Integrator blocker has no exact owning role binding",
            )
    if state == "closeout_pending" and proof.get("clean_closeout"):
        return {"kind": "retire_worktree", "target_role": None}
    if state == "retired" and proof.get("archive_authorized"):
        return {"kind": "archive_one_task", "target_role": None}
    raise CtlError("CTL_INVALID_TRANSITION", f"no legal action from {state}")


def apply_callback_proof(
    registry: dict[str, Any], lane_id: str,
    payload: Mapping[str, Any], outcome: str,
) -> None:
    lane = registry["lanes"][lane_id]
    proof = lane.setdefault("proof", {})
    role = str(payload["role"]).casefold()
    if role in ("developer", "planner"):
        proof[f"{role}_status"] = outcome
    elif role == "reviewer":
        key = "readiness_status" if lane.get("state") == "implementation_readiness_pending" else (
            "review_status")
        proof[key] = outcome
    elif role == "qa":
        proof["qa_status"] = outcome
    elif role == "integrator":
        proof["integrator_status"] = outcome
    elif role == "user":
        proof["user_approved"] = outcome == "approved"


def classify_manual_smoke(*, integrated: bool, scope_changed: bool, attributed: bool) -> str:
    return ("corrective_lane_required" if integrated else
            "planner_reconciliation_required" if scope_changed or not attributed else
            "active_lane_bounded_fix")
