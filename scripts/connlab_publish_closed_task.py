from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import NoReturn


BOARD = Path("docs/task_board.md")
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


class GateBlocked(RuntimeError):
    def __init__(self, code: str, message: str, **facts: object) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.facts = facts


def git(repo: Path, *args: str, remote: bool = False) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    if completed.returncode:
        detail = (completed.stderr or completed.stdout).strip()
        if remote:
            raise GateBlocked(
                "BLOCKED_REMOTE_OPERATION",
                detail or f"Git remote operation failed: {' '.join(args)}",
                local_close_committed=True,
            )
        raise GateBlocked("BLOCKED_GIT_STATE", detail or f"Git command failed: {' '.join(args)}")
    return completed.stdout.strip()


def read_control(repo: Path) -> dict:
    try:
        text = (repo / BOARD).read_text(encoding="utf-8")
        payload = text.split(BEGIN, 1)[1].split(END, 1)[0]
        payload = payload.split("```json", 1)[1].rsplit("```", 1)[0]
        return json.loads(payload)
    except (OSError, IndexError, json.JSONDecodeError) as exc:
        raise GateBlocked("BLOCKED_BOARD_INVALID", f"Cannot read task board control block: {exc}") from exc


def block(code: str, message: str, **facts: object) -> NoReturn:
    raise GateBlocked(code, message, **facts)


def publish(repo: Path, task_id: str, expected_head: str) -> dict:
    head = git(repo, "rev-parse", "HEAD")
    if head != expected_head:
        block("BLOCKED_HEAD_MISMATCH", "HEAD does not match the expected close commit.", head=head)

    branch = git(repo, "branch", "--show-current")
    if branch != "master":
        block("BLOCKED_BRANCH", "Closed tasks may be published only from master.", branch=branch)

    if git(repo, "status", "--porcelain=v1", "--untracked-files=all"):
        block("BLOCKED_DIRTY_WORKTREE", "Working tree and index must be clean before publication.")

    control = read_control(repo)
    if control.get("state") != "idle" or control.get("active") is not None:
        block("BLOCKED_BOARD_STATE", "Task board must be idle with no active task.")
    last_closed = control.get("last_closed") or {}
    if last_closed.get("task_id") != task_id:
        block("BLOCKED_CLOSED_TASK_ID", "last_closed does not match the requested task.")
    if last_closed.get("disposition") != "completed":
        block("BLOCKED_CLOSE_DISPOSITION", "Only a completed close may be published.")

    parent = git(repo, "rev-parse", "HEAD^")
    changed_paths = [
        line.replace("\\", "/")
        for line in git(repo, "diff", "--name-only", parent, head).splitlines()
        if line
    ]
    if changed_paths != [BOARD.as_posix()]:
        block(
            "BLOCKED_CLOSE_COMMIT_SCOPE",
            "Expected HEAD must be a board-only close commit.",
            changed_paths=changed_paths,
        )

    remotes = git(repo, "remote").splitlines()
    if "origin" not in remotes:
        block("BLOCKED_ORIGIN", "Remote 'origin' is required.")
    try:
        upstream = git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    except GateBlocked as exc:
        block("BLOCKED_UPSTREAM", "master must track origin/master.", detail=exc.message)
    if upstream != "origin/master":
        block("BLOCKED_UPSTREAM", "master must track origin/master.", upstream=upstream)

    git(repo, "fetch", "origin", "master", remote=True)
    remote_tracking = git(repo, "rev-parse", "refs/remotes/origin/master")
    ancestor = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", remote_tracking, head],
        capture_output=True,
    )
    if ancestor.returncode != 0:
        block(
            "BLOCKED_NON_FAST_FORWARD",
            "origin/master is not an ancestor of the completed close commit.",
            remote_head=remote_tracking,
            head=head,
        )

    changed = remote_tracking != head
    if changed:
        git(repo, "push", "origin", "HEAD:refs/heads/master", remote=True)

    advertised = git(repo, "ls-remote", "--heads", "origin", "refs/heads/master", remote=True)
    advertised_head = advertised.split(maxsplit=1)[0] if advertised else ""
    if advertised_head != head:
        block(
            "BLOCKED_REMOTE_VERIFICATION",
            "origin/master did not advertise the expected close commit after push.",
            remote_head=advertised_head,
            head=head,
            local_close_committed=True,
        )

    return {
        "code": "PUBLISHED_CLOSED_TASK",
        "changed": changed,
        "task_id": task_id,
        "head": head,
        "remote": "origin/master",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish one exact completed ConnLab close commit.")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        result = publish(args.repo_root.resolve(), args.task_id, args.expected_head)
        exit_code = 0
    except GateBlocked as exc:
        result = {
            "code": exc.code,
            "changed": False,
            "message": exc.message,
            **exc.facts,
        }
        exit_code = 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    else:
        print(result.get("message", result["code"]))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
