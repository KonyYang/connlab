from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
RUN_TASK = ROOT / "scripts" / "run_task.ps1"
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"
FORBIDDEN = {
    "api_contract": False,
    "database": False,
    "schema_or_migration": False,
    "persistence": False,
    "authority": False,
    "public_drive_workflow": False,
    "business_rule_semantics": False,
    "destructive_action": False,
    "external_mutation": False,
}


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def board_hash(repo: Path) -> str:
    return hashlib.sha256((repo / "docs" / "task_board.md").read_bytes()).hexdigest()


def control(repo: Path) -> dict:
    text = (repo / "docs" / "task_board.md").read_text(encoding="utf-8")
    return json.loads(text.split(f"{BEGIN}\n```json\n", 1)[1].split(f"\n```\n{END}", 1)[0])


def request(task_id: str) -> str:
    return json.dumps(
        {
            "schema": "connlab.personal-task-request",
            "version": 1,
            "task_id": task_id,
            "summary": f"Summary for {task_id}",
            "kind": "simple",
            "may_touch": ["docs/task_board.md", "impl.py"],
            "expected_file_count": 2,
            "classification_reason": "Known root cause and result.",
            "targeted_validation": ["pytest targeted"],
            "forbidden_categories": FORBIDDEN,
            "plan_ref": None,
        }
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-b", "master")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test User")
    (tmp_path / ".gitignore").write_text("tmp/\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    value = {
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
    (tmp_path / "docs" / "task_board.md").write_text(
        f"# Board\n\n{BEGIN}\n```json\n{json.dumps(value, indent=2)}\n```\n{END}\n",
        encoding="utf-8",
    )
    git(tmp_path, "add", ".gitignore", "docs/task_board.md")
    git(tmp_path, "commit", "-m", "fixture")
    return tmp_path


def replace_control(repo: Path, value: dict) -> None:
    board = repo / "docs" / "task_board.md"
    board.write_text(
        f"# Board\n\n{BEGIN}\n```json\n{json.dumps(value, indent=2)}\n```\n{END}\n",
        encoding="utf-8",
        newline="\n",
    )


def invoke(
    repo: Path,
    task_id: str,
    request_json: str | None,
    *,
    controlled: bool = False,
    activate_next: bool = False,
    json_output: bool = False,
) -> tuple[int, dict]:
    command = [
        "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(RUN_TASK),
        "-Task", task_id, "-RepositoryRoot", str(repo), "-ExpectedBoardSha256", board_hash(repo),
    ]
    if request_json is not None:
        command.extend(["-RequestJson", request_json])
    if controlled:
        command.append("-ControlledLaneV2")
    if activate_next:
        command.append("-ActivateNext")
    if json_output:
        command.append("-Json")
    completed = subprocess.run(command, text=True, capture_output=True)
    return completed.returncode, json.loads(completed.stdout)


def test_run_task_activates_when_idle_then_queues_without_dispatch(repo: Path) -> None:
    first_code, first = invoke(repo, "TASK_ONE", request("TASK_ONE"))
    second_code, second = invoke(repo, "TASK_TWO", request("TASK_TWO"))

    assert first_code == second_code == 0
    assert first["code"] == "ALLOW_ACTIVATE"
    assert second["code"] == "QUEUED_NEW"
    assert control(repo)["active"]["task_id"] == "TASK_ONE"
    assert [item["task_id"] for item in control(repo)["queue"]] == ["TASK_TWO"]
    assert git(repo, "branch", "--show-current") == "master"
    assert git(repo, "worktree", "list", "--porcelain").count("worktree ") == 1


def test_run_task_activate_next_starts_only_the_fifo_head_and_accepts_json(repo: Path) -> None:
    invoke(repo, "TASK_ONE", request("TASK_ONE"))
    invoke(repo, "TASK_TWO", request("TASK_TWO"))
    value = control(repo)
    value["active"] = None
    value["state"] = "idle"
    replace_control(repo, value)
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "closed active fixture")

    code, result = invoke(
        repo,
        "TASK_TWO",
        None,
        activate_next=True,
        json_output=True,
    )

    assert code == 0
    assert result["code"] == "ALLOW_ACTIVATE_NEXT"
    assert control(repo)["active"]["task_id"] == "TASK_TWO"
    assert control(repo)["queue"] == []


def test_controlled_lane_switch_is_stably_frozen_and_zero_write(repo: Path) -> None:
    before = (repo / "docs" / "task_board.md").read_bytes()

    code, result = invoke(repo, "TASK_ONE", request("TASK_ONE"), controlled=True)

    assert code == 2
    assert result["code"] == "BLOCKED_LEGACY_MODE_FROZEN"
    assert result["changed"] is False
    assert (repo / "docs" / "task_board.md").read_bytes() == before
