"""Read-only preview service for specialized LLCR/CR record workbooks."""

from __future__ import annotations

from typing import Protocol

from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordProjection,
    build_llcr_cr_record_projection,
)
from backend.application.effective_contact_measurement_llcr_cr_record_projection import (
    build_effective_llcr_cr_record_projection,
)
from backend.domain import ConfirmedMatrixSnapshot


class LlcrCrRecordWorkbookPreviewNotFoundError(LookupError):
    """Raised when a project has no active confirmed Matrix authority."""


class ConfirmedMatrixAuthorityStore(Protocol):
    """Confirmed authority read capability required by specialized record preview."""

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return the active confirmed Matrix snapshot for one project."""


class LlcrCrRecordWorkbookPreviewService:
    """Build no-write specialized record preview from confirmed contact authority."""

    def __init__(self, *, confirmed_store: ConfirmedMatrixAuthorityStore, consumer_adapter=None) -> None:
        self._confirmed_store = confirmed_store
        self._consumer_adapter = consumer_adapter

    def preview(self, project_id: str) -> LlcrCrRecordProjection:
        """Return a deterministic no-write projection for one project."""
        snapshot = self._confirmed_store.get_active_by_project(project_id)
        if snapshot is None:
            raise LlcrCrRecordWorkbookPreviewNotFoundError(
                "Active confirmed Matrix not found."
            )
        if self._consumer_adapter is None:
            return build_llcr_cr_record_projection(snapshot)
        effective = self._consumer_adapter.get_effective(project_id)
        if effective is None:
            return build_llcr_cr_record_projection(snapshot)
        return build_effective_llcr_cr_record_projection(snapshot, effective)
