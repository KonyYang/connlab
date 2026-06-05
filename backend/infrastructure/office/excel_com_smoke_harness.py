"""Timeout-controlled parent harness for manual Excel COM smoke runs."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any
from uuid import uuid4


DEFAULT_EXCEL_COM_SMOKE_TIMEOUT_SECONDS = 90.0
DEFAULT_EXCEL_COM_SMOKE_TEMPLATE = Path(
    "D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls"
)
DEFAULT_EXCEL_COM_SMOKE_OUTPUT_ROOT = Path("tmp/task_290a_excel_com_smoke")


@dataclass(frozen=True, slots=True)
class ExcelComSmokeCommand:
    """Input command for one isolated Excel COM smoke run."""

    template_path: Path = DEFAULT_EXCEL_COM_SMOKE_TEMPLATE
    output_root: Path = DEFAULT_EXCEL_COM_SMOKE_OUTPUT_ROOT
    output_name: str = "task290a_matrix_basic_fill_smoke.xls"
    timeout_seconds: float = DEFAULT_EXCEL_COM_SMOKE_TIMEOUT_SECONDS
    cleanup: bool = False


@dataclass(frozen=True, slots=True)
class ExcelComSmokeResult:
    """Structured result from a parent-managed Excel COM smoke run."""

    status: str
    timed_out: bool
    exit_code: int | None
    elapsed_seconds: float
    stdout: str
    stderr: str
    output_path: Path | None = None
    output_size: int | None = None
    steps: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    error_message: str | None = None
    manual_cleanup_warning: str | None = None


def run_excel_com_smoke(command: ExcelComSmokeCommand) -> ExcelComSmokeResult:
    """Run one Excel COM smoke child process with parent timeout control."""
    output_root = command.output_root.resolve()
    run_dir = output_root / f"run-{uuid4().hex}"
    run_dir.mkdir(parents=True, exist_ok=False)
    argv = _smoke_child_command(command, run_dir=run_dir)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            argv,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            timeout=command.timeout_seconds,
            check=False,
        )
        elapsed = time.monotonic() - started
        result = _parse_child_result(
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
            elapsed_seconds=elapsed,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - started
        result = ExcelComSmokeResult(
            status="timeout",
            timed_out=True,
            exit_code=None,
            elapsed_seconds=elapsed,
            stdout=_decode_process_text(exc.output),
            stderr=_decode_process_text(exc.stderr),
            manual_cleanup_warning=(
                "Smoke subprocess timed out. Excel cleanup is uncertain; "
                "check for a remaining Excel process manually."
            ),
        )
    if command.cleanup:
        _cleanup_run_directory(root=output_root, run_dir=run_dir)
    return result


def _smoke_child_command(command: ExcelComSmokeCommand, *, run_dir: Path) -> list[str]:
    """Return the child process command with absolute template/output paths."""
    return [
        sys.executable,
        "-m",
        "backend.infrastructure.office.excel_com_smoke_child",
        "--template-path",
        str(command.template_path.resolve()),
        "--output-dir",
        str(run_dir.resolve()),
        "--output-name",
        command.output_name,
    ]


def _parse_child_result(
    *,
    stdout: str,
    stderr: str,
    exit_code: int,
    elapsed_seconds: float,
) -> ExcelComSmokeResult:
    """Convert child stdout JSON into a structured parent result."""
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return ExcelComSmokeResult(
            status="execution_failure",
            timed_out=False,
            exit_code=exit_code,
            elapsed_seconds=elapsed_seconds,
            stdout=stdout,
            stderr=stderr,
            error_message="Child process did not emit one valid JSON object to stdout.",
        )
    output_path = payload.get("output_path")
    output_size = payload.get("output_size")
    status = str(payload.get("status") or ("success" if exit_code == 0 else "failure"))
    return ExcelComSmokeResult(
        status=status,
        timed_out=False,
        exit_code=exit_code,
        elapsed_seconds=elapsed_seconds,
        stdout=stdout,
        stderr=stderr,
        output_path=Path(output_path) if output_path else None,
        output_size=int(output_size) if output_size is not None else None,
        steps=tuple(payload.get("steps") or ()),
        warnings=tuple(str(warning) for warning in payload.get("warnings") or ()),
        error_message=payload.get("error_message"),
        manual_cleanup_warning=payload.get("manual_cleanup_warning"),
    )


def _cleanup_run_directory(*, root: Path, run_dir: Path) -> None:
    """Remove one harness-owned run directory while refusing external paths."""
    root_resolved = root.resolve()
    run_resolved = run_dir.resolve()
    if run_resolved == root_resolved or root_resolved not in run_resolved.parents:
        raise ValueError(f"Refusing to clean path outside harness root: {run_dir}")
    if run_resolved.exists():
        shutil.rmtree(run_resolved)


def _decode_process_text(value: str | bytes | None) -> str:
    """Decode subprocess timeout output into text for result reporting."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
