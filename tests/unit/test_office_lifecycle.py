import sys
from pathlib import Path

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
