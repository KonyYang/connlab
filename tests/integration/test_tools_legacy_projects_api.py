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
    assert api.post("/api/tools/legacy-projects/import", json={}).status_code == 404


def test_invalid_batches_and_picker_cancel_are_non_writing(tmp_path):
    api = client()
    assert api.post("/api/tools/legacy-projects/preview", json={"roots": []}).status_code == 422
    assert api.post("/api/tools/legacy-projects/preview", json={"roots": ["x"] * 21}).status_code == 422
    api.app.dependency_overrides[get_directory_picker] = lambda: lambda: None
    assert api.post("/api/tools/legacy-projects/pick-directory").json() == {"path": None}
    assert list(tmp_path.iterdir()) == []


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
