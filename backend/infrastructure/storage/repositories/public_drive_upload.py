"""Repository for public-drive upload file records."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.application.public_drive_upload_service import PublicDriveUploadFileRecord
from backend.infrastructure.storage.models import PublicDriveUploadFileRecordModel


class PublicDriveUploadRepository:
    """Persist ConnLab-managed public-drive uploaded file state."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def get_file(
        self,
        project_id: str,
        relative_path: Path,
    ) -> PublicDriveUploadFileRecord | None:
        """Return the previous upload record for a project file."""
        row = self._session.scalar(
            select(PublicDriveUploadFileRecordModel).where(
                PublicDriveUploadFileRecordModel.project_id == project_id,
                PublicDriveUploadFileRecordModel.relative_path == relative_path.as_posix(),
            )
        )
        return _to_domain(row) if row else None

    def save_file(
        self,
        record: PublicDriveUploadFileRecord,
    ) -> PublicDriveUploadFileRecord:
        """Create or update one public-drive upload file record."""
        row = self._session.scalar(
            select(PublicDriveUploadFileRecordModel).where(
                PublicDriveUploadFileRecordModel.project_id == record.project_id,
                PublicDriveUploadFileRecordModel.relative_path
                == record.relative_path.as_posix(),
            )
        )
        if row is None:
            self._session.add(_to_model(record))
        else:
            row.public_path = str(record.public_path)
            row.local_fingerprint = record.local_fingerprint
            row.public_fingerprint = record.public_fingerprint
            row.uploaded_at = record.uploaded_at
            row.operation_id = record.operation_id
        self._session.flush()
        return record


def _to_model(record: PublicDriveUploadFileRecord) -> PublicDriveUploadFileRecordModel:
    """Convert an upload file record into an ORM row."""
    return PublicDriveUploadFileRecordModel(
        project_id=record.project_id,
        relative_path=record.relative_path.as_posix(),
        public_path=str(record.public_path),
        local_fingerprint=record.local_fingerprint,
        public_fingerprint=record.public_fingerprint,
        uploaded_at=record.uploaded_at,
        operation_id=record.operation_id,
    )


def _to_domain(row: PublicDriveUploadFileRecordModel) -> PublicDriveUploadFileRecord:
    """Convert an ORM row into an upload file record."""
    return PublicDriveUploadFileRecord(
        project_id=row.project_id,
        relative_path=Path(row.relative_path),
        public_path=Path(row.public_path),
        local_fingerprint=row.local_fingerprint,
        public_fingerprint=row.public_fingerprint,
        uploaded_at=row.uploaded_at,
        operation_id=row.operation_id,
    )
