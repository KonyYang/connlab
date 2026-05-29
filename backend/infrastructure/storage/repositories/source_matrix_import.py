"""Repository for Source Matrix import snapshots."""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain import (
    SourceMatrixCellSnapshot,
    SourceMatrixGroupSnapshot,
    SourceMatrixImportRecord,
    SourceMatrixImportStatus,
    SourceMatrixRowSnapshot,
    SourceMatrixSnapshot,
)
from backend.infrastructure.storage.models_matrix_source import (
    SourceMatrixCellSnapshotModel,
    SourceMatrixGroupSnapshotModel,
    SourceMatrixImportRecordModel,
    SourceMatrixRowSnapshotModel,
    SourceMatrixSnapshotModel,
)


class SourceMatrixImportRepository:
    """Persist and load Source Matrix import records and snapshots."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_import_snapshot(
        self,
        import_record: SourceMatrixImportRecord,
        snapshot: SourceMatrixSnapshot,
    ) -> None:
        """Persist one immutable Source Matrix import snapshot atomically in one session."""
        self._session.add(_to_import_model(import_record))
        self._session.add(_to_snapshot_model(snapshot))
        self._session.add_all(_to_row_models(snapshot))
        self._session.add_all(_to_group_models(snapshot))
        self._session.add_all(_to_cell_models(snapshot))
        self._session.flush()

    def get_import(self, import_id: str) -> SourceMatrixImportRecord | None:
        """Return one import metadata record by id."""
        row = self._session.get(SourceMatrixImportRecordModel, import_id)
        return _to_import_domain(row) if row else None

    def get_snapshot_by_import(self, import_id: str) -> SourceMatrixSnapshot | None:
        """Return one snapshot body by import id."""
        snapshot_row = self._session.scalar(
            select(SourceMatrixSnapshotModel).where(
                SourceMatrixSnapshotModel.import_id == import_id
            )
        )
        if snapshot_row is None:
            return None
        row_rows = self._session.scalars(
            select(SourceMatrixRowSnapshotModel)
            .where(SourceMatrixRowSnapshotModel.snapshot_id == snapshot_row.snapshot_id)
            .order_by(SourceMatrixRowSnapshotModel.row_order.asc())
        ).all()
        group_rows = self._session.scalars(
            select(SourceMatrixGroupSnapshotModel)
            .where(SourceMatrixGroupSnapshotModel.snapshot_id == snapshot_row.snapshot_id)
            .order_by(SourceMatrixGroupSnapshotModel.group_order.asc())
        ).all()
        cell_rows = self._session.scalars(
            select(SourceMatrixCellSnapshotModel)
            .where(SourceMatrixCellSnapshotModel.snapshot_id == snapshot_row.snapshot_id)
            .order_by(SourceMatrixCellSnapshotModel.cell_snapshot_id.asc())
        ).all()
        return SourceMatrixSnapshot(
            snapshot_id=snapshot_row.snapshot_id,
            import_id=snapshot_row.import_id,
            project_id=snapshot_row.project_id,
            source_table_index=snapshot_row.source_table_index,
            rows=tuple(_to_row_domain(row) for row in row_rows),
            groups=tuple(_to_group_domain(group) for group in group_rows),
            cells=tuple(_to_cell_domain(cell) for cell in cell_rows),
            created_at=snapshot_row.created_at,
        )

    def get_snapshot(self, snapshot_id: str) -> SourceMatrixSnapshot | None:
        """Return one snapshot body by snapshot id."""
        snapshot_row = self._session.get(SourceMatrixSnapshotModel, snapshot_id)
        if snapshot_row is None:
            return None
        row_rows = self._session.scalars(
            select(SourceMatrixRowSnapshotModel)
            .where(SourceMatrixRowSnapshotModel.snapshot_id == snapshot_row.snapshot_id)
            .order_by(SourceMatrixRowSnapshotModel.row_order.asc())
        ).all()
        group_rows = self._session.scalars(
            select(SourceMatrixGroupSnapshotModel)
            .where(SourceMatrixGroupSnapshotModel.snapshot_id == snapshot_row.snapshot_id)
            .order_by(SourceMatrixGroupSnapshotModel.group_order.asc())
        ).all()
        cell_rows = self._session.scalars(
            select(SourceMatrixCellSnapshotModel)
            .where(SourceMatrixCellSnapshotModel.snapshot_id == snapshot_row.snapshot_id)
            .order_by(SourceMatrixCellSnapshotModel.cell_snapshot_id.asc())
        ).all()
        return SourceMatrixSnapshot(
            snapshot_id=snapshot_row.snapshot_id,
            import_id=snapshot_row.import_id,
            project_id=snapshot_row.project_id,
            source_table_index=snapshot_row.source_table_index,
            rows=tuple(_to_row_domain(row) for row in row_rows),
            groups=tuple(_to_group_domain(group) for group in group_rows),
            cells=tuple(_to_cell_domain(cell) for cell in cell_rows),
            created_at=snapshot_row.created_at,
        )

    def list_imports_by_project(self, project_id: str) -> list[SourceMatrixImportRecord]:
        """Return Source Matrix imports by project, newest first."""
        rows = self._session.scalars(
            select(SourceMatrixImportRecordModel)
            .where(SourceMatrixImportRecordModel.project_id == project_id)
            .order_by(SourceMatrixImportRecordModel.created_at.desc())
        ).all()
        return [_to_import_domain(row) for row in rows]

    def get_import_by_project_and_fingerprint(
        self,
        *,
        project_id: str,
        task261_commit_fingerprint: str,
    ) -> SourceMatrixImportRecord | None:
        """Return one Source Matrix import by project and TASK_261 fingerprint."""
        row = self._session.scalar(
            select(SourceMatrixImportRecordModel).where(
                SourceMatrixImportRecordModel.project_id == project_id,
                SourceMatrixImportRecordModel.task261_commit_fingerprint
                == task261_commit_fingerprint,
            )
        )
        return _to_import_domain(row) if row else None


def _to_import_model(import_record: SourceMatrixImportRecord) -> SourceMatrixImportRecordModel:
    return SourceMatrixImportRecordModel(
        import_id=import_record.import_id,
        project_id=import_record.project_id,
        draft_id=import_record.draft_id,
        source_document_path=import_record.source_document_path,
        source_document_name=import_record.source_document_name,
        source_format=import_record.source_format,
        source_asset_id=import_record.source_asset_id,
        source_case_id=import_record.source_case_id,
        source_draft_id=import_record.source_draft_id,
        import_status=import_record.import_status.value,
        source_spec_number=import_record.source_spec_number,
        source_spec_revision=import_record.source_spec_revision,
        parse_time=import_record.parse_time,
        parser_version=import_record.parser_version,
        payload_schema_version=import_record.payload_schema_version,
        source_preview_payload_json=(
            json.dumps(import_record.source_preview_payload, ensure_ascii=False)
            if import_record.source_preview_payload is not None
            else None
        ),
        warnings_json=json.dumps(list(import_record.warnings), ensure_ascii=False),
        blockers_json=json.dumps(list(import_record.blockers), ensure_ascii=False),
        selected_group_keys_at_import_json=json.dumps(
            list(import_record.selected_group_keys_at_import),
            ensure_ascii=False,
        ),
        task261_commit_fingerprint=import_record.task261_commit_fingerprint,
        created_at=import_record.created_at,
    )


def _to_snapshot_model(snapshot: SourceMatrixSnapshot) -> SourceMatrixSnapshotModel:
    return SourceMatrixSnapshotModel(
        snapshot_id=snapshot.snapshot_id,
        import_id=snapshot.import_id,
        project_id=snapshot.project_id,
        source_table_index=snapshot.source_table_index,
        row_count=len(snapshot.rows),
        group_count=len(snapshot.groups),
        cell_count=len(snapshot.cells),
        created_at=snapshot.created_at,
    )


def _to_row_models(snapshot: SourceMatrixSnapshot) -> list[SourceMatrixRowSnapshotModel]:
    return [
        SourceMatrixRowSnapshotModel(
            row_snapshot_id=row.row_snapshot_id,
            snapshot_id=snapshot.snapshot_id,
            row_order=row.row_order,
            source_row_index=row.source_row_index,
            test_item=row.test_item,
            source_section=row.source_section,
            is_sample_row=row.is_sample_row,
        )
        for row in snapshot.rows
    ]


def _to_group_models(snapshot: SourceMatrixSnapshot) -> list[SourceMatrixGroupSnapshotModel]:
    return [
        SourceMatrixGroupSnapshotModel(
            group_snapshot_id=group.group_snapshot_id,
            snapshot_id=snapshot.snapshot_id,
            group_order=group.group_order,
            group_key=group.group_key,
            group_label=group.group_label,
            sample_size=group.sample_size,
            sample_quantity_expression=group.sample_quantity_expression,
            sample_note=group.sample_note,
        )
        for group in snapshot.groups
    ]


def _to_cell_models(snapshot: SourceMatrixSnapshot) -> list[SourceMatrixCellSnapshotModel]:
    return [
        SourceMatrixCellSnapshotModel(
            cell_snapshot_id=cell.cell_snapshot_id,
            snapshot_id=snapshot.snapshot_id,
            row_snapshot_id=cell.row_snapshot_id,
            group_snapshot_id=cell.group_snapshot_id,
            cell_value=cell.cell_value,
        )
        for cell in snapshot.cells
    ]


def _to_import_domain(row: SourceMatrixImportRecordModel) -> SourceMatrixImportRecord:
    return SourceMatrixImportRecord(
        import_id=row.import_id,
        project_id=row.project_id,
        draft_id=row.draft_id,
        source_document_path=row.source_document_path,
        source_document_name=row.source_document_name,
        source_format=row.source_format,
        source_asset_id=row.source_asset_id,
        source_case_id=row.source_case_id,
        source_draft_id=row.source_draft_id,
        import_status=SourceMatrixImportStatus(row.import_status),
        source_spec_number=row.source_spec_number,
        source_spec_revision=row.source_spec_revision,
        parse_time=row.parse_time,
        parser_version=row.parser_version,
        payload_schema_version=row.payload_schema_version,
        source_preview_payload=_loads_dict(row.source_preview_payload_json),
        warnings=tuple(_loads_string_list(row.warnings_json)),
        blockers=tuple(_loads_string_list(row.blockers_json)),
        selected_group_keys_at_import=tuple(
            _loads_string_list(row.selected_group_keys_at_import_json)
        ),
        task261_commit_fingerprint=row.task261_commit_fingerprint,
        created_at=row.created_at,
    )


def _to_row_domain(row: SourceMatrixRowSnapshotModel) -> SourceMatrixRowSnapshot:
    return SourceMatrixRowSnapshot(
        row_snapshot_id=row.row_snapshot_id,
        row_order=row.row_order,
        source_row_index=row.source_row_index,
        test_item=row.test_item,
        source_section=row.source_section,
        is_sample_row=row.is_sample_row,
    )


def _to_group_domain(row: SourceMatrixGroupSnapshotModel) -> SourceMatrixGroupSnapshot:
    return SourceMatrixGroupSnapshot(
        group_snapshot_id=row.group_snapshot_id,
        group_order=row.group_order,
        group_key=row.group_key,
        group_label=row.group_label,
        sample_size=row.sample_size,
        sample_quantity_expression=row.sample_quantity_expression,
        sample_note=row.sample_note,
    )


def _to_cell_domain(row: SourceMatrixCellSnapshotModel) -> SourceMatrixCellSnapshot:
    return SourceMatrixCellSnapshot(
        cell_snapshot_id=row.cell_snapshot_id,
        row_snapshot_id=row.row_snapshot_id,
        group_snapshot_id=row.group_snapshot_id,
        cell_value=row.cell_value,
    )


def _loads_string_list(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    result: list[str] = []
    for item in parsed:
        if isinstance(item, str):
            text = item.strip()
            if text:
                result.append(text)
    return result


def _loads_dict(value: str | None) -> dict | None:
    if not value:
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None
