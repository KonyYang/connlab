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


class _FakeOfficeFacade:
    def __init__(
        self,
        read_only: bool = False,
        rows: tuple[tuple[object, ...], ...] | None = None,
    ) -> None:
        self.handle = _FakeHandle(read_only=read_only, rows=rows)
        self.open_calls: list[dict] = []

    def open_excel_workbook(
        self,
        source_path: Path,
        *,
        modify_password: str | None = None,
        read_only: bool = False,
    ):
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
        self._sheets = {"2026": _FakeSheet("2026", rows)}

    def __iter__(self):
        return iter(self._sheets.values())

    def Item(self, name: str):
        return self._sheets[name]


class _FakeSheet:
    def __init__(self, name: str, rows: tuple[tuple[object, ...], ...] | None) -> None:
        self.Name = name
        self.UsedRange = _FakeUsedRange(rows=2)
        self.rows = rows or (("Apr", 30, 30, "DL-2026-04-030"),)
        self.range_reads: list[str] = []
        self.range_writes: list[str] = []
        self.last_written_rows: list[list[object]] = []

    def Range(self, address: str):
        return _FakeRange(self, address)


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
