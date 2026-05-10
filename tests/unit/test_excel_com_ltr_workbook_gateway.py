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
    assert sheet.range_writes == ["A3:Q3"]
    assert pointer.row_number == 3
    assert office.handle.saved is True
    assert office.handle.closed is True


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


class _FakeOfficeFacade:
    def __init__(
        self,
        read_only: bool = False,
        rows: tuple[tuple[object, ...], ...] | None = None,
        open_error: Exception | None = None,
    ) -> None:
        self.handle = _FakeHandle(read_only=read_only, rows=rows)
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
    ) -> None:
        self.workbook = _FakeWorkbook(read_only, rows)
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
    ) -> None:
        self.ReadOnly = read_only
        self.Worksheets = _FakeWorksheets(rows)


class _FakeWorksheets:
    def __init__(self, rows: tuple[tuple[object, ...], ...] | None) -> None:
        base = _FakeSheet("2026", rows)
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
        copied = _FakeSheet(source.Name, source.rows)
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
    def __init__(self, name: str, rows: tuple[tuple[object, ...], ...] | None) -> None:
        self._owner = None
        self._name = name
        self.rows = rows or (("Apr", 30, 30, "DL-2026-04-030"),)
        self.UsedRange = _FakeUsedRange(rows=len(self.rows) + 1)
        self.range_reads: list[str] = []
        self.range_writes: list[str] = []
        self.clear_calls: list[str] = []
        self.last_written_rows: list[list[object]] = []

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

    def Copy(self, *, After) -> None:
        after_name = After.Name
        owner = self._owner
        if owner is None:
            raise ValueError("owner not set")
        owner._copy_sheet_after(self.Name, after_name)


class _FakeUsedRange:
    def __init__(self, rows: int) -> None:
        self.Rows = _FakeRows(rows)


class _FakeRows:
    def __init__(self, count: int) -> None:
        self.Count = count


class _FakeRange:
    def __init__(self, sheet: _FakeSheet, address: str) -> None:
        self._sheet = sheet
        self._address = address

    @property
    def Value(self):
        self._sheet.range_reads.append(self._address)
        return self._sheet.rows

    @Value.setter
    def Value(self, rows) -> None:
        self._sheet.range_writes.append(self._address)
        self._sheet.last_written_rows.extend(rows)

    def ClearContents(self) -> None:
        self._sheet.clear_calls.append(self._address)
