"""Process-local project report jobs; own only temporary download artifacts."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import logging
import json
import os
from pathlib import Path
import shutil
import threading
import time
from uuid import uuid4

from backend.application.customer_report_projection_service import CustomerReportGenerationResult

logger = logging.getLogger(__name__)


class ProjectCustomerReportJobExpired(ValueError):
    """The server restarted or the retained job has expired."""


@dataclass
class _Job:
    operation_id: str
    project_id: str
    root: Path
    started: float
    status: str = "queued"
    stage: str = "queued"
    finished: float | None = None
    message: str | None = None
    error_code: str | None = None
    result: CustomerReportGenerationResult | None = None
    leases: int = 0


class ProjectCustomerReportJobService:
    def __init__(self, *, root, generate, dispatch, clock=time.monotonic, retention_seconds=3600, shutdown=None):
        self._root = Path(root).resolve()
        self._generate = generate
        self._dispatch = dispatch
        self._clock = clock
        self._retention = retention_seconds
        self._jobs = {}
        self._lock = threading.RLock()
        self._shutdown = shutdown
        self._closed = False

    def start(self, project_id, expected_source, expected_customer):
        self.prune()
        with self._lock:
            if self._closed:
                raise ValueError("Customer report service is shutting down. Retry after restart.")
            active = next((j for j in self._jobs.values() if j.project_id == project_id and j.finished is None), None)
            if active:
                return self._view(active)
            identity = uuid4().hex
            root = self._root / identity
            root.mkdir(parents=True, exist_ok=False)
            (root / ".connlab-report-job.json").write_text(json.dumps({"owner": "connlab-project-customer-report", "operation_id": identity, "pid": os.getpid(), "created": time.time()}), encoding="utf-8")
            job = _Job(identity, project_id, root, self._clock())
            self._jobs[identity] = job
        try:
            self._dispatch(lambda: self._run(job, expected_source, expected_customer))
        except Exception as exc:
            self._fail(job, exc)
        with self._lock:
            return self._view(job)

    def latest(self, project_id):
        self.prune()
        with self._lock:
            jobs = [j for j in self._jobs.values() if j.project_id == project_id]
            return self._view(jobs[-1]) if jobs else None

    def close(self):
        with self._lock:
            if self._closed:
                return
            self._closed = True
        if self._shutdown:
            self._shutdown()
        with self._lock:
            for job in self._jobs.values():
                if job.finished is None:
                    job.status = "failed"
                    job.finished = self._clock()
                    job.error_code = "customer_report_job_expired"
                    job.message = "The backend stopped before this task completed. Generate again after restart."
                if not job.leases:
                    self._cleanup(job)

    def read(self, project_id, operation_id):
        self.prune()
        with self._lock:
            return self._view(self._require(project_id, operation_id))

    @contextmanager
    def download(self, project_id, operation_id):
        self.prune()
        with self._lock:
            job = self._require(project_id, operation_id)
            result = job.result
            if job.status != "completed" or result is None or result.mode != "managed_download":
                raise ValueError("A completed downloadable customer report is not available.")
            path = result.file_path.resolve()
            if job.root not in path.parents or not path.is_file():
                raise ProjectCustomerReportJobExpired("The download artifact is unavailable. Generate again.")
            job.leases += 1
        try:
            yield path
        finally:
            with self._lock:
                job.leases -= 1
                if self._closed and not job.leases:
                    self._cleanup(job)

    def prune(self):
        with self._lock:
            for identity, job in list(self._jobs.items()):
                if job.finished is not None and not job.leases and self._clock() - job.finished >= self._retention:
                    if self._cleanup(job):
                        del self._jobs[identity]
            self._prune_abandoned()

    def _run(self, job, source, customer):
        with self._lock:
            if job.finished is not None:
                return
            job.status = "running"
            job.stage = "validating"
        try:
            result = self._generate(job.project_id, source, customer, job.root, lambda stage: self._progress(job, stage))
            if result.mode == "managed_download" and job.root not in result.file_path.resolve().parents:
                raise ValueError("Generated download escaped its task-owned directory.")
            with self._lock:
                job.result = result
                job.status = "completed"
                job.stage = "completed"
                job.finished = self._clock()
        except Exception as exc:
            self._fail(job, exc)

    def _progress(self, job, stage):
        with self._lock:
            job.stage = stage

    def _fail(self, job, exc):
        logger.exception("Customer report job %s project %s failed", job.operation_id, job.project_id, exc_info=exc)
        with self._lock:
            job.error_code = getattr(exc, "code", None) or ("customer_report_publication_failed" if job.stage == "publishing" else "customer_report_generation_failed")
            job.message = str(exc) or "Customer report generation failed."
            job.status = "failed"
            job.finished = self._clock()
            self._cleanup(job)

    def _require(self, project_id, operation_id):
        job = self._jobs.get(operation_id)
        if job is None or job.project_id != project_id:
            raise ProjectCustomerReportJobExpired("The customer report task expired or the backend restarted. Start generation again.")
        return job

    def _cleanup(self, job):
        if job.root.resolve().parent != self._root or job.root.name != job.operation_id:
            raise ValueError("Refusing cleanup outside task-owned customer-report storage.")
        try:
            if job.root.exists():
                shutil.rmtree(job.root)
            return True
        except OSError:
            logger.exception("Will retry cleanup of customer report job %s", job.operation_id)
            return False

    def _prune_abandoned(self):
        if not self._root.exists():
            return
        for directory in self._root.iterdir():
            if directory.name in self._jobs or not directory.is_dir() or directory.is_symlink():
                continue
            try:
                marker = json.loads((directory / ".connlab-report-job.json").read_text(encoding="utf-8"))
                if (marker.get("owner") == "connlab-project-customer-report"
                        and marker.get("operation_id") == directory.name
                        and len(directory.name) == 32
                        and all(c in "0123456789abcdef" for c in directory.name)
                        and time.time() - marker["created"] >= self._retention
                        and not _process_alive(marker["pid"])
                        and directory.resolve().parent == self._root):
                    shutil.rmtree(directory)
            except (OSError, ValueError, TypeError, KeyError):
                logger.debug("Retaining unverified or unavailable report job directory %s", directory, exc_info=True)

    def _view(self, job):
        result = job.result
        return {"operation_id": job.operation_id, "project_id": job.project_id,
                "status": job.status, "stage": job.stage,
                "elapsed_seconds": max(0, (job.finished if job.finished is not None else self._clock()) - job.started),
                "message": job.message, "error_code": job.error_code,
                "can_regenerate": job.error_code == "customer_report_missing_after_preview",
                "result": None if result is None else {
                    "project_id": result.project_id, "mode": result.mode, "file_name": result.file_name,
                    "file_sha256": result.file_sha256, "source_report_sha256": result.source_report_sha256,
                    "changed": result.changed, "archive_path": str(result.archive_path) if result.archive_path else None}}


def _process_alive(pid):
    """Fail closed when process ownership cannot be established (including PID reuse)."""
    if not isinstance(pid, int) or pid <= 0:
        return True
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() != 87  # invalid PID; access denied remains live
        try:
            code = wintypes.DWORD()
            kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
            return not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value == 259
        finally:
            kernel.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
