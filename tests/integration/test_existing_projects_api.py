"""Real HTTP contracts over disposable database/folder storage only."""
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from backend.api.main import app
from backend.api.dependencies import get_session, get_settings
from backend.infrastructure.storage.database import init_db, create_session_factory
from backend.shared.config import Settings


@pytest.fixture
def client(tmp_path):
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    init_db(engine)
    sessions = create_session_factory(engine)
    def session_override():
        with sessions() as session:
            try:
                yield session
                session.commit()
            except BaseException:
                session.rollback()
                raise
    settings = Settings(data_dir=tmp_path / "data",projects_dir=tmp_path / "projects",templates_dir=tmp_path / "templates",database_path=tmp_path / "unused.sqlite3")
    app.dependency_overrides[get_session] = session_override
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        with TestClient(app) as http:
            yield http
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def intake(client, path, number="HIST-001", **decisions):
    preview = client.post("/api/existing-projects/preview", json={"path":str(path)})
    assert preview.status_code == 200, preview.text
    request = {"path":str(path),"token":preview.json()["token"],"action":"register","management_number":number,**decisions}
    return client.post("/api/existing-projects/register",json=request), request


def test_manual_intake_repeat_browse_download_hidden_protection_and_restore(client,tmp_path):
    folder = tmp_path / "source"; folder.mkdir(); (folder / "result.txt").write_bytes(b"do not change")
    scan = client.post("/api/existing-projects/scan", json={"roots":[str(folder)],"depth":0})
    assert scan.status_code == 200
    assert client.get("/api/projects").json() == []
    response, request = intake(client,folder)
    assert response.status_code == 200, response.text
    registered = response.json(); pid=registered["project_id"]; lid=registered["location_id"]
    assert client.post("/api/existing-projects/register",json=request).json() == registered
    assert len(client.get("/api/existing-projects/locations").json()) == 1
    assert client.get(f"/api/projects/{pid}").status_code == 200
    registry_preview = client.get(f"/api/project-registry/{pid}/preview?action=trash").json()
    assert "LTR records retained: 0" in registry_preview["retained_data"]
    assert "Confirmed Matrix versions retained: 0" in registry_preview["retained_data"]
    files=client.get(f"/api/existing-projects/locations/{lid}/files").json()
    assert files["entries"][0]["name"] == "result.txt"
    download=client.get(f"/api/existing-projects/locations/{lid}/download",params={"relative":"result.txt"})
    assert download.content == b"do not change"
    assert "attachment" in download.headers["content-disposition"]
    assert client.get(f"/api/existing-projects/locations/{lid}/download",params={"relative":"../else.txt"}).status_code == 409
    assert client.get(f"/api/existing-projects/locations/{lid}/files",params={"relative":"../"}).status_code == 409
    preview=client.get(f"/api/project-registry/{pid}/preview?action=trash").json()
    assert client.post(f"/api/project-registry/{pid}/trash",json={"token":preview["token"],"reason":"Old temporary record"}).status_code == 200
    assert client.get("/api/existing-projects/locations").json()[0]["registry_state"] == "trash"
    assert client.post("/api/existing-projects/register",json=request).status_code == 409
    assert client.post(f"/api/existing-projects/locations/{lid}/relocation-preview",json={"path":str(folder)}).status_code == 409
    assert client.get(f"/api/existing-projects/locations/{lid}/files").status_code == 200
    restore=client.get(f"/api/project-registry/{pid}/preview?action=restore").json()
    assert client.post(f"/api/project-registry/{pid}/restore",json={"token":restore["token"]}).status_code == 200
    assert (folder / "result.txt").read_bytes() == b"do not change"
    assert not (folder / ".connlab").exists()


def test_foreign_identity_collision_requires_explicit_decision_and_managed_number_is_unique(client,tmp_path):
    source={"schema_version":1,"project_id":"b"*32,"dl_number":"DL-2026-09-001","official_project_folder_path":"Z:/another/pc"}
    folders=[]
    for name in ["one","two"]:
        folder=tmp_path/name; folder.mkdir(); (folder/".connlab").mkdir(); (folder/".connlab"/"manifest.json").write_text(json.dumps(source));folders.append(folder)
    first,_=intake(client,folders[0],"DL-2026-09-001")
    assert first.status_code == 200 and first.json()["project_id"] == "b"*32
    collision,_=intake(client,folders[1],"LOCAL-B")
    assert collision.status_code == 409
    taken,_=intake(client,folders[1],"DL-2026-09-001",action="independent")
    assert taken.status_code == 409
    new,_=intake(client,folders[1],"LOCAL-B",action="independent")
    assert new.status_code == 200
    assert new.json()["project_id"] != "b"*32
    assert len(client.get("/api/projects").json()) == 2


def test_changed_target_invalidates_preview_and_moved_folder_can_rebind(client,tmp_path):
    folder=tmp_path/"original";folder.mkdir();(folder/"keep.txt").write_bytes(b"keep")
    added,_=intake(client,folder);lid=added.json()["location_id"]
    moved=tmp_path/"moved";folder.rename(moved)
    assert client.get(f"/api/existing-projects/locations/{lid}/files").status_code == 409
    preview=client.post(f"/api/existing-projects/locations/{lid}/relocation-preview",json={"path":str(moved)})
    assert preview.status_code == 200,preview.text
    changed=client.post(f"/api/existing-projects/locations/{lid}/relocate",json={"path":str(moved),"token":preview.json()["token"]})
    assert changed.status_code == 200,changed.text
    assert changed.json()["project_id"] == added.json()["project_id"]
    assert client.get(f"/api/existing-projects/locations/{lid}/files").status_code == 200
    assert (moved/"keep.txt").read_bytes() == b"keep"


def test_download_closes_source_handle_when_first_asgi_frame_cannot_be_sent(tmp_path):
    import asyncio
    from starlette.requests import ClientDisconnect
    from backend.api.routes_existing_projects import download
    source=tmp_path/"original.txt";source.write_bytes(b"original")
    opened=source.open("rb")
    class Files:
        def open_file(self,location_id,relative):return opened,"original.txt"
    response=download("location","original.txt",service=Files())
    async def receive():return {"type":"http.disconnect"}
    async def send(_message):raise OSError("Client disconnected before headers")
    try:
        with pytest.raises(ClientDisconnect):
            asyncio.run(response({"type":"http","method":"GET","headers":[],"asgi":{"spec_version":"2.4"}},receive,send))
        assert opened.closed
        assert source.read_bytes() == b"original"
    finally:
        opened.close()

