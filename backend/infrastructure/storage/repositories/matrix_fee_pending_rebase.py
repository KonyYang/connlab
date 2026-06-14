"""Repository for pending Matrix-to-Fee rebase payloads."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from backend.application.matrix_fee_pending_rebase_service import (
    MatrixFeePendingRebaseSnapshot,
)
from backend.infrastructure.storage.models import MatrixFeePendingRebaseModel


class MatrixFeePendingRebaseRepository:
    """Persist pending Fee rebase payloads bound to Matrix draft ids."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_current(
        self, snapshot: MatrixFeePendingRebaseSnapshot
    ) -> MatrixFeePendingRebaseSnapshot:
        """Create or replace pending rebase only with a newer generation."""
        insert_stmt = sqlite_insert(MatrixFeePendingRebaseModel).values(
            pending_rebase_id=snapshot.pending_rebase_id,
            project_id=snapshot.project_id,
            project_matrix_draft_id=snapshot.project_matrix_draft_id,
            base_confirmed_matrix_id=snapshot.base_confirmed_matrix_id,
            base_confirmed_revision=snapshot.base_confirmed_revision,
            fee_rule_version_id=snapshot.fee_rule_version_id,
            matrix_draft_payload_signature=snapshot.matrix_draft_payload_signature,
            generation=snapshot.generation,
            payload_json=snapshot.payload_json,
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
        )
        self._session.execute(
            insert_stmt.on_conflict_do_update(
                index_elements=[
                    MatrixFeePendingRebaseModel.project_matrix_draft_id,
                    MatrixFeePendingRebaseModel.fee_rule_version_id,
                ],
                set_={
                    "project_id": insert_stmt.excluded.project_id,
                    "base_confirmed_matrix_id": (
                        insert_stmt.excluded.base_confirmed_matrix_id
                    ),
                    "base_confirmed_revision": (
                        insert_stmt.excluded.base_confirmed_revision
                    ),
                    "matrix_draft_payload_signature": (
                        insert_stmt.excluded.matrix_draft_payload_signature
                    ),
                    "generation": insert_stmt.excluded.generation,
                    "payload_json": insert_stmt.excluded.payload_json,
                    "updated_at": insert_stmt.excluded.updated_at,
                },
                where=(
                    MatrixFeePendingRebaseModel.generation
                    < insert_stmt.excluded.generation
                ),
            )
        )
        self._session.flush()
        self._session.expire_all()
        saved = self.get_by_context(
            project_matrix_draft_id=snapshot.project_matrix_draft_id,
            fee_rule_version_id=snapshot.fee_rule_version_id,
        )
        if saved is None:
            raise RuntimeError("Pending Matrix-to-Fee rebase upsert did not persist.")
        return saved

    def get_by_context(
        self,
        *,
        project_matrix_draft_id: str,
        fee_rule_version_id: str,
    ) -> MatrixFeePendingRebaseSnapshot | None:
        """Return pending rebase for one Matrix draft/rule context."""
        row = self._session.scalar(
            select(MatrixFeePendingRebaseModel).where(
                MatrixFeePendingRebaseModel.project_matrix_draft_id
                == project_matrix_draft_id,
                MatrixFeePendingRebaseModel.fee_rule_version_id
                == fee_rule_version_id,
            )
        )
        return _to_snapshot(row) if row is not None else None

    def get_latest_by_matrix_draft(
        self,
        project_matrix_draft_id: str,
    ) -> MatrixFeePendingRebaseSnapshot | None:
        """Return latest pending rebase for one Matrix draft across rule contexts."""
        row = self._session.scalar(
            select(MatrixFeePendingRebaseModel)
            .where(
                MatrixFeePendingRebaseModel.project_matrix_draft_id
                == project_matrix_draft_id
            )
            .order_by(
                MatrixFeePendingRebaseModel.updated_at.desc(),
                MatrixFeePendingRebaseModel.pending_rebase_id.desc(),
            )
        )
        return _to_snapshot(row) if row is not None else None

    def delete_by_matrix_draft(self, project_matrix_draft_id: str) -> int:
        """Delete all pending rebases for one Matrix draft id."""
        result = self._session.execute(
            delete(MatrixFeePendingRebaseModel).where(
                MatrixFeePendingRebaseModel.project_matrix_draft_id
                == project_matrix_draft_id
            )
        )
        self._session.flush()
        return int(result.rowcount or 0)


def _to_snapshot(row: MatrixFeePendingRebaseModel) -> MatrixFeePendingRebaseSnapshot:
    return MatrixFeePendingRebaseSnapshot(
        pending_rebase_id=row.pending_rebase_id,
        project_id=row.project_id,
        project_matrix_draft_id=row.project_matrix_draft_id,
        base_confirmed_matrix_id=row.base_confirmed_matrix_id,
        base_confirmed_revision=row.base_confirmed_revision,
        fee_rule_version_id=row.fee_rule_version_id,
        matrix_draft_payload_signature=row.matrix_draft_payload_signature,
        generation=row.generation,
        payload_json=row.payload_json,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
