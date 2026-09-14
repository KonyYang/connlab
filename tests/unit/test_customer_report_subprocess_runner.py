from __future__ import annotations

import subprocess
import json
from pathlib import Path

import pytest

from backend.application.tools_service import ToolsError
from backend.infrastructure.office.customer_report_subprocess_runner import (
    CustomerReportSubprocessRunner,
    _child_command,
)
from backend.infrastructure.office.customer_report_subprocess_child import _execute


def test_runner_times_out_a_stuck_word_process_and_releases_its_run_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def timeout_run(*args: object, **kwargs: object) -> object:
        raise subprocess.TimeoutExpired(
            cmd=["py", "-m", "customer-report-child"],
            timeout=0.01,
            output="",
            stderr="",
        )

    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_subprocess_runner.subprocess.run",
        timeout_run,
    )
    source = tmp_path / "internal.docx"
    template = tmp_path / "template.docx"
    source.write_bytes(b"source")
    template.write_bytes(b"template")
    progress: list[str] = []
    runner = CustomerReportSubprocessRunner(
        output_root=tmp_path / "runs",
        timeout_seconds=0.01,
    )

    with pytest.raises(ToolsError, match="did not finish within"):
        runner.generate_customer_report(
            source_path=source,
            template_path=template,
            output_path=tmp_path / "customer.docx",
            progress=progress.append,
        )

    assert progress == ["opening_word"]
    assert list((tmp_path / "runs").glob("run-*")) == []


def test_child_command_uses_the_packaged_customer_report_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command_json = tmp_path / "command.json"
    executable = r"D:\Release\ConnLab_Server.exe"
    import backend.infrastructure.office.customer_report_subprocess_runner as runner_module

    monkeypatch.setattr(runner_module.sys, "frozen", True, raising=False)
    monkeypatch.setattr(runner_module.sys, "executable", executable)

    assert _child_command(command_json) == [
        executable,
        "--connlab-customer-report-child",
        "--command-json",
        str(command_json.resolve()),
    ]


def test_child_generates_the_requested_output_from_its_command_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "internal.docx"
    template = tmp_path / "template.docx"
    output = tmp_path / "customer.docx"
    command_json = tmp_path / "command.json"
    source.write_bytes(b"source")
    template.write_bytes(b"template")
    command_json.write_text(
        json.dumps(
            {
                "source_path": str(source),
                "template_path": str(template),
                "output_path": str(output),
            }
        ),
        encoding="utf-8",
    )

    class _Gateway:
        def generate_customer_report(self, **paths: Path) -> Path:
            paths["output_path"].write_bytes(b"customer")
            return paths["output_path"]

    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_subprocess_child.CustomerReportDocumentGateway",
        _Gateway,
    )

    result = _execute(command_json)

    assert result == {"status": "success"}
    assert output.read_bytes() == b"customer"
