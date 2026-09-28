"""Keep the close transition, board-only commit and publication under one shared lock."""
from __future__ import annotations

from pathlib import Path

import connlab_sol_task as w
from connlab_publish_closed_task import GateBlocked, publish, read_control, verify_parallel_close


def commit_board(root: Path, message: str) -> str:
    status = w.run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode:
        raise w.Blocked("BLOCKED_GIT_INVALID", "Cannot inspect pending board commit.")
    lines = status.stdout.splitlines()
    if len(lines) != 1 or lines[0][3:].replace("\\", "/") != w.BOARD_REL.as_posix():
        raise w.Blocked("BLOCKED_CLOSE_COMMIT_SCOPE", "Only the board may be dirty for a task checkpoint commit.")
    for argv in (("add", "--", w.BOARD_REL.as_posix()), ("commit", "-m", message)):
        if argv[0] == "commit":
            staged = w.run_git(root, "diff", "--cached", "--name-only")
            if staged.returncode or staged.stdout.splitlines() != [w.BOARD_REL.as_posix()]:
                raise w.Blocked("BLOCKED_CLOSE_COMMIT_SCOPE", "Staging is not board-only.")
        outcome = w.run_git(root, *argv)
        if outcome.returncode:
            raise w.Blocked("BLOCKED_BOARD_COMMIT", "Board transition is durable but its commit failed; inspect before continuing. " + outcome.stderr.strip())
    w.require_clean(root, "Task checkpoint commit left unexpected changes.")
    return w.current_head(root)


def close_and_publish(args, root: Path) -> dict:
    with w.board_lock(root):
        _, control, _, raw = w.read_board(root)
        before = w.sha256(raw)
        if not args.expected_board_sha256 or args.expected_board_sha256 != before:
            raise w.Blocked("BLOCKED_BOARD_HASH_MISMATCH", "Inspect the current board before closing.")
        if w.run_git(root, "branch", "--show-current").stdout.strip() != "master":
            raise w.Blocked("BLOCKED_BRANCH", "Public close runs only on primary master.")
        w.required_decision_ref(args.decision_ref, "Explicit User close/cancel decision is required.")
        last = control.get("last_closed") or {}
        active_ids = set(control["tasks"]) if control["version"] == 2 else {(control.get("active") or {}).get("task_id")}
        resumed = args.task_id not in active_ids and last.get("task_id") == args.task_id and last.get("disposition") == args.disposition
        if not resumed:
            if control["version"] == 2:
                from connlab_parallel_task import transition
                before, after, control = transition(args, root)
            else:
                before, after, control = w.close(args, root)
        else:
            after = before
        # Supports reconnect after board replacement, after close commit, or after remote failure.
        if w.run_git(root, "status", "--porcelain=v1", "--untracked-files=all").stdout:
            if resumed:
                committed = read_control(root, "HEAD")
                if control["version"] == 2:
                    try:
                        verify_parallel_close(committed, control, args.task_id)
                    except GateBlocked as exc:
                        raise w.Blocked(exc.code, exc.message) from exc
                elif (committed.get("active") or {}).get("task_id") != args.task_id:
                    raise w.Blocked("BLOCKED_CLOSE_COMMIT_SCOPE", "Uncommitted board changes are not a pending close.")
            head = commit_board(root, f"close({args.task_id}): record {args.disposition} task")
        else:
            head = w.current_head(root)
        answer = w.result("ALLOW_CLOSE", "close", root, control, before, after,
                          task_id=args.task_id, changed=not resumed)
        answer["close_commit"] = head
        if args.disposition == "cancelled":
            answer["publication"] = {"code": "SKIPPED_CANCELLED_CLOSE", "changed": False}
            return answer
        if control["version"] == 2 and any(e["integrated_head"] for e in control["tasks"].values()):
            answer["publication"] = {"code": "DEFERRED_UNACCEPTED_DELIVERY", "changed": False}
            return answer
        try:
            answer["publication"] = publish(root, args.task_id, head)
        except GateBlocked as exc:
            return dict(code=exc.code, allowed=False, changed=False, message=exc.message,
                        close_result=answer, close_commit=head, local_close_committed=True)
        return answer
