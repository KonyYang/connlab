"""Generate Word Test Record drafts from active Confirmed Matrix authority."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.application.confirmed_matrix_test_record_preview_service import (
    BuildConfirmedMatrixTestRecordPreviewCommand,
    ConfirmedMatrixTestRecordPreviewNotFoundError,
    ConfirmedMatrixTestRecordPreviewService,
)


class ConfirmedMatrixTestRecordDocumentGenerationError(ValueError):
    """Raised when active confirmed Matrix data cannot generate a document."""


class ConfirmedMatrixTestRecordDocumentGenerationNotFoundError(LookupError):
    """Raised when required active authority or project data is missing."""


class ProjectLookup(Protocol):
    """Project read operations needed for document metadata."""

    def get(self, project_id: str):
        """Return one project domain object by id."""


class ConfirmedMatrixTestRecordDocumentWriter(Protocol):
    """Infrastructure writer for Word Test Record drafts."""

    def generate_from_confirmed_matrix(
        self,
        *,
        output_path: Path,
        project_id: str,
        project_no: str,
        product_description: str,
        applicable_specification: str,
        confirmed_matrix_id: str,
        groups: tuple,
    ) -> Path:
        """Write one `.docx` draft and return its output path."""


@dataclass(frozen=True, slots=True)
class GenerateConfirmedMatrixTestRecordDocumentCommand:
    """Command for ConfirmedMatrix-backed Test Record Word generation."""

    project_id: str
    output_dir: Path
    overwrite: bool = True


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordDocumentGenerationResult:
    """Result for one generated Test Record Word draft."""

    project_id: str
    confirmed_matrix_id: str
    output_path: Path
    file_name: str


class ConfirmedMatrixTestRecordDocumentGenerationService:
    """Generate one Word Test Record draft from active ConfirmedMatrix preview data."""

    def __init__(
        self,
        *,
        preview_service: ConfirmedMatrixTestRecordPreviewService,
        project_store: ProjectLookup,
        writer: ConfirmedMatrixTestRecordDocumentWriter,
    ) -> None:
        self._preview_service = preview_service
        self._project_store = project_store
        self._writer = writer

    def generate(
        self,
        command: GenerateConfirmedMatrixTestRecordDocumentCommand,
    ) -> ConfirmedMatrixTestRecordDocumentGenerationResult:
        """Generate a downloadable Word draft from active ConfirmedMatrix authority."""
        output_dir = Path(command.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        preview = self._load_preview(command.project_id)
        if preview.preview_status != "ready" or not preview.groups:
            raise ConfirmedMatrixTestRecordDocumentGenerationError(
                "Active confirmed matrix has no previewable Test Record steps."
            )

        project = self._project_store.get(command.project_id)
        project_no = str(getattr(project, "project_no", "") or "")
        product_description = str(getattr(project, "product_name", "") or "")
        file_name = _safe_file_name(command.project_id)
        output_path = output_dir / file_name
        if output_path.exists() and not command.overwrite:
            raise ConfirmedMatrixTestRecordDocumentGenerationError(
                f"Output file already exists: {output_path}"
            )

        written = self._writer.generate_from_confirmed_matrix(
            output_path=output_path,
            project_id=command.project_id,
            project_no=project_no,
            product_description=product_description,
            applicable_specification="",
            confirmed_matrix_id=preview.confirmed_matrix_id,
            groups=preview.groups,
        )
        return ConfirmedMatrixTestRecordDocumentGenerationResult(
            project_id=command.project_id,
            confirmed_matrix_id=preview.confirmed_matrix_id,
            output_path=written,
            file_name=file_name,
        )

    def _load_preview(self, project_id: str):
        try:
            return self._preview_service.build_preview(
                BuildConfirmedMatrixTestRecordPreviewCommand(project_id=project_id)
            )
        except ConfirmedMatrixTestRecordPreviewNotFoundError as exc:
            raise ConfirmedMatrixTestRecordDocumentGenerationNotFoundError(str(exc)) from exc


def _safe_file_name(project_id: str) -> str:
    safe_project = project_id.replace("/", "_").replace("\\", "_").strip() or "project"
    return f"{safe_project}_test_record_draft.docx"
