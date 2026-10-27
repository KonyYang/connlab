from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.shared.config import Settings
from backend.infrastructure.storage.database import init_db
from backend.api.routes_project_library import router, get_project_library_service
from backend.application.project_library.service import ProjectLibraryService
from backend.infrastructure.project_library.files import LibraryFiles
from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository


@pytest.fixture
def library(tmp_path):
    root = tmp_path / "library"
    settings = Settings(root / "Data", root / "Projects", root / "Templates", root / "Data" / "connlab.sqlite3", library_root=root)
    settings.ensure_directories()
    engine = create_engine(f"sqlite:///{settings.database_path}", connect_args={"check_same_thread": False})
    init_db(engine)
    app = FastAPI()
    app.include_router(router)
    opened = []
    def service():
        with Session(engine) as session:
            yield ProjectLibraryService(ProjectLibraryRepository(session), settings, files=LibraryFiles(settings), opener=opened.append)
    app.dependency_overrides[get_project_library_service] = service
    yield TestClient(app), settings, opened
    engine.dispose()


def test_batch_intake_browsing_title_and_daily_files_keep_identity(library, tmp_path):
    client, settings, opened = library
    source = tmp_path / "source" / "DL-2026-09-032 Old title"
    (source / "Test results").mkdir(parents=True)
    (source / "Test results" / "record.csv").write_text("10.2", encoding="utf-8")
    scan = client.post("/api/project-library/scan", json={"roots": [str(source)]}).json()
    assert scan["items"][0]["ltr_number"] == "DL-2026-09-032"
    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    batch = client.post("/api/project-library/batches", json={"plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"], "selected": [str(source)], "keep_separate": []}).json()
    assert batch["counts"]["added"] == 1
    member_id = batch["items"][0]["member_id"]
    member = client.get(f"/api/project-library/members/{member_id}").json()
    target = Path(member["folder_path"])
    assert target.is_relative_to(settings.projects_dir)
    (target / "Test results" / "record.csv").write_text("11.7", encoding="utf-8")
    (target / "Photos").mkdir()
    (target / "Photos" / "photo.txt").write_text("new photo", encoding="utf-8")
    title = client.post(f"/api/project-library/members/{member_id}/title-plan", json={"title": "New title"}).json()
    changed = client.post(f"/api/project-library/members/{member_id}/title", json={"plan_id": title["plan_id"], "fingerprint": title["fingerprint"]}).json()
    assert changed["member_id"] == member_id
    assert changed["ltr_number"] == "DL-2026-09-032"
    assert Path(changed["folder_path"]).name == "DL-2026-09-032 New title"
    assert (Path(changed["folder_path"]) / "Test results" / "record.csv").read_text() == "11.7"
    assert (source / "Test results" / "record.csv").read_text() == "10.2"
    client.post(f"/api/project-library/members/{member_id}/open-folder")
    assert opened == [changed["folder_path"]]


def receive(client, paths, assignments=None, batch_id=None):
    request = {"sources": [str(path) for path in paths]}
    if assignments:
        request["assignments"] = assignments
    review = client.post("/api/project-library/intake-plan", json=request)
    assert review.status_code == 200, review.text
    plan = review.json()
    payload = {key: plan[key] for key in ("plan_id", "fingerprint")}
    payload["selected"] = [str(path) for path in paths]
    if batch_id:
        payload["batch_id"] = batch_id
    result = client.post("/api/project-library/batches", json=payload)
    assert result.status_code == 200, result.text
    return result.json(), payload


def test_three_hundred_projects_are_received_once_and_retry_is_idempotent(library, tmp_path):
    client, settings, _ = library
    sources = []
    for i in range(300):
        source = tmp_path / "incoming" / f"DL-2026-10-{i + 1:03d} Connector {i}"
        (source / "Source Book").mkdir(parents=True)
        (source / "result.csv").write_text(f"sample,{i}", encoding="utf-8")
        sources.append(source)
    result, payload = receive(client, sources, batch_id="1" * 32)
    assert result["counts"] == {"added": 300, "already_added": 0, "review": 0, "failed": 0}
    assert len(client.get("/api/project-library/members").json()["items"]) == 300
    retry = client.post("/api/project-library/batches", json=payload)
    assert retry.status_code == 200, retry.text
    assert retry.json()["batch_id"] == result["batch_id"]
    assert len(client.get("/api/project-library/members").json()["items"]) == 300
    assert (sources[177] / "result.csv").read_text() == "sample,177"


def test_loose_files_require_explicit_assignment_and_group_into_one_project(library, tmp_path):
    client, _, _ = library
    first, second = tmp_path / "report.txt", tmp_path / "readings.csv"
    first.write_text("report", encoding="utf-8")
    second.write_text("0.248", encoding="utf-8")
    unassigned = client.post("/api/project-library/intake-plan", json={"sources": [str(first)]}).json()
    assert unassigned["items"][0]["status"] == "conflict"
    assert not unassigned["items"][0]["can_keep_separate"]
    assignments = [{"source_path": str(path), "new_project_title": "Incoming Qualification"} for path in (first, second)]
    result, _ = receive(client, [first, second], assignments)
    assert result["counts"]["added"] == 2
    assert len({row["member_id"] for row in result["items"]}) == 1
    members = client.get("/api/project-library/members").json()["items"]
    assert len(members) == 1
    assert (Path(members[0]["folder_path"]) / first.name).read_text() == "report"
    additional = tmp_path / "more.csv"
    additional.write_text("0.198", encoding="utf-8")
    added, _ = receive(client, [additional], [{"source_path": str(additional), "target_member_id": members[0]["member_id"]}])
    assert added["counts"]["added"] == 1
    assert len(client.get("/api/project-library/members").json()["items"]) == 1
    assert (Path(members[0]["folder_path"]) / "Imported Material" / "more.csv").read_text() == "0.198"


def test_interrupted_after_copy_can_resume_using_known_batch_identity(library, tmp_path, monkeypatch):
    from backend.infrastructure.project_library.files import LibraryFiles
    client, _, _ = library
    source = tmp_path / "DL-2026-09-032 Interruption"
    source.mkdir()
    (source / "measurement.txt").write_text("retain me", encoding="utf-8")
    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    payload = {key: plan[key] for key in ("plan_id", "fingerprint")}
    payload.update(selected=[str(source)], batch_id="2" * 32)
    original = LibraryFiles.receive
    def crash(self, *args, **kwargs):
        original(self, *args, **kwargs)
        raise RuntimeError("simulated process interruption after verified copy")
    with monkeypatch.context() as patch:
        patch.setattr(LibraryFiles, "receive", crash)
        with pytest.raises(RuntimeError, match="simulated"):
            client.post("/api/project-library/batches", json=payload)
    observed = client.get("/api/project-library/batches/" + payload["batch_id"])
    assert observed.status_code == 200
    assert observed.json()["status"] == "running"
    resumed = client.post("/api/project-library/batches/" + payload["batch_id"] + "/resume")
    assert resumed.status_code == 200, resumed.text
    assert resumed.json()["counts"]["added"] == 1
    assert len(client.get("/api/project-library/members").json()["items"]) == 1


def test_source_change_after_review_is_not_registered(library, tmp_path):
    client, _, _ = library
    source = tmp_path / "DL-2026-09-032 Changed"
    source.mkdir()
    (source / "result.txt").write_text("before", encoding="utf-8")
    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    (source / "result.txt").write_text("after", encoding="utf-8")
    result = client.post("/api/project-library/batches", json={**{key: plan[key] for key in ("plan_id", "fingerprint")}, "selected": [str(source)]}).json()
    assert result["counts"]["failed"] == 1
    assert client.get("/api/project-library/members").json()["items"] == []


def test_title_change_recovers_after_copy_path_commit_failure(library, tmp_path, monkeypatch):
    from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository
    client, _, _ = library
    source = tmp_path / "DL-2026-09-032 Recovery"
    source.mkdir()
    (source / "result.csv").write_text("never lose this", encoding="utf-8")
    result, _ = receive(client, [source])
    mid = result["items"][0]["member_id"]
    review = client.post(f"/api/project-library/members/{mid}/title-plan", json={"title": "Recovered title"}).json()
    payload = {key: review[key] for key in ("plan_id", "fingerprint")}
    original = ProjectLibraryRepository.publish_move
    with monkeypatch.context() as patch:
        patch.setattr(ProjectLibraryRepository, "publish_move", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("simulated database boundary")))
        failed = client.post(f"/api/project-library/members/{mid}/title", json=payload)
    assert failed.status_code == 422
    recovered_review = client.post(f"/api/project-library/members/{mid}/title-plan", json={"title": "Recovered title"}).json()
    assert recovered_review["warnings"]
    recovered = client.post(f"/api/project-library/members/{mid}/title", json={key: recovered_review[key] for key in ("plan_id", "fingerprint")})
    assert recovered.status_code == 200, recovered.text
    assert recovered.json()["member_id"] == mid
    assert (Path(recovered.json()["folder_path"]) / "result.csv").read_text() == "never lose this"
    assert len(client.get("/api/project-library/members").json()["items"]) == 1


def test_missing_marker_can_be_rebuilt_only_after_explicit_reconnect_review(library, tmp_path):
    client, _, _ = library
    source = tmp_path / "DL-2026-09-032 Missing marker"
    source.mkdir()
    (source / "result.txt").write_text("original measurement", encoding="utf-8")
    result, _ = receive(client, [source])
    mid = result["items"][0]["member_id"]
    before = client.get(f"/api/project-library/members/{mid}").json()
    folder = Path(before["folder_path"])
    (folder / ".connlab" / "library.json").unlink()
    plan = client.post(f"/api/project-library/members/{mid}/location-plan", json={"folder": str(folder)})
    assert plan.status_code == 200, plan.text
    assert any("identity" in value.lower() for value in plan.json()["warnings"])
    assert not (folder / ".connlab" / "library.json").exists()
    updated = client.post(f"/api/project-library/members/{mid}/location", json={key: plan.json()[key] for key in ("plan_id", "fingerprint")})
    assert updated.status_code == 200, updated.text
    assert updated.json()["member_id"] == mid
    assert updated.json()["ltr_number"] == before["ltr_number"]
    assert (folder / ".connlab" / "library.json").is_file()
    assert (folder / "result.txt").read_text() == "original measurement"


def test_foreign_identity_is_not_claimed_by_matching_ltr(library, tmp_path):
    import json
    client, _, _ = library
    source = tmp_path / "DL-2026-09-032 Owner"
    source.mkdir()
    (source / "result.txt").write_text("A", encoding="utf-8")
    result, _ = receive(client, [source])
    mid = result["items"][0]["member_id"]
    foreign = tmp_path / "DL-2026-09-032 Foreign"
    (foreign / ".connlab").mkdir(parents=True)
    (foreign / ".connlab" / "library.json").write_text(json.dumps({"member_id": "someone-else", "ltr_number": "DL-2026-09-032"}), encoding="utf-8")
    rejected = client.post(f"/api/project-library/members/{mid}/location-plan", json={"folder": str(foreign)})
    assert rejected.status_code == 409


def test_reimport_same_path_compares_content_before_calling_it_a_duplicate(library,tmp_path):
    client,_,_=library
    source=tmp_path/"DL-2026-09-032 Old project"
    source.mkdir()
    (source/"result.txt").write_text("first",encoding="utf-8")
    plan=client.post("/api/project-library/intake-plan",json={"sources":[str(source)]}).json()
    added=client.post("/api/project-library/batches",json={**{k:plan[k] for k in ("plan_id","fingerprint")},"selected":[str(source)]}).json()
    assert added["counts"]["added"]==1
    duplicate=client.post("/api/project-library/intake-plan",json={"sources":[str(source)]}).json()
    assert duplicate["items"][0]["status"]=="already_added"
    (source/"result.txt").write_text("second source revision",encoding="utf-8")
    changed=client.post("/api/project-library/intake-plan",json={"sources":[str(source)]}).json()
    assert changed["items"][0]["status"]=="conflict",changed
    assert changed["items"][0]["can_keep_separate"] is True
