from __future__ import annotations

from collections.abc import Generator
from dataclasses import replace
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import (
    get_matrix_editor_session_service,
    get_matrix_import_commit_service,
    get_session,
)
from backend.api.main import app
from backend.application.external_excel_read_service import (
    StandardRecordReadResult,
    StandardRecordRow,
)
from backend.application.matrix_import_commit_service import MatrixImportCommitService
from backend.application.matrix_import_method_authority import (
    MatrixImportMethodAuthorityResolver,
)
from backend.application.source_matrix_import_persistence_service import (
    SourceMatrixImportPersistenceService,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    Project,
    ProjectStatus,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ProjectMatrixDraftRepository,
    ProjectRepository,
    SourceMatrixImportRepository,
)
from backend.shared.config import Settings


def test_matrix_editor_session_composes_import_method_authority(tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            service = get_matrix_editor_session_service(
                session=session,
                settings=settings,
            )
            assert isinstance(
                service._matrix_import_commit._method_authority,
                MatrixImportMethodAuthorityResolver,
            )
    finally:
        engine.dispose()


def test_replace_updates_methods_returns_summary_and_strictly_reuses(tmp_path: Path) -> None:
    authority = _AuthorityFacts()
    client, engine, session_factory = _client(tmp_path, authority)
    try:
        first = client.post(
            "/api/projects/P1/matrix-import/commit", json=_request()
        )
        assert first.status_code == 201
        body = first.json()
        assert body["commit_status"] == "created"
        assert [row["method"] for row in body["project_matrix_draft"]["rows"]] == [
            "EIA-364-18C",
            "EIA-364-20A",
        ]
        assert body["method_authority_sync"]["status"] == "synchronized"
        assert body["method_authority_sync"]["updated_count"] == 1
        assert body["method_authority_sync"]["current_count"] == 1
        assert body["method_authority_sync"]["review_count"] == 0
        counts = _counts(session_factory)

        replay = client.post(
            "/api/projects/P1/matrix-import/commit", json=_request()
        )
        assert replay.status_code == 201
        assert replay.json()["commit_status"] == "reused"
        assert _counts(session_factory) == counts
        assert authority.reader.calls == 2
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_replace_blocks_changed_catalog_context_without_writes(tmp_path: Path) -> None:
    authority = _AuthorityFacts()
    client, engine, session_factory = _client(tmp_path, authority)
    try:
        created = client.post(
            "/api/projects/P1/matrix-import/commit", json=_request()
        )
        assert created.status_code == 201
        counts = _counts(session_factory)
        authority.reader.revision = "D"

        conflict = client.post(
            "/api/projects/P1/matrix-import/commit", json=_request()
        )
        assert conflict.status_code == 409
        assert "authority changed" in conflict.json()["detail"]
        assert _counts(session_factory) == counts
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_replace_blocks_changed_standard_path_with_identical_rows(tmp_path: Path) -> None:
    authority = _AuthorityFacts()
    client, engine, session_factory = _client(tmp_path, authority)
    try:
        created = client.post(
            "/api/projects/P1/matrix-import/commit", json=_request()
        )
        assert created.status_code == 201
        counts = _counts(session_factory)
        authority.path = Path("D:/replacement/standards.xlsx")
        authority.reader.resource_path = "D:/replacement/standards.xlsx"

        conflict = client.post(
            "/api/projects/P1/matrix-import/commit", json=_request()
        )
        assert conflict.status_code == 409
        assert _counts(session_factory) == counts
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_replace_blocks_missing_context_and_manual_method_change(tmp_path: Path) -> None:
    authority = _AuthorityFacts()
    client, engine, session_factory = _client(tmp_path, authority)
    try:
        created = client.post(
            "/api/projects/P1/matrix-import/commit", json=_request()
        )
        assert created.status_code == 201
        draft_id = created.json()["project_matrix_draft"]["record"][
            "project_matrix_draft_id"
        ]
        counts = _counts(session_factory)
        with session_factory() as session:
            repository = ProjectMatrixDraftRepository(session)
            snapshot = repository.get(draft_id)
            assert snapshot is not None
            repository.replace_snapshot(
                replace(
                    snapshot,
                    record=replace(snapshot.record, method_sync_context_json=None),
                    rows=(replace(snapshot.rows[0], method="manual"), *snapshot.rows[1:]),
                )
            )
            session.commit()

        conflict = client.post(
            "/api/projects/P1/matrix-import/commit", json=_request()
        )
        assert conflict.status_code == 409
        assert "missing or malformed" in conflict.json()["detail"]
        assert _counts(session_factory) == counts
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_replace_source_authority_failure_is_all_table_zero_write(tmp_path: Path) -> None:
    authority = _AuthorityFacts()
    authority.reader.failure = ValueError("invalid Standard worksheet")
    client, engine, session_factory = _client(tmp_path, authority)
    try:
        response = client.post(
            "/api/projects/P1/matrix-import/commit", json=_request()
        )
        assert response.status_code == 422
        assert "invalid Standard worksheet" in response.json()["detail"]
        assert _counts(session_factory) == (0, 0)
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_replace_persistence_failure_rolls_back_source_and_draft(tmp_path: Path) -> None:
    authority = _AuthorityFacts()
    client, engine, session_factory = _client(
        tmp_path, authority, fail_after_draft=True
    )
    try:
        response = client.post(
            "/api/projects/P1/matrix-import/commit", json=_request()
        )
        assert response.status_code == 409
        assert _counts(session_factory) == (0, 0)
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path, authority, *, fail_after_draft=False):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        ProjectRepository(session).create(
            Project(
                project_id="P1",
                project_no="DL-366C",
                product_name="Connector",
                requestor="Alice",
                status=ProjectStatus.LTR_REGISTERED,
                created_on=date(2026, 7, 21),
            )
        )
        session.commit()

    def override_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def override_service():
        with session_factory() as session:
            source = SourceMatrixImportRepository(session)
            draft = ProjectMatrixDraftRepository(session)
            draft_store = _FailAfterDraft(draft) if fail_after_draft else draft
            service = MatrixImportCommitService(
                project_store=ProjectRepository(session),
                source_store=source,
                draft_store=draft_store,
                source_persistence_service=SourceMatrixImportPersistenceService(
                    store=source
                ),
                method_authority=MatrixImportMethodAuthorityResolver(
                    resource_store=authority,
                    catalog_reader=authority.reader,
                    now=lambda: "2026-07-21T00:00:00+00:00",
                ),
                transaction_scope=session.begin_nested,
                now=lambda: "2026-07-21T00:00:00+00:00",
            )
            try:
                yield service
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_matrix_import_commit_service] = override_service
    return TestClient(app), engine, session_factory


def _request() -> dict[str, object]:
    return {
        "source_document_path": "C:/spec.docx",
        "source_document_name": "spec.docx",
        "source_format": ".docx",
        "selected_group_keys": ["g1"],
        "preview_payload": {
            "groups": [
                {
                    "group_key": "g1",
                    "group_label": "Group 1",
                    "steps": [
                        {
                            "source_row_index": 1,
                            "raw_token": "1",
                            "method_summary": "EIA-364-18B",
                        },
                        {
                            "source_row_index": 2,
                            "raw_token": "2",
                            "method_summary": "EIA-364-20A",
                        },
                    ],
                }
            ],
            "rows": [
                {
                    "source_row_index": 1,
                    "test_item": "Visual",
                    "group_tokens": {"g1": "1"},
                },
                {
                    "source_row_index": 2,
                    "test_item": "Mechanical",
                    "group_tokens": {"g1": "2"},
                },
            ],
            "warnings": [],
            "blockers": [],
        },
    }


def _counts(session_factory) -> tuple[int, int]:
    with session_factory() as session:
        return (
            len(SourceMatrixImportRepository(session).list_imports_by_project("P1")),
            len(ProjectMatrixDraftRepository(session).list_by_project("P1")),
        )


class _AuthorityFacts:
    def __init__(self) -> None:
        self.path = Path("C:/standards.xlsx")
        self.reader = _CatalogReader()

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        return ExternalResource(
            resource_id="standard-1",
            resource_type=resource_type,
            path=self.path,
            worksheet_name="认可标准",
        )


class _CatalogReader:
    def __init__(self) -> None:
        self.calls = 0
        self.revision = "C"
        self.resource_path = "C:/standards.xlsx"
        self.failure: Exception | None = None

    def read_standard_records(self) -> StandardRecordReadResult:
        self.calls += 1
        if self.failure:
            raise self.failure
        return StandardRecordReadResult(
            resource_path=self.resource_path,
            matched_sheets=("认可标准",),
            rows=(
                StandardRecordRow(
                    standard_code=f"EIA-364-18{self.revision}-2024",
                    test_item="Visual",
                    sample_description=None,
                    source_sheet="认可标准",
                    source_row_number=3,
                ),
                StandardRecordRow(
                    standard_code="EIA-364-20A-2024",
                    test_item="Mechanical",
                    sample_description=None,
                    source_sheet="认可标准",
                    source_row_number=4,
                ),
            ),
        )


class _FailAfterDraft:
    def __init__(self, delegate: ProjectMatrixDraftRepository) -> None:
        self._delegate = delegate

    def __getattr__(self, name):
        return getattr(self._delegate, name)

    def create_snapshot(self, snapshot):
        self._delegate.create_snapshot(snapshot)
        raise RuntimeError("injected post-draft failure")
