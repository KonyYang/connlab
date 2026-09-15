from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.application.tools_service import ToolsError
from backend.infrastructure.office.customer_report_subprocess_runner import (
    CustomerReportSubprocessRunner,
    _child_command,
)
from backend.infrastructure.office.customer_report_subprocess_child import _execute


def test_unexpected_poll_failure_stops_child_and_cleans_temporary_files(tmp_path, monkeypatch):
    class Process:
        returncode = None
        killed = False
        def poll(self):
            raise RuntimeError("broken progress channel")
        def kill(self):
            self.killed = True
            self.returncode = -9
        def communicate(self):
            return "", ""
    process = Process()
    monkeypatch.setattr("backend.infrastructure.office.customer_report_subprocess_runner.subprocess.Popen", lambda *a, **k: process)
    with pytest.raises(RuntimeError, match="broken progress channel"):
        CustomerReportSubprocessRunner(output_root=tmp_path / "runs").generate_customer_report(
            source_path=tmp_path / "source.docx", template_path=tmp_path / "template.docx", output_path=tmp_path / "out.docx")
    assert process.killed
    assert list((tmp_path / "runs").iterdir()) == []


def test_runner_times_out_a_stuck_word_process_and_releases_its_run_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _StuckProcess:
        returncode = None

        def __init__(self) -> None:
            self.killed = False

        def poll(self):
            return None

        def kill(self) -> None:
            self.killed = True
            self.returncode = -9

        def communicate(self):
            return "", ""

    process = _StuckProcess()

    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_subprocess_runner.subprocess.Popen",
        lambda *_args, **_kwargs: process,
    )
    source = tmp_path / "internal.docx"
    template = tmp_path / "template.docx"
    source.write_bytes(b"source")
    template.write_bytes(b"template")
    progress: list[str] = []
    runner = CustomerReportSubprocessRunner(
        output_root=tmp_path / "runs",
        timeout_seconds=0.01,
        absolute_timeout_seconds=1,
        poll_interval_seconds=0,
    )

    with pytest.raises(ToolsError, match="stayed at one processing stage for"):
        runner.generate_customer_report(
            source_path=source,
            template_path=template,
            output_path=tmp_path / "customer.docx",
            progress=progress.append,
        )

    assert progress == ["preparing_template"]
    assert process.killed is True
    assert list((tmp_path / "runs").glob("run-*")) == []


def test_runner_forwards_child_progress_and_resets_the_stall_deadline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _CompletedProcess:
        returncode = None

        def __init__(self, command: list[str]) -> None:
            command_path = Path(command[-1])
            payload = json.loads(command_path.read_text(encoding="utf-8"))
            self.progress_path = Path(payload["progress_path"])
            self.output_path = Path(payload["output_path"])
            self.polls = 0

        def poll(self):
            self.polls += 1
            if self.polls == 1:
                self.progress_path.write_text(
                    json.dumps({"sequence": 1, "stage": "copying_content"}),
                    encoding="utf-8",
                )
                return None
            self.output_path.write_bytes(b"customer")
            self.returncode = 0
            return 0

        def communicate(self):
            return json.dumps({"status": "success"}), ""

    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_subprocess_runner.subprocess.Popen",
        lambda command, **_kwargs: _CompletedProcess(command),
    )
    source = tmp_path / "internal.docx"
    template = tmp_path / "template.docx"
    source.write_bytes(b"source")
    template.write_bytes(b"template")
    progress: list[str] = []

    result = CustomerReportSubprocessRunner(
        output_root=tmp_path / "runs",
        timeout_seconds=1,
        absolute_timeout_seconds=10,
        poll_interval_seconds=0,
    ).generate_customer_report(
        source_path=source,
        template_path=template,
        output_path=tmp_path / "customer.docx",
        progress=progress.append,
    )

    assert result.read_bytes() == b"customer"
    assert progress == ["preparing_template", "copying_content"]
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


def test_child_publishes_gateway_progress_for_the_parent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "internal.docx"
    template = tmp_path / "template.docx"
    output = tmp_path / "customer.docx"
    progress_json = tmp_path / "progress.json"
    command_json = tmp_path / "command.json"
    source.write_bytes(b"source")
    template.write_bytes(b"template")
    command_json.write_text(
        json.dumps(
            {
                "source_path": str(source),
                "template_path": str(template),
                "output_path": str(output),
                "progress_path": str(progress_json),
            }
        ),
        encoding="utf-8",
    )

    class _Gateway:
        def generate_customer_report(self, **paths) -> Path:
            paths["progress"]("copying_content")
            paths["output_path"].write_bytes(b"customer")
            return paths["output_path"]

    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_subprocess_child.CustomerReportDocumentGateway",
        _Gateway,
    )

    assert _execute(command_json) == {"status": "success"}
    assert json.loads(progress_json.read_text(encoding="utf-8")) == {
        "sequence": 1,
        "stage": "copying_content",
    }
