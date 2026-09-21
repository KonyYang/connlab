"""Child entry point for isolated standalone customer-report generation."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import threading
import time
import traceback
from typing import Any, Callable

from backend.infrastructure.office.customer_report_document_gateway import (
    CustomerReportDocumentGateway,
)


DEFAULT_CHILD_STALL_DIAGNOSTIC_SECONDS = 120.0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = _parse_args(argv)
    result = _execute(args.command_json)
    print(json.dumps(result, ensure_ascii=False), end="")
    return 0 if result.get("status") == "success" else 1


def _execute(command_json: Path) -> dict[str, Any]:
    try:
        payload = json.loads(command_json.read_text(encoding="utf-8"))
        source = Path(payload["source_path"])
        template = Path(payload["template_path"])
        output = Path(payload["output_path"])
        progress_path_value = payload.get("progress_path")
        diagnostic_path_value = payload.get("diagnostic_path")
        reporter = _ChildProgressReporter(
            progress_path=(
                Path(progress_path_value)
                if isinstance(progress_path_value, str) and progress_path_value
                else None
            ),
            diagnostic_path=(
                Path(diagnostic_path_value)
                if isinstance(diagnostic_path_value, str) and diagnostic_path_value
                else None
            ),
            stall_diagnostic_seconds=DEFAULT_CHILD_STALL_DIAGNOSTIC_SECONDS,
        )
        with reporter:
            CustomerReportDocumentGateway().generate_customer_report(
                source_path=source,
                template_path=template,
                output_path=output,
                progress=reporter.write if reporter.enabled else None,
            )
        return {"status": "success"}
    except Exception as exc:
        return {
            "status": "failure",
            "error_type": type(exc).__name__,
            "error_message": " ".join(str(exc).split()) or type(exc).__name__,
        }


class _ChildProgressReporter:
    """Publish progress and capture Python stacks without aborting slow Word work."""

    def __init__(
        self,
        *,
        progress_path: Path | None,
        diagnostic_path: Path | None,
        stall_diagnostic_seconds: float,
    ) -> None:
        self._progress_path = progress_path
        self._diagnostic_path = diagnostic_path
        self._stall_diagnostic_seconds = stall_diagnostic_seconds
        self._sequence = 0
        self._diagnostic_sequence = 0
        self._stage: str | None = None
        self._stage_started_at = time.monotonic()
        self._diagnostic_written_for_stage = False
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def enabled(self) -> bool:
        return self._progress_path is not None or self._diagnostic_path is not None

    def __enter__(self) -> _ChildProgressReporter:
        if self._diagnostic_path is not None:
            self._thread = threading.Thread(
                target=self._watch_for_stall,
                name="customer-report-stall-diagnostics",
                daemon=True,
            )
            self._thread.start()
        return self

    def __exit__(self, _exc_type, _exc, _traceback) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1)

    def write(self, stage: str) -> None:
        with self._lock:
            self._sequence += 1
            sequence = self._sequence
            self._stage = stage
            self._stage_started_at = time.monotonic()
            self._diagnostic_written_for_stage = False
        if self._progress_path is not None:
            _write_json_atomically(
                self._progress_path,
                {"sequence": sequence, "stage": stage},
            )

    def _watch_for_stall(self) -> None:
        poll_seconds = min(
            1.0,
            max(0.005, self._stall_diagnostic_seconds / 4),
        )
        while not self._stop.wait(poll_seconds):
            now = time.monotonic()
            with self._lock:
                if (
                    self._stage is None
                    or self._diagnostic_written_for_stage
                    or now - self._stage_started_at
                    < self._stall_diagnostic_seconds
                ):
                    continue
                self._diagnostic_sequence += 1
                sequence = self._diagnostic_sequence
                stage = self._stage
                elapsed_seconds = now - self._stage_started_at
                self._diagnostic_written_for_stage = True
            if self._diagnostic_path is not None:
                _write_json_atomically(
                    self._diagnostic_path,
                    {
                        "sequence": sequence,
                        "stage": stage,
                        "elapsed_seconds": round(elapsed_seconds, 2),
                        "pid": os.getpid(),
                        "python_stacks": _capture_python_stacks(),
                    },
                )


def _write_json_atomically(path: Path, payload: dict[str, object]) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _capture_python_stacks() -> str:
    names = {
        thread.ident: thread.name
        for thread in threading.enumerate()
        if thread.ident is not None
    }
    lines: list[str] = []
    for thread_id, frame in sys._current_frames().items():
        lines.append(f"Thread {names.get(thread_id, thread_id)} ({thread_id})\n")
        lines.extend(traceback.format_stack(frame))
    return "".join(lines)


def _progress_writer(path: Path) -> Callable[[str], None]:
    reporter = _ChildProgressReporter(
        progress_path=path,
        diagnostic_path=None,
        stall_diagnostic_seconds=DEFAULT_CHILD_STALL_DIAGNOSTIC_SECONDS,
    )

    def write(stage: str) -> None:
        reporter.write(stage)

    return write


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate one customer report in an isolated Word process."
    )
    parser.add_argument("--command-json", required=True, type=Path)
    return parser.parse_args(argv)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

