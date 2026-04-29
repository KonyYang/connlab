from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.api.main import app
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
)
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


def test_exception_workflow_api_marks_no_form_package_for_follow_up(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_package(session_factory, assets=[_asset("spec", IntakeAssetRole.SPECIFICATION)])

        response = client.post("/api/intake-packages/pkg-1/exceptions/review")

        assert response.status_code == 200
        payload = response.json()
        assert payload["package_status"] == "needs_application_form_selection"
        assert payload["issues"][0]["kind"] == "no_application_form"
        assert payload["issues"][0]["blocking"] is True
        assert payload["case_ids"] == []
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_exception_workflow_api_creates_cases_for_multiple_forms(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_package(
            session_factory,
            assets=[
                _asset("form-a", IntakeAssetRole.APPLICATION_FORM_CANDIDATE),
                _asset("form-b", IntakeAssetRole.APPLICATION_FORM_CANDIDATE),
            ],
        )

        response = client.post("/api/intake-packages/pkg-1/exceptions/review")

        assert response.status_code == 200
        payload = response.json()
        assert [issue["kind"] for issue in payload["issues"]] == [
            "multiple_application_forms",
            "multiple_application_forms",
        ]
        assert len(payload["case_ids"]) == 2
        assert len(payload["draft_ids"]) == 2
        with session_factory() as session:
            assert len(IntakeCaseRepository(session).list_by_package("pkg-1")) == 2
            assert all(
                IntakeDraftRepository(session).get_by_case(case_id) is not None
                for case_id in payload["case_ids"]
            )
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path: Path):
    """Create an isolated API client."""
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
        """Yield a test session."""
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    return TestClient(app), engine, session_factory


def _seed_package(session_factory, assets: list[IntakeAsset]) -> None:
    """Persist one package and assets."""
    with session_factory() as session:
        IntakePackageRepository(session).create(
            IntakePackage(
                package_id="pkg-1",
                source_type=IntakePackageSourceType.OUTLOOK_MSG,
                status=IntakePackageStatus.READY_FOR_REVIEW,
                source_original_name="request.msg",
                source_stored_path=Path("data/intake/pkg-1/source/request.msg"),
            )
        )
        repository = IntakeAssetRepository(session)
        for asset in assets:
            repository.create(asset)
        session.commit()


def _asset(asset_id: str, role: IntakeAssetRole) -> IntakeAsset:
    """Create an intake asset."""
    return IntakeAsset(
        asset_id=asset_id,
        package_id="pkg-1",
        original_name=f"{asset_id}.docx",
        stored_path=Path(f"data/intake/pkg-1/attachments/{asset_id}.docx"),
        extension=".docx",
        mime_type="application/octet-stream",
        size_bytes=100,
        sha256=asset_id * 16,
        asset_role=role,
    )
