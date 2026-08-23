"""Generate LLCR/CR preview workbooks from the current Matrix Editor state."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol

from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordProjection,
)
from backend.application.matrix_editor_llcr_cr_record_projection import (
    MatrixEditorLlcrCrRecordGroupInput,
    MatrixEditorLlcrCrRecordRowInput,
    build_matrix_editor_llcr_cr_record_projection,
)


class MatrixEditorLlcrCrRecordGenerationError(ValueError):
    """Raised when the current Matrix Editor state cannot generate a workbook."""


class MatrixEditorPointProfileReader(Protocol):
    def get_effective(self, project_id: str) -> object:
        """Return the effective Test points profile for one project."""


class MatrixEditorLtrRecordLookup(Protocol):
    def list_by_project(self, project_id: str) -> list[object]:
        """Return the locally registered LTR history for one project."""


class MatrixEditorLlcrCrWorkbookWriter(Protocol):
    def write(self, *, output_path: Path, projection: LlcrCrRecordProjection) -> Path:
        """Write one draft projection to an XLSX workbook."""


class MatrixEditorLlcrCrDraftArtifact(Protocol):
    file_name: str
    output_path: Path


class MatrixEditorLlcrCrDraftArtifactStore(Protocol):
    def prepare_draft(
        self,
        *,
        project_id: str,
        record_type: str,
    ) -> MatrixEditorLlcrCrDraftArtifact:
        """Reserve one contained path for an unconfirmed draft workbook."""


@dataclass(frozen=True, slots=True)
class GenerateMatrixEditorLlcrCrRecordCommand:
    project_id: str
    record_type: str
    groups: tuple[MatrixEditorLlcrCrRecordGroupInput, ...]
    rows: tuple[MatrixEditorLlcrCrRecordRowInput, ...]


@dataclass(frozen=True, slots=True)
class MatrixEditorLlcrCrRecordGenerationResult:
    project_id: str
    record_type: str
    file_name: str
    output_path: Path


class MatrixEditorLlcrCrRecordGenerationService:
    """Create one unconfirmed workbook directly from the supplied live draft."""

    def __init__(
        self,
        *,
        point_profile_adapter: MatrixEditorPointProfileReader,
        workbook_gateway: MatrixEditorLlcrCrWorkbookWriter,
        artifact_store: MatrixEditorLlcrCrDraftArtifactStore,
        ltr_store: MatrixEditorLtrRecordLookup | None = None,
    ) -> None:
        self._point_profile_adapter = point_profile_adapter
        self._workbook_gateway = workbook_gateway
        self._artifact_store = artifact_store
        self._ltr_store = ltr_store

    def generate(
        self,
        command: GenerateMatrixEditorLlcrCrRecordCommand,
    ) -> MatrixEditorLlcrCrRecordGenerationResult:
        profile = self._point_profile_adapter.get_effective(command.project_id)
        projection = build_matrix_editor_llcr_cr_record_projection(
            project_id=command.project_id,
            record_type=command.record_type,
            groups=command.groups,
            rows=command.rows,
            point_profile=profile,
        )
        projection = replace(
            projection,
            ltr_number=self._latest_registered_ltr_number(command.project_id),
        )
        if projection.status != "ready" or not projection.sections:
            messages = " ".join(item.message for item in projection.diagnostics).strip()
            raise MatrixEditorLlcrCrRecordGenerationError(
                messages or f"Current Matrix draft does not require {command.record_type.upper()}."
            )
        try:
            artifact = self._artifact_store.prepare_draft(
                project_id=command.project_id,
                record_type=command.record_type,
            )
            output_path = self._workbook_gateway.write(
                output_path=artifact.output_path,
                projection=projection,
            )
        except (OSError, ValueError) as exc:
            raise MatrixEditorLlcrCrRecordGenerationError(
                f"Unable to generate the current Matrix draft workbook: {exc}"
            ) from exc
        return MatrixEditorLlcrCrRecordGenerationResult(
            project_id=command.project_id,
            record_type=command.record_type,
            file_name=artifact.file_name,
            output_path=output_path,
        )

    def _latest_registered_ltr_number(self, project_id: str) -> str | None:
        if self._ltr_store is None:
            return None
        registered = []
        for record in self._ltr_store.list_by_project(project_id):
            status = getattr(record, "status", None)
            if getattr(status, "value", status) == "registered":
                registered.append(record)
        if not registered:
            return None
        latest = max(
            registered,
            key=lambda record: (
                str(getattr(record, "registered_on", "") or ""),
                str(getattr(record, "ltr_number", "") or ""),
            ),
        )
        return str(getattr(latest, "ltr_number", "") or "").strip() or None
