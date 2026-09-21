from __future__ import annotations

import json
import logging
from pathlib import Path
import time

import pytest

from backend.application.tools_service import ToolsError
from backend.infrastructure.office.customer_report_subprocess_runner import (
    CustomerReportSubprocessRunner,
    _child_command,
)
from backend.infrastructure.office.customer_report_subprocess_child import _execute


def _wait_for_file(path: Path, *, timeout_seconds: float) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if path.is_file():
            return True
        time.sleep(0.005)
    return path.is_file()


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
    (tmp_path / "source.docx").write_bytes(b"source")
    (tmp_path / "template.docx").write_bytes(b"template")
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


def test_runner_does_not_abort_only_because_one_stage_exceeds_120_seconds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _SlowButSuccessfulProcess:
        returncode = None

        def __init__(self, command: list[str]) -> None:
            payload = json.loads(Path(command[-1]).read_text(encoding="utf-8"))
            self.output_path = Path(payload["output_path"])
            self.polls = 0

        def poll(self):
            self.polls += 1
            if self.polls == 1:
                return None
            self.output_path.write_bytes(b"customer")
            self.returncode = 0
            return 0

        def communicate(self):
            return json.dumps({"status": "success"}), ""

        def kill(self) -> None:
            self.returncode = -9

    moments = iter((0.0, 121.0, 122.0))
    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_subprocess_runner.subprocess.Popen",
        lambda command, **_kwargs: _SlowButSuccessfulProcess(command),
    )
    source = tmp_path / "internal.docx"
    template = tmp_path / "template.docx"
    source.write_bytes(b"source")
    template.write_bytes(b"template")

    output = CustomerReportSubprocessRunner(
        output_root=tmp_path / "runs",
        absolute_timeout_seconds=600,
        poll_interval_seconds=0,
        clock=lambda: next(moments),
    ).generate_customer_report(
        source_path=source,
        template_path=template,
        output_path=tmp_path / "customer.docx",
    )

    assert output.read_bytes() == b"customer"


def test_child_records_the_python_stacks_when_a_stage_stops_advancing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "internal.docx"
    template = tmp_path / "template.docx"
    output = tmp_path / "customer.docx"
    progress_json = tmp_path / "progress.json"
    diagnostic_json = tmp_path / "diagnostic.json"
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
                "diagnostic_path": str(diagnostic_json),
            }
        ),
        encoding="utf-8",
    )

    class _BlockedGateway:
        def generate_customer_report(self, **paths) -> Path:
            paths["progress"]("opening_word")
            assert _wait_for_file(diagnostic_json, timeout_seconds=1)
            paths["output_path"].write_bytes(b"customer")
            return paths["output_path"]

    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_subprocess_child.CustomerReportDocumentGateway",
        _BlockedGateway,
    )
    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_subprocess_child.DEFAULT_CHILD_STALL_DIAGNOSTIC_SECONDS",
        0.01,
    )

    assert _execute(command_json) == {"status": "success"}
    diagnostic = json.loads(diagnostic_json.read_text(encoding="utf-8"))
    assert diagnostic["stage"] == "opening_word"
    assert diagnostic["elapsed_seconds"] >= 0.01
    assert "_wait_for_file" in diagnostic["python_stacks"]


def test_runner_logs_the_stall_snapshot_without_local_paths_or_secrets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    class _DiagnosedProcess:
        returncode = None

        def __init__(self, command: list[str]) -> None:
            payload = json.loads(Path(command[-1]).read_text(encoding="utf-8"))
            self.diagnostic_path = Path(payload["diagnostic_path"])
            self.output_path = Path(payload["output_path"])
            self.polls = 0

        def poll(self):
            self.polls += 1
            if self.polls == 1:
                self.diagnostic_path.write_text(
                    json.dumps(
                        {
                            "sequence": 1,
                            "stage": "opening_word",
                            "elapsed_seconds": 120.0,
                            "python_stacks": (
                                'File "C:\\Sensitive\\blocked.py", line 1\n'
                                "password=secret"
                            ),
                        }
                    ),
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
        lambda command, **_kwargs: _DiagnosedProcess(command),
    )
    source = tmp_path / "internal.docx"
    template = tmp_path / "template.docx"
    source.write_bytes(b"source")
    template.write_bytes(b"template")
    moments = iter((0.0, 121.0, 122.0))
    caplog.set_level(logging.INFO, logger="connlab.customer_report")

    CustomerReportSubprocessRunner(
        output_root=tmp_path / "runs",
        absolute_timeout_seconds=600,
        poll_interval_seconds=0,
        clock=lambda: next(moments),
    ).generate_customer_report(
        source_path=source,
        template_path=template,
        output_path=tmp_path / "customer.docx",
    )

    assert "customer_report_child_stalled" in caplog.text
    assert "stage=opening_word" in caplog.text
    assert "<LOCAL_PATH>" in caplog.text
    assert "password=<REDACTED>" in caplog.text
    assert "Sensitive" not in caplog.text
    assert "password=secret" not in caplog.text


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


def test_runner_stages_word_inputs_and_output_away_from_the_project_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Path] = {}
    staged_contents: dict[str, bytes] = {}

    class _CompletedProcess:
        returncode = None

        def __init__(self, command: list[str]) -> None:
            payload = json.loads(Path(command[-1]).read_text(encoding="utf-8"))
            captured.update({key: Path(payload[key]) for key in ("source_path", "template_path", "output_path")})
            staged_contents["source"] = captured["source_path"].read_bytes()
            staged_contents["template"] = captured["template_path"].read_bytes()
            self.output_path = captured["output_path"]

        def poll(self):
            self.output_path.write_bytes(b"customer")
            self.returncode = 0
            return 0

        def communicate(self):
            return json.dumps({"status": "success"}), ""

    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_subprocess_runner.subprocess.Popen",
        lambda command, **_kwargs: _CompletedProcess(command),
    )
    project_folder = tmp_path / "DL-2026-09-002 PwrBlade Ultra Pro Rec.R-A TYPE WITH 2HP+20S Qualification test"
    project_folder.mkdir()
    source = project_folder / "DL-2026-09-002 PwrBlade Ultra Pro Rec.R-A TYPE WITH 2HP+20S Qualification test Report_Rev_A.docx"
    output = project_folder / "DL-2026-09-002-CR PwrBlade Ultra Pro Rec.R-A TYPE WITH 2HP+20S Qualification test Report_Rev_A.docx"
    template = tmp_path / "E-4515_F Customer Report.docx"
    source.write_bytes(b"source")
    template.write_bytes(b"template")

    result = CustomerReportSubprocessRunner(
        output_root=tmp_path / "runs",
        timeout_seconds=1,
        absolute_timeout_seconds=10,
        poll_interval_seconds=0,
    ).generate_customer_report(
        source_path=source,
        template_path=template,
        output_path=output,
    )

    assert result == output
    assert output.read_bytes() == b"customer"
    assert captured["source_path"] != source.resolve()
    assert captured["template_path"] != template.resolve()
    assert captured["output_path"] != output.resolve()
    assert staged_contents == {"source": b"source", "template": b"template"}
    assert list((tmp_path / "runs").glob("run-*")) == []


def test_runner_rejects_an_existing_output_without_deleting_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "internal.docx"
    template = tmp_path / "template.docx"
    output = tmp_path / "customer.docx"
    source.write_bytes(b"source")
    template.write_bytes(b"template")
    output.write_bytes(b"existing customer report")
    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_subprocess_runner.subprocess.Popen",
        lambda *_args, **_kwargs: pytest.fail("Word child must not start for an existing output"),
    )

    with pytest.raises(FileExistsError, match="already exists"):
        CustomerReportSubprocessRunner(output_root=tmp_path / "runs").generate_customer_report(
            source_path=source,
            template_path=template,
            output_path=output,
        )

    assert output.read_bytes() == b"existing customer report"
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
