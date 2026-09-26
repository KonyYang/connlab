from pathlib import Path
from dataclasses import replace

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine

from backend.api import dependencies as deps
from backend.api.main import app
from backend.api.project_folder_generation_composition import ProjectFolderGenerationRunner
from backend.application.project_basic_information_service import (
    ConfirmProjectBasicInformationCommand,
    SaveProjectBasicInformationDraftCommand,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    ExternalResource,
    ExternalResourceType,
    LtrRecord,
    LtrStatus,
    Project,
    ProjectLifecycleState,
    ProjectStatus,
)
from backend.infrastructure.storage.database import Base, create_session_factory
from backend.infrastructure.storage.project_schedule_schema_migration import (
    bootstrap_project_schedule_schema,
)
from backend.shared.config import Settings


def _complete_basic_information_values() -> dict[str, str]:
    return {
        "dl_number": "DL-001",
        "project_type": "NPD",
        "product_description": "Connector",
        "test_item": "Qualification Testing",
        "tests_to_be_performed": "Qualification Testing",
        "requested_by": "Test",
        "project_leader": "Engineer",
        "lab_performing_tests": "Dongguan",
    }


@pytest.mark.parametrize("strategy", ["backup_and_recreate", "update_in_place"])
def test_start_accepts_explicit_existing_folder_strategy(strategy) -> None:
    captured = []

    class Service:
        def start(
            self, project_id, strategy, expected_context, request_id,
            replaces_operation_id=None,
        ):
            captured.append(
                (project_id, strategy, expected_context, request_id, replaces_operation_id)
            )
            return {
                "project_id": project_id,
                "operation_id": "replacement",
                "status": "queued",
                "step": 0,
                "completed_steps": [],
                "message": None,
                "can_restart": False,
            }

    app.dependency_overrides[deps.get_project_folder_generation_service] = Service
    try:
        response = TestClient(app).post(
            "/api/projects/P1/project-folder/generation/start",
            json={
                "expected_context": "fresh-preview",
                "request_id": "continue-request",
                "conflict_strategy": strategy,
                "replaces_operation_id": "locked-operation",
            },
        )
    finally:
        app.dependency_overrides.pop(deps.get_project_folder_generation_service, None)

    assert response.status_code == 202, response.text
    assert captured == [
        ("P1", strategy, "fresh-preview", "continue-request", "locked-operation")
    ]


def test_start_is_blocked_before_writes_when_complete_basic_information_is_unconfirmed(
    tmp_path,
):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "fixture.sqlite",
    )
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    bootstrap_project_schedule_schema(engine)
    sessions = create_session_factory(engine)
    template, destination = tmp_path / "template", tmp_path / "output"
    destination.mkdir()
    for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
        (template / name).mkdir(parents=True)
    with sessions() as session:
        deps.ProjectRepository(session).create(
            Project(
                project_id="P1",
                project_no="DL-001",
                product_name="Connector",
                requestor="Test",
                status=ProjectStatus.DRAFT,
            )
        )
        deps.LtrRecordRepository(session).create(
            LtrRecord(
                ltr_id="ltr",
                project_id="P1",
                ltr_number="DL-001",
                status=LtrStatus.REGISTERED,
            )
        )
        resources = deps.ExternalResourceRepository(session)
        resources.upsert(
            ExternalResource(
                "root", ExternalResourceType.PROJECT_OUTPUT_ROOT, destination
            )
        )
        resources.upsert(
            ExternalResource(
                "template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template
            )
        )
        deps.get_project_basic_information_service(session).save_draft(
            SaveProjectBasicInformationDraftCommand(
                project_id="P1",
                values=_complete_basic_information_values(),
            )
        )
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    service = runner.service()
    queued = []
    service.dispatch = queued.append
    app.dependency_overrides[deps.get_project_folder_generation_service] = lambda: service
    try:
        client = TestClient(app)
        url = "/api/projects/P1/project-folder/generation"
        preview = client.get(url + "/preview")
        assert preview.status_code == 200, preview.text
        assert preview.json()["recovery"] is None
        payload = preview.json()
        guidance = (
            "Basic Information is complete but not confirmed. Open Basic Information "
            "and click Confirm before generating Project Folder outputs."
        )
        assert payload["workspace_preview"]["status"] == "blocked"
        assert payload["workspace_preview"]["blockers"] == [guidance]

        started = client.post(
            url + "/start",
            json={
                "expected_context": payload["expected_context"],
                "request_id": "unconfirmed-basic-information",
            },
        )
        assert started.status_code == 409
        assert started.json()["detail"] == guidance
        assert client.get(url).json() is None
        assert queued == []
        assert list(destination.iterdir()) == []
    finally:
        dependency_override = app.dependency_overrides.pop(
            deps.get_project_folder_generation_service, None
        )
        assert dependency_override is not None
        runner.pool.shutdown()
        engine.dispose()


def test_start_is_blocked_before_writes_when_project_schedule_is_unconfirmed(
    tmp_path,
):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "fixture.sqlite",
    )
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    bootstrap_project_schedule_schema(engine)
    sessions = create_session_factory(engine)
    template, destination = tmp_path / "template", tmp_path / "output"
    destination.mkdir()
    for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
        (template / name).mkdir(parents=True)
    with sessions() as session:
        deps.ProjectRepository(session).create(
            Project(
                project_id="P1",
                project_no="DL-001",
                product_name="Connector",
                requestor="Test",
                status=ProjectStatus.DRAFT,
            )
        )
        deps.LtrRecordRepository(session).create(
            LtrRecord(
                ltr_id="ltr",
                project_id="P1",
                ltr_number="DL-001",
                status=LtrStatus.REGISTERED,
            )
        )
        resources = deps.ExternalResourceRepository(session)
        resources.upsert(
            ExternalResource(
                "root", ExternalResourceType.PROJECT_OUTPUT_ROOT, destination
            )
        )
        resources.upsert(
            ExternalResource(
                "template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template
            )
        )
        deps.get_project_basic_information_service(session).confirm(
            ConfirmProjectBasicInformationCommand(
                project_id="P1",
                values={
                    **_complete_basic_information_values(),
                    "date_lab_received_samples": "2026-09-01",
                },
                confirmed_by="operator",
            )
        )
        deps.ConfirmedMatrixAuthorityRepository(session).create_snapshot(
            ConfirmedMatrixSnapshot(
                version=ConfirmedMatrixVersion(
                    confirmed_matrix_id="CM1",
                    project_id="P1",
                    project_matrix_draft_id="DRAFT1",
                    source_import_id="IMPORT1",
                    source_snapshot_id="SNAP1",
                    confirmed_revision=1,
                    is_active_authority=True,
                    status=ConfirmedMatrixStatus.CONFIRMED,
                    confirmed_by="operator",
                    confirmed_at="2026-09-01T00:00:00Z",
                ),
                groups=(ConfirmedMatrixGroup(
                    confirmed_group_id="CG1", confirmed_matrix_id="CM1",
                    draft_group_id="DG1", source_group_snapshot_id=None,
                    group_order=1, group_key="g1", group_label="1",
                    sample_quantity_expression="1",
                ),),
                rows=(ConfirmedMatrixRow(
                    confirmed_row_id="CR1", confirmed_matrix_id="CM1",
                    draft_row_id="DR1", source_row_snapshot_id=None,
                    row_order=1, test_item="Visual Examination", day_expression="0",
                ),),
                cells=(ConfirmedMatrixCell(
                    confirmed_cell_id="CC1", confirmed_matrix_id="CM1",
                    confirmed_row_id="CR1", confirmed_group_id="CG1",
                    draft_row_id="DR1", draft_group_id="DG1", cell_value="1",
                ),),
            )
        )
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    service = runner.service()
    queued = []
    service.dispatch = queued.append
    app.dependency_overrides[deps.get_project_folder_generation_service] = lambda: service
    def override_session():
        with sessions() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
    app.dependency_overrides[deps.get_session] = override_session
    app.dependency_overrides[deps.get_settings] = lambda: settings
    try:
        client = TestClient(app)
        url = "/api/projects/P1/project-folder/generation"
        preview = client.get(url + "/preview")
        assert preview.status_code == 200, preview.text
        payload = preview.json()
        guidance = (
            "Confirmed Matrix plan dates are incomplete or historical Project Schedule dates "
            "have not been migrated. Open Matrix Editor, review the plan dates, and click "
            "Confirm Matrix before generating Project Folder outputs."
        )
        assert payload["workspace_preview"]["status"] == "blocked"
        assert payload["workspace_preview"]["blockers"] == [guidance]
        assert payload["start_blockers"] == [guidance]

        started = client.post(
            url + "/start",
            json={
                "expected_context": payload["expected_context"],
                "request_id": "unconfirmed-project-schedule",
            },
        )
        assert started.status_code == 409
        assert started.json()["detail"] == guidance
        assert client.get(url).json() is None
        assert queued == []
        assert list(destination.iterdir()) == []
        matrix_seed = client.get("/api/projects/P1/matrix-editor/session")
        assert matrix_seed.status_code == 200, matrix_seed.text
        matrix = matrix_seed.json()
        matrix_confirm_payload = {
            "expected_active_confirmed_matrix_id": matrix["active_confirmed_matrix_id"],
            "expected_active_confirmed_revision": matrix["active_confirmed_revision"],
            "source_import_id": matrix["active_source_import_id"],
            "source_snapshot_id": matrix["active_source_snapshot_id"],
            "groups": matrix["editor_draft"]["groups"],
            "rows": matrix["editor_draft"]["rows"],
            "cells": matrix["editor_draft"]["cells"],
            "confirmed_by": "operator",
            "post_test_buffer_days": "0",
            "planned_test_start_date": "2026-09-02",
            "planned_test_complete_date": "2026-09-02",
            "estimated_completion_date": "2026-09-02",
        }
        missing_date = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
            **matrix_confirm_payload,
            "estimated_completion_date": "",
        })
        assert missing_date.status_code == 422, missing_date.text
        still_blocked = client.get(url + "/preview")
        assert guidance in still_blocked.json()["start_blockers"]
        saved = client.put("/api/projects/P1/matrix-editor/session/draft", json=matrix_confirm_payload)
        assert saved.status_code == 200, saved.text
        confirmed_schedule = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
            **matrix_confirm_payload,
            "expected_editor_draft_id": saved.json()["editor_draft_id"],
            "expected_saved_payload_signature": saved.json()["saved_payload_signature"],
        })
        assert confirmed_schedule.status_code == 200, confirmed_schedule.text
        assert confirmed_schedule.json()["publish_status"] == "published"
        after_confirm = client.get(url + "/preview")
        assert after_confirm.status_code == 200, after_confirm.text
        assert guidance not in after_confirm.json()["workspace_preview"]["blockers"]
        assert guidance not in after_confirm.json()["start_blockers"]
    finally:
        app.dependency_overrides.pop(deps.get_session, None)
        app.dependency_overrides.pop(deps.get_settings, None)
        dependency_override = app.dependency_overrides.pop(
            deps.get_project_folder_generation_service, None
        )
        assert dependency_override is not None
        runner.pool.shutdown()
        engine.dispose()


def test_preview_surfaces_missing_project_root_before_required_form_blockers(
    tmp_path,
):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "fixture.sqlite",
    )
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    bootstrap_project_schedule_schema(engine)
    sessions = create_session_factory(engine)
    template = tmp_path / "template"
    missing_destination = tmp_path / "missing-output"
    for name in (
        "E-mail",
        "Submitted Material",
        "Photos",
        "Test results/Final Examination",
    ):
        (template / name).mkdir(parents=True)
    with sessions() as session:
        deps.ProjectRepository(session).create(
            Project(
                project_id="P1",
                project_no="DL-001",
                product_name="Connector",
                requestor="Test",
                status=ProjectStatus.DRAFT,
            )
        )
        deps.LtrRecordRepository(session).create(
            LtrRecord(
                ltr_id="ltr",
                project_id="P1",
                ltr_number="DL-001",
                status=LtrStatus.REGISTERED,
            )
        )
        resources = deps.ExternalResourceRepository(session)
        resources.upsert(
            ExternalResource(
                "root",
                ExternalResourceType.PROJECT_OUTPUT_ROOT,
                missing_destination,
            )
        )
        resources.upsert(
            ExternalResource(
                "template",
                ExternalResourceType.PROJECT_FOLDER_TEMPLATE,
                template,
            )
        )
        deps.get_project_basic_information_service(session).confirm(
            ConfirmProjectBasicInformationCommand(
                project_id="P1",
                values=_complete_basic_information_values(),
                confirmed_by="operator",
            )
        )
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    service = runner.service()
    app.dependency_overrides[deps.get_project_folder_generation_service] = lambda: service
    try:
        response = TestClient(app).get(
            "/api/projects/P1/project-folder/generation/preview"
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        blocker = (
            f"Project default save location does not exist: {missing_destination}"
        )
        assert payload["workspace_preview"]["status"] == "blocked"
        assert payload["workspace_preview"]["blockers"] == [blocker]
        assert payload["start_blockers"] == [blocker]
        assert "Resolve the project folder location and identity first" not in str(
            payload["start_blockers"]
        )
    finally:
        app.dependency_overrides.clear()
        runner.pool.shutdown()
        engine.dispose()


def test_real_preflight_rejects_missing_inputs_before_creating_any_folder(tmp_path, monkeypatch):
    settings = Settings(data_dir=tmp_path / "data", projects_dir=tmp_path / "projects", templates_dir=tmp_path / "templates",
                        database_path=tmp_path / "fixture.sqlite")
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    bootstrap_project_schedule_schema(engine)
    sessions = create_session_factory(engine)
    template, destination = tmp_path / "template", tmp_path / "output"
    destination.mkdir()
    for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
        (template / name).mkdir(parents=True)
    (template / "template.txt").write_text("fixture", encoding="utf-8")
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(project_id="P1", project_no="DL-001", product_name="Connector",
                                                     requestor="Test", status=ProjectStatus.DRAFT))
        deps.LtrRecordRepository(session).create(LtrRecord(ltr_id="ltr", project_id="P1", ltr_number="DL-001", status=LtrStatus.REGISTERED))
        resources = deps.ExternalResourceRepository(session)
        resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, destination))
        resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
        deps.get_project_basic_information_service(session).confirm(
            ConfirmProjectBasicInformationCommand(
                project_id="P1",
                values=_complete_basic_information_values(),
                confirmed_by="operator",
            )
        )
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    service = runner.service()
    queued = []
    service.dispatch = queued.append
    app.dependency_overrides[deps.get_project_folder_generation_service] = lambda: service
    try:
        hashed_paths = []
        monkeypatch.setattr(
            "backend.api.project_folder_generation_composition.tree_hash",
            lambda path: hashed_paths.append(path) or "reviewed-target-hash",
        )
        client = TestClient(app)
        url = "/api/projects/P1/project-folder/generation"
        assert client.get(url).json() is None
        before_context = runner.context("P1")
        preview = client.get(url + "/preview")
        assert preview.status_code == 200, preview.text
        assert hashed_paths == []
        advanced_preview = client.get(url + "/preview?intent=backup_rebuild")
        assert advanced_preview.status_code == 200, advanced_preview.text
        assert hashed_paths == [], "A new rebuild preview must not content-hash business files"
        body = {**preview.json(), "request_id": "request-one"}
        stale = client.post(url + "/start", json={**body, "expected_context": "stale"})
        assert stale.status_code == 409
        started = client.post(url + "/start", json=body)
        assert started.status_code == 409, started.text
        assert "Application Form" in started.json()["detail"]
        assert client.get(url).json() is None
        assert runner.context("P1") == before_context
        assert list(destination.iterdir()) == []
        assert queued == []

        # An existing folder can be linked by the separate identity-only route
        # even while missing generation inputs still prohibit Start.
        planned = preview.json()["workspace_preview"]
        Path(planned["source_book_path"]).mkdir(parents=True)
        Path(planned["official_project_folder_path"]).mkdir()
        link_preview = client.get(url + "/preview")
        assert link_preview.status_code == 200, link_preview.text
        assert link_preview.json()["workspace_preview"]["status"] == "adoptable"
        assert link_preview.json()["start_blockers"]
        linked_start = client.post(url + "/start", json={
            "expected_context": link_preview.json()["expected_context"],
            "request_id": "link-is-not-generation",
        })
        assert linked_start.status_code == 409
        assert client.get(url).json() is None
    finally:
        app.dependency_overrides.clear()
        runner.pool.shutdown()
        engine.dispose()


def test_new_start_rejects_legacy_mutating_strategies():
    app.dependency_overrides[deps.get_project_folder_generation_service] = lambda: object()
    try:
        client = TestClient(app)
        url = "/api/projects/P1/project-folder/generation/start"
        body = {"expected_context": "reviewed", "request_id": "new"}
        assert client.post(url, json={**body, "conflict_strategy": "continue_existing"}).status_code == 422
        assert client.post(
            url, json={**body, "conflict_strategy": "overwrite_rebuild"}
        ).status_code == 422
    finally:
        app.dependency_overrides.clear()
