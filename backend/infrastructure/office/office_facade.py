"""Facade for ConnLab Office-related file reading and classification."""

from __future__ import annotations

import mimetypes
from pathlib import Path

from backend.infrastructure.office.excel_workbook_gateway import ExcelWorkbookGateway
from backend.infrastructure.office.models import (
    ExcelTabularReadResult,
    ExcelStructureProbeResult,
    ImportedMailPackage,
    OfficeFileClassification,
    OfficeFileKind,
    WordDocumentSnapshot,
    WordHeaderCellResult,
)
from backend.infrastructure.office.outlook_msg_gateway import OutlookMsgGateway
from backend.infrastructure.office.word_document_gateway import WordDocumentGateway
from backend.infrastructure.office.office_lifecycle import (
    ExcelWorkbookHandle,
    OfficeLifecycleManager,
)


class OfficeFacade:
    """Single entry point for Office infrastructure operations."""

    def __init__(
        self,
        *,
        word_gateway: WordDocumentGateway | None = None,
        outlook_gateway: OutlookMsgGateway | None = None,
        excel_gateway: ExcelWorkbookGateway | None = None,
        lifecycle: OfficeLifecycleManager | None = None,
    ) -> None:
        """Create the facade with optional gateway overrides for tests."""
        self._word_gateway = word_gateway or WordDocumentGateway()
        self._outlook_gateway = outlook_gateway or OutlookMsgGateway()
        self._excel_gateway = excel_gateway or ExcelWorkbookGateway()
        self._lifecycle = lifecycle or OfficeLifecycleManager()

    def classify_file(self, source_path: Path) -> OfficeFileClassification:
        """Classify an office-related file by extension and size."""
        path = Path(source_path)
        if not path.is_file():
            raise FileNotFoundError(f"Office source file does not exist: {path}")

        extension = path.suffix.lower().lstrip(".")
        kind = _kind_from_extension(extension)
        mime_type = mimetypes.guess_type(path.name)[0] or _fallback_mime_type(kind)
        return OfficeFileClassification(
            original_name=path.name,
            extension=extension,
            kind=kind,
            mime_type=mime_type,
            size_bytes=path.stat().st_size,
            supported=kind is not OfficeFileKind.UNKNOWN,
        )

    def read_word_document(self, source_path: Path) -> WordDocumentSnapshot:
        """Read a Word document through the configured gateway."""
        return self._word_gateway.read_word_document(source_path)

    def read_word_header_table_cell(
        self,
        source_path: Path,
        row: int,
        column: int,
    ) -> WordHeaderCellResult:
        """Read one Word header table cell through the configured gateway."""
        return self._word_gateway.read_header_table_cell(source_path, row, column)

    def import_outlook_msg(
        self,
        source_path: Path,
        target_dir: Path,
        *,
        original_name: str | None = None,
    ) -> ImportedMailPackage:
        """Import an Outlook `.msg` file through the configured gateway."""
        return self._outlook_gateway.import_outlook_msg(
            source_path,
            target_dir,
            original_name=original_name,
        )

    def read_excel_workbook(self, source_path: Path) -> object:
        """Read an Excel workbook through the configured gateway."""
        return self._excel_gateway.read_workbook(source_path)

    def probe_excel_structure(
        self,
        source_path: Path,
        *,
        expected_headers: tuple[str, ...],
        expected_date_headers: tuple[str, ...] = (),
        expected_sheet_names: tuple[str, ...] = (),
        expected_sheet_name_patterns: tuple[str, ...] = (),
    ) -> ExcelStructureProbeResult:
        """Probe workbook sheets and headers through the Excel gateway."""
        return self._excel_gateway.probe_structure(
            source_path,
            expected_headers=expected_headers,
            expected_date_headers=expected_date_headers,
            expected_sheet_names=expected_sheet_names,
            expected_sheet_name_patterns=expected_sheet_name_patterns,
        )

    def read_excel_tabular_rows(
        self,
        source_path: Path,
        *,
        expected_headers: tuple[str, ...],
        expected_sheet_names: tuple[str, ...] = (),
        expected_sheet_name_patterns: tuple[str, ...] = (),
    ) -> ExcelTabularReadResult:
        """Read header-aligned worksheet rows through the Excel gateway."""
        return self._excel_gateway.read_tabular_rows(
            source_path,
            expected_headers=expected_headers,
            expected_sheet_names=expected_sheet_names,
            expected_sheet_name_patterns=expected_sheet_name_patterns,
        )

    def open_excel_workbook(
        self,
        source_path: Path,
        *,
        modify_password: str | None = None,
        read_only: bool = False,
    ) -> ExcelWorkbookHandle:
        """Open an Excel workbook through the Office lifecycle boundary."""
        return self._lifecycle.open_excel_workbook(
            Path(source_path),
            modify_password=modify_password,
            read_only=read_only,
        )


def _kind_from_extension(extension: str) -> OfficeFileKind:
    """Map a file extension to a coarse Office file kind."""
    if extension == "docx":
        return OfficeFileKind.DOCX
    if extension == "doc":
        return OfficeFileKind.DOC
    if extension == "xlsx":
        return OfficeFileKind.XLSX
    if extension == "xls":
        return OfficeFileKind.XLS
    if extension == "pdf":
        return OfficeFileKind.PDF
    if extension == "msg":
        return OfficeFileKind.OUTLOOK_MSG
    if extension in {"jpg", "jpeg", "png", "gif", "bmp", "tif", "tiff"}:
        return OfficeFileKind.IMAGE
    return OfficeFileKind.UNKNOWN


def _fallback_mime_type(kind: OfficeFileKind) -> str:
    """Return a stable fallback MIME type for known Office file kinds."""
    fallback = {
        OfficeFileKind.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        OfficeFileKind.DOC: "application/msword",
        OfficeFileKind.XLSX: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        OfficeFileKind.XLS: "application/vnd.ms-excel",
        OfficeFileKind.PDF: "application/pdf",
        OfficeFileKind.IMAGE: "image/*",
        OfficeFileKind.OUTLOOK_MSG: "application/vnd.ms-outlook",
        OfficeFileKind.UNKNOWN: "application/octet-stream",
    }
    return fallback[kind]
