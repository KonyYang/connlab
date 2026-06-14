from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.application.matrix_fee_pending_rebase_service import (
    MatrixFeePendingRebaseSnapshot,
)
from backend.infrastructure.storage.database import Base
from backend.infrastructure.storage.models import ProjectModel
from backend.infrastructure.storage.models_project_matrix_draft import (
    ProjectMatrixDraftRecordModel,
)
from backend.infrastructure.storage.repositories.matrix_fee_pending_rebase import (
    MatrixFeePendingRebaseRepository,
)


def test_pending_rebase_repository_upserts_current_context() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_project_and_draft(session)
        repo = MatrixFeePendingRebaseRepository(session)

        first = repo.upsert_current(_snapshot("pending-1", generation=1, payload="first"))
        second = repo.upsert_current(_snapshot("pending-2", generation=2, payload="second"))
        loaded = repo.get_by_context(
            project_matrix_draft_id="pmd-1",
            fee_rule_version_id="fee-rules-v1",
        )

    assert first.pending_rebase_id == "pending-1"
    assert second.pending_rebase_id == "pending-1"
    assert loaded is not None
    assert loaded.generation == 2
    assert loaded.payload_json == "second"


def test_pending_rebase_repository_rejects_older_generation_overwrite() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_project_and_draft(session)
        repo = MatrixFeePendingRebaseRepository(session)

        repo.upsert_current(_snapshot("pending-1", generation=3, payload="newer"))
        stale = repo.upsert_current(_snapshot("pending-2", generation=2, payload="older"))
        loaded = repo.get_latest_by_matrix_draft("pmd-1")

    assert stale.pending_rebase_id == "pending-1"
    assert loaded is not None
    assert loaded.generation == 3
    assert loaded.payload_json == "newer"


def test_pending_rebase_repository_rejects_equal_generation_overwrite() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_project_and_draft(session)
        repo = MatrixFeePendingRebaseRepository(session)

        repo.upsert_current(_snapshot("pending-1", generation=3, payload="first"))
        equal = repo.upsert_current(_snapshot("pending-2", generation=3, payload="equal"))
        loaded = repo.get_latest_by_matrix_draft("pmd-1")

    assert equal.pending_rebase_id == "pending-1"
    assert loaded is not None
    assert loaded.generation == 3
    assert loaded.payload_json == "first"


def test_pending_rebase_repository_rejects_stale_cross_session_overwrite(
    tmp_path,
) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'pending-rebase.db'}", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine, future=True, expire_on_commit=False)
    with SessionLocal() as session:
        _seed_project_and_draft(session)
        MatrixFeePendingRebaseRepository(session).upsert_current(
            _snapshot("pending-1", generation=1, payload="initial")
        )
        session.commit()

    with SessionLocal() as stale_session, SessionLocal() as newer_session:
        stale_repo = MatrixFeePendingRebaseRepository(stale_session)
        newer_repo = MatrixFeePendingRebaseRepository(newer_session)
        assert stale_repo.get_by_context(
            project_matrix_draft_id="pmd-1",
            fee_rule_version_id="fee-rules-v1",
        ).generation == 1

        newer_repo.upsert_current(_snapshot("pending-3", generation=3, payload="newer"))
        newer_session.commit()
        stale = stale_repo.upsert_current(
            _snapshot("pending-2", generation=2, payload="stale")
        )
        stale_session.commit()

    with Session(engine) as session:
        loaded = MatrixFeePendingRebaseRepository(session).get_latest_by_matrix_draft(
            "pmd-1"
        )

    assert stale.generation == 3
    assert loaded is not None
    assert loaded.generation == 3
    assert loaded.payload_json == "newer"


def test_pending_rebase_repository_deletes_by_matrix_draft() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_project_and_draft(session)
        repo = MatrixFeePendingRebaseRepository(session)

        repo.upsert_current(_snapshot("pending-1", generation=1, payload="first"))
        repo.upsert_current(
            _snapshot(
                "pending-2",
                generation=1,
                payload="second",
                fee_rule_version_id="fee-rules-v2",
            )
        )
        deleted_count = repo.delete_by_matrix_draft("pmd-1")
        loaded = repo.get_latest_by_matrix_draft("pmd-1")

    assert deleted_count == 2
    assert loaded is None


def _seed_project_and_draft(session: Session) -> None:
    session.add(
        ProjectModel(
            project_id="P1",
            project_no="DL-2026-06-001",
            product_name="Connector",
            requestor="Alice",
            status="active",
        )
    )
    session.add(
        ProjectMatrixDraftRecordModel(
            project_matrix_draft_id="pmd-1",
            project_id="P1",
            source_import_id=None,
            source_snapshot_id="snapshot-1",
            base_confirmed_matrix_id="cmv-base",
            status="draft",
            created_at="2026-06-14T09:00:00+00:00",
            updated_at="2026-06-14T09:01:00+00:00",
        )
    )
    session.flush()


def _snapshot(
    pending_rebase_id: str,
    *,
    generation: int,
    payload: str,
    fee_rule_version_id: str = "fee-rules-v1",
) -> MatrixFeePendingRebaseSnapshot:
    return MatrixFeePendingRebaseSnapshot(
        pending_rebase_id=pending_rebase_id,
        project_id="P1",
        project_matrix_draft_id="pmd-1",
        base_confirmed_matrix_id="cmv-base",
        base_confirmed_revision=1,
        fee_rule_version_id=fee_rule_version_id,
        matrix_draft_payload_signature=f"sig-{generation}",
        generation=generation,
        payload_json=payload,
        created_at="2026-06-14T09:00:00+00:00",
        updated_at=f"2026-06-14T09:0{generation}:00+00:00",
    )
