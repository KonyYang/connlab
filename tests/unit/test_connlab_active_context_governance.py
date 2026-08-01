from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    target = ROOT / path
    assert target.is_file(), f"required governance artifact is missing: {path}"
    return target.read_text(encoding="utf-8")


def test_active_context_contract_is_the_single_normative_reference() -> None:
    contract = read(
        "docs/project_management/"
        "ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md"
    )
    for path in (
        "AGENTS.md",
        "docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md",
        "docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md",
        "docs/project_management/PARALLEL_EXECUTION_MODEL.md",
        "docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md",
        "docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md",
        "docs/project_management/TASK_EXECUTION_SKILL.md",
        "docs/project_management/TASK_REVIEW_CHECKLIST.md",
        ".agents/skills/connlab-lane-orchestrator/SKILL.md",
        ".agents/skills/connlab-planner/SKILL.md",
    ):
        assert "ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md" in read(path)

    for event in ("DEVELOPER_READY", "REVIEWER_BLOCKED", "REVIEWER_PASS", "QA_PASS"):
        assert event in contract
    assert "sole machine authority" in contract
    assert "one transition" in contract
    assert "one dispatch" in contract
    assert "FULL_READ_REQUIRED" in contract
    assert "60 seconds" in contract


def test_context_artifacts_obey_frozen_byte_budgets() -> None:
    budgets = {
        ".agents/skills/connlab-lane-orchestrator/SKILL.md": 16_384,
        ".agents/skills/connlab-planner/SKILL.md": 8_192,
        "docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md": 12_288,
    }
    for path, maximum in budgets.items():
        assert len((ROOT / path).read_bytes()) <= maximum, path


def test_helpers_and_new_tests_remain_bounded() -> None:
    helpers = (
        "scripts/connlab_execution_transition.py",
        "scripts/connlab_active_context.py",
        "scripts/connlab_handoff_contract.py",
    )
    tests = (
        "tests/unit/test_connlab_execution_transition.py",
        "tests/integration/test_connlab_execution_transition_recovery.py",
        "tests/unit/test_connlab_active_context.py",
        "tests/integration/test_connlab_board_closeout_maintenance.py",
        "tests/unit/test_connlab_handoff_contract.py",
        "tests/unit/test_connlab_active_context_governance.py",
    )
    for path in helpers:
        assert len(read(path).splitlines()) < 500, path
    for path in tests:
        assert len(read(path).splitlines()) < 400, path
