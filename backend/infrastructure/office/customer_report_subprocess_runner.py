"""Timeout-controlled parent runner for standalone customer-report generation."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Callable
from uuid import uuid4

from backend.application.tools_service import ToolsError


DEFAULT_CUSTOMER_REPORT_TIMEOUT_SECONDS = 120.0
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
    ) -> None:
        self._output_root = Path(output_root)
        self._timeout_seconds = timeout_seconds

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
        command_json.write_text(
            json.dumps(
                {
                    "source_path": str(Path(source_path).resolve()),
                    "template_path": str(Path(template_path).resolve()),
                    "output_path": str(Path(output_path).resolve()),
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        if progress is not None:
            progress("opening_word")
        try:
            completed = subprocess.run(
                _child_command(command_json),
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                timeout=self._timeout_seconds,
                check=False,
                creationflags=_creation_flags(),
            )
        except subprocess.TimeoutExpired as exc:
            Path(output_path).unlink(missing_ok=True)
            raise ToolsError(
                "Customer report generation did not finish within "
                f"{self._timeout_seconds:g} seconds. The isolated Word task was stopped; "
                "the original report was not changed. Select the source again and retry."
            ) from exc
        finally:
            _cleanup_run_directory(root=output_root, run_dir=run_dir)

        payload = _parse_child_result(completed.stdout)
        if completed.returncode != 0 or payload.get("status") != "success":
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

