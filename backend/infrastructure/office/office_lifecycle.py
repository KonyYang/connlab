"""Office automation lifecycle boundary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class OfficeAutomationUnavailable(RuntimeError):
    """Raised when a COM fallback is requested before it is implemented."""


@dataclass(slots=True)
class ExcelWorkbookHandle:
    """Handle for one COM-opened Excel workbook and its application."""

    excel_app: object
    workbook: object
    previous_settings: dict[str, object]

    def save(self) -> None:
        """Save the workbook."""
        self.workbook.Save()

    def close(self, save_changes: bool = False) -> None:
        """Close workbook and quit the dedicated Excel instance."""
        try:
            self.workbook.Close(SaveChanges=save_changes)
        finally:
            _restore_excel_settings(self.excel_app, self.previous_settings)
            self.excel_app.Quit()


class OfficeLifecycleManager:
    """Centralize future COM automation lifecycle management."""

    def require_com_fallback(self, application_name: str) -> None:
        """Reject COM fallback until a task explicitly implements it."""
        raise OfficeAutomationUnavailable(
            f"{application_name} COM fallback is not implemented in this phase."
        )

    def open_excel_workbook(
        self,
        path: Path,
        modify_password: str | None = None,
        read_only: bool = False,
    ) -> ExcelWorkbookHandle:
        """Open an Excel workbook in a dedicated hidden COM instance."""
        try:
            import win32com.client  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - depends on Windows host
            raise OfficeAutomationUnavailable(
                "Excel COM automation requires pywin32 on Windows."
            ) from exc

        excel = win32com.client.DispatchEx("Excel.Application")
        previous_settings = _apply_excel_automation_settings(excel)
        workbook = None
        try:
            workbook = excel.Workbooks.Open(
                str(path),
                ReadOnly=read_only,
                WriteResPassword=modify_password or "",
            )
            return ExcelWorkbookHandle(
                excel_app=excel,
                workbook=workbook,
                previous_settings=previous_settings,
            )
        except Exception:
            if workbook is not None:
                workbook.Close(SaveChanges=False)
            _restore_excel_settings(excel, previous_settings)
            excel.Quit()
            raise


def _apply_excel_automation_settings(excel: object) -> dict[str, object]:
    """Apply safe Excel automation settings and return previous values."""
    previous = {
        "Visible": getattr(excel, "Visible", False),
        "DisplayAlerts": getattr(excel, "DisplayAlerts", True),
        "ScreenUpdating": getattr(excel, "ScreenUpdating", True),
        "EnableEvents": getattr(excel, "EnableEvents", True),
        "Calculation": getattr(excel, "Calculation", None),
    }
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.ScreenUpdating = False
    excel.EnableEvents = False
    excel.Calculation = -4135
    return previous


def _restore_excel_settings(excel: object, previous: dict[str, object]) -> None:
    """Restore Excel automation settings when possible."""
    for key, value in previous.items():
        if value is not None:
            try:
                setattr(excel, key, value)
            except Exception:
                continue
