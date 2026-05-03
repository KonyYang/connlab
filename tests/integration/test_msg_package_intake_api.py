from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from docx import Document
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories.intake_package import (
    IntakeAssetRepository,
    IntakeCaseRepository,
    IntakeDraftRepository,
    IntakePackageRepository,
)
from backend.shared.config import Settings
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
)


def test_msg_package_import_api_persists_package_and_assets(tmp_path: Path) -> None:
    """The API imports one manual `.msg` package through application service boundaries."""
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
        """Yield one test database session."""
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    try:
        response = client.post(
            "/api/intake-packages/import-msg",
            files={
                "file": (
                    "request.msg",
                    _msg_bytes(
                        [
                            "Subject: Connector qualification request",
                            "From: Jane Engineer <jane@example.com>",
                            "Attachment: E-3718 Application Form.docx; content=docx bytes",
                            "Attachment: drawing.pdf; content=pdf bytes",
                        ]
                    ),
                    "application/vnd.ms-outlook",
                )
            },
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["source_type"] == "outlook_msg"
        assert payload["package_status"] == "ready_for_review"
        assert payload["subject"] == "Connector qualification request"
        assert payload["sender_email"] == "jane@example.com"
        assert payload["asset_count"] == 3
        assert payload["candidate_count"] == 1
        assert payload["next_action"] == "review_application_form_candidates"

        detail_response = client.get(f"/api/intake-packages/{payload['package_id']}")
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["package_id"] == payload["package_id"]
        assert detail["source_stored"] is True
        assert detail["asset_count"] == 3
        assert detail["candidate_count"] == 1
        assert detail["case_count"] == 0
        assert detail["next_action"] == "create_review_cases"
        assert [asset["original_name"] for asset in detail["candidate_assets"]] == [
            "E-3718 Application Form.docx"
        ]

        with session_factory() as session:
            package = IntakePackageRepository(session).get(payload["package_id"])
            assets = IntakeAssetRepository(session).list_by_package(payload["package_id"])
            assert package is not None
            assert package.source_stored_path.is_file()
            assert len(assets) == 3
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_intake_package_detail_api_returns_404_for_missing_package(
    tmp_path: Path,
) -> None:
    """The package detail endpoint reports missing package ids clearly."""
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
        """Yield one test database session."""
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    try:
        response = client.get("/api/intake-packages/missing")

        assert response.status_code == 404
        assert "Intake package not found" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_select_form_api_binds_selected_docx_to_precheck_case(tmp_path: Path) -> None:
    """Selecting one Word asset creates the case opened by Precheck with parsed fields."""
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
        """Yield one test database session."""
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    try:
        docx_path = _create_application_docx(tmp_path / "application.docx")
        with session_factory() as session:
            package_repo = IntakePackageRepository(session)
            asset_repo = IntakeAssetRepository(session)
            package_repo.create(
                IntakePackage(
                    package_id="pkg-select",
                    source_type=IntakePackageSourceType.OUTLOOK_MSG,
                    status=IntakePackageStatus.READY_FOR_REVIEW,
                    source_original_name="request.msg",
                    source_stored_path=tmp_path / "request.msg",
                )
            )
            asset_repo.create(
                IntakeAsset(
                    asset_id="asset-selected",
                    package_id="pkg-select",
                    original_name=docx_path.name,
                    stored_path=docx_path,
                    extension=".docx",
                    mime_type="application/octet-stream",
                    size_bytes=docx_path.stat().st_size,
                    sha256="a" * 64,
                    asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
                    candidate_score=90,
                )
            )
            asset_repo.create(
                IntakeAsset(
                    asset_id="asset-other",
                    package_id="pkg-select",
                    original_name="other.docx",
                    stored_path=docx_path,
                    extension=".docx",
                    mime_type="application/octet-stream",
                    size_bytes=docx_path.stat().st_size,
                    sha256="b" * 64,
                    asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
                    candidate_score=80,
                )
            )
            session.commit()

        response = client.post(
            "/api/intake-packages/pkg-select/select-form",
            json={"asset_id": "asset-selected"},
        )

        assert response.status_code == 200
        selected = response.json()
        assert selected["selected_form_asset_id"] == "asset-selected"
        assert selected["case_id"]

        review_response = client.get("/api/intake-packages/pkg-select/case-review")
        assert review_response.status_code == 200
        cases = review_response.json()["cases"]
        assert len(cases) == 1
        assert cases[0]["case_id"] == selected["case_id"]
        assert cases[0]["selected_form_asset_id"] == "asset-selected"
        field_values = {field["key"]: field["value"] for field in cases[0]["fields"]}
        assert field_values["requester"] == "Alice Requestor"
        assert field_values["product_name"] == "Connector A"
        assert field_values["form_no"] == "E-3718"
        assert cases[0]["sample_rows"][0]["product_name"] == "Connector A"
        assert cases[0]["sample_rows"][0]["part_number"] == "PN-073"

        with session_factory() as session:
            assert (
                IntakeCaseRepository(session).list_by_package("pkg-select")[0].selected_form_asset_id
                == "asset-selected"
            )
            draft = IntakeDraftRepository(session).get_by_case(selected["case_id"])
            assert draft is not None
            assert "Alice Requestor" in draft.parsed_fields_json
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_intake_asset_preview_api_returns_docx_preview_without_paths(
    tmp_path: Path,
) -> None:
    """The preview endpoint returns structured DOCX content without local paths."""
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
        """Yield one test database session."""
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    try:
        docx_path = _create_application_docx(tmp_path / "preview-application.docx")
        pdf_path = tmp_path / "drawing.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        image_path = tmp_path / "photo.png"
        image_path.write_bytes(b"\x89PNG\r\n\x1a\n")
        with session_factory() as session:
            package_repo = IntakePackageRepository(session)
            asset_repo = IntakeAssetRepository(session)
            package_repo.create(
                IntakePackage(
                    package_id="pkg-preview",
                    source_type=IntakePackageSourceType.OUTLOOK_MSG,
                    status=IntakePackageStatus.READY_FOR_REVIEW,
                    source_original_name="request.msg",
                    source_stored_path=tmp_path / "request.msg",
                )
            )
            asset_repo.create(
                IntakeAsset(
                    asset_id="asset-docx-preview",
                    package_id="pkg-preview",
                    original_name=docx_path.name,
                    stored_path=docx_path,
                    extension=".docx",
                    mime_type="application/octet-stream",
                    size_bytes=docx_path.stat().st_size,
                    sha256="c" * 64,
                    asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
                    candidate_score=90,
                )
            )
            asset_repo.create(
                IntakeAsset(
                    asset_id="asset-pdf-preview",
                    package_id="pkg-preview",
                    original_name=pdf_path.name,
                    stored_path=pdf_path,
                    extension=".pdf",
                    mime_type="application/pdf",
                    size_bytes=pdf_path.stat().st_size,
                    sha256="d" * 64,
                    asset_role=IntakeAssetRole.SUPPORTING_ATTACHMENT,
                )
            )
            asset_repo.create(
                IntakeAsset(
                    asset_id="asset-image-preview",
                    package_id="pkg-preview",
                    original_name=image_path.name,
                    stored_path=image_path,
                    extension=".png",
                    mime_type="image/png",
                    size_bytes=image_path.stat().st_size,
                    sha256="e" * 64,
                    asset_role=IntakeAssetRole.SUPPORTING_ATTACHMENT,
                )
            )
            session.commit()

        response = client.get("/api/intake-assets/asset-docx-preview/preview")

        assert response.status_code == 200
        payload = response.json()
        assert payload["kind"] == "docx_application_form"
        assert payload["metadata"]["original_name"] == "preview-application.docx"
        assert "stored_path" not in str(payload)
        fields = {field["label"]: field["value"] for field in payload["fields"]}
        assert fields["Requested By"] == "Alice Requestor"
        assert any(table["title"] == "Test Sample Information" for table in payload["tables"])

        unsupported = client.get("/api/intake-assets/asset-pdf-preview/preview")
        assert unsupported.status_code == 200
        assert unsupported.json()["kind"] == "metadata_only"
        assert unsupported.json()["fields"][1]["value"] == "PDF"

        image = client.get("/api/intake-assets/asset-image-preview/preview")
        assert image.status_code == 200
        image_payload = image.json()
        assert image_payload["kind"] == "image"
        assert image_payload["image_data_url"].startswith("data:image/png;base64,")

        missing = client.get("/api/intake-assets/missing/preview")
        assert missing.status_code == 404
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_msg_package_import_api_rejects_non_msg_upload(tmp_path: Path) -> None:
    """The API rejects non-msg files before intake records are created."""
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
        """Yield one test database session."""
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    try:
        response = client.post(
            "/api/intake-packages/import-msg",
            files={
                "file": (
                    "request.docx",
                    b"word",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

        assert response.status_code == 400
        assert "accepts only .msg files" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _msg_bytes(lines: list[str]) -> bytes:
    """Build a fixture-style `.msg` byte stream."""
    return "\n".join(lines).encode("utf-8")


def _create_application_docx(path: Path) -> Path:
    """Create a small application-form document for selected-form API tests."""
    document = Document()
    table = document.add_table(rows=3, cols=2)
    for row_index, (label, value) in enumerate(
        [
            ("Form No.", "E-3718"),
            ("Requested By", "Alice Requestor"),
            ("Email", "alice@example.com"),
        ]
    ):
        table.cell(row_index, 0).text = label
        table.cell(row_index, 1).text = value
    sample_table = document.add_table(rows=2, cols=4)
    for index, header in enumerate(["Product Name", "Part Number", "Revision", "Quantity"]):
        sample_table.cell(0, index).text = header
    for index, value in enumerate(["Connector A", "PN-073", "A", "12"]):
        sample_table.cell(1, index).text = value
    document.save(path)
    return path
