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
class WordHeaderCellResult:
    """Result from reading one Word header table cell."""

    value: str | None
    gateway_mode: str


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
