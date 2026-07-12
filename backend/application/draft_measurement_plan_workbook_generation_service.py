"""Fingerprint-protected generation of review-only draft workbooks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.application.draft_measurement_plan_workbook_preview_service import (
    DraftMeasurementPlanWorkbookPreviewService,
)
from backend.infrastructure.files.draft_measurement_plan_workbook_artifact_store import (
    DraftMeasurementPlanWorkbookArtifactStore,
)


class DraftMeasurementPlanWorkbookGenerationError(ValueError):
    """Raised when generation cannot safely publish a draft artifact."""


@dataclass(frozen=True, slots=True)
class DraftMeasurementPlanWorkbookGenerationResult:
    project_id: str
    revision_id: str
    artifact_id: str
    file_name: str
    output_path: Path
    output_label: str
    cleanup_warning: str | None


class DraftMeasurementPlanWorkbookGenerationService:
    """Recompute preview before writing one contained draft workbook."""

    def __init__(self, *, preview_service: DraftMeasurementPlanWorkbookPreviewService, workbook_gateway, artifact_store: DraftMeasurementPlanWorkbookArtifactStore) -> None:
        self._preview_service = preview_service
        self._workbook_gateway = workbook_gateway
        self._artifact_store = artifact_store

    def generate(self, project_id: str, revision_id: str, preview_fingerprint: str) -> DraftMeasurementPlanWorkbookGenerationResult:
        projection = self._preview_service.preview(project_id, revision_id)
        if not projection.generate_allowed or not projection.preview_fingerprint:
            raise DraftMeasurementPlanWorkbookGenerationError("Draft workbook preview is blocked or empty.")
        if projection.preview_fingerprint != preview_fingerprint:
            raise DraftMeasurementPlanWorkbookGenerationError("Editable measurement plan changed. Preview again before generating.")
        artifact = self._artifact_store.prepare(project_id=project_id, output_label=projection.output_label or "DRAFT", matrix_revision=projection.matrix_revision or 0, plan_sequence=projection.revision_sequence or 0, preview_fingerprint=projection.preview_fingerprint)
        try:
            self._workbook_gateway.write(output_path=artifact.temporary_path, projection=projection)
            metadata = self._artifact_store.publish(
                artifact,
                metadata={
                    "project_id": project_id,
                    "revision_id": revision_id,
                    "plan_sequence": projection.revision_sequence,
                    "revision_state": projection.revision_state,
                    "revision_fingerprint": projection.revision_fingerprint,
                    "matrix_id": projection.matrix_id,
                    "matrix_revision": projection.matrix_revision,
                    "matrix_binding_fingerprint": projection.matrix_binding_fingerprint,
                    "output_class": "measurement_plan_draft",
                    "output_label": projection.output_label,
                    "layout_version": "LLCR_CR_RECORD_LAYOUT_V1",
                    "preview_fingerprint": projection.preview_fingerprint,
                    "status": projection.status,
                    "section_count": len(projection.sections),
                    "row_count": projection.row_count,
                    "review_diagnostics": [item.code for item in projection.diagnostics],
                },
            )
        except (OSError, ValueError) as exc:
            self._artifact_store.discard_incomplete(artifact)
            raise DraftMeasurementPlanWorkbookGenerationError(f"Unable to generate draft workbook: {exc}") from exc
        return DraftMeasurementPlanWorkbookGenerationResult(
            project_id,
            revision_id,
            metadata.artifact_id,
            metadata.file_name,
            metadata.output_path,
            projection.output_label or "DRAFT",
            metadata.cleanup_warning,
        )
