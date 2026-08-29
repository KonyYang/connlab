"""Immutable result-dataset domain models for report synchronization."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


RESULT_OUTCOMES = {"pass", "fail", "not_determined"}


@dataclass(frozen=True, slots=True)
class ResultDatasetSourceIdentity:
    """Stable identity for one imported source file."""

    file_name: str
    sha256: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class LlcrMeasurement:
    """One original-precision LLCR measurement with source lineage."""

    sample_index: int
    position: str
    value: Decimal
    unit: str
    source_sheet: str
    source_cell: str
    raw_value: Decimal
    raw_unit: str
    raw_source_cell: str


@dataclass(frozen=True, slots=True)
class LlcrResultEntry:
    """One Matrix Group/Step LLCR result ready for confirmation."""

    result_id: str
    confirmed_group_id: str
    group_label: str
    confirmed_row_id: str
    matrix_step_sequence: int
    matrix_step_token: str
    stage: str
    stage_label: str
    requirement: str
    requirement_comparator: str
    requirement_limit: Decimal
    requirement_unit: str
    measurements: tuple[LlcrMeasurement, ...]
    summary_min: Decimal
    summary_max: Decimal
    summary_average: Decimal
    provisional_outcome: str
    confirmed_outcome: str | None = None
    override_reason: str | None = None
    source_range: str = ""

    def __post_init__(self) -> None:
        if self.stage not in {"initial", "delta"}:
            raise ValueError("LLCR stage must be initial or delta.")
        if self.provisional_outcome not in RESULT_OUTCOMES:
            raise ValueError("Unsupported provisional LLCR outcome.")
        if self.confirmed_outcome is not None and self.confirmed_outcome not in RESULT_OUTCOMES:
            raise ValueError("Unsupported confirmed LLCR outcome.")
        if not self.measurements:
            raise ValueError("LLCR result requires at least one measurement.")
        if (
            self.confirmed_outcome is not None
            and self.confirmed_outcome != self.provisional_outcome
            and not (self.override_reason or "").strip()
        ):
            raise ValueError("An LLCR outcome override requires a reason.")


@dataclass(frozen=True, slots=True)
class LlcrDatasetPayload:
    """Typed payload owned only by the LLCR importer."""

    entries: tuple[LlcrResultEntry, ...]


@dataclass(frozen=True, slots=True)
class ResultDatasetRevision:
    """One immutable, confirmed dataset revision."""

    dataset_id: str
    dataset_type: str
    revision: int
    project_id: str
    confirmed_matrix_id: str
    confirmed_matrix_revision: int
    source: ResultDatasetSourceIdentity
    imported_at: str
    imported_by: str
    confirmed_at: str
    confirmed_by: str
    parser_profile_version: str
    validation_status: str
    payload: LlcrDatasetPayload

    def __post_init__(self) -> None:
        if self.dataset_type != "llcr":
            raise ValueError("This dataset revision requires the LLCR dataset type.")
        if self.revision < 1:
            raise ValueError("Dataset revision must be positive.")
        if self.validation_status != "confirmed":
            raise ValueError("Persisted result datasets must be confirmed.")
        if any(entry.confirmed_outcome is None for entry in self.payload.entries):
            raise ValueError("Every persisted LLCR result must be confirmed.")


@dataclass(frozen=True, slots=True)
class LlcrImportDiagnostic:
    """One preview warning or blocking conflict."""

    code: str
    severity: str
    message: str
    group_label: str | None = None
    step_token: str | None = None


@dataclass(frozen=True, slots=True)
class LlcrImportPreview:
    """Non-authoritative result of inspecting one uploaded workbook."""

    preview_id: str
    project_id: str
    confirmed_matrix_id: str
    confirmed_matrix_revision: int
    source: ResultDatasetSourceIdentity
    parser_profile_version: str
    detected_sheets: tuple[str, ...]
    entries: tuple[LlcrResultEntry, ...]
    diagnostics: tuple[LlcrImportDiagnostic, ...] = field(default_factory=tuple)

    @property
    def can_confirm(self) -> bool:
        return bool(self.entries) and not any(
            diagnostic.severity == "blocked" for diagnostic in self.diagnostics
        )


@dataclass(frozen=True, slots=True)
class LlcrConfirmationDecision:
    """Operator confirmation for one provisional result."""

    result_id: str
    outcome: str
    override_reason: str | None = None


@dataclass(frozen=True, slots=True)
class ReportDraftRevision:
    """Traceable, non-overwriting internal report draft revision."""

    report_revision_id: str
    project_id: str
    revision: int
    file_name: str
    file_path: str
    file_sha256: str
    size_bytes: int
    confirmed_matrix_id: str
    result_dataset_id: str | None
    base_report_revision_id: str | None
    created_at: str
    created_by: str
