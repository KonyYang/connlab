from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "connlab_execution_gate.ps1"
RUN_TASK = ROOT / "scripts" / "run_task.ps1"
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


def board_control() -> dict:
    text = (ROOT / "docs/task_board.md").read_text(encoding="utf-8")
    payload = text.split(f"{BEGIN}\n```json\n", 1)[1].split(f"\n```\n{END}", 1)[0]
    return json.loads(payload)


def test_primary_board_has_one_personal_active_slot_and_fifo() -> None:
    control = board_control()

    assert control["schema"] == "connlab.personal-serial-control"
    assert control["mode"] == "personal_serial"
    assert control["wip_limit"] == 1
    assert control["state"] in {"idle", "running", "implemented_pending_human_review"}
    assert isinstance(control["queue"], list)
    assert control["next_enqueue_sequence"] >= 1
    assert len(control["retained_history"]) == 4


def test_legacy_dispatch_intent_is_zero_write_on_the_real_board() -> None:
    board = ROOT / "docs/task_board.md"
    before = board.read_bytes()
    completed = subprocess.run(
        [
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(GATE),
            "-Intent", "ImplementationDispatch", "-TaskId", "TASK_LEGACY", "-RepositoryRoot", str(ROOT), "-Json",
        ],
        text=True,
        capture_output=True,
    )
    result = json.loads(completed.stdout)

    assert completed.returncode == 2
    assert result["code"] == "BLOCKED_LEGACY_MODE_FROZEN"
    assert result["changed"] is False
    assert board.read_bytes() == before

def test_run_task_preview_is_read_only_and_returns_the_standard_envelope() -> None:
    board = ROOT / "docs/task_board.md"
    before = board.read_bytes()
    completed = subprocess.run(
        [
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(RUN_TASK),
            "-Task", "TASK_PREVIEW", "-RepositoryRoot", str(ROOT),
            "-ExpectedBoardSha256", hashlib.sha256(before).hexdigest(),
            "-RequestJson", "{}", "-Preview",
        ],
        text=True,
        capture_output=True,
    )
    result = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert result["schema"] == "connlab.personal-task-result"
    assert result["code"] == "ALLOW_INSPECT"
    assert result["changed"] is False
    assert board.read_bytes() == before
