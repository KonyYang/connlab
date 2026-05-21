"""Deterministic parser for product specification Matrix tables."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


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
    _MARKER_IN_PAREN_RE = re.compile(r"\((?:\d*\s*)?([a-z])\)", re.IGNORECASE)
    _SYMBOL_MARKER_RE = re.compile(r"([*#])")
    _SAMPLE_ROW_RE = re.compile(r"\bsamples?\b", re.IGNORECASE)
    _SECTION_STEP_LIKE_RE = re.compile(r"^\s*\d+(\.\d+)*\s*$")
    _LETTER_NOTE_RE = re.compile(r"^\s*\(([a-z])\)\s*(.+)\s*$", re.IGNORECASE)
    _LETTER_NOTE_ALT_PAREN_RE = re.compile(r"^\s*（([a-z])）\s*(.+)\s*$", re.IGNORECASE)
    _LETTER_NOTE_SUFFIX_DELIM_RE = re.compile(r"^\s*([a-z])[)\.]\s*(.+)\s*$", re.IGNORECASE)
    _NOTE_WRAPPED_LETTER_RE = re.compile(r"^\s*note\s*\(([a-z])\)\s*[:：]?\s*(.+)\s*$", re.IGNORECASE)
    _SYMBOL_NOTE_RE = re.compile(r"^\s*([*#])\s*(.+)\s*$")

    def parse_tables(
        self,
        tables: list[list[list[str]]],
        paragraphs: list[str] | None = None,
        selected_table_index: int | None = None,
    ) -> MatrixParseResult:
        """Parse the first supported Matrix-like table from document tables."""
        warnings: list[str] = []
        marker_notes = _collect_marker_notes(paragraphs or [])
        best_result: MatrixParseResult | None = None
        best_score = -1
        for table_index, table in enumerate(tables, start=1):
            if selected_table_index is not None and table_index != selected_table_index:
                continue
            header = self._find_header(table)
            if header is None:
                continue
            result = self._parse_table(table, table_index, header, marker_notes)
            score = _table_score(result.groups)
            if score > best_score:
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


def _collect_marker_notes(paragraphs: list[str]) -> dict[str, str]:
    """Collect marker notes from the most plausible contiguous note block."""
    note_blocks = [
        *_collect_marker_note_blocks(paragraphs),
        *_collect_backfilled_letter_note_blocks(paragraphs),
    ]
    if not note_blocks:
        return _collect_marker_notes_global(paragraphs)
    # Prefer the last valid contiguous marker block, which most often matches
    # the matrix-adjacent footer note area in product specs.
    return note_blocks[-1]


def _collect_marker_note_blocks(paragraphs: list[str]) -> list[dict[str, str]]:
    """Collect contiguous marker-note blocks from paragraphs in reading order."""
    blocks: list[dict[str, str]] = []
    current_block: dict[str, str] = {}
    current_marker_count = 0

    for raw in paragraphs:
        text = _clean(raw)
        if not text:
            if current_marker_count >= 2:
                blocks.append(current_block)
            current_block = {}
            current_marker_count = 0
            continue

        parsed = _parse_marker_note_line(text)
        if parsed is None:
            if current_marker_count >= 2:
                blocks.append(current_block)
            current_block = {}
            current_marker_count = 0
            continue

        marker, normalized_note = parsed
        current_block[marker] = normalized_note
        current_marker_count += 1

    if current_marker_count >= 2:
        blocks.append(current_block)
    return blocks


def _collect_backfilled_letter_note_blocks(paragraphs: list[str]) -> list[dict[str, str]]:
    """Recover Word list-label notes when python-docx drops earlier labels."""
    blocks: list[dict[str, str]] = []
    cleaned = [_clean(raw) for raw in paragraphs]
    for index, text in enumerate(cleaned):
        parsed = _parse_marker_note_line(text)
        if parsed is None:
            continue
        marker, normalized_note = parsed
        if len(marker) != 1 or not marker.isalpha():
            continue
        marker_index = ord(marker.lower()) - ord("a")
        if marker_index <= 0:
            continue
        start = index - marker_index
        if start < 0:
            continue
        previous_lines = cleaned[start:index]
        if len(previous_lines) != marker_index:
            continue
        if any(not line or _parse_marker_note_line(line) is not None for line in previous_lines):
            continue
        if not _looks_like_matrix_note_backfill_context(cleaned, start):
            continue
        block = {
            chr(ord("a") + offset): f"({chr(ord('a') + offset)}) {line.strip()}"
            for offset, line in enumerate(previous_lines)
        }
        block[marker.lower()] = normalized_note
        blocks.append(block)
    return blocks


def _looks_like_matrix_note_backfill_context(paragraphs: list[str], start: int) -> bool:
    """Return true when unlabeled note lines follow a matrix/table caption."""
    context_start = max(0, start - 3)
    context = " ".join(paragraphs[context_start:start]).lower()
    return "table" in context and ("qualification" in context or "test" in context)


def _collect_marker_notes_global(paragraphs: list[str]) -> dict[str, str]:
    """Fallback global scan for sparse documents with isolated marker lines."""
    notes: dict[str, str] = {}
    for raw in paragraphs:
        text = _clean(raw)
        if not text:
            continue
        parsed = _parse_marker_note_line(text)
        if parsed is None:
            continue
        marker, normalized_note = parsed
        notes[marker] = normalized_note
    return notes


def _parse_marker_note_line(text: str) -> tuple[str, str] | None:
    """Parse one marker-note line into normalized (marker, note text)."""
    letter_match = ProductSpecMatrixParser._LETTER_NOTE_RE.match(text)
    if letter_match:
        marker = letter_match.group(1).lower()
        return marker, f"({marker}) {letter_match.group(2).strip()}"
    alt_paren_match = ProductSpecMatrixParser._LETTER_NOTE_ALT_PAREN_RE.match(text)
    if alt_paren_match:
        marker = alt_paren_match.group(1).lower()
        return marker, f"({marker}) {alt_paren_match.group(2).strip()}"
    suffix_delim_match = ProductSpecMatrixParser._LETTER_NOTE_SUFFIX_DELIM_RE.match(text)
    if suffix_delim_match:
        marker = suffix_delim_match.group(1).lower()
        return marker, f"({marker}) {suffix_delim_match.group(2).strip()}"
    note_wrapped_match = ProductSpecMatrixParser._NOTE_WRAPPED_LETTER_RE.match(text)
    if note_wrapped_match:
        marker = note_wrapped_match.group(1).lower()
        return marker, f"({marker}) {note_wrapped_match.group(2).strip()}"
    symbol_match = ProductSpecMatrixParser._SYMBOL_NOTE_RE.match(text)
    if symbol_match:
        marker = symbol_match.group(1)
        return marker, f"{marker} {symbol_match.group(2).strip()}"
    return None


def _extract_marker(token: str | None) -> str | None:
    """Extract a marker key from one token/value."""
    if not token:
        return None
    paren = ProductSpecMatrixParser._MARKER_IN_PAREN_RE.search(token)
    if paren:
        return paren.group(1).lower()
    symbol = ProductSpecMatrixParser._SYMBOL_MARKER_RE.search(token)
    if symbol:
        return symbol.group(1)
    return None


def _sample_size_value(text: str | None) -> int | None:
    """Parse sample quantity as integer when possible."""
    if not text:
        return None
    match = re.match(r"^\s*(\d+)\s*$", text)
    if match:
        return int(match.group(1))
    return None


def _row_item_section_note(
    test_item: str | None,
    source_section: str | None,
    marker_notes: dict[str, str],
) -> str | None:
    """Build concise item/section note text from row markers."""
    item_marker = _extract_marker(test_item)
    section_marker = _extract_marker(source_section)
    if section_marker and section_marker in marker_notes and source_section:
        return f"Section: {source_section} {_note_text_without_marker(marker_notes[section_marker])}".strip()
    if item_marker and item_marker in marker_notes and test_item:
        return f"Test Item: {test_item} {_note_text_without_marker(marker_notes[item_marker])}".strip()
    return None


def _table_score(groups: tuple[MatrixGroupPreview, ...]) -> int:
    """Score one parsed table for best candidate selection."""
    if not groups:
        return 0
    group_count = len(groups)
    step_count = sum(len(group.steps) for group in groups)
    return group_count * 1000 + step_count


def _note_text_without_marker(note: str) -> str:
    """Remove marker prefix so combined text does not duplicate symbols."""
    text = note.strip()
    text = re.sub(r"^\([a-z]\)\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^[*#]\s*", "", text)
    return text


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
    return normalized.startswith(("note", "rev", "©", "copyright"))


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
