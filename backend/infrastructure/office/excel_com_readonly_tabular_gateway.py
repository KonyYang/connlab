"""Read legacy `.xls` tables through one owned read-only Excel COM session."""

from __future__ import annotations

import math
import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Protocol

from backend.infrastructure.office.models import ExcelStructureProbeResult
from backend.infrastructure.office.models import ExcelTabularReadResult
from backend.infrastructure.office.office_lifecycle import ExcelWorkbookHandle
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable

MAX_XLS_USED_RANGE_ROWS = 65_536
MAX_XLS_USED_RANGE_COLUMNS = 256
MAX_XLS_USED_RANGE_CELLS = 1_000_000


class ExternalExcelTabularGatewayError(ValueError):
    """Base error mapped by the existing external-resource API to HTTP 400."""


class UnsupportedExternalExcelTabularFormatError(ExternalExcelTabularGatewayError):
    """Raised for a file suffix outside the tabular read contract."""


class LegacyExcelComUnavailableError(ExternalExcelTabularGatewayError):
    """Raised when the Windows Excel COM runtime is unavailable."""


class LegacyExcelReadOnlyOpenError(ExternalExcelTabularGatewayError):
    """Raised when Excel cannot open a legacy workbook read-only."""


class LegacyExcelRangeError(ExternalExcelTabularGatewayError):
    """Raised before reading an invalid or oversized UsedRange."""


class LegacyExcelReadError(ExternalExcelTabularGatewayError):
    """Raised when a legacy workbook cannot be read deterministically."""


class LegacyExcelCleanupError(ExternalExcelTabularGatewayError):
    """Raised when a successful read cannot cleanly release Excel."""


class ExcelReadonlyLifecyclePort(Protocol):
    """Narrow lifecycle dependency used by the legacy tabular reader."""

    def open_excel_workbook(
        self,
        path: Path,
        modify_password: str | None = None,
        read_only: bool = False,
    ) -> ExcelWorkbookHandle: ...


class ExcelComReadonlyTabularGateway:
    """Read `.xls` worksheets without Save, conversion, or source mutation."""

    def __init__(self, lifecycle: ExcelReadonlyLifecyclePort) -> None:
        self._lifecycle = lifecycle

    def probe_structure(
        self,
        source_path: Path,
        *,
        expected_headers: tuple[str, ...],
        expected_date_headers: tuple[str, ...] = (),
        expected_sheet_names: tuple[str, ...] = (),
        expected_sheet_name_patterns: tuple[str, ...] = (),
    ) -> ExcelStructureProbeResult:
        path = self._validated_path(source_path)
        sheet_names, sheets = self._read_matching_sheets(
            path, expected_sheet_names, expected_sheet_name_patterns
        )
        observed: list[str] = []
        for _name, rows in sheets:
            observed.extend(_first_non_empty_row(rows))
        normalized = {_normalize_header(value) for value in observed}
        missing = tuple(
            value for value in expected_headers if _normalize_header(value) not in normalized
        )
        missing_dates = tuple(
            value
            for value in expected_date_headers
            if _normalize_header(value) not in normalized
        )
        failure = _probe_failure(sheets, missing, missing_dates)
        return ExcelStructureProbeResult(
            workbook_path=path,
            sheet_names=sheet_names,
            matched_sheet_names=tuple(name for name, _rows in sheets),
            observed_headers=tuple(dict.fromkeys(observed)),
            missing_headers=missing,
            missing_date_headers=missing_dates,
            valid=failure is None,
            failure_reason=failure,
        )

    def read_tabular_rows(
        self,
        source_path: Path,
        *,
        expected_headers: tuple[str, ...],
        expected_sheet_names: tuple[str, ...] = (),
        expected_sheet_name_patterns: tuple[str, ...] = (),
    ) -> ExcelTabularReadResult:
        path = self._validated_path(source_path)
        _sheet_names, sheets = self._read_matching_sheets(
            path, expected_sheet_names, expected_sheet_name_patterns
        )
        if not sheets:
            raise LegacyExcelReadError("No worksheet matched the expected sheet rules.")
        normalized_headers = [_normalize_header(value) for value in expected_headers]
        matched: list[str] = []
        collected: list[dict[str, str]] = []
        for sheet_name, rows in sheets:
            header_row = _first_non_empty_row(rows)
            index_map = _header_index_map(header_row, normalized_headers)
            if index_map is None:
                continue
            matched.append(sheet_name)
            for row in rows:
                if not any(row) or _row_is_header(row, header_row):
                    continue
                mapped = {
                    header: row[index] if index < len(row) else ""
                    for header, index in zip(expected_headers, index_map, strict=True)
                }
                if any(mapped.values()):
                    mapped["__sheet_name"] = sheet_name
                    collected.append(mapped)
        if not matched:
            raise LegacyExcelReadError("Expected headers were not found.")
        return ExcelTabularReadResult(
            workbook_path=path,
            matched_sheet_names=tuple(matched),
            headers=tuple(expected_headers),
            rows=tuple(collected),
        )

    def _validated_path(self, source_path: Path) -> Path:
        path = Path(source_path)
        if not path.is_file():
            raise FileNotFoundError(f"Excel workbook does not exist: {path}")
        if path.suffix.lower() != ".xls":
            raise UnsupportedExternalExcelTabularFormatError(
                f"Expected a legacy Excel file (.xls): {path}"
            )
        return path

    def _read_matching_sheets(
        self,
        path: Path,
        expected_names: tuple[str, ...],
        expected_patterns: tuple[str, ...],
    ) -> tuple[tuple[str, ...], list[tuple[str, list[list[str]]]]]:
        try:
            handle = self._lifecycle.open_excel_workbook(
                path, modify_password=None, read_only=True
            )
        except OfficeAutomationUnavailable as exc:
            raise LegacyExcelComUnavailableError(
                "Legacy .xls reading requires Microsoft Excel COM and pywin32 on Windows."
            ) from exc
        except Exception as exc:
            raise LegacyExcelReadOnlyOpenError(
                f"Unable to open legacy .xls workbook read-only: {_summary(exc)}"
            ) from exc

        try:
            result = _read_workbook_sheets(
                handle.workbook, expected_names, expected_patterns
            )
        except ExternalExcelTabularGatewayError as primary:
            _close_after_primary(handle, primary)
            raise
        except Exception as exc:
            primary = LegacyExcelReadError(
                f"Unable to read legacy .xls workbook: {_summary(exc)}"
            )
            _close_after_primary(handle, primary)
            raise primary from exc
        try:
            handle.close(save_changes=False)
        except Exception as exc:
            raise LegacyExcelCleanupError(
                f"Legacy .xls read completed but cleanup failed: {_summary(exc)}"
            ) from exc
        return result


def _read_workbook_sheets(
    workbook: object,
    expected_names: tuple[str, ...],
    expected_patterns: tuple[str, ...],
) -> tuple[tuple[str, ...], list[tuple[str, list[list[str]]]]]:
    worksheets = workbook.Worksheets
    count = _count_value(worksheets.Count, "worksheet")
    exact = {name.lower() for name in expected_names}
    patterns = [re.compile(value, re.IGNORECASE) for value in expected_patterns]
    names: list[str] = []
    matched: list[tuple[str, list[list[str]]]] = []
    for index in range(1, count + 1):
        sheet = worksheets.Item(index)
        name = str(sheet.Name)
        names.append(name)
        selected = not exact and not patterns
        selected = selected or name.lower() in exact
        selected = selected or any(pattern.fullmatch(name) for pattern in patterns)
        if selected:
            matched.append((name, _read_used_range(sheet, name)))
        sheet = None
    worksheets = None
    return tuple(names), matched


def _read_used_range(sheet: object, sheet_name: str) -> list[list[str]]:
    used_range = sheet.UsedRange
    rows = _count_value(used_range.Rows.Count, "row")
    columns = _count_value(used_range.Columns.Count, "column")
    if rows > MAX_XLS_USED_RANGE_ROWS:
        raise LegacyExcelRangeError(f"Worksheet {sheet_name!r} exceeds 65,536 rows.")
    if columns > MAX_XLS_USED_RANGE_COLUMNS:
        raise LegacyExcelRangeError(f"Worksheet {sheet_name!r} exceeds 256 columns.")
    if rows * columns > MAX_XLS_USED_RANGE_CELLS:
        raise LegacyExcelRangeError(f"Worksheet {sheet_name!r} exceeds 1,000,000 cells.")
    if rows == 0 or columns == 0:
        return []
    try:
        raw = used_range.Value
    except Exception as exc:
        if not _is_com_read_compatibility_error(exc):
            raise LegacyExcelReadError(
                f"Unable to read worksheet {sheet_name!r} UsedRange.Value: "
                f"{_summary(exc)}"
            ) from exc
        try:
            raw = used_range.Value2
        except Exception as fallback_error:
            raise LegacyExcelReadError(
                f"Unable to read worksheet {sheet_name!r} UsedRange.Value2: "
                f"{_summary(fallback_error)}"
            ) from fallback_error
    matrix = _coerce_matrix(raw, rows, columns)
    raw = None
    used_range = None
    return [
        [_cell_text(value, sheet_name, row_index, column_index) for column_index, value in enumerate(row, 1)]
        for row_index, row in enumerate(matrix, 1)
    ]


def _count_value(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise LegacyExcelRangeError(f"Invalid Excel UsedRange {label} count: {value!r}")
    return value


def _coerce_matrix(raw: object, rows: int, columns: int) -> tuple[tuple[object, ...], ...]:
    if rows == 1 and columns == 1 and not _sequence(raw):
        return ((raw,),)
    if not _sequence(raw):
        raise LegacyExcelReadError("Excel UsedRange value shape does not match its dimensions.")
    outer = tuple(raw)  # type: ignore[arg-type]
    if len(outer) == rows and all(_sequence(value) for value in outer):
        matrix = tuple(tuple(value) for value in outer)  # type: ignore[arg-type]
    elif rows == 1 and len(outer) == columns:
        matrix = (outer,)
    elif columns == 1 and len(outer) == rows:
        matrix = tuple((value,) for value in outer)
    else:
        raise LegacyExcelReadError("Excel UsedRange value shape does not match its dimensions.")
    if any(len(row) != columns for row in matrix):
        raise LegacyExcelReadError("Excel UsedRange value shape does not match its dimensions.")
    return matrix


def _sequence(value: object) -> bool:
    return isinstance(value, (tuple, list))


def _is_com_read_compatibility_error(exc: Exception) -> bool:
    """Recognize pywin32 COM read errors without importing the optional runtime."""
    error_type = type(exc)
    return error_type.__module__ == "pywintypes" and error_type.__name__ == "com_error"


def _cell_text(value: object, sheet: str, row: int, column: int) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, datetime):
        return value.isoformat(timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, (float, Decimal)):
        if not math.isfinite(float(value)):
            raise LegacyExcelReadError(
                f"Unsupported value at {sheet}!R{row}C{column}: non-finite number."
            )
        text = format(Decimal(str(value)), "f")
        return text.rstrip("0").rstrip(".") if "." in text else text
    raise LegacyExcelReadError(
        f"Unsupported value at {sheet}!R{row}C{column}: {type(value).__name__}."
    )


def _first_non_empty_row(rows: list[list[str]]) -> list[str]:
    for row in rows:
        cleaned = [value.strip() for value in row if value.strip()]
        if cleaned:
            return cleaned
    return []


def _normalize_header(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _header_index_map(header_row: list[str], normalized: list[str]) -> list[int] | None:
    available = [_normalize_header(value) for value in header_row]
    try:
        return [available.index(value) for value in normalized]
    except ValueError:
        return None


def _row_is_header(row: list[str], header_row: list[str]) -> bool:
    return [_normalize_header(value) for value in row[: len(header_row)]] == [
        _normalize_header(value) for value in header_row
    ]


def _probe_failure(
    sheets: list[tuple[str, list[list[str]]]],
    missing: tuple[str, ...],
    missing_dates: tuple[str, ...],
) -> str | None:
    if not sheets:
        return "No worksheet matched the expected sheet rules."
    if missing:
        return f"Missing required headers: {', '.join(missing)}"
    if missing_dates:
        return f"Missing required date headers: {', '.join(missing_dates)}"
    return None


def _close_after_primary(handle: ExcelWorkbookHandle, primary: Exception) -> None:
    try:
        handle.close(save_changes=False)
    except Exception as cleanup_error:
        primary.add_note(f"Cleanup warning: {_summary(cleanup_error)}")


def _summary(exc: Exception) -> str:
    return (" ".join(str(exc).split()) or exc.__class__.__name__)[:240]
