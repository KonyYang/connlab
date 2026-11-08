import pytest

from backend.infrastructure.files.windows_dialog_layout import compact_dialog_bounds


def test_large_monitor_uses_compact_centered_dialog():
    assert compact_dialog_bounds((0, 0, 1920, 1040)) == (510, 220, 900, 600)


def test_secondary_monitor_retains_its_negative_origin():
    assert compact_dialog_bounds((-1920, 0, 0, 1040)) == (-1410, 220, 900, 600)


def test_small_work_area_keeps_dialog_within_screen():
    x, y, width, height = compact_dialog_bounds((0, 0, 800, 560))
    assert (width, height) == (640, 420)
    assert x > 0 and y > 0
    assert x + width < 800 and y + height < 560


def test_native_layout_hook_is_local_one_shot_and_released(monkeypatch):
    import sys
    if sys.platform != "win32":
        pytest.skip("Windows layout adapter")
    from types import SimpleNamespace
    import win32gui
    import win32api
    from backend.infrastructure.files import windows_dialog_layout as layout
    events = []
    callbacks = []
    def register(kind, callback, module, thread):
        assert thread == 1234 and module is None
        callbacks.append(callback)
        return 55
    api = SimpleNamespace(SetWindowsHookExW=register,
        CallNextHookEx=lambda *args: 0,
        UnhookWindowsHookEx=lambda handle: events.append(("unhook", handle)) or 1)
    monkeypatch.setattr(layout, "_hook_api", lambda: (api, 1234))
    monkeypatch.setattr(win32gui, "GetClassName", lambda hwnd: "#32770")
    monkeypatch.setattr(win32gui, "GetWindowText", lambda hwnd: "Import Projects — choose one project folder" if hwnd == 321 else "Other dialog")
    monkeypatch.setattr(win32api, "MonitorFromWindow", lambda hwnd, flags: 1)
    monkeypatch.setattr(win32api, "GetMonitorInfo", lambda monitor: {"Work": (0, 0, 1920, 1040)})
    monkeypatch.setattr(win32gui, "SetWindowPos", lambda *args: events.append(("position", args)))
    with pytest.raises(RuntimeError, match="show failed"):
        with layout.compact_folder_dialog():
            callbacks[0](-1, 321, 0)
            callbacks[0](5, 999, 0)
            callbacks[0](5, 321, 0)
            callbacks[0](5, 321, 0)
            raise RuntimeError("show failed")
    assert len([item for item in events if item[0] == "position"]) == 1
    assert events[-1] == ("unhook", 55)
