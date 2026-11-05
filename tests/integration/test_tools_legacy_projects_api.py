import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.routes_tools_legacy_projects import router, get_directory_picker


def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_preview_reads_a_selected_folder_without_registration_or_writes(tmp_path):
    folder = tmp_path / "DL-2021-01-030UC Old project"
    folder.mkdir()
    source = folder / "report.docx"
    source.write_bytes(b"original")
    api = client()
    response = api.post("/api/tools/legacy-projects/preview", json={"roots": [str(tmp_path)]})
    assert response.status_code == 200
    assert response.json()["read_only"] is True
    assert response.json()["projects"][0]["number"] == "DL-2021-01-030UC"
    assert source.read_bytes() == b"original"
    assert sorted(p.name for p in folder.iterdir()) == ["report.docx"]


def test_invalid_batches_and_picker_cancel_are_non_writing(tmp_path):
    api = client()
    assert api.post("/api/tools/legacy-projects/preview", json={"roots": []}).status_code == 422
    assert api.post("/api/tools/legacy-projects/preview", json={"roots": ["x"] * 21}).status_code == 422
    api.app.dependency_overrides[get_directory_picker] = lambda: lambda: None
    assert api.post("/api/tools/legacy-projects/pick-directory").json() == {"path": None}
    assert list(tmp_path.iterdir()) == []


@pytest.mark.skipif(os.name != "nt", reason="Windows native picker boundary")
@pytest.mark.parametrize("cancelled", [False, True])
def test_project_picker_uses_compact_windows_folder_browser(monkeypatch, tmp_path, cancelled):
    import pythoncom
    from win32com.shell import shell, shellcon
    from backend.infrastructure.files.windows_path_picker import WindowsPathPicker, filedialog

    selected = tmp_path / "DL-2026-09-032 项目"
    released = []
    calls = []
    monkeypatch.setattr(pythoncom, "CoInitialize", lambda: None)
    monkeypatch.setattr(pythoncom, "CoUninitialize", lambda: released.append(True))

    def choose(*args):
        calls.append(args)
        return None if cancelled else (b"selected", "name", 0)

    monkeypatch.setattr(shell, "SHBrowseForFolder", choose)
    monkeypatch.setattr(shell, "SHGetPathFromIDListW", lambda value: str(selected))
    monkeypatch.setattr(
        filedialog,
        "askdirectory",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("Tk folder dialog not expected")),
    )

    assert WindowsPathPicker().pick_legacy_project_directory() == (
        None if cancelled else selected
    )
    assert calls[0][2] == "Choose one project folder"
    assert calls[0][3] & shellcon.BIF_RETURNONLYFSDIRS
    assert calls[0][3] & shellcon.BIF_EDITBOX
    assert not calls[0][3] & 0x0040
    assert released == [True]


def test_registered_application_preview_never_requests_database_or_settings(tmp_path):
    from backend.api.main import app
    from backend.api.dependencies import get_session, get_settings
    original = app.dependency_overrides.copy()

    def forbidden():
        raise AssertionError("Read-only preview must not initialize or commit the business store")

    app.dependency_overrides[get_session] = forbidden
    app.dependency_overrides[get_settings] = forbidden
    folder = tmp_path / "DL-2021-01-030UC"
    folder.mkdir()
    try:
        response = TestClient(app).post("/api/tools/legacy-projects/preview", json={"roots": [str(folder)]})
        assert response.status_code == 200
        assert response.json()["projects"][0]["number"] == "DL-2021-01-030UC"
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original)
