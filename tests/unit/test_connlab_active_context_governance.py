from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_personal_helper_and_board_remain_bounded() -> None:
    helper = ROOT / "scripts/connlab_personal_task.py"
    board = ROOT / "docs/task_board.md"

    assert len(helper.read_text(encoding="utf-8").splitlines()) < 500
    assert len(board.read_bytes()) <= 32_768
    assert len(board.read_text(encoding="utf-8").splitlines()) <= 400


def test_legacy_active_context_contract_is_explicitly_frozen() -> None:
    contract = read(
        "docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md"
    ).lower()

    assert "frozen legacy" in contract
    assert "connlab.personal-serial-control" in contract


def test_history_compatibility_helper_remains_bounded() -> None:
    active_context = ROOT / "scripts/connlab_active_context.py"

    assert len(active_context.read_text(encoding="utf-8").splitlines()) < 500


def test_legacy_inspect_accepts_personal_board_but_maintenance_stays_frozen(tmp_path: Path) -> None:
    control = {
        "schema": "connlab.personal-serial-control",
        "version": 1,
        "mode": "personal_serial",
        "wip_limit": 1,
        "state": "idle",
        "active": None,
        "queue": [],
        "next_enqueue_sequence": 1,
        "last_closed": None,
        "retained_history": [],
    }
    board = tmp_path / "docs" / "task_board.md"
    board.parent.mkdir()
    board.write_text(
        "# Board\n\n<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->\n```json\n"
        + json.dumps(control)
        + "\n```\n<!-- CONNLAB_EXECUTION_CONTROL_END -->\n",
        encoding="utf-8",
        newline="\n",
    )
    subprocess.run(["git", "-C", str(tmp_path), "init", "-b", "master"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test User"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "docs/task_board.md"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "personal board"], check=True, capture_output=True)
    script = ROOT / "scripts" / "connlab_active_context.py"

    inspected = subprocess.run(
        [sys.executable, str(script), "inspect", "--repo-root", str(tmp_path), "--json"],
        text=True,
        capture_output=True,
    )
    head = subprocess.run(
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True, check=True, capture_output=True
    ).stdout.strip()
    maintenance = subprocess.run(
        [
            sys.executable,
            str(script),
            "plan-maintenance",
            "--repo-root",
            str(tmp_path),
            "--expected-head",
            head,
            "--expected-board-sha256",
            hashlib.sha256(board.read_bytes()).hexdigest(),
            "--json",
        ],
        text=True,
        capture_output=True,
    )

    assert inspected.returncode == 0
    assert json.loads(inspected.stdout)["decision"] == "ALLOW_INSPECT"
    assert maintenance.returncode == 2
    assert json.loads(maintenance.stdout)["reason_codes"] == ["BLOCKED_SCHEMA_UNSUPPORTED"]
