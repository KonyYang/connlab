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
    duplicate = client.post("/api/project-library/intake-plan", json={"sources": [str(additional)], "assignments": [{"source_path": str(additional), "target_member_id": members[0]["member_id"]}]}).json()
    assert duplicate["items"][0]["status"] == "already_added"
    assert duplicate["items"][0]["existing_member_id"] == members[0]["member_id"]


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
    member_id = added["items"][0]["member_id"]
    assert duplicate["items"][0]["existing_member_id"] == member_id
    assert client.get("/api/project-library/members").json()["items"][0]["member_id"] == member_id
    assert (source/"result.txt").read_text(encoding="utf-8") == "first"
    (source/"result.txt").write_text("second source revision",encoding="utf-8")
    changed=client.post("/api/project-library/intake-plan",json={"sources":[str(source)]}).json()
    assert changed["items"][0]["status"]=="conflict",changed
    assert changed["items"][0]["can_keep_separate"] is True
    assert changed["items"][0]["existing_member_id"] is None


def test_scan_keeps_explicit_manual_parent_boundary_without_hashing_it_again(library,tmp_path,monkeypatch):
    from backend.infrastructure.project_library import files as file_module
    client,_,_=library
    root=tmp_path/"Manual project archive"
    for folder,name in (("Photos","photo.bin"),("Test results","result.csv")):
        (root/folder).mkdir(parents=True)
        (root/folder/name).write_bytes(b"original manual project evidence")
    original=file_module.file_hash;reads=[]
    def track(path):
        reads.append(str(path));return original(path)
    monkeypatch.setattr(file_module,"file_hash",track)
    response=client.post("/api/project-library/scan",json={"roots":[str(root)]})
    assert response.status_code==200,response.text
    scan=response.json()
    assert scan["boundary_roots"][0]["source_path"]==str(root)
    assert set(scan["boundary_roots"][0]["child_folders"])=={str(root/"Photos"),str(root/"Test results")}
    assert all(reads.count(str(path))<=1 for path in root.rglob("*") if path.is_file()),reads
    # Explicit parent selection is authoritative even when auto suggestions go deeper.
    plan=client.post("/api/project-library/intake-plan",json={"sources":[scan["boundary_roots"][0]["source_path"]]}).json()
    assert [item["source_path"] for item in plan["items"]]==[str(root)]
    received=client.post("/api/project-library/batches",json={**{key:plan[key] for key in ("plan_id","fingerprint")},"selected":[str(root)]}).json()
    assert received["counts"]["added"]==1,received
    member=client.get("/api/project-library/members/"+received["items"][0]["member_id"]).json()
    assert (Path(member["folder_path"])/"Photos/photo.bin").read_bytes()==b"original manual project evidence"
    assert (Path(member["folder_path"])/"Test results/result.csv").is_file()


def test_scan_accepts_the_initial_batch_of_three_hundred_explicit_roots(library,tmp_path):
    client,_,_=library
    roots=[]
    for i in range(300):
        root=tmp_path/f"Manual root {i}"
        (root/"Photos").mkdir(parents=True)
        roots.append(str(root))
    response=client.post("/api/project-library/scan",json={"roots":roots})
    assert response.status_code==200,response.text
    assert {row["source_path"] for row in response.json()["boundary_roots"]}==set(roots)


@pytest.mark.parametrize("folder_name",["DL-2026-09-032 Same Project","Same manual project"])
def test_same_batch_keep_separate_reserves_distinct_destinations_and_retries_once(library,tmp_path,folder_name):
    client,settings,_=library
    sources=[]
    for i in (1,2):
        source=tmp_path/f"computer-{i}"/folder_name
        source.mkdir(parents=True)
        (source/"result.txt").write_text(f"source evidence {i}",encoding="utf-8")
        sources.append(str(source))
    plan=client.post("/api/project-library/intake-plan",json={"sources":sources}).json()
    assert all(item["status"]=="conflict" and item["can_keep_separate"] for item in plan["items"]),plan
    request={**{key:plan[key] for key in ("plan_id","fingerprint")},"selected":sources,"keep_separate":sources,"batch_id":"b"*32}
    response=client.post("/api/project-library/batches",json=request)
    assert response.status_code==200,response.text
    batch=response.json()
    assert batch["counts"]["added"]==2 and batch["counts"]["failed"]==0,batch
    members=client.get("/api/project-library/members").json()["items"]
    assert len({row["folder_path"] for row in members})==2
    assert {(Path(row["folder_path"])/"result.txt").read_text() for row in members}=={"source evidence 1","source evidence 2"}
    repeated=client.post("/api/project-library/batches",json=request).json()
    assert repeated["items"]==batch["items"]
    assert len(client.get("/api/project-library/members").json()["items"])==2
    assert len(list(settings.projects_dir.iterdir()))==2
    assert [(Path(path)/"result.txt").read_text() for path in sources]==["source evidence 1","source evidence 2"]


def test_keep_separate_same_name_loose_files_preserves_their_extension(library,tmp_path):
    client,_,_=library
    sources=[]
    for i in (1,2):
        path=tmp_path/f"computer-{i}"/"result.csv";path.parent.mkdir()
        path.write_text(f"result,{i}",encoding="utf-8");sources.append(str(path))
    plan=client.post("/api/project-library/intake-plan",json={"sources":sources,"assignments":[{"source_path":path,"new_project_title":"Supplementary project"} for path in sources]}).json()
    assert all(row["status"]=="conflict" and row["can_keep_separate"] for row in plan["items"]),plan
    batch=client.post("/api/project-library/batches",json={**{key:plan[key] for key in ("plan_id","fingerprint")},"selected":sources,"keep_separate":sources}).json()
    assert batch["counts"]["added"]==2,batch
    member=client.get("/api/project-library/members/"+batch["items"][0]["member_id"]).json()
    files=list(Path(member["folder_path"]).glob("*.csv"))
    assert len(files)==2
    assert {path.read_text() for path in files}=={"result,1","result,2"}


@pytest.mark.parametrize("change",["project_id","ltr_number","both","same_source_reused","member_identity_only","ltr_only_metadata"])
def test_equal_material_does_not_hide_a_different_stable_project_identity(library,tmp_path,change):
    import json
    client,_,_=library
    first=tmp_path/"computer-1"/"Same title"
    first.mkdir(parents=True);(first/".connlab").mkdir()
    identity={"project_id":None if change=="ltr_only_metadata" else "3"*32,"ltr_number":"DL-2026-09-001"}
    (first/".connlab/library.json").write_text(json.dumps(identity),encoding="utf-8")
    (first/"template.txt").write_text("same ordinary template",encoding="utf-8")
    plan=client.post("/api/project-library/intake-plan",json={"sources":[str(first)]}).json()
    batch=client.post("/api/project-library/batches",json={**{key:plan[key] for key in ("plan_id","fingerprint")},"selected":[str(first)]}).json()
    assert batch["counts"]["added"]==1,batch
    assert client.post("/api/project-library/intake-plan",json={"sources":[str(first)]}).json()["items"][0]["status"]=="already_added"
    if change=="member_identity_only":
        received=client.get("/api/project-library/members/"+batch["items"][0]["member_id"]).json()
        (Path(received["folder_path"])/".connlab/library.json").unlink()
    second=first if change=="same_source_reused" else tmp_path/"computer-2"/"Same title"
    if second!=first:
        second.mkdir(parents=True);(second/".connlab").mkdir()
    changed=dict(identity)
    if change in {"project_id","both","same_source_reused","member_identity_only"}:
        changed["project_id"]="4"*32
    if change in {"ltr_number","both","same_source_reused","member_identity_only","ltr_only_metadata"}:
        changed["ltr_number"]="DL-2026-09-002"
    (second/".connlab/library.json").write_text(json.dumps(changed),encoding="utf-8")
    (second/"template.txt").write_text("same ordinary template",encoding="utf-8")
    plan=client.post("/api/project-library/intake-plan",json={"sources":[str(second)]}).json()
    assert plan["items"][0]["status"]=="conflict" and plan["items"][0]["can_keep_separate"],plan
    assert any("identity" in warning.lower() or "ltr" in warning.lower() for warning in plan["items"][0]["warnings"])
    assert plan["items"][0]["existing_member_id"] is None
    separate=client.post("/api/project-library/batches",json={**{key:plan[key] for key in ("plan_id","fingerprint")},"selected":[str(second)],"keep_separate":[str(second)]}).json()
    assert separate["counts"]["added"]==1,separate
    members=client.get("/api/project-library/members").json()["items"]
    assert len(members)==2 and len({row["folder_path"] for row in members})==2
    for member in members:
        assert (Path(member["folder_path"])/"template.txt").read_text()=="same ordinary template"
    if change=="same_source_reused":
        (first/".connlab/library.json").write_text(json.dumps(identity),encoding="utf-8")
        original_again=client.post("/api/project-library/intake-plan",json={"sources":[str(first)]}).json()
        assert original_again["items"][0]["status"]=="already_added",original_again


def test_same_known_identity_and_equal_material_at_another_source_remains_duplicate(library,tmp_path):
    import json,shutil
    client,_,_=library
    first=tmp_path/"computer-1"/"Same title"
    (first/".connlab").mkdir(parents=True)
    (first/".connlab/library.json").write_text(json.dumps({"project_id":"3"*32,"ltr_number":"DL-2026-09-001"}),encoding="utf-8")
    (first/"template.txt").write_text("same template",encoding="utf-8")
    plan=client.post("/api/project-library/intake-plan",json={"sources":[str(first)]}).json()
    assert client.post("/api/project-library/batches",json={**{key:plan[key] for key in ("plan_id","fingerprint")},"selected":[str(first)]}).json()["counts"]["added"]==1
    second=tmp_path/"computer-2"/"Same title";shutil.copytree(first,second)
    result=client.post("/api/project-library/intake-plan",json={"sources":[str(second)]}).json()
    assert result["items"][0]["status"]=="already_added",result
    member_id = client.get("/api/project-library/members").json()["items"][0]["member_id"]
    assert result["items"][0]["existing_member_id"] == member_id


@pytest.mark.parametrize("source_is_target",[True,False])
def test_unregistered_equal_material_has_explicit_managed_copy_action(library,tmp_path,source_is_target):
    client,settings,_=library
    target=settings.projects_dir/"DL-2026-09-032 Already here"
    target.mkdir();(target/"record.txt").write_text("original evidence",encoding="utf-8")
    source=target
    if not source_is_target:
        source=tmp_path/"external source"/target.name
        source.mkdir(parents=True);(source/"record.txt").write_text("original evidence",encoding="utf-8")
    assert client.get("/api/project-library/members").json()["items"]==[]
    plan=client.post("/api/project-library/intake-plan",json={"sources":[str(source)]}).json()
    assert plan["items"][0]["status"]=="conflict" and plan["items"][0]["can_keep_separate"],plan
    assert any("not registered" in warning.lower() for warning in plan["items"][0]["warnings"])
    batch=client.post("/api/project-library/batches",json={**{key:plan[key] for key in ("plan_id","fingerprint")},"selected":[str(source)],"keep_separate":[str(source)]}).json()
    assert batch["counts"]["added"]==1,batch
    members=client.get("/api/project-library/members").json()["items"]
    assert len(members)==1 and members[0]["folder_path"]!=str(target)
    assert (Path(members[0]["folder_path"])/"record.txt").read_text()=="original evidence"
    assert not (target/".connlab/library.json").exists()
    assert not (source/".connlab/library.json").exists()
    assert (source/"record.txt").read_text()=="original evidence"
