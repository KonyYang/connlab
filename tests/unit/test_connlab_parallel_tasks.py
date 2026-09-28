"""Exercise parallel task lifecycle through the real CLI and isolated Git worktrees."""
from __future__ import annotations

import json
import subprocess
import sys
import pytest
from pathlib import Path

from test_connlab_sol_native_workflow import (
    BOARD, SCRIPT, RUN_TASK, board_bytes, board_hash, control, git, invoke, repo, report, request, submit,
)


def commit_board(root: Path) -> None:
    if not git(root, "status", "--porcelain"):
        return
    git(root, "add", str(BOARD))
    git(root, "commit", "-m", "task checkpoint")


def worktree(root: Path, name: str) -> Path:
    path = root.parent / (root.name + "-" + name)
    git(root, "worktree", "add", "-b", name, str(path))
    return path


def start(root: Path, name: str, slot: str, path: str, *, expected_exit=0, resources=None):
    tree = worktree(root, name)
    result = invoke(
        root, "submit", "--task-id", name, "--slot", slot,
        "--worktree-root", str(tree), "--resources-json", json.dumps(resources or []),
        "--request-json", request(name, "standard" if slot == "main" else "micro", scope_paths=[path]),
        "--expected-board-sha256", board_hash(root), expected_exit=expected_exit,
    )
    if expected_exit == 0:
        commit_board(root)
    return tree, result


def test_two_slots_share_authority_but_keep_task_state_isolated(repo: Path):
    main, _ = start(repo, "MAIN", "main", "backend/")
    (main / "unfinished.txt").write_text("main work in progress", encoding="utf-8")
    micro, _ = start(repo, "SMALL", "micro", "frontend/map.json")
    before = control(repo)["tasks"]["MAIN"]
    checkpoint = dict(schema="connlab.sol-task-checkpoint", version=1, task_id="SMALL",
                      stage="development", status="running", summary="map entry", requires_user=False)
    invoke(repo, "checkpoint", "--task-id", "SMALL", "--checkpoint-json", json.dumps(checkpoint),
           "--expected-board-sha256", board_hash(repo))
    assert control(repo)["tasks"]["MAIN"] == before
    assert control(repo)["tasks"]["SMALL"]["task"]["checkpoint"]["summary"] == "map entry"
    assert (main / "unfinished.txt").read_text() == "main work in progress"
    inspected = invoke(micro, "inspect")
    assert inspected["primary_root"] == str(repo.resolve())
    assert set(inspected["active_tasks"]) == {"MAIN", "SMALL"}


def test_third_task_and_overlapping_paths_are_zero_write(repo: Path):
    start(repo, "MAIN", "main", "frontend/components/")
    original = board_bytes(repo)
    _, rejected = start(repo, "OVERLAP", "micro", "FRONTEND/components/Button.tsx", expected_exit=2)
    assert rejected["code"] == "BLOCKED_SCOPE_OVERLAP"
    assert board_bytes(repo) == original
    start(repo, "SMALL", "micro", "map.json")
    original = board_bytes(repo)
    _, rejected = start(repo, "THIRD", "micro", "other.json", expected_exit=2)
    assert rejected["code"] == "BLOCKED_WIP_LIMIT"
    assert board_bytes(repo) == original


def test_shared_resources_are_exclusive(repo: Path):
    start(repo, "MAIN", "main", "a.py", resources=["test-db"])
    original = board_bytes(repo)
    _, rejected = start(repo, "SMALL", "micro", "b.py", resources=["TEST-DB"], expected_exit=2)
    assert rejected["code"] == "BLOCKED_RESOURCE_OVERLAP"
    assert board_bytes(repo) == original


def implement(tree: Path, name: str, path: str, tier="micro") -> dict:
    output = tree / path
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(name, encoding="utf-8")
    git(tree, "add", path)
    git(tree, "commit", "-m", name)
    payload = report(name, git(tree, "rev-parse", "HEAD"), tier)
    payload["changed_paths"] = [path]
    payload["integration"] = {"status": "pending"}
    return payload


def finish(root: Path, name: str, payload: dict, expected_exit=0):
    return invoke(root, "finish", "--task-id", name, "--result-json", json.dumps(payload),
                  "--expected-board-sha256", board_hash(root), expected_exit=expected_exit)


def test_micro_integrates_and_closes_while_main_worktree_is_dirty(repo: Path):
    main, _ = start(repo, "MAIN", "main", "main.py")
    micro, _ = start(repo, "SMALL", "micro", "map.json")
    (main / "main.py").write_text("unfinished", encoding="utf-8")
    untouched = control(repo)["tasks"]["MAIN"]
    payload = implement(micro, "SMALL", "map.json")
    finish(repo, "SMALL", payload)
    assert (repo / "map.json").read_text() == "SMALL"
    assert control(repo)["tasks"]["SMALL"]["state"] == "ready_for_close"
    commit_board(repo)
    invoke(repo, "close", "--task-id", "SMALL", "--decision-ref", "User accepted and closed SMALL",
           "--expected-board-sha256", board_hash(repo))
    assert control(repo)["tasks"] == {"MAIN": untouched}
    assert control(repo)["last_closed"]["task_id"] == "SMALL"
    assert (main / "main.py").read_text() == "unfinished"


def test_stale_validation_cannot_integrate_after_peer_code_lands(repo: Path):
    main, _ = start(repo, "MAIN", "main", "main.py")
    micro, _ = start(repo, "SMALL", "micro", "map.json")
    main_report = implement(main, "MAIN", "main.py", "standard")
    finish(repo, "SMALL", implement(micro, "SMALL", "map.json"))
    commit_board(repo)
    before = board_bytes(repo), git(repo, "rev-parse", "HEAD")
    rejected = finish(repo, "MAIN", main_report, expected_exit=2)
    assert rejected["code"] == "BLOCKED_REVALIDATION_REQUIRED"
    assert (board_bytes(repo), git(repo, "rev-parse", "HEAD")) == before
    git(main, "merge", "master", "--no-edit")
    main_report["subject"] = git(main, "rev-parse", "HEAD")
    finish(repo, "MAIN", main_report)
    assert control(repo)["tasks"]["MAIN"]["task"]["report"]["changed_paths"] == ["main.py"]


def test_cancel_and_revision_only_change_selected_task(repo: Path):
    start(repo, "MAIN", "main", "main.py")
    micro, _ = start(repo, "SMALL", "micro", "map.json")
    main_before = control(repo)["tasks"]["MAIN"]
    finish(repo, "SMALL", implement(micro, "SMALL", "map.json"))
    commit_board(repo)
    invoke(repo, "revise", "--task-id", "SMALL", "--decision-ref", "User requested a correction",
           "--expected-board-sha256", board_hash(repo))
    assert control(repo)["tasks"]["SMALL"]["task"]["report"] is None
    assert control(repo)["tasks"]["MAIN"] == main_before
    commit_board(repo)
    invoke(repo, "close", "--task-id", "SMALL", "--disposition", "cancelled",
           "--decision-ref", "User cancelled", "--expected-board-sha256", board_hash(repo))
    assert control(repo)["tasks"] == {"MAIN": main_before}


def test_exact_task_diff_cannot_escape_reserved_scope(repo: Path):
    main, _ = start(repo, "MAIN", "main", "main.py")
    micro, _ = start(repo, "SMALL", "micro", "map.json")
    before = board_bytes(repo), git(repo, "rev-parse", "HEAD")
    rejected = finish(repo, "SMALL", implement(micro, "SMALL", "main.py"), expected_exit=2)
    assert rejected["code"] == "BLOCKED_SCOPE_DRIFT"
    assert (board_bytes(repo), git(repo, "rev-parse", "HEAD")) == before


def local_origin(root: Path) -> Path:
    remote = root.parent / (root.name + "-origin.git")
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    git(root, "remote", "add", "origin", str(remote))
    git(root, "push", "-u", "origin", "master")
    return remote


def public_close(root: Path, name: str, expected_exit=0):
    return invoke(root, "close", "--publish-close", "--task-id", name,
                  "--decision-ref", "User accepted and closed " + name,
                  "--expected-board-sha256", board_hash(root), expected_exit=expected_exit)


def test_public_close_publishes_completed_micro_not_unfinished_main(repo: Path):
    remote = local_origin(repo)
    main, _ = start(repo, "MAIN", "main", "main.py")
    micro, _ = start(repo, "SMALL", "micro", "map.json")
    implement(main, "MAIN", "main.py", "standard")
    finish(repo, "SMALL", implement(micro, "SMALL", "map.json"))
    commit_board(repo)
    closed = public_close(repo, "SMALL")
    assert closed["publication"]["code"] == "PUBLISHED_CLOSED_TASK"
    assert git(remote, "rev-parse", "master") == git(repo, "rev-parse", "HEAD")
    assert "main.py" not in git(remote, "ls-tree", "--name-only", "master").splitlines()
    assert set(control(repo)["tasks"]) == {"MAIN"}
    head = git(repo, "rev-parse", "HEAD")
    public_close(repo, "SMALL")
    assert git(repo, "rev-parse", "HEAD") == head  # reconnect does not repeat close commit


def test_publication_waits_for_other_integrated_delivery_to_be_closed(repo: Path):
    remote = local_origin(repo)
    main, _ = start(repo, "MAIN", "main", "main.py")
    micro, _ = start(repo, "SMALL", "micro", "map.json")
    finish(repo, "SMALL", implement(micro, "SMALL", "map.json"))
    commit_board(repo)
    git(main, "merge", "master", "--no-edit")
    finish(repo, "MAIN", implement(main, "MAIN", "main.py", "standard"))
    commit_board(repo)
    remote_before = git(remote, "rev-parse", "master")
    closed = public_close(repo, "SMALL")
    assert closed["publication"]["code"] == "DEFERRED_UNACCEPTED_DELIVERY"
    assert git(remote, "rev-parse", "master") == remote_before
    closed = public_close(repo, "MAIN")
    assert closed["publication"]["code"] == "PUBLISHED_CLOSED_TASK"
    assert not control(repo)["tasks"]


def test_running_legacy_task_cannot_be_migrated(repo: Path):
    submit(repo, "LEGACY", "micro")
    commit_board(repo)
    before = board_bytes(repo), git(repo, "rev-parse", "HEAD")
    _, rejected = start(repo, "SMALL", "micro", "map.json", expected_exit=2)
    assert rejected["code"] == "BLOCKED_ACTIVE_TASK_RUNNING"
    assert (board_bytes(repo), git(repo, "rev-parse", "HEAD")) == before


def test_scope_amendment_rechecks_peer_without_new_approval(repo: Path):
    start(repo, "MAIN", "main", "main.py")
    start(repo, "SMALL", "micro", "map.json")
    payload = dict(schema="connlab.sol-task-scope-amendment", version=1, task_id="SMALL",
                   scope_paths=["map.json", "map.test.json"])
    invoke(repo, "amend-scope", "--task-id", "SMALL", "--request-json", json.dumps(payload),
           "--expected-board-sha256", board_hash(repo))
    before = board_bytes(repo)
    payload["scope_paths"].append("main.py")
    rejected = invoke(repo, "amend-scope", "--task-id", "SMALL", "--request-json", json.dumps(payload),
                      "--expected-board-sha256", board_hash(repo), expected_exit=2)
    assert rejected["code"] == "BLOCKED_SCOPE_OVERLAP"
    assert board_bytes(repo) == before


def test_merge_commit_survives_interruption_without_repeated_merge(repo: Path):
    micro, _ = start(repo, "SMALL", "main", "map.json")
    payload = implement(micro, "SMALL", "map.json", "standard")
    # The real durable Git outcome at the merge/board-write crash boundary.
    git(repo, "merge", "--no-ff", "-m", f"integrate(SMALL): {payload['subject']}", payload["subject"])
    integrated = git(repo, "rev-parse", "HEAD")
    finish(repo, "SMALL", payload)
    assert control(repo)["tasks"]["SMALL"]["integrated_head"] == integrated
    assert control(repo)["tasks"]["SMALL"]["task"]["report"]["integration"]["recovered"] is True
    assert git(repo, "rev-parse", "HEAD^") == integrated


def test_other_process_lock_blocks_all_worktree_writers(repo: Path):
    tree, _ = start(repo, "MAIN", "main", "main.py")
    code = ("import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);"
            "import connlab_sol_task as w;"
            "\nwith w.board_lock(Path(sys.argv[2])):\n print('locked',flush=True)\n sys.stdin.readline()")
    process = subprocess.Popen([sys.executable, "-c", code, str(SCRIPT.parent), str(repo)],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        assert process.stdout.readline().strip() == "locked"
        before = board_bytes(repo), git(repo, "rev-parse", "HEAD")
        rejected = invoke(tree, "close", "--task-id", "MAIN", "--disposition", "cancelled",
                          "--decision-ref", "cancel", "--expected-board-sha256", board_hash(repo), expected_exit=2)
        assert rejected["code"] == "BLOCKED_LOCKED"
        assert (board_bytes(repo), git(repo, "rev-parse", "HEAD")) == before
    finally:
        process.communicate("release\n", timeout=10)


def test_powershell_parallel_submit_and_cancel_preserve_peer(repo: Path):
    start(repo, "MAIN", "main", "main.py")
    tree = worktree(repo, "SMALL")
    before = control(repo)["tasks"]["MAIN"]
    for extra in (
        ["-Action", "Submit", "-WorktreeRoot", str(tree), "-Slot", "micro",
         "-RequestJson", request("SMALL", "micro", scope_paths=["map.json"])],
        ["-Action", "Close", "-Disposition", "cancelled", "-DecisionRef", "User cancelled"],
    ):
        completed = subprocess.run(["powershell.exe", "-NoProfile", "-File", str(RUN_TASK),
            "-Task", "SMALL", "-RepositoryRoot", str(repo), "-ExpectedBoardSha256", board_hash(repo), *extra],
            capture_output=True, text=True, encoding="utf-8")
        assert completed.returncode == 0, completed.stderr or completed.stdout
    assert control(repo)["tasks"] == {"MAIN": before}


def test_rollover_and_bad_identity_do_not_consume_other_slot(repo: Path):
    start(repo, "MAIN", "main", "main.py")
    start(repo, "SMALL", "micro", "map.json")
    peer = control(repo)["tasks"]["MAIN"]
    before = board_bytes(repo)
    rejected = invoke(repo, "close", "--task-id", "WRONG", "--disposition", "cancelled",
                      "--decision-ref", "cancel", "--expected-board-sha256", board_hash(repo), expected_exit=2)
    assert rejected["code"] == "BLOCKED_TASK_MISMATCH"
    assert board_bytes(repo) == before
    tree = worktree(repo, "NEXT")
    invoke(repo, "close-and-submit", "--task-id", "SMALL", "--next-task-id", "NEXT",
           "--disposition", "cancelled", "--decision-ref", "Cancel SMALL, start NEXT",
           "--worktree-root", str(tree), "--slot", "micro",
           "--request-json", request("NEXT", "micro", scope_paths=["next.json"]),
           "--expected-board-sha256", board_hash(repo))
    assert control(repo)["tasks"]["MAIN"] == peer
    assert set(control(repo)["tasks"]) == {"MAIN", "NEXT"}


@pytest.mark.parametrize("case,code", [
    ("stale_hash", "BLOCKED_BOARD_HASH_MISMATCH"),
    ("host_branch", "BLOCKED_HOST_IDENTITY"),
    ("subject", "BLOCKED_SUBJECT_MISMATCH"),
    ("dirty_primary", "BLOCKED_WORKTREE_DIRTY"),
    ("board_edit", "BLOCKED_SCOPE_DRIFT"),
])
def test_invalid_finish_preserves_primary_and_board(repo: Path, case: str, code: str):
    tree, _ = start(repo, "MAIN", "main", "main.py")
    payload = implement(tree, "MAIN", "main.py", "standard")
    expected = board_hash(repo)
    if case == "stale_hash":
        expected = "0" * 64
    elif case == "host_branch":
        git(tree, "switch", "-c", "unregistered")
    elif case == "subject":
        payload["subject"] = "0" * 40
    elif case == "dirty_primary":
        (repo / "unrelated.txt").write_text("preserve", encoding="utf-8")
    elif case == "board_edit":
        with (tree / BOARD).open("a", encoding="utf-8") as stream:
            stream.write("\nnot the authority\n")
        git(tree, "add", str(BOARD))
        git(tree, "commit", "-m", "wrong board edit")
        payload["subject"] = git(tree, "rev-parse", "HEAD")
    before = board_bytes(repo), git(repo, "rev-parse", "HEAD")
    rejected = invoke(repo, "finish", "--task-id", "MAIN", "--result-json", json.dumps(payload),
                      "--expected-board-sha256", expected, expected_exit=2)
    assert rejected["code"] == code
    assert (board_bytes(repo), git(repo, "rev-parse", "HEAD")) == before


def test_close_retry_does_not_commit_unrelated_board_changes(repo: Path):
    local_origin(repo)
    tree, _ = start(repo, "SMALL", "micro", "map.json")
    finish(repo, "SMALL", implement(tree, "SMALL", "map.json"))
    public_close(repo, "SMALL")
    with (repo / BOARD).open("a", encoding="utf-8") as stream:
        stream.write("\nUser unfinished board notes\n")
    before = board_bytes(repo), git(repo, "rev-parse", "HEAD")
    rejected = public_close(repo, "SMALL", expected_exit=2)
    assert rejected["code"] == "BLOCKED_CLOSE_COMMIT_SCOPE"
    assert (board_bytes(repo), git(repo, "rev-parse", "HEAD")) == before


def test_secondary_slot_cannot_run_another_standard_task(repo: Path):
    start(repo, "MAIN", "main", "main.py")
    tree = worktree(repo, "OTHER")
    before = board_bytes(repo), git(repo, "rev-parse", "HEAD")
    rejected = invoke(repo, "submit", "--task-id", "OTHER", "--slot", "micro", "--worktree-root", str(tree),
        "--request-json", request("OTHER", "standard", scope_paths=["other.py"]),
        "--expected-board-sha256", board_hash(repo), expected_exit=2)
    assert rejected["code"] == "BLOCKED_TIER_UNSAFE"
    assert (board_bytes(repo), git(repo, "rev-parse", "HEAD")) == before


def test_invalid_rollover_keeps_both_tasks_and_git_unchanged(repo: Path):
    start(repo, "MAIN", "main", "main.py")
    start(repo, "SMALL", "micro", "map.json")
    tree = worktree(repo, "NEXT")
    before = board_bytes(repo), git(repo, "rev-parse", "HEAD")
    rejected = invoke(repo, "close-and-submit", "--task-id", "SMALL", "--next-task-id", "NEXT",
        "--disposition", "cancelled", "--decision-ref", "Cancel SMALL and start NEXT",
        "--worktree-root", str(tree), "--slot", "micro",
        "--request-json", request("NEXT", "micro", scope_paths=["main.py"]),
        "--expected-board-sha256", board_hash(repo), expected_exit=2)
    assert rejected["code"] == "BLOCKED_SCOPE_OVERLAP"
    assert (board_bytes(repo), git(repo, "rev-parse", "HEAD")) == before
