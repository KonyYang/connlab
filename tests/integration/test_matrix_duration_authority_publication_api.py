"""API publication and reload regressions for typed Matrix duration authority."""

from decimal import Decimal
from pathlib import Path

from backend.api.matrix_editor_session_dtos import MatrixEditorSessionConfirmResponse
from backend.application.source_matrix_import_persistence_service import (
    PersistSourceMatrixImportCommand,
    SourceMatrixImportPersistenceService,
)
from backend.infrastructure.storage.repositories import SourceMatrixImportRepository
from tests.integration.test_confirmed_matrix_authority_api import (
    _client,
    _seed_project,
)
from tests.integration.test_matrix_typed_duration_authority_round_trip_api import (
    _source_payload,
)


def test_first_confirm_and_revision_preserve_duration_authority(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source(session_factory, tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={
                "source_import_id": source_import_id,
                "selected_group_keys": ["g1"],
            },
        )
        assert created.status_code == 201
        draft_id = created.json()["record"]["project_matrix_draft_id"]

        first_confirm = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert first_confirm.status_code == 201
        first_authorities = first_confirm.json()["duration_authorities"]
        assert len(first_authorities) == 1
        assert Decimal(first_authorities[0]["normalized_hours"]) == Decimal("48")
        first_session_response = MatrixEditorSessionConfirmResponse.model_validate(
            {
                "publish_status": "confirmed",
                "message": "Matrix confirmed.",
                "confirmed_snapshot": first_confirm.json(),
            }
        )
        assert (
            first_session_response.confirmed_snapshot.version.confirmed_revision == 1
        )

        revision = client.post("/api/projects/P1/matrix-revisions")
        assert revision.status_code == 201
        revision_payload = revision.json()
        revision_id = revision_payload["record"]["project_matrix_draft_id"]
        revision_reload = client.get(
            f"/api/projects/P1/matrix-drafts/{revision_id}"
        )
        assert revision_reload.status_code == 200
        assert len(revision_reload.json()["duration_authorities"]) == 1
        confirmed_revision = client.post(
            f"/api/projects/P1/matrix-drafts/{revision_id}/confirm-revision",
            json={
                "confirmed_by": "operator",
                "superseded_reason": "Duration authority carry-forward regression",
            },
        )
        assert confirmed_revision.status_code == 201
        assert confirmed_revision.json()["version"]["confirmed_revision"] == 2
        assert Decimal(
            confirmed_revision.json()["duration_authorities"][0]["normalized_hours"]
        ) == Decimal("48")
        revision_session_response = MatrixEditorSessionConfirmResponse.model_validate(
            {
                "publish_status": "confirmed",
                "message": "Matrix revision confirmed.",
                "confirmed_snapshot": confirmed_revision.json(),
            }
        )
        assert (
            revision_session_response.confirmed_snapshot.version.confirmed_revision == 2
        )
        assert (
            "ConfirmedMatrixSnapshotResponse"
            in MatrixEditorSessionConfirmResponse.model_json_schema()["$defs"]
        )
    finally:
        from backend.api.main import app

        app.dependency_overrides.clear()
        engine.dispose()


def _seed_source(session_factory, tmp_path: Path) -> str:
    with session_factory() as session:
        source_import_id = SourceMatrixImportPersistenceService(
            store=SourceMatrixImportRepository(session)
        ).persist_from_draft(
            PersistSourceMatrixImportCommand(
                project_id="P1",
                draft_id="ptpd-duration-publication",
                source_document_path=str(tmp_path / "spec.docx"),
                source_document_name="spec.docx",
                source_format=".docx",
                source_asset_id=None,
                source_case_id=None,
                source_draft_id=None,
                payload=_source_payload(),
                created_at="2026-07-24T08:00:00+00:00",
            )
        )
        session.commit()
    return source_import_id
