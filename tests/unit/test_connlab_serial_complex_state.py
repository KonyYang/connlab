from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest

from scripts.connlab_personal_task import transition
from scripts.connlab_serial_complex import (
    SerialContractError,
    callback_transition,
    complex_transition,
    validate_complex_blocker,
)


ZERO40 = "0" * 40
ZERO64 = "0" * 64
EVIDENCE = f"docs/lane_evidence/example.md@{ZERO40}#{ZERO64}"


CALLBACK_CASES = [
    ("Planner", "ready", "User", "awaiting_user_approval", None),
    ("Planner", "discovery_required", "User", "blocked", "DISCOVERY_REQUIRED"),
    ("Developer", "ready", "Reviewer", "review", None),
    ("Developer", "blocked", "User", "blocked", "DEVELOPER_BLOCKED"),
    ("Reviewer", "pass", "QA", "qa", None),
    ("Reviewer", "blocked", "Developer", "development", "REVIEWER_BLOCKED"),
    ("QA", "pass", "Integrator", "integration", None),
    ("QA", "blocked", "Developer", "development", "QA_BLOCKED"),
    ("Integrator", "pass", "User", "integration", None),
    ("Integrator", "blocked", "User", "blocked", "INTEGRATION_BLOCKED"),
]


def failure_proof(operation: str = "targeted-tests") -> dict:
    return {
        "schema": "connlab.serial-failure-proof",
        "version": 1,
        "operation": operation,
        "command": ["py", "-m", "pytest"],
        "exit_code": 1,
        "summary": "bounded failure",
        "recorded_at": "2026-08-06T00:00:00Z",
    }


def blocker(code: str, stage: str, **overrides: object) -> dict:
    value = {
        "schema": "connlab.serial-task-blocker",
        "version": 1,
        "code": code,
        "stage": stage,
        "reason": "bounded reason",
        "dirty_paths": [],
        "failed_validation": None,
        "subject_commit": None,
        "evidence_ref": None,
        "native_action_id": None,
        "related_ids": [],
        "retryable": True,
        "requires_user": True,
        "resume_phase": stage,
        "recorded_at": "2026-08-06T00:00:00Z",
    }
    value.update(overrides)
    return value


@pytest.mark.parametrize("role,status,next_role,target,blocker_code", CALLBACK_CASES)
def test_callback_table_is_exact(role: str, status: str, next_role: str, target: str, blocker_code: str | None) -> None:
    supplied_blocker = None
    if blocker_code:
        supplied_blocker = blocker(
            blocker_code,
            {"Planner": "planning", "Developer": "development", "Reviewer": "review", "QA": "qa", "Integrator": "integration"}[role],
            evidence_ref=EVIDENCE,
            subject_commit=ZERO40 if blocker_code != "DISCOVERY_REQUIRED" else None,
            related_ids=["finding-1"] if blocker_code in {"DISCOVERY_REQUIRED", "REVIEWER_BLOCKED", "QA_BLOCKED"} else [],
            failed_validation=failure_proof() if blocker_code in {"DEVELOPER_BLOCKED", "QA_BLOCKED", "INTEGRATION_BLOCKED"} else None,
            retryable=blocker_code != "INTEGRATION_BLOCKED",
            requires_user=blocker_code not in {"REVIEWER_BLOCKED", "QA_BLOCKED"},
            resume_phase={
                "DISCOVERY_REQUIRED": "planning",
                "DEVELOPER_BLOCKED": "development",
                "REVIEWER_BLOCKED": "development",
                "QA_BLOCKED": "development",
                "INTEGRATION_BLOCKED": "integration",
            }.get(blocker_code),
        )
    callback = {
        "schema": "connlab.serial-callback",
        "version": 1,
        "task_id": "TASK_EXAMPLE",
        "role": role,
        "status": status,
        "subject_commit": ZERO40,
        "evidence": EVIDENCE,
        "next": next_role,
        "blocker": supplied_blocker,
    }

    transition = callback_transition(callback)

    assert transition["target_phase"] == target
    assert transition["blocker_code"] == blocker_code
    assert transition["integration_ready"] is (role == "Integrator" and status == "pass")


def test_callback_alias_and_blocker_on_pass_fail_closed() -> None:
    callback = {
        "schema": "connlab.serial-callback",
        "version": 1,
        "task_id": "TASK_EXAMPLE",
        "role": "Reviewer",
        "status": "passed",
        "subject_commit": ZERO40,
        "evidence": EVIDENCE,
        "next": "QA",
        "blocker": None,
    }
    with pytest.raises(SerialContractError, match="BLOCKED_CALLBACK_INVALID"):
        callback_transition(callback)
    callback["status"] = "pass"
    callback["blocker"] = blocker("REVIEWER_BLOCKED", "review")
    with pytest.raises(SerialContractError, match="BLOCKED_CALLBACK_INVALID"):
        callback_transition(callback)


BLOCKER_CASES = [
    ("DISCOVERY_REQUIRED", "planning", {"evidence_ref": EVIDENCE, "related_ids": ["missing-1"]}, True, True, "planning"),
    ("APPROVAL_REQUIRED", "awaiting_user_approval", {"related_ids": ["plan@ref"]}, True, True, "awaiting_user_approval"),
    ("DEVELOPER_BLOCKED", "development", {"evidence_ref": EVIDENCE, "subject_commit": ZERO40, "failed_validation": failure_proof()}, True, True, "development"),
    ("REVIEWER_BLOCKED", "review", {"evidence_ref": EVIDENCE, "subject_commit": ZERO40, "related_ids": ["finding-1"]}, True, False, "development"),
    ("QA_BLOCKED", "qa", {"evidence_ref": EVIDENCE, "subject_commit": ZERO40, "failed_validation": failure_proof(), "related_ids": ["finding-1"]}, True, False, "development"),
    ("INTEGRATION_BLOCKED", "integration", {"evidence_ref": EVIDENCE, "subject_commit": ZERO40, "failed_validation": failure_proof("git-proof")}, False, True, "integration"),
    ("DIRTY_WORKTREE", "development", {"dirty_paths": ["backend/example.py"], "subject_commit": ZERO40}, True, True, "development"),
    ("CALLBACK_PENDING", "review", {"native_action_id": ZERO64, "related_ids": ["attempt-1"]}, True, False, "review"),
    ("ARCHIVE_PENDING", "closing", {"native_action_id": ZERO64, "related_ids": ["thread-1"]}, True, True, "closing"),
    ("ARCHIVE_PENDING_UNVERIFIABLE", "closing", {"native_action_id": ZERO64, "evidence_ref": EVIDENCE, "related_ids": ["thread-1"]}, True, True, "closing"),
    ("WORKTREE_RETIREMENT_PENDING", "closing", {"dirty_paths": ["tmp/example"], "related_ids": ["host-1"]}, True, True, "closing"),
    ("SCOPE_EXPANDED", "planning", {"dirty_paths": ["extra.py"], "evidence_ref": EVIDENCE}, True, True, "planning"),
    ("VALIDATION_FAILED", "qa", {"subject_commit": ZERO40, "failed_validation": failure_proof()}, True, True, "qa"),
    ("NATIVE_ACTION_FAILED", "development", {"native_action_id": ZERO64, "failed_validation": failure_proof("native"), "related_ids": ["invocation-1"]}, True, True, "development"),
    ("CUTOVER_FAILED", "human_review", {"subject_commit": ZERO40, "failed_validation": failure_proof("cutover"), "evidence_ref": EVIDENCE, "related_ids": ["cutover-1"]}, False, True, "human_review"),
]


@pytest.mark.parametrize("code,stage,required,retryable,requires_user,resume", BLOCKER_CASES)
def test_blocker_policy_table_is_exact(code: str, stage: str, required: dict, retryable: bool, requires_user: bool, resume: str) -> None:
    value = blocker(
        code,
        stage,
        **required,
        retryable=retryable,
        requires_user=requires_user,
        resume_phase=resume,
    )
    assert validate_complex_blocker(value) == value


def test_blocker_rejects_wrong_policy_and_populated_forbidden_field() -> None:
    value = blocker(
        "REVIEWER_BLOCKED",
        "review",
        evidence_ref=EVIDENCE,
        subject_commit=ZERO40,
        related_ids=["finding-1"],
        retryable=False,
        requires_user=False,
        resume_phase="development",
    )
    with pytest.raises(SerialContractError, match="BLOCKED_BLOCKER_INVALID"):
        validate_complex_blocker(value)


def active(phase: str, role: str | None = None) -> dict:
    return {
        "task_id": "TASK_EXAMPLE",
        "phase": phase,
        "blocker": None,
        "complex_context": {
            "current_role": role,
            "current_attempt": 1,
            "pending_callback": None,
            "role_invocations": [],
            "host_id": None,
            "host_thread_id": None,
            "task_branch": None,
            "task_worktree": None,
            "base_sha": ZERO40,
            "head_sha": ZERO40,
            "developer_subject_commit": None,
            "reviewer_subject_commit": None,
            "qa_subject_commit": None,
            "integrated_commit": None,
            "evidence_refs": [],
            "closeout_disposition": None,
            "retained_resource_refs": [],
            "close_decision_ref": None,
        },
    }


def retained_closeout(**overrides: object) -> dict:
    value = {
        "schema": "connlab.serial-closeout",
        "version": 1,
        "action_id": ZERO64,
        "disposition": "retained",
        "task_id": "TASK_EXAMPLE",
        "thread_id": "thread-1",
        "worktree": "D:/tmp/task-example",
        "branch": "codex/task-example",
        "head_sha": "4" * 40,
        "clean": True,
        "integrated_commit": "5" * 40,
        "evidence_ref": EVIDENCE,
        "reason": "retained_nonblocking_manual_maintenance",
        "recorded_at": "2026-08-06T00:00:00Z",
    }
    value.update(overrides)
    return value


def closing_active() -> dict:
    value = active("closing")
    value["complex_context"].update(
        host_thread_id="thread-1",
        host_id="host-1",
        task_branch="codex/task-example",
        task_worktree="D:/tmp/task-example",
        head_sha="4" * 40,
        integrated_commit="5" * 40,
        worktree_lifecycle="integrated",
        close_decision_ref="User close",
    )
    return value


def native_action(action: str, role: str) -> dict:
    return {
        "schema": "connlab.serial-native-action", "version": 1, "action_id": ZERO64,
        "action": action, "role": role, "attempt": 1, "prompt_sha256": ZERO64,
        "title": f"ConnLab {role}", "recorded_at": "2026-08-06T00:00:00Z",
    }


def test_role_order_blocks_reviewer_before_developer_handoff() -> None:
    value = active("development")
    with pytest.raises(SerialContractError, match="BLOCKED_ROLE_ORDER"):
        complex_transition(value, "begin-role", {"role": "Reviewer", "native_action": native_action("reviewer_dispatch", "Reviewer")})


def test_begin_and_record_developer_invocation_survive_recovery() -> None:
    value = active("development")
    value["complex_context"].update(host_id="host-1", host_thread_id="thread-1")
    complex_transition(value, "begin-role", {"role": "Developer", "native_action": native_action("developer_dispatch", "Developer")})
    assert value["complex_context"]["pending_callback"]["state"] == "dispatch_pending"
    invocation = {
        "schema": "connlab.serial-invocation", "version": 1, "action_id": ZERO64,
        "role": "Developer", "attempt": 1, "thread_id": None, "agent_id": "agent-1",
        "host_id": "host-1", "status": "started", "recorded_at": "2026-08-06T00:00:01Z",
    }
    complex_transition(value, "record-invocation", {"invocation": invocation})
    assert value["complex_context"]["pending_callback"]["state"] == "callback_pending"
    assert value["complex_context"]["role_invocations"] == [invocation]


def test_callback_consumption_advances_exact_phase_and_subject() -> None:
    value = active("development", "Developer")
    value["complex_context"]["pending_callback"] = {"state": "callback_pending", "action_id": ZERO64, "role": "Developer", "attempt": 1}
    callback = {
        "schema": "connlab.serial-callback", "version": 1, "task_id": "TASK_EXAMPLE",
        "role": "Developer", "status": "ready", "subject_commit": "4" * 40,
        "evidence": EVIDENCE, "next": "Reviewer", "blocker": None,
    }
    complex_transition(value, "consume-callback", {"callback": callback})
    assert value["phase"] == "review"
    assert value["complex_context"]["developer_subject_commit"] == "4" * 40
    assert value["complex_context"]["pending_callback"] is None

    value["retryable"] = True
    value["dirty_paths"] = ["unexpected.py"]
    with pytest.raises(SerialContractError, match="BLOCKED_BLOCKER_INVALID"):
        validate_complex_blocker(value)


def test_exact_retained_closeout_is_idempotent_and_releases_after_user_close() -> None:
    value = closing_active()
    closeout = retained_closeout()

    first = complex_transition(value, "record-closeout", {"closeout": closeout})
    second = complex_transition(value, "record-closeout", {"closeout": closeout})
    finalized = complex_transition(value, "finalize-close", {"decision_ref": "User close"})

    assert first == "ALLOW_RECORD_CLOSEOUT"
    assert second == "NOOP_CLOSEOUT_ALREADY_RECORDED"
    assert finalized == "ALLOW_FINALIZE_CLOSE"
    assert value["complex_context"]["closeout_disposition"] == closeout
    assert value["complex_context"]["retained_resource_refs"] == [EVIDENCE]
    assert value["complex_context"]["worktree_lifecycle"] == "retained"
    assert value["_release_active"] is True


@pytest.mark.parametrize(
    ("mutate", "code"),
    [
        (lambda active_value, proof: proof.update(clean=False), "BLOCKED_WORKTREE_FACTS"),
        (lambda active_value, proof: proof.update(thread_id="other-thread"), "BLOCKED_WORKTREE_FACTS"),
        (lambda active_value, proof: active_value["complex_context"].update(current_role="Integrator"), "BLOCKED_CALLBACK_PENDING"),
        (lambda active_value, proof: active_value["complex_context"].update(pending_callback={"state": "callback_pending"}), "BLOCKED_CALLBACK_PENDING"),
    ],
)
def test_retained_closeout_fails_closed_without_mutating_resources(mutate, code: str) -> None:
    value = closing_active()
    closeout = retained_closeout()
    before = value["complex_context"].copy()
    mutate(value, closeout)

    with pytest.raises(SerialContractError, match=code):
        complex_transition(value, "record-closeout", {"closeout": closeout})

    assert value["phase"] == "closing"
    assert value["complex_context"].get("closeout_disposition") is None
    assert value["complex_context"].get("retained_resource_refs") == []
    assert value["complex_context"]["task_worktree"] == before["task_worktree"]


def test_finalize_retained_closeout_releases_active_without_starting_fifo() -> None:
    active_value = closing_active()
    closeout = retained_closeout()
    active_value["complex_context"].update(
        closeout_disposition=closeout,
        retained_resource_refs=[EVIDENCE],
        worktree_lifecycle="retained",
    )
    queued = {"task_id": "TASK_NEXT", "enqueue_sequence": 1}
    control = {"version": 2, "state": "running", "active": active_value, "queue": [queued]}
    args = Namespace(
        command="finalize-close",
        task_id="TASK_EXAMPLE",
        decision_ref="User close",
        role=None,
        native_action_json=None,
        invocation_json=None,
        callback_json=None,
        worktree_json=None,
        integration_json=None,
        closeout_json=None,
    )

    code, changed, _ = transition(args, Path.cwd(), control)

    assert (code, changed) == ("ALLOW_FINALIZE_CLOSE", True)
    assert control["state"] == "idle"
    assert control["active"] is None
    assert control["queue"] == [queued]
    assert control["last_closed"]["disposition"] == "retained"
    assert control["last_closed"]["closeout_evidence_ref"] == EVIDENCE
    assert control["last_closed"]["retained_resources"] == {
        "thread_id": "thread-1",
        "worktree": "D:/tmp/task-example",
        "branch": "codex/task-example",
        "head_sha": "4" * 40,
    }
