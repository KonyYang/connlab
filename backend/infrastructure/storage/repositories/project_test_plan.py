"""Repository for Project-stage test-plan draft snapshots."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain import ProjectTestPlanDraft, ProjectTestPlanDraftStatus
from backend.infrastructure.storage.models import ProjectTestPlanDraftModel


class ProjectTestPlanDraftRepository:
    """Persist and load Project test-plan draft snapshots."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, draft: ProjectTestPlanDraft) -> ProjectTestPlanDraft:
        """Persist a new draft snapshot."""
        self._session.add(_to_model(draft))
        self._session.flush()
        return draft

    def get(self, draft_id: str) -> ProjectTestPlanDraft | None:
        """Return a draft by id, or None when missing."""
        row = self._session.get(ProjectTestPlanDraftModel, draft_id)
        return _to_domain(row) if row else None

    def list_by_project(self, project_id: str) -> list[ProjectTestPlanDraft]:
        """Return draft snapshots for one Project."""
        rows = self._session.scalars(
            select(ProjectTestPlanDraftModel)
            .where(ProjectTestPlanDraftModel.project_id == project_id)
            .order_by(
                ProjectTestPlanDraftModel.source_document_path,
                ProjectTestPlanDraftModel.version.desc(),
                ProjectTestPlanDraftModel.updated_at.desc(),
            )
        ).all()
        return [_to_domain(row) for row in rows]

    def list_by_project_and_source(
        self,
        project_id: str,
        source_document_path: str,
    ) -> list[ProjectTestPlanDraft]:
        """Return draft snapshots for one Project/source pair."""
        rows = self._session.scalars(
            select(ProjectTestPlanDraftModel)
            .where(
                ProjectTestPlanDraftModel.project_id == project_id,
                ProjectTestPlanDraftModel.source_document_path == source_document_path,
            )
            .order_by(ProjectTestPlanDraftModel.version.desc())
        ).all()
        return [_to_domain(row) for row in rows]

    def update(self, draft: ProjectTestPlanDraft) -> ProjectTestPlanDraft:
        """Update an existing draft snapshot."""
        row = self._session.get(ProjectTestPlanDraftModel, draft.draft_id)
        if row is None:
            raise ValueError(f"Project test-plan draft not found: {draft.draft_id}")
        row.project_id = draft.project_id
        row.source_document_path = draft.source_document_path
        row.source_document_name = draft.source_document_name
        row.source_format = draft.source_format
        row.source_asset_id = draft.source_asset_id
        row.source_case_id = draft.source_case_id
        row.source_draft_id = draft.source_draft_id
        row.status = draft.status.value
        row.version = draft.version
        row.payload_json = draft.payload_json
        row.created_at = draft.created_at
        row.updated_at = draft.updated_at
        row.reviewed_at = draft.reviewed_at
        self._session.flush()
        return draft


def _to_model(draft: ProjectTestPlanDraft) -> ProjectTestPlanDraftModel:
    """Convert a domain draft to an ORM row."""
    return ProjectTestPlanDraftModel(
        draft_id=draft.draft_id,
        project_id=draft.project_id,
        source_document_path=draft.source_document_path,
        source_document_name=draft.source_document_name,
        source_format=draft.source_format,
        source_asset_id=draft.source_asset_id,
        source_case_id=draft.source_case_id,
        source_draft_id=draft.source_draft_id,
        status=draft.status.value,
        version=draft.version,
        payload_json=draft.payload_json,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
        reviewed_at=draft.reviewed_at,
    )


def _to_domain(row: ProjectTestPlanDraftModel) -> ProjectTestPlanDraft:
    """Convert an ORM row to a domain draft."""
    return ProjectTestPlanDraft(
        draft_id=row.draft_id,
        project_id=row.project_id,
        source_document_path=row.source_document_path,
        source_document_name=row.source_document_name,
        source_format=row.source_format,
        source_asset_id=row.source_asset_id,
        source_case_id=row.source_case_id,
        source_draft_id=row.source_draft_id,
        status=ProjectTestPlanDraftStatus(row.status),
        version=row.version,
        payload_json=row.payload_json,
        created_at=row.created_at,
        updated_at=row.updated_at,
        reviewed_at=row.reviewed_at,
    )
