"""Repository for local official project workspace records."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.infrastructure.files.recoverable_output_publisher import file_hash
from backend.infrastructure.official_workspace_manifest import OfficialWorkspaceManifestGateway, stable_folder_identity
from backend.infrastructure.storage.models import (
    FileAssetModel, ProjectFolderRecordModel, ProjectOfficialWorkspaceRecordModel,
    ProjectRequestMaterialCollectionModel, ProjectRequestMaterialCollectionItemModel,
)
from backend.infrastructure.storage.repositories.project_output_record import ProjectOutputRecordRepository


class ProjectOfficialWorkspaceRepository:
    """Persist and load local official project workspace records."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        """Return the workspace record for a project when one exists."""
        row = self._session.scalar(
            select(ProjectOfficialWorkspaceRecordModel).where(
                ProjectOfficialWorkspaceRecordModel.project_id == project_id
            )
        )
        return _to_domain(row) if row else None

    def save(self, record: OfficialWorkspaceRecord) -> OfficialWorkspaceRecord:
        """Create or update the workspace record for a project."""
        row = self._session.scalar(
            select(ProjectOfficialWorkspaceRecordModel).where(
                ProjectOfficialWorkspaceRecordModel.project_id == record.project_id
            )
        )
        if row is None:
            self._session.add(_to_model(record))
        else:
            row.workspace_id = record.workspace_id
            row.dl_number = record.dl_number
            row.local_workspace_path = str(record.local_workspace_path)
            row.source_book_path = str(record.source_book_path)
            row.official_folder_path = str(record.official_folder_path)
            row.manifest_path = str(record.manifest_path)
            row.template_source_path = str(record.template_source_path)
            row.created_at = record.created_at
        self._session.flush()
        return record

    def preflight_placed_materials(
        self, record: OfficialWorkspaceRecord, *, source: Path,
    ) -> None:
        """Verify live collection targets before a physical folder move."""
        latest_collection = self._session.scalar(
            select(ProjectRequestMaterialCollectionModel)
            .where(ProjectRequestMaterialCollectionModel.project_id == record.project_id)
            .order_by(ProjectRequestMaterialCollectionModel.created_at.desc())
            .limit(1)
        )
        if latest_collection is None:
            return
        for item in self._session.scalars(
            select(ProjectRequestMaterialCollectionItemModel).where(
                ProjectRequestMaterialCollectionItemModel.collection_id == latest_collection.collection_id
            )
        ).all():
            if item.status not in {"copied", "already_present"}:
                continue
            old_target = Path(item.target_path)
            if not old_target.is_relative_to(record.official_folder_path):
                continue
            current = source / old_target.relative_to(record.official_folder_path)
            if item.sha256 is None:
                raise ValueError("Latest request-material target has no fingerprint; review before relocation.")
            self._require_regular_relocated_file(current, source, item.sha256)
            if item.size_bytes is not None and current.stat().st_size != item.size_bytes:
                raise ValueError("Latest request-material target size changed before relocation.")

    def publish_relocation(
        self, record: OfficialWorkspaceRecord, *, source: Path, target: Path,
        operation_id: str, expected_identity: list[int],
    ) -> OfficialWorkspaceRecord:
        """Commit live file references after a proven same-directory move."""
        row = self._session.scalar(
            select(ProjectOfficialWorkspaceRecordModel).where(
                ProjectOfficialWorkspaceRecordModel.project_id == record.project_id
            )
        )
        if row is None:
            raise ValueError("Official workspace index disappeared during relocation.")
        if row.official_folder_path == str(target):
            if stable_folder_identity(target) != expected_identity:
                raise ValueError("Relocated folder identity changed before commit.")
            return _to_domain(row)
        if (row.official_folder_path != str(source) or not target.is_dir() or source.exists()
                or stable_folder_identity(target) != expected_identity):
            raise ValueError("Official workspace index or folder changed during relocation.")
        try:
            for asset in self._session.scalars(
                select(FileAssetModel).where(FileAssetModel.project_id == record.project_id)
            ).all():
                old = Path(asset.path)
                if not old.is_relative_to(source):
                    continue
                new = target / old.relative_to(source)
                self._reject_redirected_relocated_path(new, target)
                if asset.sha256 is not None and file_hash(new) == asset.sha256:
                    asset.path = str(new)
                # A changed or removed operator file is not a verified asset.
                # Retain its stale index path rather than bind it to different bytes.
            for folder in self._session.scalars(
                select(ProjectFolderRecordModel).where(ProjectFolderRecordModel.project_id == record.project_id)
            ).all():
                old = Path(folder.folder_path)
                if not old.is_relative_to(source):
                    continue
                new = target / old.relative_to(source)
                self._reject_redirected_relocated_path(new, target)
                if new.is_dir():
                    folder.folder_path = str(new)
                # Deleted child directories remain stale records, not live links.
            latest_collection = self._session.scalar(
                select(ProjectRequestMaterialCollectionModel)
                .where(ProjectRequestMaterialCollectionModel.project_id == record.project_id)
                .order_by(ProjectRequestMaterialCollectionModel.created_at.desc())
                .limit(1)
            )
            if latest_collection is not None:
                for item in self._session.scalars(
                    select(ProjectRequestMaterialCollectionItemModel).where(
                        ProjectRequestMaterialCollectionItemModel.collection_id == latest_collection.collection_id
                    )
                ).all():
                    # Planned/skipped rows describe decisions, not files to rebind.
                    if item.status not in {"copied", "already_present"}:
                        continue
                    old_target = Path(item.target_path)
                    if not old_target.is_relative_to(source):
                        continue
                    new_target = target / old_target.relative_to(source)
                    if item.sha256 is None:
                        raise ValueError("Latest request-material target has no fingerprint; review before relocation.")
                    self._require_regular_relocated_file(new_target, target, item.sha256)
                    if item.size_bytes is not None and new_target.stat().st_size != item.size_bytes:
                        raise ValueError("Latest request-material target size changed after relocation.")
                    item.target_path = str(new_target)
            ProjectOutputRecordRepository(self._session).append_verified_relocations(
                record.project_id, source=source, target=target, operation_id=operation_id,
            )
            if stable_folder_identity(target) != expected_identity:
                raise ValueError("Relocated folder identity changed before database commit.")
            row.official_folder_path = str(target)
            self._session.commit()
        except BaseException:
            self._session.rollback()
            raise
        return _to_domain(row)

    @staticmethod
    def _require_regular_relocated_file(
        path: Path, target: Path, expected_hash: str | None
    ) -> None:
        ProjectOfficialWorkspaceRepository._reject_redirected_relocated_path(path, target)
        digest = file_hash(path)
        if digest is None or expected_hash is not None and digest != expected_hash:
            raise ValueError("Registered project file is missing or changed after relocation.")

    @staticmethod
    def _reject_redirected_relocated_path(path: Path, target: Path) -> None:
        if OfficialWorkspaceManifestGateway.first_redirected_path(
            *[part for part in (path, *path.parents)
              if part == target or part.is_relative_to(target)]
        ) is not None:
            raise ValueError("Registered file path redirects through a link or junction.")


def _to_model(record: OfficialWorkspaceRecord) -> ProjectOfficialWorkspaceRecordModel:
    """Convert a domain-like record to an ORM row."""
    return ProjectOfficialWorkspaceRecordModel(
        workspace_id=record.workspace_id,
        project_id=record.project_id,
        dl_number=record.dl_number,
        local_workspace_path=str(record.local_workspace_path),
        source_book_path=str(record.source_book_path),
        official_folder_path=str(record.official_folder_path),
        manifest_path=str(record.manifest_path),
        template_source_path=str(record.template_source_path),
        created_at=record.created_at,
    )


def _to_domain(row: ProjectOfficialWorkspaceRecordModel) -> OfficialWorkspaceRecord:
    """Convert an ORM row to a domain-like record."""
    return OfficialWorkspaceRecord(
        workspace_id=row.workspace_id,
        project_id=row.project_id,
        dl_number=row.dl_number,
        local_workspace_path=Path(row.local_workspace_path),
        source_book_path=Path(row.source_book_path),
        official_folder_path=Path(row.official_folder_path),
        manifest_path=Path(row.manifest_path),
        template_source_path=Path(row.template_source_path),
        created_at=row.created_at,
    )
