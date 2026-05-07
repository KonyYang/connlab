from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.routes_intake import router as intake_router
from backend.api.routes_intake_review import router as intake_review_router
from backend.domain import LtrRecord, LtrStatus
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import LtrRecordRepository
from backend.shared.config import Settings


def test_create_list_and_get_frozen_field_revision_request(tmp_path: Path) -> None:
    settings, engine, session_factory = _test_database(tmp_path)
    test_app = FastAPI(title="Test App")
    test_app.include_router(intake_router)
    test_app.include_router(intake_review_router)
    test_app.dependency_overrides[get_session] = _override_session(session_factory)
    test_app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(test_app)

    try:
        created = _create_and_freeze_case(client, session_factory)

        create_response = client.post(
            f"/api/intake-cases/{created['case_id']}/frozen-field-revision-requests",
            json={
                "reason": "Customer corrected product name.",
                "requested_by": "White",
                "changes": [{"field_key": "product_name", "proposed_value": "Connector X"}],
            },
        )
        assert create_response.status_code == 201
        created_request = create_response.json()
        assert created_request["status"] == "requested"
        assert created_request["intake_case_id"] == created["case_id"]
        assert created_request["project_id"] == created["project_id"]
        assert created_request["ltr_number"] == "DL-2026-05-001"
        assert created_request["changes"][0]["field_key"] == "product_name"
        assert created_request["changes"][0]["current_value"] == "Connector sample"
        assert created_request["changes"][0]["proposed_value"] == "Connector X"

        list_response = client.get(
            f"/api/intake-cases/{created['case_id']}/frozen-field-revision-requests"
        )
        assert list_response.status_code == 200
        listed = list_response.json()
        assert len(listed) == 1
        assert listed[0]["request_id"] == created_request["request_id"]

        project_list_response = client.get(
            f"/api/projects/{created['project_id']}/frozen-field-revision-requests"
        )
        assert project_list_response.status_code == 200
        assert len(project_list_response.json()) == 1

        detail_response = client.get(
            f"/api/frozen-field-revision-requests/{created_request['request_id']}"
        )
        assert detail_response.status_code == 200
        assert detail_response.json()["request_id"] == created_request["request_id"]
    finally:
        test_app.dependency_overrides.clear()
        engine.dispose()


def test_create_frozen_field_revision_request_rejects_non_frozen_case(tmp_path: Path) -> None:
    settings, engine, session_factory = _test_database(tmp_path)
    test_app = FastAPI(title="Test App")
    test_app.include_router(intake_router)
    test_app.include_router(intake_review_router)
    test_app.dependency_overrides[get_session] = _override_session(session_factory)
    test_app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(test_app)

    try:
        create_response = client.post(
            "/api/intake-packages/manual",
            json={"product_name": "Connector sample", "requester": "Test user"},
        )
        assert create_response.status_code == 201
        case_id = create_response.json()["case_id"]

        revision_response = client.post(
            f"/api/intake-cases/{case_id}/frozen-field-revision-requests",
            json={
                "reason": "Need correction",
                "changes": [{"field_key": "product_name", "proposed_value": "Connector X"}],
            },
        )
        assert revision_response.status_code == 400
        assert "not frozen" in revision_response.json()["detail"]
    finally:
        test_app.dependency_overrides.clear()
        engine.dispose()


def _create_and_freeze_case(client: TestClient, session_factory) -> dict[str, str]:
    create_response = client.post(
        "/api/intake-packages/manual",
        json={
            "product_name": "Connector sample",
            "requester": "Test user",
            "email": "test@example.com",
            "business_unit": "Power Solutions",
            "project_no": "PRJ-001",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    update_response = client.patch(
        f"/api/intake-cases/{created['case_id']}/review-fields",
        json={
            "fields": {
                "form_no": "E-3718",
                "revision": "H",
                "product_name": "Connector sample",
                "requester": "Test user",
                "phone": "555-0100",
                "request_date": "2026-05-03",
                "email": "test@example.com",
                "business_unit": "Power Solutions",
                "manufacturing_site": "Nantong",
                "results_format": "Formal Report (Customer)",
                "requested_completion_date": "2026-05-10",
                "test_type": "Customer Specific Testing",
                "sample_status": "Production",
                "project_type": "New Product Development",
                "post_testing_disposition": "Keep in the Lab",
                "requested_testing": "Bend testing",
                "confidential": "No",
                "subcontract": "Yes",
                "send_copies_recipients": "Team",
            },
            "sample_rows": [
                {
                    "product_name": "Connector sample",
                    "part_number": "PN-100",
                    "lot_or_traceability": "LOT-100",
                    "material": "Copper",
                    "plating": "Ag",
                    "housing_material": "PA10T",
                    "quantity": "20 pcs",
                }
            ],
        },
    )
    assert update_response.status_code == 200
    confirm_response = client.post(
        f"/api/intake-cases/{created['case_id']}/confirm",
        json={"operator_confirmed": True},
    )
    assert confirm_response.status_code == 200
    project_id = confirm_response.json()["project_id"]
    with session_factory() as session:
        LtrRecordRepository(session).create(
            LtrRecord(
                ltr_id="ltr-registered-1",
                project_id=project_id,
                ltr_number="DL-2026-05-001",
                status=LtrStatus.REGISTERED,
                registered_on=date(2026, 5, 7),
            )
        )
        session.commit()
    return {"case_id": created["case_id"], "project_id": project_id}


def _test_database(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    return settings, engine, create_session_factory(engine)


def _override_session(session_factory):
    def override_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    return override_session
