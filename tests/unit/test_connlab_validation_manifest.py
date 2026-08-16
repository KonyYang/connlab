from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.connlab_validation_manifest import ManifestError, run_manifest, validate_manifest


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


def test_manifest_rejects_shell_strings_and_parent_cwd() -> None:
    bad_argv = manifest(["py -m pytest"])
    bad_cwd = manifest([sys.executable, "-V"])
    bad_cwd["checks"][0]["cwd"] = "../outside"

    with pytest.raises(ManifestError, match="argv"):
        validate_manifest(bad_argv)
    with pytest.raises(ManifestError, match="cwd"):
        validate_manifest(bad_cwd)
