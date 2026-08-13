from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_worktree_script_exposes_json_dry_run_and_adopt_without_force() -> None:
    text = (ROOT / "scripts" / "connlab_lane_worktree.ps1").read_text(encoding="utf-8")

    assert '"Adopt"' in text
    assert "[switch]$Json" in text
    assert "[switch]$DryRun" in text
    assert "worktree\", \"remove\", \"--force\"" not in text
    assert "branch\", \"-D\"" not in text
    assert "reset --hard" not in text


def test_worktree_create_requires_task_id_and_execution_gate() -> None:
    text = (ROOT / "scripts" / "connlab_lane_worktree.ps1").read_text(encoding="utf-8")

    assert "[string]$TaskId" in text
    assert "connlab_execution_gate.ps1" in text
    assert '"CreateWorktree"' in text
    assert "ALLOW_WORKTREE_CREATE" in text


def test_worktree_create_queue_result_never_creates_branch_or_worktree(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "worktree-tests@example.invalid")
    _git(repo, "config", "user.name", "Worktree Tests")
    (repo / "docs").mkdir()
    (repo / "scripts").mkdir()
    shutil.copy2(
        ROOT / "scripts" / "connlab_execution_gate.ps1",
        repo / "scripts" / "connlab_execution_gate.ps1",
    )
    shutil.copy2(
        ROOT / "scripts" / "connlab_lane_worktree.ps1",
        repo / "scripts" / "connlab_lane_worktree.ps1",
    )
    control = {
        "schema": "connlab.execution-control",
        "version": 1,
        "wip_limit": 1,
        "execution_token_owner": "TASK_OWNER",
        "execution_state": "implementation_running",
        "active": {
            "task_id": "TASK_OWNER",
            "lane": "task-owner",
            "role": "Developer",
            "branch": "lane/task-owner",
            "worktree": "owner-worktree",
            "base_sha": "a" * 40,
            "head_sha": "b" * 40,
            "locked_paths": ["owner/path"],
            "evidence": "owner.md",
        },
        "queue": [],
        "paused": None,
        "quick_fix": None,
        "residuals": [],
        "parallel_exception": None,
        "last_governance_commit": "fixture",
        "evidence": "fixture.md",
    }
    payload = json.dumps(control, indent=2)
    (repo / "docs" / "task_board.md").write_text(
        f"# Board\n\n{BEGIN}\n```json\n{payload}\n```\n{END}\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "queue fixture")
    stale_lane = tmp_path / "stale-entry-lane"
    _git(repo, "worktree", "add", "-b", "lane/stale-entry", str(stale_lane), "HEAD")
    stale_control = dict(control)
    stale_control["execution_token_owner"] = "TASK_QUEUED"
    stale_control["active"] = dict(control["active"])
    stale_control["active"].update(task_id="TASK_QUEUED", lane="task-queued")
    stale_payload = json.dumps(stale_control, indent=2)
    (stale_lane / "docs" / "task_board.md").write_text(
        f"# Stale Lane Board\n\n{BEGIN}\n```json\n{stale_payload}\n```\n{END}\n",
        encoding="utf-8",
    )
    worktree_root = tmp_path / "lanes"

    completed = subprocess.run(
        [
            "powershell.exe", "-NoProfile", "-File",
            str(stale_lane / "scripts" / "connlab_lane_worktree.ps1"),
            "-Action", "Create", "-TaskId", "TASK_QUEUED", "-Lane", "task-queued",
            "-WorktreeRoot", str(worktree_root), "-Json",
        ],
        cwd=stale_lane,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    # The legacy worktree entry is no longer compatible with the personal gate contract.
    # Its only supported behavior is to fail before creating another branch/worktree.
    assert _git(repo, "branch", "--list", "lane/task-queued") == ""
    assert not (worktree_root / "task-queued").exists()


def test_v2_run_task_path_does_not_load_codex_runtime() -> None:
    text = (ROOT / "scripts" / "run_task.ps1").read_text(encoding="utf-8")

    assert "[switch]$ControlledLaneV2" in text
    assert "_codex_runtime.ps1" not in text
    assert "connlab_controlled_lane.ps1" not in text
    assert "BLOCKED_LEGACY_MODE_FROZEN" in text


def test_controlled_lane_skill_forbids_credentials_and_real_dry_run_actions() -> None:
    text = (
        ROOT / ".agents" / "skills" / "connlab-controlled-lane" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "_codex_runtime" in text
    assert "must not" in text.lower()
    assert "exactly one external action" in text
    assert "zero-write dry-run" in text
    assert "`route-plan` is a" in text and "diagnostic-only pure projection" in text


def test_v2_governance_hooks_are_present_without_bootstrap_activation() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    protocol = (
        ROOT / "docs" / "project_management" / "LANE_ORCHESTRATION_PROTOCOL.md"
    ).read_text(encoding="utf-8")
    operations = (
        ROOT / "docs" / "project_management" / "PARALLEL_LANE_OPERATIONS_GUIDE.md"
    ).read_text(encoding="utf-8")
    v2 = (
        ROOT
        / "docs"
        / "project_management"
        / "CONTROLLED_LANE_ORCHESTRATION_V2.md"
    ).read_text(encoding="utf-8")

    assert "CONTROLLED_LANE_ORCHESTRATION_V2.md" in agents
    assert "Frozen Legacy Automation Modes" in agents
    assert "dispatch_ack" in protocol
    assert "mark-invocation-started" in operations
    assert "Status: frozen legacy" in v2
    assert "Bootstrap is not activated" in v2


def test_powershell_adapter_freezes_legacy_entry_before_consuming_inputs(
    tmp_path: Path,
) -> None:
    registry_root = tmp_path / "registry"
    board_before = (ROOT / "docs" / "task_board.md").read_bytes()
    head_before = _git(ROOT, "rev-parse", "HEAD")
    status_before = _git(ROOT, "status", "--porcelain=v1", "--untracked-files=all")
    branches_before = _git(ROOT, "branch", "--format=%(refname)")
    worktrees_before = _git(ROOT, "worktree", "list", "--porcelain")

    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-File",
            str(ROOT / "scripts" / "connlab_controlled_lane.ps1"),
            "-Command",
            "prepare-dispatch",
            "-RequestJson",
            str(tmp_path / "unreadable-request.json"),
            "-RegistryRoot",
            str(registry_root),
            "-AllowTestRegistryRoot",
            "-DryRun",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = json.loads(completed.stdout)
    assert completed.returncode == 2
    assert output["code"] == "BLOCKED_LEGACY_MODE_FROZEN"
    assert output["allowed"] is False
    assert output["changed"] is False
    assert output["zero_write"] is True
    assert output["command"] == "prepare-dispatch"
    assert (ROOT / "docs" / "task_board.md").read_bytes() == board_before
    assert not registry_root.exists()
    assert _git(ROOT, "rev-parse", "HEAD") == head_before
    assert _git(ROOT, "status", "--porcelain=v1", "--untracked-files=all") == status_before
    assert _git(ROOT, "branch", "--format=%(refname)") == branches_before
    assert _git(ROOT, "worktree", "list", "--porcelain") == worktrees_before
