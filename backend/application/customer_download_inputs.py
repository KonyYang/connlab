"""Issue short-lived, single-use input handles before starting a Word download job."""
from dataclasses import dataclass, field
from pathlib import Path
import shutil
from tempfile import mkdtemp
from threading import Lock
import time
from typing import BinaryIO
from uuid import uuid4


@dataclass
class _Input:
    source: BinaryIO
    job_parent: Path
    file_name: str
    digest: str
    choices: object
    scope: str
    expires: float
    operation: str | None = None
    lock: Lock = field(default_factory=Lock)


class CustomerDownloadInputs:
    def __init__(self, inspect_document, prepare_document, clock=time.monotonic):
        self._inspect = inspect_document
        self._prepare = prepare_document
        self._clock = clock
        self._lock = Lock()
        self._inputs = {}

    def _prune(self):
        expired = []
        with self._lock:
            for key, item in list(self._inputs.items()):
                if item.expires <= self._clock() and item.lock.acquire(blocking=False):
                    self._inputs.pop(key)
                    expired.append(item)
        for item in expired:
            try:
                item.source.close()
            finally:
                item.lock.release()

    def inspect(self, source, file_name, choices, scope, job_parent):
        self._prune()
        review = self._inspect(source)
        digest = review["source_sha256"]
        item = _Input(source, job_parent, file_name, digest, choices, scope, self._clock() + 3600)
        key = uuid4().hex
        saved = choices.read(scope, digest)
        with self._lock:
            self._inputs[key] = item
        return {**review, "decisions": saved, "input_id": key}

    def generate(self, key, decisions, template, jobs, validate_source=None):
        self._prune()
        with self._lock:
            item = self._inputs.get(key)
            if not item:
                raise LookupError("This report selection expired. Choose the internal report again.")
            # Claim before pruning can remove the folder. Refuse concurrent duplicates.
            if not item.lock.acquire(blocking=False):
                raise ValueError("This customer report is being prepared. Retry in a moment.")
        try:
            if item.operation:
                return jobs.read(item.operation)
            if validate_source:
                validate_source(item.scope, item.digest)
            root = Path(mkdtemp(prefix="cr-out-", dir=item.job_parent))
            try:
                prepared = root / "prepared.docx"
                self._prepare(item.source, prepared, decisions, expected_source_sha256=item.digest)
                item.choices.remember(item.scope, item.digest, decisions)
                job = jobs.start(root=root, source_path=prepared, template_path=template,
                                 output_path=root / "customer.docx", download_name=item.file_name,
                                 lineage_sha256=item.digest)
            except Exception:
                shutil.rmtree(root, ignore_errors=True)
                raise
            item.operation = job["operation_id"]
            item.source.close()
            return job
        finally:
            item.lock.release()

    def discard(self, key):
        with self._lock:
            item = self._inputs.get(key)
            if not item or not item.lock.acquire(blocking=False):
                return
            self._inputs.pop(key)
        try:
            item.source.close()
        finally:
            item.lock.release()
