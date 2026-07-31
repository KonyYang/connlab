from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from scripts.connlab_controlled_lane.contracts import canonical_digest


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
    assert "QUEUE_REQUIRED" in completed.stdout + completed.stderr
    assert _git(repo, "branch", "--list", "lane/task-queued") == ""
    assert not (worktree_root / "task-queued").exists()


def test_v2_run_task_path_does_not_load_codex_runtime() -> None:
    text = (ROOT / "scripts" / "run_task.ps1").read_text(encoding="utf-8")

    assert "[switch]$ControlledLaneV2" in text
    assert "if (-not $ControlledLaneV2)" in text
    assert "connlab_controlled_lane.ps1" in text
    assert '-Command "scan"' in text
    assert '-Command "route-plan"' not in text


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


def test_powershell_adapter_dry_run_is_stable_and_zero_write(tmp_path: Path) -> None:
    payload = {
        "current_state": "worktree_ready",
        "action_kind": "create_or_adopt_developer_task",
    }
    request = {
        "schema_version": 2,
        "command": "prepare-dispatch",
        "request_id": "request-1",
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "expected_registry_generation": 0,
        "idempotency_key": "key-1",
        "operation_id": "operation-1",
        "route_id": "route-1",
        "scope_fingerprint": "scope-1",
        "payload": payload,
        "payload_digest": canonical_digest(payload),
    }
    request_path = tmp_path / "request.json"
    registry_root = tmp_path / "registry"
    request_path.write_text(json.dumps(request), encoding="utf-8")

    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-File",
            str(ROOT / "scripts" / "connlab_controlled_lane.ps1"),
            "-Command",
            "prepare-dispatch",
            "-RequestJson",
            str(request_path),
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
    assert completed.returncode == 0
    assert output["code"] == "CTL_DRY_RUN"
    assert output["zero_write"] is True
    assert not registry_root.exists()
