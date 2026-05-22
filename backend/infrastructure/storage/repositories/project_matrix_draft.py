"""Repository for Project Matrix draft working-copy persistence."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.domain import (
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
)
from backend.infrastructure.storage.models_project_matrix_draft import (
    ProjectMatrixDraftCellModel,
    ProjectMatrixDraftGroupModel,
    ProjectMatrixDraftRecordModel,
    ProjectMatrixDraftRowModel,
)


class ProjectMatrixDraftRepository:
    """Persist and load structured Project Matrix draft working copies."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_snapshot(self, snapshot: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftSnapshot:
        """Persist one draft root and child rows atomically in one session."""
        self._session.add(_to_record_model(snapshot.record))
        self._session.add_all(_to_group_models(snapshot.groups))
        self._session.add_all(_to_row_models(snapshot.rows))
        self._session.add_all(_to_cell_models(snapshot.cells))
        self._session.flush()
        return snapshot

    def replace_snapshot(self, snapshot: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftSnapshot:
        """Replace one existing draft aggregate atomically in one session."""
        record_row = self._session.get(
            ProjectMatrixDraftRecordModel,
            snapshot.record.project_matrix_draft_id,
        )
        if record_row is None:
            raise LookupError("Project matrix draft record not found.")
        record_row.status = snapshot.record.status.value
        record_row.updated_at = snapshot.record.updated_at
        self._session.execute(
            delete(ProjectMatrixDraftCellModel).where(
                ProjectMatrixDraftCellModel.project_matrix_draft_id
                == snapshot.record.project_matrix_draft_id
            )
        )
        self._session.execute(
            delete(ProjectMatrixDraftGroupModel).where(
                ProjectMatrixDraftGroupModel.project_matrix_draft_id
                == snapshot.record.project_matrix_draft_id
            )
        )
        self._session.execute(
            delete(ProjectMatrixDraftRowModel).where(
                ProjectMatrixDraftRowModel.project_matrix_draft_id
                == snapshot.record.project_matrix_draft_id
            )
        )
        self._session.add_all(_to_group_models(snapshot.groups))
        self._session.add_all(_to_row_models(snapshot.rows))
        self._session.add_all(_to_cell_models(snapshot.cells))
        self._session.flush()
        return snapshot

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        """Return one draft aggregate by draft id."""
        record_row = self._session.get(ProjectMatrixDraftRecordModel, project_matrix_draft_id)
        if record_row is None:
            return None
        group_rows = self._session.scalars(
            select(ProjectMatrixDraftGroupModel)
            .where(ProjectMatrixDraftGroupModel.project_matrix_draft_id == project_matrix_draft_id)
            .order_by(ProjectMatrixDraftGroupModel.group_order.asc())
        ).all()
        row_rows = self._session.scalars(
            select(ProjectMatrixDraftRowModel)
            .where(ProjectMatrixDraftRowModel.project_matrix_draft_id == project_matrix_draft_id)
            .order_by(ProjectMatrixDraftRowModel.row_order.asc())
        ).all()
        cell_rows = self._session.scalars(
            select(ProjectMatrixDraftCellModel)
            .where(ProjectMatrixDraftCellModel.project_matrix_draft_id == project_matrix_draft_id)
            .order_by(ProjectMatrixDraftCellModel.draft_cell_id.asc())
        ).all()
        return ProjectMatrixDraftSnapshot(
            record=_to_record_domain(record_row),
            groups=tuple(_to_group_domain(row) for row in group_rows),
            rows=tuple(_to_row_domain(row) for row in row_rows),
            cells=tuple(_to_cell_domain(row) for row in cell_rows),
        )

    def list_by_project(self, project_id: str) -> list[ProjectMatrixDraftRecord]:
        """List draft records by project, newest first."""
        rows = self._session.scalars(
            select(ProjectMatrixDraftRecordModel)
            .where(ProjectMatrixDraftRecordModel.project_id == project_id)
            .order_by(ProjectMatrixDraftRecordModel.updated_at.desc())
        ).all()
        return [_to_record_domain(row) for row in rows]

    def get_by_project_and_source_import(
        self,
        project_id: str,
        source_import_id: str,
    ) -> ProjectMatrixDraftRecord | None:
        """Return one draft record by project and source import lineage."""
        row = self._session.scalar(
            select(ProjectMatrixDraftRecordModel).where(
                ProjectMatrixDraftRecordModel.project_id == project_id,
                ProjectMatrixDraftRecordModel.source_import_id == source_import_id,
            )
        )
        return _to_record_domain(row) if row else None

    def get_by_project_and_base_confirmed_matrix(
        self,
        project_id: str,
        base_confirmed_matrix_id: str,
    ) -> ProjectMatrixDraftRecord | None:
        """Return one draft record by project and base confirmed authority lineage."""
        row = self._session.scalar(
            select(ProjectMatrixDraftRecordModel).where(
                ProjectMatrixDraftRecordModel.project_id == project_id,
                ProjectMatrixDraftRecordModel.base_confirmed_matrix_id == base_confirmed_matrix_id,
            )
        )
        return _to_record_domain(row) if row else None


def _to_record_model(record: ProjectMatrixDraftRecord) -> ProjectMatrixDraftRecordModel:
    return ProjectMatrixDraftRecordModel(
        project_matrix_draft_id=record.project_matrix_draft_id,
        project_id=record.project_id,
        source_import_id=record.source_import_id,
        source_snapshot_id=record.source_snapshot_id,
        base_confirmed_matrix_id=record.base_confirmed_matrix_id,
        status=record.status.value,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _to_group_models(groups: tuple[ProjectMatrixDraftGroup, ...]) -> list[ProjectMatrixDraftGroupModel]:
    return [
        ProjectMatrixDraftGroupModel(
            draft_group_id=group.draft_group_id,
            project_matrix_draft_id=group.project_matrix_draft_id,
            source_group_snapshot_id=group.source_group_snapshot_id,
            group_order=group.group_order,
            group_key=group.group_key,
            group_label=group.group_label,
            is_selected=group.is_selected,
            sample_quantity_expression=group.sample_quantity_expression,
            sample_note=group.sample_note,
        )
        for group in groups
    ]


def _to_row_models(rows: tuple[ProjectMatrixDraftRow, ...]) -> list[ProjectMatrixDraftRowModel]:
    return [
        ProjectMatrixDraftRowModel(
            draft_row_id=row.draft_row_id,
            project_matrix_draft_id=row.project_matrix_draft_id,
            source_row_snapshot_id=row.source_row_snapshot_id,
            row_order=row.row_order,
            test_item=row.test_item,
            source_section=row.source_section,
            method=row.method,
            condition=row.condition,
            requirement=row.requirement,
            is_sample_row=row.is_sample_row,
        )
        for row in rows
    ]


def _to_cell_models(
    cells: tuple[ProjectMatrixDraftCell, ...],
) -> list[ProjectMatrixDraftCellModel]:
    return [
        ProjectMatrixDraftCellModel(
            draft_cell_id=cell.draft_cell_id,
            project_matrix_draft_id=cell.project_matrix_draft_id,
            draft_row_id=cell.draft_row_id,
            draft_group_id=cell.draft_group_id,
            cell_value=cell.cell_value,
        )
        for cell in cells
    ]


def _to_record_domain(row: ProjectMatrixDraftRecordModel) -> ProjectMatrixDraftRecord:
    return ProjectMatrixDraftRecord(
        project_matrix_draft_id=row.project_matrix_draft_id,
        project_id=row.project_id,
        source_import_id=row.source_import_id,
        source_snapshot_id=row.source_snapshot_id,
        base_confirmed_matrix_id=row.base_confirmed_matrix_id,
        status=ProjectMatrixDraftStatus(row.status),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_group_domain(row: ProjectMatrixDraftGroupModel) -> ProjectMatrixDraftGroup:
    return ProjectMatrixDraftGroup(
        draft_group_id=row.draft_group_id,
        project_matrix_draft_id=row.project_matrix_draft_id,
        source_group_snapshot_id=row.source_group_snapshot_id,
        group_order=row.group_order,
        group_key=row.group_key,
        group_label=row.group_label,
        is_selected=row.is_selected,
        sample_quantity_expression=row.sample_quantity_expression,
        sample_note=row.sample_note,
    )


def _to_row_domain(row: ProjectMatrixDraftRowModel) -> ProjectMatrixDraftRow:
    return ProjectMatrixDraftRow(
        draft_row_id=row.draft_row_id,
        project_matrix_draft_id=row.project_matrix_draft_id,
        source_row_snapshot_id=row.source_row_snapshot_id,
        row_order=row.row_order,
        test_item=row.test_item,
        source_section=row.source_section,
        method=row.method,
        condition=row.condition,
        requirement=row.requirement,
        is_sample_row=row.is_sample_row,
    )


def _to_cell_domain(row: ProjectMatrixDraftCellModel) -> ProjectMatrixDraftCell:
    return ProjectMatrixDraftCell(
        draft_cell_id=row.draft_cell_id,
        project_matrix_draft_id=row.project_matrix_draft_id,
        draft_row_id=row.draft_row_id,
        draft_group_id=row.draft_group_id,
        cell_value=row.cell_value,
    )
