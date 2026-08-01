from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts" / "connlab_active_context.py"
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def board_text(control: dict[str, object], terminal_count: int, filler_lines: int = 0) -> str:
    active = control["active"]
    assert isinstance(active, dict)
    payload = json.dumps(control, indent=2)
    terminal = "\n".join(
        f"- `TASK_OLD_{index:03d}`: complete/accepted. Evidence: `old-{index}.md`."
        for index in range(terminal_count)
    )
    filler = "\n".join(f"Historical explanatory line {index}." for index in range(filler_lines))
    return (
        "# ConnLab Task Board\n\n"
        f"> Current Active Task: `{active['task_id']}` is the sole WIP=`1` token owner "
        f"in `{control['execution_state']}/{active['role']}` on lane `{active['lane']}`.\n\n"
        f"{BEGIN}\n```json\n{payload}\n```\n{END}\n\n"
        "## Active Execution Model\n\n"
        f"- `{active['task_id']}`: gate_running/Integrator; current evidence retained.\n"
        "- `TASK_NEXT`: `planned_pending_user_approval`; proposed and not executable.\n"
        f"{terminal}\n{filler}\n"
    )


def make_repo(tmp_path: Path, *, terminal_count: int = 30, filler_lines: int = 430) -> dict[str, object]:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-b", "master")
    git(repo, "config", "user.email", "maintenance@example.invalid")
    git(repo, "config", "user.name", "Maintenance Test")
    (repo / "docs").mkdir()
    (repo / "scripts").mkdir()
    shutil.copy2(HELPER, repo / "scripts" / HELPER.name)
    control: dict[str, object] = {
        "schema": "connlab.execution-control", "version": 1, "wip_limit": 1,
        "execution_token_owner": "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF",
        "execution_state": "gate_running",
        "active": {
            "task_id": "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF",
            "lane": "task-governance-active-context-deterministic-transition-and-event-handoff",
            "role": "Integrator", "branch": "lane/task-a", "worktree": str(tmp_path / "lane"),
            "base_sha": "a" * 40, "head_sha": "b" * 40, "locked_paths": ["docs/task_board.md"],
            "required_gates": ["Reviewer", "QA", "Integrator"], "evidence": "qa.md",
        },
        "queue": [], "paused": None, "quick_fix": None,
        "residuals": [{"task_id": "OLD", "residual_owner": "owner", "disposition": "retain", "evidence": "old.md"}],
        "parallel_exception": None, "last_governance_commit": "fixture", "evidence": "qa.md",
        "transition_history": [
            {"event": "DEVELOPER_READY"}, {"event": "REVIEWER_PASS"}, {"event": "QA_PASS"}
        ],
    }
    board = repo / "docs" / "task_board.md"
    board.write_text(board_text(control, terminal_count, filler_lines), encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "integrator closeout")
    return {"repo": repo, "board": board, "head": git(repo, "rev-parse", "HEAD")}


def invoke(fx: dict[str, object], command: str, **extra: str) -> tuple[int, dict[str, object]]:
    args = ["py", str(HELPER), command, "--repo-root", str(fx["repo"])]
    if command in {"plan-maintenance", "apply-maintenance"}:
        values = {
            "expected-head": str(fx["head"]),
            "expected-board-sha256": hashlib.sha256(Path(fx["board"]).read_bytes()).hexdigest(),
        }
        values.update(extra)
        for key, value in values.items():
            args.extend((f"--{key}", value))
        if command == "apply-maintenance" and "expected-plan-digest" not in values:
            plan = invoke(fx, "plan-maintenance")[1]
            args.extend(("--expected-plan-digest", str(plan["plan_digest"])))
    args.append("--json")
    done = subprocess.run(args, check=False, capture_output=True, text=True)
    return done.returncode, json.loads(done.stdout)


def test_first_plan_is_zero_write_and_first_apply_archives_exact_board(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    board = Path(fx["board"])
    before = board.read_bytes()
    before_tree = sorted(path.relative_to(fx["repo"]).as_posix() for path in Path(fx["repo"]).rglob("*") if path.is_file())

    code, plan = invoke(fx, "plan-maintenance")
    assert code == 0 and plan["decision"] == "MAINTENANCE_REQUIRED"
    assert plan["generation"] == 1 and plan["zero_write"] is True
    assert board.read_bytes() == before
    assert sorted(path.relative_to(fx["repo"]).as_posix() for path in Path(fx["repo"]).rglob("*") if path.is_file()) == before_tree

    code, applied = invoke(fx, "apply-maintenance")
    assert code == 0 and applied["decision"] == "APPLIED_MAINTENANCE"
    assert applied["changed_paths"] == [
        "docs/archive/task_board_history/generation-000001-" + str(fx["head"]) + ".md",
        "docs/archive/task_board_history/index.v1.jsonl",
        "docs/task_board.md",
    ]
    archive = Path(fx["repo"]) / applied["archive_path"]
    assert archive.read_bytes() == before
    assert len(board.read_text(encoding="utf-8").splitlines()) <= 400
    assert len(board.read_bytes()) <= 65_536
    assert "TASK_NEXT" in board.read_text(encoding="utf-8")
    assert BEGIN in board.read_text(encoding="utf-8")


def test_below_all_thresholds_is_zero_write(tmp_path: Path) -> None:
    fx = make_repo(tmp_path, terminal_count=2, filler_lines=0)
    before = Path(fx["board"]).read_bytes()

    code, plan = invoke(fx, "plan-maintenance")

    assert code == 0 and plan["decision"] == "NO_MAINTENANCE_REQUIRED"
    assert plan["changed_paths"] == []
    assert Path(fx["board"]).read_bytes() == before


def test_each_line_byte_and_terminal_threshold_triggers_independently(tmp_path: Path) -> None:
    line_fx = make_repo(tmp_path / "lines", terminal_count=2, filler_lines=430)
    terminal_fx = make_repo(tmp_path / "terminal", terminal_count=25, filler_lines=0)
    byte_fx = make_repo(tmp_path / "bytes", terminal_count=2, filler_lines=0)
    board = Path(byte_fx["board"])
    board.write_text(board.read_text(encoding="utf-8") + ("X" * 66_000) + "\n", encoding="utf-8")
    git(Path(byte_fx["repo"]), "add", "docs/task_board.md")
    git(Path(byte_fx["repo"]), "commit", "-m", "byte threshold")
    byte_fx["head"] = git(Path(byte_fx["repo"]), "rev-parse", "HEAD")

    for fx in (line_fx, terminal_fx, byte_fx):
        code, plan = invoke(fx, "plan-maintenance")
        assert code == 0 and plan["decision"] == "MAINTENANCE_REQUIRED"


def test_first_generation_proves_byte_exact_rollback(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    original = Path(fx["board"]).read_bytes()
    invoke(fx, "apply-maintenance")
    output = tmp_path / "rollback.md"
    done = subprocess.run(
        ["py", str(HELPER), "prove-rollback", "--repo-root", str(fx["repo"]), "--generation", "1", "--output", str(output), "--json"],
        check=False, capture_output=True, text=True,
    )
    result = json.loads(done.stdout)
    assert done.returncode == 0 and result["decision"] == "ROLLBACK_PROVEN"
    assert output.read_bytes() == original


def test_same_generation_apply_is_idempotent(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    original_hash = hashlib.sha256(Path(fx["board"]).read_bytes()).hexdigest()
    plan = invoke(fx, "plan-maintenance")[1]
    assert invoke(fx, "apply-maintenance")[0] == 0

    code, repeated = invoke(
        fx,
        "apply-maintenance",
        **{
            "expected-board-sha256": original_hash,
            "expected-plan-digest": str(plan["plan_digest"]),
        },
    )

    assert code == 0 and repeated["decision"] == "ALREADY_APPLIED"
    assert repeated["changed_paths"] == []


def test_apply_requires_integrator_and_complete_gate_history(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    board = Path(fx["board"])
    raw = board.read_text(encoding="utf-8")
    raw = raw.replace('"role": "Integrator"', '"role": "Reviewer"').replace("gate_running/Integrator", "gate_running/Reviewer")
    board.write_text(raw, encoding="utf-8")
    git(Path(fx["repo"]), "add", "docs/task_board.md")
    git(Path(fx["repo"]), "commit", "-m", "reviewer authority")
    fx["head"] = git(Path(fx["repo"]), "rev-parse", "HEAD")

    code, result = invoke(fx, "apply-maintenance")

    assert code != 0
    assert "BLOCKED_MAINTENANCE_AUTHORITY" in result["reason_codes"]
