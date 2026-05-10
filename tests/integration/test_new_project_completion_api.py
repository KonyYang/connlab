from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import (
    get_ltr_authority_service,
    get_session,
    get_settings,
)
from backend.api.main import app
from backend.application.ltr_authority import LtrAuthorityCommitResult
from backend.application.ltr_workbook_write_commit_service import (
    LtrWorkbookWriteCommitError,
)
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakeCase,
    IntakeCaseStatus,
    IntakeDraft,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
    LtrRecord,
    LtrStatus,
    ProjectStatus,
    Project,
)
from backend.modules.ltr import next_monthly_dl_number, parse_ltr_number
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    LtrRecordRepository,
    ProjectFolderRecordRepository,
    ProjectRepository,
)
from backend.infrastructure.storage.repositories.intake_package import (
    IntakeAssetRepository,
    IntakeCaseRepository,
    IntakeDraftRepository,
    IntakePackageRepository,
)
from backend.shared.config import Settings


def test_complete_new_project_auto_ltr_applies_ltr_without_folder(
    tmp_path: Path,
) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=_create_template(tmp_path / "{DL_NUMBER}_{PROJECT_NO}_{PRODUCT_NAME}"),
        database_path=tmp_path / "connlab.sqlite3",
    )
    settings.ensure_directories()
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
    shared_state = _FakeWorkbookNumberState()

    def override_ltr_commit_service(
        session: Session = Depends(get_session),
    ) -> _FakeWorkbookCommitService:
        return _FakeWorkbookCommitService(session, shared_state)

    app.dependency_overrides[get_ltr_authority_service] = (
        override_ltr_commit_service
    )
    client = TestClient(app)

    try:
        case_id = _seed_intake_case(session_factory, tmp_path)

        response = client.post(
            f"/api/intake-cases/{case_id}/complete-new-project",
            json=_completion_payload("auto"),
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["project_status"] == "ltr_registered"
        assert payload["ltr_number"] == "DL-2026-05-001"
        assert payload["workbook_sheet_name"] == "2026"
        assert payload["workbook_row_number"] == 3
        assert "project_folder_path" not in payload
        assert "folder_id" not in payload

        project_id = payload["project_id"]
        with session_factory() as session:
            project = ProjectRepository(session).get(project_id)
            ltrs = LtrRecordRepository(session).list_by_project(project_id)
            folders = ProjectFolderRecordRepository(session).list_by_project(project_id)
            assert project is not None
            assert project.status.value == "ltr_registered"
            assert [ltr.ltr_number for ltr in ltrs] == ["DL-2026-05-001"]
            assert folders == []
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_complete_new_project_rejects_duplicate_specified_ltr(tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=_create_template(tmp_path / "{DL_NUMBER}_{PRODUCT_NAME}"),
        database_path=tmp_path / "connlab.sqlite3",
    )
    settings.ensure_directories()
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
    shared_state = _FakeWorkbookNumberState()

    def override_ltr_commit_service(
        session: Session = Depends(get_session),
    ) -> _FakeWorkbookCommitService:
        return _FakeWorkbookCommitService(session, shared_state)

    app.dependency_overrides[get_ltr_authority_service] = (
        override_ltr_commit_service
    )
    client = TestClient(app)

    try:
        first_case_id = _seed_intake_case(session_factory, tmp_path, suffix="A")
        second_case_id = _seed_intake_case(session_factory, tmp_path, suffix="B")
        first = client.post(
            f"/api/intake-cases/{first_case_id}/complete-new-project",
            json={
                **_completion_payload("specified"),
                "specified_ltr_number": "DL-2026-05-007",
            },
        )
        duplicate = client.post(
            f"/api/intake-cases/{second_case_id}/complete-new-project",
            json={
                **_completion_payload("specified"),
                "specified_ltr_number": "DL-2026-05-007",
            },
        )

        assert first.status_code == 201
        assert duplicate.status_code == 400
        assert "already exists" in duplicate.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_complete_new_project_is_idempotent_for_completed_case(tmp_path: Path) -> None:
    """Repeating completion for one case returns the same project instead of duplicating."""
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=_create_template(tmp_path / "{DL_NUMBER}_{PRODUCT_NAME}"),
        database_path=tmp_path / "connlab.sqlite3",
    )
    settings.ensure_directories()
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
    shared_state = _FakeWorkbookNumberState()

    def override_ltr_commit_service(
        session: Session = Depends(get_session),
    ) -> _FakeWorkbookCommitService:
        return _FakeWorkbookCommitService(session, shared_state)

    app.dependency_overrides[get_ltr_authority_service] = (
        override_ltr_commit_service
    )
    client = TestClient(app)

    try:
        case_id = _seed_intake_case(session_factory, tmp_path, suffix="IDEM")

        first = client.post(
            f"/api/intake-cases/{case_id}/complete-new-project",
            json=_completion_payload("auto"),
        )
        second = client.post(
            f"/api/intake-cases/{case_id}/complete-new-project",
            json=_completion_payload("auto"),
        )

        assert first.status_code == 201
        assert second.status_code == 201
        first_payload = first.json()
        second_payload = second.json()
        assert second_payload["project_id"] == first_payload["project_id"]
        assert second_payload["ltr_number"] == first_payload["ltr_number"]
        assert second_payload["project_status"] == "ltr_registered"

        with session_factory() as session:
            projects = ProjectRepository(session).list()
            ltrs = LtrRecordRepository(session).list_by_project(first_payload["project_id"])
            folders = ProjectFolderRecordRepository(session).list_by_project(
                first_payload["project_id"]
            )
            assert len(projects) == 1
            assert [ltr.ltr_number for ltr in ltrs] == ["DL-2026-05-001"]
            assert folders == []
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_complete_new_project_returns_existing_external_ltr_without_folder(
    tmp_path: Path,
) -> None:
    """A prior workbook-backed LTR commit is returned without folder generation."""
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=_create_template(tmp_path / "{DL_NUMBER}_{PRODUCT_NAME}"),
        database_path=tmp_path / "connlab.sqlite3",
    )
    settings.ensure_directories()
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
    shared_state = _FakeWorkbookNumberState()

    def override_ltr_commit_service(
        session: Session = Depends(get_session),
    ) -> _FakeWorkbookCommitService:
        return _FakeWorkbookCommitService(session, shared_state)

    app.dependency_overrides[get_ltr_authority_service] = (
        override_ltr_commit_service
    )
    client = TestClient(app)

    try:
        case_id = _seed_intake_case(session_factory, tmp_path, suffix="EXT")
        confirmed = client.post(
            f"/api/intake-cases/{case_id}/confirm",
            json={"operator_confirmed": True},
        )
        assert confirmed.status_code == 200
        project_id = confirmed.json()["project_id"]
        with session_factory() as session:
            projects = ProjectRepository(session)
            project = projects.get(project_id)
            assert project is not None
            projects.update(project.with_status(ProjectStatus.LTR_REGISTERED))
            LtrRecordRepository(session).create(
                LtrRecord(
                    ltr_id="LTR-EXT",
                    project_id=project_id,
                    ltr_number="DL-2026-05-009",
                    status=LtrStatus.REGISTERED,
                    requested_by="Alice",
                    requested_date=None,
                    notes="external workbook commit",
                )
            )
            session.commit()

        response = client.post(
            f"/api/intake-cases/{case_id}/complete-new-project",
            json={
                **_completion_payload("specified"),
                "specified_ltr_number": "DL-2026-05-009",
            },
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["ltr_number"] == "DL-2026-05-009"
        assert payload["project_status"] == "ltr_registered"
        assert "project_folder_path" not in payload
        with session_factory() as session:
            assert ProjectFolderRecordRepository(session).list_by_project(project_id) == []
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_complete_new_project_does_not_register_local_ltr_when_workbook_commit_fails(
    tmp_path: Path,
) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=_create_template(tmp_path / "{DL_NUMBER}_{PROJECT_NO}_{PRODUCT_NAME}"),
        database_path=tmp_path / "connlab.sqlite3",
    )
    settings.ensure_directories()
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
    app.dependency_overrides[get_ltr_authority_service] = (
        lambda: _FailingWorkbookCommitService()
    )
    client = TestClient(app)

    try:
        case_id = _seed_intake_case(session_factory, tmp_path, suffix="FAIL")
        response = client.post(
            f"/api/intake-cases/{case_id}/complete-new-project",
            json=_completion_payload("auto"),
        )
        assert response.status_code == 400
        assert "workbook locked" in response.json()["detail"]
        with session_factory() as session:
            intake_case = IntakeCaseRepository(session).get(case_id)
            assert intake_case is not None
            assert intake_case.confirmed_project_id is None
            assert ProjectRepository(session).list() == []
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_complete_new_project_returns_409_when_local_ltr_unique_conflicts(
    tmp_path: Path,
) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=_create_template(tmp_path / "{DL_NUMBER}_{PROJECT_NO}_{PRODUCT_NAME}"),
        database_path=tmp_path / "connlab.sqlite3",
    )
    settings.ensure_directories()
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
    app.dependency_overrides[get_ltr_authority_service] = (
        lambda session=Depends(get_session): _DuplicateLtrNumberCommitService(session)
    )
    client = TestClient(app)

    try:
        _seed_intake_case(session_factory, tmp_path, suffix="BASE")
        conflict_case_id = _seed_intake_case(session_factory, tmp_path, suffix="CONFLICT")

        with session_factory() as session:
            project_id = uuid4().hex
            ProjectRepository(session).create(
                Project(
                    project_id=project_id,
                    project_no="BASELINE",
                    product_name="Baseline",
                    requestor="Alice",
                    status=ProjectStatus.LTR_REGISTERED,
                    business_unit="Power Solutions",
                )
            )
            LtrRecordRepository(session).create(
                LtrRecord(
                    ltr_id="LTR-BASE-001",
                    project_id=project_id,
                    ltr_number="DL-2026-05-777",
                    status=LtrStatus.REGISTERED,
                    requested_by="Alice",
                    requested_date=None,
                    notes="baseline",
                )
            )
            session.commit()

        response = client.post(
            f"/api/intake-cases/{conflict_case_id}/complete-new-project",
            json=_completion_payload("auto"),
        )
        assert response.status_code == 409
        assert "already exists in local records" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _seed_intake_case(session_factory, tmp_path: Path, suffix: str = "") -> str:
    package_id = f"PKG{suffix or '1'}"
    asset_id = f"ASSET{suffix or '1'}"
    case_id = f"CASE{suffix or '1'}"
    draft_id = f"DRAFT{suffix or '1'}"
    source_path = tmp_path / f"source{suffix or '1'}.msg"
    form_path = tmp_path / f"application{suffix or '1'}.docx"
    source_path.write_text("source", encoding="utf-8")
    form_path.write_text("application", encoding="utf-8")
    with session_factory() as session:
        IntakePackageRepository(session).create(
            IntakePackage(
                package_id=package_id,
                source_type=IntakePackageSourceType.DIRECT_APPLICATION_FORM,
                status=IntakePackageStatus.READY_FOR_REVIEW,
                source_original_name=source_path.name,
                source_stored_path=source_path,
            )
        )
        IntakeAssetRepository(session).create(
            IntakeAsset(
                asset_id=asset_id,
                package_id=package_id,
                original_name=form_path.name,
                stored_path=form_path,
                extension=".docx",
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                size_bytes=form_path.stat().st_size,
                sha256="hash",
                asset_role=IntakeAssetRole.SELECTED_APPLICATION_FORM,
            )
        )
        IntakeCaseRepository(session).create(
            IntakeCase(
                case_id=case_id,
                package_id=package_id,
                selected_form_asset_id=asset_id,
                status=IntakeCaseStatus.NEEDS_REVIEW,
            )
        )
        IntakeDraftRepository(session).create(
            IntakeDraft(
                draft_id=draft_id,
                case_id=case_id,
                parsed_fields_json=json.dumps(_draft_fields(suffix), ensure_ascii=True),
            )
        )
        session.commit()
    return case_id


def _draft_fields(suffix: str) -> dict[str, object]:
    return {
        "form_no": "E-3718",
        "revision": "H",
        "product_name": f"Connector{suffix}",
        "requester": "Alice",
        "phone": "555-0101",
        "request_date": "2026-05-06",
        "email": "alice@example.test",
        "business_unit": "Power Solutions",
        "manufacturing_site": "Nantong",
        "project_no": f"PRJ-{suffix or '001'}",
        "results_format": "Formal Report",
        "requested_completion_date": "2026-06-01",
        "test_type": "Qualification",
        "sample_status": "Production",
        "project_type": "New Product Development",
        "requested_testing": "Qualification test per GS-12-2113 specification",
        "post_testing_disposition": "Keep in the Lab",
        "confidential": "No",
        "subcontract": "No",
        "send_copies_recipients": "Alice",
        "additional_information": "PO pending",
        "lab": "Nantong Lab",
        "assigned_personnel": "Bob",
        "samples": [
            {
                "product_name": f"Connector{suffix}",
                "part_number": "PN-001",
                "lot_or_traceability": "LOT-1",
                "material": "Copper",
                "plating": "Ag",
                "housing_material": "PA10T",
                "quantity": "20",
            }
        ],
    }


def _completion_payload(ltr_mode: str) -> dict[str, object]:
    return {
        "ltr_mode": ltr_mode,
        "operator_confirmed": True,
        "plan_date": "2026-05-06",
        "test_item": "Qualification bend testing",
        "sample_description": "CoolPower connector samples",
        "location": "AIPG Guangzhou",
        "test_type_in_sheet": "Qualification",
        "project_leader": "Alice",
    }


def _create_template(template: Path) -> Path:
    (template / "request").mkdir(parents=True)
    (template / "request" / "form.txt").write_text("template", encoding="utf-8")
    return template


class _FakeWorkbookNumberState:
    def __init__(self) -> None:
        self.numbers = ["DL-2026-05-000"]


class _FakeWorkbookCommitService:
    def __init__(self, session: Session, state: _FakeWorkbookNumberState) -> None:
        self._session = session
        self._state = state

    def commit_project(self, project_id: str, command):
        if not command.operator_confirmed:
            raise LtrWorkbookWriteCommitError("Operator confirmation is required.")

        plan = command.plan_date
        raw = (command.number_input or "").strip()
        if raw:
            try:
                number = parse_ltr_number(raw).normalized
            except Exception:
                number = raw.upper()
            if number in self._state.numbers:
                raise LtrWorkbookWriteCommitError(
                    f"LTR number already exists in the workbook: {number}"
                )
        else:
            number = next_monthly_dl_number(
                year=plan.year,
                month=plan.month,
                existing_numbers=self._state.numbers,
            )
        self._state.numbers.append(number)
        row_number = len(self._state.numbers) + 1
        ltr = LtrRecord(
            ltr_id=f"LTR-{project_id}",
            project_id=project_id,
            ltr_number=number,
            status=LtrStatus.REGISTERED,
            requested_by=command.requested_by,
            requested_date=command.requested_date,
            notes=command.operator_note,
        )
        projects = ProjectRepository(self._session)
        ltrs = LtrRecordRepository(self._session)
        project = projects.get(project_id)
        assert project is not None
        ltrs.create(ltr)
        projects.update(project.with_status(ProjectStatus.LTR_REGISTERED))
        return LtrAuthorityCommitResult(
            ltr=ltr,
            workbook_path="D:/simulated/LTR_number.xlsx",
            workbook_sheet_name=f"{plan.year:04d}",
            workbook_row_number=row_number,
            workbook_backup_path="D:/simulated/backups/LTR_number.xlsx",
        )


class _FailingWorkbookCommitService:
    def commit_project(self, project_id: str, command):
        raise LtrWorkbookWriteCommitError("LTR workbook locked by another operator.")


class _DuplicateLtrNumberCommitService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def commit_project(self, project_id: str, command):
        ltr = LtrRecord(
            ltr_id=f"LTR-{project_id}",
            project_id=project_id,
            ltr_number="DL-2026-05-777",
            status=LtrStatus.REGISTERED,
            requested_by=command.requested_by,
            requested_date=command.requested_date,
            notes=command.operator_note,
        )
        projects = ProjectRepository(self._session)
        ltrs = LtrRecordRepository(self._session)
        project = projects.get(project_id)
        assert project is not None
        ltrs.create(ltr)
        projects.update(project.with_status(ProjectStatus.LTR_REGISTERED))
        return LtrAuthorityCommitResult(
            ltr=ltr,
            workbook_path="D:/simulated/LTR_number.xlsx",
            workbook_sheet_name=f"{command.plan_date.year:04d}",
            workbook_row_number=9,
            workbook_backup_path="D:/simulated/backups/LTR_number.xlsx",
        )
