"""Timeout-controlled parent runner for standalone customer-report generation."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Callable
from uuid import uuid4

from backend.application.tools_service import ToolsError


DEFAULT_CUSTOMER_REPORT_TIMEOUT_SECONDS = 120.0
DEFAULT_CUSTOMER_REPORT_ABSOLUTE_TIMEOUT_SECONDS = 600.0
DEFAULT_CUSTOMER_REPORT_POLL_INTERVAL_SECONDS = 0.25
DEFAULT_CUSTOMER_REPORT_SUBPROCESS_ROOT = Path(
    "tmp/customer_report_subprocess"
)


class CustomerReportSubprocessRunner:
    """Keep potentially blocking Word COM work outside the API server process."""

    def __init__(
        self,
        *,
        output_root: Path = DEFAULT_CUSTOMER_REPORT_SUBPROCESS_ROOT,
        timeout_seconds: float = DEFAULT_CUSTOMER_REPORT_TIMEOUT_SECONDS,
        absolute_timeout_seconds: float = DEFAULT_CUSTOMER_REPORT_ABSOLUTE_TIMEOUT_SECONDS,
        poll_interval_seconds: float = DEFAULT_CUSTOMER_REPORT_POLL_INTERVAL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("Customer-report stall timeout must be positive.")
        if absolute_timeout_seconds < timeout_seconds:
            raise ValueError(
                "Customer-report absolute timeout must not be shorter than its stall timeout."
            )
        if poll_interval_seconds < 0:
            raise ValueError("Customer-report poll interval must not be negative.")
        self._output_root = Path(output_root)
        self._timeout_seconds = timeout_seconds
        self._absolute_timeout_seconds = absolute_timeout_seconds
        self._poll_interval_seconds = poll_interval_seconds
        self._clock = clock
        self._sleep = sleep

    def generate_customer_report(
        self,
        *,
        source_path: Path,
        template_path: Path,
        output_path: Path,
        progress: Callable[[str], None] | None = None,
    ) -> Path:
        output_root = self._output_root.resolve()
        run_dir = output_root / f"run-{uuid4().hex}"
        run_dir.mkdir(parents=True, exist_ok=False)
        command_json = run_dir / "command.json"
        progress_json = run_dir / "progress.json"
        command_json.write_text(
            json.dumps(
                {
                    "source_path": str(Path(source_path).resolve()),
                    "template_path": str(Path(template_path).resolve()),
                    "output_path": str(Path(output_path).resolve()),
                    "progress_path": str(progress_json.resolve()),
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        if progress is not None:
            progress("preparing_template")
        try:
            process = subprocess.Popen(
                _child_command(command_json),
                cwd=Path.cwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                creationflags=_creation_flags(),
            )
            started_at = self._clock()
            last_progress_at = started_at
            last_sequence = 0
            last_stage = "preparing_template"
            while True:
                returncode = process.poll()
                now = self._clock()
                event = _read_progress(progress_json, after_sequence=last_sequence)
                if event is not None:
                    last_sequence, stage = event
                    last_progress_at = now
                    if progress is not None and stage != last_stage:
                        progress(stage)
                    last_stage = stage
                if returncode is not None:
                    break
                if now - started_at >= self._absolute_timeout_seconds:
                    _stop_process(process)
                    Path(output_path).unlink(missing_ok=True)
                    raise ToolsError(
                        "Customer report generation exceeded the "
                        f"{self._absolute_timeout_seconds:g}-second safety limit. "
                        "The isolated Word task was stopped; the original report was not changed. "
                        "Select the source again and retry."
                    )
                if now - last_progress_at >= self._timeout_seconds:
                    _stop_process(process)
                    Path(output_path).unlink(missing_ok=True)
                    raise ToolsError(
                        "Customer report generation stayed at one processing stage for "
                        f"{self._timeout_seconds:g} seconds. The isolated Word task was stopped; "
                        "the original report was not changed. Select the source again and retry."
                    )
                self._sleep(self._poll_interval_seconds)
            stdout, _stderr = process.communicate()
        finally:
            _cleanup_run_directory(root=output_root, run_dir=run_dir)

        payload = _parse_child_result(stdout)
        if returncode != 0 or payload.get("status") != "success":
            message = str(payload.get("error_message") or "").strip()
            raise ToolsError(
                message
                or "The isolated Word task could not generate the customer report."
            )
        output = Path(output_path)
        if not output.is_file():
            raise ToolsError(
                "The isolated Word task finished without producing the customer report."
            )
        return output


def _read_progress(path: Path, *, after_sequence: int) -> tuple[int, str] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    if not isinstance(payload, dict):
        return None
    sequence = payload.get("sequence")
    stage = payload.get("stage")
    if (
        not isinstance(sequence, int)
        or sequence <= after_sequence
        or not isinstance(stage, str)
        or not stage
    ):
        return None
    return sequence, stage


def _stop_process(process) -> None:
    try:
        process.kill()
    finally:
        process.communicate()


def _child_command(command_json: Path) -> list[str]:
    if getattr(sys, "frozen", False):
        return [
            sys.executable,
            "--connlab-customer-report-child",
            "--command-json",
            str(command_json.resolve()),
        ]
    return [
        sys.executable,
        "-m",
        "backend.infrastructure.office.customer_report_subprocess_child",
        "--command-json",
        str(command_json.resolve()),
    ]


def _creation_flags() -> int:
    return int(getattr(subprocess, "CREATE_NO_WINDOW", 0))


def _parse_child_result(stdout: str) -> dict[str, object]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ToolsError(
            "The isolated Word task ended without a valid result."
        ) from exc
    if not isinstance(payload, dict):
        raise ToolsError("The isolated Word task returned an invalid result.")
    return payload


def _cleanup_run_directory(*, root: Path, run_dir: Path) -> None:
    root_resolved = root.resolve()
    run_resolved = run_dir.resolve()
    if run_resolved == root_resolved or root_resolved not in run_resolved.parents:
        raise ValueError(
            f"Refusing to clean path outside customer-report subprocess root: {run_dir}"
        )
    if run_resolved.exists():
        shutil.rmtree(run_resolved)

