from __future__ import annotations

from pathlib import Path

import pytest

from backend.infrastructure.office.ltr_workbook_readonly_open_gateway import (
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


def test_open_workbook_readonly_does_not_use_write_reservation_password() -> None:
    workbooks = _RecordingWorkbooks()

    workbook = _open_workbook_readonly(workbooks, Path("D:/LabShare/LTR/LTR_updated.xlsx"))

    assert workbook == "workbook"
    assert workbooks.kwargs["Filename"] == "D:\\LabShare\\LTR\\LTR_updated.xlsx"
    assert workbooks.kwargs["ReadOnly"] is True
    assert "Password" not in workbooks.kwargs
    assert "WriteResPassword" not in workbooks.kwargs
    assert workbooks.kwargs["IgnoreReadOnlyRecommended"] is True
    assert workbooks.kwargs["AddToMru"] is False
    assert workbooks.kwargs["CorruptLoad"] == 2


def test_open_workbook_readonly_uses_excel_open_keyword_shape() -> None:
    workbooks = _RecordingWorkbooks()

    _open_workbook_readonly(workbooks, Path("D:/LabShare/LTR/LTR_updated.xlsx"))

    assert "path" not in workbooks.kwargs
    assert workbooks.kwargs["UpdateLinks"] == 0
    assert workbooks.kwargs["ReadOnly"] is True


class _RecordingWorkbooks:
    def __init__(self) -> None:
        self.kwargs: dict[str, object] = {}

    def Open(self, **kwargs: object) -> str:  # noqa: N802 - Excel COM API name
        self.kwargs = kwargs
        return "workbook"
