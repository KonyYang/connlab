from __future__ import annotations

import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

from backend.infrastructure.office.ltr_workbook_readonly_open_gateway import (
    ExcelComLtrWorkbookReadonlyOpenGateway,
    LtrWorkbookReadonlyOpenError,
    _open_workbook_readonly,
    a1_address,
)


def test_a1_address_uses_ltr_dl_column() -> None:
    assert a1_address(row_number=260, column_number=4) == "D260"


def test_a1_address_supports_double_letter_columns() -> None:
    assert a1_address(row_number=1, column_number=27) == "AA1"


def test_a1_address_rejects_invalid_numbers() -> None:
    with pytest.raises(LtrWorkbookReadonlyOpenError):
        a1_address(row_number=0, column_number=4)
    with pytest.raises(LtrWorkbookReadonlyOpenError):
        a1_address(row_number=1, column_number=0)


def test_open_workbook_readonly_uses_configured_password_for_readonly_open() -> None:
    workbooks = _RecordingWorkbooks()

    workbook = _open_workbook_readonly(
        workbooks,
        Path("D:/LabShare/LTR/LTR_updated.xlsx"),
        modify_password="operator-secret",
    )

    assert workbook == "workbook"
    assert workbooks.kwargs["Filename"] == "D:\\LabShare\\LTR\\LTR_updated.xlsx"
    assert workbooks.kwargs["ReadOnly"] is True
    assert workbooks.kwargs["Password"] == "operator-secret"
    assert "WriteResPassword" not in workbooks.kwargs
    assert workbooks.kwargs["IgnoreReadOnlyRecommended"] is True
    assert workbooks.kwargs["AddToMru"] is False
    assert workbooks.kwargs["CorruptLoad"] == 2


def test_open_workbook_readonly_omits_password_when_unconfigured() -> None:
    workbooks = _RecordingWorkbooks()

    _open_workbook_readonly(workbooks, Path("D:/LabShare/LTR/LTR_updated.xlsx"))

    assert workbooks.kwargs["Password"] == ""


def test_open_workbook_readonly_uses_excel_open_keyword_shape() -> None:
    workbooks = _RecordingWorkbooks()

    _open_workbook_readonly(workbooks, Path("D:/LabShare/LTR/LTR_updated.xlsx"))

    assert "path" not in workbooks.kwargs
    assert workbooks.kwargs["UpdateLinks"] == 0
    assert workbooks.kwargs["ReadOnly"] is True


def test_open_at_cell_uses_isolated_readonly_instance_without_active_workbook_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workbook_path = tmp_path / "LTR_updated.xlsx"
    workbook_path.write_text("placeholder", encoding="utf-8")
    pythoncom = _RecordingPythonCom()
    win32_client = _FakeWin32ClientWithDispatch()
    monkeypatch.setitem(sys.modules, "pythoncom", pythoncom)
    monkeypatch.setitem(sys.modules, "win32com", SimpleNamespace(client=win32_client))
    monkeypatch.setitem(sys.modules, "win32com.client", win32_client)

    selected_cell = ExcelComLtrWorkbookReadonlyOpenGateway().open_at_cell(
        workbook_path=workbook_path,
        sheet_name="2026",
        row_number=3,
        column_number=4,
    )

    assert selected_cell == "D3"
    assert pythoncom.initialized is True
    assert pythoncom.uninitialized is True
    assert win32_client.get_active_object_called is False
    assert win32_client.dispatch_program_ids == ["Excel.Application"]
    excel = win32_client.dispatched_excel
    assert excel is not None
    assert excel.Visible is True
    assert excel.DisplayAlerts is True
    assert excel.Workbooks.kwargs["Filename"] == str(workbook_path.resolve())
    assert excel.Workbooks.kwargs["ReadOnly"] is True
    worksheet = excel.opened_workbook.worksheet
    assert worksheet.rows_hidden is False
    assert worksheet.columns_hidden is False
    assert worksheet.activated is True
    assert worksheet.selected_cell == (3, 4)
    assert excel.goto_cell == (3, 4)


class _RecordingWorkbooks:
    def __init__(self) -> None:
        self.kwargs: dict[str, object] = {}

    def Open(self, **kwargs: object) -> str:  # noqa: N802 - Excel COM API name
        self.kwargs = kwargs
        return "workbook"


class _RecordingPythonCom:
    def __init__(self) -> None:
        self.initialized = False
        self.uninitialized = False

    def CoInitialize(self) -> None:  # noqa: N802 - pythoncom API name
        self.initialized = True

    def CoUninitialize(self) -> None:  # noqa: N802 - pythoncom API name
        self.uninitialized = True


class _FakeWin32ClientWithDispatch:
    def __init__(self) -> None:
        self.get_active_object_called = False
        self.dispatch_program_ids: list[str] = []
        self.dispatched_excel: _FakeExcelForOpen | None = None

    def GetActiveObject(self, _program_id: str) -> object:  # noqa: N802
        self.get_active_object_called = True
        raise AssertionError("open_at_cell must not inspect active Excel workbooks")

    def DispatchEx(self, program_id: str) -> "_FakeExcelForOpen":  # noqa: N802
        self.dispatch_program_ids.append(program_id)
        self.dispatched_excel = _FakeExcelForOpen()
        return self.dispatched_excel


class _FakeExcelForOpen:
    def __init__(self) -> None:
        self.Visible = False
        self.DisplayAlerts = False
        self.Workbooks = _FakeWorkbooksForOpen()
        self.opened_workbook = self.Workbooks.workbook
        self.goto_cell: tuple[int, int] | None = None

    def Goto(self, cell: "_FakeCell", _scroll: bool) -> None:  # noqa: N802
        self.goto_cell = (cell.row_number, cell.column_number)


class _FakeWorkbooksForOpen:
    def __init__(self) -> None:
        self.kwargs: dict[str, object] = {}
        self.workbook = _FakeWorkbookForOpen()

    def Open(self, **kwargs: object) -> "_FakeWorkbookForOpen":  # noqa: N802
        self.kwargs = kwargs
        return self.workbook


class _FakeWorkbookForOpen:
    def __init__(self) -> None:
        self.worksheet = _FakeWorksheetForOpen()
        self.Worksheets = _FakeWorksheets(self.worksheet)


class _FakeWorksheets:
    def __init__(self, worksheet: "_FakeWorksheetForOpen") -> None:
        self.worksheet = worksheet

    def Item(self, _sheet_name: str) -> "_FakeWorksheetForOpen":  # noqa: N802
        return self.worksheet


class _FakeWorksheetForOpen:
    def __init__(self) -> None:
        self.Rows = _FakeVisibilityTarget()
        self.Columns = _FakeVisibilityTarget()
        self.FilterMode = False
        self.ListObjects: list[object] = []
        self.activated = False
        self.selected_cell: tuple[int, int] | None = None

    @property
    def rows_hidden(self) -> bool | None:
        return self.Rows.Hidden

    @property
    def columns_hidden(self) -> bool | None:
        return self.Columns.Hidden

    def Activate(self) -> None:  # noqa: N802
        self.activated = True

    def Cells(self, row_number: int, column_number: int) -> "_FakeCell":  # noqa: N802
        return _FakeCell(self, row_number, column_number)


class _FakeVisibilityTarget:
    def __init__(self) -> None:
        self.Hidden: bool | None = True


class _FakeCell:
    def __init__(
        self,
        worksheet: _FakeWorksheetForOpen,
        row_number: int,
        column_number: int,
    ) -> None:
        self.worksheet = worksheet
        self.row_number = row_number
        self.column_number = column_number

    def Select(self) -> None:  # noqa: N802
        self.worksheet.selected_cell = (self.row_number, self.column_number)
