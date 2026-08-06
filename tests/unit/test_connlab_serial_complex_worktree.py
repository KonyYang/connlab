from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/connlab_serial_worktree.ps1"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["powershell", "-NoProfile", "-File", str(SCRIPT), *args, "-Json"],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True, check=True)
    return completed.stdout.strip()


def test_inspect_and_retire_dry_run_preserve_unique_worktree(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    worktree = tmp_path / "task-worktree"
    primary.mkdir()
    git(primary, "init", "-b", "master")
    git(primary, "config", "user.email", "test@example.invalid")
    git(primary, "config", "user.name", "Test")
    (primary / "README.md").write_text("base\n", encoding="utf-8")
    git(primary, "add", "README.md")
    git(primary, "commit", "-m", "base")
    git(primary, "worktree", "add", "-b", "codex/task-example", str(worktree), "HEAD")
    head = git(worktree, "rev-parse", "HEAD")

    common = (
        "-RepoRoot", str(primary), "-TaskId", "TASK_EXAMPLE", "-Branch", "codex/task-example",
        "-Worktree", str(worktree), "-ExpectedHead", head,
    )
    inspected = run("-Action", "Inspect", *common)
    assert inspected.returncode == 0, inspected.stderr
    assert json.loads(inspected.stdout)["code"] == "ALLOW_WORKTREE_INSPECT"

    retired = run(
        "-Action", "Retire", *common, "-IntegrationCommit", head, "-UserCloseRef", "User close",
        "-HostStopped", "-DryRun",
    )
    assert retired.returncode == 0, retired.stderr
    assert json.loads(retired.stdout)["code"] == "ALLOW_WORKTREE_RETIRE_DRY_RUN"
    assert worktree.exists()


def test_dirty_worktree_is_retained(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    worktree = tmp_path / "task-worktree"
    primary.mkdir()
    git(primary, "init", "-b", "master")
    git(primary, "config", "user.email", "test@example.invalid")
    git(primary, "config", "user.name", "Test")
    (primary / "README.md").write_text("base\n", encoding="utf-8")
    git(primary, "add", "README.md")
    git(primary, "commit", "-m", "base")
    git(primary, "worktree", "add", "-b", "codex/task-example", str(worktree), "HEAD")
    head = git(worktree, "rev-parse", "HEAD")
    (worktree / "dirty.txt").write_text("retain", encoding="utf-8")

    result = run(
        "-Action", "Retire", "-RepoRoot", str(primary), "-TaskId", "TASK_EXAMPLE",
        "-Branch", "codex/task-example", "-Worktree", str(worktree), "-ExpectedHead", head,
        "-IntegrationCommit", head, "-UserCloseRef", "User close", "-HostStopped", "-DryRun",
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["code"] == "BLOCKED_RETIREMENT_PENDING"
    assert worktree.exists()
