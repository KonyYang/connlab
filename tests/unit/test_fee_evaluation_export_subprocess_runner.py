from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from backend.application.confirmed_matrix_fee_evaluation_export_service import (
    ExportConfirmedMatrixFeeEvaluationCommand,
)
from backend.infrastructure.office.fee_evaluation_export_subprocess_runner import (
    FeeEvaluationExportSubprocessRunner,
    _child_command,
    _parse_child_result,
)


def test_runner_returns_timeout_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def timeout_run(*args: object, **kwargs: object) -> object:
        raise subprocess.TimeoutExpired(
            cmd=["py", "-m", "backend.infrastructure.office.fee_evaluation_export_child"],
            timeout=0.01,
            output="partial stdout",
            stderr="partial stderr",
        )

    monkeypatch.setattr(
        "backend.infrastructure.office.fee_evaluation_export_subprocess_runner.subprocess.run",
        timeout_run,
    )
    runner = FeeEvaluationExportSubprocessRunner(
        output_root=tmp_path / "runs",
        timeout_seconds=0.01,
    )

    result = runner.run(_command(tmp_path))

    assert result.status == "timeout"
    assert result.timed_out is True
    assert result.exit_code is None
    assert result.stdout == "partial stdout"
    assert result.stderr == "partial stderr"
    assert result.manual_cleanup_warning is not None


def test_child_command_uses_absolute_command_json_path(tmp_path: Path) -> None:
    command_json = tmp_path / "runs" / "run-1" / "command.json"

    argv = _child_command(command_json)

    assert "-m" in argv
    assert "backend.infrastructure.office.fee_evaluation_export_child" in argv
    assert str(command_json.resolve()) in argv


def test_child_command_uses_packaged_child_flag_when_frozen(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command_json = tmp_path / "runs" / "run-1" / "command.json"
    executable = r"D:\Release\ConnLab_Server.exe"
    import backend.infrastructure.office.fee_evaluation_export_subprocess_runner as runner_module

    monkeypatch.setattr(runner_module.sys, "frozen", True, raising=False)
    monkeypatch.setattr(runner_module.sys, "executable", executable)

    argv = _child_command(command_json)

    assert argv == [
        executable,
        "--connlab-fee-export-child",
        "--command-json",
        str(command_json.resolve()),
    ]
    assert "-m" not in argv


def test_parse_success_child_json_result() -> None:
    result = _parse_child_result(
        stdout='{"status":"success","result":{"project_id":"P1"},"warnings":[]}',
        stderr="",
        exit_code=0,
        elapsed_seconds=1.2,
    )

    assert result.status == "success"
    assert result.timed_out is False
    assert result.exit_code == 0
    assert result.payload["result"]["project_id"] == "P1"


def test_parse_non_json_stdout_is_execution_failure() -> None:
    result = _parse_child_result(
        stdout='ordinary log\n{"status":"success"}',
        stderr="",
        exit_code=0,
        elapsed_seconds=0.2,
    )

    assert result.status == "execution_failure"
    assert "valid JSON" in result.error_message
    assert result.stdout.startswith("ordinary log")


def test_runner_removes_only_harness_command_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def success_run(*args: object, **kwargs: object) -> object:
        class Completed:
            stdout = '{"status":"execution_failure","error_message":"fake"}'
            stderr = ""
            returncode = 1

        return Completed()

    external = tmp_path / "external"
    external.mkdir()
    monkeypatch.setattr(
        "backend.infrastructure.office.fee_evaluation_export_subprocess_runner.subprocess.run",
        success_run,
    )
    runner = FeeEvaluationExportSubprocessRunner(output_root=tmp_path / "runs")

    runner.run(_command(tmp_path))

    assert external.exists()
    assert list((tmp_path / "runs").glob("run-*")) == []


def _command(tmp_path: Path) -> ExportConfirmedMatrixFeeEvaluationCommand:
    return ExportConfirmedMatrixFeeEvaluationCommand(
        project_id="P1",
        template_path=tmp_path / "template.xls",
        output_dir=tmp_path,
        fill_mode="matrix_basic",
    )
