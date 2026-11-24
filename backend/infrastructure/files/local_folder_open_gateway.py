"""Local folder open gateway for operator workstation actions."""

from __future__ import annotations

import logging
import ntpath
import os
import time
from pathlib import Path
from typing import Callable

from backend.application.project_folder_open_service import ProjectFolderOpenResult


logger = logging.getLogger(__name__)


class LocalFolderOpenGateway:
    """Open an existing directory without creating or modifying files."""

    def __init__(self, *, launcher: Callable[[str], None] | None = None) -> None:
        """Create the gateway with an optional launcher for tests."""
        self._launcher = launcher or _windows_startfile

    def open_directory(self, path: Path) -> ProjectFolderOpenResult:
        """Open an existing local directory if the environment supports it."""
        if not path.exists() or not path.is_dir():
            return ProjectFolderOpenResult(
                project_id="",
                status="blocked",
                message="Project folder is not available yet.",
                local_official_folder_path=path,
            )
        try:
            self._launcher(str(path))
        except RuntimeError as exc:
            return ProjectFolderOpenResult(
                project_id="",
                status="unsupported",
                message=str(exc),
                local_official_folder_path=path,
            )
        except OSError as exc:
            return ProjectFolderOpenResult(
                project_id="",
                status="blocked",
                message=str(exc),
                local_official_folder_path=path,
            )
        return ProjectFolderOpenResult(
            project_id="",
            status="opened",
            message="Project folder opened.",
            local_official_folder_path=path,
        )


def _windows_startfile(path: str) -> None:
    launcher = getattr(os, "startfile", None)
    if launcher is None:
        raise RuntimeError("Open folder is only available on the local Windows workstation.")
    launcher(path)

    _show_explorer_folder(path)


def _show_explorer_folder(path: str) -> None:
    """Restore and raise the Explorer window that displays the requested directory."""
    try:
        import pythoncom
        import pywintypes
        import win32com.client
        import win32con
        import win32gui
    except ImportError:
        logger.warning("Windows Explorer window activation is unavailable", exc_info=True)
        return

    target = ntpath.normcase(ntpath.normpath(path))
    try:
        # The HTTP request runs on a worker thread, so initialize COM on that thread.
        pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
        try:
            shell = win32com.client.Dispatch("Shell.Application")
            # The launch returns before Explorer registers or navigates its window.
            deadline = time.monotonic() + 1.5
            while True:
                for window in shell.Windows():
                    try:
                        hwnd = window.HWND
                        if win32gui.GetClassName(hwnd) != "CabinetWClass":
                            continue
                        current = window.Document.Folder.Self.Path
                    except (AttributeError, pywintypes.com_error, win32gui.error):
                        continue  # Explorer can close or navigate a window during enumeration.
                    if not current or ntpath.normcase(ntpath.normpath(current)) != target:
                        continue

                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    try:
                        win32gui.SetForegroundWindow(hwnd)
                    except win32gui.error:
                        # Windows can deny keyboard focus to the background HTTP process.
                        win32gui.SetWindowPos(
                            hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                            | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW,
                        )
                    return

                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    logger.debug("No matching Explorer window appeared after opening a folder")
                    return
                time.sleep(min(0.05, remaining))
        finally:
            shell = window = None
            pythoncom.CoUninitialize()
    except (pywintypes.com_error, OSError, win32gui.error):
        # The shell accepted the launch. Do not report it as failed over optional activation.
        logger.warning("Could not bring the opened Explorer folder forward", exc_info=True)
