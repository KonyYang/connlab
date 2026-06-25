"""Excel COM LTR workbook write gateway."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from pathlib import Path

from backend.infrastructure.office.office_facade import OfficeFacade
from backend.modules.ltr import next_monthly_dl_number, parse_ltr_number


class LtrWorkbookWriteError(RuntimeError):
    """Raised when an LTR workbook write operation cannot proceed."""


class LtrWorkbookWriteDisabledError(LtrWorkbookWriteError):
    """Raised when workbook write is disabled by configuration."""


class LtrWorkbookReadOnlyError(LtrWorkbookWriteError):
    """Raised when Excel opens the workbook read-only."""


@dataclass(frozen=True, slots=True)
class LtrWorkbookWriteConfig:
    """Configuration required for an LTR workbook write session."""

    path: Path | None
    write_enabled: bool = False
    modify_password: str | None = None


@dataclass(frozen=True, slots=True)
class LtrWorkbookRowData:
    """One row of LTR workbook registration data for columns A:Q."""

    month: str
    total: int
    monthly_number: int
    dl_number: str
    project_type: str | None = None
    description_pn: str | None = None
    test_item: str | None = None
    test_type: str | None = None
    requested_by: str | None = None
    location: str | None = None
    project_leader: str | None = None
    test_result: str | None = None
    failed_item: str | None = None
    sample_deposition: str | None = None
    sub_contract: str | None = None
    test_fee: str | None = None
    remarks_po: str | None = None

    def as_excel_row(self) -> list[object]:
        """Return values ordered for columns A:Q."""
        return [
            self.month,
            self.total,
            self.monthly_number,
            self.dl_number,
            self.project_type,
            self.description_pn,
            self.test_item,
            self.test_type,
            self.requested_by,
            self.location,
            self.project_leader,
            self.test_result,
            self.failed_item,
            self.sample_deposition,
            self.sub_contract,
            self.test_fee,
            self.remarks_po,
        ]


@dataclass(frozen=True, slots=True)
class LtrWorkbookRowPointer:
    """Pointer to a written workbook row."""

    sheet_name: str
    row_number: int
    dl_number: str


@dataclass(frozen=True, slots=True)
class LtrWorkbookExistingRow:
    """Existing workbook row located by DL number."""

    sheet_name: str
    row_number: int
    dl_number: str
    values: tuple[object, ...]


@dataclass(frozen=True, slots=True)
class LtrWorkbookDropdownEnsureResult:
    """Result of ensuring one workbook dropdown list contains a value."""

    appended: bool
    appended_value: str | None
    source_range_before: str
    source_range_after: str


@dataclass(frozen=True, slots=True)
class LtrWorkbookSheetPreparationResult:
    """Result of preparing one workbook sheet for operation."""

    sheet_name: str
    mode: str
    filter_cleared: bool
    hidden_rows_detected: bool
    hidden_columns_detected: bool
    warnings: tuple[str, ...] = ()


class ExcelComLTRWorkbookGateway:
    """Open `.xls` LTR workbooks through OfficeFacade and Excel COM."""

    def __init__(
        self,
        office: OfficeFacade,
        config: LtrWorkbookWriteConfig,
    ) -> None:
        """Create the gateway."""
        self._office = office
        self._config = config

    def open_write_session(self) -> "ExcelComLTRWorkbookWriteSession":
        """Open a write session through the Office facade."""
        if not self._config.write_enabled:
            raise LtrWorkbookWriteDisabledError("LTR workbook write is disabled.")
        if self._config.path is None:
            raise LtrWorkbookWriteError("LTR workbook path is not configured.")
        if not self._config.modify_password:
            raise LtrWorkbookWriteError("LTR workbook modify password is not configured.")

        try:
            handle = self._office.open_excel_workbook(
                self._config.path,
                modify_password=self._config.modify_password,
                read_only=False,
            )
        except Exception as exc:
            raise LtrWorkbookWriteError(
                "Unable to open LTR workbook with modify permission. "
                "Check workbook path, modify password, and Excel file lock state. "
                f"Excel error: {_exception_summary(exc)}"
            ) from exc
        return ExcelComLTRWorkbookWriteSession(handle)

    def open_read_session(self) -> "ExcelComLTRWorkbookReadSession":
        """Open a read-only session through the Office facade."""
        if self._config.path is None:
            raise LtrWorkbookWriteError("LTR workbook path is not configured.")

        try:
            handle = self._office.open_excel_workbook(
                self._config.path,
                modify_password=None,
                read_only=True,
            )
        except Exception as exc:
            raise LtrWorkbookWriteError(
                "Unable to open LTR workbook for preview. "
                "Check workbook path and Excel file lock state. "
                f"Excel error: {_exception_summary(exc)}"
            ) from exc
        return ExcelComLTRWorkbookReadSession(handle)


class ExcelComLTRWorkbookWriteSession:
    """Context-manager write session for one LTR workbook transaction."""

    def __init__(self, handle) -> None:
        """Create a write session from an OfficeFacade workbook handle."""
        self._handle = handle
        self._closed = False

    def __enter__(self) -> "ExcelComLTRWorkbookWriteSession":
        try:
            self.assert_not_read_only()
        except Exception:
            self.close(save_changes=False)
            raise
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close(save_changes=False)

    def assert_not_read_only(self) -> None:
        """Block write operations if Excel opened the workbook read-only."""
        if bool(getattr(self._handle.workbook, "ReadOnly", False)):
            raise LtrWorkbookReadOnlyError(
                "LTR workbook opened read-only; check password or file lock."
            )

    def list_sheets(self) -> list[str]:
        """Return workbook sheet names."""
        return [sheet.Name for sheet in self._handle.workbook.Worksheets]

    def read_annual_sheet(self, sheet_name: str) -> tuple[tuple[object, ...], ...]:
        """Read annual sheet A:Q data in one batch range call."""
        try:
            sheet = self._handle.workbook.Worksheets.Item(sheet_name)
            last_row = int(sheet.UsedRange.Rows.Count)
            if last_row < 2:
                return ()
            try:
                values = sheet.Range(f"A2:Q{last_row}").Value2
            except Exception:
                values = sheet.Range(f"A2:Q{last_row}").Value
        except Exception as exc:
            raise LtrWorkbookWriteError(
                f"Unable to read LTR workbook sheet {sheet_name}. "
                f"Excel error: {_exception_summary(exc)}"
            ) from exc
        return _tuple_rows(values)

    def read_ltr_number_column(self, sheet_name: str) -> tuple[str, ...]:
        """Read visible DL numbers from column D only."""
        try:
            sheet = self._handle.workbook.Worksheets.Item(sheet_name)
            last_row = int(sheet.UsedRange.Rows.Count)
            if last_row < 2:
                return ()
            try:
                values = sheet.Range(f"D2:D{last_row}").Value2
            except Exception:
                values = sheet.Range(f"D2:D{last_row}").Value
        except Exception as exc:
            raise LtrWorkbookWriteError(
                f"Unable to read LTR numbers from workbook sheet {sheet_name}. "
                f"Excel error: {_exception_summary(exc)}"
            ) from exc
        return tuple(
            str(value).strip().upper()
            for value in _tuple_column_values(values)
            if str(value or "").strip()
        )

    def read_ltr_number_cells(self, sheet_name: str) -> tuple[tuple[int, object], ...]:
        """Read column-D DL cells with worksheet row numbers."""
        try:
            sheet = self._handle.workbook.Worksheets.Item(sheet_name)
            last_row = int(sheet.UsedRange.Rows.Count)
            if last_row < 2:
                return ()
            try:
                values = sheet.Range(f"D2:D{last_row}").Value2
            except Exception:
                values = sheet.Range(f"D2:D{last_row}").Value
        except Exception as exc:
            raise LtrWorkbookWriteError(
                f"Unable to read LTR numbers from workbook sheet {sheet_name}. "
                f"Excel error: {_exception_summary(exc)}"
            ) from exc
        return tuple(
            (row_number, value)
            for row_number, value in enumerate(_tuple_column_values(values), start=2)
        )

    def read_ltr_number_cell(self, sheet_name: str, row_number: int) -> object:
        """Read one column-D DL cell."""
        if row_number < 2:
            raise LtrWorkbookWriteError("LTR workbook read row must be 2 or greater.")
        try:
            sheet = self._handle.workbook.Worksheets.Item(sheet_name)
            try:
                return sheet.Cells(row_number, 4).Value2
            except Exception:
                return sheet.Cells(row_number, 4).Value
        except Exception as exc:
            raise LtrWorkbookWriteError(
                f"Unable to read LTR cell from workbook sheet {sheet_name}. "
                f"Excel error: {_exception_summary(exc)}"
            ) from exc

    def read_registration_row(
        self,
        sheet_name: str,
        row_number: int,
    ) -> tuple[object, ...]:
        """Read one existing A:Q registration row."""
        if row_number < 2:
            raise LtrWorkbookWriteError("LTR workbook read row must be 2 or greater.")
        try:
            sheet = self._handle.workbook.Worksheets.Item(sheet_name)
            try:
                values = sheet.Range(f"A{row_number}:Q{row_number}").Value2
            except Exception:
                values = sheet.Range(f"A{row_number}:Q{row_number}").Value
        except Exception as exc:
            raise LtrWorkbookWriteError(
                f"Unable to read LTR workbook row {row_number} from sheet {sheet_name}. "
                f"Excel error: {_exception_summary(exc)}"
            ) from exc
        rows = _tuple_rows(values)
        return rows[0] if rows else ()

    def append_registration_row(
        self,
        sheet_name: str,
        row_data: LtrWorkbookRowData,
    ) -> LtrWorkbookRowPointer:
        """Append one registration row at the first empty LTR-number cell."""
        sheet = self._handle.workbook.Worksheets.Item(sheet_name)
        target_row = _first_blank_ltr_row(sheet)
        adjusted_row_data = replace(
            row_data,
            total=_next_total_before_row(sheet, target_row, row_data.total),
        )
        _prepare_month_cell(sheet, target_row, adjusted_row_data.month)
        sheet.Range(f"A{target_row}:Q{target_row}").Value = [
            adjusted_row_data.as_excel_row()
        ]
        _fit_description_pn_cell(sheet, target_row)
        _merge_adjacent_month_cells(sheet, target_row, adjusted_row_data.month)
        return LtrWorkbookRowPointer(
            sheet_name=sheet_name,
            row_number=target_row,
            dl_number=adjusted_row_data.dl_number,
        )

    def write_registration_row(
        self,
        sheet_name: str,
        row_number: int,
        row_data: LtrWorkbookRowData,
    ) -> LtrWorkbookRowPointer:
        """Write one registration row to an existing A:Q row."""
        if row_number < 2:
            raise LtrWorkbookWriteError("LTR workbook write row must be 2 or greater.")
        sheet = self._handle.workbook.Worksheets.Item(sheet_name)
        sheet.Range(f"A{row_number}:Q{row_number}").Value = [row_data.as_excel_row()]
        _fit_description_pn_cell(sheet, row_number)
        return LtrWorkbookRowPointer(
            sheet_name=sheet_name,
            row_number=row_number,
            dl_number=row_data.dl_number,
        )

    def bootstrap_year_sheet(
        self,
        target_sheet_name: str,
        *,
        template_sheet_name: str,
        clear_start_row: int = 2,
    ) -> bool:
        """Copy a template year sheet, rename it, and clear configured data rows."""
        if target_sheet_name in self.list_sheets():
            return False
        if clear_start_row < 2:
            raise LtrWorkbookWriteError(
                "Year sheet bootstrap clear_start_row must be 2 or greater."
            )
        workbook = self._handle.workbook
        try:
            template_sheet = workbook.Worksheets.Item(template_sheet_name)
        except Exception as exc:
            raise LtrWorkbookWriteError(
                f"Template sheet not found for year-sheet bootstrap: {template_sheet_name}"
            ) from exc
        template_sheet.Copy(After=workbook.Worksheets.Item(workbook.Worksheets.Count))
        created_sheet = workbook.Worksheets.Item(workbook.Worksheets.Count)
        created_sheet.Name = target_sheet_name
        self._clear_sheet_rows(created_sheet, clear_start_row)
        return True

    def find_ltr_number(
        self,
        ltr_number: str,
        sheet_names: tuple[str, ...] | None = None,
    ) -> LtrWorkbookExistingRow | None:
        """Return the first workbook row whose column D exactly matches the LTR number."""
        candidates = sheet_names or tuple(self.list_sheets())
        for sheet_name in candidates:
            for index, row in enumerate(self.read_annual_sheet(sheet_name), start=2):
                if len(row) >= 4 and str(row[3]).strip().upper() == ltr_number.upper():
                    return LtrWorkbookExistingRow(
                        sheet_name=sheet_name,
                        row_number=index,
                        dl_number=str(row[3]).strip().upper(),
                        values=row,
                    )
        return None

    def list_ltr_numbers(
        self,
        sheet_names: tuple[str, ...] | None = None,
    ) -> tuple[str, ...]:
        """Return visible LTR numbers from column D across selected sheets."""
        numbers: list[str] = []
        candidates = sheet_names or tuple(self.list_sheets())
        for sheet_name in candidates:
            numbers.extend(self.read_ltr_number_column(sheet_name))
        return tuple(dict.fromkeys(numbers))

    def append_next_normal_registration(
        self,
        sheet_name: str,
        year: int,
        month: int,
        row_data: LtrWorkbookRowData,
    ) -> LtrWorkbookRowPointer:
        """Calculate the final normal DL inside the write session and append it."""
        existing_numbers = [
            str(row[3])
            for row in self.read_annual_sheet(sheet_name)
            if len(row) >= 4 and row[3]
        ]
        final_number = next_monthly_dl_number(
            year=year,
            month=month,
            existing_numbers=existing_numbers,
        )
        parsed = parse_ltr_number(final_number)
        return self.append_registration_row(
            sheet_name,
            replace(
                row_data,
                monthly_number=parsed.sequence or row_data.monthly_number,
                dl_number=final_number,
            ),
        )

    def ensure_location_dropdown_value(
        self,
        sheet_name: str,
        location: str,
        *,
        row_number: int | None = None,
    ) -> LtrWorkbookDropdownEnsureResult:
        """Ensure J-column dropdown source list includes the given location."""
        text = str(location or "").strip()
        if not text:
            raise LtrWorkbookWriteError("Location is required.")
        sheet = self._handle.workbook.Worksheets.Item(sheet_name)
        target_row = row_number or max(_first_blank_ltr_row(sheet), 2)
        source, validation_cell = _dropdown_source_formula(sheet, target_row)
        source_values = _tuple_column_values(sheet.Range(source.address).Value2)
        normalized = _normalize_dropdown_text(text)
        exists = any(_normalize_dropdown_text(value) == normalized for value in source_values)
        if exists:
            return LtrWorkbookDropdownEnsureResult(
                appended=False,
                appended_value=None,
                source_range_before=source.formula,
                source_range_after=source.formula,
            )
        next_row = source.end_row + 1
        sheet.Cells(next_row, _column_index(source.column)).Value = text
        updated_formula = source.formula_for_end_row(next_row)
        _set_validation_formula(validation_cell, updated_formula)
        return LtrWorkbookDropdownEnsureResult(
            appended=True,
            appended_value=text,
            source_range_before=source.formula,
            source_range_after=updated_formula,
        )

    def prepare_sheet_for_operation(
        self,
        sheet_name: str,
        *,
        mode: str = "write",
    ) -> LtrWorkbookSheetPreparationResult:
        """Normalize filter/view state before read/write operations."""
        sheet = self._handle.workbook.Worksheets.Item(sheet_name)
        filter_cleared = _clear_sheet_filter(sheet)
        hidden_rows_detected = _unhide_sheet_rows(sheet)
        hidden_columns_detected = _unhide_sheet_columns(sheet)
        return LtrWorkbookSheetPreparationResult(
            sheet_name=sheet_name,
            mode=mode,
            filter_cleared=filter_cleared,
            hidden_rows_detected=hidden_rows_detected,
            hidden_columns_detected=hidden_columns_detected,
            warnings=(),
        )

    def save(self) -> None:
        """Save the workbook."""
        self._handle.save()

    def close(self, save_changes: bool = False) -> None:
        """Close the workbook handle once."""
        if self._closed:
            return
        self._closed = True
        self._handle.close(save_changes=save_changes)

    def _clear_sheet_rows(self, sheet, clear_start_row: int) -> None:
        """Clear A:Q data rows on a newly copied annual sheet."""
        last_row = int(sheet.UsedRange.Rows.Count)
        if last_row < clear_start_row:
            return
        sheet.Range(f"A{clear_start_row}:Q{last_row}").ClearContents()


class ExcelComLTRWorkbookReadSession(ExcelComLTRWorkbookWriteSession):
    """Read-only session for workbook preview operations."""

    def __enter__(self) -> "ExcelComLTRWorkbookReadSession":
        return self


def _tuple_rows(values) -> tuple[tuple[object, ...], ...]:
    """Normalize Excel range values to tuple rows."""
    if values is None:
        return ()
    if not isinstance(values, tuple):
        return ((values,),)
    if values and not isinstance(values[0], tuple):
        return (values,)
    return tuple(tuple(row) for row in values)


def _tuple_column_values(values) -> tuple[object, ...]:
    """Normalize a single-column Excel range to flat values."""
    if values is None:
        return ()
    if not isinstance(values, tuple):
        return (values,)
    if values and isinstance(values[0], tuple):
        return tuple(row[0] if row else None for row in values)
    return values


def _first_blank_ltr_row(sheet) -> int:
    """Return the first row whose LTR-number column is empty."""
    last_row = max(int(sheet.UsedRange.Rows.Count), 2)
    for row_number in range(2, last_row + 2):
        value = sheet.Cells(row_number, 4).Value
        if not str(value or "").strip():
            return row_number
    return last_row + 1


def _next_total_before_row(sheet, target_row: int, fallback_total: int) -> int:
    """Return the next annual total based on the previous occupied LTR row."""
    for row_number in range(target_row - 1, 1, -1):
        ltr_number = sheet.Cells(row_number, 4).Value
        if not str(ltr_number or "").strip():
            continue
        total = sheet.Cells(row_number, 2).Value
        try:
            return int(total) + 1
        except (TypeError, ValueError):
            return fallback_total
    return max(fallback_total, 1)


def _prepare_month_cell(sheet, target_row: int, month: str) -> None:
    """Split an existing month merge so the target row can carry its own month."""
    cell = sheet.Cells(target_row, 1)
    if not bool(getattr(cell, "MergeCells", False)):
        return
    merge_area = cell.MergeArea
    start_row = int(merge_area.Row)
    row_count = int(merge_area.Rows.Count)
    end_row = start_row + row_count - 1
    if row_count <= 1:
        return
    old_month = merge_area.Cells(1, 1).Value
    merge_area.UnMerge()
    _restore_month_merge(sheet, start_row, target_row - 1, old_month)
    _restore_month_merge(sheet, target_row + 1, end_row, old_month)
    sheet.Cells(target_row, 1).Value = month


def _restore_month_merge(sheet, start_row: int, end_row: int, value) -> None:
    """Restore one side of a split month merge."""
    if end_row < start_row:
        return
    target = sheet.Range(f"A{start_row}:A{end_row}")
    target.Value = value
    if end_row > start_row:
        target.Merge()


def _merge_adjacent_month_cells(sheet, target_row: int, month: str) -> None:
    """Merge the contiguous occupied rows that share the target month label."""
    start_row = target_row
    end_row = target_row
    while start_row > 2 and _occupied_row_month(sheet, start_row - 1) == month:
        start_row -= 1
    last_row = max(int(sheet.UsedRange.Rows.Count), target_row)
    while end_row < last_row and _occupied_row_month(sheet, end_row + 1) == month:
        end_row += 1
    if end_row <= start_row:
        sheet.Cells(target_row, 1).Value = month
        return
    target = sheet.Range(f"A{start_row}:A{end_row}")
    try:
        target.UnMerge()
    except Exception:
        pass
    target.Value = month
    target.Merge()


def _occupied_row_month(sheet, row_number: int) -> str | None:
    """Return a row's month label only when the LTR-number cell is occupied."""
    ltr_number = sheet.Cells(row_number, 4).Value
    if not str(ltr_number or "").strip():
        return None
    cell = sheet.Cells(row_number, 1)
    if bool(getattr(cell, "MergeCells", False)):
        value = cell.MergeArea.Cells(1, 1).Value
    else:
        value = cell.Value
    text = str(value or "").strip()
    return text or None


def _exception_summary(exc: Exception) -> str:
    """Return a compact exception summary safe for operator-facing diagnostics."""
    text = str(exc).strip()
    if not text:
        text = exc.__class__.__name__
    return text[:500]


@dataclass(frozen=True, slots=True)
class _DropdownSource:
    """Parsed dropdown source formula and range details."""

    formula: str
    column: str
    start_row: int
    end_row: int
    sheet_prefix: str = ""

    @property
    def address(self) -> str:
        return f"{self.column}{self.start_row}:{self.column}{self.end_row}"

    def formula_for_end_row(self, end_row: int) -> str:
        prefix = f"{self.sheet_prefix}!" if self.sheet_prefix else ""
        return f"={prefix}${self.column}${self.start_row}:${self.column}${end_row}"


def _dropdown_source_formula(sheet, target_row: int):
    """Parse J-column validation source formula for the target row."""
    primary_cell = sheet.Cells(target_row, 10)
    formula = _validation_formula(primary_cell)
    validation_cell = primary_cell
    if formula is None:
        fallback_cell = sheet.Cells(2, 10)
        formula = _validation_formula(fallback_cell)
        if formula is not None:
            validation_cell = fallback_cell
    if formula is None:
        formula = "=$AB$1:$AB$36"
    parsed = _parse_dropdown_source(formula)
    if parsed is None:
        raise LtrWorkbookWriteError(
            f"Unsupported J-column dropdown source formula: {formula}"
        )
    return parsed, validation_cell


def _validation_formula(cell) -> str | None:
    """Return one cell validation formula when available."""
    validation = getattr(cell, "Validation", None)
    if validation is None:
        return None
    text = str(getattr(validation, "Formula1", "") or "").strip()
    return text or None


def _set_validation_formula(cell, formula: str) -> None:
    """Set one cell validation formula."""
    validation = getattr(cell, "Validation", None)
    if validation is None:
        return
    try:
        validation.Formula1 = formula
        return
    except Exception:
        pass
    try:
        validation.Modify(
            getattr(validation, "Type", 3),
            getattr(validation, "AlertStyle", 1),
            getattr(validation, "Operator", 1),
            formula,
            getattr(validation, "Formula2", ""),
        )
    except Exception as exc:
        raise LtrWorkbookWriteError(
            f"Unable to update J-column dropdown source formula: {formula}. "
            f"Excel error: {_exception_summary(exc)}"
        ) from exc


def _fit_description_pn_cell(sheet, row_number: int) -> None:
    """Allow the LTR Description P/N cell to wrap and expand the row height."""
    try:
        sheet.Range(f"F{row_number}").WrapText = True
        sheet.Rows(row_number).AutoFit()
    except Exception as exc:
        raise LtrWorkbookWriteError(
            f"Unable to auto-fit LTR Description P/N cell on row {row_number}. "
            f"Excel error: {_exception_summary(exc)}"
        ) from exc


def _clear_sheet_filter(sheet) -> bool:
    """Clear active AutoFilter state when possible."""
    auto_filter_mode = bool(getattr(sheet, "AutoFilterMode", False))
    filter_mode = bool(getattr(sheet, "FilterMode", False))
    if not auto_filter_mode and not filter_mode:
        return False
    try:
        sheet.ShowAllData()
        return True
    except Exception:
        auto_filter = getattr(sheet, "AutoFilter", None)
        if auto_filter is None:
            return False
        filter_obj = getattr(auto_filter, "FilterMode", None)
        if filter_obj:
            try:
                auto_filter.ShowAllData()
                return True
            except Exception:
                return False
        return False


def _unhide_sheet_rows(sheet) -> bool:
    """Unhide worksheet rows in used range scope and return whether hidden rows were detected."""
    try:
        rows = sheet.UsedRange.Rows
        hidden = bool(getattr(rows, "Hidden", False))
        try:
            rows.Hidden = False
        except Exception:
            sheet.Rows.Hidden = False
        return hidden
    except Exception as exc:
        raise LtrWorkbookWriteError(
            f"Unable to unhide worksheet rows. Excel error: {_exception_summary(exc)}"
        ) from exc


def _unhide_sheet_columns(sheet) -> bool:
    """Unhide worksheet columns in used range scope and return whether hidden columns were detected."""
    try:
        columns = sheet.UsedRange.Columns
        hidden = bool(getattr(columns, "Hidden", False))
        try:
            columns.Hidden = False
        except Exception:
            sheet.Columns.Hidden = False
        return hidden
    except Exception as exc:
        raise LtrWorkbookWriteError(
            f"Unable to unhide worksheet columns. Excel error: {_exception_summary(exc)}"
        ) from exc


def _parse_dropdown_source(formula: str) -> _DropdownSource | None:
    """Parse formulas such as =$AB$1:$AB$36 or ='2026'!$AB$1:$AB$36."""
    text = formula.strip()
    pattern = re.compile(
        r"^=(?:(?P<prefix>'[^']+'|[^!]+)!)?\$(?P<col1>[A-Z]+)\$(?P<start>\d+):\$(?P<col2>[A-Z]+)\$(?P<end>\d+)$"
    )
    match = pattern.match(text)
    if match is None:
        return None
    col1 = match.group("col1")
    col2 = match.group("col2")
    if col1 != col2:
        return None
    start_row = int(match.group("start"))
    end_row = int(match.group("end"))
    if start_row < 1 or end_row < start_row:
        return None
    return _DropdownSource(
        formula=text,
        column=col1,
        start_row=start_row,
        end_row=end_row,
        sheet_prefix=match.group("prefix") or "",
    )


def _column_index(column: str) -> int:
    """Convert an Excel column label to a 1-based index."""
    result = 0
    for character in column:
        result = result * 26 + (ord(character.upper()) - ord("A") + 1)
    return result


def _normalize_dropdown_text(value: object) -> str:
    """Return normalized text for dropdown duplicate checks."""
    return str(value or "").strip().casefold()
