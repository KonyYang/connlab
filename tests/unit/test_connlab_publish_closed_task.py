from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "connlab_publish_closed_task.py"
BOARD = Path("docs/task_board.md")
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=check,
    )


def write_board(repo: Path, *, task_id: str, state: str = "idle", disposition: str = "completed") -> None:
    value = {
        "schema": "connlab.sol-task-control",
        "version": 1,
        "mode": "sol_native",
        "wip_limit": 1,
        "state": state,
        "active": None if state == "idle" else {"task_id": "OTHER"},
        "last_closed": {
            "task_id": task_id,
            "tier": "micro",
            "subject": "1" * 40,
            "summary": "Done.",
            "disposition": disposition,
            "decision_ref": "User said close.",
            "closed_at": "2026-09-22T00:00:00Z",
        },
        "retained_history": [],
    }
    board = repo / BOARD
    board.parent.mkdir(parents=True, exist_ok=True)
    board.write_text(
        "# Board\n\n"
        + BEGIN
        + "\n```json\n"
        + json.dumps(value, indent=2)
        + "\n```\n"
        + END
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def invoke(repo: Path, task_id: str, expected_head: str, *, expected_exit: int = 0) -> dict:
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-root",
            str(repo),
            "--task-id",
            task_id,
            "--expected-head",
            expected_head,
            "--json",
        ],
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    assert completed.returncode == expected_exit, completed.stderr or completed.stdout
    return json.loads(completed.stdout)


@pytest.fixture
def closed_repo(tmp_path: Path) -> tuple[Path, Path, str]:
    repo = tmp_path / "repo"
    remote = tmp_path / "origin.git"
    repo.mkdir()
    git(repo, "init", "-b", "master")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test User")
    (repo / ".gitignore").write_text("tmp/\n", encoding="utf-8")
    write_board(repo, task_id="PREVIOUS")
    git(repo, "add", ".gitignore", str(BOARD))
    git(repo, "commit", "-m", "baseline")
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    git(repo, "remote", "add", "origin", str(remote))
    git(repo, "push", "-u", "origin", "master")
    write_board(repo, task_id="TASK_DONE")
    git(repo, "add", str(BOARD))
    git(repo, "commit", "-m", "close task")
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    return repo, remote, head


def remote_head(remote: Path) -> str:
    return subprocess.run(
        ["git", "--git-dir", str(remote), "rev-parse", "refs/heads/master"],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    ).stdout.strip()


def test_publishes_exact_completed_close_commit_to_local_origin(closed_repo: tuple[Path, Path, str]) -> None:
    repo, remote, head = closed_repo

    result = invoke(repo, "TASK_DONE", head)

    assert result == {
        "code": "PUBLISHED_CLOSED_TASK",
        "changed": True,
        "task_id": "TASK_DONE",
        "head": head,
        "remote": "origin/master",
    }
    assert remote_head(remote) == head


@pytest.mark.parametrize(
    ("mutate", "code"),
    [
        (lambda repo, head: (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8"), "BLOCKED_DIRTY_WORKTREE"),
        (lambda repo, head: git(repo, "switch", "-c", "topic"), "BLOCKED_BRANCH"),
    ],
)
def test_rejects_unsafe_local_state_without_pushing(
    closed_repo: tuple[Path, Path, str], mutate, code: str
) -> None:
    repo, remote, head = closed_repo
    before = remote_head(remote)
    mutate(repo, head)

    result = invoke(repo, "TASK_DONE", head, expected_exit=2)

    assert result["code"] == code
    assert result["changed"] is False
    assert remote_head(remote) == before


@pytest.mark.parametrize(
    ("board_kwargs", "code"),
    [
        ({"state": "running"}, "BLOCKED_BOARD_STATE"),
        ({"disposition": "cancelled"}, "BLOCKED_CLOSE_DISPOSITION"),
    ],
)
def test_rejects_committed_non_publishable_board_state(
    closed_repo: tuple[Path, Path, str], board_kwargs: dict[str, str], code: str
) -> None:
    repo, remote, _head = closed_repo
    before = remote_head(remote)
    write_board(repo, task_id="TASK_DONE", **board_kwargs)
    git(repo, "add", str(BOARD))
    git(repo, "commit", "--amend", "--no-edit")
    amended = git(repo, "rev-parse", "HEAD").stdout.strip()

    result = invoke(repo, "TASK_DONE", amended, expected_exit=2)

    assert result["code"] == code
    assert result["changed"] is False
    assert remote_head(remote) == before


def test_rejects_wrong_expected_head_and_non_board_close_commit(
    closed_repo: tuple[Path, Path, str],
) -> None:
    repo, remote, head = closed_repo
    wrong = invoke(repo, "TASK_DONE", "0" * 40, expected_exit=2)
    assert wrong["code"] == "BLOCKED_HEAD_MISMATCH"

    (repo / "also-changed.txt").write_text("not a board-only close\n", encoding="utf-8")
    git(repo, "add", "also-changed.txt")
    git(repo, "commit", "--amend", "--no-edit")
    amended = git(repo, "rev-parse", "HEAD").stdout.strip()
    not_board_only = invoke(repo, "TASK_DONE", amended, expected_exit=2)
    assert not_board_only["code"] == "BLOCKED_CLOSE_COMMIT_SCOPE"
    assert remote_head(remote) != amended


def test_rejects_non_origin_master_upstream_and_remote_divergence(
    closed_repo: tuple[Path, Path, str], tmp_path: Path
) -> None:
    repo, remote, head = closed_repo
    git(repo, "branch", "--set-upstream-to", "origin/master")
    git(repo, "config", "branch.master.merge", "refs/heads/other")
    upstream = invoke(repo, "TASK_DONE", head, expected_exit=2)
    assert upstream["code"] == "BLOCKED_UPSTREAM"

    git(repo, "config", "branch.master.merge", "refs/heads/master")
    other = tmp_path / "other"
    subprocess.run(["git", "clone", str(remote), str(other)], check=True, capture_output=True)
    git(other, "config", "user.email", "test@example.com")
    git(other, "config", "user.name", "Test User")
    (other / "remote.txt").write_text("remote advanced\n", encoding="utf-8")
    git(other, "add", "remote.txt")
    git(other, "commit", "-m", "advance remote")
    git(other, "push", "origin", "master")

    diverged = invoke(repo, "TASK_DONE", head, expected_exit=2)
    assert diverged["code"] == "BLOCKED_NON_FAST_FORWARD"
    assert remote_head(remote) != head


def test_remote_failure_preserves_local_close_commit(closed_repo: tuple[Path, Path, str]) -> None:
    repo, _remote, head = closed_repo
    git(repo, "remote", "set-url", "origin", str(repo / "missing-origin.git"))

    result = invoke(repo, "TASK_DONE", head, expected_exit=2)

    assert result["code"] == "BLOCKED_REMOTE_OPERATION"
    assert result["changed"] is False
    assert result["local_close_committed"] is True
    assert git(repo, "rev-parse", "HEAD").stdout.strip() == head
