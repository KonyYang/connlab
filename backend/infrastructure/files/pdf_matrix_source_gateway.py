"""Deterministic text-PDF source gateway for Matrix import previews."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class PdfMatrixSourceGatewayError(ValueError):
    """Raised when a PDF cannot produce a text Matrix source snapshot."""


@dataclass(frozen=True, slots=True)
class PdfTableLocation:
    """Layout metadata for one extracted PDF table."""

    table_index: int
    page_number: int | None
    page_table_index: int | None
    preceding_paragraph: str | None
    text_preview: str
    row_count: int
    column_count: int


@dataclass(frozen=True, slots=True)
class PdfDocumentSnapshot:
    """Text and table snapshot read from a text PDF."""

    paragraphs: tuple[str, ...]
    tables: tuple[tuple[tuple[str, ...], ...], ...]
    table_locations: tuple[PdfTableLocation, ...]
    raw_text: str


class PdfMatrixSourceGateway:
    """Read text PDFs into Word-like Matrix preview snapshots."""

    def read_pdf_document(self, source_path: Path) -> PdfDocumentSnapshot:
        """Read one text PDF into paragraphs, tables, and page-table locations."""
        path = Path(source_path)
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Only .pdf files are supported by the PDF Matrix gateway: {path}")
        if not path.is_file():
            raise FileNotFoundError(f"PDF source file does not exist: {path}")

        try:
            import pdfplumber
        except ImportError as exc:
            raise PdfMatrixSourceGatewayError(
                "Cannot read this PDF for Matrix import on this workstation."
            ) from exc

        paragraphs: list[str] = []
        raw_text_parts: list[str] = []
        tables: list[tuple[tuple[str, ...], ...]] = []
        locations: list[PdfTableLocation] = []

        try:
            with pdfplumber.open(path) as pdf:
                for page_number, page in enumerate(pdf.pages, start=1):
                    page_text = _clean_text(page.extract_text() or "")
                    if page_text:
                        raw_text_parts.append(page_text)
                    page_paragraphs = _split_paragraphs(page_text)
                    paragraphs.extend(page_paragraphs)
                    page_table_index = 0
                    for raw_table in _extract_page_tables(page):
                        table = _normalize_table(raw_table)
                        if not table:
                            continue
                        page_table_index += 1
                        table_index = len(tables) + 1
                        tables.append(table)
                        locations.append(
                            PdfTableLocation(
                                table_index=table_index,
                                page_number=page_number,
                                page_table_index=page_table_index,
                                preceding_paragraph=page_paragraphs[-1] if page_paragraphs else None,
                                text_preview=_table_text_preview(table),
                                row_count=len(table),
                                column_count=max((len(row) for row in table), default=0),
                            )
                        )
        except PdfMatrixSourceGatewayError:
            raise
        except Exception as exc:
            raise PdfMatrixSourceGatewayError(
                "Cannot read this PDF for Matrix import on this workstation."
            ) from exc

        raw_text = "\n".join(raw_text_parts)
        if not raw_text.strip():
            raise PdfMatrixSourceGatewayError(
                "This PDF has no extractable text. OCR is not supported in this version."
            )
        if not tables:
            raise PdfMatrixSourceGatewayError("No text table was found in this PDF.")

        return PdfDocumentSnapshot(
            paragraphs=tuple(paragraphs),
            tables=tuple(tables),
            table_locations=tuple(locations),
            raw_text=raw_text,
        )


def _extract_page_tables(page: Any) -> list[Any]:
    """Extract page tables with line-first settings and a text fallback."""
    line_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "join_tolerance": 3,
        "intersection_tolerance": 5,
        "text_x_tolerance": 2,
        "text_y_tolerance": 3,
    }
    tables = page.extract_tables(table_settings=line_settings) or []
    if tables:
        return tables
    text_settings = {
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        "intersection_tolerance": 5,
        "text_x_tolerance": 2,
        "text_y_tolerance": 3,
    }
    return page.extract_tables(table_settings=text_settings) or []


def _normalize_table(raw_table: Any) -> tuple[tuple[str, ...], ...]:
    """Clean extracted table cells and discard empty rows/columns."""
    rows: list[list[str]] = []
    for raw_row in raw_table or []:
        row = [_clean_text(str(cell or "")) for cell in raw_row or []]
        if any(cell for cell in row):
            rows.append(row)
    if not rows:
        return ()

    max_columns = max(len(row) for row in rows)
    padded = [row + [""] * (max_columns - len(row)) for row in rows]
    keep_columns = [
        index
        for index in range(max_columns)
        if any(row[index].strip() for row in padded)
    ]
    if not keep_columns:
        return ()
    normalized = tuple(tuple(row[index] for index in keep_columns) for row in padded)
    if _looks_like_revision_record_table(normalized):
        return ()
    return _collapse_fragmented_matrix_header(normalized)


def _split_paragraphs(page_text: str) -> list[str]:
    """Split extracted page text into parser-friendly paragraph lines."""
    return [line for line in (_clean_text(line) for line in page_text.splitlines()) if line]


def _table_text_preview(table: tuple[tuple[str, ...], ...]) -> str:
    """Build a short searchable table preview."""
    parts = [" | ".join(cell for cell in row if cell) for row in table[:4]]
    return _clean_text(" ".join(part for part in parts if part))[:500]


def _clean_text(value: str) -> str:
    """Normalize whitespace in extracted PDF text."""
    text = " ".join(value.replace("\x00", " ").split())
    return re.sub(r"\bSECTIO\s+N\b", "SECTION", text, flags=re.IGNORECASE)


def _collapse_fragmented_matrix_header(
    rows: tuple[tuple[str, ...], ...],
) -> tuple[tuple[str, ...], ...]:
    """Make PDF-fragmented Matrix headers look like the Word table shape."""
    group_row_index = next(
        (
            index
            for index, row in enumerate(rows)
            if any("test group id" in _clean_text(cell).lower() for cell in row)
        ),
        None,
    )
    if group_row_index is None:
        return rows

    description_row_index = next(
        (
            index
            for index in range(group_row_index + 1, len(rows))
            if _looks_like_matrix_description_header(rows[index])
        ),
        None,
    )
    if description_row_index is None or description_row_index == group_row_index + 1:
        return rows

    return (
        *rows[: group_row_index + 1],
        rows[description_row_index],
        *rows[description_row_index + 1 :],
    )


def _looks_like_matrix_description_header(row: tuple[str, ...]) -> bool:
    """Return whether a row carries test item and section header cells."""
    normalized = [_clean_text(cell).lower() for cell in row]
    has_test_item = any(
        "test description" in cell
        or "test item" in cell
        or cell == "test"
        for cell in normalized
    )
    has_section = any("section" in cell or "para" in cell for cell in normalized)
    return has_test_item and has_section


def _looks_like_revision_record_table(rows: tuple[tuple[str, ...], ...]) -> bool:
    """Return whether a PDF table is an obvious revision record."""
    if not rows:
        return False
    first_row = {_clean_text(cell).lower() for cell in rows[0] if cell}
    return {"rev", "page", "description", "date"}.issubset(first_row)
