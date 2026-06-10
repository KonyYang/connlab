from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.domain import (
    ApplicationForm,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    Project,
    ProjectStatus,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ApplicationFormRepository,
    ConfirmedMatrixAuthorityRepository,
    ProjectRepository,
)
from backend.shared.config import Settings


def test_section2_sync_preview_returns_field_status(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project_context(tmp_path)

        response = client.get("/api/projects/P1/section2-sync/preview")

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ready"
        assert payload["confirmed_matrix_id"] == "CM1"
        assert payload["confirmed_revision"] == 3
        assert [(field["field_key"], field["status"], field["next_value"]) for field in payload["fields"]] == [
            ("received_date", "will_change", "2026-06-01"),
            ("estimated_completion_date", "will_change", "2026-06-08"),
        ]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_section2_sync_post_updates_application_form_when_expected_identity_matches(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project_context(tmp_path)

        response = client.post(
            "/api/projects/P1/section2-sync",
            json={
                "expected_confirmed_matrix_id": "CM1",
                "expected_confirmed_revision": 3,
                "operator": "MP Cao",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "synced"
        assert payload["operator"] == "MP Cao"
        with session_factory() as session:
            form = ApplicationFormRepository(session).get("FORM1")
            assert form is not None
            assert form.received_date == "2026-06-01"
            assert form.estimated_completion_date == "2026-06-08"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_section2_sync_without_active_confirmed_matrix_returns_409(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project_context(tmp_path, include_matrix=False)

        response = client.get("/api/projects/P1/section2-sync/preview")

        assert response.status_code == 409
        assert "Confirm Matrix authority" in response.text
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_section2_sync_multiple_forms_returns_409_and_leaves_forms_unchanged(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project_context(tmp_path, extra_form=True)

        response = client.post(
            "/api/projects/P1/section2-sync",
            json={"expected_confirmed_matrix_id": "CM1", "expected_confirmed_revision": 3},
        )

        assert response.status_code == 409
        assert "Multiple Application Forms" in response.text
        with session_factory() as session:
            forms = ApplicationFormRepository(session).list_by_project("P1")
            assert {form.form_id: form.received_date for form in forms} == {
                "FORM1": "2026-05-01",
                "FORM2": "2026-05-02",
            }
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_section2_sync_expected_revision_mismatch_returns_409_and_leaves_form_unchanged(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project_context(tmp_path)

        response = client.post(
            "/api/projects/P1/section2-sync",
            json={"expected_confirmed_matrix_id": "CM1", "expected_confirmed_revision": 2},
        )

        assert response.status_code == 409
        assert "Refresh Section 2 dates" in response.text
        with session_factory() as session:
            form = ApplicationFormRepository(session).get("FORM1")
            assert form is not None
            assert form.received_date == "2026-05-01"
            assert form.estimated_completion_date == "2026-05-10"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_section2_sync_invalid_source_date_returns_422_and_leaves_form_unchanged(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project_context(tmp_path, sample_received_date="06/01/2026")

        response = client.post(
            "/api/projects/P1/section2-sync",
            json={"expected_confirmed_matrix_id": "CM1", "expected_confirmed_revision": 3},
        )

        assert response.status_code == 422
        assert "invalid Section 2 date" in response.text
        with session_factory() as session:
            form = ApplicationFormRepository(session).get("FORM1")
            assert form is not None
            assert form.received_date == "2026-05-01"
            assert form.estimated_completion_date == "2026-05-10"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path: Path) -> tuple[TestClient, object, object]:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
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
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app), engine, session_factory


def _seed_project_context(
    tmp_path: Path,
    *,
    include_matrix: bool = True,
    extra_form: bool = False,
    sample_received_date: str | None = "2026-06-01",
) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        ProjectRepository(session).create(
            Project(
                project_id="P1",
                project_no="DL-2026-05-003",
                product_name="Coolpower",
                requestor="MP Cao",
                status=ProjectStatus.LTR_REGISTERED,
                created_on=date(2026, 6, 1),
            )
        )
        form_repo = ApplicationFormRepository(session)
        form_repo.create(_form("FORM1", received_date="2026-05-01", estimated_completion_date="2026-05-10"))
        if extra_form:
            form_repo.create(_form("FORM2", received_date="2026-05-02", estimated_completion_date="2026-05-11"))
        if include_matrix:
            ConfirmedMatrixAuthorityRepository(session).create_snapshot(
                ConfirmedMatrixSnapshot(
                    version=ConfirmedMatrixVersion(
                        confirmed_matrix_id="CM1",
                        project_id="P1",
                        project_matrix_draft_id="DRAFT1",
                        source_import_id="IMPORT1",
                        source_snapshot_id="SNAP1",
                        confirmed_revision=3,
                        is_active_authority=True,
                        status=ConfirmedMatrixStatus.CONFIRMED,
                        confirmed_by="operator",
                        confirmed_at="2026-06-01T00:00:00Z",
                        sample_received_date=sample_received_date,
                        estimated_completion_date="2026-06-08",
                    )
                )
            )
        session.commit()
    engine.dispose()


def _form(
    form_id: str,
    *,
    received_date: str | None,
    estimated_completion_date: str | None,
) -> ApplicationForm:
    return ApplicationForm(
        form_id=form_id,
        project_id="P1",
        form_no="E-3718",
        revision="H",
        requester="MP Cao",
        received_date=received_date,
        estimated_completion_date=estimated_completion_date,
    )
