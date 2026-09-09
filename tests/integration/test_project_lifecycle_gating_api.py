from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.domain import ProjectStatus, LtrRecord, LtrStatus
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import ProjectRepository, LtrRecordRepository
from backend.shared.config import Settings
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.storage.models import (
    ApplicationFormModel, IntakeCaseModel, IntakePackageModel,
    PrecheckIssueModel, PrecheckResultModel, ProjectModel,
)


def test_ltr_preview_api_is_blocked_before_confirmed_project_data(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        project_id = client.post(
            "/api/projects",
            json={
                "project_no": "PRJ-GATE-1",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        ).json()["project_id"]

        response = client.get(
            f"/api/projects/{project_id}/ltr/preview",
            params={"year": 2026, "month": 4},
        )

        assert response.status_code == 400
        assert "confirmed project data" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_folder_generate_api_is_blocked_before_ltr_registration(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        project_id = client.post(
            "/api/projects",
            json={
                "project_no": "PRJ-GATE-2",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        ).json()["project_id"]
        template = tmp_path / "template"
        template.mkdir()

        response = client.post(
            f"/api/projects/{project_id}/folder/generate",
            json={"template_path": str(template), "target_root": str(tmp_path)},
        )

        assert response.status_code == 400
        assert "registered LTR" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_closed_project_rejects_ltr_registration_api(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        project_id = client.post(
            "/api/projects",
            json={
                "project_no": "PRJ-GATE-3",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        ).json()["project_id"]
        _set_project_status(engine, project_id, tmp_path, ProjectStatus.CLOSED)

        response = client.post(
            f"/api/projects/{project_id}/ltr",
            json={"ltr_number": "LTR-GATE"},
        )

        assert response.status_code == 400
        assert "closed" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path: Path) -> tuple[TestClient, object]:
    """Create a test client backed by an isolated database."""
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
        """Yield a test database session."""
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: Settings(
        data_dir=tmp_path / "data", projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates", database_path=tmp_path / "connlab.sqlite3",
    )
    return TestClient(app), engine


def _set_project_status(
    engine,
    project_id: str,
    tmp_path: Path,
    status: ProjectStatus,
) -> None:
    """Update project status in an isolated test database."""
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        repository = ProjectRepository(session)
        project = repository.get(project_id)
        assert project is not None
        repository.update(project.with_status(status))
        session.commit()


@pytest.mark.parametrize("location", ["trash", "history"])
@pytest.mark.parametrize("path,payload", [
    ("/stop", {"reason": "Old tab"}),
    ("/official-workspace/create", {}),
])
def test_hidden_project_rejects_old_tab_write_without_changing_lifecycle(tmp_path, location, path, payload):
    client, engine = _client(tmp_path)
    try:
        project_id = _registry_project(client, engine, location)
        response = client.post(f"/api/projects/{project_id}{path}", json=payload)
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "project_registry_read_only"
        with create_session_factory(engine)() as session:
            project = session.get(ProjectModel, project_id)
            assert project.lifecycle_state == "active"
            assert project.stopped_reason is None
            assert project.registry_state == location
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


@pytest.mark.parametrize("endpoint,method,payload", [
    ("/api/application-forms/guard-form/precheck/run", "post", None),
    ("/api/precheck-issues/guard-issue/resolve", "patch", None),
    ("/api/intake-cases/guard-case/review-fields", "patch", {"fields": {"requester": "Changed"}}),
    ("/api/intake-packages/guard-package/draft/discard", "post", None),
])
def test_hidden_project_rejects_indirect_intake_writes(tmp_path, endpoint, method, payload):
    client, engine = _client(tmp_path)
    try:
        project_id = _registry_project(client, engine, "trash")
        with create_session_factory(engine)() as session:
            session.add(IntakePackageModel(package_id="guard-package", source_type="manual", status="confirmed",
                source_original_name="Synthetic", source_stored_path=str(tmp_path / "source")))
            session.flush()
            session.add(IntakeCaseModel(case_id="guard-case", package_id="guard-package", status="confirmed",
                confirmed_project_id=project_id))
            session.add(ApplicationFormModel(form_id="guard-form", project_id=project_id, form_no="F", revision="1", requester="Alice"))
            session.flush()
            session.add(PrecheckResultModel(result_id="guard-result", application_form_id="guard-form", status="failed"))
            session.flush()
            session.add(PrecheckIssueModel(issue_id="guard-issue", result_id="guard-result", category="form_metadata",
                level="error", message="Synthetic issue", resolved=False))
            session.commit()
        response = getattr(client, method)(endpoint, json=payload)
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "project_registry_read_only"
        with create_session_factory(engine)() as session:
            assert session.get(PrecheckIssueModel, "guard-issue").resolved is False
            assert len(list(session.scalars(select(PrecheckResultModel)))) == 1
            assert session.get(IntakeCaseModel, "guard-case") is not None
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_generation_lock_rejects_ordinary_business_write(tmp_path):
    client, engine = _client(tmp_path)
    try:
        project_id = _registry_project(client, engine, "active")
        journal = GenerationJournal(tmp_path / "data" / "project_folder_generation")
        with journal.lock(project_id):
            response = client.post(f"/api/projects/{project_id}/stop", json={"reason": "Old tab"})
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "project_registry_busy"
        with create_session_factory(engine)() as session:
            assert session.get(ProjectModel, project_id).lifecycle_state == "active"
            assert session.get(ProjectModel, project_id).stopped_reason is None
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _registry_project(client, engine, location):
    response = client.post("/api/projects", json={"project_no": "GUARD-SYNTHETIC", "product_name": "Synthetic", "requestor": "Alice"})
    assert response.status_code == 201
    project_id = response.json()["project_id"]
    with create_session_factory(engine)() as session:
        session.get(ProjectModel, project_id).registry_state = location
        session.commit()
    return project_id


def test_business_write_invalidates_restore_preview_of_conflicting_project(tmp_path):
    client, engine = _client(tmp_path)
    try:
        old = _registry_project(client, engine, "trash")
        current = _registry_project(client, engine, "active")
        with create_session_factory(engine)() as session:
            for project_id in (old, current):
                LtrRecordRepository(session).create(LtrRecord(ltr_id="ltr-" + project_id,
                    project_id=project_id, ltr_number="DL-2026-01-002", status=LtrStatus.REGISTERED,
                    is_current_owner=False))
            session.add(ApplicationFormModel(form_id="revision-form", project_id=current, form_no="F", revision="1", requester="Alice"))
            session.flush()
            session.add(PrecheckResultModel(result_id="revision-result", application_form_id="revision-form", status="failed"))
            session.flush()
            session.add(PrecheckIssueModel(issue_id="revision-issue", result_id="revision-result", category="form_metadata",
                level="error", message="Resolve this existing issue", resolved=False))
            session.commit()
        preview = client.get(f"/api/project-registry/{old}/preview?action=restore").json()
        assert preview["conflicts"][0]["project_id"] == current
        updated = client.patch("/api/precheck-issues/revision-issue/resolve")
        assert updated.status_code == 200, updated.text
        restore = client.post(f"/api/project-registry/{old}/restore", json={
            "token": preview["token"], "destination": "active", "replace_conflicts": True})
        assert restore.status_code == 409
        assert restore.json()["detail"]["code"] == "project_registry_preview_stale"
        with create_session_factory(engine)() as session:
            assert session.get(ProjectModel, old).registry_state == "trash"
            assert session.get(ProjectModel, current).registry_state == "active"
            assert session.get(PrecheckIssueModel, "revision-issue").resolved is True
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
