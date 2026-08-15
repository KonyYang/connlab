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


def test_simple_fast_path_is_bounded_without_becoming_another_task_tier() -> None:
    agents = " ".join(read("AGENTS.md").split()).lower()
    orchestrator = " ".join(
        read(".agents/skills/connlab-lane-orchestrator/SKILL.md").split()
    )
    protocol = " ".join(
        read("docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md").split()
    )

    for contract in (agents, orchestrator, protocol):
        assert "simple-fast" in contract
        assert "not a task kind, state, role, or approval" in contract

    assert "one implementation path" in protocol
    assert "one existing test path" in protocol
    assert "one targeted test command" in protocol
    assert "does not load `$impeccable`" in protocol
    assert agents.count("except for protocol-eligible `simple-fast`") == 2
    assert "does not run a production build or browser smoke" in protocol
    assert "must not probe, install, or download Playwright" in protocol
    assert "fall back to ordinary `simple`" in protocol
    assert "one to three minutes" in protocol
    assert "report the concrete delay once at five minutes" in protocol


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


def test_orchestrator_delegates_detailed_runtime_contract_to_protocol() -> None:
    orchestrator = read(".agents/skills/connlab-lane-orchestrator/SKILL.md")
    protocol = read("docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md")

    assert "SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md" in orchestrator
    assert "connlab.serial-task-request" not in orchestrator
    assert "ACTUAL_MODEL_ROUTING" not in orchestrator
    assert len(orchestrator.splitlines()) <= 100

    assert "connlab.serial-task-request" in protocol
    assert "connlab.personal-task-approved-request" in protocol
    assert "-Action Close -DecisionRef" in protocol
    assert "ACTUAL_MODEL_ROUTING" in protocol
    assert "networkidle" in protocol


def test_current_workflow_documents_do_not_conflict_on_role_dispatch() -> None:
    agents = read("AGENTS.md")
    execution = read("docs/project_management/TASK_EXECUTION_SKILL.md")
    planning = read("docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md")

    assert "## 14." not in agents
    assert "Classic Persistent Roles" not in agents
    assert "Quick Fixer Fast Path" not in agents
    assert "Never dispatch roles" not in execution
    assert "No Planner role conversation" not in planning
    assert "queued planned intake" not in planning
    assert "Developer -> Reviewer -> QA -> Integrator" in execution
    assert "read-only Planner" in planning


def test_orchestrator_scopes_supporting_skills_by_role_and_risk() -> None:
    orchestrator = read(".agents/skills/connlab-lane-orchestrator/SKILL.md")
    normalized = " ".join(orchestrator.split())

    for skill in (
        "$tdd",
        "$diagnosing-bugs",
        "$code-review",
        "$codebase-design",
        "$grilling",
        "$playwright",
        "$impeccable",
    ):
        assert skill in orchestrator
    assert "hard, repeated, flaky, or unexplained" in normalized
    assert "material product ambiguity" in normalized


def test_legacy_workflow_skills_are_not_implicitly_injected() -> None:
    for skill in ("connlab-planner", "connlab-controlled-lane"):
        metadata = read(f".agents/skills/{skill}/agents/openai.yaml")
        assert "allow_implicit_invocation: false" in metadata


def test_protocol_assigns_one_final_matrix_and_fail_fast_integration() -> None:
    orchestrator = " ".join(
        read(".agents/skills/connlab-lane-orchestrator/SKILL.md").split()
    )
    protocol = " ".join(
        read("docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md").split()
    )

    assert "any later implementation or test change invalidates that result" in orchestrator
    assert "Reviewer runs risk-targeted tests" in orchestrator
    assert "QA is the only default independent repeat of the complete approved matrix" in protocol
    assert "must not mutate board, phase, validation, or fixture state" in protocol
    assert "Integrator does not repeat the complete pytest matrix" in protocol
    assert "stop remaining unrelated checks" in protocol
    assert "request the complete command's required permission boundary first" in protocol
    assert "Never write a truncated SHA" in protocol
    assert "approximate elapsed time" in protocol


def test_protocol_records_phase2_runtime_as_the_existing_v2_authority() -> None:
    protocol = read("docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md")
    compact = " ".join(protocol.split())

    assert "Phase 2 runtime recovery" in protocol
    assert "REVIEWER_BLOCKED / QA_BLOCKED / INTEGRATION_BLOCKED -> development" in compact
    assert "one atomic amendment transition" in compact
    assert "active_snapshot" in protocol and "next_action" in protocol
    assert "scripts/connlab_serial_payload.py native-action" in compact
    assert "does not create another authority or task tier" in compact
