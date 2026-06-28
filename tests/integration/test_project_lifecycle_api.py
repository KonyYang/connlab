from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.api.main import app
from backend.domain import (
    ProjectOutputKind,
    ProjectOutputRecord,
    ProjectOutputSource,
    ProjectOutputStatus,
)
from backend.infrastructure.storage.repositories import ProjectOutputRecordRepository
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.shared.config import Settings


def test_lifecycle_stop_resume_and_close_administrative_api(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        project_id = _create_project(client, project_no="DL-2026-06-010")

        initial = client.get(f"/api/projects/{project_id}/lifecycle")
        stopped = client.post(
            f"/api/projects/{project_id}/lifecycle/stop",
            json={"operator": "Lab User"},
        )
        legacy_detail = client.get(f"/api/projects/{project_id}")
        resumed = client.post(
            f"/api/projects/{project_id}/lifecycle/resume",
            json={"operator": "Lab User"},
        )
        closed = client.post(
            f"/api/projects/{project_id}/lifecycle/close-administrative",
            json={"reason": "Customer cancelled.", "operator": "Lab User"},
        )
        resume_closed = client.post(
            f"/api/projects/{project_id}/lifecycle/resume",
            json={"operator": "Lab User"},
        )

        assert initial.status_code == 200
        assert initial.json()["lifecycle_state"] == "active"
        assert stopped.status_code == 200
        assert stopped.json()["lifecycle_state"] == "stopped"
        assert stopped.json()["readonly"] is True
        assert stopped.json()["allowed_actions"] == ["activate", "resume", "close"]
        assert legacy_detail.json()["status"] == "cancelled"
        assert resumed.status_code == 200
        assert resumed.json()["lifecycle_state"] == "active"
        assert resumed.json()["status"] == "draft"
        assert closed.status_code == 200
        assert closed.json()["lifecycle_state"] == "closed"
        assert closed.json()["closure_type"] is None
        assert closed.json()["close_reason_category"] == "other"
        assert closed.json()["close_reason_label"] == "Other"
        assert resume_closed.status_code == 409
        detail = resume_closed.json()["detail"]
        assert detail["code"] == "project_lifecycle_conflict"
        assert detail["project_id"] == project_id
        assert detail["lifecycle_state"] == "closed"
        assert detail["closure_type"] is None
        assert detail["close_reason_category"] == "other"
        assert detail["allowed_actions"] == ["activate"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_close_completed_compatibility_allows_temporary_project_api(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        temp = client.post(
            "/api/projects/temporary",
            json={"request_summary": "Planning only", "requestor": "Alice"},
        )
        assert temp.status_code == 201
        project_id = temp.json()["project_id"]

        response = client.post(
            f"/api/projects/{project_id}/lifecycle/close-completed",
            json={
                "close_note": "Done.",
                "manual_completion_confirmed": True,
                "output_summary_acknowledged": True,
                "operator": "Lab User",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["lifecycle_state"] == "closed"
        assert payload["closure_type"] == "completed"
        assert payload["close_reason_category"] == "completed"
        assert payload["allowed_actions"] == ["activate"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_close_completed_requires_confirmation_and_note_api(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        project_id = _create_project(client, project_no="DL-2026-06-011")
        _register_manual_output(engine, project_id)
        project_id_ack = _create_project(client, project_no="DL-2026-06-012")
        _register_manual_output(engine, project_id_ack, output_record_id="OUT2")
        project_id_closed = _create_project(client, project_no="DL-2026-06-013")
        _register_manual_output(engine, project_id_closed, output_record_id="OUT3")

        missing_note = client.post(
            f"/api/projects/{project_id}/lifecycle/close-completed",
            json={
                "close_note": " ",
                "manual_completion_confirmed": True,
                "output_summary_acknowledged": True,
            },
        )
        missing_ack = client.post(
            f"/api/projects/{project_id_ack}/lifecycle/close-completed",
            json={
                "close_note": "Done.",
                "manual_completion_confirmed": True,
                "output_summary_acknowledged": False,
            },
        )
        closed = client.post(
            f"/api/projects/{project_id_closed}/lifecycle/close-completed",
            json={
                "close_note": "Done.",
                "manual_completion_confirmed": True,
                "output_summary_acknowledged": True,
                "operator": "Lab User",
            },
        )

        assert missing_note.status_code == 409
        assert "Close completed note is required" in missing_note.json()["detail"]["message"]
        assert missing_ack.status_code == 200
        assert missing_ack.json()["completion_summary"]["output_summary_acknowledged"] is False
        assert closed.status_code == 200
        payload = closed.json()
        assert payload["lifecycle_state"] == "closed"
        assert payload["closure_type"] == "completed"
        assert payload["close_reason_category"] == "completed"
        assert payload["completion_summary"]["manual_completion_confirmed"] is True
        assert payload["completion_summary"]["signals"] == {
            "project_identity": "DL-2026-06-013",
            "registered_ltr": False,
            "output_status_summary_available": True,
        }
        output_summary = payload["completion_summary"]["output_status_summary"]
        assert output_summary["project_id"] == project_id_closed
        assert output_summary["items"][0]["output_kind"] == "section2_write_back"
        assert output_summary["items"][0]["status"] == "manual"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_unified_close_and_activate_closed_project_api(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        project_id = _create_project(client, project_no="DL-2026-06-012")

        closed = client.post(
            f"/api/projects/{project_id}/lifecycle/close",
            json={
                "reason_category": "failed",
                "note": "Qualification failed.",
                "operator": "Lab User",
            },
        )
        active_conflict = client.post(
            f"/api/projects/{project_id}/lifecycle/activate",
            json={"reason": " "},
        )
        activated = client.post(
            f"/api/projects/{project_id}/lifecycle/activate",
            json={"reason": "Retest approved.", "operator": "Lab User"},
        )

        assert closed.status_code == 200
        assert closed.json()["lifecycle_state"] == "closed"
        assert closed.json()["closure_type"] is None
        assert closed.json()["close_reason_category"] == "failed"
        assert closed.json()["close_reason_label"] == "Failed"
        assert closed.json()["allowed_actions"] == ["activate"]
        assert active_conflict.status_code == 409
        assert "Activation reason is required" in active_conflict.json()["detail"]["message"]
        assert activated.status_code == 200
        assert activated.json()["lifecycle_state"] == "active"
        assert activated.json()["status"] == "draft"
        assert activated.json()["closure_type"] is None
        assert activated.json()["close_reason_category"] is None
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path: Path) -> tuple[TestClient, object]:
    engine = create_database_engine(
        Settings(
            data_dir=tmp_path / "data",
            projects_dir=tmp_path / "projects",
            templates_dir=tmp_path / "templates",
            database_path=tmp_path / "connlab.sqlite3",
        )
    )
    init_db(engine)
    session_factory = create_session_factory(engine)

    def override_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    return TestClient(app), engine


def _create_project(client: TestClient, *, project_no: str) -> str:
    response = client.post(
        "/api/projects",
        json={
            "project_no": project_no,
            "product_name": "Connector",
            "requestor": "Alice",
        },
    )
    assert response.status_code == 201
    return response.json()["project_id"]


def _register_manual_output(
    engine,
    project_id: str,
    *,
    output_record_id: str = "OUT1",
) -> None:
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        ProjectOutputRecordRepository(session).create(
            ProjectOutputRecord(
                output_record_id=output_record_id,
                project_id=project_id,
                draft_id=None,
                draft_version=None,
                output_kind=ProjectOutputKind.SECTION2_WRITE_BACK,
                output_path="D:/outputs/section2.xlsx",
                output_sha256=None,
                output_size_bytes=None,
                source_context_signature=None,
                status=ProjectOutputStatus.MANUAL,
                source=ProjectOutputSource.MANUAL,
                created_at="2026-06-27T02:00:00+00:00",
                updated_at="2026-06-27T02:00:00+00:00",
                note="Manual output available.",
            )
        )
        session.commit()
