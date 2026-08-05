from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_role_registry_and_orchestrator_are_frozen_historical_material() -> None:
    registry = read("docs/project_management/ROLE_THREAD_REGISTRY.md").lower()
    orchestrator = read(".agents/skills/connlab-lane-orchestrator/SKILL.md").lower()
    protocol = read("docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md").lower()

    assert "frozen legacy" in registry
    assert "frozen legacy" in orchestrator
    assert "frozen legacy" in protocol
    assert "connlab_personal_task.py" in orchestrator


def test_personal_workflow_never_requires_a_role_thread_for_daily_execution() -> None:
    policy = read("docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md")

    assert "Current conversation" in policy
    assert "no role dispatch" in policy.lower()
    assert "implemented_pending_human_review" in policy
