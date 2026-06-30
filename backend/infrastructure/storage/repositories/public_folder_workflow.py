"""Repository for TASK_346C public folder workflow state and audit records."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.application.public_folder_workflow_service import (
    PublicFolderWorkflowFileRecord,
    PublicFolderWorkflowOperationRecord,
    PublicFolderWorkflowState,
)
from backend.infrastructure.storage.models import (
    ProjectPublicFolderWorkflowFileRecordModel,
    ProjectPublicFolderWorkflowOperationModel,
    ProjectPublicFolderWorkflowStateModel,
)


class PublicFolderWorkflowRepository:
    """Persist public folder workflow state, file records, and operations."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def get_state(self, project_id: str) -> PublicFolderWorkflowState:
        """Return existing workflow state or a default record."""
        row = self._session.get(ProjectPublicFolderWorkflowStateModel, project_id)
        if row is None:
            return PublicFolderWorkflowState(project_id=project_id)
        return PublicFolderWorkflowState(
            project_id=row.project_id,
            auto_sync_enabled=row.auto_sync_enabled,
            sync_locked=row.sync_locked,
            submitted_at=row.submitted_at,
            submit_operation_id=row.submit_operation_id,
            last_sync_operation_id=row.last_sync_operation_id,
            last_pull_operation_id=row.last_pull_operation_id,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def save_state(self, state: PublicFolderWorkflowState) -> PublicFolderWorkflowState:
        """Create or update workflow state."""
        row = self._session.get(ProjectPublicFolderWorkflowStateModel, state.project_id)
        if row is None:
            self._session.add(
                ProjectPublicFolderWorkflowStateModel(
                    project_id=state.project_id,
                    auto_sync_enabled=state.auto_sync_enabled,
                    sync_locked=state.sync_locked,
                    submitted_at=state.submitted_at,
                    submit_operation_id=state.submit_operation_id,
                    last_sync_operation_id=state.last_sync_operation_id,
                    last_pull_operation_id=state.last_pull_operation_id,
                    created_at=state.created_at,
                    updated_at=state.updated_at,
                )
            )
        else:
            row.auto_sync_enabled = state.auto_sync_enabled
            row.sync_locked = state.sync_locked
            row.submitted_at = state.submitted_at
            row.submit_operation_id = state.submit_operation_id
            row.last_sync_operation_id = state.last_sync_operation_id
            row.last_pull_operation_id = state.last_pull_operation_id
            row.created_at = state.created_at
            row.updated_at = state.updated_at
        self._session.flush()
        return state

    def get_file(
        self,
        project_id: str,
        relative_path: Path,
    ) -> PublicFolderWorkflowFileRecord | None:
        """Return a managed workflow file record."""
        row = self._session.get(
            ProjectPublicFolderWorkflowFileRecordModel,
            (project_id, relative_path.as_posix()),
        )
        return _file_to_domain(row) if row else None

    def save_file(
        self,
        record: PublicFolderWorkflowFileRecord,
    ) -> PublicFolderWorkflowFileRecord:
        """Create or update a managed workflow file record."""
        row = self._session.get(
            ProjectPublicFolderWorkflowFileRecordModel,
            (record.project_id, record.relative_path.as_posix()),
        )
        if row is None:
            self._session.add(
                ProjectPublicFolderWorkflowFileRecordModel(
                    project_id=record.project_id,
                    relative_path=record.relative_path.as_posix(),
                    public_path=str(record.public_path),
                    local_fingerprint=record.local_fingerprint,
                    public_fingerprint=record.public_fingerprint,
                    updated_at=record.updated_at,
                    operation_id=record.operation_id,
                )
            )
        else:
            row.public_path = str(record.public_path)
            row.local_fingerprint = record.local_fingerprint
            row.public_fingerprint = record.public_fingerprint
            row.updated_at = record.updated_at
            row.operation_id = record.operation_id
        self._session.flush()
        return record

    def rebase_files(
        self,
        *,
        project_id: str,
        old_root: Path,
        new_root: Path,
        operation_id: str,
        updated_at: str,
    ) -> None:
        """Update public paths after a safe Open-to-Closed move."""
        rows = self._session.scalars(
            select(ProjectPublicFolderWorkflowFileRecordModel).where(
                ProjectPublicFolderWorkflowFileRecordModel.project_id == project_id
            )
        ).all()
        for row in rows:
            public_path = Path(row.public_path)
            try:
                relative = public_path.relative_to(old_root)
            except ValueError:
                continue
            row.public_path = str(new_root / relative)
            row.operation_id = operation_id
            row.updated_at = updated_at
        self._session.flush()

    def save_operation(
        self,
        record: PublicFolderWorkflowOperationRecord,
    ) -> PublicFolderWorkflowOperationRecord:
        """Persist one workflow operation audit row."""
        self._session.add(
            ProjectPublicFolderWorkflowOperationModel(
                operation_id=record.operation_id,
                project_id=record.project_id,
                operation_type=record.operation_type,
                status=record.status,
                preview_hash=record.preview_hash,
                requested_at=record.requested_at,
                started_at=record.started_at,
                completed_at=record.completed_at,
                operator=record.operator,
                public_root=_path(record.public_root),
                public_root_class=record.public_root_class,
                public_folder_year=record.public_folder_year,
                year_source=record.year_source,
                local_official_folder_path=_path(record.local_official_folder_path),
                public_open_path=_path(record.public_open_path),
                public_closed_path=_path(record.public_closed_path),
                target_path=_path(record.target_path),
                counts_json=json.dumps(record.counts, sort_keys=True),
                blockers_json=json.dumps(list(record.blockers)),
                warnings_json=json.dumps(list(record.warnings)),
                conflicts_json=json.dumps(list(record.conflicts)),
                snapshot_json=record.snapshot_json,
                metadata_json=record.metadata_json,
            )
        )
        self._session.flush()
        return record


def _file_to_domain(
    row: ProjectPublicFolderWorkflowFileRecordModel,
) -> PublicFolderWorkflowFileRecord:
    return PublicFolderWorkflowFileRecord(
        project_id=row.project_id,
        relative_path=Path(row.relative_path),
        public_path=Path(row.public_path),
        local_fingerprint=row.local_fingerprint,
        public_fingerprint=row.public_fingerprint,
        updated_at=row.updated_at,
        operation_id=row.operation_id,
    )


def _path(path: Path | None) -> str | None:
    return str(path) if path is not None else None
