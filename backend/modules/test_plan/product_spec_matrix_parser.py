"""Deterministic parser for product specification Matrix tables."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from backend.modules.test_plan.product_spec_matrix_parser_support import (
    clean as _clean,
    collect_marker_notes as _collect_marker_notes,
    extract_marker as _extract_marker,
    find_test_sequence_header as _find_test_sequence_header,
    looks_like_revision_record_table as _looks_like_revision_record_table,
    normalize as _normalize,
    row_item_section_note as _row_item_section_note,
    table_score as _table_score,
)
from backend.modules.test_plan.spec_section_text_extractor import (
    MatrixRowDetailExtraction,
    extract_row_details_by_section,
)


@dataclass(frozen=True, slots=True)
class MatrixStepPreview:
    """One test step extracted from a Matrix group column."""

    sequence: int
    raw_token: str
    suffix_note: str | None
    test_item: str
    source_section: str | None
    source_table_index: int
    source_row_index: int
    source_note: str | None = None
    source_note_origin: str | None = None
    source_item_section_note: str | None = None
    condition_summary: str | None = None
    method_summary: str | None = None
    reference_standard: str | None = None
    judgement_criteria: str | None = None
    estimated_duration_hint: str | None = None
    duration_source: str | None = None
    duration_status: str = "deferred"
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class MatrixGroupPreview:
    """One test group extracted from a Matrix table."""

    group_key: str
    group_label: str
    source_table_index: int
    extraction_status: str
    steps: tuple[MatrixStepPreview, ...]
    sample_size: int | None = None
    sample_quantity_expression: str | None = None
    sample_note: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixRowPreview:
    """One source matrix row preserved in source order."""

    source_row_index: int
    test_item: str
    source_section: str | None
    group_tokens: dict[str, str]
    is_sample_row: bool = False
    method: str | None = None
    condition: str | None = None
    requirement: str | None = None
    detail_extraction_status: str | None = None
    detail_extraction_source_section: str | None = None
    detail_extraction_notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class MatrixParseResult:
    """Read-only Matrix extraction result."""

    groups: tuple[MatrixGroupPreview, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)
    blockers: tuple[str, ...] = field(default_factory=tuple)
    selected_table_index: int | None = None
    rows: tuple[MatrixRowPreview, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class _Header:
    row_index: int
    item_column: int
    section_column: int | None
    group_columns: tuple[tuple[int, str], ...]


class ProductSpecMatrixParser:
    """Extract group sequences from Matrix-like product specification tables."""

    _GROUP_RE = re.compile(r"\bgroup\s*(\d+)\b", re.IGNORECASE)
    _GROUP_NUMERIC_RE = re.compile(r"^\s*\d+[a-z]?\s*$", re.IGNORECASE)
    _STEP_TOKEN_RE = re.compile(r"^(?P<number>\d+)(?P<suffix>.*)$")
    _SAMPLE_ROW_RE = re.compile(r"\bsamples?\b", re.IGNORECASE)
    _SECTION_STEP_LIKE_RE = re.compile(r"^\s*\d+(\.\d+)*\s*$")
    _MIN_MATRIX_SCORE = 45

    def parse_tables(
        self,
        tables: list[list[list[str]]],
        paragraphs: list[str] | None = None,
        selected_table_index: int | None = None,
        table_contexts: dict[int, str] | None = None,
    ) -> MatrixParseResult:
        """Parse the first supported Matrix-like table from document tables."""
        warnings: list[str] = []
        source_paragraphs = paragraphs or []
        marker_notes = _collect_marker_notes(source_paragraphs)
        row_details = extract_row_details_by_section(source_paragraphs)
        best_result: MatrixParseResult | None = None
        best_score = -1
        for table_index, table in enumerate(tables, start=1):
            if selected_table_index is not None and table_index != selected_table_index:
                continue
            if _looks_like_revision_record_table(table):
                continue
            header = self._find_header(table)
            if header is None:
                continue
            result = self._parse_table(table, table_index, header, marker_notes, row_details)
            score = _table_score(
                result=result,
                header=header,
                table=table,
                table_context=(table_contexts or {}).get(table_index),
            )
            if score < self._MIN_MATRIX_SCORE:
                continue
            prefer_later_tie = (
                score == best_score
                and best_result is not None
                and (best_result.selected_table_index or 0) < table_index
            )
            if score > best_score or prefer_later_tie:
                best_score = score
                best_result = MatrixParseResult(
                    groups=result.groups,
                    warnings=tuple([*warnings, *result.warnings]),
                    blockers=result.blockers,
                    selected_table_index=table_index,
                    rows=result.rows,
                )
        if best_result is not None:
            return best_result
        if selected_table_index is not None:
            return MatrixParseResult(
                groups=(),
                blockers=(f"Selected table {selected_table_index} is not a valid Matrix table.",),
            )
        return MatrixParseResult(
            groups=(),
            blockers=("No Matrix table with test items, section, and Group columns was found.",),
        )

    def _find_header(self, table: list[list[str]]) -> _Header | None:
        """Find the header row that defines test item, section, and groups."""
        special_header = _find_test_sequence_header(table)
        if special_header is not None:
            row_index, item_column, section_column, group_columns = special_header
            return _Header(
                row_index=row_index,
                item_column=item_column,
                section_column=section_column,
                group_columns=group_columns,
            )
        for row_index, row in enumerate(table, start=1):
            normalized = [_normalize(cell) for cell in row]
            group_columns = tuple(
                (index, _clean(row[index]))
                for index, value in enumerate(normalized)
                if self._GROUP_RE.search(value) or self._GROUP_NUMERIC_RE.match(value)
            )
            if not group_columns:
                continue
            item_column = _find_column(normalized, ("test items", "test item", "test description", "test"))
            section_column = _find_column(normalized, ("section", "para"))
            if (item_column is None or section_column is None) and row_index < len(table):
                next_row = table[row_index]
                next_normalized = [_normalize(cell) for cell in next_row]
                next_item = _find_column(next_normalized, ("test items", "test item", "test description", "test"))
                next_section = _find_column(next_normalized, ("section", "para"))
                if next_item is not None and next_section is not None:
                    return _Header(
                        row_index=row_index + 1,
                        item_column=next_item,
                        section_column=next_section,
                        group_columns=group_columns,
                    )
            if item_column is None or section_column is None:
                previous = table[row_index - 2] if row_index >= 2 else []
                combined = [_normalize(cell) for cell in [*previous, *row]]
                if not any(("test item" in cell or cell == "test") for cell in combined):
                    continue
                item_column = item_column if item_column is not None else 0
                section_column = section_column if section_column is not None else 1
            return _Header(
                row_index=row_index,
                item_column=item_column,
                section_column=section_column,
                group_columns=group_columns,
            )
        return None

    def _parse_table(
        self,
        table: list[list[str]],
        table_index: int,
        header: _Header,
        marker_notes: dict[str, str],
        row_details: dict[str, MatrixRowDetailExtraction],
    ) -> MatrixParseResult:
        """Extract Matrix groups from one table."""
        group_steps: dict[str, list[MatrixStepPreview]] = {
            label: [] for _, label in header.group_columns
        }
        group_sample_size: dict[str, int | None] = {label: None for _, label in header.group_columns}
        group_sample_expression: dict[str, str | None] = {label: None for _, label in header.group_columns}
        group_sample_note: dict[str, str | None] = {label: None for _, label in header.group_columns}
        source_rows: list[MatrixRowPreview] = []
        warnings: list[str] = []
        for row_index, row in enumerate(table[header.row_index :], start=header.row_index + 1):
            test_item = _cell(row, header.item_column)
            if not test_item or _looks_like_note_or_footer(test_item):
                continue
            source_section = _cell(row, header.section_column) if header.section_column is not None else None
            row_detail = _row_detail_for_section(source_section, row_details)
            is_sample_row = _looks_like_sample_row(test_item, source_section, self._SAMPLE_ROW_RE)
            row_item_section_note = _row_item_section_note(test_item, source_section, marker_notes)
            row_tokens: dict[str, str] = {}
            for column, group_label in header.group_columns:
                cell_value = _cell(row, column)
                row_tokens[group_label] = cell_value or ""
                if not cell_value:
                    continue
                if is_sample_row:
                    group_sample_expression[group_label] = cell_value
                    group_sample_size[group_label] = _sample_size_value(cell_value)
                    marker = _extract_marker(cell_value)
                    if marker:
                        group_sample_note[group_label] = marker_notes.get(marker)
                    continue
                parsed_tokens, token_warnings = _parse_step_tokens(cell_value)
                for warning in token_warnings:
                    warnings.append(f"Table {table_index} row {row_index} {group_label}: {warning}")
                for token in parsed_tokens:
                    marker = _extract_marker(token["raw_token"])
                    group_steps[group_label].append(
                        MatrixStepPreview(
                            sequence=token["sequence"],
                            raw_token=token["raw_token"],
                            suffix_note=token["suffix"],
                            test_item=test_item,
                            source_section=source_section,
                            source_note=marker_notes.get(marker) if marker else None,
                            source_note_origin="step" if marker and marker_notes.get(marker) else None,
                            source_item_section_note=row_item_section_note,
                            source_table_index=table_index,
                            source_row_index=row_index,
                            duration_status="deferred",
                            warnings=tuple(token_warnings),
                        )
                    )
            source_rows.append(
                MatrixRowPreview(
                    source_row_index=row_index,
                    test_item=test_item,
                    source_section=source_section,
                    group_tokens=row_tokens,
                    is_sample_row=is_sample_row,
                    method=row_detail.method if row_detail else None,
                    condition=row_detail.condition if row_detail else None,
                    requirement=row_detail.requirement if row_detail else None,
                    detail_extraction_status=row_detail.status if row_detail else None,
                    detail_extraction_source_section=row_detail.source_section if row_detail else None,
                    detail_extraction_notes=row_detail.notes if row_detail else (),
                )
            )
        groups = tuple(
            _build_group(
                label,
                table_index,
                steps,
                group_sample_size.get(label),
                group_sample_expression.get(label),
                group_sample_note.get(label),
            )
            for label, steps in group_steps.items()
            if steps
        )
        if not groups:
            return MatrixParseResult(
                groups=(),
                warnings=tuple(warnings),
                blockers=(f"Matrix table {table_index} contains no group sequences.",),
                rows=tuple(source_rows),
            )
        duplicate_warnings = _duplicate_sequence_warnings(groups)
        return MatrixParseResult(
            groups=groups,
            warnings=tuple([*warnings, *duplicate_warnings]),
            selected_table_index=table_index,
            rows=tuple(source_rows),
        )


def _build_group(
    label: str,
    table_index: int,
    steps: list[MatrixStepPreview],
    sample_size: int | None,
    sample_quantity_expression: str | None,
    sample_note: str | None,
) -> MatrixGroupPreview:
    """Build one sorted group preview with duplicate-preserving steps."""
    sorted_steps = tuple(
        sorted(steps, key=lambda step: (step.sequence, step.source_row_index, step.test_item))
    )
    status = "extracted" if sorted_steps else "blocked"
    return MatrixGroupPreview(
        group_key=_group_key(label),
        group_label=label,
        source_table_index=table_index,
        extraction_status=status,
        sample_size=sample_size,
        sample_quantity_expression=sample_quantity_expression,
        sample_note=sample_note,
        steps=sorted_steps,
    )


def _row_detail_for_section(
    source_section: str | None,
    row_details: dict[str, MatrixRowDetailExtraction],
) -> MatrixRowDetailExtraction | None:
    """Return row-level extracted details for one Matrix section cell."""
    section = (source_section or "").strip()
    if not section:
        return None
    first_detail: MatrixRowDetailExtraction | None = None
    for candidate in _section_candidates(section):
        detail = row_details.get(candidate)
        if not detail:
            continue
        first_detail = first_detail or detail
        if detail.method or detail.condition or detail.requirement:
            return detail
    return first_detail


def _section_candidates(source_section: str) -> tuple[str, ...]:
    matches = re.findall(r"\d+(?:\.\d+)+", source_section)
    if not matches:
        return (source_section,)
    candidates: list[str] = []
    for match in matches:
        if match not in candidates:
            candidates.append(match)
    return tuple(candidates)


def _duplicate_sequence_warnings(groups: tuple[MatrixGroupPreview, ...]) -> list[str]:
    """Return warnings for duplicate step numbers within a group."""
    warnings: list[str] = []
    for group in groups:
        seen: set[int] = set()
        duplicates: set[int] = set()
        for step in group.steps:
            if step.sequence in seen:
                duplicates.add(step.sequence)
            seen.add(step.sequence)
        for sequence in sorted(duplicates):
            warnings.append(f"{group.group_label} has duplicate sequence {sequence}.")
    return warnings


def _parse_step_tokens(
    value: str,
) -> tuple[tuple[dict[str, int | str | None], ...], tuple[str, ...]]:
    """Parse matrix step tokens preserving raw token and suffix."""
    warnings: list[str] = []
    tokens: list[dict[str, int | str | None]] = []
    normalized = value.replace("，", ",").replace(";", ",").replace("\n", ",")
    for token in (part.strip() for part in normalized.split(",")):
        if not token:
            continue
        match = ProductSpecMatrixParser._STEP_TOKEN_RE.match(token)
        if match is None:
            warnings.append(f"Unrecognized sequence token '{token}'.")
            continue
        number = match.group("number")
        suffix = match.group("suffix").strip() or None
        tokens.append({"sequence": int(number), "raw_token": token, "suffix": suffix})
    return tuple(tokens), tuple(warnings)


def _sample_size_value(text: str | None) -> int | None:
    """Parse sample quantity as integer when possible."""
    if not text:
        return None
    match = re.match(r"^\s*(\d+)\s*$", text)
    if match:
        return int(match.group(1))
    return None


def _find_column(row: list[str], candidates: tuple[str, ...]) -> int | None:
    """Return the first column whose normalized text contains a candidate."""
    for index, value in enumerate(row):
        if any(candidate in value for candidate in candidates):
            return index
    return None


def _cell(row: list[str], index: int | None) -> str | None:
    """Return a cleaned cell value by index."""
    if index is None or index >= len(row):
        return None
    value = _clean(row[index])
    return value or None


def _clean(value: str) -> str:
    """Normalize table cell whitespace."""
    return re.sub(r"\s+", " ", str(value).replace("\x07", " ")).strip()


def _normalize(value: str) -> str:
    """Normalize text for header matching."""
    return _clean(value).lower()


def _group_key(label: str) -> str:
    """Create a stable key for one Matrix group label."""
    normalized = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    return normalized or "group"


def _looks_like_note_or_footer(value: str) -> bool:
    """Return true for note/footer rows that are not test items."""
    normalized = _normalize(value)
    return normalized.startswith(("applicable cable", "note", "rev", "©", "copyright"))


def _looks_like_sample_row(
    test_item: str | None,
    source_section: str | None,
    sample_row_re: re.Pattern[str],
) -> bool:
    """Identify sample quantity/size rows that should not be treated as step rows."""
    item = (test_item or "").strip()
    if not item:
        return False
    if sample_row_re.search(item) is None:
        return False
    section = (source_section or "").strip()
    if not section:
        return True
    return ProductSpecMatrixParser._SECTION_STEP_LIKE_RE.match(section) is None
