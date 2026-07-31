from __future__ import annotations

import copy
import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "connlab_execution_gate.ps1"
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


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


def _active(
    *, task: str = "TASK_PRIMARY", lane: str = "task-primary", role: str = "Developer",
    branch: str | None = None, worktree: str = "primary-worktree",
    base: str = "a" * 40, head: str = "b" * 40,
) -> dict[str, object]:
    return {
        "task_id": task, "lane": lane, "role": role,
        "branch": branch or f"lane/{lane}", "worktree": worktree,
        "base_sha": base, "head_sha": head, "locked_paths": ["primary/path"],
        "evidence": "primary.md",
    }


def _queue(task: str, position: int, sequence: int | object | None = None) -> dict[str, object]:
    return {
        "task_id": task, "lane": task.lower().replace("_", "-"),
        "enqueue_sequence": position if sequence is None else sequence,
        "enqueued_at": f"2026-07-31T00:00:0{position}+00:00",
        "dependencies": [], "locked_paths": [f"queue/{task.lower()}"],
        "requested_priority": "normal", "queue_position": position,
        "evidence": f"{task}.md",
    }


def _parallel(*, worktree: str = "D:/disposable/secondary") -> dict[str, object]:
    return {
        "primary_task_id": "TASK_PRIMARY",
        "secondary_execution_token_owner": "TASK_SECONDARY",
        "secondary_task_id": "TASK_SECONDARY", "secondary_lane": "task-secondary",
        "secondary_role": "Developer", "secondary_branch": "lane/task-secondary",
        "secondary_worktree": worktree, "secondary_head_sha": "c" * 40,
        "user_approval_evidence": "USER_APPROVAL_1", "scope_proof": "disjoint scope",
        "independence_proof": "independent validation and authority",
        "locked_paths": ["secondary/path"], "end_condition": "Integrator acceptance",
    }


def _write_board(repo: Path, control: dict[str, object], *, duplicate: bool = False) -> None:
    block = f"{BEGIN}\n```json\n{json.dumps(control, indent=2)}\n```\n{END}\n"
    if duplicate: block = f"{block}\n{block}"
    (repo / "docs" / "task_board.md").write_text(f"# Fixture Board\n\n{block}", encoding="utf-8")


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
            "powershell.exe", "-NoProfile", "-File", str(GATE), "-Intent", intent,
            "-TaskId", task_id, "-Lane", lane, "-RepositoryRoot", str(repo),
            "-AllowTestRepositoryRoot", "-Json",
        ],
        check=False, capture_output=True, text=True,
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
    active = _active(task="TASK_OWNER", lane="task-owner", role=role, worktree=str(tmp_path / "owner"))
    active["locked_paths"] = ["shared/path"]
    _write_board(repo, _control(execution_token_owner="TASK_OWNER", execution_state=state, active=active))

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
                queue=[_queue("TASK_A", 1), _queue("TASK_B", 1, 2)]
            ),
            "BLOCKED_QUEUE_POSITION_DUPLICATE",
        ),
        (
            lambda state: state.update(
                queue=[_queue("TASK_A", 1), _queue("TASK_A", 2)]
            ),
            "BLOCKED_QUEUE_TASK_DUPLICATE",
        ),
        (
            lambda state: state.update(queue=[{"task_id": "TASK_Q", "queue_position": 1}]),
            "BLOCKED_QUEUE_INVALID",
        ),
        (
            lambda state: state.update(queue=[_queue("TASK_B", 2), _queue("TASK_A", 1)]),
            "BLOCKED_QUEUE_FIFO_INVALID",
        ),
        (
            lambda state: state.update(
                execution_state="implementation_running",
                execution_token_owner="TASK_OWNER",
                active=_active(task="TASK_OTHER", lane="task-other", worktree="unused"),
            ),
            "BLOCKED_ACTIVE_OWNER_MISMATCH",
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


def test_complete_fifo_queue_record_is_allowed_by_general_inspect(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_board(repo, _control(queue=[_queue("TASK_A", 1), _queue("TASK_B", 2)]))

    completed, output = _run_gate(repo, "Inspect")

    assert completed.returncode == 0
    assert output["code"] == "ALLOW_INSPECT"


@pytest.mark.parametrize(
    ("field", "invalid"),
    [("enqueue_sequence", "1"), ("enqueued_at", "not-a-time"),
     ("dependencies", "TASK_DEP"), ("locked_paths", []), ("requested_priority", 1)],
)
def test_queue_field_types_fail_closed(tmp_path: Path, field: str, invalid: object) -> None:
    repo = _init_repo(tmp_path)
    queue = _queue("TASK_A", 1)
    queue[field] = invalid
    _write_board(repo, _control(queue=[queue]))

    completed, output = _run_gate(repo, "Inspect")

    assert completed.returncode != 0
    assert output["code"] == "BLOCKED_QUEUE_INVALID"


def test_parallel_exception_allows_only_recorded_secondary_owner(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    active = _active(worktree=str(tmp_path / "primary"))
    active["locked_paths"] = ["path/primary"]
    control = _control(
        execution_token_owner="TASK_PRIMARY",
        execution_state="implementation_running",
        active=active,
        parallel_exception={**_parallel(worktree=str(tmp_path / "secondary")), "locked_paths": ["path/secondary"]},
    )
    _write_board(repo, control)

    inspected, inspect_output = _run_gate(repo, "Inspect")
    secondary, secondary_output = _run_gate(repo, "CreateWorktree", task_id="TASK_SECONDARY", lane="task-secondary")
    third, third_output = _run_gate(repo, "CreateWorktree", task_id="TASK_THIRD", lane="task-third")

    assert inspected.returncode == 0
    assert inspect_output["code"] == "ALLOW_INSPECT"
    assert secondary.returncode == 0
    assert secondary_output["code"] == "ALLOW_WORKTREE_CREATE"
    assert third.returncode == 0
    assert third_output["code"] == "QUEUE_REQUIRED"


def test_parallel_exception_without_primary_owner_fails_closed(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_board(
        repo,
        _control(
            parallel_exception=_parallel(),
        ),
    )

    completed, output = _run_gate(repo, "Inspect")

    assert completed.returncode != 0
    assert output["code"] == "BLOCKED_PARALLEL_PRIMARY_REQUIRED"


@pytest.mark.parametrize(
    "missing",
    [("independence_proof",),
     ("secondary_role", "secondary_branch", "secondary_worktree", "secondary_head_sha")],
)
def test_parallel_exception_requires_complete_proof(
    tmp_path: Path, missing: tuple[str, ...],
) -> None:
    repo = _init_repo(tmp_path)
    active = _active()
    incomplete = _parallel()
    for field in missing:
        incomplete.pop(field)
    _write_board(
        repo,
        _control(
            execution_token_owner="TASK_PRIMARY",
            execution_state="implementation_running",
            active=active,
            parallel_exception=incomplete,
        ),
    )

    completed, output = _run_gate(repo, "Inspect")

    assert completed.returncode != 0
    assert output["code"] == "BLOCKED_PARALLEL_EXCEPTION_INCOMPLETE"


@pytest.mark.parametrize("role", ["Reviewer", "QA", "Integrator"])
def test_gate_running_never_authorizes_implementation_dispatch(
    tmp_path: Path, role: str
) -> None:
    repo = _init_repo(tmp_path)
    active = _active(task="TASK_OWNER", lane="task-owner", role=role, branch="master", worktree=str(repo))
    _write_board(
        repo,
        _control(
            execution_token_owner="TASK_OWNER",
            execution_state="gate_running",
            active=active,
        ),
    )

    completed, output = _run_gate(repo, "ImplementationDispatch", task_id="TASK_OWNER", lane="task-owner")

    assert completed.returncode != 0
    assert output["code"] == "BLOCKED_DISPATCH_STATE"


def test_durable_developer_fix_transition_allows_primary_dispatch(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    _write_board(repo, _control())
    _git(repo, "add", "docs/task_board.md", "seed.txt")
    _git(repo, "commit", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    worktree = tmp_path / "developer-fix"
    _git(repo, "worktree", "add", "-b", "lane/developer-fix", str(worktree), base)
    active = _active(task="TASK_OWNER", lane="developer-fix", worktree=str(worktree), base=base, head=base)
    active["evidence"] = "reviewer-blocking-fix.md"
    _write_board(
        repo,
        _control(
            execution_token_owner="TASK_OWNER",
            execution_state="implementation_running",
            active=active,
        ),
    )

    completed, output = _run_gate(
        repo, "ImplementationDispatch", task_id="TASK_OWNER", lane="developer-fix"
    )

    assert completed.returncode == 0
    assert output["code"] == "ALLOW_DISPATCH"


def test_gate_invoked_from_lane_reads_primary_board_not_stale_lane_copy(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path)
    scripts = repo / "scripts"
    scripts.mkdir()
    shutil.copy2(GATE, scripts / GATE.name)
    primary = _active(worktree="primary-owner-worktree")
    _write_board(
        repo,
        _control(
            execution_token_owner="TASK_PRIMARY",
            execution_state="implementation_running",
            active=primary,
        ),
    )
    _git(repo, "add", "docs/task_board.md", "scripts/connlab_execution_gate.ps1")
    _git(repo, "commit", "-m", "primary authority")
    lane = tmp_path / "stale-lane"
    _git(repo, "worktree", "add", "-b", "lane/stale", str(lane), "HEAD")
    stale = dict(primary)
    stale.update(task_id="TASK_STALE", lane="task-stale")
    _write_board(
        lane,
        _control(
            execution_token_owner="TASK_STALE",
            execution_state="implementation_running",
            active=stale,
        ),
    )

    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-File",
            str(lane / "scripts" / GATE.name),
            "-Intent",
            "StartTask",
            "-TaskId",
            "TASK_STALE",
            "-Lane",
            "task-stale",
            "-Json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    output = json.loads(completed.stdout)
    dispatch = subprocess.run(
        [
            "powershell.exe", "-NoProfile", "-File", str(lane / "scripts" / GATE.name),
            "-Intent", "ImplementationDispatch", "-TaskId", "TASK_STALE",
            "-Lane", "task-stale", "-Json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    dispatch_output = json.loads(dispatch.stdout)

    assert completed.returncode == 0
    assert output["code"] == "QUEUE_REQUIRED"
    assert output["execution_token_owner"] == "TASK_PRIMARY"
    assert Path(str(output["authority_root"])) == repo
    assert dispatch.returncode != 0
    assert dispatch_output["code"] == "BLOCKED_TOKEN_OWNED"
    assert Path(str(dispatch_output["authority_root"])) == repo


def test_nested_quick_fix_and_overlapping_preemption_are_rejected(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    paused = {
        "task_id": "TASK_ORIGINAL", "lane": "task-original",
        "branch": "lane/task-original", "worktree": str(tmp_path / "original"),
        "previous_owner": "Developer", "paused_reason": "urgent fix",
        "preempted_by": "TASK_QF", "checkpoint_sha": "a" * 40,
        "pause_master_sha": "b" * 40, "resume_condition": "after reconciliation",
        "unfinished_items": ["review"], "locked_paths": ["shared/path"],
        "evidence": "paused.md",
    }
    quick_fix = {
        "task_id": "TASK_QF", "lane": "task-qf", "role": "Quick Fixer",
        "risk_gate": "QF-2", "goal": "Repair a bounded defect",
        "why_safe": "Reproduced, disjoint, and no authority change",
        "may_touch": ["quick/path"], "must_not_touch": ["authority/path"],
        "preempting_task_id": "TASK_ORIGINAL", "locked_paths": ["quick/path"],
        "targeted_validation": ["targeted smoke"],
        "required_gates": ["Reviewer", "Integrator"],
        "planner_required": False, "full_plan_required": False, "qa_required": False,
        "branch": "lane/task-qf", "worktree": str(tmp_path / "quick-fix"),
        "base_sha": "a" * 40, "head_sha": "a" * 40, "evidence": "quick-fix.md",
        "accepted_head": None, "accepted_on_master": False,
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

    nested, nested_output = _run_gate(repo, "QuickFixPreempt", task_id="TASK_QF_2", lane="task-qf-2")
    assert nested.returncode != 0
    assert nested_output["code"] == "BLOCKED_NESTED_PREEMPTION"

    overlap = copy.deepcopy(quick_fix)
    overlap["locked_paths"] = ["shared/path"]
    _write_board(repo, _control(execution_state="paused_preempted", paused=paused, quick_fix=overlap))
    overlapping, overlap_output = _run_gate(repo, "QuickFixPreempt", task_id="TASK_QF", lane="task-qf")
    assert overlapping.returncode != 0
    assert overlap_output["code"] == "BLOCKED_LOCKED_PATH_OVERLAP"
