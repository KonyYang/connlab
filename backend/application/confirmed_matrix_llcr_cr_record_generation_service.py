"""Preview-fingerprint-protected generation for specialized LLCR/CR records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.application.confirmed_matrix_llcr_cr_record_preview_service import (
    LlcrCrRecordWorkbookPreviewService,
)
from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordProjection,
)
from backend.infrastructure.files.llcr_cr_specialized_record_artifact_store import (
    LlcrCrSpecializedRecordArtifactStore,
)


class LlcrCrRecordWorkbookGenerationError(ValueError):
    """Raised when preview state cannot safely create a specialized workbook."""


class LlcrCrRecordWorkbookWriter(Protocol):
    """Workbook write capability held by the Office infrastructure boundary."""

    def write(self, *, output_path: Path, projection: LlcrCrRecordProjection) -> Path:
        """Write one macro-free specialized workbook from a ready projection."""


@dataclass(frozen=True, slots=True)
class GenerateLlcrCrRecordWorkbookCommand:
    """One explicit request to generate a previously previewed workbook."""

    project_id: str
    preview_fingerprint: str
    record_type: str = "llcr"


@dataclass(frozen=True, slots=True)
class LlcrCrRecordWorkbookGenerationResult:
    """Safe generated artifact metadata for route/client download handling."""

    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    artifact_id: str
    file_name: str
    output_path: Path
    record_type: str = "llcr"


class LlcrCrRecordWorkbookGenerationService:
    """Regenerate a confirmed projection and write only after fingerprint match."""

    def __init__(
        self,
        *,
        preview_service: LlcrCrRecordWorkbookPreviewService,
        workbook_gateway: LlcrCrRecordWorkbookWriter,
        artifact_store: LlcrCrSpecializedRecordArtifactStore,
    ) -> None:
        self._preview_service = preview_service
        self._workbook_gateway = workbook_gateway
        self._artifact_store = artifact_store

    def generate(
        self,
        command: GenerateLlcrCrRecordWorkbookCommand,
    ) -> LlcrCrRecordWorkbookGenerationResult:
        """Write one workbook only when the requested preview is still current."""
        projection = self._preview_service.preview(command.project_id, command.record_type)
        if projection.status not in {"ready", "complete", "partial_compatible"} or not projection.preview_fingerprint:
            raise LlcrCrRecordWorkbookGenerationError(
                "LLCR/CR workbook preview requires review before generation."
            )
        if projection.preview_fingerprint != command.preview_fingerprint:
            raise LlcrCrRecordWorkbookGenerationError(
                "Confirmed Matrix contact plan changed. Preview again before generating."
            )
        artifact = self._artifact_store.prepare(
            project_id=projection.project_id,
            confirmed_revision=projection.confirmed_revision,
            record_type=command.record_type,
        )
        try:
            written = self._workbook_gateway.write(
                output_path=artifact.output_path,
                projection=projection,
            )
        except (OSError, ValueError) as exc:
            raise LlcrCrRecordWorkbookGenerationError(
                f"Unable to generate LLCR/CR workbook: {exc}"
            ) from exc
        return LlcrCrRecordWorkbookGenerationResult(
            project_id=projection.project_id,
            confirmed_matrix_id=projection.confirmed_matrix_id,
            confirmed_revision=projection.confirmed_revision,
            artifact_id=artifact.artifact_id,
            file_name=artifact.file_name,
            output_path=written,
            record_type=command.record_type,
        )
