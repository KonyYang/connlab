"""Application service for Confirmed-Matrix-backed Fee Evaluation export."""

from __future__ import annotations

from dataclasses import dataclass
import getpass
import re
from pathlib import Path
from typing import Literal, Protocol

from backend.application.confirmed_matrix_fee_draft_service import (
    BuildConfirmedMatrixFeeDraftCommand,
    ConfirmedMatrixFeeDraftError,
    ConfirmedMatrixFeeDraftNotFoundError,
    ConfirmedMatrixFeeDraftService,
    FeeEvaluationDraft,
)
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    BuildMatrixBasicFeeTemplateCommand,
    ConfirmedMatrixAuthorityStore,
    ConfirmedMatrixFeeTemplateBasicFillService,
    MatrixBasicFillWorkbook,
)
from backend.application.fee_evaluation_export_lineage import (
    FeeEvaluationExportLineTrace,
    lineage_note,
    line_traceability,
    matrix_basic_lineage_note,
    matrix_basic_line_traceability,
)
from backend.application.project_output_record_service import (
    ProjectOutputRecordService,
    RegisterProjectOutputCommand,
)
from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus
from backend.infrastructure.office.models import FeeEvaluationWorkbookWriteResult
from backend.modules.fee_evaluation import (
    FeeRuleSeedLoaderError,
    FeeRuleSeedValidationError,
)


class ConfirmedMatrixFeeEvaluationExportError(ValueError):
    """Raised when a fee evaluation export request is invalid or cannot complete."""


class ConfirmedMatrixFeeEvaluationExportNotFoundError(LookupError):
    """Raised when a required export input path or authority record is missing."""


class ConfirmedMatrixFeeEvaluationExportUnavailableError(RuntimeError):
    """Raised when the workbook writer is unavailable for export."""


@dataclass(frozen=True, slots=True)
class ExportConfirmedMatrixFeeEvaluationCommand:
    """Input command for exporting a confirmed-Matrix fee evaluation workbook."""

    project_id: str
    template_path: Path
    output_dir: Path | None = None
    output_file_name: str | None = None
    overwrite: bool = False
    allow_review_required: bool = False
    prepared_by: str | None = None
    approved_by: str | None = None
    connlab_user: str | None = None
    fill_mode: Literal["fee_draft", "matrix_basic"] = "fee_draft"


@dataclass(frozen=True, slots=True)
class ExportConfirmedMatrixFeeEvaluationResult:
    """Result metadata for one generated fee evaluation workbook."""

    project_id: str
    output_path: Path
    output_format: str
    status: str
    confirmed_matrix_id: str
    confirmed_revision: int
    pricing_rule_version_id: str
    pricing_effective_from: str | None
    prepared_by: str | None
    approved_by: str | None
    output_record_id: str | None
    line_traceability: tuple[FeeEvaluationExportLineTrace, ...]
    warnings: tuple[str, ...]


class FeeEvaluationWorkbookWriter(Protocol):
    """Workbook writer port implemented by Office infrastructure."""

    def generate_from_draft(
        self,
        *,
        template_path: Path,
        output_path: Path,
        draft: FeeEvaluationDraft,
        prepared_by: str | None,
        approved_by: str | None,
    ) -> FeeEvaluationWorkbookWriteResult:
        """Generate a workbook from a structured fee draft."""

    def generate_matrix_basic_fill(
        self,
        *,
        template_path: Path,
        output_path: Path,
        basic_fill: MatrixBasicFillWorkbook,
        review_required: bool,
        prepared_by: str | None,
        approved_by: str | None,
    ) -> FeeEvaluationWorkbookWriteResult:
        """Generate a workbook from Matrix basic-fill rows."""


class ConfirmedMatrixFeeEvaluationExportService:
    """Export active Confirmed Matrix fee draft data to a workbook output."""

    def __init__(
        self,
        *,
        fee_draft_service: ConfirmedMatrixFeeDraftService,
        confirmed_store: ConfirmedMatrixAuthorityStore,
        project_output_service: ProjectOutputRecordService,
        workbook_writer: FeeEvaluationWorkbookWriter,
    ) -> None:
        self._fee_draft_service = fee_draft_service
        self._basic_fill_service = ConfirmedMatrixFeeTemplateBasicFillService(
            confirmed_store=confirmed_store
        )
        self._project_output_service = project_output_service
        self._writer = workbook_writer

    def export(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> ExportConfirmedMatrixFeeEvaluationResult:
        """Generate one fee evaluation workbook and register output lineage."""
        template_path = _require_template(command.template_path)
        output_dir = _require_output_dir(command.output_dir)
        if command.fill_mode == "fee_draft":
            draft = self._fee_draft_service.build_draft(
                BuildConfirmedMatrixFeeDraftCommand(project_id=command.project_id)
            )
            return self._export_fee_draft(
                command=command,
                template_path=template_path,
                output_dir=output_dir,
                draft=draft,
            )
        if command.fill_mode == "matrix_basic":
            return self._export_matrix_basic(
                command=command,
                template_path=template_path,
                output_dir=output_dir,
            )
        raise ConfirmedMatrixFeeEvaluationExportError(
            f"Unsupported fee evaluation export fill mode: {command.fill_mode}"
        )

    def _export_fee_draft(
        self,
        *,
        command: ExportConfirmedMatrixFeeEvaluationCommand,
        template_path: Path,
        output_dir: Path,
        draft: FeeEvaluationDraft,
    ) -> ExportConfirmedMatrixFeeEvaluationResult:
        """Export the original TASK_288 fee-draft workbook mode."""
        _require_exportable_draft(draft, command.allow_review_required)
        output_path = output_dir / _output_file_name(command, draft, template_path)
        if output_path.exists() and not command.overwrite:
            raise ConfirmedMatrixFeeEvaluationExportError(
                f"Output file already exists: {output_path}"
            )

        prepared_by, prepared_warnings = resolve_prepared_by(
            prepared_by=command.prepared_by,
            connlab_user=command.connlab_user,
        )
        approved_by = _normalize_optional_text(command.approved_by)
        warnings = list(prepared_warnings)
        if approved_by is None:
            warnings.append("Approval remains manual.")

        write = self._writer.generate_from_draft(
            template_path=template_path,
            output_path=output_path,
            draft=draft,
            prepared_by=prepared_by,
            approved_by=approved_by,
        )
        warnings.extend(write.warnings)

        record_id = self._register_output(
            project_id=command.project_id,
            output_path=write.output_path,
            note=lineage_note(draft),
        )
        return ExportConfirmedMatrixFeeEvaluationResult(
            project_id=command.project_id,
            output_path=write.output_path,
            output_format=write.output_path.suffix.lower().lstrip("."),
            status=write.status,
            confirmed_matrix_id=draft.header.confirmed_matrix_id,
            confirmed_revision=draft.header.confirmed_revision,
            pricing_rule_version_id=draft.header.pricing_rule_version_id,
            pricing_effective_from=draft.header.pricing_effective_from,
            prepared_by=prepared_by,
            approved_by=approved_by,
            output_record_id=record_id,
            line_traceability=line_traceability(draft),
            warnings=tuple(warnings),
        )

    def _export_matrix_basic(
        self,
        *,
        command: ExportConfirmedMatrixFeeEvaluationCommand,
        template_path: Path,
        output_dir: Path,
    ) -> ExportConfirmedMatrixFeeEvaluationResult:
        """Export Matrix basic-fill rows without requiring fee calculation readiness."""
        basic_fill = self._basic_fill_service.build(
            BuildMatrixBasicFeeTemplateCommand(project_id=command.project_id)
        )
        if basic_fill.status == "empty":
            raise ConfirmedMatrixFeeEvaluationExportError(
                "Confirmed Matrix has no selected rows to export."
            )
        draft, draft_warnings = self._try_build_fee_draft(command.project_id)
        output_path = output_dir / _output_file_name(command, draft, template_path, basic_fill)
        if output_path.exists() and not command.overwrite:
            raise ConfirmedMatrixFeeEvaluationExportError(
                f"Output file already exists: {output_path}"
            )

        prepared_by, prepared_warnings = resolve_prepared_by(
            prepared_by=command.prepared_by,
            connlab_user=command.connlab_user,
        )
        approved_by = _normalize_optional_text(command.approved_by)
        pricing_requires_review, review_warnings = _matrix_basic_review_state(
            basic_fill=basic_fill,
            draft=draft,
        )
        warnings = list(prepared_warnings)
        warnings.append("Matrix basic fill only.")
        warnings.extend(draft_warnings)
        warnings.extend(review_warnings)
        if pricing_requires_review:
            warnings.append("Pricing still requires review.")
        if approved_by is None:
            warnings.append("Approval remains manual.")

        write = self._writer.generate_matrix_basic_fill(
            template_path=template_path,
            output_path=output_path,
            basic_fill=basic_fill,
            review_required=pricing_requires_review,
            prepared_by=prepared_by,
            approved_by=approved_by,
        )
        warnings.extend(
            warning for warning in write.warnings if warning not in warnings
        )

        record_id = self._register_output(
            project_id=command.project_id,
            output_path=write.output_path,
            note=matrix_basic_lineage_note(
                basic_fill=basic_fill,
                pricing_requires_review=pricing_requires_review,
            ),
        )
        return ExportConfirmedMatrixFeeEvaluationResult(
            project_id=command.project_id,
            output_path=write.output_path,
            output_format=write.output_path.suffix.lower().lstrip("."),
            status=write.status,
            confirmed_matrix_id=basic_fill.header.confirmed_matrix_id,
            confirmed_revision=basic_fill.header.confirmed_revision,
            pricing_rule_version_id=draft.header.pricing_rule_version_id if draft else "",
            pricing_effective_from=draft.header.pricing_effective_from if draft else None,
            prepared_by=prepared_by,
            approved_by=approved_by,
            output_record_id=record_id,
            line_traceability=matrix_basic_line_traceability(basic_fill),
            warnings=tuple(warnings),
        )

    def _try_build_fee_draft(
        self, project_id: str
    ) -> tuple[FeeEvaluationDraft | None, tuple[str, ...]]:
        """Return best-effort fee draft metadata for Matrix basic-fill exports."""
        try:
            return (
                self._fee_draft_service.build_draft(
                    BuildConfirmedMatrixFeeDraftCommand(project_id=project_id)
                ),
                (),
            )
        except (
            ConfirmedMatrixFeeDraftError,
            ConfirmedMatrixFeeDraftNotFoundError,
            FeeRuleSeedLoaderError,
            FeeRuleSeedValidationError,
        ):
            return None, ("Fee draft review metadata is unavailable.",)

    def _register_output(
        self,
        *,
        project_id: str,
        output_path: Path,
        note: str,
    ) -> str | None:
        summary = self._project_output_service.get_status_summary(project_id)
        if not summary.active_draft_id:
            raise ConfirmedMatrixFeeEvaluationExportError(
                "An active reviewed draft is required to register fee evaluation output."
            )
        record = self._project_output_service.register_output(
            RegisterProjectOutputCommand(
                project_id=project_id,
                output_kind=ProjectOutputKind.FEE_EVALUATION,
                status=ProjectOutputStatus.CURRENT,
                source=ProjectOutputSource.SYSTEM_GENERATED,
                output_path=str(output_path),
                draft_id=summary.active_draft_id,
                note=note,
            )
        )
        return getattr(record, "output_record_id", None)


def resolve_prepared_by(
    *,
    prepared_by: str | None = None,
    connlab_user: str | None = None,
) -> tuple[str | None, tuple[str, ...]]:
    """Resolve Prepared by using explicit value, ConnLab user, then OS user."""
    explicit = _normalize_optional_text(prepared_by)
    if explicit:
        return explicit, ()
    user = _normalize_optional_text(connlab_user)
    if user:
        return user, ()
    try:
        os_user = _normalize_optional_text(getpass.getuser())
    except Exception:
        return None, ("Prepared by could not be resolved from the current user.",)
    if os_user:
        return os_user, ()
    return None, ("Prepared by could not be resolved from the current user.",)


def _require_template(path: Path) -> Path:
    template = Path(path)
    if template.suffix.lower() not in {".xls", ".xlsx"}:
        raise ConfirmedMatrixFeeEvaluationExportError(
            f"Unsupported fee template type: {template}"
        )
    if not template.is_file():
        raise ConfirmedMatrixFeeEvaluationExportNotFoundError(
            f"Template does not exist: {template}"
        )
    return template


def _require_output_dir(path: Path | None) -> Path:
    if path is None:
        raise ConfirmedMatrixFeeEvaluationExportError(
            "output_dir is required for fee evaluation export."
        )
    output_dir = Path(path)
    if not output_dir.is_dir():
        raise ConfirmedMatrixFeeEvaluationExportNotFoundError(
            f"Output directory does not exist: {output_dir}"
        )
    return output_dir


def _require_exportable_draft(
    draft: FeeEvaluationDraft, allow_review_required: bool
) -> None:
    if draft.draft_status == "empty":
        raise ConfirmedMatrixFeeEvaluationExportError(
            "Fee draft has no fee lines to export."
        )
    if draft.draft_status == "needs_review" and not allow_review_required:
        raise ConfirmedMatrixFeeEvaluationExportError(
            "Fee draft requires review before export."
        )


def _output_file_name(
    command: ExportConfirmedMatrixFeeEvaluationCommand,
    draft: FeeEvaluationDraft | None,
    template_path: Path,
    basic_fill: MatrixBasicFillWorkbook | None = None,
) -> str:
    explicit = _normalize_optional_text(command.output_file_name)
    if explicit:
        return _sanitize_file_name(explicit)
    if draft is None:
        if basic_fill is None:
            raise ConfirmedMatrixFeeEvaluationExportError(
                "Fee export output file name cannot be resolved."
            )
        stem = _sanitize_file_name(
            (
                f"{command.project_id}_fee_evaluation_"
                f"{basic_fill.header.confirmed_revision}_matrix_basic"
            )
        )
        return f"{stem}{template_path.suffix.lower()}"
    stem = _sanitize_file_name(
        (
            f"{command.project_id}_fee_evaluation_"
            f"{draft.header.confirmed_revision}_"
            f"{draft.header.pricing_rule_version_id}"
        )
    )
    return f"{stem}{template_path.suffix.lower()}"


def _matrix_basic_review_state(
    *,
    basic_fill: MatrixBasicFillWorkbook,
    draft: FeeEvaluationDraft | None,
) -> tuple[bool, list[str]]:
    """Return review state for Matrix basic fill using draft only as metadata."""
    if draft is None:
        return True, []
    warnings: list[str] = []
    requires_review = draft.draft_status != "ready"
    draft_line_ids = {
        line.line_id
        for group in draft.groups
        for line in group.line_items
    }
    basic_line_ids = {
        line.line_id
        for group in basic_fill.groups
        for line in group.lines
    }
    if basic_line_ids - draft_line_ids:
        requires_review = True
        warnings.append("Matrix basic fill includes rows not present in fee draft.")
    return requires_review, warnings


def _sanitize_file_name(value: str) -> str:
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", value.strip())
    sanitized = sanitized.rstrip(" .")
    if not sanitized:
        raise ConfirmedMatrixFeeEvaluationExportError("Output file name is empty.")
    return sanitized


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None
