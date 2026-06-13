"""Repositories for LTR, folder, and file asset records."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain import (
    FileAsset,
    FileAssetType,
    LtrRecord,
    LtrStatus,
    ProjectFolderRecord,
)
from backend.infrastructure.storage.models import (
    FileAssetModel,
    LtrRecordModel,
    ProjectFolderRecordModel,
)


class LtrRecordRepository:
    """Persist and load LTR records."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, ltr: LtrRecord) -> LtrRecord:
        """Persist a new LTR record."""
        self._session.add(_ltr_to_model(ltr))
        self._session.flush()
        return ltr

    def get(self, ltr_id: str) -> LtrRecord | None:
        """Return an LTR record by ID, or None when missing."""
        row = self._session.get(LtrRecordModel, ltr_id)
        return _ltr_to_domain(row) if row else None

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return LTR records for a project."""
        rows = self._session.scalars(_by_project(LtrRecordModel, project_id)).all()
        return [_ltr_to_domain(row) for row in rows]

    def list(self) -> list[LtrRecord]:
        """Return all LTR records ordered by LTR number."""
        rows = self._session.scalars(
            select(LtrRecordModel).order_by(LtrRecordModel.ltr_number)
        ).all()
        return [_ltr_to_domain(row) for row in rows]

    def search(self, query: str) -> list[LtrRecord]:
        """Search LTR records by LTR number or project ID."""
        pattern = f"%{query}%"
        rows = self._session.scalars(
            select(LtrRecordModel)
            .where(
                (LtrRecordModel.ltr_number.like(pattern))
                | (LtrRecordModel.project_id.like(pattern))
            )
            .order_by(LtrRecordModel.ltr_number)
        ).all()
        return [_ltr_to_domain(row) for row in rows]

    def update(self, ltr: LtrRecord) -> LtrRecord:
        """Update an existing LTR record."""
        row = self._session.get(LtrRecordModel, ltr.ltr_id)
        if row is None:
            raise ValueError(f"LTR record not found: {ltr.ltr_id}")
        row.project_id = ltr.project_id
        row.ltr_number = ltr.ltr_number
        row.status = ltr.status.value
        row.registered_on = ltr.registered_on
        row.requested_by = ltr.requested_by
        row.requested_date = ltr.requested_date
        row.notes = ltr.notes
        self._session.flush()
        return ltr


class ProjectFolderRecordRepository:
    """Persist and load project folder records."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, folder: ProjectFolderRecord) -> ProjectFolderRecord:
        """Persist a new project folder record."""
        self._session.add(_folder_to_model(folder))
        self._session.flush()
        return folder

    def get(self, folder_id: str) -> ProjectFolderRecord | None:
        """Return a folder record by ID, or None when missing."""
        row = self._session.get(ProjectFolderRecordModel, folder_id)
        return _folder_to_domain(row) if row else None

    def list_by_project(self, project_id: str) -> list[ProjectFolderRecord]:
        """Return folder records for a project."""
        rows = self._session.scalars(
            _by_project(ProjectFolderRecordModel, project_id)
        ).all()
        return [_folder_to_domain(row) for row in rows]

    def update(self, folder: ProjectFolderRecord) -> ProjectFolderRecord:
        """Update an existing project folder record."""
        row = self._session.get(ProjectFolderRecordModel, folder.folder_id)
        if row is None:
            raise ValueError(f"Project folder record not found: {folder.folder_id}")
        row.project_id = folder.project_id
        row.folder_path = str(folder.folder_path)
        row.created_on = folder.created_on
        self._session.flush()
        return folder


class FileAssetRepository:
    """Persist and load project file assets."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, asset: FileAsset) -> FileAsset:
        """Persist a new file asset."""
        self._session.add(_asset_to_model(asset))
        self._session.flush()
        return asset

    def get(self, asset_id: str) -> FileAsset | None:
        """Return a file asset by ID, or None when missing."""
        row = self._session.get(FileAssetModel, asset_id)
        return _asset_to_domain(row) if row else None

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        """Return file assets for a project."""
        rows = self._session.scalars(_by_project(FileAssetModel, project_id)).all()
        return [_asset_to_domain(row) for row in rows]

    def update(self, asset: FileAsset) -> FileAsset:
        """Update an existing file asset."""
        row = self._session.get(FileAssetModel, asset.asset_id)
        if row is None:
            raise ValueError(f"File asset not found: {asset.asset_id}")
        row.project_id = asset.project_id
        row.asset_type = asset.asset_type.value
        row.path = str(asset.path)
        row.original_name = asset.original_name
        row.registered_on = asset.registered_on
        row.source_package_id = asset.source_package_id
        row.source_intake_asset_id = asset.source_intake_asset_id
        row.source_role = asset.source_role
        row.sha256 = asset.sha256
        self._session.flush()
        return asset


ModelT = TypeVar(
    "ModelT",
    LtrRecordModel,
    ProjectFolderRecordModel,
    FileAssetModel,
)


def _by_project(model: type[ModelT], project_id: str):
    """Build a project-scoped select statement ordered by primary key."""
    primary_key = next(iter(model.__table__.primary_key.columns))
    return select(model).where(model.project_id == project_id).order_by(primary_key)


def _ltr_to_model(ltr: LtrRecord) -> LtrRecordModel:
    """Convert an LTR domain record to an ORM row."""
    return LtrRecordModel(
        ltr_id=ltr.ltr_id,
        project_id=ltr.project_id,
        ltr_number=ltr.ltr_number,
        status=ltr.status.value,
        registered_on=ltr.registered_on,
        requested_by=ltr.requested_by,
        requested_date=ltr.requested_date,
        notes=ltr.notes,
    )


def _ltr_to_domain(row: LtrRecordModel) -> LtrRecord:
    """Convert an LTR ORM row to a domain record."""
    return LtrRecord(
        ltr_id=row.ltr_id,
        project_id=row.project_id,
        ltr_number=row.ltr_number,
        status=LtrStatus(row.status),
        registered_on=row.registered_on,
        requested_by=row.requested_by,
        requested_date=row.requested_date,
        notes=row.notes,
    )


def _folder_to_model(folder: ProjectFolderRecord) -> ProjectFolderRecordModel:
    """Convert a folder domain record to an ORM row."""
    return ProjectFolderRecordModel(
        folder_id=folder.folder_id,
        project_id=folder.project_id,
        folder_path=str(folder.folder_path),
        created_on=folder.created_on,
    )


def _folder_to_domain(row: ProjectFolderRecordModel) -> ProjectFolderRecord:
    """Convert a folder ORM row to a domain record."""
    return ProjectFolderRecord(
        folder_id=row.folder_id,
        project_id=row.project_id,
        folder_path=Path(row.folder_path),
        created_on=row.created_on,
    )


def _asset_to_model(asset: FileAsset) -> FileAssetModel:
    """Convert a file asset domain record to an ORM row."""
    return FileAssetModel(
        asset_id=asset.asset_id,
        project_id=asset.project_id,
        asset_type=asset.asset_type.value,
        path=str(asset.path),
        original_name=asset.original_name,
        registered_on=asset.registered_on,
        source_package_id=asset.source_package_id,
        source_intake_asset_id=asset.source_intake_asset_id,
        source_role=asset.source_role,
        sha256=asset.sha256,
    )


def _asset_to_domain(row: FileAssetModel) -> FileAsset:
    """Convert a file asset ORM row to a domain record."""
    return FileAsset(
        asset_id=row.asset_id,
        project_id=row.project_id,
        asset_type=FileAssetType(row.asset_type),
        path=Path(row.path),
        original_name=row.original_name,
        registered_on=row.registered_on,
        source_package_id=row.source_package_id,
        source_intake_asset_id=row.source_intake_asset_id,
        source_role=row.source_role,
        sha256=row.sha256,
    )
