"""Desktop-host path picker bridge for Settings file locations."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Protocol


FOLDER_RESOURCE_TYPES = frozenset(
    {
        "project_folder_template",
        "project_output_root",
        "official_public_drive_root",
    }
)


class DesktopPathPickerPort(Protocol):
    """Native picker operations required by the desktop bridge."""

    def pick_file(self, resource_type: str) -> Path | None:
        """Return one selected file path, or None when cancelled."""

    def pick_directory(self, resource_type: str) -> Path | None:
        """Return one selected directory path, or None when cancelled."""

    def pick_matrix_import_source(self, initial_directory: Path | None) -> Path | None:
        """Return a Matrix source selected from an optional initial directory."""


class DesktopPathPickerApi:
    """JavaScript-exposed API for Settings file and folder selection."""

    def __init__(self, *, picker: DesktopPathPickerPort) -> None:
        """Create the bridge API with a native path picker implementation."""
        self._picker = picker

    def pickExternalResourcePath(self, resource_type: str) -> str | None:
        """Return a selected absolute path for the requested resource type."""
        if resource_type in FOLDER_RESOURCE_TYPES:
            selected = self._picker.pick_directory(resource_type)
        else:
            selected = self._picker.pick_file(resource_type)
        if selected is None:
            return None
        return str(selected)

    def pickMatrixImportSource(self, initial_directory: str | None) -> str | None:
        """Return a selected Matrix source without trusting an invalid directory."""
        candidate = Path(initial_directory) if initial_directory else None
        safe_directory = candidate if candidate is not None and candidate.is_dir() else None
        selected = self._picker.pick_matrix_import_source(safe_directory)
        return str(selected) if selected is not None else None


class PyWebViewPathPicker:
    """Native picker implementation backed by the active PyWebView window."""

    def __init__(self, *, window_provider: Callable[[], object | None]) -> None:
        """Create a picker that resolves the current desktop window lazily."""
        self._window_provider = window_provider

    def pick_file(self, resource_type: str) -> Path | None:
        """Return one selected file path from a native open-file dialog."""
        webview = _load_webview()
        window = _require_window(self._window_provider())
        selection = window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=_file_types(resource_type),
        )
        return _first_selected_path(selection)

    def pick_directory(self, resource_type: str) -> Path | None:
        """Return one selected directory path from a native folder dialog."""
        webview = _load_webview()
        window = _require_window(self._window_provider())
        selection = window.create_file_dialog(
            webview.FOLDER_DIALOG,
            allow_multiple=False,
        )
        return _first_selected_path(selection)

    def pick_matrix_import_source(self, initial_directory: Path | None) -> Path | None:
        """Return one Matrix source using the project directory when available."""
        webview = _load_webview()
        window = _require_window(self._window_provider())
        selection = window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            directory=str(initial_directory) if initial_directory is not None else "",
            file_types=(
                "Matrix source documents (*.pdf;*.doc;*.docx;*.xlsx)",
                "All files (*.*)",
            ),
        )
        return _first_selected_path(selection)


def _load_webview() -> object:
    try:
        import webview  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "ConnLab desktop shell requires pywebview. Install the desktop "
            "runtime before running 'py -m backend.desktop.shell'."
        ) from exc
    return webview


def _require_window(window: object | None) -> object:
    if window is None:
        raise RuntimeError("ConnLab desktop window is not available for path picking.")
    return window


def _first_selected_path(selection: object) -> Path | None:
    if selection is None or selection == "":
        return None
    if isinstance(selection, (list, tuple)):
        if not selection:
            return None
        return Path(str(selection[0]))
    return Path(str(selection))


def _file_types(resource_type: str) -> tuple[str, ...]:
    if resource_type == "application_form_template":
        return ("Word documents (*.docx)", "All files (*.*)")
    if resource_type in {
        "ltr_workbook",
        "standard_record_excel",
        "equipment_calibration_excel",
    }:
        return ("Excel workbooks (*.xlsx;*.xls)", "All files (*.*)")
    return ("Excel workbooks (*.xlsx)", "All files (*.*)")
