from pathlib import Path

import pytest

from backend.infrastructure.office import (
    ExcelComLTRWorkbookGateway,
    LtrWorkbookReadOnlyError,
    LtrWorkbookRowData,
    LtrWorkbookWriteConfig,
    LtrWorkbookWriteDisabledError,
    LtrWorkbookWriteError,
)


def test_excel_com_gateway_requires_write_enabled_path_and_password() -> None:
    office = _FakeOfficeFacade()

    with pytest.raises(LtrWorkbookWriteDisabledError, match="disabled"):
        ExcelComLTRWorkbookGateway(
            office,
            LtrWorkbookWriteConfig(path=Path("ltr.xls"), write_enabled=False),
        ).open_write_session()

    with pytest.raises(LtrWorkbookWriteError, match="path"):
        ExcelComLTRWorkbookGateway(
            office,
            LtrWorkbookWriteConfig(path=None, write_enabled=True, modify_password="pw"),
        ).open_write_session()

    with pytest.raises(LtrWorkbookWriteError, match="password"):
        ExcelComLTRWorkbookGateway(
            office,
            LtrWorkbookWriteConfig(path=Path("ltr.xls"), write_enabled=True),
        ).open_write_session()


def test_excel_com_gateway_opens_with_configured_modify_password() -> None:
    office = _FakeOfficeFacade()
    gateway = ExcelComLTRWorkbookGateway(
        office,
        LtrWorkbookWriteConfig(
            path=Path("ltr.xls"),
            write_enabled=True,
            modify_password="operator-secret",
        ),
    )

    session = gateway.open_write_session()

    assert office.open_calls == [
        {
            "path": Path("ltr.xls"),
            "modify_password": "operator-secret",
            "read_only": False,
        }
    ]
    session.close()


def test_excel_com_gateway_wraps_open_failure_as_business_error() -> None:
    office = _FakeOfficeFacade(open_error=RuntimeError("com open failed"))
    gateway = ExcelComLTRWorkbookGateway(
        office,
        LtrWorkbookWriteConfig(
            path=Path("ltr.xls"),
            write_enabled=True,
            modify_password="operator-secret",
        ),
    )

    with pytest.raises(LtrWorkbookWriteError, match="Unable to open LTR workbook"):
        gateway.open_write_session()


def test_excel_com_write_session_blocks_read_only_workbook() -> None:
    office = _FakeOfficeFacade(read_only=True)
    gateway = ExcelComLTRWorkbookGateway(
        office,
        LtrWorkbookWriteConfig(
            path=Path("ltr.xls"),
            write_enabled=True,
            modify_password="operator-secret",
        ),
    )

    with pytest.raises(LtrWorkbookReadOnlyError, match="read-only"):
        with gateway.open_write_session():
            pass

    assert office.handle.closed is True


def test_excel_com_write_session_uses_batch_read_and_row_write() -> None:
    office = _FakeOfficeFacade()
    gateway = ExcelComLTRWorkbookGateway(
        office,
        LtrWorkbookWriteConfig(
            path=Path("ltr.xls"),
            write_enabled=True,
            modify_password="operator-secret",
        ),
    )

    with gateway.open_write_session() as session:
        rows = session.read_annual_sheet("2026")
        pointer = session.append_registration_row(
            "2026",
            LtrWorkbookRowData(
                month="Apr",
                total=31,
                monthly_number=31,
                dl_number="DL-2026-04-031",
                project_type="Qualification",
            ),
        )
        session.save()

    sheet = office.handle.workbook.Worksheets.Item("2026")
    assert rows == (("Apr", 30, 30, "DL-2026-04-030"),)
    assert sheet.range_reads == ["A2:Q2"]
    assert sheet.range_writes == ["A3:Q3", "A2:A3"]
    assert pointer.row_number == 3
    assert office.handle.saved is True
    assert office.handle.closed is True


def test_excel_com_write_session_appends_at_first_blank_ltr_number_cell() -> None:
    office = _FakeOfficeFacade(
        rows=(
            ("Apr", 30, 30, "DL-2026-04-030"),
            ("Apr", 31, 31, None),
            ("Apr", 32, 32, None),
        ),
        used_rows=10,
    )
    gateway = ExcelComLTRWorkbookGateway(
        office,
        LtrWorkbookWriteConfig(
            path=Path("ltr.xls"),
            write_enabled=True,
            modify_password="operator-secret",
        ),
    )

    with gateway.open_write_session() as session:
        pointer = session.append_registration_row(
            "2026",
            LtrWorkbookRowData(
                month="Apr",
                total=0,
                monthly_number=31,
                dl_number="DL-2026-04-031",
                project_type="Qualification",
            ),
        )

    sheet = office.handle.workbook.Worksheets.Item("2026")
    assert pointer.row_number == 3
    assert sheet.range_writes == ["A3:Q3", "A2:A3"]
    assert sheet.last_written_rows[0][1] == 31
    assert sheet.last_written_rows[0][2] == 31
    assert sheet.last_written_rows[0][3] == "DL-2026-04-031"


def test_excel_com_write_session_finds_and_replaces_existing_ltr_row() -> None:
    """Existing workbook rows can be located and replaced in A:Q."""
    office = _FakeOfficeFacade(rows=(("Apr", 30, 30, "DL-2026-04-030"),))
    gateway = ExcelComLTRWorkbookGateway(
        office,
        LtrWorkbookWriteConfig(
            path=Path("ltr.xls"),
            write_enabled=True,
            modify_password="operator-secret",
        ),
    )

    with gateway.open_write_session() as session:
        existing = session.find_ltr_number("DL-2026-04-030")
        assert existing is not None
        pointer = session.write_registration_row(
            existing.sheet_name,
            existing.row_number,
            LtrWorkbookRowData(
                month="Apr",
                total=30,
                monthly_number=30,
                dl_number="DL-2026-04-030",
                project_type="Replacement",
            ),
        )

    sheet = office.handle.workbook.Worksheets.Item("2026")
    assert pointer.row_number == 2
    assert sheet.range_writes == ["A2:Q2"]
    assert sheet.last_written_rows[0][4] == "Replacement"


def test_excel_com_write_session_calculates_normal_number_after_open() -> None:
    office = _FakeOfficeFacade(
        rows=(("Apr", 30, 30, "DL-2026-04-030A"),),
    )
    gateway = ExcelComLTRWorkbookGateway(
        office,
        LtrWorkbookWriteConfig(
            path=Path("ltr.xls"),
            write_enabled=True,
            modify_password="operator-secret",
        ),
    )

    with gateway.open_write_session() as session:
        pointer = session.append_next_normal_registration(
            "2026",
            2026,
            4,
            LtrWorkbookRowData(
                month="Apr",
                total=31,
                monthly_number=0,
                dl_number="",
                project_type="Qualification",
            ),
        )

    sheet = office.handle.workbook.Worksheets.Item("2026")
    assert sheet.range_reads == ["A2:Q2"]
    assert sheet.last_written_rows[0][3] == "DL-2026-04-031"
    assert sheet.last_written_rows[0][2] == 31
    assert pointer.dl_number == "DL-2026-04-031"


def test_excel_com_write_session_bootstraps_missing_year_sheet() -> None:
    """Write session can copy a template year sheet and clear data rows."""
    office = _FakeOfficeFacade()
    gateway = ExcelComLTRWorkbookGateway(
        office,
        LtrWorkbookWriteConfig(
            path=Path("ltr.xls"),
            write_enabled=True,
            modify_password="operator-secret",
        ),
    )

    with gateway.open_write_session() as session:
        created = session.bootstrap_year_sheet(
            "2027",
            template_sheet_name="2026",
            clear_start_row=2,
        )

    workbook = office.handle.workbook
    created_sheet = workbook.Worksheets.Item("2027")
    assert created is True
    assert "2027" in session.list_sheets()
    assert created_sheet.clear_calls == ["A2:Q2"]


def test_excel_com_write_session_appends_missing_location_to_dropdown_source() -> None:
    """Missing location is appended to AB list and source range expands by one row."""
    office = _FakeOfficeFacade()
    gateway = ExcelComLTRWorkbookGateway(
        office,
        LtrWorkbookWriteConfig(
            path=Path("ltr.xls"),
            write_enabled=True,
            modify_password="operator-secret",
        ),
    )

    with gateway.open_write_session() as session:
        result = session.ensure_location_dropdown_value("2026", "Dongguan")

    sheet = office.handle.workbook.Worksheets.Item("2026")
    assert result.appended is True
    assert result.source_range_before == "=$AB$1:$AB$3"
    assert result.source_range_after == "=$AB$1:$AB$4"
    assert sheet._cells[(4, 28)] == "Dongguan"


def test_excel_com_write_session_keeps_dropdown_source_when_value_exists() -> None:
    """Existing location does not change AB list source range."""
    office = _FakeOfficeFacade()
    gateway = ExcelComLTRWorkbookGateway(
        office,
        LtrWorkbookWriteConfig(
            path=Path("ltr.xls"),
            write_enabled=True,
            modify_password="operator-secret",
        ),
    )

    with gateway.open_write_session() as session:
        result = session.ensure_location_dropdown_value("2026", "nantong")

    assert result.appended is False
    assert result.source_range_before == "=$AB$1:$AB$3"
    assert result.source_range_after == "=$AB$1:$AB$3"


def test_excel_com_write_session_updates_validation_via_modify_when_formula1_set_fails() -> None:
    """Fallback to Validation.Modify when Formula1 property setter is blocked."""
    office = _FakeOfficeFacade(validation_formula_settable=False)
    gateway = ExcelComLTRWorkbookGateway(
        office,
        LtrWorkbookWriteConfig(
            path=Path("ltr.xls"),
            write_enabled=True,
            modify_password="operator-secret",
        ),
    )

    with gateway.open_write_session() as session:
        result = session.ensure_location_dropdown_value("2026", "Dongguan")

    sheet = office.handle.workbook.Worksheets.Item("2026")
    validation = sheet._validations[(2, 10)]
    assert result.appended is True
    assert validation.modified_calls == [("=$AB$1:$AB$4", "")]
    assert validation.Formula1 == "=$AB$1:$AB$4"


def test_excel_com_write_session_prepares_sheet_by_clearing_active_filter() -> None:
    """Preparation clears active filters for full-range workbook operations."""
    office = _FakeOfficeFacade(filter_mode=True)
    gateway = ExcelComLTRWorkbookGateway(
        office,
        LtrWorkbookWriteConfig(
            path=Path("ltr.xls"),
            write_enabled=True,
            modify_password="operator-secret",
        ),
    )

    with gateway.open_write_session() as session:
        result = session.prepare_sheet_for_operation("2026", mode="write")

    sheet = office.handle.workbook.Worksheets.Item("2026")
    assert result.filter_cleared is True
    assert result.hidden_rows_detected is True
    assert result.hidden_columns_detected is True
    assert sheet.show_all_data_calls == 1
    assert sheet.UsedRange.Rows.Hidden is False
    assert sheet.UsedRange.Columns.Hidden is False


class _FakeOfficeFacade:
    def __init__(
        self,
        read_only: bool = False,
        rows: tuple[tuple[object, ...], ...] | None = None,
        used_rows: int | None = None,
        open_error: Exception | None = None,
        validation_formula_settable: bool = True,
        filter_mode: bool = False,
    ) -> None:
        self.handle = _FakeHandle(
            read_only=read_only,
            rows=rows,
            used_rows=used_rows,
            validation_formula_settable=validation_formula_settable,
            filter_mode=filter_mode,
        )
        self.open_calls: list[dict] = []
        self.open_error = open_error

    def open_excel_workbook(
        self,
        source_path: Path,
        *,
        modify_password: str | None = None,
        read_only: bool = False,
    ):
        if self.open_error is not None:
            raise self.open_error
        self.open_calls.append(
            {
                "path": source_path,
                "modify_password": modify_password,
                "read_only": read_only,
            }
        )
        return self.handle


class _FakeHandle:
    def __init__(
        self,
        read_only: bool,
        rows: tuple[tuple[object, ...], ...] | None = None,
        used_rows: int | None = None,
        validation_formula_settable: bool = True,
        filter_mode: bool = False,
    ) -> None:
        self.workbook = _FakeWorkbook(
            read_only,
            rows,
            used_rows,
            validation_formula_settable,
            filter_mode,
        )
        self.saved = False
        self.closed = False

    def save(self) -> None:
        self.saved = True

    def close(self, save_changes: bool = False) -> None:
        self.closed = True


class _FakeWorkbook:
    def __init__(
        self,
        read_only: bool,
        rows: tuple[tuple[object, ...], ...] | None,
        used_rows: int | None,
        validation_formula_settable: bool,
        filter_mode: bool,
    ) -> None:
        self.ReadOnly = read_only
        self.Worksheets = _FakeWorksheets(
            rows,
            used_rows,
            validation_formula_settable,
            filter_mode,
        )


class _FakeWorksheets:
    def __init__(
        self,
        rows: tuple[tuple[object, ...], ...] | None,
        used_rows: int | None,
        validation_formula_settable: bool,
        filter_mode: bool,
    ) -> None:
        base = _FakeSheet("2026", rows, used_rows, validation_formula_settable, filter_mode)
        self._sheets = {"2026": base}
        self._order = ["2026"]
        base._owner = self

    def __iter__(self):
        return iter(self._sheets[name] for name in self._order)

    @property
    def Count(self) -> int:
        return len(self._order)

    def Item(self, name_or_index):
        if isinstance(name_or_index, int):
            return self._sheets[self._order[name_or_index - 1]]
        return self._sheets[name_or_index]

    def _copy_sheet_after(self, source_name: str, after_name: str) -> "_FakeSheet":
        source = self._sheets[source_name]
        copied = _FakeSheet(
            source.Name,
            source.rows,
            source.UsedRange.Rows.Count,
            source._validation_formula_settable,
            source.FilterMode,
        )
        insert_at = self._order.index(after_name) + 1
        temp_name = f"_copy_{len(self._order) + 1}"
        copied.Name = temp_name
        copied._owner = self
        self._order.insert(insert_at, temp_name)
        self._sheets[temp_name] = copied
        return copied

    def _rename_sheet(self, old_name: str, new_name: str) -> None:
        if new_name in self._sheets:
            raise ValueError("sheet already exists")
        sheet = self._sheets.pop(old_name)
        self._sheets[new_name] = sheet
        self._order[self._order.index(old_name)] = new_name


class _FakeSheet:
    def __init__(
        self,
        name: str,
        rows: tuple[tuple[object, ...], ...] | None,
        used_rows: int | None = None,
        validation_formula_settable: bool = True,
        filter_mode: bool = False,
    ) -> None:
        self._owner = None
        self._name = name
        self._validation_formula_settable = validation_formula_settable
        self.AutoFilterMode = filter_mode
        self.FilterMode = filter_mode
        self.show_all_data_calls = 0
        self.rows = rows or (("Apr", 30, 30, "DL-2026-04-030"),)
        self._cells = _rows_to_cells(self.rows)
        self.UsedRange = _FakeUsedRange(rows=used_rows or len(self.rows) + 1)
        self.range_reads: list[str] = []
        self.range_writes: list[str] = []
        self.clear_calls: list[str] = []
        self.last_written_rows: list[list[object]] = []
        self._validations: dict[tuple[int, int], _FakeValidation] = {
            (2, 10): _FakeValidation(
                "=$AB$1:$AB$3",
                formula_settable=validation_formula_settable,
            )
        }
        self._cells[(1, 28)] = "Berlin"
        self._cells[(2, 28)] = "Nantong"
        self._cells[(3, 28)] = "Cochin"

    @property
    def Name(self) -> str:
        return self._name

    @Name.setter
    def Name(self, value: str) -> None:
        if self._owner is None:
            self._name = value
            return
        self._owner._rename_sheet(self._name, value)
        self._name = value

    def Range(self, address: str):
        return _FakeRange(self, address)

    def Cells(self, row: int, column: int):
        return _FakeCell(self, row, column)

    def Copy(self, *, After) -> None:
        after_name = After.Name
        owner = self._owner
        if owner is None:
            raise ValueError("owner not set")
        owner._copy_sheet_after(self.Name, after_name)

    def ShowAllData(self) -> None:
        self.FilterMode = False
        self.show_all_data_calls += 1


class _FakeUsedRange:
    def __init__(self, rows: int) -> None:
        self.Rows = _FakeRows(rows)
        self.Columns = _FakeColumns()


class _FakeRows:
    def __init__(self, count: int) -> None:
        self.Count = count
        self.Hidden = True


class _FakeColumns:
    def __init__(self) -> None:
        self.Hidden = True


class _FakeRange:
    def __init__(self, sheet: _FakeSheet, address: str) -> None:
        self._sheet = sheet
        self._address = address

    @property
    def Value(self):
        self._sheet.range_reads.append(self._address)
        start, end = _split_range(self._address)
        start_col, start_row = _cell_ref(start)
        end_col, end_row = _cell_ref(end)
        if start_col == 1 and end_col == 17 and start_row == 2:
            return self._sheet.rows
        if start_col == end_col:
            return tuple(
                (self._sheet._cells.get((row, start_col)),)
                for row in range(start_row, end_row + 1)
            )
        rows = []
        for row in range(start_row, end_row + 1):
            rows.append(
                tuple(
                    self._sheet._cells.get((row, column))
                    for column in range(start_col, end_col + 1)
                )
            )
        return tuple(rows)

    @property
    def Value2(self):
        return self.Value

    @Value.setter
    def Value(self, rows) -> None:
        self._sheet.range_writes.append(self._address)
        if ":" not in self._address:
            self._set_single_value(rows)
            return
        start = self._address.split(":", 1)[0]
        end = self._address.split(":", 1)[1]
        start_row = _row_number(start)
        end_row = _row_number(end)
        if not isinstance(rows, list):
            for row_number in range(start_row, end_row + 1):
                self._sheet._cells[(row_number, 1)] = rows
            return
        self._sheet.last_written_rows.extend(rows)
        for offset, row_values in enumerate(rows):
            row_number = start_row + offset
            for index, value in enumerate(row_values, start=1):
                self._sheet._cells[(row_number, index)] = value

    def ClearContents(self) -> None:
        self._sheet.clear_calls.append(self._address)

    def Merge(self) -> None:
        return None

    def UnMerge(self) -> None:
        return None

    @property
    def Row(self) -> int:
        return _row_number(self._address.split(":", 1)[0])

    @property
    def Rows(self):
        return _FakeRows(1)

    def Cells(self, row: int, column: int):
        return _FakeCell(self._sheet, self.Row + row - 1, column)

    def _set_single_value(self, value) -> None:
        column, row = _cell_ref(self._address)
        self._sheet._cells[(row, column)] = value


class _FakeCell:
    MergeCells = False

    def __init__(self, sheet: _FakeSheet, row: int, column: int) -> None:
        self._sheet = sheet
        self._row = row
        self._column = column

    @property
    def Value(self):
        return self._sheet._cells.get((self._row, self._column))

    @Value.setter
    def Value(self, value) -> None:
        self._sheet._cells[(self._row, self._column)] = value

    @property
    def Validation(self):
        return self._sheet._validations.get((self._row, self._column))


class _FakeValidation:
    def __init__(self, formula1: str, *, formula_settable: bool = True) -> None:
        self._formula1 = formula1
        self._formula_settable = formula_settable
        self.Formula2 = ""
        self.Type = 3
        self.AlertStyle = 1
        self.Operator = 1
        self.modified_calls: list[tuple[str, str]] = []

    @property
    def Formula1(self) -> str:
        return self._formula1

    @Formula1.setter
    def Formula1(self, value: str) -> None:
        if not self._formula_settable:
            raise RuntimeError("Property '<unknown>.Formula1' can not be set.")
        self._formula1 = value

    def Modify(
        self,
        _type: int,
        _alert_style: int,
        _operator: int,
        formula1: str,
        formula2: str = "",
    ) -> None:
        self._formula1 = formula1
        self.Formula2 = formula2
        self.modified_calls.append((formula1, formula2))


def _rows_to_cells(rows: tuple[tuple[object, ...], ...]) -> dict[tuple[int, int], object]:
    cells: dict[tuple[int, int], object] = {}
    for row_offset, row in enumerate(rows, start=2):
        for column, value in enumerate(row, start=1):
            cells[(row_offset, column)] = value
    return cells


def _row_number(address: str) -> int:
    digits = "".join(character for character in address if character.isdigit())
    return int(digits)


def _split_range(address: str) -> tuple[str, str]:
    if ":" in address:
        left, right = address.split(":", 1)
        return left, right
    return address, address


def _cell_ref(address: str) -> tuple[int, int]:
    letters = "".join(character for character in address if character.isalpha())
    digits = "".join(character for character in address if character.isdigit())
    return _column_index(letters), int(digits)


def _column_index(label: str) -> int:
    value = 0
    for character in label.upper():
        value = value * 26 + (ord(character) - ord("A") + 1)
    return value
