from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
RUN_TASK = ROOT / "scripts" / "run_task.ps1"
EXECUTION_GATE = ROOT / "scripts" / "connlab_execution_gate.ps1"
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
    if json_output:
        command.append("-Json")
    completed = subprocess.run(command, text=True, capture_output=True)
    return completed.returncode, json.loads(completed.stdout)


def test_run_task_public_entry_surface_is_submit_approve_and_close_only() -> None:
    source = RUN_TASK.read_text(encoding="utf-8")

    assert '[ValidateSet("Submit", "Approve", "Close")]' in source
    assert "ActivateNext" not in source
    assert "activate-next" not in source.lower()


def test_entry_points_resolve_default_root_after_parameter_binding() -> None:
    for script in (RUN_TASK, EXECUTION_GATE):
        source = script.read_text(encoding="utf-8")
        assert "[string]$RepositoryRoot," in source
        assert "[string]$RepositoryRoot =" not in source
        assert "if ([string]::IsNullOrWhiteSpace($RepositoryRoot))" in source


def test_controlled_lane_switch_is_stably_frozen_and_zero_write(repo: Path) -> None:
    before = (repo / "docs" / "task_board.md").read_bytes()

    code, result = invoke(repo, "TASK_ONE", request("TASK_ONE"), controlled=True)

    assert code == 2
    assert result["code"] == "BLOCKED_LEGACY_MODE_FROZEN"
    assert result["changed"] is False
    assert (repo / "docs" / "task_board.md").read_bytes() == before


def test_v2_busy_submit_is_zero_write_then_same_request_can_resubmit_after_close(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "v2-resubmit"
    repo.mkdir()
    git(repo, "init", "-b", "master")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test User")
    (repo / ".gitignore").write_text("tmp/\n", encoding="utf-8")
    (repo / "docs").mkdir()
    v2 = {
        "schema": "connlab.personal-serial-control", "version": 2,
        "mode": "personal_serial", "wip_limit": 1, "state": "idle", "active": None,
        "queue": [], "next_enqueue_sequence": 1, "last_closed": None,
        "retained_history": [],
    }
    replace_control(repo, v2)
    git(repo, "add", ".gitignore", "docs/task_board.md")
    git(repo, "commit", "-m", "v2 fixture")
    request_json = json.dumps({
        "schema": "connlab.serial-task-request", "version": 1, "task_id": "TASK_RESUBMIT",
        "summary": "same request after close", "root_cause_clear": True,
        "expected_result_clear": True, "may_touch": ["docs/task_board.md"],
        "targeted_validation": ["pytest targeted"], "requires_independent_review": False,
        "forbidden_categories": {**FORBIDDEN, "push_or_release": False},
    }, separators=(",", ":"))
    first_code, first = invoke(repo, "TASK_RESUBMIT", request_json, json_output=True)
    assert first_code == 0 and first["code"] == "ALLOW_ACTIVATE"
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "activate task")
    before = (repo / "docs" / "task_board.md").read_bytes()

    busy_code, busy = invoke(repo, "TASK_RESUBMIT", request_json, json_output=True)
    assert busy_code == 2
    assert busy["code"] == "BLOCKED_ACTIVE_TASK_RUNNING"
    assert busy["changed"] is False
    assert (repo / "docs" / "task_board.md").read_bytes() == before

    validation = json.dumps({
        "schema": "connlab.personal-task-validation", "version": 1, "status": "passed",
        "checks": [{"command": "pytest targeted", "exit_code": 0, "summary": "passed"}],
        "observed_paths": ["docs/task_board.md"], "manual_checks": [],
        "recorded_at": "2026-08-07T00:00:00Z",
    }, separators=(",", ":"))
    reviewed = subprocess.run(
        ["py", "-m", "scripts.connlab_personal_task", "mark-review", "--repo-root", str(repo),
         "--expected-board-sha256", board_hash(repo), "--task-id", "TASK_RESUBMIT",
         "--validation-json", validation, "--json"],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    assert reviewed.returncode == 0
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "mark reviewed")
    completed = subprocess.run(
        ["powershell.exe", "-NoProfile", "-File", str(RUN_TASK), "-Task", "TASK_RESUBMIT",
         "-Action", "Close", "-RepositoryRoot", str(repo), "-ExpectedBoardSha256", board_hash(repo),
         "-DecisionRef", "User closed task.", "-Json"],
        check=False, capture_output=True, text=True,
    )
    assert completed.returncode == 0
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "close task")
    resubmit_code, resubmit = invoke(repo, "TASK_RESUBMIT", request_json, json_output=True)
    assert resubmit_code == 0
    assert resubmit["code"] == "ALLOW_ACTIVATE"
