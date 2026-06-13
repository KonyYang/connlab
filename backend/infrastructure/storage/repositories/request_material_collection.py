"""Repository for request-material collection records."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.application.project_request_material_collection_service import (
    ProjectRequestMaterialCollectionItemRecord,
    ProjectRequestMaterialCollectionRecord,
)
from backend.infrastructure.storage.models import (
    ProjectRequestMaterialCollectionItemModel,
    ProjectRequestMaterialCollectionModel,
)


class ProjectRequestMaterialCollectionRepository:
    """Persist and load request-material collection runs."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def save_collection(
        self,
        collection: ProjectRequestMaterialCollectionRecord,
        items: tuple[ProjectRequestMaterialCollectionItemRecord, ...],
    ) -> ProjectRequestMaterialCollectionRecord:
        """Persist a collection run and its item rows."""
        self._session.add(_collection_to_model(collection))
        for item in items:
            self._session.add(_item_to_model(item))
        self._session.flush()
        return collection

    def latest_by_project(
        self,
        project_id: str,
    ) -> ProjectRequestMaterialCollectionRecord | None:
        """Return the latest collection run for a project."""
        row = self._session.scalar(
            select(ProjectRequestMaterialCollectionModel)
            .where(ProjectRequestMaterialCollectionModel.project_id == project_id)
            .order_by(ProjectRequestMaterialCollectionModel.created_at.desc())
            .limit(1)
        )
        return _collection_to_domain(row) if row else None

    def list_items(
        self,
        collection_id: str,
    ) -> tuple[ProjectRequestMaterialCollectionItemRecord, ...]:
        """Return persisted items for a collection run."""
        rows = self._session.scalars(
            select(ProjectRequestMaterialCollectionItemModel)
            .where(ProjectRequestMaterialCollectionItemModel.collection_id == collection_id)
            .order_by(ProjectRequestMaterialCollectionItemModel.item_id)
        ).all()
        return tuple(_item_to_domain(row) for row in rows)


def _collection_to_model(
    record: ProjectRequestMaterialCollectionRecord,
) -> ProjectRequestMaterialCollectionModel:
    """Convert a collection record into an ORM row."""
    return ProjectRequestMaterialCollectionModel(
        collection_id=record.collection_id,
        project_id=record.project_id,
        workspace_id=record.workspace_id,
        status=record.status,
        item_count=record.item_count,
        copied_count=record.copied_count,
        already_present_count=record.already_present_count,
        conflict_count=record.conflict_count,
        skipped_count=record.skipped_count,
        missing_source_count=record.missing_source_count,
        created_at=record.created_at,
        updated_at=record.updated_at,
        warnings_json=json.dumps(list(record.warnings)),
    )


def _collection_to_domain(
    row: ProjectRequestMaterialCollectionModel,
) -> ProjectRequestMaterialCollectionRecord:
    """Convert an ORM row into a collection record."""
    return ProjectRequestMaterialCollectionRecord(
        collection_id=row.collection_id,
        project_id=row.project_id,
        workspace_id=row.workspace_id,
        status=row.status,
        item_count=row.item_count,
        copied_count=row.copied_count,
        already_present_count=row.already_present_count,
        conflict_count=row.conflict_count,
        skipped_count=row.skipped_count,
        missing_source_count=row.missing_source_count,
        created_at=row.created_at,
        updated_at=row.updated_at,
        warnings=tuple(json.loads(row.warnings_json or "[]")),
    )


def _item_to_model(
    record: ProjectRequestMaterialCollectionItemRecord,
) -> ProjectRequestMaterialCollectionItemModel:
    """Convert a collection item into an ORM row."""
    return ProjectRequestMaterialCollectionItemModel(
        item_id=record.item_id,
        collection_id=record.collection_id,
        project_id=record.project_id,
        source_asset_id=record.source_asset_id,
        source_asset_type=record.source_asset_type,
        source_role=record.source_role,
        dedupe_key=record.dedupe_key,
        source_path=str(record.source_path),
        original_name=record.original_name,
        target_area=record.target_area,
        target_path=str(record.target_path),
        status=record.status,
        action=record.action,
        review_required=record.review_required,
        size_bytes=record.size_bytes,
        sha256=record.sha256,
    )


def _item_to_domain(
    row: ProjectRequestMaterialCollectionItemModel,
) -> ProjectRequestMaterialCollectionItemRecord:
    """Convert an ORM row into a collection item."""
    return ProjectRequestMaterialCollectionItemRecord(
        item_id=row.item_id,
        collection_id=row.collection_id,
        project_id=row.project_id,
        source_asset_id=row.source_asset_id,
        source_asset_type=row.source_asset_type,
        source_role=row.source_role,
        dedupe_key=row.dedupe_key,
        source_path=Path(row.source_path),
        original_name=row.original_name,
        target_area=row.target_area,
        target_path=Path(row.target_path),
        status=row.status,
        action=row.action,
        review_required=row.review_required,
        size_bytes=row.size_bytes,
        sha256=row.sha256,
    )
