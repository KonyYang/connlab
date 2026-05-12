"""Application service for test record and fee document generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.application.test_record_fee_dataset_preview_service import (
    TestRecordFeeDatasetPreview,
    TestRecordFeeDatasetPreviewCommand,
    TestRecordFeeDatasetPreviewError,
    TestRecordFeeDatasetPreviewNotFoundError,
    TestRecordFeeDatasetPreviewService,
    TestRecordGroupDataset,
)
from backend.infrastructure.office import (
    FeeEvaluationWorkbookWriteResult,
    OfficeAutomationUnavailable,
    TestRecordDocumentWriteResult,
)


class TestRecordFeeDocumentGenerationError(ValueError):
    """Raised when a generation request is invalid."""


class TestRecordFeeDocumentGenerationNotFoundError(LookupError):
    """Raised when generation source data cannot be found."""


class TestRecordDocumentWriter(Protocol):
    """Write operation needed for test-record document generation."""

    def generate(
        self,
        *,
        template_path: Path,
        output_path: Path,
        source_document_name: str,
        groups: tuple[TestRecordGroupDataset, ...],
        warnings: tuple[str, ...],
    ) -> TestRecordDocumentWriteResult:
        """Generate one test-record document from structured dataset data."""


class FeeEvaluationWorkbookWriter(Protocol):
    """Write operation needed for fee-evaluation workbook generation."""

    def generate(
        self,
        *,
        template_path: Path,
        output_path: Path,
        preview: TestRecordFeeDatasetPreview,
    ) -> FeeEvaluationWorkbookWriteResult:
        """Generate one fee-evaluation workbook from structured dataset data."""


@dataclass(frozen=True, slots=True)
class TestRecordFeeDocumentGenerationCommand:
    """Input for generating test-record and fee-evaluation documents."""

    project_id: str
    draft_id: str
    output_dir: Path
    test_record_template_path: Path | None = None
    fee_evaluation_template_path: Path | None = None
    overwrite: bool = False
    include_test_record: bool = True
    include_fee_evaluation: bool = True


@dataclass(frozen=True, slots=True)
class GeneratedApprovalDocument:
    """Result entry for one generated or skipped approval-package file."""

    kind: str
    source_template_path: Path
    output_path: Path | None
    status: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TestRecordFeeDocumentGenerationResult:
    """Result of one test-record and fee-evaluation generation request."""

    project_id: str
    draft_id: str
    generated_files: tuple[GeneratedApprovalDocument, ...]
    warnings: tuple[str, ...]


class TestRecordFeeDocumentGenerationService:
    """Generate controlled approval-package documents from test-plan draft data."""

    def __init__(
        self,
        *,
        dataset_preview_service: TestRecordFeeDatasetPreviewService,
        test_record_writer: TestRecordDocumentWriter,
        fee_writer: FeeEvaluationWorkbookWriter,
    ) -> None:
        """Create the service with preview and Office write boundaries."""
        self._preview = dataset_preview_service
        self._test_record_writer = test_record_writer
        self._fee_writer = fee_writer

    def generate(
        self,
        command: TestRecordFeeDocumentGenerationCommand,
    ) -> TestRecordFeeDocumentGenerationResult:
        """Generate selected approval-package documents from the structured preview."""
        _validate_command(command)
        output_dir = _validate_output_dir(command.output_dir)
        preview = self._preview_or_raise(command)
        generated: list[GeneratedApprovalDocument] = []
        warnings = list(preview.warnings)

        if command.include_test_record:
            template = _require_template(command.test_record_template_path, (".docx",))
            output_path = output_dir / _test_record_file_name(preview.source_document_name)
            _ensure_output_target(output_path, command.overwrite)
            write = self._test_record_writer.generate(
                template_path=template,
                output_path=output_path,
                source_document_name=preview.source_document_name,
                groups=(
                    preview.test_record_dataset.groups
                    if preview.test_record_dataset is not None
                    else ()
                ),
                warnings=preview.warnings,
            )
            generated.append(
                GeneratedApprovalDocument(
                    kind="test_record",
                    source_template_path=template,
                    output_path=write.output_path,
                    status=write.status,
                    warnings=write.warnings,
                )
            )

        if command.include_fee_evaluation:
            template = _require_template(command.fee_evaluation_template_path, (".xls", ".xlsx"))
            output_path = output_dir / _fee_file_name(preview.source_document_name, template.suffix)
            _ensure_output_target(output_path, command.overwrite)
            try:
                write = self._fee_writer.generate(
                    template_path=template,
                    output_path=output_path,
                    preview=preview,
                )
                generated.append(
                    GeneratedApprovalDocument(
                        kind="fee_evaluation",
                        source_template_path=template,
                        output_path=write.output_path,
                        status=write.status,
                        warnings=write.warnings,
                    )
                )
            except OfficeAutomationUnavailable as exc:
                generated.append(
                    GeneratedApprovalDocument(
                        kind="fee_evaluation",
                        source_template_path=template,
                        output_path=None,
                        status="skipped_unavailable",
                        warnings=(str(exc),),
                    )
                )

        return TestRecordFeeDocumentGenerationResult(
            project_id=command.project_id,
            draft_id=command.draft_id,
            generated_files=tuple(generated),
            warnings=tuple(warnings),
        )

    def _preview_or_raise(
        self,
        command: TestRecordFeeDocumentGenerationCommand,
    ) -> TestRecordFeeDatasetPreview:
        """Load the structured test-plan preview and map known preview failures."""
        try:
            return self._preview.preview(
                TestRecordFeeDatasetPreviewCommand(
                    project_id=command.project_id,
                    draft_id=command.draft_id,
                    include_test_record_dataset=command.include_test_record,
                    include_fee_dataset=command.include_fee_evaluation,
                )
            )
        except TestRecordFeeDatasetPreviewNotFoundError as exc:
            raise TestRecordFeeDocumentGenerationNotFoundError(str(exc)) from exc
        except TestRecordFeeDatasetPreviewError as exc:
            raise TestRecordFeeDocumentGenerationError(str(exc)) from exc


def _validate_command(command: TestRecordFeeDocumentGenerationCommand) -> None:
    """Validate generation include flags and required templates."""
    if not command.include_test_record and not command.include_fee_evaluation:
        raise TestRecordFeeDocumentGenerationError(
            "At least one output must be requested."
        )
    if command.include_test_record and command.test_record_template_path is None:
        raise TestRecordFeeDocumentGenerationError(
            "test_record_template_path is required when include_test_record is true."
        )
    if command.include_fee_evaluation and command.fee_evaluation_template_path is None:
        raise TestRecordFeeDocumentGenerationError(
            "fee_evaluation_template_path is required when include_fee_evaluation is true."
        )


def _validate_output_dir(path: Path) -> Path:
    """Validate and normalize the output directory for generated files."""
    directory = Path(path)
    if not directory.exists() or not directory.is_dir():
        raise TestRecordFeeDocumentGenerationNotFoundError(
            f"Output directory does not exist: {directory}"
        )
    return directory


def _require_template(path: Path | None, suffixes: tuple[str, ...]) -> Path:
    """Validate template path existence and expected extension."""
    if path is None:
        raise TestRecordFeeDocumentGenerationError("Template path is required.")
    template = Path(path)
    if template.suffix.lower() not in suffixes:
        allowed = ", ".join(sorted(suffixes))
        raise TestRecordFeeDocumentGenerationError(
            f"Unsupported template type for {template}. Allowed: {allowed}"
        )
    if not template.is_file():
        raise TestRecordFeeDocumentGenerationNotFoundError(
            f"Template file does not exist: {template}"
        )
    return template


def _ensure_output_target(path: Path, overwrite: bool) -> None:
    """Reject existing output files unless overwrite is explicitly enabled."""
    if path.exists() and not overwrite:
        raise TestRecordFeeDocumentGenerationError(
            f"Output file already exists and overwrite is false: {path}"
        )


def _test_record_file_name(source_document_name: str) -> str:
    """Build deterministic test-record output file name."""
    stem = Path(source_document_name).stem or "test_plan"
    return f"{stem}_test_record_generated.docx"


def _fee_file_name(source_document_name: str, suffix: str) -> str:
    """Build deterministic fee-evaluation output file name."""
    stem = Path(source_document_name).stem or "test_plan"
    return f"{stem}_fee_evaluation_generated{suffix}"
