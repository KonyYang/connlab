from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.connlab_validation_manifest import ManifestError, run_manifest, validate_manifest
from scripts.connlab_serial_board import render_board, v2_submit


def manifest(argv: list[str], *, permission: str = "workspace") -> dict:
    return {
        "schema": "connlab.validation-manifest",
        "version": 1,
        "task_id": "TASK_VALIDATION",
        "checks": [{
            "id": "literal-argv",
            "kind": "targeted",
            "run_for": ["Developer", "QA"],
            "cwd": ".",
            "argv": argv,
            "timeout_seconds": 30,
            "permission": permission,
            "required": True,
        }],
    }


def init_repo(path: Path) -> None:
    path.mkdir()
    subprocess.run(["git", "-C", str(path), "init", "-b", "master"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Validation Test"], check=True)
    (path / "tracked.txt").write_text("clean\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "tracked.txt"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "fixture"], check=True, capture_output=True)


def test_runner_passes_shell_metacharacters_as_literal_argv_and_binds_subject(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    init_repo(repo)
    value = manifest([
        sys.executable,
        "-c",
        "import sys; raise SystemExit(0 if sys.argv[1] == 'literal;not-shell' else 9)",
        "literal;not-shell",
    ])

    result = run_manifest(repo, validate_manifest(value), role="Developer", allowed_permissions={"workspace"})

    assert result["status"] == "passed"
    assert result["subject_before"] == result["subject_after"]
    assert result["checks"][0]["argv"][-1] == "literal;not-shell"
    assert result["checks"][0]["exit_code"] == 0


def test_runner_requests_declared_permission_before_starting_the_command(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    init_repo(repo)
    marker = repo / "must-not-exist.txt"
    value = manifest([sys.executable, "-c", f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')"], permission="pytest_temp")

    result = run_manifest(repo, validate_manifest(value), role="QA", allowed_permissions={"workspace"})

    assert result["status"] == "blocked"
    assert result["code"] == "BLOCKED_PERMISSION_REQUIRED"
    assert result["required_permissions"] == ["pytest_temp"]
    assert not marker.exists()


def test_non_developer_validation_rejects_a_subject_that_differs_from_board(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    init_repo(repo)
    marker = repo / "ran.txt"
    value = manifest([sys.executable, "-c", "from pathlib import Path; Path('ran.txt').write_text('ran')"])
    binding = {
        "task_id": "TASK_VALIDATION",
        "role": "QA",
        "attempt": 1,
        "repo_root": str(repo.resolve()),
        "recorded_subject": "0" * 40,
    }

    result = run_manifest(
        repo, value, role="QA", allowed_permissions={"workspace"}, binding=binding,
    )

    assert result["code"] == "BLOCKED_SUBJECT_MISMATCH"
    assert not marker.exists()


def test_manifest_rejects_shell_strings_and_parent_cwd() -> None:
    bad_argv = manifest(["py -m pytest"])
    bad_cwd = manifest([sys.executable, "-V"])
    bad_cwd["checks"][0]["cwd"] = "../outside"

    with pytest.raises(ManifestError, match="argv"):
        validate_manifest(bad_argv)
    with pytest.raises(ManifestError, match="cwd"):
        validate_manifest(bad_cwd)


@pytest.mark.parametrize("explicit_repo_root", [False, True])
def test_cli_reads_manifest_from_primary_authority_and_runs_on_task_worktree(
    tmp_path: Path, explicit_repo_root: bool,
) -> None:
    primary = tmp_path / "primary"
    task = tmp_path / "task"
    init_repo(primary)
    subprocess.run(
        ["git", "-C", str(primary), "worktree", "add", "-b", "task", str(task), "HEAD"],
        check=True,
        capture_output=True,
    )
    (task / "tracked.txt").write_text("task\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(task), "add", "tracked.txt"], check=True)
    subprocess.run(["git", "-C", str(task), "commit", "-m", "task subject"], check=True, capture_output=True)
    task_head = subprocess.run(
        ["git", "-C", str(task), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    value = manifest([
        sys.executable,
        "-c",
        "from pathlib import Path; raise SystemExit(0 if Path('tracked.txt').read_text() == 'task\\n' else 9)",
    ])
    control = {
        "schema": "connlab.personal-serial-control",
        "version": 2,
        "mode": "personal_serial",
        "wip_limit": 1,
        "state": "idle",
        "active": None,
        "queue": [],
        "next_enqueue_sequence": 1,
        "last_closed": None,
        "retained_history": [],
    }
    request = {
        "schema": "connlab.serial-task-request",
        "version": 1,
        "task_id": "TASK_VALIDATION",
        "summary": "Validate an exact task subject from primary authority.",
        "root_cause_clear": True,
        "expected_result_clear": True,
        "may_touch": ["tracked.txt", "docs/task_board.md"],
        "targeted_validation": ["validation manifest runner"],
        "requires_independent_review": True,
        "forbidden_categories": {
            "api_contract": False,
            "database": False,
            "schema_or_migration": False,
            "persistence": False,
            "authority": False,
            "public_drive_workflow": False,
            "business_rule_semantics": False,
            "destructive_action": False,
            "external_mutation": False,
            "push_or_release": False,
        },
    }
    v2_submit(control, request, subprocess.run(
        ["git", "-C", str(primary), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip())
    active = control["active"]
    active["phase"] = "qa"
    context = active["complex_context"]
    context.update(
        task_branch="task",
        task_worktree=str(task.resolve()),
        head_sha=task_head,
        current_role="QA",
        current_attempt=1,
        validation_manifest=value,
    )
    board = primary / "docs" / "task_board.md"
    board.parent.mkdir()
    board_bytes = render_board("", control, "\n")
    board.write_bytes(board_bytes)
    subprocess.run(["git", "-C", str(primary), "add", "docs/task_board.md"], check=True)
    subprocess.run(["git", "-C", str(primary), "commit", "-m", "qa authority"], check=True, capture_output=True)

    command = [
        sys.executable,
        "-m",
        "scripts.connlab_validation_manifest",
        "run",
        "--authority-root",
        str(primary),
        "--from-board",
        "--role",
        "QA",
    ]
    if explicit_repo_root:
        command.extend(["--repo-root", str(task)])
    completed = subprocess.run(
        command,
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    result = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert result["status"] == "passed"
    assert result["subject_before"] == result["subject_after"] == task_head
    assert result["binding"] == {
        "task_id": "TASK_VALIDATION",
        "role": "QA",
        "attempt": 1,
        "repo_root": str(task.resolve()),
        "recorded_subject": task_head,
    }
    assert result["authority"] == {
        "root": str(primary.resolve()),
        "head": subprocess.run(
            ["git", "-C", str(primary), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip(),
        "board_sha256": hashlib.sha256(board_bytes).hexdigest(),
        "manifest_sha256": hashlib.sha256(
            json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest(),
    }
