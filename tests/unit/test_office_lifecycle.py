import sys
from pathlib import Path

import pytest

from backend.infrastructure.office.office_lifecycle import ExcelWorkbookHandle
from backend.infrastructure.office.office_lifecycle import OfficeAutomationCleanupError
from backend.infrastructure.office.office_lifecycle import _apply_excel_automation_settings
from backend.infrastructure.office.office_lifecycle import OfficeLifecycleManager


def test_apply_excel_automation_settings_tolerates_calculation_assignment_failure() -> None:
    excel = _FakeExcelFailCalculation()

    previous = _apply_excel_automation_settings(excel)

    assert excel.Visible is False
    assert excel.DisplayAlerts is False
    assert excel.ScreenUpdating is False
    assert excel.EnableEvents is False
    assert previous["Calculation"] is None


class _FakeExcelFailCalculation:
    def __init__(self) -> None:
        self.Visible = True
        self.DisplayAlerts = True
        self.ScreenUpdating = True
        self.EnableEvents = True
        self._calculation = 1

    @property
    def Calculation(self) -> int:
        return self._calculation

    @Calculation.setter
    def Calculation(self, value: int) -> None:
        raise RuntimeError("Calculation assignment blocked.")


def test_open_excel_workbook_passes_password_to_open_and_write_reservation(monkeypatch) -> None:
    manager = OfficeLifecycleManager()
    fake_excel = _FakeExcelAppForOpen()

    class _FakeClientModule:
        @staticmethod
        def DispatchEx(name: str):
            assert name == "Excel.Application"
            return fake_excel

    class _FakeWin32ComModule:
        client = _FakeClientModule()

    fake_pythoncom = _FakePythonComModule()

    monkeypatch.setitem(sys.modules, "pythoncom", fake_pythoncom)
    monkeypatch.setitem(sys.modules, "win32com", _FakeWin32ComModule())
    monkeypatch.setitem(sys.modules, "win32com.client", _FakeClientModule())

    assert fake_pythoncom.initialized is False
    handle = manager.open_excel_workbook(
        path=Path("D:/LabShare/LTR.XLS"),
        modify_password="DGLAB",
        read_only=False,
    )
    assert fake_pythoncom.initialized is True
    handle.close(save_changes=False)
    assert fake_pythoncom.initialized is False
    assert fake_pythoncom.initialize_calls == 1
    assert fake_pythoncom.uninitialize_calls == 1

    kwargs = fake_excel.open_calls[0]
    assert kwargs["Filename"] == "D:\\LabShare\\LTR.XLS" or kwargs["Filename"] == "D:/LabShare/LTR.XLS"
    assert kwargs["UpdateLinks"] == 0
    assert kwargs["ReadOnly"] is False
    assert kwargs["Format"] is None
    assert kwargs["Password"] == ""
    assert kwargs["WriteResPassword"] == "DGLAB"
    assert kwargs["Origin"] is None
    assert kwargs["Delimiter"] is None
    assert kwargs["IgnoreReadOnlyRecommended"] is True
    assert kwargs["AddToMru"] is False
    assert kwargs["CorruptLoad"] == 2


class _FakeWorkbookForOpen:
    ReadOnly = False

    def Save(self) -> None:
        return None

    def Close(self, SaveChanges: bool = False) -> None:
        return None


class _FakeWorkbooksForOpen:
    def __init__(self, excel) -> None:
        self._excel = excel

    def Open(self, **kwargs):
        self._excel.open_calls.append(kwargs)
        return _FakeWorkbookForOpen()


class _FakeExcelAppForOpen:
    def __init__(self) -> None:
        self.Visible = True
        self.DisplayAlerts = True
        self.ScreenUpdating = True
        self.EnableEvents = True
        self.Calculation = 1
        self.Workbooks = _FakeWorkbooksForOpen(self)
        self.open_calls = []

    def Quit(self) -> None:
        return None


class _FakePythonComModule:
    def __init__(self) -> None:
        self.initialized = False
        self.initialize_calls = 0
        self.uninitialize_calls = 0

    def CoInitialize(self) -> None:
        self.initialized = True
        self.initialize_calls += 1

    def CoUninitialize(self) -> None:
        self.initialized = False
        self.uninitialize_calls += 1


def test_handle_close_attempts_all_cleanup_steps_once_when_close_and_quit_fail() -> None:
    events: list[str] = []
    workbook = _RecordingWorkbook(events, close_error=RuntimeError("close failed"))
    excel = _RecordingExcel(events, quit_error=RuntimeError("quit failed"))
    pythoncom = _RecordingPythonCom(events)
    handle = ExcelWorkbookHandle(
        excel_app=excel,
        workbook=workbook,
        previous_settings={},
        pythoncom=pythoncom,
    )

    with pytest.raises(OfficeAutomationCleanupError, match="close failed"):
        handle.close(save_changes=False)

    assert events == ["close:False", "quit", "uninitialize"]
    handle.close(save_changes=False)
    assert events == ["close:False", "quit", "uninitialize"]


def test_open_settings_failure_preserves_primary_error_and_cleans_owned_resources(
    monkeypatch,
) -> None:
    events: list[str] = []
    excel = _RecordingExcel(events, display_alerts_error=RuntimeError("settings failed"))
    pythoncom = _RecordingPythonCom(events)
    _install_fake_com(monkeypatch, excel, pythoncom)

    with pytest.raises(RuntimeError, match="settings failed"):
        OfficeLifecycleManager().open_excel_workbook(Path("legacy.xls"), read_only=True)

    assert events == ["initialize", "dispatch", "quit", "uninitialize"]


def test_open_failure_preserves_primary_error_when_quit_also_fails(monkeypatch) -> None:
    events: list[str] = []
    excel = _RecordingExcel(
        events,
        open_error=RuntimeError("open failed"),
        quit_error=RuntimeError("quit failed"),
    )
    pythoncom = _RecordingPythonCom(events)
    _install_fake_com(monkeypatch, excel, pythoncom)

    with pytest.raises(RuntimeError, match="open failed") as exc_info:
        OfficeLifecycleManager().open_excel_workbook(Path("legacy.xls"), read_only=True)

    assert "quit failed" in " ".join(exc_info.value.__notes__)
    assert events == ["initialize", "dispatch", "open", "quit", "uninitialize"]


def test_dispatch_failure_uninitializes_com_once_without_excel_cleanup(monkeypatch) -> None:
    events: list[str] = []
    excel = _RecordingExcel(events, dispatch_error=RuntimeError("dispatch failed"))
    pythoncom = _RecordingPythonCom(events)
    _install_fake_com(monkeypatch, excel, pythoncom)

    with pytest.raises(RuntimeError, match="dispatch failed"):
        OfficeLifecycleManager().open_excel_workbook(Path("legacy.xls"), read_only=True)

    assert events == ["initialize", "dispatch", "uninitialize"]


class _RecordingWorkbook:
    def __init__(self, events: list[str], close_error: Exception | None = None) -> None:
        self._events = events
        self._close_error = close_error

    def Close(self, SaveChanges: bool = False) -> None:
        self._events.append(f"close:{SaveChanges}")
        if self._close_error is not None:
            raise self._close_error


class _RecordingWorkbooks:
    def __init__(self, owner: "_RecordingExcel") -> None:
        self._owner = owner

    def Open(self, **_kwargs):
        self._owner.events.append("open")
        if self._owner.open_error is not None:
            raise self._owner.open_error
        return _RecordingWorkbook(self._owner.events)


class _RecordingExcel:
    def __init__(
        self,
        events: list[str],
        *,
        close_error: Exception | None = None,
        open_error: Exception | None = None,
        quit_error: Exception | None = None,
        display_alerts_error: Exception | None = None,
        dispatch_error: Exception | None = None,
    ) -> None:
        self.events = events
        self.open_error = open_error
        self.quit_error = quit_error
        self.dispatch_error = dispatch_error
        self._display_alerts = True
        self._display_alerts_error = display_alerts_error
        self.Visible = True
        self.ScreenUpdating = True
        self.EnableEvents = True
        self.Calculation = 1
        self.Workbooks = _RecordingWorkbooks(self)
        self.workbook = _RecordingWorkbook(events, close_error)

    @property
    def DisplayAlerts(self) -> bool:
        return self._display_alerts

    @DisplayAlerts.setter
    def DisplayAlerts(self, value: bool) -> None:
        if value is False and self._display_alerts_error is not None:
            raise self._display_alerts_error
        self._display_alerts = value

    def Quit(self) -> None:
        self.events.append("quit")
        if self.quit_error is not None:
            raise self.quit_error


class _RecordingPythonCom:
    def __init__(self, events: list[str]) -> None:
        self._events = events

    def CoInitialize(self) -> None:
        self._events.append("initialize")

    def CoUninitialize(self) -> None:
        self._events.append("uninitialize")


def _install_fake_com(monkeypatch, excel: _RecordingExcel, pythoncom: _RecordingPythonCom) -> None:
    class _Client:
        @staticmethod
        def DispatchEx(name: str):
            assert name == "Excel.Application"
            excel.events.append("dispatch")
            if excel.dispatch_error is not None:
                raise excel.dispatch_error
            return excel

    class _Win32Com:
        client = _Client()

    monkeypatch.setitem(sys.modules, "pythoncom", pythoncom)
    monkeypatch.setitem(sys.modules, "win32com", _Win32Com())
    monkeypatch.setitem(sys.modules, "win32com.client", _Client())
