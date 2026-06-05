from __future__ import annotations

from pathlib import Path

import pytest


OPTIMIZED_TEMPLATE = Path(
    "D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls"
)


def test_task289_optimized_testing_prices_layout() -> None:
    """Verify the TASK_289 optimized fee template layout without mutating it."""
    pytest.importorskip("win32com")
    if not OPTIMIZED_TEMPLATE.is_file():
        pytest.skip(f"Optimized fee template is not available: {OPTIMIZED_TEMPLATE}")

    import win32com.client  # type: ignore[import-not-found]

    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    workbook = None
    try:
        workbook = excel.Workbooks.Open(
            str(OPTIMIZED_TEMPLATE),
            ReadOnly=True,
            UpdateLinks=0,
        )
        sheet_names = [
            workbook.Worksheets.Item(index).Name
            for index in range(1, workbook.Worksheets.Count + 1)
        ]
        sheet = workbook.Worksheets.Item("Testing Prices")
        page_setup = sheet.PageSetup

        assert sheet_names == ["Testing Prices", "Unit Price Reference"]
        assert sheet.UsedRange.Address == "$A$1:$I$12"
        assert page_setup.PrintArea == "$A$1:$I$12"
        assert page_setup.PaperSize == 9
        assert page_setup.Orientation == 1
        assert page_setup.Zoom is False
        assert page_setup.FitToPagesWide == 1
        assert page_setup.FitToPagesTall is False

        assert sheet.Range("D1").Font.Size == 11
        assert sheet.Range("B4").Font.Size == 9
        assert sheet.Range("C5").Font.Size == 9
        assert sheet.Columns("A").ColumnWidth == pytest.approx(8.0, abs=0.1)
        assert sheet.Columns("C").ColumnWidth == pytest.approx(22.47, abs=0.1)
        assert sheet.Rows(5).RowHeight == pytest.approx(20.0, abs=0.2)

        assert sheet.Range("A4").Value == "Group"
        assert sheet.Range("C7").Value == "Report preparation"
        assert sheet.Range("I5").Formula == "=D5*F5*(1-H5)+G5"
        assert sheet.Range("I6").Formula == "=D6*F6*(1-H6)+G6"
        assert sheet.Range("I7").Formula == "=D7*F7*(1-H7)+G7"
        assert sheet.Range("I8").Formula == "=D8*F8*(1-H8)+G8"
        assert sheet.Range("B9").Formula == "=SUM(B5:B8)"
        assert sheet.Range("D10").Formula == "=B9"
        assert sheet.Range("I10").Formula == "=D10*180"
        assert sheet.Range("I11").Formula == "=I10+D11"
    finally:
        if workbook is not None:
            workbook.Close(SaveChanges=False)
        excel.Quit()
