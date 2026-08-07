from __future__ import annotations

from pathlib import Path


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
