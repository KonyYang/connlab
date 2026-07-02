"""Read-only Excel opener for the configured LTR workbook."""

from __future__ import annotations

from pathlib import Path


class LtrWorkbookReadonlyOpenError(RuntimeError):
    """Raised when the LTR workbook cannot be opened safely for read-only review."""


class ExcelComLtrWorkbookReadonlyOpenGateway:
    """Open an LTR workbook read-only and select the exact DL cell."""

    def __init__(self, *, modify_password: str | None = None) -> None:
        self._modify_password = modify_password

    def open_at_cell(
        self,
        *,
        workbook_path: Path,
        sheet_name: str,
        row_number: int,
        column_number: int,
    ) -> str:
        """Open the workbook read-only and select one cell for operator review."""
        path = Path(workbook_path).resolve()
        if not path.is_file():
            raise LtrWorkbookReadonlyOpenError(f"LTR workbook does not exist: {path}")
        selected_cell = a1_address(row_number=row_number, column_number=column_number)

        try:
            import pythoncom  # type: ignore[import-not-found]
            import win32com.client  # type: ignore[import-not-found]
        except ImportError as exc:
            raise LtrWorkbookReadonlyOpenError(
                "Excel automation is not available on this workstation."
            ) from exc

        pythoncom.CoInitialize()
        try:
            _raise_if_workbook_already_open(win32com.client, path)
            excel = win32com.client.DispatchEx("Excel.Application")
            excel.Visible = True
            excel.DisplayAlerts = True
            workbook = _open_workbook_readonly(
                excel.Workbooks,
                path,
                modify_password=self._modify_password,
            )
            worksheet = workbook.Worksheets.Item(sheet_name)
            _prepare_sheet_for_review(worksheet)
            worksheet.Activate()
            cell = worksheet.Cells(row_number, column_number)
            cell.Select()
            excel.Goto(cell, True)
            return selected_cell
        except LtrWorkbookReadonlyOpenError:
            raise
        except Exception as exc:
            raise LtrWorkbookReadonlyOpenError(
                "Excel could not open the LTR workbook read-only at the exact DL row. "
                "Confirm any Excel read-only prompt, then retry. Check the setup "
                "workbook path and password if it still fails."
            ) from exc
        finally:
            pythoncom.CoUninitialize()


def a1_address(*, row_number: int, column_number: int) -> str:
    """Return an A1 address for one-based row and column numbers."""
    if row_number < 1 or column_number < 1:
        raise LtrWorkbookReadonlyOpenError("Excel row and column numbers must be positive.")
    column = ""
    number = column_number
    while number:
        number, remainder = divmod(number - 1, 26)
        column = chr(ord("A") + remainder) + column
    return f"{column}{row_number}"


def _open_workbook_readonly(
    workbooks,
    workbook_path: Path,
    *,
    modify_password: str | None = None,
):
    """Open an LTR workbook for operator review without write access."""
    return workbooks.Open(
        Filename=str(workbook_path),
        UpdateLinks=0,
        ReadOnly=True,
        Password=modify_password or "",
        AddToMru=False,
        IgnoreReadOnlyRecommended=True,
        CorruptLoad=2,
    )


def _raise_if_workbook_already_open(win32_client, workbook_path: Path) -> None:
    """Block rather than mutate a user-controlled open Excel workbook."""
    try:
        excel = win32_client.GetActiveObject("Excel.Application")
    except Exception:
        return
    try:
        workbooks = list(excel.Workbooks)
    except Exception:
        return
    for workbook in workbooks:
        try:
            full_name = Path(str(workbook.FullName))
        except Exception:
            continue
        if _path_key(full_name) == _path_key(workbook_path):
            raise LtrWorkbookReadonlyOpenError(
                "The LTR workbook is already open in Excel. Close it and retry."
            )


def _prepare_sheet_for_review(worksheet) -> None:
    """Unhide rows/columns and clear active filters in the read-only viewer session."""
    _try_optional_excel_adjustment(lambda: setattr(worksheet.Rows, "Hidden", False))
    _try_optional_excel_adjustment(lambda: setattr(worksheet.Columns, "Hidden", False))
    _try_optional_excel_adjustment(
        lambda: worksheet.ShowAllData() if worksheet.FilterMode else None
    )
    _try_optional_excel_adjustment(
        lambda: [
            table.AutoFilter.ShowAllData()
            for table in worksheet.ListObjects
            if table.AutoFilter.FilterMode
        ]
    )


def _try_optional_excel_adjustment(action) -> None:
    """Best-effort viewer cleanup; selection still works if Excel rejects one setting."""
    try:
        action()
    except Exception:
        return


def _path_key(path: Path) -> str:
    return str(path.resolve()).casefold()
