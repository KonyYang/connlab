from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "connlab_execution_gate.ps1"
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


def _git(repo: Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _init_repository(tmp_path: Path) -> tuple[Path, Path, str]:
    repo = tmp_path / "repository"
    original = tmp_path / "original-lane"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "connlab-tests@example.invalid")
    _git(repo, "config", "user.name", "ConnLab Tests")
    (repo / "docs").mkdir()
    (repo / "shared.txt").write_text("base\n", encoding="utf-8")
    (repo / "docs" / "task_board.md").write_text("# Board\n", encoding="utf-8")
    _git(repo, "add", "docs/task_board.md", "shared.txt")
    _git(repo, "commit", "-m", "fixture base")
    base = _git(repo, "rev-parse", "HEAD")
    _git(repo, "worktree", "add", "-b", "lane/original", str(original), base)
    return repo, original, base


def _control(
    *,
    state: str,
    owner: str | None,
    paused: dict[str, object] | None = None,
    quick_fix: dict[str, object] | None = None,
    residuals: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "schema": "connlab.execution-control",
        "version": 1,
        "wip_limit": 1,
        "execution_token_owner": owner,
        "execution_state": state,
        "active": None,
        "queue": [],
        "paused": paused,
        "quick_fix": quick_fix,
        "residuals": residuals or [],
        "parallel_exception": None,
        "last_governance_commit": "fixture",
        "evidence": "fixture.md",
    }


def _write_board(repo: Path, control: dict[str, object]) -> None:
    text = (
        "# Fixture Board\n\n"
        f"{BEGIN}\n```json\n{json.dumps(control, indent=2)}\n```\n{END}\n"
    )
    (repo / "docs" / "task_board.md").write_text(text, encoding="utf-8")


def _run_gate(
    repo: Path, intent: str, task_id: str, lane: str
) -> tuple[int, dict[str, object]]:
    assert GATE.is_file(), "production execution gate is not implemented"
    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-File",
            str(GATE),
            "-Intent",
            intent,
            "-TaskId",
            task_id,
            "-Lane",
            lane,
            "-RepositoryRoot",
            str(repo),
            "-AllowTestRepositoryRoot",
            "-Json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode, json.loads(completed.stdout)


def _paused(original: Path, checkpoint: str, master: str) -> dict[str, object]:
    return {
        "task_id": "TASK_ORIGINAL",
        "lane": "original",
        "branch": "lane/original",
        "worktree": str(original),
        "previous_owner": "Developer",
        "paused_reason": "preempted for bounded repair",
        "preempted_by": "TASK_QF",
        "checkpoint_sha": checkpoint,
        "pause_master_sha": master,
        "resume_condition": "merge accepted master and rerun validation",
        "unfinished_items": ["Reviewer"],
        "locked_paths": ["original/path"],
        "evidence": "original.md",
    }


def _quick_fix(*, accepted_head: str | None, accepted: bool) -> dict[str, object]:
    return {
        "task_id": "TASK_QF",
        "lane": "task-qf",
        "risk_gate": "QF-2",
        "preempting_task_id": "TASK_ORIGINAL",
        "locked_paths": ["quick/path"],
        "accepted_head": accepted_head,
        "accepted_on_master": accepted,
        "residual_owner": None,
    }


def _registered_worktree_snapshot() -> str:
    return _git(ROOT, "worktree", "list", "--porcelain") + "\n" + _git(
        ROOT, "status", "--porcelain=v1"
    )


def test_preempting_recovery_is_restart_stable_and_preserves_real_worktrees(
    tmp_path: Path,
) -> None:
    protected_before = _registered_worktree_snapshot()
    repo, original, base = _init_repository(tmp_path)
    paused = _paused(original, base, base)
    _write_board(
        repo,
        _control(
            state="quick_fix_running",
            owner="TASK_QF",
            paused=paused,
            quick_fix=_quick_fix(accepted_head=base, accepted=True),
        ),
    )

    first_code, first = _run_gate(repo, "Reconcile", "TASK_ORIGINAL", "original")
    second_code, second = _run_gate(repo, "Reconcile", "TASK_ORIGINAL", "original")

    assert first_code == second_code == 0
    assert first["code"] == second["code"] == "ALLOW_RECONCILE"
    assert first["snapshot_digest"] == second["snapshot_digest"]
    assert _git(original, "rev-parse", "HEAD") == base
    assert _git(original, "status", "--porcelain=v1") == ""
    assert _registered_worktree_snapshot() == protected_before


def test_dirty_original_blocks_preemption_until_clean_checkpoint(tmp_path: Path) -> None:
    repo, original, base = _init_repository(tmp_path)
    (original / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    paused = _paused(original, base, base)
    _write_board(
        repo,
        _control(
            state="paused_preempted",
            owner=None,
            paused=paused,
            quick_fix=_quick_fix(accepted_head=None, accepted=False),
        ),
    )

    code, output = _run_gate(repo, "QuickFixPreempt", "TASK_QF", "task-qf")

    assert code != 0
    assert output["code"] == "BLOCKED_CHECKPOINT_DIRTY"


def test_clean_checkpoint_allows_serialized_preemption(tmp_path: Path) -> None:
    repo, original, base = _init_repository(tmp_path)
    paused = _paused(original, base, base)
    _write_board(
        repo,
        _control(
            state="paused_preempted",
            owner=None,
            paused=paused,
            quick_fix=_quick_fix(accepted_head=None, accepted=False),
        ),
    )

    code, output = _run_gate(repo, "QuickFixPreempt", "TASK_QF", "task-qf")

    assert code == 0
    assert output["code"] == "ALLOW_PREEMPT_CHECKPOINTED"


def test_reconciliation_fails_closed_when_preserved_checkpoint_drifts(
    tmp_path: Path,
) -> None:
    repo, original, base = _init_repository(tmp_path)
    (original / "lane.txt").write_text("new checkpoint\n", encoding="utf-8")
    _git(original, "add", "lane.txt")
    _git(original, "commit", "-m", "unexpected drift")
    paused = _paused(original, base, base)
    _write_board(
        repo,
        _control(
            state="quick_fix_running",
            owner="TASK_QF",
            paused=paused,
            quick_fix=_quick_fix(accepted_head=base, accepted=True),
        ),
    )

    code, output = _run_gate(repo, "Reconcile", "TASK_ORIGINAL", "original")

    assert code != 0
    assert output["code"] == "BLOCKED_CHECKPOINT_DRIFT"
    assert _git(original, "status", "--porcelain=v1") == ""


def test_explicit_parallel_secondary_dispatch_requires_matching_clean_worktree(
    tmp_path: Path,
) -> None:
    repo, original, base = _init_repository(tmp_path)
    secondary = tmp_path / "secondary-lane"
    _git(repo, "worktree", "add", "-b", "lane/secondary", str(secondary), base)
    control = _control(state="implementation_running", owner="TASK_PRIMARY")
    control["active"] = {
        "task_id": "TASK_PRIMARY",
        "lane": "primary",
        "role": "Developer",
        "branch": "lane/primary",
        "worktree": str(original),
        "base_sha": base,
        "head_sha": base,
        "locked_paths": ["primary/path"],
        "evidence": "primary.md",
    }
    control["parallel_exception"] = {
        "secondary_execution_token_owner": "TASK_SECONDARY",
        "secondary_lane": "secondary",
        "secondary_branch": "lane/secondary",
        "secondary_worktree": str(secondary),
        "secondary_head_sha": base,
        "user_approval_evidence": "USER_APPROVAL_PARALLEL_1",
        "scope_proof": "secondary/path is disjoint from primary/path",
        "locked_paths": ["secondary/path"],
        "end_condition": "secondary Integrator acceptance",
    }
    _write_board(repo, control)

    code, output = _run_gate(
        repo, "ImplementationDispatch", "TASK_SECONDARY", "secondary"
    )

    assert code == 0
    assert output["code"] == "ALLOW_DISPATCH"
    assert _git(secondary, "status", "--porcelain=v1") == ""


def test_reconciling_original_can_resume_after_clean_reconciliation_checkpoint(
    tmp_path: Path,
) -> None:
    repo, original, base = _init_repository(tmp_path)
    paused = _paused(original, base, base)
    _write_board(
        repo,
        _control(
            state="reconciling",
            owner="TASK_ORIGINAL",
            paused=paused,
            quick_fix=_quick_fix(accepted_head=base, accepted=True),
        ),
    )

    code, output = _run_gate(repo, "Resume", "TASK_ORIGINAL", "original")

    assert code == 0
    assert output["code"] == "ALLOW_RESUME"


def test_standalone_quick_fix_running_has_the_quick_fix_as_sole_owner(
    tmp_path: Path,
) -> None:
    repo, _, base = _init_repository(tmp_path)
    quick_fix = _quick_fix(accepted_head=base, accepted=False)
    quick_fix["preempting_task_id"] = None
    _write_board(
        repo,
        _control(
            state="quick_fix_running",
            owner="TASK_QF",
            quick_fix=quick_fix,
        ),
    )

    code, output = _run_gate(repo, "Inspect", "TASK_QF", "task-qf")

    assert code == 0
    assert output["code"] == "ALLOW_INSPECT"
    assert output["execution_token_owner"] == "TASK_QF"


@pytest.mark.parametrize(
    ("state", "owner", "paused_present", "residuals", "expected"),
    [
        ("complete", None, False, [], "ALLOW_INSPECT"),
        (
            "cancelled",
            None,
            False,
            [{"task_id": "TASK_QF", "residual_owner": "Orchestrator", "disposition": "retain"}],
            "ALLOW_INSPECT",
        ),
        (
            "paused_preempted",
            None,
            True,
            [{"task_id": "TASK_QF", "residual_owner": "Planner/User", "disposition": "retain"}],
            "ALLOW_INSPECT",
        ),
        ("paused_preempted", "TASK_ORIGINAL", True, [], "BLOCKED_OWNER_STATE_CONTRADICTION"),
    ],
)
def test_terminal_and_failure_owner_invariants(
    tmp_path: Path,
    state: str,
    owner: str | None,
    paused_present: bool,
    residuals: list[dict[str, object]],
    expected: str,
) -> None:
    repo, original, base = _init_repository(tmp_path)
    paused = _paused(original, base, base) if paused_present else None
    control = _control(
        state=state,
        owner=owner,
        paused=paused,
        residuals=residuals,
    )
    if state in {"complete", "cancelled"}:
        control["quick_fix"] = _quick_fix(accepted_head=base, accepted=state == "complete")
        if state == "cancelled":
            control["quick_fix"]["residual_owner"] = "Orchestrator"  # type: ignore[index]
    _write_board(repo, control)

    code, output = _run_gate(repo, "Inspect", "TASK_QF", "task-qf")

    assert output["code"] == expected
    assert (code == 0) is expected.startswith("ALLOW_")
