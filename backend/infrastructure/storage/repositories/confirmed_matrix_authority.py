"""Repository for immutable Confirmed Matrix authority persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)
from backend.infrastructure.storage.models_confirmed_matrix_authority import (
    ConfirmedMatrixCellModel,
    ConfirmedMatrixGroupModel,
    ConfirmedMatrixRowModel,
    ConfirmedMatrixVersionModel,
)


class ConfirmedMatrixAuthorityRepository:
    """Persist and load immutable Confirmed Matrix authority snapshots."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_snapshot(self, snapshot: ConfirmedMatrixSnapshot) -> ConfirmedMatrixSnapshot:
        """Persist one confirmed authority aggregate in one transaction scope."""
        self._session.add(_to_version_model(snapshot.version))
        self._session.add_all(_to_group_models(snapshot.groups))
        self._session.add_all(_to_row_models(snapshot.rows))
        self._session.add_all(_to_cell_models(snapshot.cells))
        self._session.flush()
        return snapshot

    def supersede_active_and_create_snapshot(
        self,
        *,
        previous_active_confirmed_matrix_id: str,
        snapshot: ConfirmedMatrixSnapshot,
        superseded_reason: str | None = None,
    ) -> ConfirmedMatrixSnapshot:
        """Supersede previous active version and create new active snapshot atomically."""
        previous_active = self._session.get(
            ConfirmedMatrixVersionModel,
            previous_active_confirmed_matrix_id,
        )
        if previous_active is None or not previous_active.is_active_authority:
            raise LookupError("Previous active confirmed matrix not found.")
        previous_active.status = ConfirmedMatrixStatus.SUPERSEDED.value
        previous_active.is_active_authority = False
        previous_active.superseded_by_confirmed_matrix_id = snapshot.version.confirmed_matrix_id
        previous_active.superseded_at = snapshot.version.confirmed_at
        previous_active.superseded_reason = _normalize_optional_text(superseded_reason)
        return self.create_snapshot(snapshot)

    def get(self, confirmed_matrix_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return one confirmed authority aggregate by id."""
        version_row = self._session.get(ConfirmedMatrixVersionModel, confirmed_matrix_id)
        if version_row is None:
            return None
        return self._build_snapshot(version_row)

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return one active confirmed authority aggregate in one project."""
        version_row = self._session.scalar(
            select(ConfirmedMatrixVersionModel).where(
                ConfirmedMatrixVersionModel.project_id == project_id,
                ConfirmedMatrixVersionModel.is_active_authority.is_(True),
            )
        )
        if version_row is None:
            return None
        return self._build_snapshot(version_row)

    def list_by_project(self, project_id: str) -> tuple[ConfirmedMatrixSnapshot, ...]:
        """Return all confirmed authority snapshots in one project by revision ascending."""
        version_rows = self._session.scalars(
            select(ConfirmedMatrixVersionModel)
            .where(ConfirmedMatrixVersionModel.project_id == project_id)
            .order_by(ConfirmedMatrixVersionModel.confirmed_revision.asc())
        ).all()
        return tuple(self._build_snapshot(version_row) for version_row in version_rows)

    def _build_snapshot(self, version_row: ConfirmedMatrixVersionModel) -> ConfirmedMatrixSnapshot:
        group_rows = self._session.scalars(
            select(ConfirmedMatrixGroupModel)
            .where(ConfirmedMatrixGroupModel.confirmed_matrix_id == version_row.confirmed_matrix_id)
            .order_by(ConfirmedMatrixGroupModel.group_order.asc())
        ).all()
        row_rows = self._session.scalars(
            select(ConfirmedMatrixRowModel)
            .where(ConfirmedMatrixRowModel.confirmed_matrix_id == version_row.confirmed_matrix_id)
            .order_by(ConfirmedMatrixRowModel.row_order.asc())
        ).all()
        cell_rows = self._session.scalars(
            select(ConfirmedMatrixCellModel)
            .where(ConfirmedMatrixCellModel.confirmed_matrix_id == version_row.confirmed_matrix_id)
            .order_by(ConfirmedMatrixCellModel.confirmed_cell_id.asc())
        ).all()
        return ConfirmedMatrixSnapshot(
            version=_to_version_domain(version_row),
            groups=tuple(_to_group_domain(row) for row in group_rows),
            rows=tuple(_to_row_domain(row) for row in row_rows),
            cells=tuple(_to_cell_domain(row) for row in cell_rows),
        )


def _to_version_model(version: ConfirmedMatrixVersion) -> ConfirmedMatrixVersionModel:
    return ConfirmedMatrixVersionModel(
        confirmed_matrix_id=version.confirmed_matrix_id,
        project_id=version.project_id,
        project_matrix_draft_id=version.project_matrix_draft_id,
        source_import_id=version.source_import_id,
        source_snapshot_id=version.source_snapshot_id,
        confirmed_revision=version.confirmed_revision,
        is_active_authority=version.is_active_authority,
        status=version.status.value,
        confirmed_by=version.confirmed_by,
        confirmed_at=version.confirmed_at,
        superseded_by_confirmed_matrix_id=version.superseded_by_confirmed_matrix_id,
        superseded_at=version.superseded_at,
        superseded_reason=version.superseded_reason,
    )


def _to_group_models(
    groups: tuple[ConfirmedMatrixGroup, ...],
) -> list[ConfirmedMatrixGroupModel]:
    return [
        ConfirmedMatrixGroupModel(
            confirmed_group_id=group.confirmed_group_id,
            confirmed_matrix_id=group.confirmed_matrix_id,
            draft_group_id=group.draft_group_id,
            source_group_snapshot_id=group.source_group_snapshot_id,
            group_order=group.group_order,
            group_key=group.group_key,
            group_label=group.group_label,
            sample_quantity_expression=group.sample_quantity_expression,
            sample_note=group.sample_note,
        )
        for group in groups
    ]


def _to_row_models(rows: tuple[ConfirmedMatrixRow, ...]) -> list[ConfirmedMatrixRowModel]:
    return [
        ConfirmedMatrixRowModel(
            confirmed_row_id=row.confirmed_row_id,
            confirmed_matrix_id=row.confirmed_matrix_id,
            draft_row_id=row.draft_row_id,
            source_row_snapshot_id=row.source_row_snapshot_id,
            row_order=row.row_order,
            test_item=row.test_item,
            source_section=row.source_section,
            method=row.method,
            condition=row.condition,
            requirement=row.requirement,
        )
        for row in rows
    ]


def _to_cell_models(
    cells: tuple[ConfirmedMatrixCell, ...],
) -> list[ConfirmedMatrixCellModel]:
    return [
        ConfirmedMatrixCellModel(
            confirmed_cell_id=cell.confirmed_cell_id,
            confirmed_matrix_id=cell.confirmed_matrix_id,
            confirmed_row_id=cell.confirmed_row_id,
            confirmed_group_id=cell.confirmed_group_id,
            draft_row_id=cell.draft_row_id,
            draft_group_id=cell.draft_group_id,
            cell_value=cell.cell_value,
        )
        for cell in cells
    ]


def _to_version_domain(row: ConfirmedMatrixVersionModel) -> ConfirmedMatrixVersion:
    return ConfirmedMatrixVersion(
        confirmed_matrix_id=row.confirmed_matrix_id,
        project_id=row.project_id,
        project_matrix_draft_id=row.project_matrix_draft_id,
        source_import_id=row.source_import_id,
        source_snapshot_id=row.source_snapshot_id,
        confirmed_revision=row.confirmed_revision,
        is_active_authority=row.is_active_authority,
        status=ConfirmedMatrixStatus(row.status),
        confirmed_by=row.confirmed_by,
        confirmed_at=row.confirmed_at,
        superseded_by_confirmed_matrix_id=row.superseded_by_confirmed_matrix_id,
        superseded_at=row.superseded_at,
        superseded_reason=row.superseded_reason,
    )


def _to_group_domain(row: ConfirmedMatrixGroupModel) -> ConfirmedMatrixGroup:
    return ConfirmedMatrixGroup(
        confirmed_group_id=row.confirmed_group_id,
        confirmed_matrix_id=row.confirmed_matrix_id,
        draft_group_id=row.draft_group_id,
        source_group_snapshot_id=row.source_group_snapshot_id,
        group_order=row.group_order,
        group_key=row.group_key,
        group_label=row.group_label,
        sample_quantity_expression=row.sample_quantity_expression,
        sample_note=row.sample_note,
    )


def _to_row_domain(row: ConfirmedMatrixRowModel) -> ConfirmedMatrixRow:
    return ConfirmedMatrixRow(
        confirmed_row_id=row.confirmed_row_id,
        confirmed_matrix_id=row.confirmed_matrix_id,
        draft_row_id=row.draft_row_id,
        source_row_snapshot_id=row.source_row_snapshot_id,
        row_order=row.row_order,
        test_item=row.test_item,
        source_section=row.source_section,
        method=row.method,
        condition=row.condition,
        requirement=row.requirement,
    )


def _to_cell_domain(row: ConfirmedMatrixCellModel) -> ConfirmedMatrixCell:
    return ConfirmedMatrixCell(
        confirmed_cell_id=row.confirmed_cell_id,
        confirmed_matrix_id=row.confirmed_matrix_id,
        confirmed_row_id=row.confirmed_row_id,
        confirmed_group_id=row.confirmed_group_id,
        draft_row_id=row.draft_row_id,
        draft_group_id=row.draft_group_id,
        cell_value=row.cell_value,
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None
