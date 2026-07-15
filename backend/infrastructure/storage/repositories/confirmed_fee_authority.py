"""Repository for immutable Confirmed Fee authority versions."""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.domain.confirmed_fee import ConfirmedFeeSummary, ConfirmedFeeVersion
from backend.application.confirmed_fee_version_service import ConfirmedFeeVersionConflictError
from backend.infrastructure.storage.models import ConfirmedFeeVersionModel


class ConfirmedFeeAuthorityRepository:
    """Persist and load versioned Confirmed Fee authority snapshots."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, version: ConfirmedFeeVersion) -> ConfirmedFeeVersion:
        """Persist one immutable Confirmed Fee version."""
        self._session.add(_to_model(version))
        self._session.flush()
        return version

    def create_or_get_exact(self, version: ConfirmedFeeVersion) -> ConfirmedFeeVersion:
        """Insert once or re-read an exact V2 lineage after SQLite revision contention."""
        try:
            return self.create(version)
        except IntegrityError as exc:
            self._session.rollback()
            existing = self._session.scalar(
                select(ConfirmedFeeVersionModel).where(
                    ConfirmedFeeVersionModel.project_id == version.project_id,
                    ConfirmedFeeVersionModel.confirmed_fee_revision
                    == version.confirmed_fee_revision,
                )
            )
            if existing is not None and _same_confirmation(_to_domain(existing), version):
                return _to_domain(existing)
            raise ConfirmedFeeVersionConflictError(
                "Fee Evaluation confirmation changed concurrently. Reload and confirm again."
            ) from exc

    def get_latest_by_project(self, project_id: str) -> ConfirmedFeeVersion | None:
        """Return the latest Confirmed Fee version for one project."""
        row = self._session.scalar(
            select(ConfirmedFeeVersionModel)
            .where(ConfirmedFeeVersionModel.project_id == project_id)
            .order_by(
                ConfirmedFeeVersionModel.confirmed_fee_revision.desc(),
                ConfirmedFeeVersionModel.confirmed_at.desc(),
                ConfirmedFeeVersionModel.confirmed_fee_id.desc(),
            )
        )
        return _to_domain(row) if row is not None else None

    def list_by_project(self, project_id: str) -> tuple[ConfirmedFeeVersion, ...]:
        """Return Confirmed Fee versions for one project by revision ascending."""
        rows = self._session.scalars(
            select(ConfirmedFeeVersionModel)
            .where(ConfirmedFeeVersionModel.project_id == project_id)
            .order_by(
                ConfirmedFeeVersionModel.confirmed_fee_revision.asc(),
                ConfirmedFeeVersionModel.confirmed_at.asc(),
                ConfirmedFeeVersionModel.confirmed_fee_id.asc(),
            )
        ).all()
        return tuple(_to_domain(row) for row in rows)


def _to_model(version: ConfirmedFeeVersion) -> ConfirmedFeeVersionModel:
    return ConfirmedFeeVersionModel(
        confirmed_fee_id=version.confirmed_fee_id,
        project_id=version.project_id,
        confirmed_fee_revision=version.confirmed_fee_revision,
        confirmed_matrix_id=version.confirmed_matrix_id,
        confirmed_revision=version.confirmed_revision,
        fee_rule_version_id=version.fee_rule_version_id,
        pricing_draft_edit_id=version.pricing_draft_edit_id,
        pricing_effective_from=version.pricing_effective_from,
        summary_json=_summary_to_json(version.summary),
        pricing_snapshot_json=version.pricing_snapshot_json,
        confirmed_by=version.confirmed_by,
        confirmed_at=version.confirmed_at,
        confirmation_note=version.confirmation_note,
    )


def _to_domain(row: ConfirmedFeeVersionModel) -> ConfirmedFeeVersion:
    return ConfirmedFeeVersion(
        confirmed_fee_id=row.confirmed_fee_id,
        project_id=row.project_id,
        confirmed_fee_revision=row.confirmed_fee_revision,
        confirmed_matrix_id=row.confirmed_matrix_id,
        confirmed_revision=row.confirmed_revision,
        fee_rule_version_id=row.fee_rule_version_id,
        pricing_draft_edit_id=row.pricing_draft_edit_id,
        pricing_effective_from=row.pricing_effective_from,
        summary=_summary_from_json(row.summary_json),
        pricing_snapshot_json=row.pricing_snapshot_json,
        confirmed_by=row.confirmed_by,
        confirmed_at=row.confirmed_at,
        confirmation_note=row.confirmation_note,
    )


def _summary_to_json(summary: ConfirmedFeeSummary) -> str:
    return json.dumps(
        {
            "testing_fee_total": summary.testing_fee_total,
            "working_hours": summary.working_hours,
            "lab_manpower_cost": summary.lab_manpower_cost,
            "external_cost": summary.external_cost,
            "grand_cost": summary.grand_cost,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def _summary_from_json(payload_json: str) -> ConfirmedFeeSummary:
    payload = json.loads(payload_json)
    return ConfirmedFeeSummary(
        testing_fee_total=str(payload["testing_fee_total"]),
        working_hours=str(payload["working_hours"]),
        lab_manpower_cost=str(payload["lab_manpower_cost"]),
        external_cost=str(payload["external_cost"]),
        grand_cost=str(payload["grand_cost"]),
    )


def _same_confirmation(left: ConfirmedFeeVersion, right: ConfirmedFeeVersion) -> bool:
    return (
        left.project_id == right.project_id
        and left.confirmed_matrix_id == right.confirmed_matrix_id
        and left.confirmed_revision == right.confirmed_revision
        and left.fee_rule_version_id == right.fee_rule_version_id
        and left.pricing_draft_edit_id == right.pricing_draft_edit_id
        and left.summary == right.summary
        and left.pricing_snapshot_json == right.pricing_snapshot_json
    )
