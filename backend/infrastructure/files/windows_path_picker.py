"""Windows-native file and folder picker for local operator paths."""

from __future__ import annotations

from pathlib import Path
from tkinter import Tk, filedialog
from typing import Callable

from backend.domain import ExternalResourceType


class WindowsPathPicker:
    """Open local Windows file and folder pickers."""

    def pick_encryption_file(self) -> Path | None:
        """Select one original Office file for a separate encrypted sibling."""
        import pythoncom
        import win32con
        import win32gui

        pythoncom.CoInitialize()
        try:
            selected, _, _ = win32gui.GetOpenFileNameW(
                Title="Select Office file: save encrypted copy beside original",
                Filter="Office files\0*.doc;*.docx;*.xls;*.xlsx;*.ppt;*.pptx\0All files\0*.*\0",
                Flags=win32con.OFN_EXPLORER | win32con.OFN_FILEMUSTEXIST
                    | win32con.OFN_PATHMUSTEXIST | win32con.OFN_NOCHANGEDIR,
            )
            return Path(selected) if selected else None
        except win32gui.error as exc:
            if exc.winerror == 0:
                return None
            raise RuntimeError("Could not open the Office file picker.") from exc
        finally:
            pythoncom.CoUninitialize()

    def pick_encryption_directory(self) -> Path | None:
        """Choose where separate encrypted siblings will be saved."""
        import pythoncom
        from win32com.shell import shell, shellcon

        # API handlers run on worker threads; own the native picker COM lifetime
        # and avoid an invisible Tk owner window for this local write operation.
        pythoncom.CoInitialize()
        try:
            selection = shell.SHBrowseForFolder(0, None,
                "Choose folder: encrypted copies will be saved beside originals",
                # BIF_NEWDIALOGSTYLE is absent from some bundled pywin32 constants.
                shellcon.BIF_RETURNONLYFSDIRS | 0x0040 | shellcon.BIF_EDITBOX,
                None, None)
            if not selection or not selection[0]:
                return None
            return Path(shell.SHGetPathFromIDListW(selection[0]))
        finally:
            pythoncom.CoUninitialize()

    def pick_legacy_project_directory(self) -> Path | None:
        """Choose one existing project with the compact Windows folder browser."""
        import pythoncom
        from win32com.shell import shell, shellcon

        pythoncom.CoInitialize()
        try:
            selection = shell.SHBrowseForFolder(
                0,
                None,
                "Choose one project folder",
                shellcon.BIF_RETURNONLYFSDIRS | shellcon.BIF_EDITBOX,
                None,
                None,
            )
            if not selection or not selection[0]:
                return None
            return Path(shell.SHGetPathFromIDListW(selection[0]))
        finally:
            pythoncom.CoUninitialize()

    def pick_file(self, resource_type: ExternalResourceType) -> Path | None:
        """Return one selected file path, or None when cancelled."""
        file_types = _file_types(resource_type)
        selection = self._run_dialog(
            lambda: filedialog.askopenfilename(
                title=_file_dialog_title(resource_type),
                filetypes=file_types,
            )
        )
        if not selection:
            return None
        return Path(selection)

    def pick_directory(self, resource_type: ExternalResourceType) -> Path | None:
        """Return one selected directory path, or None when cancelled."""
        selection = self._run_dialog(
            lambda: filedialog.askdirectory(
                title=_directory_dialog_title(resource_type),
                mustexist=True,
            )
        )
        if not selection:
            return None
        return Path(selection)

    def _run_dialog(self, dialog: Callable[[], str]) -> str:
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            return str(dialog())
        finally:
            root.destroy()


def _file_dialog_title(resource_type: ExternalResourceType) -> str:
    if resource_type is ExternalResourceType.LTR_WORKBOOK:
        return "Select LTR registration workbook"
    if resource_type is ExternalResourceType.STANDARD_RECORD_EXCEL:
        return "Select Standard record Excel"
    if resource_type is ExternalResourceType.EQUIPMENT_CALIBRATION_EXCEL:
        return "Select Equipment calibration Excel"
    if resource_type is ExternalResourceType.APPLICATION_FORM_TEMPLATE:
        return "Select application form template"
    return "Select file"


def _directory_dialog_title(resource_type: ExternalResourceType) -> str:
    if resource_type is ExternalResourceType.PROJECT_OUTPUT_ROOT:
        return "Select Project default save location"
    if resource_type is ExternalResourceType.PROJECT_FOLDER_TEMPLATE:
        return "Select Template folder"
    if resource_type is ExternalResourceType.OFFICIAL_PUBLIC_DRIVE_ROOT:
        return "Select Public Project locations"
    return "Select folder"


def _file_types(
    resource_type: ExternalResourceType,
) -> list[tuple[str, str]]:
    if resource_type is ExternalResourceType.APPLICATION_FORM_TEMPLATE:
        return [
            ("Word document", "*.docx"),
            ("All files", "*.*"),
        ]
    if resource_type is ExternalResourceType.LTR_WORKBOOK:
        return [
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*"),
        ]
    return [
        ("Excel workbook", "*.xlsx"),
        ("All files", "*.*"),
    ]
