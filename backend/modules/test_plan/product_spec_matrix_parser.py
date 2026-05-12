"""Deterministic parser for product specification Matrix tables."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class MatrixStepPreview:
    """One test step extracted from a Matrix group column."""

    sequence: int
    test_item: str
    source_section: str | None
    source_table_index: int
    source_row_index: int
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


@dataclass(frozen=True, slots=True)
class MatrixParseResult:
    """Read-only Matrix extraction result."""

    groups: tuple[MatrixGroupPreview, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)
    blockers: tuple[str, ...] = field(default_factory=tuple)
    selected_table_index: int | None = None


@dataclass(frozen=True, slots=True)
class _Header:
    row_index: int
    item_column: int
    section_column: int | None
    group_columns: tuple[tuple[int, str], ...]


class ProductSpecMatrixParser:
    """Extract group sequences from Matrix-like product specification tables."""

    _GROUP_RE = re.compile(r"\bgroup\s*(\d+)\b", re.IGNORECASE)

    def parse_tables(self, tables: list[list[list[str]]]) -> MatrixParseResult:
        """Parse the first supported Matrix-like table from document tables."""
        warnings: list[str] = []
        for table_index, table in enumerate(tables, start=1):
            header = self._find_header(table)
            if header is None:
                continue
            result = self._parse_table(table, table_index, header)
            return MatrixParseResult(
                groups=result.groups,
                warnings=tuple([*warnings, *result.warnings]),
                blockers=result.blockers,
                selected_table_index=table_index,
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
                if self._GROUP_RE.search(value)
            )
            if not group_columns:
                continue
            item_column = _find_column(normalized, ("test items", "test item"))
            section_column = _find_column(normalized, ("section",))
            if item_column is None or section_column is None:
                previous = table[row_index - 2] if row_index >= 2 else []
                combined = [_normalize(cell) for cell in [*previous, *row]]
                if not any("test item" in cell for cell in combined):
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
    ) -> MatrixParseResult:
        """Extract Matrix groups from one table."""
        group_steps: dict[str, list[MatrixStepPreview]] = {
            label: [] for _, label in header.group_columns
        }
        warnings: list[str] = []
        for row_index, row in enumerate(table[header.row_index :], start=header.row_index + 1):
            test_item = _cell(row, header.item_column)
            if not test_item or _looks_like_note_or_footer(test_item):
                continue
            source_section = _cell(row, header.section_column) if header.section_column is not None else None
            for column, group_label in header.group_columns:
                sequence_text = _cell(row, column)
                if not sequence_text:
                    continue
                parsed_sequences, sequence_warnings = _parse_sequences(sequence_text)
                for warning in sequence_warnings:
                    warnings.append(
                        f"Table {table_index} row {row_index} {group_label}: {warning}"
                    )
                for sequence in parsed_sequences:
                    group_steps[group_label].append(
                        MatrixStepPreview(
                            sequence=sequence,
                            test_item=test_item,
                            source_section=source_section,
                            source_table_index=table_index,
                            source_row_index=row_index,
                            duration_status="deferred",
                            warnings=tuple(sequence_warnings),
                        )
                    )
        groups = tuple(
            _build_group(label, table_index, steps)
            for label, steps in group_steps.items()
            if steps
        )
        if not groups:
            return MatrixParseResult(
                groups=(),
                warnings=tuple(warnings),
                blockers=(f"Matrix table {table_index} contains no group sequences.",),
            )
        duplicate_warnings = _duplicate_sequence_warnings(groups)
        return MatrixParseResult(
            groups=groups,
            warnings=tuple([*warnings, *duplicate_warnings]),
            selected_table_index=table_index,
        )


def _build_group(
    label: str,
    table_index: int,
    steps: list[MatrixStepPreview],
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


def _parse_sequences(value: str) -> tuple[tuple[int, ...], tuple[str, ...]]:
    """Parse comma-separated Matrix sequence values."""
    warnings: list[str] = []
    sequences: list[int] = []
    normalized = value.replace("，", ",").replace(";", ",").replace("\n", ",")
    for token in (part.strip() for part in normalized.split(",")):
        if not token:
            continue
        if not token.isdigit():
            warnings.append(f"Unrecognized sequence token '{token}'.")
            continue
        sequences.append(int(token))
    return tuple(sequences), tuple(warnings)


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
