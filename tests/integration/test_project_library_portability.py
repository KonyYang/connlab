import pytest
from hashlib import sha256
import json
from pathlib import Path
import shutil
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from backend.shared.config import Settings
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.models import ProjectModel
from backend.infrastructure.storage.models_report_authoring import ReportAuthoringRevisionModel
from backend.api.routes_project_library import router, get_project_library_service
from backend.application.project_library.service import ProjectLibraryService
from backend.infrastructure.project_library.files import LibraryFiles
from backend.infrastructure.project_library.portability import ProjectPortability
from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository


def app_at(root):
    settings = Settings(root / "Data", root / "Projects", root / "Templates", root / "Data" / "connlab.sqlite3", library_root=root)
    settings.ensure_directories()
    engine = create_engine(f"sqlite:///{settings.database_path}", connect_args={"check_same_thread": False})
    init_db(engine)
    app = FastAPI()
    app.include_router(router)
    def service():
        with Session(engine) as session:
            store = ProjectLibraryRepository(session)
            files = LibraryFiles(settings)
            yield ProjectLibraryService(store, settings, files=files,
                portability=ProjectPortability(store, files, settings), opener=lambda path: None)
    app.dependency_overrides[get_project_library_service] = service
    return TestClient(app), settings, engine


def confirm(client, url, plan):
    response = client.post(url, json={"plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"]})
    assert response.status_code == 200, response.text
    return response.json()


def test_project_travels_without_source_database_and_preserves_report_evidence(tmp_path):
    a, settings_a, engine_a = app_at(tmp_path / "A")
    b, settings_b, engine_b = app_at(tmp_path / "B")
    source = tmp_path / "old" / "DL-2026-09-032 Manual project"
    source.mkdir(parents=True)
    (source / "result.csv").write_text("P1,12.34", encoding="utf-8")
    plan = a.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    batch = a.post("/api/project-library/batches", json={**{k: plan[k] for k in ("plan_id", "fingerprint")}, "selected": [str(source)]}).json()
    member_id = batch["items"][0]["member_id"]
    take_plan = a.get(f"/api/project-library/members/{member_id}/takeover-plan").json()
    managed = confirm(a, f"/api/project-library/members/{member_id}/takeover", take_plan)
    project_id = managed["project_id"]
    content = b"evidence from computer A"
    content_hash = sha256(content).hexdigest()
    evidence = settings_a.data_dir / "report_authoring_assets" / sha256(project_id.encode()).hexdigest() / (content_hash + ".txt")
    evidence.parent.mkdir(parents=True)
    evidence.write_bytes(content)
    payload = {"project_id": project_id, "revision": 1, "sources": [{"source_id": "source-A", "role": "evidence", "file_name": "evidence.txt", "sha256": content_hash, "size_bytes": len(content), "created_at": "2026-10-27T00:00:00Z", "report_dl": ""}], "mappings": [], "base_source_id": None, "outputs": [], "results": [], "customer_outputs": []}
    with Session(engine_a) as session:
        session.add(ReportAuthoringRevisionModel(project_id=project_id, revision=1, payload_json=json.dumps(payload)))
        second = {**payload, "revision": 2, "base_source_id": "source-A"}
        session.add(ReportAuthoringRevisionModel(project_id=project_id, revision=2, payload_json=json.dumps(second)))
        session.commit()
    with Session(engine_b) as session:
        session.add(ProjectModel(project_id="unrelated", project_no=None, product_name="Other", requestor="Other", status="draft"))
        session.flush()
        session.add(ReportAuthoringRevisionModel(project_id="unrelated", revision=1, payload_json=json.dumps({"sources": []})))
        session.commit()
    info = a.get(f"/api/project-library/members/{member_id}/portable").json()
    prepared = a.post(f"/api/project-library/members/{member_id}/prepare", json={"fingerprint": info["fingerprint"]})
    assert prepared.status_code == 200, prepared.text
    assert prepared.json()["record_counts"]["report_authoring_revisions"] == 2
    member = a.get(f"/api/project-library/members/{member_id}").json()
    travelling = tmp_path / "copied to another disk" / Path(member["folder_path"]).name
    shutil.copytree(member["folder_path"], travelling)
    engine_a.dispose()
    settings_a.database_path.rename(settings_a.database_path.with_suffix(".inaccessible"))
    shutil.rmtree(settings_a.projects_dir)
    restore_plan = b.post("/api/project-library/restore-plan", json={"folder": str(travelling)}).json()
    assert restore_plan["status"] == "ready", restore_plan
    restored = confirm(b, "/api/project-library/restore", restore_plan)
    assert restored["member"]["project_id"] == project_id
    assert restored["member"]["can_continue"] is True
    assert restored["member"]["snapshot_status"] == "current"
    assert (Path(restored["member"]["folder_path"]) / "result.csv").read_text() == "P1,12.34"
    restored_evidence = settings_b.data_dir / "report_authoring_assets" / sha256(project_id.encode()).hexdigest() / (content_hash + ".txt")
    assert restored_evidence.read_bytes() == content
    with Session(engine_b) as session:
        rows = list(session.scalars(select(ReportAuthoringRevisionModel).where(ReportAuthoringRevisionModel.project_id == project_id)))
        assert len(rows) == 2
        assert json.loads(rows[0].payload_json)["sources"][0]["source_id"] == "source-A"
        assert rows[0].id != 1
    repeated = b.post("/api/project-library/restore-plan", json={"folder": str(travelling)}).json()
    assert repeated["status"] == "already_added", repeated
    assert confirm(b, "/api/project-library/restore", repeated)["status"] == "already_added"
    engine_b.dispose()


def prepared_manual_project(client, root):
    source = root / "DL-2026-09-032 History"
    source.mkdir(parents=True)
    (source / "result.txt").write_text("source result", encoding="utf-8")
    plan = client.post("/api/project-library/intake-plan", json={"sources": [str(source)]}).json()
    batch = client.post("/api/project-library/batches", json={**{k: plan[k] for k in ("plan_id", "fingerprint")}, "selected": [str(source)]}).json()
    member_id = batch["items"][0]["member_id"]
    plan = client.get(f"/api/project-library/members/{member_id}/takeover-plan").json()
    member = confirm(client, f"/api/project-library/members/{member_id}/takeover", plan)["member"]
    info = client.get(f"/api/project-library/members/{member_id}/portable").json()
    response = client.post(f"/api/project-library/members/{member_id}/prepare", json={"fingerprint": info["fingerprint"]})
    assert response.status_code == 200, response.text
    return member


def test_explicit_replacement_preserves_target_recovery_copy_and_binds_revision(tmp_path):
    a, _, ea = app_at(tmp_path / "A")
    b, _, eb = app_at(tmp_path / "B")
    member_a = prepared_manual_project(a, tmp_path / "old")
    plan = b.post("/api/project-library/restore-plan", json={"folder": member_a["folder_path"]}).json()
    member_b = confirm(b, "/api/project-library/restore", plan)["member"]
    (Path(member_b["folder_path"]) / "target-only.txt").write_text("retain target evidence", encoding="utf-8")
    with Session(eb) as session:
        session.get(ProjectModel, member_b["project_id"]).product_name = "Target revision"
        session.commit()
    review = b.post("/api/project-library/restore-plan", json={"folder": member_a["folder_path"]}).json()
    assert review["status"] == "conflict"
    assert "replace_working_copy" in review["resolution_options"]
    plan = b.post("/api/project-library/restore-plan", json={"folder": member_a["folder_path"], "resolution": "replace_working_copy"}).json()
    assert plan["status"] == "ready", plan
    assert plan["backup_path"]
    response = b.post("/api/project-library/restore", json={"plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"], "resolution": "replace_working_copy"})
    assert response.status_code == 200, response.text
    restored = response.json()
    assert restored["member"]["member_id"] == member_b["member_id"]
    assert restored["member"]["can_continue"] is True
    backup = b.get("/api/project-library/members/" + restored["backup_member_id"]).json()
    assert backup["is_history"] is True
    assert backup["can_continue"] is False
    assert (Path(backup["folder_path"]) / "target-only.txt").read_text() == "retain target evidence"
    packet = json.loads((Path(backup["folder_path"]) / ".connlab/portable/snapshot.json").read_text())
    assert packet["body"]["rows"]["projects"][0]["product_name"] == "Target revision"
    assert not (Path(restored["member"]["folder_path"]) / "target-only.txt").exists()
    ea.dispose()
    eb.dispose()


def test_same_ltr_different_identity_can_be_retained_as_read_only_history(tmp_path):
    from backend.infrastructure.storage.models import LtrRecordModel
    a, _, ea = app_at(tmp_path / "A")
    b, _, eb = app_at(tmp_path / "B")
    member_a = prepared_manual_project(a, tmp_path / "old")
    with Session(eb) as session:
        session.add(ProjectModel(project_id="target-owner", product_name="Existing owner", requestor="Lab", status="draft"))
        session.flush()
        session.add(LtrRecordModel(ltr_id="target-ltr", project_id="target-owner", ltr_number="DL-2026-09-032", status="registered", is_current_owner=True))
        session.commit()
    review = b.post("/api/project-library/restore-plan", json={"folder": member_a["folder_path"]}).json()
    assert "keep_as_history" in review["resolution_options"]
    plan = b.post("/api/project-library/restore-plan", json={"folder": member_a["folder_path"], "resolution": "keep_as_history"}).json()
    assert plan["status"] == "ready", plan
    response = b.post("/api/project-library/restore", json={"plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"], "resolution": "keep_as_history"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["status"] == "history_kept"
    assert result["member"]["is_history"] is True
    assert result["member"]["can_continue"] is False
    assert b.get(f"/api/project-library/members/{result['member']['member_id']}/takeover-plan").json()["blockers"]
    assert b.get("/api/project-library/members", params={"q":"History"}).json()["items"]
    with Session(eb) as session:
        assert session.get(LtrRecordModel, "target-ltr").is_current_owner is True
        assert session.get(ProjectModel, member_a["project_id"]).registry_state == "history"
    ea.dispose()
    eb.dispose()


def test_nonempty_complete_graph_restores_and_continues_without_computer_a(tmp_path, monkeypatch):
    from tests.fixtures.project_library.full_graph import seed_full_graph
    from backend.infrastructure.project_library.ownership import TABLES
    from sqlalchemy import text
    with seed_full_graph(tmp_path / "A") as graph:
        lab = graph["lab"]
        client_a = lab["client"]
        source = str(graph["project_root"])
        plan = client_a.post("/api/project-library/intake-plan", json={"sources": [source]}).json()
        batch = client_a.post("/api/project-library/batches", json={**{k: plan[k] for k in ("plan_id", "fingerprint")}, "selected": [source]}).json()
        assert batch["counts"]["added"] == 1, batch
        member_id = batch["items"][0]["member_id"]
        member = client_a.get(f"/api/project-library/members/{member_id}").json()
        assert member["project_id"] == "P1"
        info = client_a.get(f"/api/project-library/members/{member_id}/portable").json()
        assert not info["blockers"], info
        prepared = client_a.post(f"/api/project-library/members/{member_id}/prepare", json={"fingerprint": info["fingerprint"]})
        assert prepared.status_code == 200, prepared.text
        assert prepared.json()["status"] == "current", prepared.text
        assert prepared.json()["record_counts"]["precheck_issues"] == 10
        travelling = tmp_path / "USB" / Path(source).name
        shutil.copytree(source, travelling)
        expected = graph["expected"]
        packet = json.loads((travelling / ".connlab/portable/snapshot.json").read_text(encoding="utf-8"))
        assert any(row["kind"] == "ltr_decision_evidence" and row["replayable"] is False for row in packet["body"]["operation_history"])
        assert any(row["kind"] == "frozen_field_decision_evidence" for row in packet["body"]["operation_history"])
        assert b"QA-NOT-A-REAL-CREDENTIAL-SENTINEL" not in (travelling / ".connlab/portable/snapshot.json").read_bytes()
    # The original DB and every original project/data path are now unavailable.
    for name in ("connlab.sqlite3", "data", "projects", "templates", "public-history"):
        old = tmp_path / "A" / name
        if old.exists():
            old.rename(old.with_name(name + "-unavailable"))
    b, settings_b, engine_b = app_at(tmp_path / "B")
    try:
        plan = b.post("/api/project-library/restore-plan", json={"folder": str(travelling)}).json()
        assert plan["status"] == "ready", plan
        restored = confirm(b, "/api/project-library/restore", plan)
        member_b = restored["member"]
        assert member_b["snapshot_status"] == "current", member_b
        assert member_b["can_continue"] is True
        manifest = json.loads((Path(member_b["folder_path"]) / ".connlab/manifest.json").read_text(encoding="utf-8"))
        assert Path(manifest["official_project_folder_path"]).is_relative_to(settings_b.projects_dir)
        assert Path(manifest["official_project_folder_path"]).is_dir()
        with Session(engine_b) as session:
            for name in TABLES:
                count = session.execute(text('SELECT COUNT(*) FROM "' + name + '"')).scalar_one()
                assert count == expected["source_counts"].get(name, 0), name
            assert session.execute(text("PRAGMA foreign_key_check")).all() == []
            assert session.execute(text("SELECT auto_sync_enabled FROM project_public_folder_workflow_states")).scalar_one() == 0
            assert session.execute(text("SELECT COUNT(*) FROM ltr_duplicate_resolution_tokens")).scalar_one() == 0
            assert session.execute(text("SELECT COUNT(*) FROM frozen_field_revision_requests")).scalar_one() == 0
            assert str(session.execute(text("SELECT duration_value FROM confirmed_matrix_duration_authorities WHERE confirmed_duration_authority_id='duration-1'")).scalar_one()) == "2.5"
        from backend.api import dependencies as deps
        from backend.api.main import app
        def session_b():
            with Session(engine_b) as session:
                yield session
                session.commit()
        app.dependency_overrides[deps.get_settings] = lambda: settings_b
        app.dependency_overrides[deps.get_session] = session_b
        client = TestClient(app, raise_server_exceptions=False)
        try:
            check = client.get("/api/projects/P1/prechecks/latest")
            assert check.status_code == 200, check.text
            assert len(check.json()["issues"]) == 10
            workspace = client.get("/api/projects/P1/report-workspace")
            assert workspace.status_code == 200, workspace.text
            assert len(workspace.json()["datasets"]) == 2
            assert "0.198" in workspace.text and "qa-report-1" in workspace.text
            authoring = client.get("/api/projects/P1/report-workspace/authoring")
            assert authoring.status_code == 200, authoring.text
            state = authoring.json()
            assert state["mappings"][0]["value"] == "2026-06-18"
            assert "0.0855111111111111" in authoring.text
            source = state["sources"][0]
            download = client.get(source["download_url"])
            assert download.status_code == 200
            assert sha256(download.content).hexdigest() == source["sha256"]
            updated = client.post("/api/projects/P1/report-workspace/authoring/mappings", json={"expected_revision": state["revision"], "source_id": source["source_id"], "kind":"specification", "source_locator":"Target computer review", "label":"Restored specification", "value":"Review continued on B", "status":"confirmed", "reason":"Operator continued from carried history"})
            assert updated.status_code == 200, updated.text
            assert updated.json()["revision"] == state["revision"] + 1
            draft = client.get("/api/projects/P1/matrix-drafts/qa-working-matrix")
            assert draft.status_code == 200, draft.text
            data = draft.json()
            data["rows"][1]["requirement"] = "Continue Matrix review on B"
            data["duration_authorities"] = [{**row, "draft_duration_authority_id": row["duration_authority_id"], "draft_group_id": row["group_id"], "draft_row_id": row["row_id"]} for row in data["duration_authorities"]]
            saved = client.put("/api/projects/P1/matrix-drafts/qa-working-matrix", json=data)
            assert saved.status_code == 200, saved.text
            assert saved.json()["rows"][1]["requirement"] == "Continue Matrix review on B"
        finally:
            app.dependency_overrides.clear()
    finally:
        engine_b.dispose()


@pytest.mark.parametrize("gap", ["non_fk_report_base", "json_source", "superseded_fk"])
def test_portable_preflight_blocks_missing_history_without_repairing_source(tmp_path, gap):
    from tests.fixtures.project_library.full_graph import seed_full_graph
    from sqlalchemy import text
    with seed_full_graph(tmp_path / "source") as graph:
        lab = graph["lab"]
        source = str(graph["project_root"])
        plan = lab["client"].post("/api/project-library/intake-plan", json={"sources": [source]}).json()
        batch = lab["client"].post("/api/project-library/batches", json={**{k:plan[k] for k in ("plan_id","fingerprint")}, "selected":[source]}).json()
        member_id = batch["items"][0]["member_id"]
        with lab["factory"]() as session:
            if gap == "non_fk_report_base":
                session.execute(text("UPDATE report_draft_revisions SET base_report_revision_id='missing-history' WHERE report_revision_id='qa-report-2'"))
            elif gap == "json_source":
                record = session.execute(text("SELECT id,payload_json FROM report_authoring_revisions ORDER BY revision DESC LIMIT 1")).first()
                payload = json.loads(record[1])
                payload["base_source_id"] = "missing-source"
                session.execute(text("UPDATE report_authoring_revisions SET payload_json=:payload WHERE id=:id"), {"payload":json.dumps(payload),"id":record[0]})
            else:
                session.execute(text("UPDATE project_matrix_draft_rows SET source_row_snapshot_id='missing-superseded-source' WHERE draft_row_id='pmdr-1'"))
            session.commit()
        status = lab["client"].get(f"/api/project-library/members/{member_id}/portable").json()
        assert status["status"] == "unavailable", status
        assert status["blockers"], status
        assert not (Path(source) / ".connlab/portable/snapshot.json").exists()
        with lab["factory"]() as session:
            if gap == "non_fk_report_base":
                assert session.execute(text("SELECT base_report_revision_id FROM report_draft_revisions WHERE report_revision_id='qa-report-2'")).scalar_one() == "missing-history"
            elif gap == "json_source":
                assert "missing-source" in session.execute(text("SELECT payload_json FROM report_authoring_revisions ORDER BY revision DESC LIMIT 1")).scalar_one()
            else:
                assert session.execute(text("SELECT COUNT(*) FROM project_matrix_draft_rows WHERE source_row_snapshot_id='missing-superseded-source'")).scalar_one() > 0


def test_replacement_failure_rolls_back_and_same_review_can_resume(tmp_path, monkeypatch):
    a, _, ea = app_at(tmp_path / "A")
    b, _, eb = app_at(tmp_path / "B")
    member_a = prepared_manual_project(a, tmp_path / "old")
    plan = b.post("/api/project-library/restore-plan", json={"folder":member_a["folder_path"]}).json()
    member_b = confirm(b, "/api/project-library/restore", plan)["member"]
    folder = Path(member_b["folder_path"])
    (folder / "B-only.txt").write_text("target remains recoverable", encoding="utf-8")
    with Session(eb) as session:
        session.get(ProjectModel, member_b["project_id"]).product_name = "B historical test"
        session.commit()
    plan = b.post("/api/project-library/restore-plan", json={"folder":member_a["folder_path"], "resolution":"replace_working_copy"}).json()
    original = ProjectPortability._insert
    def disk_failure(self, *args, **kwargs):
        if kwargs.get("replace_rows") is not None:
            raise OSError("simulated publication failure")
        return original(self, *args, **kwargs)
    monkeypatch.setattr(ProjectPortability, "_insert", disk_failure)
    request = {"plan_id":plan["plan_id"], "fingerprint":plan["fingerprint"], "resolution":"replace_working_copy"}
    failed = b.post("/api/project-library/restore", json=request)
    assert failed.status_code == 422, failed.text
    assert (folder / "B-only.txt").read_text() == "target remains recoverable"
    with Session(eb) as session:
        assert session.get(ProjectModel, member_b["project_id"]).product_name == "B historical test"
    monkeypatch.setattr(ProjectPortability, "_insert", original)
    resumed = b.post("/api/project-library/restore", json=request)
    assert resumed.status_code == 200, resumed.text
    backup = b.get("/api/project-library/members/" + resumed.json()["backup_member_id"]).json()
    assert backup["is_history"] is True
    assert backup["snapshot_status"] == "current"
    assert (Path(backup["folder_path"]) / "B-only.txt").read_text() == "target remains recoverable"
    # The retained target packet independently restores its old SQL and files on C.
    c, _, ec = app_at(tmp_path / "C")
    review_c = c.post("/api/project-library/restore-plan", json={"folder":backup["folder_path"]}).json()
    recovered = confirm(c, "/api/project-library/restore", review_c)
    assert (Path(recovered["member"]["folder_path"]) / "B-only.txt").read_text() == "target remains recoverable"
    with Session(ec) as session:
        assert session.get(ProjectModel, member_b["project_id"]).product_name == "B historical test"
    for engine in (ea, eb, ec):
        engine.dispose()


def test_stale_coverage_reports_saved_snapshot_not_unprepared_changes(tmp_path):
    client, _, engine = app_at(tmp_path / "library")
    member = prepared_manual_project(client, tmp_path / "old")
    url = f"/api/project-library/members/{member['member_id']}/portable"
    saved = client.get(url).json()
    (Path(member["folder_path"]) / "unprepared.txt").write_text("new notes",encoding="utf-8")
    with Session(engine) as session:
        session.add(ReportAuthoringRevisionModel(project_id=member["project_id"], revision=1, payload_json=json.dumps({"sources":[],"mappings":[]})))
        session.commit()
    stale = client.get(url).json()
    assert stale["status"] == "stale"
    assert stale["created_at"] == saved["created_at"]
    assert stale["file_count"] == saved["file_count"]
    assert stale["record_counts"]["report_authoring_revisions"] == 0
    assert stale["warnings"]
    refreshed = client.post(url.rsplit("/",1)[0]+"/prepare", json={"fingerprint":stale["fingerprint"]}).json()
    assert refreshed["status"] == "current"
    assert refreshed["file_count"] == saved["file_count"]+1
    assert refreshed["record_counts"]["report_authoring_revisions"] == 1
    engine.dispose()


def test_self_consistent_portable_package_never_grants_target_public_write_permission(tmp_path):
    from tests.fixtures.project_library.full_graph import seed_full_graph
    from backend.infrastructure.project_library.files import fingerprint
    from sqlalchemy import text
    with seed_full_graph(tmp_path / "A") as graph:
        client=graph["lab"]["client"]
        source=str(graph["project_root"])
        plan=client.post("/api/project-library/intake-plan",json={"sources":[source]}).json()
        batch=client.post("/api/project-library/batches",json={**{k:plan[k] for k in ("plan_id","fingerprint")},"selected":[source]}).json()
        member_id=batch["items"][0]["member_id"]
        status=client.get(f"/api/project-library/members/{member_id}/portable").json()
        response=client.post(f"/api/project-library/members/{member_id}/prepare",json={"fingerprint":status["fingerprint"]})
        assert response.status_code==200,response.text
        travelling=tmp_path/"USB"/Path(source).name
        shutil.copytree(source,travelling)
    packet_path=travelling/".connlab/portable/snapshot.json"
    packet=json.loads(packet_path.read_text(encoding="utf-8"))
    body=packet["body"]
    body["rows"]["project_public_folder_workflow_states"][0]["auto_sync_enabled"]=True
    content={key:body[key] for key in ("project_id","ltr_number","title","rows","files","assets","operation_history")}
    body["source_signature"]=fingerprint(content)
    packet_path.write_text(json.dumps({"body":body,"checksum":fingerprint(body)}),encoding="utf-8")
    b,_,engine=app_at(tmp_path/"B")
    plan=b.post("/api/project-library/restore-plan",json={"folder":str(travelling)}).json()
    assert plan["status"]=="ready",plan
    confirm(b,"/api/project-library/restore",plan)
    with Session(engine) as session:
        assert session.execute(text("SELECT auto_sync_enabled FROM project_public_folder_workflow_states")).scalar_one()==0
    engine.dispose()


def test_carried_test_data_cannot_be_bypassed_by_plain_intake_or_empty_takeover(tmp_path):
    a, _, ea = app_at(tmp_path/"A")
    b, _, eb = app_at(tmp_path/"B")
    source=prepared_manual_project(a,tmp_path/"old")
    for corrupt in (False,True):
        if corrupt:
            (Path(source["folder_path"])/".connlab/portable/snapshot.json").write_text("{}",encoding="utf-8")
        plan=b.post("/api/project-library/intake-plan",json={"sources":[source["folder_path"]]}).json()
        assert plan["items"][0]["status"]=="conflict",plan
        assert plan["items"][0]["can_keep_separate"] is False
        assert "restore" in " ".join(plan["items"][0]["warnings"]).lower()
        result=b.post("/api/project-library/batches",json={**{k:plan[k] for k in ("plan_id","fingerprint")},"selected":[source["folder_path"]],"keep_separate":[source["folder_path"]]}).json()
        assert result["counts"]["added"]==0,result
    raw=tmp_path/"Raw old project"
    raw.mkdir()
    (raw/"note.txt").write_text("raw note",encoding="utf-8")
    plan=b.post("/api/project-library/intake-plan",json={"sources":[str(raw)]}).json()
    result=b.post("/api/project-library/batches",json={**{k:plan[k] for k in ("plan_id","fingerprint")},"selected":[str(raw)]}).json()
    member=b.get("/api/project-library/members/"+result["items"][0]["member_id"]).json()
    packet=Path(member["folder_path"])/".connlab/portable/snapshot.json"
    packet.parent.mkdir(parents=True)
    packet.write_text("{}",encoding="utf-8")
    review=b.get(f"/api/project-library/members/{member['member_id']}/takeover-plan").json()
    assert review["blockers"]
    assert b.post(f"/api/project-library/members/{member['member_id']}/takeover",json={k:review[k] for k in ("plan_id","fingerprint")}).status_code==409
    with Session(eb) as session:
        assert list(session.scalars(select(ProjectModel)))==[]
    ea.dispose();eb.dispose()


@pytest.mark.parametrize("damage", ["version", "shape", "checksum", "unbound_path", "duplicate_record"])
def test_portable_inspection_rejects_unsupported_or_damaged_packet_before_target_write(tmp_path,damage):
    from backend.infrastructure.project_library.files import fingerprint
    a,_,ea=app_at(tmp_path/"A")
    b,settings_b,eb=app_at(tmp_path/"B")
    member=prepared_manual_project(a,tmp_path/"old")
    path=Path(member["folder_path"])/".connlab/portable/snapshot.json"
    packet=json.loads(path.read_text(encoding="utf-8"))
    body=packet["body"]
    if damage=="version":
        body["format_version"]=99
    elif damage=="shape":
        body["assets"]=[{"blob":"broken"}]
    elif damage=="unbound_path":
        body["rows"]["project_folder_records"]=[{"folder_id":"bad-folder", "project_id":member["project_id"], "folder_path":str(tmp_path/"untrusted-outside"), "created_on":"2026-10-27"}]
    elif damage=="duplicate_record":
        body["rows"]["projects"].append(dict(body["rows"]["projects"][0]))
    else:
        body["title"]="checksum changed"
    if damage!="checksum":
        content={key:body[key] for key in ("project_id","ltr_number","title","rows","files","assets","operation_history")}
        body["source_signature"]=fingerprint(content)
        packet["checksum"]=fingerprint(body)
    path.write_text(json.dumps(packet),encoding="utf-8")
    review=b.post("/api/project-library/restore-plan",json={"folder":member["folder_path"]})
    assert review.status_code==200,review.text
    assert review.json()["status"]=="unavailable",review.text
    assert review.json()["blockers"]
    assert not list(settings_b.projects_dir.iterdir())
    with Session(eb) as session:
        assert list(session.scalars(select(ProjectModel)))==[]
    ea.dispose();eb.dispose()


def test_replacement_blocks_cross_project_non_fk_references(tmp_path):
    from tests.fixtures.project_library.full_graph import seed_full_graph
    from backend.infrastructure.storage.models_result_dataset import ResultDatasetRevisionModel
    from dataclasses import replace
    from tests.unit.test_result_dataset_repository import _dataset
    from backend.infrastructure.storage.repositories.result_dataset import ResultDatasetRepository
    with seed_full_graph(tmp_path/"A") as graph:
        a=graph["lab"]["client"];source=str(graph["project_root"])
        plan=a.post("/api/project-library/intake-plan",json={"sources":[source]}).json()
        batch=a.post("/api/project-library/batches",json={**{k:plan[k] for k in ("plan_id","fingerprint")},"selected":[source]}).json()
        member_id=batch["items"][0]["member_id"]
        info=a.get(f"/api/project-library/members/{member_id}/portable").json()
        assert a.post(f"/api/project-library/members/{member_id}/prepare",json={"fingerprint":info["fingerprint"]}).status_code==200
        travelling=tmp_path/"USB"/Path(source).name
        shutil.copytree(source,travelling)
    b,_,engine=app_at(tmp_path/"B")
    plan=b.post("/api/project-library/restore-plan",json={"folder":str(travelling)}).json()
    member=confirm(b,"/api/project-library/restore",plan)["member"]
    (Path(member["folder_path"])/"B-change.txt").write_text("target revision",encoding="utf-8")
    with Session(engine) as session:
        session.add(ProjectModel(project_id="other-project",product_name="Unrelated",requestor="QA",status="draft"))
        session.flush()
        dataset=replace(_dataset("other-dataset",1),project_id="other-project",confirmed_matrix_id="cmv-1",confirmed_matrix_revision=2)
        ResultDatasetRepository(session).create_dataset(dataset)
        session.commit()
    review=b.post("/api/project-library/restore-plan",json={"folder":str(travelling),"resolution":"replace_working_copy"}).json()
    assert review["status"]=="unavailable",review
    assert any("another project" in message.lower() for message in review["blockers"])
    with Session(engine) as session:
        assert session.get(ResultDatasetRevisionModel,"other-dataset") is not None
    engine.dispose()


def test_daily_title_and_location_remain_available_with_preserved_incomplete_history(tmp_path):
    from tests.fixtures.project_library.full_graph import seed_full_graph
    from sqlalchemy import text
    with seed_full_graph(tmp_path/"source") as graph:
        client=graph["lab"]["client"];source=str(graph["project_root"])
        plan=client.post("/api/project-library/intake-plan",json={"sources":[source]}).json()
        batch=client.post("/api/project-library/batches",json={**{k:plan[k] for k in ("plan_id","fingerprint")},"selected":[source]}).json()
        member_id=batch["items"][0]["member_id"]
        with graph["lab"]["factory"]() as session:
            session.execute(text("UPDATE project_matrix_draft_rows SET source_row_snapshot_id='missing-historic-source' WHERE draft_row_id='pmdr-1'"))
            session.commit()
        blocked=client.get(f"/api/project-library/members/{member_id}/portable").json()
        assert blocked["blockers"]
        plan=client.post(f"/api/project-library/members/{member_id}/title-plan",json={"title":"Changed descriptive title"}).json()
        changed=confirm(client,f"/api/project-library/members/{member_id}/title",plan)
        assert changed["title"]=="Changed descriptive title"
        root=Path(changed["folder_path"])
        moved=root.with_name(root.name+" relocated")
        root.rename(moved)
        plan=client.post(f"/api/project-library/members/{member_id}/location-plan",json={"folder":str(moved)}).json()
        located=confirm(client,f"/api/project-library/members/{member_id}/location",plan)
        assert located["folder_path"]==str(moved)
        with graph["lab"]["factory"]() as session:
            assert session.execute(text("SELECT source_row_snapshot_id FROM project_matrix_draft_rows WHERE draft_row_id='pmdr-1'")).scalar_one()=="missing-historic-source"
        assert client.get(f"/api/project-library/members/{member_id}/portable").json()["blockers"]


@pytest.mark.parametrize("foreign_token", ["@data/local_identity.sqlite3", "@data/report_authoring_assets/" + "a"*64 + "/evidence.docx"])
def test_receiver_rejects_self_consistent_assets_outside_own_project_partition(tmp_path,foreign_token):
    from tests.fixtures.project_library.full_graph import seed_full_graph
    from backend.infrastructure.project_library.files import fingerprint
    from backend.infrastructure.project_library.ownership import transform_paths
    with seed_full_graph(tmp_path/"A") as graph:
        a=graph["lab"]["client"];source=str(graph["project_root"])
        plan=a.post("/api/project-library/intake-plan",json={"sources":[source]}).json()
        batch=a.post("/api/project-library/batches",json={**{k:plan[k] for k in ("plan_id","fingerprint")},"selected":[source]}).json()
        member_id=batch["items"][0]["member_id"]
        info=a.get(f"/api/project-library/members/{member_id}/portable").json()
        assert a.post(f"/api/project-library/members/{member_id}/prepare",json={"fingerprint":info["fingerprint"]}).status_code==200
        travelling=tmp_path/"USB"/Path(source).name
        shutil.copytree(source,travelling)
    path=travelling/".connlab/portable/snapshot.json"
    packet=json.loads(path.read_text(encoding="utf-8"));body=packet["body"]
    original=body["assets"][0]["token"]
    body["assets"][0]["token"]=foreign_token
    body["rows"]=transform_paths(body["rows"],lambda value:foreign_token if value==original else value)
    content={key:body[key] for key in ("project_id","ltr_number","title","rows","files","assets","operation_history")}
    body["source_signature"]=fingerprint(content)
    path.write_text(json.dumps({"body":body,"checksum":fingerprint(body)}),encoding="utf-8")
    b,settings,engine=app_at(tmp_path/"B")
    sentinel=settings.data_dir/foreign_token[len("@data/"):]
    sentinel.parent.mkdir(parents=True,exist_ok=True)
    sentinel.write_bytes(b"target private or unrelated project sentinel")
    review=b.post("/api/project-library/restore-plan",json={"folder":str(travelling)}).json()
    assert review["status"]=="unavailable",review
    assert any("partition" in message.lower() for message in review["blockers"]),review
    assert sentinel.read_bytes()==b"target private or unrelated project sentinel"
    assert not list(settings.projects_dir.iterdir())
    engine.dispose()


@pytest.mark.parametrize("crash_after_commit", [False,True])
def test_process_crash_during_working_copy_switch_recovers_same_confirmation(tmp_path,crash_after_commit):
    import subprocess
    import sys
    a,_,ea=app_at(tmp_path/"A");b,settings,eb=app_at(tmp_path/"B")
    source=prepared_manual_project(a,tmp_path/"old")
    plan=b.post("/api/project-library/restore-plan",json={"folder":source["folder_path"]}).json()
    target=confirm(b,"/api/project-library/restore",plan)["member"]
    (Path(target["folder_path"])/"target-old.txt").write_text("old evidence",encoding="utf-8")
    plan=b.post("/api/project-library/restore-plan",json={"folder":source["folder_path"],"resolution":"replace_working_copy"}).json()
    assert plan["status"]=="ready",plan
    script = """
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.shared.config import Settings
from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository
from backend.infrastructure.project_library.files import LibraryFiles
from backend.infrastructure.project_library.portability import ProjectPortability
root=Path(ROOT)
settings=Settings(root/'Data',root/'Projects',root/'Templates',root/'Data'/'connlab.sqlite3',library_root=root)
engine=create_engine('sqlite:///'+str(settings.database_path))
from backend.infrastructure.storage.database import init_db
init_db(engine)
with Session(engine) as session:
    store=ProjectLibraryRepository(session)
    operation=ProjectPortability(store,LibraryFiles(settings),settings)
    original=operation._insert
    def crash(*args,**kwargs):
        if AFTER:
            original(*args,**kwargs)
        os._exit(42)
    operation._insert=crash
    operation.restore(PLAN,EXPECTED,'replace_working_copy')
""".replace("ROOT",repr(str(settings.library_root))).replace("AFTER",repr(crash_after_commit)).replace("PLAN",repr(plan["plan_id"])).replace("EXPECTED",repr(plan["fingerprint"]))
    result=subprocess.run([sys.executable,"-c",script],capture_output=True,text=True,timeout=20)
    assert result.returncode==42,result.stderr
    response=b.post("/api/project-library/restore",json={"plan_id":plan["plan_id"],"fingerprint":plan["fingerprint"],"resolution":"replace_working_copy"})
    assert response.status_code==200,response.text
    restored=response.json()
    assert restored["member"]["can_continue"] is True
    backup=b.get("/api/project-library/members/"+restored["backup_member_id"]).json()
    assert (Path(backup["folder_path"])/"target-old.txt").read_text()=="old evidence"
    assert not (Path(restored["member"]["folder_path"])/"target-old.txt").exists()
    ea.dispose();eb.dispose()


def test_working_copy_switch_respects_existing_project_writer_slot(tmp_path):
    a,_,ea=app_at(tmp_path/"A");b,settings,eb=app_at(tmp_path/"B")
    source=prepared_manual_project(a,tmp_path/"old")
    plan=b.post("/api/project-library/restore-plan",json={"folder":source["folder_path"]}).json()
    member=confirm(b,"/api/project-library/restore",plan)["member"]
    (Path(member["folder_path"])/"target-note.txt").write_text("working data",encoding="utf-8")
    plan=b.post("/api/project-library/restore-plan",json={"folder":source["folder_path"],"resolution":"replace_working_copy"}).json()
    request={"plan_id":plan["plan_id"],"fingerprint":plan["fingerprint"],"resolution":"replace_working_copy"}
    with LibraryFiles(settings).project_lock(member["project_id"]):
        busy=b.post("/api/project-library/restore",json=request)
        assert busy.status_code==409,busy.text
        assert (Path(member["folder_path"])/"target-note.txt").read_text()=="working data"
    assert b.post("/api/project-library/restore",json=request).status_code==200
    ea.dispose();eb.dispose()
