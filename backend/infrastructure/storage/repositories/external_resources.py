"""Repository for external resource registry records."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ExternalResourceValidationStatus,
)
from backend.infrastructure.storage.models import ExternalResourceModel


class ExternalResourceRepository:
    """Persist and load external resource registry entries."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def list_all(self) -> list[ExternalResource]:
        """Return all registered external resources ordered by type."""
        rows = self._session.scalars(
            select(ExternalResourceModel).order_by(ExternalResourceModel.resource_type)
        ).all()
        return [_to_domain(row) for row in rows]

    def get_by_type(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource | None:
        """Return one resource by type, or None when missing."""
        row = self._session.scalar(
            select(ExternalResourceModel).where(
                ExternalResourceModel.resource_type == resource_type.value
            )
        )
        return _to_domain(row) if row else None

    def upsert(self, resource: ExternalResource) -> ExternalResource:
        """Create or update a resource by resource type."""
        row = self._session.scalar(
            select(ExternalResourceModel).where(
                ExternalResourceModel.resource_type == resource.resource_type.value
            )
        )
        if row is None:
            self._session.add(_to_model(resource))
        else:
            row.path = str(resource.path)
            row.active = resource.active
            row.validation_status = resource.validation_status.value
            row.last_validated_at = resource.last_validated_at
            row.validation_failure_reason = resource.validation_failure_reason
            row.worksheet_name = resource.worksheet_name
        self._session.flush()
        return resource


def _to_model(resource: ExternalResource) -> ExternalResourceModel:
    """Convert a domain resource into an ORM row."""
    return ExternalResourceModel(
        resource_id=resource.resource_id,
        resource_type=resource.resource_type.value,
        path=str(resource.path),
        active=resource.active,
        validation_status=resource.validation_status.value,
        last_validated_at=resource.last_validated_at,
        validation_failure_reason=resource.validation_failure_reason,
        worksheet_name=resource.worksheet_name,
    )


def _to_domain(row: ExternalResourceModel) -> ExternalResource:
    """Convert an ORM row into a domain resource."""
    return ExternalResource(
        resource_id=row.resource_id,
        resource_type=ExternalResourceType(row.resource_type),
        path=Path(row.path),
        active=row.active,
        validation_status=ExternalResourceValidationStatus(row.validation_status),
        last_validated_at=row.last_validated_at,
        validation_failure_reason=row.validation_failure_reason,
        worksheet_name=row.worksheet_name,
    )
