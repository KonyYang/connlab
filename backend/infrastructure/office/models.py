"""Data models shared by ConnLab Office infrastructure gateways."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path


class OfficeFileKind(StrEnum):
    """Supported coarse file categories for Office intake."""

    DOCX = "docx"
    DOC = "doc"
    XLSX = "xlsx"
    XLS = "xls"
    PDF = "pdf"
    IMAGE = "image"
    OUTLOOK_MSG = "outlook_msg"
    UNKNOWN = "unknown"


class LtrWorkbookFormat(StrEnum):
    """Supported LTR workbook file formats."""

    XLS = "xls"
    XLSX = "xlsx"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class OfficeFileClassification:
    """Classification result for an imported office-related file."""

    original_name: str
    extension: str
    kind: OfficeFileKind
    mime_type: str
    size_bytes: int
    supported: bool


@dataclass(frozen=True, slots=True)
class ImportedMailAttachment:
    """Attachment extracted from an imported mail package."""

    original_name: str
    stored_path: Path
    extension: str
    kind: OfficeFileKind
    mime_type: str
    size_bytes: int
    sha256: str
    content_id: str | None = None


@dataclass(frozen=True, slots=True)
class ImportedMailPackage:
    """Metadata and attachments from an imported Outlook mail package."""

    source_original_name: str
    source_stored_path: Path
    subject: str | None
    sender_name: str | None
    sender_email: str | None
    recipients: list[str] = field(default_factory=list)
    cc: list[str] = field(default_factory=list)
    sent_at: datetime | None = None
    body_text: str | None = None
    attachments: list[ImportedMailAttachment] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class WordDocumentSnapshot:
    """Text and table snapshot read from a Word document."""

    paragraphs: list[str]
    tables: list[list[list[str]]]
    headers: list[str]
    footers: list[str]
    raw_text: str


@dataclass(frozen=True, slots=True)
class WordTableLocation:
    """Layout metadata for one Word table."""

    table_index: int
    page_number: int | None
    page_table_index: int | None
    preceding_paragraph: str | None
    text_preview: str
    row_count: int
    column_count: int


@dataclass(frozen=True, slots=True)
class WordHeaderCellResult:
    """Result from reading one Word header table cell."""

    value: str | None
    gateway_mode: str


@dataclass(frozen=True, slots=True)
class WordSection2FieldChange:
    """Single Word Section 2 field update result."""

    field_key: str
    label: str
    old_value: str
    new_value: str
    location: str


@dataclass(frozen=True, slots=True)
class OfficeTimingStage:
    """One named Office automation timing stage."""

    name: str
    seconds: float


@dataclass(frozen=True, slots=True)
class OfficeTimingSnapshot:
    """Structured timing snapshot for one Office automation operation."""

    stages: tuple[OfficeTimingStage, ...] = ()

    @classmethod
    def from_seconds(cls, timings: dict[str, float]) -> "OfficeTimingSnapshot":
        """Build a timing snapshot from stage names and elapsed seconds."""
        return cls(
            stages=tuple(
                OfficeTimingStage(name=name, seconds=float(seconds))
                for name, seconds in timings.items()
            )
        )

    @property
    def total_seconds(self) -> float:
        """Return the sum of all recorded stage timings."""
        gateway_total = self.stage_seconds("gateway_total")
        if gateway_total:
            return gateway_total
        return sum(stage.seconds for stage in self.stages)

    def stage_seconds(self, name: str) -> float:
        """Return seconds recorded for a named stage, or zero when missing."""
        for stage in self.stages:
            if stage.name == name:
                return stage.seconds
        return 0.0


@dataclass(frozen=True, slots=True)
class WordSection2WriteResult:
    """Result from writing Section 2 fields into a Word document."""

    changed_fields: tuple[WordSection2FieldChange, ...]
    unchanged_fields: tuple[WordSection2FieldChange, ...]
    warnings: tuple[str, ...] = ()
    timings: OfficeTimingSnapshot | None = None



@dataclass(frozen=True, slots=True)
class LtrWorkbookSnapshot:
    """Read-only metadata and existing LTR numbers from a workbook."""

    workbook_path: Path
    workbook_format: LtrWorkbookFormat
    size_bytes: int
    modified_time: datetime
    sheet_names: tuple[str, ...]
    readable_sheet_names: tuple[str, ...]
    sheet_strategy: str
    existing_ltr_numbers: tuple[str, ...]
    unsupported_reason: str | None = None


@dataclass(frozen=True, slots=True)
class ExcelStructureProbeResult:
    """Read-only workbook structure probe result."""

    workbook_path: Path
    sheet_names: tuple[str, ...]
    matched_sheet_names: tuple[str, ...]
    observed_headers: tuple[str, ...]
    missing_headers: tuple[str, ...]
    missing_date_headers: tuple[str, ...]
    valid: bool
    failure_reason: str | None = None


@dataclass(frozen=True, slots=True)
class ExcelTabularReadResult:
    """Read-only tabular rows extracted from one or more worksheets."""

    workbook_path: Path
    matched_sheet_names: tuple[str, ...]
    headers: tuple[str, ...]
    rows: tuple[dict[str, str], ...]

@dataclass(frozen=True, slots=True)
class TestRecordDocumentWriteResult:
    """Result from generating a test-record document file."""

    output_path: Path
    status: str
    group_count: int
    warning_count: int
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class FeeEvaluationWorkbookWriteResult:
    """Result from generating a fee-evaluation workbook file."""

    output_path: Path
    status: str
    warnings: tuple[str, ...] = ()
