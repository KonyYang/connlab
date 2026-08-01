from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_permanent_roles_are_the_default_task_orchestration_contract() -> None:
    agents = read("AGENTS.md")
    skill = read(".agents/skills/connlab-lane-orchestrator/SKILL.md")
    protocol = read("docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md")

    assert "Classic Persistent Roles And Quick Fixer" in agents
    assert "ROLE_THREAD_REGISTRY.md" in agents
    assert "ConnLab｜全自动编排 Orchestrator" in skill
    assert "Exact native thread IDs remain authoritative" in skill
    assert "permanent Orchestrator" in protocol
    assert "permanent role" in protocol
    assert "task-specific Controller" not in skill
    assert "closeout_archive_authorized" not in protocol


def test_active_bundle_is_frozen_snapshot_and_v2_is_frozen() -> None:
    bundle = read("docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md")
    registry = read("docs/project_management/ROLE_THREAD_REGISTRY.md")
    v2 = read("docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md")

    assert "state:" in bundle
    assert "task_id:" in bundle or "active_task_id:" in bundle
    assert "frozen" in bundle.lower()
    assert "019faaf2-f172-7523-b70f-2c4952acd59f" in registry
    assert "Status: frozen legacy" in v2
    assert "heartbeat remains `PAUSED`" in v2


def test_compact_callback_returns_to_permanent_orchestrator() -> None:
    skill = read(".agents/skills/connlab-lane-orchestrator/SKILL.md")
    protocol = read("docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md")

    for field in ("TASK_ID:", "ROLE:", "STATUS:", "EVIDENCE:", "COMMIT:", "NEXT:", "BLOCKER:"):
        assert field in skill
    assert "permanent Orchestrator" in protocol
    assert "Permanent role conversations are not archived" in protocol
    assert "task-specific Controller" not in protocol
