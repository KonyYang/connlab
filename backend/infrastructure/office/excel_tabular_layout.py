"""Pure explicit-layout mapping shared by XLSX and legacy Excel readers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from backend.infrastructure.office.models import ExcelStructureProbeResult


class ExcelTabularLayoutError(ValueError):
    """Raised when an explicit worksheet layout does not match its contract."""


@dataclass(frozen=True, slots=True)
class ExcelTabularLayout:
    """One fixed worksheet header/data layout."""

    header_row_number: int
    required_header_columns: tuple[tuple[str, int], ...]
    optional_headers: tuple[str, ...] = ()
    include_row_number: bool = False
    require_unique_sheet_match: bool = False

    def __post_init__(self) -> None:
        if self.header_row_number < 1:
            raise ValueError("header_row_number must be positive.")
        if any(column < 1 for _header, column in self.required_header_columns):
            raise ValueError("Header columns must be positive.")


def map_explicit_layout_rows(
    rows: list[list[str]],
    *,
    sheet_name: str,
    layout: ExcelTabularLayout,
) -> tuple[tuple[str, ...], tuple[dict[str, str], ...]]:
    """Map rows using an exact physical header row and required column positions."""
    header_index = layout.header_row_number - 1
    if header_index >= len(rows):
        raise ExcelTabularLayoutError(
            f"Worksheet {sheet_name!r} does not contain header row "
            f"{layout.header_row_number}."
        )
    header_row = [value.strip() for value in rows[header_index]]
    required_indexes: dict[str, int] = {}
    for header, one_based_column in layout.required_header_columns:
        index = one_based_column - 1
        actual = header_row[index] if index < len(header_row) else ""
        if _normalize_header(actual) != _normalize_header(header):
            raise ExcelTabularLayoutError(
                f"Expected {header!r} at column {one_based_column} on row "
                f"{layout.header_row_number}."
            )
        required_indexes[header] = index
    normalized_headers = [_normalize_header(value) for value in header_row]
    optional_indexes: dict[str, int] = {}
    for header in layout.optional_headers:
        normalized = _normalize_header(header)
        if normalized in normalized_headers:
            optional_indexes[header] = normalized_headers.index(normalized)
    indexes = {**required_indexes, **optional_indexes}
    headers = tuple(indexes)
    mapped_rows: list[dict[str, str]] = []
    for zero_based_row, raw_row in enumerate(rows[header_index + 1 :], header_index + 1):
        mapped = {
            header: raw_row[index].strip() if index < len(raw_row) else ""
            for header, index in indexes.items()
        }
        if not any(mapped.values()):
            continue
        mapped["__sheet_name"] = sheet_name
        if layout.include_row_number:
            mapped["__row_number"] = str(zero_based_row + 1)
        mapped_rows.append(mapped)
    return headers, tuple(mapped_rows)


def normalized_sheet_name(value: str) -> str:
    """Normalize one configured sheet name for exact logical matching."""
    return re.sub(r"\s+", " ", value.strip()).casefold()


def matching_sheet_pairs(
    sheet_names: list[str],
    sheet_xml_paths: list[str],
    expected_sheet_names: tuple[str, ...],
    expected_sheet_name_patterns: tuple[str, ...],
    *,
    normalize_exact: bool = False,
) -> list[tuple[str, str]]:
    """Return sheet names and paths matching the configured rules."""
    if not expected_sheet_names and not expected_sheet_name_patterns:
        return list(zip(sheet_names, sheet_xml_paths, strict=True))
    exact = {
        normalized_sheet_name(name) if normalize_exact else name.lower()
        for name in expected_sheet_names
    }
    patterns = [
        re.compile(pattern, flags=re.IGNORECASE)
        for pattern in expected_sheet_name_patterns
    ]
    matched: list[tuple[str, str]] = []
    for sheet_name, sheet_xml_path in zip(sheet_names, sheet_xml_paths, strict=True):
        candidate = (
            normalized_sheet_name(sheet_name) if normalize_exact else sheet_name.lower()
        )
        if candidate in exact or any(
            pattern.fullmatch(sheet_name) for pattern in patterns
        ):
            matched.append((sheet_name, sheet_xml_path))
    return matched


def probe_explicit_xlsx_layout(
    path: Path,
    sheet_names: tuple[str, ...],
    matched_pairs: list[tuple[str, str]],
    shared_strings: list[str],
    expected_headers: tuple[str, ...],
    expected_date_headers: tuple[str, ...],
    layout: ExcelTabularLayout,
    read_rows: Callable[[Path, str, list[str]], list[list[str]]],
) -> ExcelStructureProbeResult:
    """Probe an explicit XLSX layout while preserving physical positions."""
    observed: tuple[str, ...] = ()
    matched_names: list[str] = []
    failure: str | None = None
    try:
        for sheet_name, sheet_xml_path in matched_pairs:
            rows = read_rows(path, sheet_xml_path, shared_strings)
            observed, mapped = map_explicit_layout_rows(
                rows, sheet_name=sheet_name, layout=layout
            )
            matched_names.append(sheet_name)
            if not mapped:
                failure = "Configured worksheet has no nonblank data rows."
    except ExcelTabularLayoutError as exc:
        failure = str(exc)
    return ExcelStructureProbeResult(
        workbook_path=path,
        sheet_names=sheet_names,
        matched_sheet_names=tuple(matched_names),
        observed_headers=observed,
        missing_headers=() if failure is None else expected_headers,
        missing_date_headers=() if failure is None else expected_date_headers,
        valid=failure is None,
        failure_reason=failure,
    )


def first_non_empty_row(rows: list[list[str]]) -> list[str]:
    """Return the first row with at least one non-empty value."""
    for row in rows:
        cleaned = [value.strip() for value in row if value.strip()]
        if cleaned:
            return cleaned
    return []


def normalize_header(value: str) -> str:
    """Normalize a workbook header for comparison."""
    return re.sub(r"\s+", " ", value.strip().lower())


def probe_failure(
    matched_pairs: list[tuple[str, str]],
    missing_headers: tuple[str, ...],
    missing_date_headers: tuple[str, ...],
) -> str | None:
    """Return a probe failure reason, or None when structure is acceptable."""
    if not matched_pairs:
        return "No worksheet matched the expected sheet rules."
    if missing_headers:
        return f"Missing required headers: {', '.join(missing_headers)}"
    if missing_date_headers:
        return f"Missing required date headers: {', '.join(missing_date_headers)}"
    return None


def header_index_map(
    header_row: list[str],
    normalized_canonical: list[str],
) -> tuple[int, ...] | None:
    """Return canonical header indexes for one sheet header row."""
    normalized_header = [normalize_header(value) for value in header_row]
    indexes: list[int] = []
    for normalized_name in normalized_canonical:
        try:
            indexes.append(normalized_header.index(normalized_name))
        except ValueError:
            return None
    return tuple(indexes)


def row_is_header(row: list[str], header_row: list[str]) -> bool:
    """Return whether a row equals the header row after trimming."""
    if len(row) < len(header_row):
        return False
    return all(
        row[index].strip() == header_row[index].strip()
        for index in range(len(header_row))
    )


def sheet_strategy(sheet_names: list[str]) -> str:
    """Describe the visible workbook sheet strategy."""
    if any(re.fullmatch(r"\d{4}", name) for name in sheet_names):
        return "year_sheets"
    if any(re.fullmatch(r"\d{4}[-_]\d{2}", name) for name in sheet_names):
        return "year_month_sheets"
    return "flat_or_unknown"


def _normalize_header(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()
