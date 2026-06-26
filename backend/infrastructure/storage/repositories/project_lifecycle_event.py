"""Repository for project lifecycle event records."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain import (
    ProjectClosureType,
    ProjectLifecycleEvent,
    ProjectLifecycleEventType,
    ProjectLifecycleState,
)
from backend.infrastructure.storage.models import ProjectLifecycleEventModel


class ProjectLifecycleEventRepository:
    """Persist and load project lifecycle transition events."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, event: ProjectLifecycleEvent) -> ProjectLifecycleEvent:
        """Persist a new lifecycle event."""
        self._session.add(_to_model(event))
        self._session.flush()
        return event

    def list_by_project(self, project_id: str) -> list[ProjectLifecycleEvent]:
        """Return lifecycle events for one project ordered by creation."""
        rows = self._session.scalars(
            select(ProjectLifecycleEventModel)
            .where(ProjectLifecycleEventModel.project_id == project_id)
            .order_by(
                ProjectLifecycleEventModel.created_at,
                ProjectLifecycleEventModel.event_id,
            )
        ).all()
        return [_to_domain(row) for row in rows]


def _to_model(event: ProjectLifecycleEvent) -> ProjectLifecycleEventModel:
    """Convert a lifecycle event domain record to an ORM row."""
    return ProjectLifecycleEventModel(
        event_id=event.event_id,
        project_id=event.project_id,
        event_type=event.event_type.value,
        previous_lifecycle_state=event.previous_lifecycle_state.value,
        new_lifecycle_state=event.new_lifecycle_state.value,
        previous_closure_type=(
            event.previous_closure_type.value if event.previous_closure_type else None
        ),
        new_closure_type=event.new_closure_type.value if event.new_closure_type else None,
        reason=event.reason,
        operator=event.operator,
        created_at=event.created_at,
        metadata_json=event.metadata_json,
    )


def _to_domain(row: ProjectLifecycleEventModel) -> ProjectLifecycleEvent:
    """Convert a lifecycle event ORM row to a domain record."""
    return ProjectLifecycleEvent(
        event_id=row.event_id,
        project_id=row.project_id,
        event_type=ProjectLifecycleEventType(row.event_type),
        previous_lifecycle_state=ProjectLifecycleState(row.previous_lifecycle_state),
        new_lifecycle_state=ProjectLifecycleState(row.new_lifecycle_state),
        previous_closure_type=(
            ProjectClosureType(row.previous_closure_type)
            if row.previous_closure_type
            else None
        ),
        new_closure_type=(
            ProjectClosureType(row.new_closure_type) if row.new_closure_type else None
        ),
        reason=row.reason,
        operator=row.operator,
        created_at=row.created_at,
        metadata_json=row.metadata_json,
    )
