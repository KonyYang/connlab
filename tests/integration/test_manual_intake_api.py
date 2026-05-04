from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from docx import Document

from backend.api.dependencies import get_session, get_settings
from backend.api.routes_intake import router as intake_router
from backend.api.routes_intake_review import router as intake_review_router
from backend.api.main import app
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories.intake_package import (
    IntakeCaseRepository,
    IntakeDraftRepository,
    IntakePackageRepository,
)
from backend.shared.config import Settings


def test_direct_word_intake_api_creates_package_and_candidate(tmp_path: Path) -> None:
    """Direct Word upload creates an intake package without an email source."""
    settings, engine, session_factory = _test_database(tmp_path)
    app.dependency_overrides[get_session] = _override_session(session_factory)
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)
    sample_path = tmp_path / "direct_application.docx"
    document = Document()
    document.add_paragraph("Laboratory Test Request")
    document.save(sample_path)

    try:
        with sample_path.open("rb") as handle:
            response = client.post(
                "/api/intake-packages/import-docx",
                files={
                    "file": (
                        sample_path.name,
                        handle,
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                },
            )

        assert response.status_code == 201
        payload = response.json()
        assert payload["source_type"] == "direct_application_form"
        assert payload["source_original_name"] == sample_path.name
        assert payload["asset_count"] == 1
        assert payload["candidate_count"] == 1
        assert "received_at" in payload
        assert payload["received_at"] is None
        assert payload["next_action"] == "review_application_form_candidates"
        assert payload["assets"][0]["original_name"] == sample_path.name
        assert payload["assets"][0]["asset_role"] in {
            "application_form_candidate",
            "selected_application_form",
        }
    finally:
        app.dependency_overrides.clear()


def test_manual_intake_api_creates_review_case(tmp_path: Path) -> None:
    """The API stores no-email manual intake before project creation."""
    settings, engine, session_factory = _test_database(tmp_path)
    app.dependency_overrides[get_session] = _override_session(session_factory)
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    try:
        response = client.post(
            "/api/intake-packages/manual",
                json={
                    "form_no": "E-3718",
                    "revision": "H",
                    "product_name": "Connector sample",
                    "requester": "White",
                    "phone": "555-0100",
                    "request_date": "2026-05-03",
                    "email": "white@example.com",
                    "business_unit": "Power Solutions",
                    "project_no": "PRJ-1",
                    "requested_testing": "Qualification",
                    "sample": {
                        "product_name": "Connector sample",
                        "part_number": "PN-001",
                        "lot_or_traceability": "LOT-001",
                        "material": "Copper",
                        "plating": "Ag",
                        "housing_material": "PA10T",
                        "quantity": 3,
                    },
                },
            )

        assert response.status_code == 201
        payload = response.json()
        assert payload["package_status"] == "ready_for_review"
        assert payload["missing_required_fields"] == []
        assert payload["next_action"] == "review_manual_intake"

        detail_response = client.get(f"/api/intake-packages/{payload['package_id']}")
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["source_type"] == "manual"
        assert detail["source_stored"] is True
        assert detail["case_count"] == 1
        assert detail["candidate_count"] == 1

        review_response = client.get(
            f"/api/intake-packages/{payload['package_id']}/case-review"
        )
        assert review_response.status_code == 200
        review = review_response.json()
        assert review["source_type"] == "manual"
        assert review["cases"][0]["case_id"] == payload["case_id"]
        assert review["cases"][0]["confirm_allowed"] is False
        assert review["cases"][0]["precheck_issues"]
        assert review["cases"][0]["missing_required_fields"]
        assert any(
            field["key"] == "product_name" and field["value"] == "Connector sample"
            for field in review["cases"][0]["fields"]
        )

        rejected_response = client.post(
            f"/api/intake-cases/{payload['case_id']}/confirm",
            json={"operator_confirmed": False},
        )
        assert rejected_response.status_code == 400

        confirm_response = client.post(
            f"/api/intake-cases/{payload['case_id']}/confirm",
            json={"operator_confirmed": True},
        )
        assert confirm_response.status_code == 400
        assert "SECTION 1 precheck blockers" in confirm_response.json()["detail"]

        with session_factory() as session:
            package = IntakePackageRepository(session).get(payload["package_id"])
            case = IntakeCaseRepository(session).get(payload["case_id"])
            draft = IntakeDraftRepository(session).get(payload["draft_id"])
            assert package is not None
            assert package.source_stored_path.is_file()
            assert case is not None
            assert case.confirmed_project_id is None
            assert draft is not None
            assert "Connector sample" in draft.parsed_fields_json
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_manual_intake_api_returns_missing_required_fields(tmp_path: Path) -> None:
    """Manual drafts can be saved while required field blockers remain visible."""
    settings, engine, session_factory = _test_database(tmp_path)
    app.dependency_overrides[get_session] = _override_session(session_factory)
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    try:
        response = client.post(
            "/api/intake-packages/manual",
            json={"product_name": "", "requester": ""},
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["missing_required_fields"] == ["product_name", "requester"]
        assert payload["next_action"] == "complete_required_manual_fields"

        review_response = client.get(
            f"/api/intake-packages/{payload['package_id']}/case-review"
        )
        assert review_response.status_code == 200
        review = review_response.json()
        assert review["cases"][0]["confirm_allowed"] is False
        assert "product_name" in review["cases"][0]["missing_required_fields"]
        assert "requester" in review["cases"][0]["missing_required_fields"]
        assert review["cases"][0]["precheck_issues"]

        update_response = client.patch(
            f"/api/intake-cases/{payload['case_id']}/review-fields",
            json={
                "fields": {
                    "form_no": "E-3718",
                    "revision": "H",
                    "product_name": "Corrected connector",
                    "requester": "White",
                    "phone": "555-0100",
                    "request_date": "2026-05-03",
                    "email": "white@example.com",
                    "business_unit": "Power Solutions",
                    "manufacturing_site": "Nantong",
                    "results_format": "Formal Report (Customer)",
                    "requested_completion_date": "2026-05-10",
                    "test_type": "Customer Specific Testing",
                    "sample_status": "Production",
                    "project_type": "New Product Development",
                    "requested_testing": "Bend testing",
                    "post_testing_disposition": "Keep in the Lab",
                    "confidential": "No",
                    "subcontract": "Yes",
                    "send_copies_recipients": "Neo Xu",
                },
                "sample_rows": [
                    {
                        "product_name": "Corrected connector",
                        "part_number": "PN-082",
                        "lot_or_traceability": "LOT-082",
                        "material": "Copper",
                        "plating": "Ag",
                        "housing_material": "PA10T",
                        "quantity": "4",
                    }
                ],
            },
        )
        assert update_response.status_code == 200
        updated_case = update_response.json()
        assert updated_case["confirm_allowed"] is True
        assert updated_case["missing_required_fields"] == []
        assert updated_case["sample_rows"][0]["part_number"] == "PN-082"

        confirm_after_update_response = client.post(
            f"/api/intake-cases/{payload['case_id']}/confirm",
            json={"operator_confirmed": True},
        )
        assert confirm_after_update_response.status_code == 200
        assert confirm_after_update_response.json()["project_id"]
        assert confirm_after_update_response.json()["sample_count"] == 1

        with session_factory() as session:
            draft = IntakeDraftRepository(session).get(payload["draft_id"])
            assert draft is not None
            assert "Corrected connector" in (draft.manual_overrides_json or "")
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _test_database(tmp_path: Path):
    """Create an isolated test database."""
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    return settings, engine, create_session_factory(engine)


def test_review_fields_persists_requested_testing_rows(tmp_path: Path) -> None:
    """PATCH /review-fields with requested_testing_rows persists and returns rows."""
    settings, engine, session_factory = _test_database(tmp_path)

    from fastapi.testclient import TestClient

    # Use IntakeDraftRepository from top-level imports
    # No additional imports needed

    # Create a fresh app instance for this test
    test_app = FastAPI(title="Test App")
    test_app.include_router(intake_router)
    test_app.include_router(intake_review_router)
    test_app.dependency_overrides[get_session] = _override_session(session_factory)

    client = TestClient(test_app)

    try:
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
        payload = create_response.json()

        # First update: complete all required fields
        update_response = client.patch(
            f"/api/intake-cases/{payload['case_id']}/review-fields",
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
                    "confidential": "No",
                    "subcontract": "Yes",
                    "send_copies_recipients": "Team",
                },
            },
        )
        assert update_response.status_code == 200

        # Second update: add requested_testing_rows
        rows_update_response = client.patch(
            f"/api/intake-cases/{payload['case_id']}/review-fields",
            json={
                "fields": {},
                "requested_testing_rows": [
                    {
                        "test_to_be_performed": "Qualification test",
                        "applicable_specification": "GS-12-2652-22",
                    },
                    {
                        "test_to_be_performed": "Environmental test",
                        "applicable_specification": "QG-03-016E_Rev2",
                    },
                ],
            },
        )
        assert rows_update_response.status_code == 200
        updated_case = rows_update_response.json()

        # Verify response contains rows
        assert "requested_testing_rows" in updated_case
        assert len(updated_case["requested_testing_rows"]) == 2
        assert updated_case["requested_testing_rows"][0]["test_to_be_performed"] == "Qualification test"
        assert updated_case["requested_testing_rows"][0]["applicable_specification"] == "GS-12-2652-22"

        # Verify compatibility field is synced
        fields_dict = {f["key"]: f["value"] for f in updated_case["fields"]}
        assert "requested_testing" in fields_dict
        assert "Qualification test" in fields_dict["requested_testing"]
        assert "Environmental test" in fields_dict["requested_testing"]

        # Verify draft persistence
        with session_factory() as session:
            draft = IntakeDraftRepository(session).get(payload["draft_id"])
            assert draft is not None
            assert draft.manual_overrides_json is not None
            import json

            overrides = json.loads(draft.manual_overrides_json)
            assert "requested_testing_rows" in overrides
            assert len(overrides["requested_testing_rows"]) == 2
            assert overrides["requested_testing_rows"][0]["test_to_be_performed"] == "Qualification test"
            # Compatibility field should also be in overrides
            assert "requested_testing" in overrides
    finally:
        test_app.dependency_overrides.clear()
        engine.dispose()


def _override_session(session_factory):
    """Return a FastAPI session dependency override."""

    def override_session() -> Generator[Session, None, None]:
        """Yield one test database session."""
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    return override_session
