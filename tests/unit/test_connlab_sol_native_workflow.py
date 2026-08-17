from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "connlab_sol_task.py"
RUN_TASK = ROOT / "scripts" / "run_task.ps1"
BOARD = Path("docs/task_board.md")
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def board_bytes(repo: Path) -> bytes:
    return (repo / BOARD).read_bytes()


def board_hash(repo: Path) -> str:
    return hashlib.sha256(board_bytes(repo)).hexdigest()


def control(repo: Path) -> dict:
    text = (repo / BOARD).read_text(encoding="utf-8")
    payload = text.split(BEGIN, 1)[1].split(END, 1)[0]
    payload = payload.split("```json", 1)[1].rsplit("```", 1)[0]
    return json.loads(payload)


def write_board(repo: Path) -> None:
    value = {
        "schema": "connlab.sol-task-control",
        "version": 1,
        "mode": "sol_native",
        "wip_limit": 1,
        "state": "idle",
        "active": None,
        "last_closed": None,
        "retained_history": [],
    }
    board = repo / BOARD
    board.parent.mkdir(parents=True)
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


def invoke(
    repo: Path,
    command: str,
    *args: str,
    expected_exit: int = 0,
) -> dict:
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            command,
            "--repo-root",
            str(repo),
            "--json",
            *args,
        ],
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    assert completed.returncode == expected_exit, completed.stderr or completed.stdout
    return json.loads(completed.stdout)


def request(
    task_id: str,
    tier: str,
    *,
    risks: list[str] | None = None,
    scope_paths: list[str] | None = None,
) -> str:
    return json.dumps(
        {
            "schema": "connlab.sol-task-request",
            "version": 1,
            "task_id": task_id,
            "summary": f"Implement {task_id} without expanding its requested scope.",
            "tier": tier,
            "scope": "Only the behavior requested by the User.",
            "scope_paths": scope_paths or ["impl.py"],
            "risk_reasons": risks or [],
        }
    )


def report(task_id: str, subject: str, tier: str) -> dict:
    roles = {
        "developer": {"status": "passed", "summary": "Implemented and self-reviewed."},
    }
    if tier in {"standard", "high_risk"}:
        roles.update(
            reviewer={"status": "passed", "summary": "Independent review passed."},
            qa={"status": "passed", "summary": "Independent complete validation passed."},
        )
    if tier == "high_risk":
        roles.update(
            planner={"status": "passed", "summary": "Plan remained in scope."},
            integrator={"status": "passed", "summary": "Integration facts passed."},
        )
    return {
        "schema": "connlab.sol-task-report",
        "version": 1,
        "task_id": task_id,
        "subject": subject,
        "summary": "Requested behavior is complete.",
        "scope_ok": True,
        "changed_paths": ["impl.py"],
        "validation": [{"name": "targeted", "status": "passed"}],
        "roles": roles,
        "integration": {
            "status": "passed",
            "mode": "direct_primary" if tier != "high_risk" else "verified_local",
        },
    }


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    write_board(tmp_path)
    (tmp_path / ".gitignore").write_text("tmp/\n", encoding="utf-8")
    git(tmp_path, "init", "-b", "master")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test User")
    git(tmp_path, "add", ".gitignore", str(BOARD))
    git(tmp_path, "commit", "-m", "baseline")
    return tmp_path


def submit(repo: Path, task_id: str, tier: str, *, risks: list[str] | None = None) -> dict:
    return invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        task_id,
        "--request-json",
        request(task_id, tier, risks=risks),
    )


def commit_activation_and_implementation(repo: Path) -> str:
    git(repo, "add", str(BOARD))
    git(repo, "commit", "-m", "activate task")
    revision_count = git(repo, "rev-list", "--count", "HEAD")
    (repo / "impl.py").write_text(f"VALUE = {revision_count}\n", encoding="utf-8")
    git(repo, "add", "impl.py")
    git(repo, "commit", "-m", "implement task")
    return git(repo, "rev-parse", "HEAD")


def test_inspect_exposes_only_compact_sol_native_next_action(repo: Path) -> None:
    result = invoke(repo, "inspect")

    assert result["code"] == "ALLOW_INSPECT"
    assert result["state"] == "idle"
    assert result["next_action"] == {"command": "submit", "requires_user": True}
    assert "command_contract" not in result["next_action"]


@pytest.mark.parametrize(
    ("tier", "expected_route"),
    [("micro", "sol_direct"), ("standard", "sol_build_review_qa"), ("high_risk", "full_chain")],
)
def test_submit_activates_one_of_three_routes(repo: Path, tier: str, expected_route: str) -> None:
    result = submit(
        repo,
        "TASK_ROUTE",
        tier,
        risks=["database migration"] if tier == "high_risk" else None,
    )

    assert result["code"] == "ALLOW_SUBMIT"
    assert result["active_snapshot"]["tier"] == tier
    assert result["active_snapshot"]["route"] == expected_route
    assert result["next_action"] == {"command": "execute", "requires_user": False}


def test_occupied_submit_is_zero_write(repo: Path) -> None:
    submit(repo, "TASK_ONE", "standard")
    before = board_bytes(repo)

    blocked = invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_TWO",
        "--request-json",
        request("TASK_TWO", "micro"),
        expected_exit=2,
    )

    assert blocked["code"] == "BLOCKED_ACTIVE_TASK_RUNNING"
    assert board_bytes(repo) == before


def test_stale_board_hash_is_zero_write(repo: Path) -> None:
    before = board_bytes(repo)

    blocked = invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        "0" * 64,
        "--task-id",
        "TASK_STALE",
        "--request-json",
        request("TASK_STALE", "micro"),
        expected_exit=2,
    )

    assert blocked["code"] == "BLOCKED_BOARD_HASH_MISMATCH"
    assert board_bytes(repo) == before


def test_stale_lock_file_does_not_block_recovery(repo: Path) -> None:
    lock = repo / "tmp" / "connlab_sol_task.lock"
    lock.parent.mkdir()
    lock.write_text("stale-after-restart", encoding="utf-8")

    result = submit(repo, "TASK_AFTER_RESTART", "micro")

    assert result["code"] == "ALLOW_SUBMIT"
    assert result["active_task_id"] == "TASK_AFTER_RESTART"


def test_invalid_or_normalized_duplicate_paths_return_typed_blocker(repo: Path) -> None:
    for paths in ([{"not": "a path"}], ["same/path.py", "same\\path.py"]):
        payload = json.loads(request("TASK_BAD_PATH", "micro"))
        payload["scope_paths"] = paths
        before = board_bytes(repo)

        blocked = invoke(
            repo,
            "submit",
            "--expected-board-sha256",
            board_hash(repo),
            "--task-id",
            "TASK_BAD_PATH",
            "--request-json",
            json.dumps(payload),
            expected_exit=2,
        )

        assert blocked["code"] == "BLOCKED_REQUEST_INVALID"
        assert board_bytes(repo) == before


def test_checkpoint_records_one_compact_recovery_fact(repo: Path) -> None:
    submit(repo, "TASK_RECOVER", "standard")
    payload = {
        "schema": "connlab.sol-task-checkpoint",
        "version": 1,
        "task_id": "TASK_RECOVER",
        "stage": "implementation",
        "status": "running",
        "summary": "Public seam implemented; targeted validation remains.",
        "requires_user": False,
    }

    result = invoke(
        repo,
        "checkpoint",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_RECOVER",
        "--checkpoint-json",
        json.dumps(payload),
    )

    assert result["code"] == "ALLOW_CHECKPOINT"
    assert result["active_snapshot"]["checkpoint"] == payload
    assert result["next_action"] == {"command": "execute", "requires_user": False}


def test_risk_cannot_be_downgraded_to_a_faster_tier(repo: Path) -> None:
    before = board_bytes(repo)

    blocked = invoke(
        repo,
        "submit",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_RISK",
        "--request-json",
        request("TASK_RISK", "standard", risks=["destructive external mutation"]),
        expected_exit=2,
    )

    assert blocked["code"] == "BLOCKED_TIER_UNSAFE"
    assert board_bytes(repo) == before


def test_finish_requires_only_proportionate_role_results(repo: Path) -> None:
    for tier in ("micro", "standard", "high_risk"):
        task_id = f"TASK_{tier.upper()}"
        submit(
            repo,
            task_id,
            tier,
            risks=["security-sensitive migration"] if tier == "high_risk" else None,
        )
        subject = commit_activation_and_implementation(repo)
        result = invoke(
            repo,
            "finish",
            "--expected-board-sha256",
            board_hash(repo),
            "--task-id",
            task_id,
            "--result-json",
            json.dumps(report(task_id, subject, tier)),
        )
        assert result["code"] == "ALLOW_FINISH"
        assert result["state"] == "ready_for_close"
        git(repo, "add", str(BOARD))
        git(repo, "commit", "-m", "finish task")
        invoke(
            repo,
            "close",
            "--expected-board-sha256",
            board_hash(repo),
            "--task-id",
            task_id,
            "--decision-ref",
            "User closed the completed task.",
        )
        git(repo, "add", str(BOARD))
        git(repo, "commit", "-m", "close task")


def test_standard_finish_rejects_missing_independent_qa(repo: Path) -> None:
    submit(repo, "TASK_STANDARD", "standard")
    subject = commit_activation_and_implementation(repo)
    value = report("TASK_STANDARD", subject, "standard")
    del value["roles"]["qa"]

    blocked = invoke(
        repo,
        "finish",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_STANDARD",
        "--result-json",
        json.dumps(value),
        expected_exit=2,
    )

    assert blocked["code"] == "BLOCKED_REPORT_INCOMPLETE"


def test_finish_rejects_scope_drift_and_subject_mismatch(repo: Path) -> None:
    submit(repo, "TASK_SCOPE", "micro")
    subject = commit_activation_and_implementation(repo)
    value = report("TASK_SCOPE", subject, "micro")
    value["changed_paths"] = ["other.py"]

    drift = invoke(
        repo,
        "finish",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_SCOPE",
        "--result-json",
        json.dumps(value),
        expected_exit=2,
    )
    value["changed_paths"] = ["impl.py"]
    value["subject"] = "0" * 40
    mismatch = invoke(
        repo,
        "finish",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_SCOPE",
        "--result-json",
        json.dumps(value),
        expected_exit=2,
    )

    assert drift["code"] == "BLOCKED_SCOPE_DRIFT"
    assert mismatch["code"] == "BLOCKED_SUBJECT_MISMATCH"


def test_only_explicit_close_releases_wip(repo: Path) -> None:
    submit(repo, "TASK_CLOSE", "micro")
    subject = commit_activation_and_implementation(repo)
    invoke(
        repo,
        "finish",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_CLOSE",
        "--result-json",
        json.dumps(report("TASK_CLOSE", subject, "micro")),
    )
    git(repo, "add", str(BOARD))
    git(repo, "commit", "-m", "ready for close")

    closed = invoke(
        repo,
        "close",
        "--expected-board-sha256",
        board_hash(repo),
        "--task-id",
        "TASK_CLOSE",
        "--decision-ref",
        "User said close.",
    )

    assert closed["code"] == "ALLOW_CLOSE"
    assert closed["state"] == "idle"
    assert control(repo)["last_closed"]["task_id"] == "TASK_CLOSE"


def test_legacy_approve_command_is_not_exposed(repo: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "approve", "--repo-root", str(repo), "--json"],
        text=True,
        encoding="utf-8",
        capture_output=True,
    )

    assert completed.returncode == 2
    assert "invalid choice" in completed.stderr


def test_powershell_user_entry_supports_only_submit_and_final_close(repo: Path) -> None:
    submitted = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-File",
            str(RUN_TASK),
            "-Task",
            "TASK_PS_ENTRY",
            "-Action",
            "Submit",
            "-RequestJson",
            request("TASK_PS_ENTRY", "micro"),
            "-ExpectedBoardSha256",
            board_hash(repo),
            "-RepositoryRoot",
            str(repo),
            "-Json",
        ],
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    assert submitted.returncode == 0, submitted.stderr or submitted.stdout
    assert json.loads(submitted.stdout)["code"] == "ALLOW_SUBMIT"

    git(repo, "add", str(BOARD))
    git(repo, "commit", "-m", "activate task through public entry")
    closed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-File",
            str(RUN_TASK),
            "-Task",
            "TASK_PS_ENTRY",
            "-Action",
            "Close",
            "-Disposition",
            "cancelled",
            "-DecisionRef",
            "User explicitly cancelled the test task.",
            "-ExpectedBoardSha256",
            board_hash(repo),
            "-RepositoryRoot",
            str(repo),
            "-Json",
        ],
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    assert closed.returncode == 0, closed.stderr or closed.stdout
    assert json.loads(closed.stdout)["code"] == "ALLOW_CLOSE"
    assert control(repo)["state"] == "idle"

    source = RUN_TASK.read_text(encoding="utf-8")
    assert '[ValidateSet("Submit", "Close")]' in source
    assert "Approve" not in source
