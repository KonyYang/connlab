"""Bound only this thread's project folder dialog before its first activation."""
from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import logging

logger = logging.getLogger(__name__)


def compact_dialog_bounds(work_area):
    left, top, right, bottom = work_area
    available_width, available_height = right - left, bottom - top
    width = min(900, max(640, int(available_width * .7)), available_width - 32)
    height = min(600, max(420, int(available_height * .72)), available_height - 32)
    return left + (available_width - width) // 2, top + (available_height - height) // 2, width, height


def _hook_api():
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, wintypes.HINSTANCE, wintypes.DWORD]
    user32.SetWindowsHookExW.restype = wintypes.HANDLE
    user32.CallNextHookEx.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
    user32.CallNextHookEx.restype = ctypes.c_ssize_t
    user32.UnhookWindowsHookEx.argtypes = [wintypes.HANDLE]
    user32.UnhookWindowsHookEx.restype = wintypes.BOOL
    kernel32 = ctypes.WinDLL("kernel32")
    kernel32.GetCurrentThreadId.restype = wintypes.DWORD
    return user32, kernel32.GetCurrentThreadId()


@contextmanager
def compact_folder_dialog():
    import win32api
    import win32con
    import win32gui

    api, thread_id = _hook_api()
    positioned = False
    hook = None
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

    @callback_type
    def before_activate(code, hwnd, parameter):
        nonlocal positioned
        # WH_CBT / HCBT_ACTIVATE. Ignore every window except our exact folder dialog.
        if code == 5 and not positioned:
            try:
                if (win32gui.GetClassName(hwnd) == "#32770"
                        and win32gui.GetWindowText(hwnd) == "Import Projects — choose one project folder"):
                    positioned = True
                    monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
                    bounds = compact_dialog_bounds(win32api.GetMonitorInfo(monitor)["Work"])
                    win32gui.SetWindowPos(hwnd, 0, *bounds, win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
            except (OSError, win32gui.error):
                # Sizing is cosmetic: retain the usable Windows dialog if positioning fails.
                logger.warning("Could not apply compact folder dialog geometry", exc_info=True)
        return api.CallNextHookEx(hook, code, hwnd, parameter)

    # A nonzero thread ID keeps the hook local; no DLL injection or global input hook.
    hook = api.SetWindowsHookExW(5, before_activate, None, thread_id)
    if not hook:
        logger.warning("Could not attach folder dialog layout hook: %s", ctypes.get_last_error())
    try:
        yield
    finally:
        if hook and not api.UnhookWindowsHookEx(hook):
            logger.warning("Could not detach folder dialog layout hook: %s", ctypes.get_last_error())
