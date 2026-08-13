from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from backend.desktop.shell import desktop_bridge_script, run_desktop_shell
from backend.desktop.path_picker_api import DesktopPathPickerApi, _file_types


def test_desktop_path_picker_api_routes_folder_resources_to_directory_picker() -> None:
    """Folder-backed Settings resources use the native directory picker."""
    picker = _Picker(file_path=Path("C:/files/source.xlsx"), directory_path=Path("C:/templates"))
    api = DesktopPathPickerApi(picker=picker)

    selected = api.pickExternalResourcePath("project_folder_template")

    assert selected == "C:\\templates"
    assert picker.file_requests == []
    assert picker.directory_requests == ["project_folder_template"]


def test_desktop_path_picker_api_routes_file_resources_to_file_picker() -> None:
    """File-backed Settings resources use the native file picker."""
    picker = _Picker(file_path=Path("C:/files/ltr.xlsx"), directory_path=Path("C:/templates"))
    api = DesktopPathPickerApi(picker=picker)

    selected = api.pickExternalResourcePath("ltr_workbook")

    assert selected == "C:\\files\\ltr.xlsx"
    assert picker.file_requests == ["ltr_workbook"]
    assert picker.directory_requests == []


def test_desktop_path_picker_api_returns_none_when_cancelled() -> None:
    """Picker cancellation returns null-compatible None to the frontend bridge."""
    picker = _Picker(file_path=None, directory_path=None)
    api = DesktopPathPickerApi(picker=picker)

    selected = api.pickExternalResourcePath("project_output_root")

    assert selected is None
    assert picker.directory_requests == ["project_output_root"]


def test_matrix_import_picker_passes_existing_initial_directory(tmp_path: Path) -> None:
    picker = _Picker(file_path=Path("C:/files/spec.pdf"), directory_path=None)
    api = DesktopPathPickerApi(picker=picker)

    selected = api.pickMatrixImportSource(str(tmp_path))

    assert selected == "C:\\files\\spec.pdf"
    assert picker.matrix_requests == [tmp_path]


def test_matrix_import_picker_ignores_unavailable_initial_directory(tmp_path: Path) -> None:
    picker = _Picker(file_path=None, directory_path=None)
    api = DesktopPathPickerApi(picker=picker)

    assert api.pickMatrixImportSource(str(tmp_path / "missing")) is None
    assert picker.matrix_requests == [None]


def test_desktop_shell_reports_missing_pywebview_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    """The shell fails clearly when the optional desktop runtime is absent."""
    original_import = builtins.__import__

    def guarded_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "webview":
            raise ImportError("missing test webview")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    with pytest.raises(RuntimeError, match="requires pywebview"):
        run_desktop_shell()


def test_desktop_bridge_script_installs_frontend_contract() -> None:
    """The shell injects the bridge name expected by the React frontend."""
    script = desktop_bridge_script()

    assert "window.connlabDesktopPathPicker" in script
    assert "window.pywebview.api.pickExternalResourcePath" in script
    assert "window.pywebview.api.pickMatrixImportSource" in script


@pytest.mark.parametrize(
    "resource_type",
    ["standard_record_excel", "equipment_calibration_excel", "ltr_workbook"],
)
def test_excel_resource_picker_accepts_xlsx_and_xls(resource_type: str) -> None:
    assert _file_types(resource_type) == (
        "Excel workbooks (*.xlsx;*.xls)",
        "All files (*.*)",
    )


def test_unrelated_file_picker_filter_remains_xlsx_only() -> None:
    assert _file_types("other_excel_resource") == (
        "Excel workbooks (*.xlsx)",
        "All files (*.*)",
    )


class _Picker:
    def __init__(self, *, file_path: Path | None, directory_path: Path | None) -> None:
        self._file_path = file_path
        self._directory_path = directory_path
        self.file_requests: list[str] = []
        self.directory_requests: list[str] = []
        self.matrix_requests: list[Path | None] = []

    def pick_file(self, resource_type: str) -> Path | None:
        self.file_requests.append(resource_type)
        return self._file_path

    def pick_directory(self, resource_type: str) -> Path | None:
        self.directory_requests.append(resource_type)
        return self._directory_path

    def pick_matrix_import_source(self, initial_directory: Path | None) -> Path | None:
        self.matrix_requests.append(initial_directory)
        return self._file_path
