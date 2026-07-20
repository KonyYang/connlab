from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend.api.dependencies import get_matrix_method_version_sync_service
from backend.api.main import app
from backend.application.external_excel_read_service import (
    StandardRecordReadResult,
    StandardRecordRow,
)
from backend.application.matrix_editor_session_service import (
    build_project_matrix_draft_payload_signature,
)
from backend.application.matrix_method_version_sync_service import (
    MatrixMethodVersionSyncService,
)
from backend.domain import ExternalResource, ExternalResourceType
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.models_project_matrix_draft import (
    ProjectMatrixDraftRecordModel,
    ProjectMatrixDraftRowModel,
)
from backend.infrastructure.storage.repositories.project_matrix_draft import (
    ProjectMatrixDraftRepository,
)
from backend.shared.config import Settings


def test_preview_apply_and_stale_conflict_use_typed_api(tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path,
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "db.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    factory = create_session_factory(engine)
    with factory() as session:
        session.add(
            ProjectMatrixDraftRecordModel(
                project_matrix_draft_id="D1",
                project_id="P1",
                source_import_id=None,
                source_snapshot_id="S1",
                base_confirmed_matrix_id="CM1",
                status="draft",
                created_at="old",
                updated_at="old",
            )
        )
        session.add(
            ProjectMatrixDraftRowModel(
                draft_row_id="R1",
                project_matrix_draft_id="D1",
                source_row_snapshot_id=None,
                row_order=1,
                test_item="Contact resistance",
                method="EIA-364-04A",
                is_sample_row=False,
            )
        )
        session.commit()
        repository = ProjectMatrixDraftRepository(session)
        signature = build_project_matrix_draft_payload_signature(repository.get("D1"))
        service = MatrixMethodVersionSyncService(
            draft_store=repository,
            confirmed_store=_Confirmed(),
            resource_store=_Resources(),
            catalog_reader=_Catalog(),
            now=lambda: "2026-07-20T12:00:00+00:00",
        )
        app.dependency_overrides[get_matrix_method_version_sync_service] = lambda: service
        client = TestClient(app)

        preview = client.post(
            "/api/projects/P1/matrix-method-version-sync/preview",
            json={
                "project_matrix_draft_id": "D1",
                "expected_saved_payload_signature": signature,
            },
        )
        assert preview.status_code == 200
        assert repository.get("D1").rows[0].method == "EIA-364-04A"

        invalid = client.post(
            "/api/projects/P1/matrix-method-version-sync/apply",
            json={
                "project_matrix_draft_id": "D1",
                "expected_saved_payload_signature": signature,
                "preview_fingerprint": preview.json()["preview_fingerprint"],
                "selected_draft_row_ids": [],
                "applied_by": "operator",
            },
        )
        missing = client.post(
            "/api/projects/P1/matrix-method-version-sync/preview",
            json={
                "project_matrix_draft_id": "missing",
                "expected_saved_payload_signature": signature,
            },
        )
        assert invalid.status_code == 400
        assert missing.status_code == 404
        assert repository.get("D1").rows[0].method == "EIA-364-04A"

        applied = client.post(
            "/api/projects/P1/matrix-method-version-sync/apply",
            json={
                "project_matrix_draft_id": "D1",
                "expected_saved_payload_signature": signature,
                "preview_fingerprint": preview.json()["preview_fingerprint"],
                "selected_draft_row_ids": ["R1"],
                "applied_by": "operator",
            },
        )
        assert applied.status_code == 200
        assert applied.json()["applied_row_ids"] == ["R1"]
        assert repository.get("D1").rows[0].method == "EIA-364-04B"

        stale = client.post(
            "/api/projects/P1/matrix-method-version-sync/preview",
            json={
                "project_matrix_draft_id": "D1",
                "expected_saved_payload_signature": signature,
            },
        )
        assert stale.status_code == 409
    app.dependency_overrides.clear()
    engine.dispose()


class _Confirmed:
    def get_active_by_project(self, _project_id: str):
        return SimpleNamespace(version=SimpleNamespace(confirmed_matrix_id="CM1"))


class _Resources:
    def get_by_type(self, _resource_type):
        return ExternalResource(
            resource_id="STD1",
            resource_type=ExternalResourceType.STANDARD_RECORD_EXCEL,
            path=Path("standard.xlsx"),
            worksheet_name="认可标准",
        )


class _Catalog:
    def read_standard_records(self):
        return StandardRecordReadResult(
            resource_path="standard.xlsx",
            matched_sheets=("认可标准",),
            rows=(StandardRecordRow("EIA-364-04B", "CR", None, "认可标准", 3),),
        )
