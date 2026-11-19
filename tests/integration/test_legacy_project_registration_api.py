import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.api.routes_tools_legacy_projects import router as tools_router
from backend.api.routes_legacy_projects import router, get_legacy_registration_service
from backend.application.legacy_project_registration_service import LegacyProjectRegistrationService
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.repositories.legacy_projects import LegacyProjectRepository
from backend.infrastructure.files.legacy_project_preview_gateway import LegacyProjectPreviewGateway
from backend.infrastructure.files.local_folder_open_gateway import LocalFolderOpenGateway


@pytest.fixture
def api(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'api.db'}", connect_args={"check_same_thread": False})
    init_db(engine)
    app = FastAPI()
    app.include_router(tools_router)
    app.include_router(router)
    launched = []
    def sessions():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = sessions
    from fastapi import Depends
    def services(session=Depends(get_session)):
        return LegacyProjectRegistrationService(LegacyProjectRepository(session), LegacyProjectPreviewGateway(), LocalFolderOpenGateway(launcher=launched.append))
    app.dependency_overrides[get_legacy_registration_service] = services
    def seed_history(path):
        with Session(engine) as session:
            service = services(session)
            row = service.plan([str(path)])["projects"][0]
            choices = [{"folder": str(path), "fingerprint": row["fingerprint"]}]
            assert service.register([str(path)], choices)["counts"]["added"] == 1
    yield TestClient(app), launched, seed_history
    engine.dispose()


def test_existing_history_can_be_searched_opened_and_reconnected(api, tmp_path):
    client, launched, seed_history = api
    path = tmp_path / "Old manual project"
    path.mkdir()
    (path / "report.pdf").write_bytes(b"untouched")
    seed_history(path)
    rows = client.get("/api/legacy-projects", params={"q": "manual"}).json()
    record_id = rows[0]["record_id"]
    assert rows[0]["name"] == "Old manual project"
    assert rows[0]["number"] is None
    assert client.get(f"/api/legacy-projects/{record_id}").status_code == 200
    assert client.post(f"/api/legacy-projects/{record_id}/open-folder").json()["status"] == "opened"
    assert launched == [str(path)]
    target = tmp_path / "Moved"
    target.mkdir()
    assert client.post(f"/api/legacy-projects/{record_id}/location", json={"folder": str(target), "expected_revision": 1}).json()["revision"] == 2
    assert client.post(f"/api/legacy-projects/{record_id}/location", json={"folder": str(path), "expected_revision": 1}).status_code == 409
    assert client.get("/api/legacy-projects/business-project-id").status_code == 404
    assert client.post("/api/legacy-projects/business-project-id/location", json={"folder": str(path), "expected_revision": 1}).status_code == 404
    assert (path / "report.pdf").read_bytes() == b"untouched"


def test_retired_tools_routes_cannot_register_an_external_folder(api, tmp_path):
    client, _, _ = api
    path = str(tmp_path)
    folders = {"folders": [path]}
    calls = [
        ("preview", {"roots": [path]}),
        ("registration-plan", folders),
        ("import", {**folders, "selected": [{"folder": path, "fingerprint": "0" * 64}]}),
    ]
    for route, payload in calls:
        response = client.post(f"/api/tools/legacy-projects/{route}", json=payload)
        assert response.status_code == 404, (route, response.text)
    assert client.get("/api/legacy-projects").json() == []
