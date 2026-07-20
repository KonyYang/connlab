"""Office automation lifecycle boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


class OfficeAutomationUnavailable(RuntimeError):
    """Raised when a COM fallback is requested before it is implemented."""


class OfficeAutomationCleanupError(RuntimeError):
    """Raised after all owned Office resources were offered cleanup."""


@dataclass(slots=True)
class ExcelWorkbookHandle:
    """Handle for one COM-opened Excel workbook and its application."""

    excel_app: object
    workbook: object
    previous_settings: dict[str, object]
    pythoncom: object | None = None
    _closed: bool = field(default=False, init=False, repr=False)

    def save(self) -> None:
        """Save the workbook."""
        self.workbook.Save()

    def close(self, save_changes: bool = False) -> None:
        """Close workbook and quit the dedicated Excel instance."""
        if self._closed:
            return
        self._closed = True
        failures = _cleanup_excel_ownership(
            workbook=self.workbook,
            excel=self.excel_app,
            previous_settings=self.previous_settings,
            pythoncom=self.pythoncom,
            save_changes=save_changes,
        )
        if failures:
            raise OfficeAutomationCleanupError(_exception_summary(failures[0])) from failures[0]


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
            import pythoncom  # type: ignore[import-not-found]
            import win32com.client  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - depends on Windows host
            raise OfficeAutomationUnavailable(
                "Excel COM automation requires pywin32 on Windows."
            ) from exc

        pythoncom.CoInitialize()
        excel = None
        workbook = None
        previous_settings: dict[str, object] = {}
        try:
            excel = win32com.client.DispatchEx("Excel.Application")
            previous_settings = _capture_excel_settings(excel)
            _apply_excel_automation_settings(excel, previous_settings)
            workbook = excel.Workbooks.Open(
                Filename=str(path),
                UpdateLinks=0,
                ReadOnly=read_only,
                Format=None,
                WriteResPassword=modify_password if (modify_password and not read_only) else "",
                Password=modify_password if (modify_password and read_only) else "",
                Origin=None,
                Delimiter=None,
                IgnoreReadOnlyRecommended=True,
                AddToMru=False,
                CorruptLoad=2,
            )
            return ExcelWorkbookHandle(
                excel_app=excel,
                workbook=workbook,
                previous_settings=previous_settings,
                pythoncom=pythoncom,
            )
        except Exception as primary_error:
            failures = _cleanup_excel_ownership(
                workbook=workbook,
                excel=excel,
                previous_settings=previous_settings,
                pythoncom=pythoncom,
                save_changes=False,
            )
            if failures:
                primary_error.add_note(
                    f"Cleanup warning: {_exception_summary(failures[0])}"
                )
            raise


def _capture_excel_settings(excel: object) -> dict[str, object]:
    """Capture settings before any mutation can fail."""
    return {
        "Visible": getattr(excel, "Visible", False),
        "DisplayAlerts": getattr(excel, "DisplayAlerts", True),
        "ScreenUpdating": getattr(excel, "ScreenUpdating", True),
        "EnableEvents": getattr(excel, "EnableEvents", True),
        "Calculation": getattr(excel, "Calculation", None),
    }


def _apply_excel_automation_settings(
    excel: object,
    previous: dict[str, object] | None = None,
) -> dict[str, object]:
    """Apply safe Excel automation settings and return previous values."""
    previous = previous if previous is not None else _capture_excel_settings(excel)
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.ScreenUpdating = False
    excel.EnableEvents = False
    # Some lab-host Excel builds reject Calculation assignment; degrade safely.
    try:
        excel.Calculation = -4135
    except Exception:
        previous["Calculation"] = None
    return previous


def _restore_excel_settings(excel: object, previous: dict[str, object]) -> None:
    """Restore Excel automation settings when possible."""
    for key, value in previous.items():
        if value is not None:
            try:
                setattr(excel, key, value)
            except Exception:
                continue


def _cleanup_excel_ownership(
    *,
    workbook: object | None,
    excel: object | None,
    previous_settings: dict[str, object],
    pythoncom: object | None,
    save_changes: bool,
) -> list[Exception]:
    failures: list[Exception] = []
    if workbook is not None:
        try:
            workbook.Close(SaveChanges=save_changes)
        except Exception as exc:
            failures.append(exc)
    if excel is not None:
        _restore_excel_settings(excel, previous_settings)
        try:
            excel.Quit()
        except Exception as exc:
            failures.append(exc)
    if pythoncom is not None:
        try:
            pythoncom.CoUninitialize()
        except Exception as exc:
            failures.append(exc)
    return failures


def _exception_summary(exc: Exception) -> str:
    summary = " ".join(str(exc).split()) or exc.__class__.__name__
    return summary[:240]
