"""Repository for temporary project planning context."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain import ProjectTemporaryContext
from backend.infrastructure.storage.models import ProjectTemporaryContextModel


class ProjectTemporaryContextRepository:
    """Persist and load planning-only context for no-LTR projects."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, context: ProjectTemporaryContext) -> ProjectTemporaryContext:
        """Persist a new temporary project context."""
        self._session.add(_to_model(context))
        self._session.flush()
        return context

    def get_by_project(self, project_id: str) -> ProjectTemporaryContext | None:
        """Return temporary context by project id."""
        row = self._session.scalar(
            select(ProjectTemporaryContextModel).where(
                ProjectTemporaryContextModel.project_id == project_id
            )
        )
        return _to_domain(row) if row else None

    def delete_by_project(self, project_id: str) -> bool:
        """Delete temporary context by project id when one exists."""
        row = self._session.scalar(
            select(ProjectTemporaryContextModel).where(
                ProjectTemporaryContextModel.project_id == project_id
            )
        )
        if row is None:
            return False
        self._session.delete(row)
        self._session.flush()
        return True


def _to_model(context: ProjectTemporaryContext) -> ProjectTemporaryContextModel:
    return ProjectTemporaryContextModel(
        context_id=context.context_id,
        project_id=context.project_id,
        request_summary=context.request_summary,
        sample_description=context.sample_description,
        test_item=context.test_item,
        notes=context.notes,
        source_asset_ids_json=json.dumps(list(context.source_asset_ids), sort_keys=True),
    )


def _to_domain(row: ProjectTemporaryContextModel) -> ProjectTemporaryContext:
    return ProjectTemporaryContext(
        context_id=row.context_id,
        project_id=row.project_id,
        request_summary=row.request_summary,
        sample_description=row.sample_description,
        test_item=row.test_item,
        notes=row.notes,
        source_asset_ids=_source_asset_ids(row.source_asset_ids_json),
    )


def _source_asset_ids(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    try:
        parsed: Any = json.loads(value)
    except (TypeError, ValueError):
        return ()
    if not isinstance(parsed, list):
        return ()
    return tuple(item.strip() for item in parsed if isinstance(item, str) and item.strip())
