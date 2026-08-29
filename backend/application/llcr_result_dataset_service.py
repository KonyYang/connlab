"""Inspect and confirm immutable LLCR ResultDataset revisions."""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import logging
from pathlib import Path
from threading import RLock
from typing import Callable, Protocol
from uuid import uuid4

from backend.domain.result_dataset_models import (
    LlcrConfirmationDecision,
    LlcrDatasetPayload,
    LlcrImportPreview,
    ResultDatasetRevision,
    ResultDatasetSourceIdentity,
)


class LlcrImportConflictError(ValueError):
    """Raised when preview authority changed before confirmation."""


class LlcrProjectionService(Protocol):
    def preview(self, project_id: str, record_type: str = "llcr"): ...


class LlcrWorkbookInspector(Protocol):
    def inspect(self, *, source_path: Path, projection): ...


class LlcrImportSourceStore(Protocol):
    def stage(self, *, preview_id: str, file_name: str, content: bytes) -> Path: ...
    def remove(self, preview_id: str) -> None: ...


class ResultDatasetStore(Protocol):
    def next_dataset_revision(self, project_id: str, dataset_type: str) -> int: ...
    def create_dataset(self, dataset: ResultDatasetRevision) -> ResultDatasetRevision: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class InspectLlcrImportCommand:
    project_id: str
    file_name: str
    content: bytes
    imported_by: str


@dataclass(frozen=True, slots=True)
class ConfirmLlcrImportCommand:
    project_id: str
    preview_id: str
    confirmed_by: str
    decisions: tuple[LlcrConfirmationDecision, ...]


@dataclass(frozen=True, slots=True)
class PendingLlcrImport:
    preview: LlcrImportPreview
    source_path: str
    imported_at: str
    imported_by: str
    authority_fingerprint: str | None


class LlcrImportPreviewRegistry:
    """Process-local registry for non-authoritative import previews."""

    def __init__(self) -> None:
        self._items: dict[str, PendingLlcrImport] = {}
        self._lock = RLock()

    def put(self, pending: PendingLlcrImport) -> None:
        with self._lock:
            self._items[pending.preview.preview_id] = pending

    def get(self, preview_id: str) -> PendingLlcrImport:
        with self._lock:
            pending = self._items.get(preview_id)
        if pending is None:
            raise LlcrImportConflictError("LLCR import preview expired or was not found.")
        return pending

    def remove(self, preview_id: str) -> None:
        with self._lock:
            self._items.pop(preview_id, None)


class LlcrResultDatasetService:
    """Deep module exposing the inspect -> confirm ResultDataset seam."""

    def __init__(
        self,
        *,
        preview_service: LlcrProjectionService,
        workbook_gateway: LlcrWorkbookInspector,
        source_store: LlcrImportSourceStore,
        preview_registry: LlcrImportPreviewRegistry,
        repository: ResultDatasetStore,
        clock: Callable[[], str],
        id_factory: Callable[[], str] = lambda: uuid4().hex,
    ) -> None:
        self._projections = preview_service
        self._workbooks = workbook_gateway
        self._sources = source_store
        self._previews = preview_registry
        self._repository = repository
        self._clock = clock
        self._ids = id_factory

    def inspect(self, command: InspectLlcrImportCommand) -> LlcrImportPreview:
        if not command.file_name.lower().endswith(".xlsx"):
            raise ValueError("Select an .xlsx LLCR workbook.")
        projection = self._projections.preview(command.project_id, "llcr")
        preview_id = f"llcr-preview-{self._ids()}"
        source_path = self._sources.stage(
            preview_id=preview_id,
            file_name=command.file_name,
            content=command.content,
        )
        try:
            inspection = self._workbooks.inspect(
                source_path=source_path,
                projection=projection,
            )
            source = ResultDatasetSourceIdentity(
                file_name=Path(command.file_name).name,
                sha256=sha256(command.content).hexdigest(),
                size_bytes=len(command.content),
            )
            preview = LlcrImportPreview(
                preview_id=preview_id,
                project_id=command.project_id,
                confirmed_matrix_id=projection.confirmed_matrix_id,
                confirmed_matrix_revision=projection.confirmed_revision,
                source=source,
                parser_profile_version=inspection.parser_profile_version,
                detected_sheets=inspection.detected_sheets,
                entries=inspection.entries,
                diagnostics=inspection.diagnostics,
            )
            self._previews.put(
                PendingLlcrImport(
                    preview=preview,
                    source_path=str(source_path),
                    imported_at=self._clock(),
                    imported_by=command.imported_by.strip() or "Lab User",
                    authority_fingerprint=getattr(
                        projection,
                        "preview_fingerprint",
                        None,
                    ),
                )
            )
            return preview
        except Exception:
            self._sources.remove(preview_id)
            raise

    def confirm(self, command: ConfirmLlcrImportCommand) -> ResultDatasetRevision:
        pending = self._previews.get(command.preview_id)
        preview = pending.preview
        if preview.project_id != command.project_id:
            raise LlcrImportConflictError("LLCR preview belongs to another project.")
        if not preview.can_confirm:
            raise LlcrImportConflictError("Resolve LLCR preview blockers before confirmation.")
        content = Path(pending.source_path).read_bytes()
        if sha256(content).hexdigest() != preview.source.sha256:
            raise LlcrImportConflictError("The LLCR workbook changed after preview; inspect it again.")
        current = self._projections.preview(command.project_id, "llcr")
        if (
            current.confirmed_matrix_id != preview.confirmed_matrix_id
            or current.confirmed_revision != preview.confirmed_matrix_revision
        ):
            raise LlcrImportConflictError("The Active Confirmed Matrix changed after preview.")
        if (
            getattr(current, "preview_fingerprint", None)
            != pending.authority_fingerprint
        ):
            raise LlcrImportConflictError(
                "The LLCR mapping authority changed after preview; inspect it again."
            )

        decision_by_id = {decision.result_id: decision for decision in command.decisions}
        expected_ids = {entry.result_id for entry in preview.entries}
        if len(decision_by_id) != len(command.decisions) or set(decision_by_id) != expected_ids:
            raise ValueError("Confirm every LLCR result exactly once.")
        confirmed_entries = []
        for entry in preview.entries:
            decision = decision_by_id[entry.result_id]
            confirmed_entries.append(
                replace(
                    entry,
                    confirmed_outcome=decision.outcome,
                    override_reason=(decision.override_reason or "").strip() or None,
                )
            )
        now = self._clock()
        dataset = ResultDatasetRevision(
            dataset_id=f"llcr-dataset-{self._ids()}",
            dataset_type="llcr",
            revision=self._repository.next_dataset_revision(command.project_id, "llcr"),
            project_id=command.project_id,
            confirmed_matrix_id=preview.confirmed_matrix_id,
            confirmed_matrix_revision=preview.confirmed_matrix_revision,
            source=preview.source,
            imported_at=pending.imported_at,
            imported_by=pending.imported_by,
            confirmed_at=now,
            confirmed_by=command.confirmed_by.strip() or "Lab User",
            parser_profile_version=preview.parser_profile_version,
            validation_status="confirmed",
            payload=LlcrDatasetPayload(tuple(confirmed_entries)),
        )
        try:
            created = self._repository.create_dataset(dataset)
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise
        self._previews.remove(command.preview_id)
        try:
            self._sources.remove(command.preview_id)
        except OSError:
            logger.warning(
                "Unable to remove staged LLCR workbook after dataset confirmation: %s",
                command.preview_id,
                exc_info=True,
            )
        return created

    def cancel(self, *, project_id: str, preview_id: str) -> None:
        """Discard one non-authoritative preview and its staged workbook."""
        pending = self._previews.get(preview_id)
        if pending.preview.project_id != project_id:
            raise LlcrImportConflictError("LLCR preview belongs to another project.")
        self._sources.remove(preview_id)
        self._previews.remove(preview_id)
