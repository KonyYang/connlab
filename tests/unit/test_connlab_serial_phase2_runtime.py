from __future__ import annotations

import copy

import pytest

from scripts.connlab_serial_complex import SerialContractError, complex_transition
from scripts.connlab_serial_phase2 import (
    active_snapshot,
    apply_bounded_fix_reentry,
    apply_scope_amendment,
    build_native_action,
    next_action,
)


ZERO40 = "0" * 40
ONE40 = "1" * 40
ZERO64 = "0" * 64
EVIDENCE = f"docs/lane_evidence/blocker.md@{ZERO40}#{ZERO64}"


def failure_proof() -> dict:
    return {
        "schema": "connlab.serial-failure-proof",
        "version": 1,
        "operation": "qa",
        "command": ["py", "-m", "pytest"],
        "exit_code": 1,
        "summary": "bounded failure",
        "recorded_at": "2026-08-15T00:00:00Z",
    }


def blocker(code: str) -> dict:
    stage = {"REVIEWER_BLOCKED": "review", "QA_BLOCKED": "qa", "INTEGRATION_BLOCKED": "integration", "SCOPE_EXPANDED": "development"}[code]
    return {
        "schema": "connlab.serial-task-blocker",
        "version": 1,
        "code": code,
        "stage": stage,
        "reason": "bounded blocker",
        "dirty_paths": ["scripts/new.py"] if code == "SCOPE_EXPANDED" else [],
        "failed_validation": failure_proof() if code in {"QA_BLOCKED", "INTEGRATION_BLOCKED"} else None,
        "subject_commit": None if code == "SCOPE_EXPANDED" else ONE40,
        "evidence_ref": EVIDENCE,
        "native_action_id": None,
        "related_ids": ["finding-1"] if code in {"REVIEWER_BLOCKED", "QA_BLOCKED"} else [],
        "retryable": code != "INTEGRATION_BLOCKED",
        "requires_user": code not in {"REVIEWER_BLOCKED", "QA_BLOCKED"},
        "resume_phase": "planning" if code == "SCOPE_EXPANDED" else ({"INTEGRATION_BLOCKED": "integration"}.get(code, "development")),
        "recorded_at": "2026-08-15T00:00:00Z",
    }


def active(code: str, *, phase: str = "blocked") -> dict:
    current = blocker(code)
    return {
        "task_id": "TASK_PHASE2",
        "summary": "Phase 2",
        "kind": "planned",
        "classification": "complex",
        "phase": phase,
        "scope_contract": {
            "may_touch": ["docs/task_board.md", "scripts/current.py"],
            "expected_file_count": 2,
            "classification_reason": "approved",
            "targeted_validation": ["pytest"],
            "forbidden_categories": {key: False for key in (
                "api_contract", "database", "schema_or_migration", "persistence", "authority",
                "public_drive_workflow", "business_rule_semantics", "destructive_action", "external_mutation",
            )},
        },
        "plan_ref": f"docs/plan.md@{ZERO40}#{ZERO64}",
        "approval_ref": "user:approved",
        "activation_parent_sha": ZERO40,
        "activated_at": "2026-08-15T00:00:00Z",
        "updated_at": "2026-08-15T00:00:00Z",
        "blocker": current,
        "validation": None,
        "complex_context": {
            "workflow_version": 1,
            "task_branch": "codex/task-phase2",
            "task_worktree": "C:/work/task-phase2",
            "base_sha": ZERO40,
            "head_sha": ONE40,
            "integration_target": "master",
            "worktree_lifecycle": "ready",
            "current_role": None,
            "current_attempt": 2,
            "role_invocations": [],
            "host_thread_id": "thread-1",
            "host_id": "host-1",
            "approved_code_paths": ["docs/task_board.md", "scripts/current.py"],
            "required_gates": ["Reviewer", "QA", "Integrator"],
            "developer_subject_commit": ONE40,
            "reviewer_subject_commit": ONE40,
            "qa_subject_commit": ONE40,
            "integrated_commit": None,
            "evidence_refs": [EVIDENCE],
            "blocker_history": [],
            "pending_callback": None,
            "closeout_disposition": None,
            "retained_resource_refs": [],
            "close_decision_ref": None,
        },
    }


def native_action(attempt: int = 3) -> dict:
    return {
        "schema": "connlab.serial-native-action",
        "version": 1,
        "action_id": "2" * 64,
        "action": "developer_dispatch",
        "role": "Developer",
        "attempt": attempt,
        "prompt_sha256": "3" * 64,
        "title": "Bounded fix",
        "recorded_at": "2026-08-15T00:00:01Z",
    }


@pytest.mark.parametrize("code,phase", [("REVIEWER_BLOCKED", "development"), ("QA_BLOCKED", "development"), ("INTEGRATION_BLOCKED", "blocked")])
def test_bounded_fix_reentry_is_one_atomic_state_transition(code: str, phase: str) -> None:
    value = active(code, phase=phase)
    original_plan = value["plan_ref"]
    original_scope = copy.deepcopy(value["scope_contract"])
    original_host = {key: value["complex_context"][key] for key in ("host_id", "host_thread_id", "task_branch", "task_worktree")}

    apply_bounded_fix_reentry(value, native_action(), "user:bounded-fix-approved", "2026-08-15T00:00:02Z")

    context = value["complex_context"]
    assert value["phase"] == "development" and value["blocker"] is None
    assert value["plan_ref"] == original_plan and value["scope_contract"] == original_scope
    assert {key: context[key] for key in original_host} == original_host
    assert context["current_attempt"] == 3 and context["current_role"] == "Developer"
    assert context["pending_callback"] == {"state": "dispatch_pending", "action_id": "2" * 64, "role": "Developer", "attempt": 3}
    assert context["blocker_history"][-1]["blocker"]["code"] == code
    assert context["blocker_history"][-1]["decision_ref"] == "user:bounded-fix-approved"


def test_bounded_fix_reentry_fails_closed_on_scope_or_attempt_drift() -> None:
    value = active("REVIEWER_BLOCKED", phase="development")
    value["complex_context"]["approved_code_paths"].append("scripts/drift.py")
    with pytest.raises(SerialContractError, match="BLOCKED_APPROVED_SCOPE_INVALID"):
        apply_bounded_fix_reentry(value, native_action(), "user:approved", "2026-08-15T00:00:02Z")

    value = active("REVIEWER_BLOCKED", phase="development")
    with pytest.raises(SerialContractError, match="BLOCKED_NATIVE_ID_MISMATCH"):
        apply_bounded_fix_reentry(value, native_action(attempt=4), "user:approved", "2026-08-15T00:00:02Z")


def test_role_begin_cannot_bypass_an_unresolved_bounded_fix_blocker() -> None:
    value = active("REVIEWER_BLOCKED", phase="development")
    with pytest.raises(SerialContractError, match="BLOCKED_STATE"):
        complex_transition(value, "begin-role", {"role": "Developer", "native_action": native_action()})


def test_first_phase2_resolution_upgrades_a_pre_phase2_active_context() -> None:
    value = active("REVIEWER_BLOCKED", phase="development")
    value["complex_context"].pop("blocker_history")
    apply_bounded_fix_reentry(value, native_action(), "user:approved", "2026-08-15T00:00:02Z")
    assert value["complex_context"]["blocker_history"][0]["resolution"] == "bounded_fix"


def test_scope_amendment_clears_blocker_and_synchronizes_all_authority_facts() -> None:
    value = active("SCOPE_EXPANDED")
    approved = {"summary": "Approved amendment"}
    scope = copy.deepcopy(value["scope_contract"])
    scope["may_touch"].append("scripts/new.py")
    scope["expected_file_count"] = 3

    apply_scope_amendment(
        value,
        approved,
        scope,
        f"docs/amended-plan.md@{ONE40}#{'4' * 64}",
        "user:scope-amendment-approved",
        "2026-08-15T00:00:02Z",
    )

    assert value["phase"] == "development" and value["blocker"] is None
    assert value["scope_contract"] == scope
    assert value["complex_context"]["approved_code_paths"] == scope["may_touch"]
    assert value["plan_ref"].startswith("docs/amended-plan.md@")
    assert value["approval_ref"] == "user:scope-amendment-approved"
    assert value["complex_context"]["blocker_history"][-1]["resolution"] == "scope_amendment"
    assert value["complex_context"]["pending_callback"] is None


def test_scope_amendment_fails_closed_on_prior_approved_path_drift() -> None:
    value = active("SCOPE_EXPANDED")
    value["complex_context"]["approved_code_paths"] = ["docs/task_board.md"]
    amended = copy.deepcopy(value["scope_contract"])
    amended["may_touch"].append("scripts/new.py")
    amended["expected_file_count"] = 3
    with pytest.raises(SerialContractError, match="BLOCKED_APPROVED_SCOPE_INVALID"):
        apply_scope_amendment(value, {"summary": "amended"}, amended, "plan", "approval", "2026-08-15T00:00:02Z")


def test_snapshot_and_next_action_resume_from_durable_pending_state() -> None:
    value = active("QA_BLOCKED", phase="development")
    control = {"state": "running", "active": value}
    assert next_action(control) == {"command": "reenter-development", "role": "Developer", "requires_user": True}

    apply_bounded_fix_reentry(value, native_action(), "user:approved", "2026-08-15T00:00:02Z")
    snapshot = active_snapshot(control)
    assert snapshot["task_id"] == "TASK_PHASE2"
    assert snapshot["pending_action_id"] == "2" * 64
    assert snapshot["pending_state"] == "dispatch_pending"
    assert snapshot["evidence_count"] == 1 and snapshot["blocker_history_count"] == 1
    assert next_action(control) == {"command": "record-invocation", "role": "Developer", "requires_user": False}


def test_native_action_builder_derives_attempt_and_hashes_without_manual_sha() -> None:
    value = active("REVIEWER_BLOCKED", phase="development")
    action = build_native_action(value, "developer_dispatch", b"exact prompt bytes\n", "Bounded fix", "2026-08-15T00:00:02Z")
    assert action["attempt"] == 3 and action["role"] == "Developer"
    assert action["prompt_sha256"] != ZERO64
    assert len(action["action_id"]) == 64

    value["phase"] = "review"
    value["blocker"] = None
    reviewer = build_native_action(value, "reviewer_dispatch", b"review prompt\n", "Review", "2026-08-15T00:00:03Z")
    assert reviewer["attempt"] == 2
