from pathlib import Path
from types import SimpleNamespace
import ctypes
from contextlib import nullcontext
import sys

import pytest

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows native dialog adapter")


@pytest.fixture
def native(monkeypatch):
    from backend.infrastructure.files import windows_project_folder_dialog as dialog
    import pythoncom
    import win32gui
    events = []
    buffer = ctypes.create_unicode_buffer(r"D:\fixture\项目")
    outcome = {"show": 0}
    def create(_clsid, _outer, _context, _iid, result):
        result._obj.value = 1
        return 0
    def call(interface, index, result_type, argtypes=(), *args):
        if index == 2:
            events.append(("release", interface.value))
        elif index == 3:
            events.append(("owner", args[0]))
            return outcome["show"]
        elif index == 4:
            events.append(("filter", args[1][0].pattern))
        elif index == 9:
            events.append(("flags", args[0]))
        elif index == 17:
            events.append(("title", args[0]))
        elif index == 10:
            args[0]._obj.value = 0
        elif index == 20:
            args[0]._obj.value = 2
        elif index == 5:
            args[1]._obj.value = ctypes.addressof(buffer)
        return 0
    monkeypatch.setattr(pythoncom, "CoInitializeEx", lambda flags: events.append("initialize"))
    monkeypatch.setattr(pythoncom, "CoUninitialize", lambda: events.append("uninitialize"))
    monkeypatch.setattr(win32gui, "GetForegroundWindow", lambda: 321)
    monkeypatch.setattr(dialog, "_ole32", lambda: SimpleNamespace(CoCreateInstance=create, CoTaskMemFree=lambda value: events.append("free")))
    monkeypatch.setattr(dialog, "_call", call)
    monkeypatch.setattr(dialog, "compact_folder_dialog", lambda *args, **kwargs: nullcontext())
    return dialog, events, outcome


def test_selected_folder_releases_native_resources(native):
    dialog, events, _ = native
    assert dialog.pick_project_folder() == Path(r"D:\fixture\项目")
    assert ("owner", 321) in events
    assert ("release", 1) in events and ("release", 2) in events
    assert "free" in events
    assert events[-1] == "uninitialize"


def test_cancellation_is_quiet_and_releases_dialog(native):
    dialog, events, outcome = native
    outcome["show"] = -2147023673  # HRESULT_FROM_WIN32(ERROR_CANCELLED)
    assert dialog.pick_project_folder() is None
    assert ("release", 1) in events
    assert "free" not in events
    assert events[-1] == "uninitialize"


def test_native_failure_is_not_treated_as_cancel(native):
    dialog, events, outcome = native
    outcome["show"] = -2147467259
    with pytest.raises(OSError):
        dialog.pick_project_folder()
    assert ("release", 1) in events
    assert events[-1] == "uninitialize"


@pytest.mark.parametrize("kind", ["file", "directory"])
@pytest.mark.parametrize("cancelled", [False, True])
def test_encryption_picker_uses_the_native_owned_dialog(native, monkeypatch, kind, cancelled):
    import win32gui
    from win32com.shell import shell
    from backend.infrastructure.files.windows_path_picker import WindowsPathPicker

    def legacy_picker(*args, **kwargs):
        pytest.fail("Encryption must use the owned Windows common item dialog")

    monkeypatch.setattr(shell, "SHBrowseForFolder", legacy_picker)
    monkeypatch.setattr(win32gui, "GetOpenFileNameW", legacy_picker)
    _, events, outcome = native
    if cancelled:
        outcome["show"] = -2147023673
    picker = WindowsPathPicker()
    selected = (picker.pick_encryption_file() if kind == "file" else picker.pick_encryption_directory())
    assert selected == (None if cancelled else Path(r"D:\fixture\项目"))
    assert ("owner", 321) in events
    assert any(event[0] == "title" and "encrypt" in event[1].lower() for event in events)
    flags = next(event[1] for event in events if event[0] == "flags")
    if kind == "file":
        assert flags & 0x1000 and not flags & 0x20
        assert ("filter", "*.doc;*.docx;*.xls;*.xlsx;*.ppt;*.pptx") in events
    else:
        assert flags & 0x20 and not flags & 0x1000
    assert events[-1] == "uninitialize"
