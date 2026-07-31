from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "connlab_execution_gate.ps1"
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "connlab-tests@example.invalid")
    _git(repo, "config", "user.name", "ConnLab Tests")
    (repo / "docs").mkdir()
    return repo


def _control(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema": "connlab.execution-control",
        "version": 1,
        "wip_limit": 1,
        "execution_token_owner": None,
        "execution_state": "idle",
        "active": None,
        "queue": [],
        "paused": None,
        "quick_fix": None,
        "residuals": [],
        "parallel_exception": None,
        "last_governance_commit": "test-fixture",
        "evidence": "tests",
    }
    value.update(overrides)
    return value


def _write_board(repo: Path, control: dict[str, object], *, duplicate: bool = False) -> None:
    block = f"{BEGIN}\n```json\n{json.dumps(control, indent=2)}\n```\n{END}\n"
    if duplicate:
        block = f"{block}\n{block}"
    (repo / "docs" / "task_board.md").write_text(
        f"# Fixture Board\n\n{block}", encoding="utf-8"
    )


def _run_gate(
    repo: Path,
    intent: str,
    *,
    task_id: str = "TASK_NEW",
    lane: str = "task-new",
) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
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
    return completed, json.loads(completed.stdout)


def test_idle_task_is_allowed_to_start_without_writing_board(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_board(repo, _control())
    before = (repo / "docs" / "task_board.md").read_bytes()

    completed, output = _run_gate(repo, "StartTask")

    assert completed.returncode == 0
    assert output["code"] == "ALLOW_START"
    assert output["allowed"] is True
    assert output["zero_write"] is True
    assert (repo / "docs" / "task_board.md").read_bytes() == before


@pytest.mark.parametrize("role", ["Developer", "Reviewer", "QA", "Integrator"])
def test_second_task_queues_while_owner_retains_token_through_gates(
    tmp_path: Path, role: str
) -> None:
    repo = _init_repo(tmp_path)
    state = "implementation_running" if role == "Developer" else "gate_running"
    active = {
        "task_id": "TASK_OWNER",
        "lane": "task-owner",
        "role": role,
        "branch": "lane/task-owner",
        "worktree": str(tmp_path / "owner"),
        "base_sha": "a" * 40,
        "head_sha": "b" * 40,
        "locked_paths": ["shared/path"],
        "evidence": "owner.md",
    }
    _write_board(
        repo,
        _control(
            execution_token_owner="TASK_OWNER",
            execution_state=state,
            active=active,
        ),
    )

    completed, output = _run_gate(repo, "StartTask")

    assert completed.returncode == 0
    assert output["code"] == "QUEUE_REQUIRED"
    assert output["execution_token_owner"] == "TASK_OWNER"
    assert output["zero_write"] is True


@pytest.mark.parametrize(
    ("board_text", "expected_code"),
    [
        ("# no markers\n", "BLOCKED_MARKERS_MISSING"),
        (
            f"{BEGIN}\n```json\n{{broken\n```\n{END}\n",
            "BLOCKED_JSON_INVALID",
        ),
    ],
)
def test_missing_or_malformed_authority_fails_closed(
    tmp_path: Path, board_text: str, expected_code: str
) -> None:
    repo = _init_repo(tmp_path)
    (repo / "docs" / "task_board.md").write_text(board_text, encoding="utf-8")

    completed, output = _run_gate(repo, "Inspect")

    assert completed.returncode != 0
    assert output["code"] == expected_code
    assert output["allowed"] is False
    assert output["zero_write"] is True


def test_duplicate_authority_blocks_fail_closed(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_board(repo, _control(), duplicate=True)

    completed, output = _run_gate(repo, "Inspect")

    assert completed.returncode != 0
    assert output["code"] == "BLOCKED_MARKERS_DUPLICATE"


@pytest.mark.parametrize(
    ("mutate", "expected_code"),
    [
        (lambda state: state.update(version=99), "BLOCKED_SCHEMA_UNSUPPORTED"),
        (
            lambda state: state.update(
                execution_state="implementation_running",
                execution_token_owner=None,
            ),
            "BLOCKED_OWNER_STATE_CONTRADICTION",
        ),
        (
            lambda state: state.update(
                queue=[
                    {"task_id": "TASK_A", "queue_position": 1},
                    {"task_id": "TASK_B", "queue_position": 1},
                ]
            ),
            "BLOCKED_QUEUE_POSITION_DUPLICATE",
        ),
    ],
)
def test_schema_and_owner_invariants_have_stable_block_codes(
    tmp_path: Path, mutate: object, expected_code: str
) -> None:
    repo = _init_repo(tmp_path)
    control = _control()
    mutate(control)  # type: ignore[operator]
    _write_board(repo, control)

    completed, output = _run_gate(repo, "Inspect")

    assert completed.returncode != 0
    assert output["code"] == expected_code


def test_parallel_exception_allows_only_recorded_secondary_owner(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    active = {
        "task_id": "TASK_PRIMARY",
        "lane": "task-primary",
        "role": "Developer",
        "branch": "lane/task-primary",
        "worktree": str(tmp_path / "primary"),
        "base_sha": "a" * 40,
        "head_sha": "b" * 40,
        "locked_paths": ["path/primary"],
        "evidence": "primary.md",
    }
    control = _control(
        execution_token_owner="TASK_PRIMARY",
        execution_state="implementation_running",
        active=active,
        parallel_exception={
            "secondary_execution_token_owner": "TASK_SECONDARY",
            "secondary_lane": "task-secondary",
            "user_approval_evidence": "USER_APPROVAL_1",
            "scope_proof": "path/secondary is disjoint",
            "locked_paths": ["path/secondary"],
            "end_condition": "secondary Integrator acceptance",
        },
    )
    _write_board(repo, control)

    secondary, secondary_output = _run_gate(
        repo, "CreateWorktree", task_id="TASK_SECONDARY", lane="task-secondary"
    )
    third, third_output = _run_gate(
        repo, "CreateWorktree", task_id="TASK_THIRD", lane="task-third"
    )

    assert secondary.returncode == 0
    assert secondary_output["code"] == "ALLOW_WORKTREE_CREATE"
    assert third.returncode != 0
    assert third_output["code"] == "BLOCKED_TOKEN_OWNED"


def test_nested_quick_fix_and_overlapping_preemption_are_rejected(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    paused = {
        "task_id": "TASK_ORIGINAL",
        "lane": "task-original",
        "branch": "lane/task-original",
        "worktree": str(tmp_path / "original"),
        "previous_owner": "Developer",
        "paused_reason": "urgent fix",
        "preempted_by": "TASK_QF",
        "checkpoint_sha": "a" * 40,
        "pause_master_sha": "b" * 40,
        "resume_condition": "after reconciliation",
        "unfinished_items": ["review"],
        "locked_paths": ["shared/path"],
        "evidence": "paused.md",
    }
    quick_fix = {
        "task_id": "TASK_QF",
        "lane": "task-qf",
        "risk_gate": "QF-2",
        "preempting_task_id": "TASK_ORIGINAL",
        "locked_paths": ["quick/path"],
        "accepted_head": None,
        "accepted_on_master": False,
        "residual_owner": None,
    }
    _write_board(
        repo,
        _control(
            execution_token_owner="TASK_QF",
            execution_state="quick_fix_running",
            paused=paused,
            quick_fix=quick_fix,
        ),
    )

    nested, nested_output = _run_gate(
        repo, "QuickFixPreempt", task_id="TASK_QF_2", lane="task-qf-2"
    )
    assert nested.returncode != 0
    assert nested_output["code"] == "BLOCKED_NESTED_PREEMPTION"

    overlap = copy.deepcopy(quick_fix)
    overlap["locked_paths"] = ["shared/path"]
    _write_board(
        repo,
        _control(
            execution_state="paused_preempted",
            paused=paused,
            quick_fix=overlap,
        ),
    )
    overlapping, overlap_output = _run_gate(
        repo, "QuickFixPreempt", task_id="TASK_QF", lane="task-qf"
    )
    assert overlapping.returncode != 0
    assert overlap_output["code"] == "BLOCKED_LOCKED_PATH_OVERLAP"
