"""Windows-native file and folder picker for local operator paths."""

from __future__ import annotations

from pathlib import Path
from tkinter import Tk, filedialog
from typing import Callable

from backend.domain import ExternalResourceType


class WindowsPathPicker:
    """Open local Windows file and folder pickers."""

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
