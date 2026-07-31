from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts.connlab_controlled_lane.contracts import canonical_digest


ROOT = Path(__file__).resolve().parents[2]


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
