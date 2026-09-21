"""Backend-owned lifecycle for long-running standalone customer reports."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import shutil
from threading import RLock
import time
from typing import Callable, Protocol
from uuid import uuid4

from backend.shared.operation_diagnostics import safe_text


_LOGGER = logging.getLogger("connlab.customer_report")


class CustomerReportGeneratorPort(Protocol):
    def generate_customer_report(
        self,
        *,
        source_path: Path,
        template_path: Path,
        output_path: Path,
        progress: Callable[[str], None] | None = None,
    ) -> Path: ...


@dataclass(slots=True)
class _CustomerReportJob:
    operation_id: str
    root: Path
    source_path: Path
    template_path: Path
    output_path: Path
    status: str
    stage: str
    message: str | None
    started_at: float
    finished_at: float | None = None


class ToolsCustomerReportJobService:
    """Run Word automation outside the HTTP request and expose bounded progress."""

    def __init__(
        self,
        *,
        generator: CustomerReportGeneratorPort,
        dispatch: Callable[[Callable[[], None]], object],
        clock: Callable[[], float] = time.monotonic,
        retention_seconds: float = 3600,
    ) -> None:
        self._generator = generator
        self._dispatch = dispatch
        self._clock = clock
        self._retention_seconds = retention_seconds
        self._jobs: dict[str, _CustomerReportJob] = {}
        self._lock = RLock()

    def start(
        self,
        *,
        root: Path,
        source_path: Path,
        template_path: Path,
        output_path: Path,
    ) -> dict[str, object]:
        self._prune_expired()
        operation_root = Path(root).resolve()
        source = Path(source_path).resolve()
        output = Path(output_path).resolve()
        if source.parent != operation_root or output.parent != operation_root:
            raise ValueError("Customer-report job files must stay inside its operation folder.")
        if not operation_root.is_dir() or not source.is_file():
            raise ValueError("Customer-report job input is no longer available.")
        job = _CustomerReportJob(
            operation_id=uuid4().hex,
            root=operation_root,
            source_path=source,
            template_path=Path(template_path).resolve(),
            output_path=output,
            status="queued",
            stage="queued",
            message=None,
            started_at=self._clock(),
        )
        with self._lock:
            self._jobs[job.operation_id] = job
        try:
            self._dispatch(lambda: self._run(job.operation_id))
        except Exception:
            with self._lock:
                self._jobs.pop(job.operation_id, None)
            shutil.rmtree(operation_root, ignore_errors=True)
            raise
        return self._view(job)

    def read(self, operation_id: str) -> dict[str, object]:
        self._prune_expired()
        with self._lock:
            return self._view(self._require(operation_id))

    def output_path(self, operation_id: str) -> Path:
        self._prune_expired()
        with self._lock:
            job = self._require(operation_id)
            if job.status != "completed" or not job.output_path.is_file():
                raise ValueError("Customer report is not ready to download.")
            return job.output_path

    def complete_download(self, operation_id: str) -> None:
        with self._lock:
            job = self._jobs.pop(operation_id, None)
        if job is not None:
            shutil.rmtree(job.root, ignore_errors=True)

    def _run(self, operation_id: str) -> None:
        with self._lock:
            job = self._require(operation_id)
            job.status = "running"
            job.stage = "validating"
        _LOGGER.info(
            "customer_report_job_started operation_id=%s stage=validating",
            operation_id,
        )
        try:
            self._generator.generate_customer_report(
                source_path=job.source_path,
                template_path=job.template_path,
                output_path=job.output_path,
                progress=lambda value: self._record_stage(operation_id, value),
            )
        except Exception as exc:
            with self._lock:
                failed_stage = job.stage
                elapsed_seconds = self._clock() - job.started_at
                job.status = "failed"
                job.stage = "failed"
                job.message = " ".join(str(exc).split()) or exc.__class__.__name__
                job.finished_at = self._clock()
            _LOGGER.error(
                "customer_report_job_failed operation_id=%s stage=%s "
                "elapsed_seconds=%.2f error_type=%s message=%s",
                operation_id,
                failed_stage,
                elapsed_seconds,
                type(exc).__name__,
                safe_text(exc),
            )
            shutil.rmtree(job.root, ignore_errors=True)
            return
        with self._lock:
            job.status = "completed"
            job.stage = "completed"
            job.finished_at = self._clock()
            elapsed_seconds = job.finished_at - job.started_at
        _LOGGER.info(
            "customer_report_job_completed operation_id=%s elapsed_seconds=%.2f",
            operation_id,
            elapsed_seconds,
        )

    def _record_stage(self, operation_id: str, stage: str) -> None:
        with self._lock:
            job = self._require(operation_id)
            if job.status == "running":
                job.stage = stage
                elapsed_seconds = self._clock() - job.started_at
            else:
                return
        _LOGGER.info(
            "customer_report_job_progress operation_id=%s stage=%s "
            "elapsed_seconds=%.2f",
            operation_id,
            stage,
            elapsed_seconds,
        )

    def _require(self, operation_id: str) -> _CustomerReportJob:
        try:
            return self._jobs[operation_id]
        except KeyError:
            raise LookupError("Customer-report job was not found.") from None

    def _prune_expired(self) -> None:
        now = self._clock()
        expired: list[_CustomerReportJob] = []
        with self._lock:
            for operation_id, job in tuple(self._jobs.items()):
                if (
                    job.finished_at is not None
                    and now - job.finished_at >= self._retention_seconds
                ):
                    expired.append(self._jobs.pop(operation_id))
        for job in expired:
            shutil.rmtree(job.root, ignore_errors=True)

    def _view(self, job: _CustomerReportJob) -> dict[str, object]:
        end = job.finished_at if job.finished_at is not None else self._clock()
        return {
            "operation_id": job.operation_id,
            "status": job.status,
            "stage": job.stage,
            "elapsed_seconds": round(max(0.0, end - job.started_at), 2),
            "message": job.message,
        }
