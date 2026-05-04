"""Word document reading gateway for the Office integration boundary."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document

from backend.infrastructure.office.models import WordDocumentSnapshot, WordHeaderCellResult
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable


class WordDocumentGateway:
    """Read Word documents into neutral snapshots without business parsing."""

    def read_word_document(self, source_path: Path) -> WordDocumentSnapshot:
        """Read a `.docx` file into paragraphs, tables, headers, and footers."""
        path = Path(source_path)
        if path.suffix.lower() != ".docx":
            raise ValueError(f"Only .docx files are supported by the Word gateway: {path}")
        if not path.is_file():
            raise FileNotFoundError(f"Word document does not exist: {path}")

        document = Document(path)
        paragraphs = [_clean(paragraph.text) for paragraph in document.paragraphs]
        tables = [_table_rows(table) for table in document.tables]
        headers = _section_text(document, part_name="header")
        footers = _section_text(document, part_name="footer")
        raw_text = _raw_text(paragraphs, tables, headers, footers)
        return WordDocumentSnapshot(
            paragraphs=[text for text in paragraphs if text],
            tables=tables,
            headers=headers,
            footers=footers,
            raw_text=raw_text,
        )

    def read_header_table_cell(
        self,
        source_path: Path,
        row: int,
        column: int,
    ) -> WordHeaderCellResult:
        """Read a Word header table cell using COM first and python-docx fallback."""
        path = Path(source_path)
        if path.suffix.lower() != ".docx":
            raise ValueError(f"Only .docx files are supported by the Word header gate: {path}")
        if not path.is_file():
            raise FileNotFoundError(f"Word document does not exist: {path}")
        value = _read_header_cell_with_python_docx(path, row, column)
        if value is not None:
            return WordHeaderCellResult(
                value=_clean(value or ""),
                gateway_mode="python_docx",
            )
        value = _read_header_cell_with_com(path, row, column)
        return WordHeaderCellResult(value=_clean(value or ""), gateway_mode="word_com")


def _table_rows(table) -> list[list[str]]:
    """Return cleaned rows from a python-docx table."""
    return [[_clean(cell.text) for cell in row.cells] for row in table.rows]


def _section_text(document, *, part_name: str) -> list[str]:
    """Extract cleaned paragraph text from section headers or footers."""
    values: list[str] = []
    for section in document.sections:
        part = getattr(section, part_name)
        values.extend(_clean(paragraph.text) for paragraph in part.paragraphs)
        for table in part.tables:
            for row in _table_rows(table):
                values.extend(row)
    return [value for value in values if value]


def _read_header_cell_with_com(path: Path, row: int, column: int) -> str | None:
    """Read the first matching header table cell through Microsoft Word COM."""
    try:
        import win32com.client  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - depends on Windows host
        raise OfficeAutomationUnavailable("Word COM automation requires pywin32.") from exc

    word = win32com.client.DispatchEx("Word.Application")
    document = None
    try:
        word.Visible = False
        word.DisplayAlerts = 0
        document = word.Documents.Open(
            str(path),
            ReadOnly=True,
            AddToRecentFiles=False,
        )
        for section in _com_iter(document.Sections):
            for header in _com_iter(section.Headers):
                tables = getattr(header, "Range", header).Tables
                for table in _com_iter(tables):
                    try:
                        return str(table.Cell(row, column).Range.Text)
                    except Exception:
                        continue
        return None
    finally:
        if document is not None:
            document.Close(SaveChanges=False)
        word.Quit()


def _com_iter(collection) -> list[object]:
    """Return COM collection items using 1-based indexing."""
    count = int(getattr(collection, "Count", 0))
    return [collection.Item(index) for index in range(1, count + 1)]


def _read_header_cell_with_python_docx(path: Path, row: int, column: int) -> str | None:
    """Read the first matching header table cell through python-docx."""
    document = Document(path)
    row_index = row - 1
    column_index = column - 1
    for section in document.sections:
        for header in (section.header, section.first_page_header, section.even_page_header):
            for table in header.tables:
                if len(table.rows) <= row_index:
                    continue
                cells = table.rows[row_index].cells
                if len(cells) <= column_index:
                    continue
                return cells[column_index].text
    return None


def _raw_text(
    paragraphs: list[str],
    tables: list[list[list[str]]],
    headers: list[str],
    footers: list[str],
) -> str:
    """Build a plain text view of the document snapshot."""
    lines: list[str] = []
    lines.extend(headers)
    lines.extend(paragraphs)
    for table in tables:
        for row in table:
            lines.append(" | ".join(cell for cell in row if cell))
    lines.extend(footers)
    return "\n".join(line for line in lines if line)


def _clean(value: str) -> str:
    """Collapse Word whitespace into a single trimmed string."""
    return re.sub(r"\s+", " ", value.replace("\x07", " ")).strip()
