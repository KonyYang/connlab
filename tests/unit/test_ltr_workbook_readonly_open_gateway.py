from __future__ import annotations

from pathlib import Path

import pytest

from backend.infrastructure.office.ltr_workbook_readonly_open_gateway import (
    LtrWorkbookReadonlyOpenError,
    _open_workbook_readonly,
    _raise_if_workbook_already_open,
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


def test_open_workbook_check_blocks_exact_active_workbook() -> None:
    win32_client = _FakeWin32Client(
        [_FakeWorkbook("D:/LabShare/LTR/LTR_updated.xlsx")]
    )

    with pytest.raises(LtrWorkbookReadonlyOpenError):
        _raise_if_workbook_already_open(
            win32_client,
            Path("D:/LabShare/LTR/LTR_updated.xlsx"),
        )


def test_open_workbook_check_skips_unreadable_unrelated_excel_workbooks() -> None:
    win32_client = _FakeWin32Client(
        [
            _FakeWorkbook("D:/Other/Workbook.xlsx"),
            _UnreadableWorkbook(),
        ]
    )

    _raise_if_workbook_already_open(
        win32_client,
        Path("D:/LabShare/LTR/LTR_updated.xlsx"),
    )


class _RecordingWorkbooks:
    def __init__(self) -> None:
        self.kwargs: dict[str, object] = {}

    def Open(self, **kwargs: object) -> str:  # noqa: N802 - Excel COM API name
        self.kwargs = kwargs
        return "workbook"


class _FakeWin32Client:
    def __init__(self, workbooks: list[object]) -> None:
        self._excel = _FakeExcel(workbooks)

    def GetActiveObject(self, _program_id: str) -> "_FakeExcel":  # noqa: N802
        return self._excel


class _FakeExcel:
    def __init__(self, workbooks: list[object]) -> None:
        self.Workbooks = workbooks


class _FakeWorkbook:
    def __init__(self, full_name: str) -> None:
        self.FullName = full_name


class _UnreadableWorkbook:
    @property
    def FullName(self) -> str:
        raise RuntimeError("COM workbook path unavailable")
