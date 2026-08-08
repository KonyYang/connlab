from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.connlab_serial_board import Blocked, approved_payload
from scripts.connlab_serial_complex import SerialContractError, classify_request

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_orchestrator_exposes_active_serial_role_chain() -> None:
    orchestrator = read(".agents/skills/connlab-lane-orchestrator/SKILL.md").lower()
    protocol = read("docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md").lower()

    assert "status: active version-2 runtime" in orchestrator
    assert "developer -> reviewer -> qa -> integrator" in orchestrator
    assert "three user interactions" in protocol
    assert "connlab_personal_task.py" in orchestrator


def test_personal_workflow_keeps_simple_direct_and_complex_automatic() -> None:
    policy = read("docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md")

    assert "directly in the current primary worktree" in policy
    assert "Developer -> Reviewer -> QA -> Integrator" in policy
    assert "three" in policy.lower()
    assert "implemented_pending_human_review" in policy


def test_v2_busy_intake_waits_without_a_queue_action() -> None:
    protocol = read("docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md")
    entry = read("scripts/run_task.ps1")

    assert "BLOCKED_ACTIVE_TASK_RUNNING" in protocol
    assert "stores no request" in protocol
    assert "before repository Git verification" in protocol
    assert "writer-lock acquisition" in protocol
    assert "ActivateNext" not in entry
    assert "`activate-next` parser token" in protocol
    assert "BLOCKED_LEGACY_MODE_FROZEN" in protocol


SUBMIT_FORBIDDEN = {
    "api_contract": False,
    "database": False,
    "schema_or_migration": False,
    "persistence": False,
    "authority": False,
    "public_drive_workflow": False,
    "business_rule_semantics": False,
    "destructive_action": False,
    "external_mutation": False,
    "push_or_release": False,
}


def submit_payload() -> dict[str, object]:
    return {
        "schema": "connlab.serial-task-request",
        "version": 1,
        "task_id": "TASK_CONTRACT",
        "summary": "Freeze the entry contract.",
        "root_cause_clear": True,
        "expected_result_clear": True,
        "may_touch": ["docs/task_board.md"],
        "targeted_validation": ["py -m pytest tests/unit/test_contract.py -q"],
        "requires_independent_review": False,
        "forbidden_categories": SUBMIT_FORBIDDEN,
    }


def approved_request() -> dict[str, object]:
    return {
        "schema": "connlab.personal-task-approved-request",
        "version": 1,
        "task_id": "TASK_CONTRACT",
        "summary": "Freeze the entry contract.",
        "kind": "planned",
        "may_touch": ["docs/task_board.md"],
        "expected_file_count": 1,
        "classification_reason": "Independent review is required.",
        "targeted_validation": ["py -m pytest tests/unit/test_contract.py -q"],
        "forbidden_categories": {
            key: value for key, value in SUBMIT_FORBIDDEN.items() if key != "push_or_release"
        },
    }


def test_submit_classifier_freezes_ten_key_payload_and_rejects_kind() -> None:
    payload = submit_payload()

    assert set(payload) == {
        "schema", "version", "task_id", "summary", "root_cause_clear", "expected_result_clear",
        "may_touch", "targeted_validation", "requires_independent_review", "forbidden_categories",
    }
    assert classify_request(payload) == {
        "classification": "simple",
        "reason_codes": ["SIMPLE_PREDICATES_PASS"],
    }

    payload["kind"] = "planned"
    with pytest.raises(SerialContractError, match="Unknown request fields") as error:
        classify_request(payload)
    assert error.value.code == "BLOCKED_CLASSIFICATION_INVALID"


def test_approve_validator_freezes_nine_key_boundary_and_kind() -> None:
    payload = approved_request()

    _, scope = approved_payload(json.dumps(payload), "TASK_CONTRACT")
    assert set(scope["forbidden_categories"]) == set(SUBMIT_FORBIDDEN) - {"push_or_release"}

    payload["forbidden_categories"] = SUBMIT_FORBIDDEN
    with pytest.raises(Blocked, match="Forbidden-category checks are incomplete") as copied_categories:
        approved_payload(json.dumps(payload), "TASK_CONTRACT")
    assert copied_categories.value.code == "BLOCKED_APPROVED_SCOPE_INVALID"

    payload = approved_request()
    payload.pop("kind")
    with pytest.raises(Blocked, match="JSON keys do not match"):
        approved_payload(json.dumps(payload), "TASK_CONTRACT")

    payload = approved_request()
    payload["kind"] = "simple"
    with pytest.raises(Blocked, match="schema/version/kind is invalid"):
        approved_payload(json.dumps(payload), "TASK_CONTRACT")


def test_powershell_entry_mapping_keeps_close_payload_free() -> None:
    entry = read("scripts/run_task.ps1")

    assert '"Submit" {' in entry
    assert '"--request-json", $RequestJson' in entry
    assert '"Approve" {' in entry
    assert '"--approved-request-json", $ApprovedRequestJson' in entry
    assert '"--plan-ref", $PlanRef, "--approval-ref", $ApprovalRef' in entry
    assert '"Close" {' in entry
    assert 'throw "Close requires -DecisionRef containing the explicit User decision."' in entry
    assert '"--decision-ref", $DecisionRef' in entry
    assert "CloseJson" not in entry


def test_routing_recovery_and_ui_smoke_contract_is_mirrored() -> None:
    orchestrator = read(".agents/skills/connlab-lane-orchestrator/SKILL.md")
    protocol = read("docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md")

    for document in (orchestrator, protocol):
        assert "connlab.serial-task-request" in document
        assert "connlab.personal-task-approved-request" in document
        assert "`kind`" in document
        assert "is forbidden" in document
        assert "push_or_release" in document
        assert "-Action Close -DecisionRef" in document
        assert "gpt-5.6-terra" in document
        assert "gpt-5.6-sol" in document
        assert "qa_bounded_low" in document
        assert "Luna is not used" in document
        assert "MODEL_ROUTE_REASON" in document
        assert "ACTUAL_MODEL_ROUTING" in document
        assert "reuses" in document
        assert "recorded host" in document
        assert "never duplicates" in document
        assert "activation" in document
        assert "user-visible UI change" in document
        assert "networkidle" in document
