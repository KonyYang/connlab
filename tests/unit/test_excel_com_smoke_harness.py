from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from backend.infrastructure.office.excel_com_smoke_harness import (
    ExcelComSmokeCommand,
    _cleanup_run_directory,
    _parse_child_result,
    _smoke_child_command,
    run_excel_com_smoke,
)


def test_smoke_runner_returns_timeout_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def timeout_run(*args: object, **kwargs: object) -> object:
        raise subprocess.TimeoutExpired(
            cmd=["py", "-m", "backend.infrastructure.office.excel_com_smoke_child"],
            timeout=0.01,
            output="partial stdout",
            stderr="partial stderr",
        )

    monkeypatch.setattr(
        "backend.infrastructure.office.excel_com_smoke_harness.subprocess.run",
        timeout_run,
    )

    result = run_excel_com_smoke(
        ExcelComSmokeCommand(
            template_path=tmp_path / "template.xls",
            output_root=tmp_path / "runs",
            timeout_seconds=0.01,
        )
    )

    assert result.timed_out is True
    assert result.exit_code is None
    assert result.stdout == "partial stdout"
    assert result.stderr == "partial stderr"
    assert result.manual_cleanup_warning is not None
    assert result.status == "timeout"


def test_child_command_uses_absolute_paths(tmp_path: Path) -> None:
    command = ExcelComSmokeCommand(
        template_path=tmp_path / "template.xls",
        output_root=tmp_path / "runs",
        output_name="smoke.xls",
    )

    argv = _smoke_child_command(command, run_dir=tmp_path / "runs" / "run-1")

    assert "-m" in argv
    assert "backend.infrastructure.office.excel_com_smoke_child" in argv
    assert str((tmp_path / "template.xls").resolve()) in argv
    assert str((tmp_path / "runs" / "run-1").resolve()) in argv
    assert "smoke.xls" in argv


def test_parse_valid_child_json_result() -> None:
    result = _parse_child_result(
        stdout=(
            '{"status":"success","output_path":"C:/tmp/out.xls",'
            '"output_size":123,"steps":[{"name":"start","message":"ok"}],'
            '"warnings":["manual"],"manual_cleanup_warning":null}'
        ),
        stderr="",
        exit_code=0,
        elapsed_seconds=1.25,
    )

    assert result.status == "success"
    assert result.timed_out is False
    assert result.exit_code == 0
    assert result.output_path == Path("C:/tmp/out.xls")
    assert result.output_size == 123
    assert result.steps[0]["name"] == "start"
    assert result.warnings == ("manual",)


def test_parse_non_json_stdout_is_execution_failure() -> None:
    result = _parse_child_result(
        stdout='ordinary log\n{"status":"success"}',
        stderr="",
        exit_code=0,
        elapsed_seconds=0.1,
    )

    assert result.status == "execution_failure"
    assert result.timed_out is False
    assert "valid JSON" in result.error_message


def test_cleanup_removes_harness_owned_run_directory(tmp_path: Path) -> None:
    root = tmp_path / "harness"
    run_dir = root / "run-1"
    run_dir.mkdir(parents=True)
    (run_dir / "out.xls").write_text("x", encoding="utf-8")

    _cleanup_run_directory(root=root, run_dir=run_dir)

    assert not run_dir.exists()
    assert root.exists()


def test_cleanup_refuses_external_directory(tmp_path: Path) -> None:
    root = tmp_path / "harness"
    external = tmp_path / "external"
    root.mkdir()
    external.mkdir()

    with pytest.raises(ValueError, match="outside harness root"):
        _cleanup_run_directory(root=root, run_dir=external)

    assert external.exists()
