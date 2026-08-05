from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "connlab_execution_gate.ps1"
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def active(task_id: str = "TASK_ACTIVE", phase: str = "implementation") -> dict:
    return {
        "task_id": task_id,
        "summary": "Active fixture",
        "kind": "simple",
        "phase": phase,
        "scope_contract": {
            "may_touch": ["docs/task_board.md"],
            "expected_file_count": 1,
            "classification_reason": "Known root cause.",
            "targeted_validation": ["pytest targeted"],
            "forbidden_categories": {
                "api_contract": False,
                "database": False,
                "schema_or_migration": False,
                "persistence": False,
                "authority": False,
                "public_drive_workflow": False,
                "business_rule_semantics": False,
                "destructive_action": False,
                "external_mutation": False,
            },
        },
        "plan_ref": None,
        "approval_ref": None,
        "activation_parent_sha": "a" * 40,
        "activated_at": "2026-08-06T00:00:00Z",
        "updated_at": "2026-08-06T00:00:00Z",
        "blocker": None,
        "validation": None,
    }


def write_board(repo: Path, *, state: str = "running", active_value: dict | None = None) -> None:
    value = {
        "schema": "connlab.personal-serial-control",
        "version": 1,
        "mode": "personal_serial",
        "wip_limit": 1,
        "state": state,
        "active": active_value,
        "queue": [],
        "next_enqueue_sequence": 1,
        "last_closed": None,
        "retained_history": [],
    }
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "task_board.md").write_text(
        f"# Board\n\n{BEGIN}\n```json\n{json.dumps(value, indent=2)}\n```\n{END}\n",
        encoding="utf-8",
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-b", "master")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test User")
    (tmp_path / ".gitignore").write_text("tmp/\n", encoding="utf-8")
    write_board(tmp_path, active_value=active())
    git(tmp_path, "add", ".gitignore", "docs/task_board.md")
    git(tmp_path, "commit", "-m", "fixture")
    return tmp_path


def invoke(repo: Path, intent: str, task_id: str | None = None) -> tuple[int, dict]:
    command = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(GATE),
        "-Intent",
        intent,
        "-RepositoryRoot",
        str(repo),
        "-Json",
    ]
    if task_id:
        command.extend(["-TaskId", task_id])
    completed = subprocess.run(command, text=True, capture_output=True)
    return completed.returncode, json.loads(completed.stdout)


def test_inspect_is_a_zero_write_helper_adapter(repo: Path) -> None:
    before = (repo / "docs" / "task_board.md").read_bytes()

    code, result = invoke(repo, "Inspect")

    assert code == 0
    assert result["schema"] == "connlab.personal-task-result"
    assert result["code"] == "ALLOW_INSPECT"
    assert result["changed"] is False
    assert (repo / "docs" / "task_board.md").read_bytes() == before


def test_active_task_is_allowed_to_implement(repo: Path) -> None:
    code, result = invoke(repo, "Implementation", "TASK_ACTIVE")

    assert code == 0
    assert result["code"] == "ALLOW_IMPLEMENTATION"
    assert result["active_task_id"] == "TASK_ACTIVE"


def test_mismatched_task_fails_closed(repo: Path) -> None:
    code, result = invoke(repo, "Implementation", "TASK_OTHER")

    assert code == 2
    assert result["code"] == "BLOCKED_TASK_MISMATCH"


@pytest.mark.parametrize(
    "intent",
    ["StartTask", "CreateWorktree", "ImplementationDispatch", "QuickFixPreempt", "Reconcile", "Resume"],
)
def test_every_legacy_intent_is_frozen(repo: Path, intent: str) -> None:
    before = (repo / "docs" / "task_board.md").read_bytes()

    code, result = invoke(repo, intent, "TASK_ACTIVE")

    assert code == 2
    assert result["code"] == "BLOCKED_LEGACY_MODE_FROZEN"
    assert result["changed"] is False
    assert (repo / "docs" / "task_board.md").read_bytes() == before


def test_close_gate_requires_pending_review_and_clean_primary(repo: Path) -> None:
    code, result = invoke(repo, "Close", "TASK_ACTIVE")

    assert code == 2
    assert result["code"] == "BLOCKED_STATE"
