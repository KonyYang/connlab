"""Repository for Project Matrix draft working-copy persistence."""

from __future__ import annotations

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from backend.domain import (
    contact_plan_from_json,
    contact_plan_to_json,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    ProjectMatrixDraftStepQuantity,
)
from backend.infrastructure.storage.models_project_matrix_draft import (
    ProjectMatrixDraftCellModel,
    ProjectMatrixDraftGroupModel,
    ProjectMatrixDraftRecordModel,
    ProjectMatrixDraftRowModel,
    ProjectMatrixDraftStepQuantityModel,
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
        self._session.add_all(_to_step_quantity_models(snapshot.step_quantities))
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
        record_row.pre_test_buffer_days = snapshot.record.pre_test_buffer_days
        record_row.post_test_buffer_days = snapshot.record.post_test_buffer_days
        record_row.sample_received_date = snapshot.record.sample_received_date
        record_row.planned_test_start_date = snapshot.record.planned_test_start_date
        record_row.planned_test_complete_date = snapshot.record.planned_test_complete_date
        record_row.estimated_completion_date = snapshot.record.estimated_completion_date
        record_row.method_sync_context_json = snapshot.record.method_sync_context_json
        self._session.execute(
            delete(ProjectMatrixDraftStepQuantityModel).where(
                ProjectMatrixDraftStepQuantityModel.project_matrix_draft_id
                == snapshot.record.project_matrix_draft_id
            )
        )
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
        self._session.add_all(_to_step_quantity_models(snapshot.step_quantities))
        self._session.flush()
        return snapshot

    def apply_method_sync(
        self,
        *,
        project_matrix_draft_id: str,
        expected_updated_at: str,
        expected_status: str,
        expected_base_confirmed_matrix_id: str | None,
        updated_at: str,
        method_sync_context_json: str,
        updates: tuple[tuple[str, str | None, str], ...],
    ) -> bool:
        """Conditionally update selected row Methods and root provenance."""
        savepoint = self._session.begin_nested()
        try:
            root_result = self._session.execute(
                update(ProjectMatrixDraftRecordModel)
                .where(
                    ProjectMatrixDraftRecordModel.project_matrix_draft_id
                    == project_matrix_draft_id,
                    ProjectMatrixDraftRecordModel.updated_at == expected_updated_at,
                    ProjectMatrixDraftRecordModel.status == expected_status,
                    ProjectMatrixDraftRecordModel.base_confirmed_matrix_id
                    == expected_base_confirmed_matrix_id,
                )
                .values(
                    updated_at=updated_at,
                    method_sync_context_json=method_sync_context_json,
                )
            )
            if root_result.rowcount != 1:
                savepoint.rollback()
                return False
            for row_id, old_method, new_method in updates:
                old_predicate = (
                    ProjectMatrixDraftRowModel.method.is_(None)
                    if old_method is None
                    else ProjectMatrixDraftRowModel.method == old_method
                )
                row_result = self._session.execute(
                    update(ProjectMatrixDraftRowModel)
                    .where(
                        ProjectMatrixDraftRowModel.project_matrix_draft_id
                        == project_matrix_draft_id,
                        ProjectMatrixDraftRowModel.draft_row_id == row_id,
                        old_predicate,
                    )
                    .values(method=new_method)
                )
                if row_result.rowcount != 1:
                    savepoint.rollback()
                    return False
            self._session.flush()
            savepoint.commit()
            return True
        except Exception:
            savepoint.rollback()
            raise

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
        quantity_rows = self._session.scalars(
            select(ProjectMatrixDraftStepQuantityModel)
            .where(
                ProjectMatrixDraftStepQuantityModel.project_matrix_draft_id
                == project_matrix_draft_id
            )
            .order_by(
                ProjectMatrixDraftStepQuantityModel.draft_group_id.asc(),
                ProjectMatrixDraftStepQuantityModel.step_sequence.asc(),
            )
        ).all()
        return ProjectMatrixDraftSnapshot(
            record=_to_record_domain(record_row),
            groups=tuple(_to_group_domain(row) for row in group_rows),
            rows=tuple(_to_row_domain(row) for row in row_rows),
            cells=tuple(_to_cell_domain(row) for row in cell_rows),
            step_quantities=tuple(_to_step_quantity_domain(row) for row in quantity_rows),
        )

    def delete(self, project_matrix_draft_id: str) -> bool:
        """Delete one draft aggregate by draft id."""
        record_row = self._session.get(ProjectMatrixDraftRecordModel, project_matrix_draft_id)
        if record_row is None:
            return False
        self._session.execute(
            delete(ProjectMatrixDraftStepQuantityModel).where(
                ProjectMatrixDraftStepQuantityModel.project_matrix_draft_id
                == project_matrix_draft_id
            )
        )
        self._session.execute(
            delete(ProjectMatrixDraftCellModel).where(
                ProjectMatrixDraftCellModel.project_matrix_draft_id == project_matrix_draft_id
            )
        )
        self._session.execute(
            delete(ProjectMatrixDraftGroupModel).where(
                ProjectMatrixDraftGroupModel.project_matrix_draft_id == project_matrix_draft_id
            )
        )
        self._session.execute(
            delete(ProjectMatrixDraftRowModel).where(
                ProjectMatrixDraftRowModel.project_matrix_draft_id == project_matrix_draft_id
            )
        )
        self._session.delete(record_row)
        self._session.flush()
        return True

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

    def replace_step_quantities(
        self,
        project_matrix_draft_id: str,
        quantities: tuple[ProjectMatrixDraftStepQuantity, ...],
    ) -> tuple[ProjectMatrixDraftStepQuantity, ...]:
        """Replace all Step quantity records for one Matrix draft."""
        self._session.execute(
            delete(ProjectMatrixDraftStepQuantityModel).where(
                ProjectMatrixDraftStepQuantityModel.project_matrix_draft_id
                == project_matrix_draft_id
            )
        )
        self._session.add_all(_to_step_quantity_models(quantities))
        self._session.flush()
        return quantities

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
        pre_test_buffer_days=record.pre_test_buffer_days,
        post_test_buffer_days=record.post_test_buffer_days,
        sample_received_date=record.sample_received_date,
        planned_test_start_date=record.planned_test_start_date,
        planned_test_complete_date=record.planned_test_complete_date,
        estimated_completion_date=record.estimated_completion_date,
        method_sync_context_json=record.method_sync_context_json,
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
            day_expression=row.day_expression,
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


def _to_step_quantity_models(
    quantities: tuple[ProjectMatrixDraftStepQuantity, ...],
) -> list[ProjectMatrixDraftStepQuantityModel]:
    return [
        ProjectMatrixDraftStepQuantityModel(
            draft_step_quantity_id=quantity.draft_step_quantity_id,
            project_matrix_draft_id=quantity.project_matrix_draft_id,
            draft_group_id=quantity.draft_group_id,
            draft_row_id=quantity.draft_row_id,
            step_sequence=quantity.step_sequence,
            step_suffix_note=_suffix_identity_value(quantity.step_suffix_note),
            raw_token=quantity.raw_token,
            test_points_per_sample=quantity.test_points_per_sample,
            readings_per_point=quantity.readings_per_point,
            contact_points_per_sample=quantity.contact_points_per_sample,
            source=quantity.source,
            review_required=quantity.review_required,
            review_reason=quantity.review_reason,
            contact_plan_json=contact_plan_to_json(quantity.contact_plan),
            updated_at=quantity.updated_at,
        )
        for quantity in quantities
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
        pre_test_buffer_days=row.pre_test_buffer_days,
        post_test_buffer_days=row.post_test_buffer_days,
        sample_received_date=row.sample_received_date,
        planned_test_start_date=row.planned_test_start_date,
        planned_test_complete_date=row.planned_test_complete_date,
        estimated_completion_date=row.estimated_completion_date,
        method_sync_context_json=row.method_sync_context_json,
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
        day_expression=row.day_expression,
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


def _to_step_quantity_domain(
    row: ProjectMatrixDraftStepQuantityModel,
) -> ProjectMatrixDraftStepQuantity:
    return ProjectMatrixDraftStepQuantity(
        draft_step_quantity_id=row.draft_step_quantity_id,
        project_matrix_draft_id=row.project_matrix_draft_id,
        draft_group_id=row.draft_group_id,
        draft_row_id=row.draft_row_id,
        step_sequence=row.step_sequence,
        step_suffix_note=_optional_text(row.step_suffix_note),
        raw_token=row.raw_token,
        test_points_per_sample=row.test_points_per_sample,
        readings_per_point=row.readings_per_point,
        contact_points_per_sample=row.contact_points_per_sample,
        source=row.source,
        review_required=row.review_required,
        review_reason=row.review_reason,
        updated_at=row.updated_at,
        contact_plan=contact_plan_from_json(row.contact_plan_json),
    )


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _suffix_identity_value(value: str | None) -> str:
    return _optional_text(value) or ""
