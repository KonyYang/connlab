"""Read-only preview service for specialized LLCR/CR record workbooks."""

from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from typing import Protocol

from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordProjection,
    build_point_profile_llcr_cr_record_projection,
    build_llcr_cr_record_projection,
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

    def preview(self, project_id: str, record_type: str = "llcr") -> LlcrCrRecordProjection:
        """Return a deterministic no-write projection for one project."""
        snapshot = self._confirmed_store.get_active_by_project(project_id)
        if snapshot is None:
            raise LlcrCrRecordWorkbookPreviewNotFoundError(
                "Active confirmed Matrix not found."
            )
        if self._consumer_adapter is None:
            return _legacy_type_projection(build_llcr_cr_record_projection(snapshot), record_type)
        effective = self._consumer_adapter.get_effective(project_id)
        if effective is None:
            return _legacy_type_projection(build_llcr_cr_record_projection(snapshot), record_type)
        return build_point_profile_llcr_cr_record_projection(snapshot, effective, record_type)


def _legacy_type_projection(
    projection: LlcrCrRecordProjection, record_type: str,
) -> LlcrCrRecordProjection:
    if record_type not in {"llcr", "cr"}:
        raise ValueError("Record type must be llcr or cr.")
    if projection.status in {"blocked", "review_required"}:
        return replace(
            projection,
            record_type=record_type,
            delta_r_enabled=record_type == "llcr",
        )
    expected = "llcr" if record_type == "llcr" else "cr_specified_current"
    sections = tuple(
        replace(section, record_type=record_type)
        for section in projection.sections
        if section.record_type == expected
    )
    status = projection.status if sections else "empty"
    fingerprint = (
        sha256(f"{projection.preview_fingerprint}:{record_type}".encode("utf-8")).hexdigest()
        if status == "ready" and projection.preview_fingerprint
        else None
    )
    return replace(
        projection,
        status=status,
        sections=sections if status == "ready" else (),
        preview_fingerprint=fingerprint,
        record_type=record_type,
        delta_r_enabled=record_type == "llcr",
    )
