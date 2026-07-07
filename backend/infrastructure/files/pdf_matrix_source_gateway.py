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

        tables, locations = _merge_matrix_continuation_tables(tables, locations)

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
    return _repair_split_sample_quantity_tail(_collapse_fragmented_matrix_header(normalized))


def _split_paragraphs(page_text: str) -> list[str]:
    """Split extracted page text into parser-friendly paragraph lines."""
    paragraphs: list[str] = []
    for line in (_clean_text(line) for line in page_text.splitlines()):
        if not line:
            continue
        paragraphs.append(line)
        paragraphs.extend(_inline_section_paragraphs(line))
        paragraphs.extend(_inline_note_paragraphs(line))
    return paragraphs


def _table_text_preview(table: tuple[tuple[str, ...], ...]) -> str:
    """Build a short searchable table preview."""
    parts = [" | ".join(cell for cell in row if cell) for row in table[:4]]
    return _clean_text(" ".join(part for part in parts if part))[:500]


def _merge_matrix_continuation_tables(
    tables: list[tuple[tuple[str, ...], ...]],
    locations: list[PdfTableLocation],
) -> tuple[list[tuple[tuple[str, ...], ...]], list[PdfTableLocation]]:
    """Merge page-continuation Matrix bodies into the previous Matrix table."""
    merged_tables: list[tuple[tuple[str, ...], ...]] = []
    merged_locations: list[PdfTableLocation] = []
    continuation_pages_by_table: dict[int, list[int]] = {}
    last_matrix_index: int | None = None

    for table, location in zip(tables, locations):
        if _can_merge_with_previous_matrix(
            table=table,
            location=location,
            last_matrix_index=last_matrix_index,
            merged_locations=merged_locations,
            continuation_pages_by_table=continuation_pages_by_table,
        ):
            target_index = last_matrix_index if last_matrix_index is not None else 0
            merged_tables[target_index] = (*merged_tables[target_index], *table)
            table_key = target_index + 1
            continuation_pages_by_table.setdefault(table_key, []).append(
                location.page_number or 0
            )
            previous = merged_locations[target_index]
            merged_locations[target_index] = PdfTableLocation(
                table_index=previous.table_index,
                page_number=previous.page_number,
                page_table_index=previous.page_table_index,
                preceding_paragraph=previous.preceding_paragraph,
                text_preview=_merged_table_preview(
                    merged_tables[target_index],
                    continuation_pages_by_table.get(table_key, []),
                ),
                row_count=len(merged_tables[target_index]),
                column_count=max((len(row) for row in merged_tables[target_index]), default=0),
            )
            merged_locations.append(
                PdfTableLocation(
                    table_index=previous.table_index,
                    page_number=location.page_number,
                    page_table_index=location.page_table_index,
                    preceding_paragraph=previous.preceding_paragraph,
                    text_preview=_clean_text(
                        f"Continuation of page {previous.page_number} table "
                        f"{previous.page_table_index}: {location.text_preview}"
                    )[:500],
                    row_count=len(merged_tables[target_index]),
                    column_count=max((len(row) for row in merged_tables[target_index]), default=0),
                )
            )
            continue
        merged_tables.append(table)
        merged_locations.append(
            PdfTableLocation(
                table_index=len(merged_tables),
                page_number=location.page_number,
                page_table_index=location.page_table_index,
                preceding_paragraph=location.preceding_paragraph,
                text_preview=location.text_preview,
                row_count=location.row_count,
                column_count=location.column_count,
            )
        )
        if _looks_like_matrix_table_start(table):
            last_matrix_index = len(merged_tables) - 1

    return merged_tables, merged_locations


def _can_merge_with_previous_matrix(
    *,
    table: tuple[tuple[str, ...], ...],
    location: PdfTableLocation,
    last_matrix_index: int | None,
    merged_locations: list[PdfTableLocation],
    continuation_pages_by_table: dict[int, list[int]],
) -> bool:
    """Return whether a table is a next-page continuation of a prior Matrix."""
    if last_matrix_index is None or last_matrix_index >= len(merged_locations):
        return False
    if not _looks_like_matrix_continuation_table(table):
        return False
    matrix_location = merged_locations[last_matrix_index]
    if location.page_number is None or matrix_location.page_number is None:
        return False
    table_key = last_matrix_index + 1
    merged_pages = continuation_pages_by_table.get(table_key, [])
    last_page = merged_pages[-1] if merged_pages else matrix_location.page_number
    return location.page_number == last_page + 1


def _merged_table_preview(
    table: tuple[tuple[str, ...], ...],
    continuation_pages: list[int],
) -> str:
    preview = _table_text_preview(table)
    pages = ", ".join(str(page) for page in continuation_pages if page)
    if not pages:
        return preview
    return _clean_text(f"{preview} Continued on page {pages}")[:500]


def _clean_text(value: str) -> str:
    """Normalize whitespace in extracted PDF text."""
    text = " ".join(value.replace("\x00", " ").replace("\u040e\u045e", "、").split())
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


def _repair_split_sample_quantity_tail(
    rows: tuple[tuple[str, ...], ...],
) -> tuple[tuple[str, ...], ...]:
    """Repair PDF Matrix tails where the sample label, values, and unit split."""
    repaired: list[tuple[str, ...]] = []
    index = 0
    while index < len(rows):
        row = rows[index]
        if (
            _looks_like_sample_quantity_label_row(row)
            and index + 2 < len(rows)
            and _looks_like_sample_quantity_values_row(rows[index + 1])
            and _looks_like_pcs_unit_row(rows[index + 2])
        ):
            values = rows[index + 1]
            width = max(len(row), len(values))
            combined = [""] * width
            combined[0] = "SAMPLES QUANTITY (PCS)"
            for column in range(1, width):
                combined[column] = _repair_sample_marker(values[column] if column < len(values) else "")
            repaired.append(tuple(combined))
            index += 3
            continue
        repaired.append(row)
        index += 1
    return tuple(repaired)


def _looks_like_sample_quantity_label_row(row: tuple[str, ...]) -> bool:
    first = _clean_text(row[0] if row else "").lower()
    return first in {"samples quantity", "sample quantity"} and not any(
        _clean_text(cell) for cell in row[1:]
    )


def _looks_like_sample_quantity_values_row(row: tuple[str, ...]) -> bool:
    values = [_clean_text(cell) for cell in row[1:]]
    return any(re.search(r"\d", cell) for cell in values) and not _clean_text(row[0] if row else "")


def _looks_like_pcs_unit_row(row: tuple[str, ...]) -> bool:
    first = _clean_text(row[0] if row else "").lower()
    return first in {"(pcs)", "pcs"} and not any(_clean_text(cell) for cell in row[1:])


def _repair_sample_marker(value: str) -> str:
    text = _clean_text(value)
    return re.sub(r"^(\d+)([a-z])\)$", r"\1(\2)", text, flags=re.IGNORECASE)


def _inline_section_paragraphs(line: str) -> list[str]:
    """Split dense PDF page text into Word-like numbered section paragraphs."""
    matches = list(
        re.finditer(
            r"(?<![\d.])(?P<section>[1-9]\d*(?:\.\d+)+)\s+(?=[A-Za-z])",
            line,
        )
    )
    paragraphs: list[str] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(line)
        paragraph = _clean_text(line[start:end])
        if paragraph:
            paragraphs.append(paragraph)
    return paragraphs


def _inline_note_paragraphs(line: str) -> list[str]:
    """Extract compact inline PDF notes into Word-parser marker paragraphs."""
    match = re.search(r"\bnotes?\s*:\s*(.+)", line, flags=re.IGNORECASE)
    if not match:
        return []
    note_text = re.split(r"\brevision\s+record\b", match.group(1), maxsplit=1, flags=re.IGNORECASE)[0]
    note_matches = list(
        re.finditer(
            r"(?P<marker>[a-z])[\.)]\s*(?P<body>.*?)(?=(?:\s+[a-z][\.)]\s*)|$)",
            note_text,
            flags=re.IGNORECASE,
        )
    )
    paragraphs: list[str] = []
    for item in note_matches:
        body = _clean_text(item.group("body"))
        if body:
            paragraphs.append(f"({item.group('marker').lower()}) {body}")
    return paragraphs


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


def _looks_like_matrix_table_start(rows: tuple[tuple[str, ...], ...]) -> bool:
    """Return whether a table contains a Matrix group header."""
    if not rows:
        return False
    has_group_header = any(
        any("test group id" in _clean_text(cell).lower() for cell in row)
        for row in rows[:4]
    )
    has_description_header = any(
        _looks_like_matrix_description_header(row) for row in rows[:6]
    )
    return has_group_header and has_description_header


def _looks_like_matrix_continuation_table(rows: tuple[tuple[str, ...], ...]) -> bool:
    """Return whether a table starts with Matrix body rows but no header."""
    if not rows or _looks_like_matrix_table_start(rows):
        return False
    first = rows[0]
    if len(first) < 3:
        return False
    item = _clean_text(first[0])
    section = _clean_text(first[1])
    if not item or not section:
        return False
    if item.lower().startswith(("number", "title", "rev", "revision")):
        return False
    if not re.search(r"[A-Za-z]{2,}", item):
        return False
    return re.match(r"^\d+(?:\.\d+)*(?:/\d+(?:\.\d+)*)?$", section) is not None


def _looks_like_revision_record_table(rows: tuple[tuple[str, ...], ...]) -> bool:
    """Return whether a PDF table is an obvious revision record."""
    if not rows:
        return False
    first_row = {_clean_text(cell).lower() for cell in rows[0] if cell}
    return {"rev", "page", "description", "date"}.issubset(first_row)
