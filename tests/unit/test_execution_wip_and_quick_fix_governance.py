from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    target = ROOT / path
    assert target.is_file(), f"required governance artifact is missing: {path}"
    return target.read_text(encoding="utf-8")


def test_one_normative_policy_owns_wip_token_and_reconciliation_contract() -> None:
    policy = read("docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md")
    agents = read("AGENTS.md")
    board = read("docs/task_board.md")

    assert "wip_limit = 1" in policy
    assert "merge current `master` into the preserved lane" in policy
    assert "never rebase" in policy
    assert "EXECUTION_WIP_AND_QUICK_FIX_POLICY.md" in agents
    assert board.count("<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->") == 1
    assert board.count("<!-- CONNLAB_EXECUTION_CONTROL_END -->") == 1
    for key in (
        '"wip_limit"',
        '"execution_token_owner"',
        '"execution_state"',
        '"queue"',
        '"paused"',
        '"quick_fix"',
        '"residuals"',
        '"parallel_exception"',
    ):
        assert key in board


def test_compact_quick_fix_capsule_is_mandatory_and_proportionate() -> None:
    policy = read("docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md")
    orchestrator = read(".agents/skills/connlab-lane-orchestrator/SKILL.md")

    for field in (
        "Goal",
        "Why Safe",
        "May Touch",
        "Must Not Touch",
        "Locked Paths",
        "Targeted Validation",
        "Risk Gate",
        "Branch / worktree / base",
        "Evidence path",
    ):
        assert field in policy
    assert "must use the compact Quick Fix capsule" in orchestrator
    assert "must not route an independent Planner" in orchestrator
    assert "QF-1" in policy and "Quick Fixer -> Integrator" in policy
    assert "QF-2" in policy and "Quick Fixer -> Reviewer -> Integrator" in policy
    assert "QF-3" in policy and "Quick Fixer -> Reviewer -> QA -> Integrator" in policy
    assert "QF-4" in policy and "full Planner/User flow" in policy


def test_semantic_copy_and_authority_changes_cannot_use_qf1() -> None:
    policy = read("docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md")

    assert "Submit -> Approve" in policy
    assert "Delete -> Archive" in policy
    assert "Confirm Matrix -> Save" in policy
    assert "API contract" in policy
    assert "schema" in policy
    assert "public-drive" in policy
    assert "QF-4" in policy


def test_referencing_protocols_do_not_restore_default_parallel_or_v1_lite_routing() -> None:
    paths = (
        "docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md",
        "docs/project_management/PARALLEL_EXECUTION_MODEL.md",
        "docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md",
        "docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md",
        ".agents/skills/connlab-lane-orchestrator/SKILL.md",
        ".agents/skills/connlab-planner/SKILL.md",
    )
    for path in paths:
        text = read(path)
        assert "EXECUTION_WIP_AND_QUICK_FIX_POLICY.md" in text
        assert "task-specific Controller" not in text
        assert "new task-specific" not in text
    model = read("docs/project_management/PARALLEL_EXECUTION_MODEL.md")
    assert "explicit User-approved parallel exception" in model
    assert "WIP=1" in model


def test_controlled_lane_v2_remains_frozen_and_unmodified_by_the_new_policy() -> None:
    agents = read("AGENTS.md")
    protocol = read("docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md")
    v2 = read("docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md")

    assert "Controlled Lane V2" in agents and "frozen" in agents.lower()
    assert "heartbeat remains `PAUSED`" in protocol
    assert "Status: frozen legacy" in v2


def test_run_task_gates_before_codex_routing_and_keeps_queue_governance_read_only() -> None:
    run_task = read("scripts/run_task.ps1")

    gate_index = run_task.index("connlab_execution_gate.ps1")
    routing_index = run_task.index("Invoke-CodexCli")
    assert gate_index < routing_index
    assert '"StartTask"' in run_task
    assert "QUEUE_REQUIRED routes queue governance only" in run_task
    assert "never dispatches implementation or creates a worktree" in run_task
