"""Extract historical Test Report method table rows from .docx documents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from backend.infrastructure.office.word_document_gateway import WordDocumentGateway


@dataclass(frozen=True, slots=True)
class HistoricalMethodRow:
    table_index: int
    row_index: int
    test_item: str
    method: str
    condition: str
    requirement: str


@dataclass(frozen=True, slots=True)
class HistoricalMethodExtractResult:
    source_path: Path
    source_table_index: int | None
    rows: tuple[HistoricalMethodRow, ...]
    warnings: tuple[str, ...] = ()


class HistoricalTestReportMethodExtractor:
    """Deterministically extract rows from report method/requirement tables."""

    def __init__(self, *, word_gateway: WordDocumentGateway | None = None) -> None:
        self._word_gateway = word_gateway or WordDocumentGateway()

    def extract(self, source_path: Path) -> HistoricalMethodExtractResult:
        snapshot = self._word_gateway.read_word_document(source_path)
        table_contexts = _table_contexts(source_path)
        best_table_index: int | None = None
        best_rows: tuple[HistoricalMethodRow, ...] = ()
        best_score = -1
        warnings: list[str] = []

        for table_index, table in enumerate(snapshot.tables, start=1):
            parse = _parse_table(
                table_index=table_index,
                table=table,
                context_text=table_contexts.get(table_index, ""),
            )
            if parse.score <= 0:
                continue
            if parse.score > best_score:
                best_score = parse.score
                best_table_index = table_index
                best_rows = parse.rows
                warnings = list(parse.warnings)

        if best_table_index is None:
            return HistoricalMethodExtractResult(
                source_path=source_path,
                source_table_index=None,
                rows=(),
                warnings=("No methods/requirements table detected.",),
            )
        if not best_rows:
            return HistoricalMethodExtractResult(
                source_path=source_path,
                source_table_index=best_table_index,
                rows=(),
                warnings=tuple([*warnings, "Detected table contains no extractable method rows."]),
            )
        return HistoricalMethodExtractResult(
            source_path=source_path,
            source_table_index=best_table_index,
            rows=best_rows,
            warnings=tuple(warnings),
        )


@dataclass(frozen=True, slots=True)
class _ParsedTable:
    score: int
    rows: tuple[HistoricalMethodRow, ...]
    warnings: tuple[str, ...] = ()


def _parse_table(*, table_index: int, table: list[list[str]], context_text: str) -> _ParsedTable:
    if len(table) < 2:
        return _ParsedTable(score=0, rows=())
    header_index, columns = _find_header(table)
    if columns is None:
        return _ParsedTable(score=0, rows=())
    rows: list[HistoricalMethodRow] = []
    for row_index, row in enumerate(table[header_index + 1 :], start=header_index + 2):
        test_item = _cell(row, columns["test_item"])
        method = _cell(row, columns["method"])
        condition = _cell(row, columns["condition"])
        requirement = _cell(row, columns["requirement"])
        if not any((test_item, method, condition, requirement)):
            continue
        if not test_item:
            continue
        if _looks_like_structural_row(test_item):
            continue
        rows.append(
            HistoricalMethodRow(
                table_index=table_index,
                row_index=row_index,
                test_item=test_item,
                method=method,
                condition=condition,
                requirement=requirement,
            )
        )
    table_text = " ".join(" ".join(row) for row in table).lower()
    score = 30
    context_has_heading = _has_methods_heading_evidence(context_text)
    table_has_heading = _has_methods_heading_evidence(table_text)
    if not context_has_heading and not table_has_heading:
        return _ParsedTable(
            score=0,
            rows=(),
            warnings=("Skipping table without section-5 methods/requirements heading evidence.",),
        )
    if table_has_heading:
        score += 20
    if context_has_heading:
        score += 20
    return _ParsedTable(score=score, rows=tuple(rows))


def _has_methods_heading_evidence(text: str) -> bool:
    normalized = _normalize(text)
    return (
        "5" in normalized
        and "test methods" in normalized
        and "requirements" in normalized
    ) or ("test methods" in normalized and "requirements" in normalized)


def _find_header(table: list[list[str]]) -> tuple[int, dict[str, int] | None]:
    for index, row in enumerate(table[:5]):
        normalized = [_normalize(cell) for cell in row]
        test_item = _find_col(normalized, ("test item", "test items", "item", "test name"))
        method = _find_col(normalized, ("method", "test method", "standard"))
        condition = _find_col(normalized, ("condition", "test condition"))
        requirement = _find_col(normalized, ("requirement", "criteria", "judgement"))
        if None not in (test_item, method, condition, requirement):
            return index, {
                "test_item": int(test_item),
                "method": int(method),
                "condition": int(condition),
                "requirement": int(requirement),
            }
    return -1, None


def _find_col(values: list[str], candidates: tuple[str, ...]) -> int | None:
    for i, value in enumerate(values):
        if any(candidate in value for candidate in candidates):
            return i
    return None


def _cell(row: list[str], index: int) -> str:
    if index >= len(row):
        return ""
    return " ".join(row[index].replace("\x07", " ").split()).strip()


def _normalize(value: str) -> str:
    return " ".join(value.lower().split())


def _looks_like_structural_row(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered in {"group number", "sample quantity", "test item", "method", "condition", "requirement"}


def _table_contexts(source_path: Path) -> dict[int, str]:
    """Return preceding paragraph context for each table index in document order."""
    document = Document(source_path)
    contexts: dict[int, str] = {}
    recent_paragraphs: list[str] = []
    table_index = 0
    for block in _iter_block_items(document):
        if isinstance(block, Paragraph):
            text = _normalize(block.text)
            if text:
                recent_paragraphs.append(text)
                if len(recent_paragraphs) > 5:
                    recent_paragraphs.pop(0)
            continue
        if isinstance(block, Table):
            table_index += 1
            contexts[table_index] = " ".join(recent_paragraphs)
    return contexts


def _iter_block_items(document: Document):
    parent_elm = document.element.body
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)
