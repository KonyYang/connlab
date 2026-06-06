"""Parent subprocess runner for production Fee Evaluation workbook exports."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from uuid import uuid4

from backend.application.confirmed_matrix_fee_evaluation_export_service import (
    ExportConfirmedMatrixFeeEvaluationCommand,
)
from backend.application.confirmed_matrix_fee_evaluation_export_timeout_service import (
    FeeEvaluationExportProcessResult,
    command_to_payload,
)


DEFAULT_FEE_EXPORT_TIMEOUT_SECONDS = 90.0
DEFAULT_FEE_EXPORT_SUBPROCESS_ROOT = Path("tmp/fee_evaluation_export_subprocess")


class FeeEvaluationExportSubprocessRunner:
    """Run production Fee Evaluation exports in a timeout-controlled subprocess."""

    def __init__(
        self,
        *,
        output_root: Path = DEFAULT_FEE_EXPORT_SUBPROCESS_ROOT,
        timeout_seconds: float = DEFAULT_FEE_EXPORT_TIMEOUT_SECONDS,
    ) -> None:
        self._output_root = output_root
        self._timeout_seconds = timeout_seconds

    def run(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> FeeEvaluationExportProcessResult:
        """Run one export command through the child entry point."""
        output_root = self._output_root.resolve()
        run_dir = output_root / f"run-{uuid4().hex}"
        run_dir.mkdir(parents=True, exist_ok=False)
        command_json = run_dir / "command.json"
        command_json.write_text(
            json.dumps(command_to_payload(command), ensure_ascii=False),
            encoding="utf-8",
        )
        argv = _child_command(command_json)
        started = time.monotonic()
        try:
            completed = subprocess.run(
                argv,
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
            )
            elapsed = time.monotonic() - started
            return _parse_child_result(
                stdout=completed.stdout,
                stderr=completed.stderr,
                exit_code=completed.returncode,
                elapsed_seconds=elapsed,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed = time.monotonic() - started
            return FeeEvaluationExportProcessResult(
                status="timeout",
                timed_out=True,
                exit_code=None,
                elapsed_seconds=elapsed,
                stdout=_decode_process_text(exc.output),
                stderr=_decode_process_text(exc.stderr),
                manual_cleanup_warning=(
                    "Fee Evaluation export timed out. Excel cleanup is uncertain; "
                    "inspect Excel and the output file manually."
                ),
            )
        finally:
            _cleanup_run_directory(root=output_root, run_dir=run_dir)


def _child_command(command_json: Path) -> list[str]:
    """Return child process argv using an absolute command JSON path."""
    return [
        sys.executable,
        "-m",
        "backend.infrastructure.office.fee_evaluation_export_child",
        "--command-json",
        str(command_json.resolve()),
    ]


def _parse_child_result(
    *,
    stdout: str,
    stderr: str,
    exit_code: int,
    elapsed_seconds: float,
) -> FeeEvaluationExportProcessResult:
    """Parse final child stdout JSON into a process result."""
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return FeeEvaluationExportProcessResult(
            status="execution_failure",
            timed_out=False,
            exit_code=exit_code,
            elapsed_seconds=elapsed_seconds,
            stdout=stdout,
            stderr=stderr,
            error_message="Child process did not emit one valid JSON object to stdout.",
        )
    status = str(payload.get("status") or ("success" if exit_code == 0 else "failure"))
    return FeeEvaluationExportProcessResult(
        status=status,
        timed_out=False,
        exit_code=exit_code,
        elapsed_seconds=elapsed_seconds,
        stdout=stdout,
        stderr=stderr,
        payload=payload,
        error_message=payload.get("error_message"),
        manual_cleanup_warning=payload.get("manual_cleanup_warning"),
    )


def _cleanup_run_directory(*, root: Path, run_dir: Path) -> None:
    """Remove one runner-owned command directory while refusing external paths."""
    root_resolved = root.resolve()
    run_resolved = run_dir.resolve()
    if run_resolved == root_resolved or root_resolved not in run_resolved.parents:
        raise ValueError(f"Refusing to clean path outside subprocess root: {run_dir}")
    if run_resolved.exists():
        shutil.rmtree(run_resolved)


def _decode_process_text(value: str | bytes | None) -> str:
    """Decode timeout stdout/stderr values into text."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
