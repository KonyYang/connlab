"""Word document reading gateway for the Office integration boundary."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document

from backend.infrastructure.office.models import WordDocumentSnapshot


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
    return re.sub(r"\s+", " ", value).strip()
