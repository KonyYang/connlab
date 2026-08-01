from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "connlab_execution_gate.ps1"
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


def read(path: str) -> str:
    target = ROOT / path
    assert target.is_file(), f"required governance artifact is missing: {path}"
    return target.read_text(encoding="utf-8")


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "governance-tests@example.invalid")
    _git(repo, "config", "user.name", "Governance Tests")
    (repo / "docs").mkdir()
    return repo


def _write_control(repo: Path, control: dict[str, object]) -> None:
    payload = json.dumps(control, indent=2)
    (repo / "docs" / "task_board.md").write_text(
        f"# Board\n\n{BEGIN}\n```json\n{payload}\n```\n{END}\n",
        encoding="utf-8",
    )


def _base_control(**overrides: object) -> dict[str, object]:
    control: dict[str, object] = {
        "schema": "connlab.execution-control",
        "version": 1,
        "wip_limit": 1,
        "execution_token_owner": None,
        "execution_state": "idle",
        "active": None,
        "queue": [],
        "paused": None,
        "quick_fix": None,
        "residuals": [],
        "parallel_exception": None,
        "last_governance_commit": "fixture",
        "evidence": "fixture.md",
    }
    control.update(overrides)
    return control


def _run_gate(repo: Path, intent: str, task_id: str, lane: str) -> tuple[int, dict[str, object]]:
    completed = subprocess.run(
        [
            "powershell.exe", "-NoProfile", "-File", str(GATE),
            "-Intent", intent, "-TaskId", task_id, "-Lane", lane,
            "-RepositoryRoot", str(repo), "-AllowTestRepositoryRoot", "-Json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode, json.loads(completed.stdout)


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


def test_semantically_neutral_button_label_uses_executable_qf1_fast_path(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    _write_control(repo, _base_control())
    _git(repo, "add", "docs/task_board.md", "seed.txt")
    _git(repo, "commit", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    worktree = tmp_path / "qf-lane"
    _git(repo, "worktree", "add", "-b", "lane/qf-button-label", str(worktree), base)
    quick_fix = {
        "task_id": "TASK_QF_BUTTON_LABEL",
        "lane": "qf-button-label",
        "role": "Quick Fixer",
        "risk_gate": "QF-1",
        "goal": "Change button label from Close to Dismiss",
        "why_safe": "The click action, permission, authority, and lifecycle stay unchanged",
        "may_touch": ["frontend/button.tsx"],
        "must_not_touch": ["api", "schema", "authority"],
        "locked_paths": ["frontend/button.tsx"],
        "targeted_validation": ["button smoke"],
        "required_gates": ["Integrator"],
        "planner_required": False,
        "full_plan_required": False,
        "qa_required": False,
        "branch": "lane/qf-button-label",
        "worktree": str(worktree),
        "base_sha": base,
        "head_sha": base,
        "evidence": "qf-button-label.md",
        "accepted_head": None,
        "accepted_on_master": False,
        "residual_owner": None,
    }
    _write_control(
        repo,
        _base_control(
            execution_token_owner="TASK_QF_BUTTON_LABEL",
            execution_state="quick_fix_running",
            quick_fix=quick_fix,
        ),
    )

    code, output = _run_gate(
        repo, "ImplementationDispatch", "TASK_QF_BUTTON_LABEL", "qf-button-label"
    )

    assert code == 0
    assert output["code"] == "ALLOW_DISPATCH"
    assert output["execution_state"] == "quick_fix_running"


def test_api_schema_authority_qf4_capsule_is_rejected_dynamically(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    quick_fix = {
        "task_id": "TASK_QF4",
        "lane": "qf4",
        "role": "Quick Fixer",
        "risk_gate": "QF-4",
        "goal": "Change API schema authority",
        "why_safe": "not applicable",
        "may_touch": ["api", "schema", "authority"],
        "must_not_touch": ["product/runtime"],
        "locked_paths": ["api"],
        "targeted_validation": ["api tests"],
        "required_gates": ["Planner", "User"],
        "planner_required": True,
        "full_plan_required": True,
        "qa_required": True,
        "branch": "lane/qf4",
        "worktree": "planned",
        "base_sha": "a" * 40,
        "head_sha": "a" * 40,
        "evidence": "qf4.md",
        "accepted_head": None,
        "accepted_on_master": False,
        "residual_owner": None,
    }
    _write_control(
        repo,
        _base_control(
            execution_token_owner="TASK_QF4",
            execution_state="quick_fix_running",
            quick_fix=quick_fix,
        ),
    )

    code, output = _run_gate(repo, "Inspect", "TASK_QF4", "qf4")

    assert code != 0
    assert output["code"] == "BLOCKED_QUICK_FIX_RISK"


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
    assert "ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md" in run_task
    assert "one durable transition and one dispatch" in run_task


def test_run_task_queue_path_never_invokes_codex(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "scripts").mkdir()
    (repo / "tasks").mkdir()
    shutil.copy2(ROOT / "scripts" / "run_task.ps1", repo / "scripts" / "run_task.ps1")
    shutil.copy2(GATE, repo / "scripts" / GATE.name)
    sentinel = tmp_path / "codex-invoked.txt"
    (repo / "scripts" / "_codex_runtime.ps1").write_text(
        "function Invoke-CodexCli { param([string]$Prompt) "
        "[System.IO.File]::WriteAllText($env:CONNLAB_TEST_SENTINEL, 'called'); return 0 }\n",
        encoding="utf-8",
    )
    (repo / "tasks" / "TASK_QUEUED.md").write_text("# queued\n", encoding="utf-8")
    active = {
        "task_id": "TASK_OWNER",
        "lane": "task-owner",
        "role": "Developer",
        "branch": "lane/task-owner",
        "worktree": "owner-worktree",
        "base_sha": "a" * 40,
        "head_sha": "b" * 40,
        "locked_paths": ["owner/path"],
        "evidence": "owner.md",
    }
    _write_control(
        repo,
        _base_control(
            execution_token_owner="TASK_OWNER",
            execution_state="implementation_running",
            active=active,
        ),
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "queue fixture")
    lane = tmp_path / "stale-run-task-lane"
    _git(repo, "worktree", "add", "-b", "lane/stale-run-task", str(lane), "HEAD")
    stale_active = dict(active)
    stale_active.update(task_id="TASK_QUEUED", lane="task-queued")
    _write_control(
        lane,
        _base_control(
            execution_token_owner="TASK_QUEUED",
            execution_state="implementation_running",
            active=stale_active,
        ),
    )
    env = os.environ.copy()
    env["CONNLAB_TEST_SENTINEL"] = str(sentinel)

    completed = subprocess.run(
        [
            "powershell.exe", "-NoProfile", "-File", str(lane / "scripts" / "run_task.ps1"),
            "-Task", "TASK_QUEUED",
        ],
        cwd=lane,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "QUEUE_REQUIRED" in completed.stdout
    assert not sentinel.exists()


def test_run_task_preview_is_reference_only_and_within_dispatch_template_budget(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "scripts").mkdir()
    (repo / "tasks").mkdir()
    shutil.copy2(ROOT / "scripts" / "run_task.ps1", repo / "scripts" / "run_task.ps1")
    shutil.copy2(GATE, repo / "scripts" / GATE.name)
    (repo / "scripts" / "_codex_runtime.ps1").write_text(
        "function Invoke-CodexCli { throw 'Preview must not invoke Codex' }\n",
        encoding="utf-8",
    )
    (repo / "tasks" / "TASK_PREVIEW.md").write_text("# Task\n", encoding="utf-8")
    _write_control(repo, _base_control())
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "preview fixture")

    completed = subprocess.run(
        ["powershell.exe", "-NoProfile", "-File", str(repo / "scripts" / "run_task.ps1"), "-Task", "TASK_PREVIEW", "-Preview"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert len(completed.stdout.encode("utf-8")) <= 2048
    assert "ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md" in completed.stdout
    assert "git worktrees:" not in completed.stdout
