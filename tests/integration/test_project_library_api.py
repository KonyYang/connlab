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
from backend.application.project_library.existing_ltr_adoption import (
    ExistingLtrAdoptionService,
    ExistingLtrAuthorityRow,
    ExcelExistingLtrAuthority,
    UnavailableExistingLtrAuthority,
)
from backend.application.project_library.automatic_snapshot import AutomaticPortableSnapshotService
from backend.infrastructure.project_library.portability import ProjectPortability
from backend.infrastructure.storage.models import LtrRecordModel, ProjectModel


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


@pytest.fixture
def authority_library(tmp_path):
    root = tmp_path / "library"
    settings = Settings(root / "Data", root / "Projects", root / "Templates", root / "Data" / "connlab.sqlite3", library_root=root)
    settings.ensure_directories()
    engine = create_engine(f"sqlite:///{settings.database_path}", connect_args={"check_same_thread": False})
    init_db(engine)

    class Authority:
        row = ExistingLtrAuthorityRow(
            ltr_number="DL-2026-11-013", sheet_name="2026", row_number=27,
            values=("Nov", 13, 13, "DL-2026-11-013", None, "Imported connector"),
        )

        def find(self, ltr_number):
            return self.row if self.row and self.row.ltr_number == ltr_number else None

    authority = Authority()
    app = FastAPI()
    app.include_router(router)

    def service():
        with Session(engine) as session:
            store = ProjectLibraryRepository(session)
            files = LibraryFiles(settings)
            portability = ProjectPortability(store, files, settings)
            yield ProjectLibraryService(
                store, settings, files=files, portability=portability,
                existing_ltr=ExistingLtrAdoptionService(store, authority),
                automatic_snapshot=AutomaticPortableSnapshotService(store, portability),
            )

    app.dependency_overrides[get_project_library_service] = service
    yield TestClient(app), settings, engine, authority
    engine.dispose()


def test_existing_ltr_is_revalidated_adopted_and_snapshotted_without_reusing_source_identity(authority_library, tmp_path):
    import json

    client, settings, engine, authority = authority_library
    source = tmp_path / "DL-2026-11-013"
    (source / ".connlab").mkdir(parents=True)
    (source / ".connlab" / "manifest.json").write_text(json.dumps({
        "schema_version": 1, "project_id": "other-computer-project", "dl_number": "DL-2026-11-013",
    }), encoding="utf-8")
    (source / "result.txt").write_text("source evidence", encoding="utf-8")
    original = {path.relative_to(source): path.read_bytes() for path in source.rglob("*") if path.is_file()}

    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    item = plan["items"][0]
    assert item["status"] == "ready", item
    assert item["source_state"] == "adopt_existing"
    assert item["authority_status"] == "found"
    assert not list(settings.projects_dir.iterdir())

    authority.row = ExistingLtrAuthorityRow(
        ltr_number="DL-2026-11-013", sheet_name="2026", row_number=27,
        values=("Nov", 13, 13, "DL-2026-11-013", None, "Changed after review"),
    )
    stale = client.post("/api/project-library/batches", json={
        "plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"], "selected": [str(source)],
    }).json()
    assert stale["counts"]["added"] == 0
    assert not list(settings.projects_dir.iterdir())

    fresh = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    added = client.post("/api/project-library/batches", json={
        "plan_id": fresh["plan_id"], "fingerprint": fresh["fingerprint"], "selected": [str(source)],
    }).json()
    assert added["counts"]["added"] == 1, added
    member = client.get(f"/api/project-library/members/{added['items'][0]['member_id']}").json()
    assert member["project_id"] != "other-computer-project"
    assert member["snapshot_status"] == "current"
    assert Path(member["folder_path"], ".connlab", "portable", "snapshot.json").is_file()
    with Session(engine) as session:
        record = session.query(LtrRecordModel).one()
        assert record.project_id == member["project_id"]
        assert record.ltr_number == "DL-2026-11-013"
        assert "adopt_existing_authority" in record.notes
        assert session.get(ProjectModel, "other-computer-project") is None
    assert {path.relative_to(source): path.read_bytes() for path in source.rglob("*") if path.is_file()} == original


def test_existing_ltr_local_owner_conflict_is_blocked_before_copy(authority_library, tmp_path):
    client, settings, engine, _ = authority_library
    source = tmp_path / "DL-2026-11-013 Other computer"
    source.mkdir()
    (source / "evidence.txt").write_text("unchanged", encoding="utf-8")
    with Session(engine) as session:
        session.add(ProjectModel(project_id="local-owner", project_no="DL-2026-11-013", product_name="Local", requestor="Lab", status="draft"))
        session.add(LtrRecordModel(ltr_id="local-ltr", project_id="local-owner", ltr_number="DL-2026-11-013", status="registered", is_current_owner=True))
        session.commit()
    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    item = plan["items"][0]
    assert item["status"] == "conflict"
    assert item["can_keep_separate"] is False
    assert "already belongs" in " ".join(item["warnings"])
    assert not list(settings.projects_dir.iterdir())


def test_numbered_legacy_project_is_unavailable_when_ltr_authority_is_not_configured(library, tmp_path):
    _, settings, _ = library
    engine = create_engine(f"sqlite:///{settings.database_path}", connect_args={"check_same_thread": False})
    app = FastAPI()
    app.include_router(router)

    def unavailable_service():
        with Session(engine) as session:
            store = ProjectLibraryRepository(session)
            yield ProjectLibraryService(
                store, settings, files=LibraryFiles(settings),
                existing_ltr=ExistingLtrAdoptionService(store, UnavailableExistingLtrAuthority()),
            )

    app.dependency_overrides[get_project_library_service] = unavailable_service
    client = TestClient(app)
    source = tmp_path / "DL-2026-11-013 Other computer"
    source.mkdir()
    (source / "evidence.txt").write_text("unchanged", encoding="utf-8")

    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()

    assert plan["items"][0]["status"] == "unavailable"
    assert "LTR workbook" in " ".join(plan["items"][0]["warnings"])
    assert not list(settings.projects_dir.iterdir())
    engine.dispose()


def test_numbered_legacy_project_is_unavailable_when_configured_ltr_gateway_cannot_read(library, tmp_path):
    _, settings, _ = library
    engine = create_engine(f"sqlite:///{settings.database_path}", connect_args={"check_same_thread": False})
    app = FastAPI()
    app.include_router(router)

    class FailingConfiguredGateway:
        def open_read_session(self):
            raise RuntimeError("Unable to open configured LTR workbook")

    def failing_service():
        with Session(engine) as session:
            store = ProjectLibraryRepository(session)
            yield ProjectLibraryService(
                store, settings, files=LibraryFiles(settings),
                existing_ltr=ExistingLtrAdoptionService(
                    store, ExcelExistingLtrAuthority(FailingConfiguredGateway())
                ),
            )

    app.dependency_overrides[get_project_library_service] = failing_service
    client = TestClient(app)
    source = tmp_path / "DL-2026-11-013 Unreadable authority"
    source.mkdir()
    (source / "evidence.txt").write_text("unchanged", encoding="utf-8")

    response = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]})

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["status"] == "unavailable"
    assert "could not be read" in " ".join(item["warnings"])
    assert not list(settings.projects_dir.iterdir())
    engine.dispose()


def test_competing_ltr_claim_after_review_is_blocked_before_target_copy(authority_library, tmp_path, monkeypatch):
    client, settings, engine, _ = authority_library
    source = tmp_path / "DL-2026-11-013 Other computer"
    source.mkdir()
    (source / "evidence.txt").write_text("unchanged", encoding="utf-8")
    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    target = Path(plan["items"][0]["target_path"])
    original_verify = ExistingLtrAdoptionService.verify
    injected = False

    def verify_then_inject_competing_owner(service, proof):
        nonlocal injected
        original_verify(service, proof)
        if not injected:
            injected = True
            session = service._store.session
            session.add(ProjectModel(
                project_id="competing-owner", project_no="DL-2026-11-013",
                product_name="Competing", requestor="Lab", status="draft",
            ))
            session.add(LtrRecordModel(
                ltr_id="competing-ltr", project_id="competing-owner",
                ltr_number="DL-2026-11-013", status="registered", is_current_owner=True,
            ))
            session.commit()

    monkeypatch.setattr(ExistingLtrAdoptionService, "verify", verify_then_inject_competing_owner)
    batch = client.post("/api/project-library/batches", json={
        "plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"],
        "selected": [str(source)],
    }).json()

    assert batch["counts"]["added"] == 0
    assert not target.exists()
    with Session(engine) as session:
        owners = session.query(LtrRecordModel).filter_by(
            ltr_number="DL-2026-11-013", status="registered", is_current_owner=True,
        ).all()
        assert [row.project_id for row in owners] == ["competing-owner"]


def test_single_project_check_keeps_ltr_root_whole_and_does_not_expand_parent(library, tmp_path):
    client, settings, _ = library
    parent = tmp_path / "old-projects"
    project = parent / "DL-2026-09-032"
    business = project / "DL-2026-09-032 Connector qualification"
    business.mkdir(parents=True)
    (project / "Source Book").mkdir()
    (business / "test.txt").write_text("original", encoding="utf-8")
    checked = client.post("/api/project-library/scan", json={"roots": [str(project)], "single_project": True})
    assert checked.status_code == 200, checked.text
    assert checked.json()["selection_issue"] is None
    assert [item["source_path"] for item in checked.json()["items"]] == [str(project)]
    assert checked.json()["items"][0]["ltr_number"] == "DL-2026-09-032"
    parent_check = client.post("/api/project-library/scan", json={"roots": [str(parent)], "single_project": True}).json()
    assert parent_check["selection_issue"] == "choose_project"
    assert parent_check["items"] == []
    partial = client.post("/api/project-library/scan", json={"roots": [str(project / "Source Book")], "single_project": True}).json()
    assert partial["selection_issue"] == "partial_project"
    assert not list(settings.projects_dir.iterdir())
    # Existing batch callers still discover the project inside a parent.
    batch = client.post("/api/project-library/scan", json={"roots": [str(parent)]}).json()
    assert [item["source_path"] for item in batch["items"]] == [str(project)]


def test_single_project_missing_ltr_is_reviewed_then_imported_without_renaming_source(library, tmp_path):
    client, settings, _ = library
    source = tmp_path / "Manual connector test"
    source.mkdir()
    (source / "original.txt").write_text("keep this", encoding="utf-8")
    check = client.post("/api/project-library/scan", json={"roots": [str(source)], "single_project": True}).json()
    assert check["selection_issue"] == "needs_ltr"
    assert not list(settings.projects_dir.iterdir())
    request = {"sources": [str(source)], "assignments": [{"source_path": str(source), "ltr_number": "DL-2026-09-032A1"}]}
    response = client.post("/api/project-library/intake-plan", json=request)
    assert response.status_code == 200, response.text
    plan = response.json()
    assert plan["items"][0]["ltr_number"] == "DL-2026-09-032A1"
    assert plan["items"][0]["status"] == "ready"
    assert not list(settings.projects_dir.iterdir())
    confirmed = client.post("/api/project-library/batches", json={"plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"], "selected": [str(source)]})
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["counts"]["added"] == 1, confirmed.text
    member = client.get("/api/project-library/members").json()["items"][0]
    assert member["ltr_number"] == "DL-2026-09-032A1"
    assert member["project_id"] and member["can_continue"]
    copied = settings.projects_dir / "DL-2026-09-032A1" / source.name / "original.txt"
    assert copied.read_text(encoding="utf-8") == "keep this"
    assert sorted(path.name for path in source.iterdir()) == ["original.txt"]
    repeated = client.post("/api/project-library/intake-plan", json=request).json()
    assert repeated["items"][0]["status"] == "already_added"
    other = tmp_path / "Another manual folder"
    other.mkdir()
    (other / "different.txt").write_text("another test", encoding="utf-8")
    conflict = client.post("/api/project-library/intake-plan", json={"sources": [str(other)], "assignments": [{"source_path": str(other), "ltr_number": "DL-2026-09-032A1"}]}).json()
    assert conflict["items"][0]["status"] == "conflict"
    assert len(client.get("/api/project-library/members").json()["items"]) == 1


def test_single_project_uses_carried_identity_and_does_not_allow_ltr_override(library, tmp_path):
    import json
    client, _, _ = library
    source = tmp_path / "collection" / "Renamed project"
    (source / ".connlab").mkdir(parents=True)
    (source / ".connlab" / "manifest.json").write_text(json.dumps({"project_id": "other-computer", "ltr_number": "DL-2026-09-032"}), encoding="utf-8")
    check = client.post("/api/project-library/scan", json={"roots": [str(source)], "single_project": True}).json()
    assert check["selection_issue"] is None
    assert check["items"][0]["ltr_number"] == "DL-2026-09-032"
    assert check["items"][0]["source_state"] == "incomplete"
    rejected = client.post("/api/project-library/intake-plan", json={"sources": [str(source)], "assignments": [{"source_path": str(source), "ltr_number": "DL-2026-09-033"}]}).json()
    assert rejected["items"][0]["status"] == "unavailable"
    parent_check = client.post("/api/project-library/scan", json={"roots": [str(source.parent)], "single_project": True}).json()
    assert parent_check["selection_issue"] == "choose_project"
    override_parent = client.post("/api/project-library/intake-plan", json={"sources": [str(source.parent)], "assignments": [{"source_path": str(source.parent), "ltr_number": "DL-2026-09-033"}]}).json()
    assert override_parent["items"][0]["status"] == "unavailable"


@pytest.mark.parametrize("numbered", [True, False])
def test_connlab_identity_without_snapshot_requires_explicit_files_only_choice(library, tmp_path, numbered):
    import json
    client, settings, _ = library
    source = tmp_path / ("DL-2020-08-001 Old project" if numbered else "Unnumbered old project")
    (source / ".connlab").mkdir(parents=True)
    manifest = json.dumps({"schema_version":1, "project_id":"old-source-identity", "dl_number":"DL-2020-08-001" if numbered else None})
    (source / ".connlab/manifest.json").write_text(manifest, encoding="utf-8")
    (source / "evidence.txt").write_text("original evidence", encoding="utf-8")
    def review(assignments=None):
        return client.post("/api/project-library/intake-plan", json={"sources":[str(source)], "assignments":assignments or []}).json()
    plan=review()
    assert plan["items"][0]["status"] == "conflict", plan
    assert plan["items"][0]["source_state"] == "incomplete"
    assert not plan["items"][0]["can_keep_separate"]
    batch=client.post("/api/project-library/batches",json={**{k:plan[k] for k in ("plan_id","fingerprint")},"selected":[str(source)],"keep_separate":[str(source)]}).json()
    assert batch["counts"]["added"] == 0
    assert list(settings.projects_dir.iterdir()) == []
    plan=review([{"source_path":str(source), "files_only":True}])
    assert plan["items"][0]["source_state"] == "files_only"
    assert plan["items"][0]["status"] == "ready", plan
    batch=client.post("/api/project-library/batches",json={**{k:plan[k] for k in ("plan_id","fingerprint")},"selected":[str(source)]}).json()
    assert batch["counts"]["added"] == 1, batch
    member=client.get("/api/project-library/members/"+batch["items"][0]["member_id"]).json()
    assert member["project_id"] and member["project_id"] != "old-source-identity"
    assert member["can_continue"] and member["snapshot_status"] == "missing"
    target=Path(member["folder_path"])/(source.name if numbered else "Imported files")
    assert (target/".connlab/manifest.json").read_text(encoding="utf-8") == manifest
    assert (target/"evidence.txt").read_text(encoding="utf-8") == "original evidence"
    assert (source/".connlab/manifest.json").read_text(encoding="utf-8") == manifest
    assert review([{"source_path":str(source),"files_only":True}])["items"][0]["status"] == "already_added"
    repeated=review()["items"][0]
    assert repeated["status"] == "already_added" and repeated["source_state"] == "files_only", repeated
    import shutil
    other=tmp_path/"other-computer"/source.name
    shutil.copytree(source,other)
    changed=json.loads(manifest);changed["project_id"]="different-original-project"
    (other/".connlab/manifest.json").write_text(json.dumps(changed),encoding="utf-8")
    conflict=client.post("/api/project-library/intake-plan",json={"sources":[str(other)],"assignments":[{"source_path":str(other),"files_only":True}]}).json()
    assert conflict["items"][0]["status"] == "conflict", conflict


@pytest.mark.parametrize("known", [False, True])
def test_newer_connlab_metadata_requires_update_even_for_files_only(library, tmp_path, known):
    import json
    client, settings, _ = library
    if known:
        seed_known_identity(settings,"future")
    source=tmp_path/"DL-2020-08-002 New version"
    (source/".connlab").mkdir(parents=True)
    (source/".connlab/library.json").write_text(json.dumps({"format_version":2,"project_id":"future"}),encoding="utf-8")
    plan=client.post("/api/project-library/intake-plan",json={"sources":[str(source)]}).json()
    row=plan["items"][0]
    assert row["source_state"] == "upgrade_required" and row["status"] == "conflict",row
    assert not row["can_keep_separate"] and "Update ConnLab" in " ".join(row["warnings"])
    plan=client.post("/api/project-library/intake-plan",json={"sources":[str(source)],"assignments":[{"source_path":str(source),"files_only":True}]}).json()
    batch=client.post("/api/project-library/batches",json={**{k:plan[k] for k in ("plan_id","fingerprint")},"selected":[str(source)]}).json()
    assert batch["counts"]["added"] == 0
    assert list(settings.projects_dir.iterdir()) == []


@pytest.mark.parametrize("metadata", ['{', '{"project_id":{},"ltr_number":42}'])
def test_damaged_connlab_identity_is_not_silently_classified_as_manual(library, tmp_path, metadata):
    client, settings, _=library
    source=tmp_path/"DL-2020-08-004 Incomplete"
    (source/".connlab").mkdir(parents=True)
    (source/".connlab/manifest.json").write_text(metadata,encoding="utf-8")
    response=client.post("/api/project-library/intake-plan",json={"sources":[str(source)]})
    assert response.status_code==200,response.text
    row=response.json()["items"][0]
    assert row["source_state"]=="incomplete" and row["status"]=="conflict",row
    assert list(settings.projects_dir.iterdir())==[]


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
    (target / source.name / "Test results" / "record.csv").write_text("11.7", encoding="utf-8")
    (target / source.name / "Photos").mkdir()
    (target / source.name / "Photos" / "photo.txt").write_text("new photo", encoding="utf-8")
    title = client.post(f"/api/project-library/members/{member_id}/title-plan", json={"title": "New title"}).json()
    changed = client.post(f"/api/project-library/members/{member_id}/title", json={"plan_id": title["plan_id"], "fingerprint": title["fingerprint"]}).json()
    assert changed["member_id"] == member_id
    assert changed["ltr_number"] == "DL-2026-09-032"
    assert Path(changed["folder_path"]) == target
    assert target.name == "DL-2026-09-032"
    assert (target / "DL-2026-09-032 New title" / "Test results" / "record.csv").read_text() == "11.7"
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


def test_confirmed_manual_import_is_managed_without_a_second_takeover(library, tmp_path):
    client, settings, _ = library
    source = tmp_path / "incoming" / "DL-2026-09-032A1 Manual connector"
    source.mkdir(parents=True)
    (source / "result.csv").write_text("original,12.3", encoding="utf-8")
    batch, request = receive(client, [source], batch_id="a" * 32)
    assert batch["counts"]["added"] == 1
    member_id = batch["items"][0]["member_id"]
    member = client.get(f"/api/project-library/members/{member_id}").json()
    assert member["project_id"], "Final import confirmation must establish a managed project"
    assert member["ltr_number"] == "DL-2026-09-032A1"
    assert member["can_continue"] is True
    assert member["snapshot_status"] == "missing"
    retry = client.post("/api/project-library/batches", json=request)
    assert retry.status_code == 200
    assert retry.json()["items"][0]["member_id"] == member_id
    members = client.get("/api/project-library/members").json()["items"]
    assert len(members) == 1
    assert members[0]["project_id"] == member["project_id"]
    assert (source / "result.csv").read_text(encoding="utf-8") == "original,12.3"


@pytest.mark.parametrize("selection", ["business", "root", "root_without_source_book"])
def test_import_receives_standard_ltr_root_without_changing_original_material(library, tmp_path, selection):
    import json
    client, settings, _ = library
    number = "DL-2026-09-032A1"
    name = number + " Manual connector"
    source = tmp_path / "incoming" / (name if selection == "business" else number)
    business = source if selection == "business" else source / name
    (business / "Photos").mkdir(parents=True)
    (business / "Photos" / "evidence.txt").write_text("original evidence", encoding="utf-8")
    if selection == "root":
        (source / "Source Book").mkdir()
        (source / "Source Book" / "original.xlsx").write_bytes(b"original workbook")
    original = {str(p.relative_to(source)): p.read_bytes() for p in source.rglob("*") if p.is_file()}
    review = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    assert review["items"][0]["target_path"] == str(settings.projects_dir / number)
    assert review["items"][0]["title"] == "Manual connector"
    assert not (settings.projects_dir / number).exists()
    batch = client.post("/api/project-library/batches", json={**{k: review[k] for k in ("plan_id", "fingerprint")}, "selected": [str(source)]}).json()
    assert batch["counts"]["added"] == 1, batch
    member = client.get("/api/project-library/members/" + batch["items"][0]["member_id"]).json()
    target = Path(member["folder_path"])
    assert target == settings.projects_dir / number
    assert (target / "Source Book").is_dir()
    assert (target / name / "Photos/evidence.txt").read_text(encoding="utf-8") == "original evidence"
    manifest = json.loads((target / ".connlab/manifest.json").read_text(encoding="utf-8"))
    assert manifest["project_id"] == member["project_id"]
    assert Path(manifest["local_workspace_path"]) == target
    assert Path(manifest["official_project_folder_path"]) == target / name
    assert Path(manifest["source_book_path"]) == target / "Source Book"
    if selection == "root":
        assert (target / "Source Book/original.xlsx").read_bytes() == b"original workbook"
    else:
        assert list((target / "Source Book").iterdir()) == []
    assert {str(p.relative_to(source)): p.read_bytes() for p in source.rglob("*") if p.is_file()} == original
    repeated = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    assert repeated["items"][0]["status"] == "already_added", repeated
    (business / "Photos/evidence.txt").write_text("changed evidence", encoding="utf-8")
    changed = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    assert changed["items"][0]["status"] == "conflict"


@pytest.mark.parametrize("layout", ["partial_photos", "partial_source_book", "multiple_business", "source_book_file"])
def test_ambiguous_boundaries_require_review_and_cannot_create_empty_projects(library, tmp_path, layout):
    client, settings, _ = library
    number = "DL-2026-09-032"
    root = tmp_path / "incoming" / number
    root.mkdir(parents=True)
    if layout.startswith("partial_"):
        source = root / ("Photos" if layout == "partial_photos" else "Source Book")
        source.mkdir()
        (source / "record.txt").write_text("partial evidence", encoding="utf-8")
    else:
        source = root
        (root / "record.txt").write_text("preserve evidence", encoding="utf-8")
        if layout == "multiple_business":
            for title in ("Old copy", "Current copy"):
                (root / (number + " " + title)).mkdir()
        elif layout == "source_book_file":
            (root / (number + " Connector")).mkdir()
            (root / "Source Book").write_text("not a directory", encoding="utf-8")
    original = {str(p.relative_to(source)): p.read_bytes() for p in source.rglob("*") if p.is_file()}
    check = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    item = check["items"][0]
    assert item["status"] == "conflict" and not item["can_keep_separate"], check
    assert item["warnings"], check
    forced = client.post("/api/project-library/batches", json={**{k: check[k] for k in ("plan_id", "fingerprint")}, "selected": [str(source)], "keep_separate": [str(source)]}).json()
    assert forced["counts"]["added"] == 0
    assert client.get("/api/project-library/members").json()["items"] == []
    assert list(settings.projects_dir.iterdir()) == []
    assert {str(p.relative_to(source)): p.read_bytes() for p in source.rglob("*") if p.is_file()} == original


@pytest.mark.parametrize("name", ["DL-2026-09-032", "DL-2026-09-032 Old layout"])
def test_flat_legacy_project_keeps_its_entire_tree_inside_the_received_business_folder(library, tmp_path, name):
    client, settings, _ = library
    source = tmp_path / "incoming" / name
    (source / "Source Book").mkdir(parents=True)
    (source / "Source Book/old-matrix.xlsx").write_bytes(b"original workbook")
    (source / "record.txt").write_text("original material", encoding="utf-8")
    batch, _ = receive(client, [source])
    assert batch["counts"]["added"] == 1, batch
    member = client.get("/api/project-library/members/" + batch["items"][0]["member_id"]).json()
    target = Path(member["folder_path"])
    assert target == settings.projects_dir / "DL-2026-09-032"
    business_name = name if " " in name else name + " Imported files"
    assert (target / business_name / "record.txt").read_text(encoding="utf-8") == "original material"
    assert (target / business_name / "Source Book/old-matrix.xlsx").read_bytes() == b"original workbook"
    assert list((target / "Source Book").iterdir()) == []
    assert (source / "Source Book/old-matrix.xlsx").read_bytes() == b"original workbook"
    assert client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()["items"][0]["status"] == "already_added"


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
    client, settings, _ = library
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
    with LibraryFiles(settings).lock():
        busy = client.post("/api/project-library/batches/" + payload["batch_id"] + "/resume")
        assert busy.status_code == 409
    assert client.get("/api/project-library/batches/" + payload["batch_id"]).json() == observed.json()
    resumed = client.post("/api/project-library/batches/" + payload["batch_id"] + "/resume")
    assert resumed.status_code == 200, resumed.text
    assert resumed.json()["counts"]["added"] == 1
    assert len(client.get("/api/project-library/members").json()["items"]) == 1


def test_interrupted_supplement_uses_its_verified_batch_receipt_on_resume(library, tmp_path, monkeypatch):
    client, _, _ = library
    folder = tmp_path / "DL-2026-09-032 Original"
    folder.mkdir()
    (folder / "original.txt").write_text("original", encoding="utf-8")
    batch, _ = receive(client, [folder])
    member_id = batch["items"][0]["member_id"]
    source = tmp_path / "measurement.csv"
    source.write_text("reviewed result", encoding="utf-8")
    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)], "assignments": [{"source_path": str(source), "target_member_id": member_id}]}).json()
    payload = {**{key: plan[key] for key in ("plan_id", "fingerprint")}, "selected": [str(source)], "batch_id": "4" * 32}
    original = LibraryFiles.receive
    def crash(self, *args, **kwargs):
        original(self, *args, **kwargs)
        raise RuntimeError("simulated process interruption")
    with monkeypatch.context() as patch:
        patch.setattr(LibraryFiles, "receive", crash)
        with pytest.raises(RuntimeError, match="simulated"):
            client.post("/api/project-library/batches", json=payload)
    resumed = client.post("/api/project-library/batches/" + payload["batch_id"] + "/resume").json()
    assert resumed["counts"]["added"] == 1, resumed
    assert Path(plan["items"][0]["target_path"]).read_text(encoding="utf-8") == "reviewed result"
    assert len(client.get("/api/project-library/members").json()["items"]) == 1


def test_replan_tokens_stay_stable_only_while_reviewed_material_is_unchanged(library, tmp_path):
    client, _, _ = library
    source = tmp_path / "DL-2026-09-032 Material"
    source.mkdir()
    evidence = source / "measurement.txt"
    evidence.write_text("first", encoding="utf-8")
    def token():
        review = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
        return review["items"][0]["review_fingerprint"]
    first = token()
    assert token() == first
    evidence.write_text("changed", encoding="utf-8")
    assert token() != first


def test_same_name_supplement_appearing_after_review_is_not_reported_as_received(library, tmp_path):
    client, _, _ = library
    folder = tmp_path / "DL-2026-09-032 Original"
    folder.mkdir()
    (folder / "original.txt").write_text("original", encoding="utf-8")
    batch, _ = receive(client, [folder])
    member_id = batch["items"][0]["member_id"]
    source = tmp_path / "measurement.csv"
    source.write_text("reviewed result", encoding="utf-8")
    review = client.post("/api/project-library/intake-plan", json={"sources": [str(source)], "assignments": [{"source_path": str(source), "target_member_id": member_id}]}).json()
    target = Path(review["items"][0]["target_path"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("unrelated result arrived later", encoding="utf-8")
    result = client.post("/api/project-library/batches", json={**{key: review[key] for key in ("plan_id", "fingerprint")}, "selected": [str(source)]}).json()
    assert result["counts"]["added"] == 0, result
    assert result["counts"]["failed"] == 1
    assert target.read_text(encoding="utf-8") == "unrelated result arrived later"
    assert source.read_text(encoding="utf-8") == "reviewed result"


def test_resume_does_not_register_changed_copied_material(library, tmp_path, monkeypatch):
    client, _, _ = library
    source = tmp_path / "DL-2026-09-032 Interrupted"
    source.mkdir()
    (source / "measurement.txt").write_text("reviewed result", encoding="utf-8")
    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    request = {**{key: plan[key] for key in ("plan_id", "fingerprint")}, "selected": [str(source)], "batch_id": "3" * 32}
    original = LibraryFiles.receive
    def crash(self, *args, **kwargs):
        original(self, *args, **kwargs)
        raise RuntimeError("simulated process interruption")
    with monkeypatch.context() as patch:
        patch.setattr(LibraryFiles, "receive", crash)
        with pytest.raises(RuntimeError, match="simulated"):
            client.post("/api/project-library/batches", json=request)
    target = Path(plan["items"][0]["target_path"]) / source.name / "measurement.txt"
    target.write_text("changed after interruption", encoding="utf-8")
    result = client.post("/api/project-library/batches/" + request["batch_id"] + "/resume").json()
    assert result["counts"]["added"] == 0, result
    assert result["counts"]["failed"] == 1
    assert client.get("/api/project-library/members").json()["items"] == []
    assert target.read_text(encoding="utf-8") == "changed after interruption"


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
    assert (Path(recovered.json()["folder_path"]) / "DL-2026-09-032 Recovered title" / "result.csv").read_text() == "never lose this"
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
    assert (folder / source.name / "result.txt").read_text() == "original measurement"


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
    assert {next(Path(row["folder_path"]).rglob("result.txt")).read_text() for row in members}=={"source evidence 1","source evidence 2"}
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


def seed_known_identity(settings, *project_ids):
    from backend.infrastructure.storage.models import ProjectModel
    engine=create_engine(f"sqlite:///{settings.database_path}")
    try:
        with Session(engine) as session:
            for project_id in project_ids:
                session.add(ProjectModel(project_id=project_id,product_name="Known project data",requestor="Lab",status="draft"))
            session.commit()
    finally:
        engine.dispose()


@pytest.mark.parametrize("change",["project_id","ltr_number","both","same_source_reused","member_identity_only","ltr_only_metadata"])
def test_equal_material_does_not_hide_a_different_stable_project_identity(library,tmp_path,change):
    import json
    client,settings,_=library
    seed_known_identity(settings,"3"*32,"4"*32)
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
    client,settings,_=library
    seed_known_identity(settings,"3"*32,"4"*32)
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
    assert (Path(members[0]["folder_path"])/source.name/"record.txt").read_text()=="original evidence"
    assert not (target/".connlab/library.json").exists()
    assert not (source/".connlab/library.json").exists()
    assert (source/"record.txt").read_text()=="original evidence"
