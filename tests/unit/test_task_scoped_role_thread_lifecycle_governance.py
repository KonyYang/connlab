from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v1_lite_is_the_default_task_orchestration_contract() -> None:
    agents = read("AGENTS.md")
    skill = read(".agents/skills/connlab-lane-orchestrator/SKILL.md")
    protocol = read("docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md")

    assert "V1-Lite Task-Scoped Role Lifecycle" in agents
    assert "ACTIVE_TASK_THREAD_BUNDLE.md" in agents
    assert "<THREAD_LABEL>｜主控" in skill
    assert "Never use the full `TASK_ID` as the native sidebar title" in skill
    assert "<thread_label>｜规划" in protocol
    assert "exact native thread ID" in protocol
    assert "task-specific Controller" in skill
    assert "closeout_archive_authorized" in protocol


def test_active_bundle_has_task_scoped_title_schema_and_v2_is_frozen() -> None:
    bundle = read("docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md")
    registry = read("docs/project_management/ROLE_THREAD_REGISTRY.md")
    v2 = read("docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md")

    assert "state:" in bundle
    assert "task_id:" in bundle or "active_task_id:" in bundle
    assert "thread_label:" in bundle
    assert "019faaf2-f172-7523-b70f-2c4952acd59f" in registry
    assert "Status: frozen legacy" in v2
    assert "heartbeat remains `PAUSED`" in v2


def test_compact_callback_and_archive_order_are_frozen() -> None:
    skill = read(".agents/skills/connlab-lane-orchestrator/SKILL.md")
    protocol = read("docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md")

    for field in ("TASK_ID:", "ROLE:", "STATUS:", "EVIDENCE:", "COMMIT:", "NEXT:"):
        assert field in skill
    archive_order = (
        "Planner -> Developer -> Reviewer -> QA -> Integrator -> task-specific Controller"
    )
    assert archive_order in protocol
