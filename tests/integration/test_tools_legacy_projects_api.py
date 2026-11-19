import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.routes_tools_legacy_projects import router, get_directory_picker


def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_cancelled_picker_returns_no_folder():
    api = client()
    api.app.dependency_overrides[get_directory_picker] = lambda: lambda: None
    assert api.post("/api/tools/legacy-projects/pick-directory").json() == {"path": None}


@pytest.mark.skipif(os.name != "nt", reason="Windows native picker boundary")
@pytest.mark.parametrize("cancelled", [False, True])
def test_project_picker_uses_compact_windows_folder_browser(monkeypatch, tmp_path, cancelled):
    from win32com.shell import shell
    from backend.infrastructure.files import windows_project_folder_dialog as dialog
    from backend.infrastructure.files.windows_path_picker import WindowsPathPicker, filedialog

    selected = tmp_path / "DL-2026-09-032 项目"
    calls = []

    def choose():
        calls.append(True)
        return None if cancelled else selected

    def forbidden(*args, **kwargs):
        raise AssertionError("The legacy or Tk picker must not open during this test")

    monkeypatch.setattr(dialog, "pick_project_folder", choose)
    monkeypatch.setattr(shell, "SHBrowseForFolder", forbidden)
    monkeypatch.setattr(filedialog, "askdirectory", forbidden)

    assert WindowsPathPicker().pick_legacy_project_directory() == (
        None if cancelled else selected
    )
    assert calls == [True]


def test_registered_application_picker_never_requests_database_or_settings(tmp_path):
    from backend.api.main import app
    from backend.api.dependencies import get_session, get_settings
    original = app.dependency_overrides.copy()

    def forbidden():
        raise AssertionError("The shared folder picker must not initialize the business store")

    app.dependency_overrides[get_session] = forbidden
    app.dependency_overrides[get_settings] = forbidden
    app.dependency_overrides[get_directory_picker] = lambda: lambda: tmp_path
    try:
        response = TestClient(app).post("/api/tools/legacy-projects/pick-directory")
        assert response.status_code == 200
        assert response.json() == {"path": str(tmp_path)}
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original)
