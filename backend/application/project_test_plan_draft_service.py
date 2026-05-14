"""Application service for Project test-plan draft snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from backend.domain import Project, ProjectTestPlanDraft, ProjectTestPlanDraftStatus


class ProjectTestPlanDraftError(ValueError):
    """Raised when a Project test-plan draft request is invalid."""


class ProjectTestPlanDraftNotFoundError(LookupError):
    """Raised when a Project test-plan draft cannot be found."""


class ProjectStore(Protocol):
    """Project lookup operations needed by the draft service."""

    def get(self, project_id: str) -> Project | None:
        """Return a Project by id."""


class ProjectTestPlanDraftStore(Protocol):
    """Persistence operations needed by the draft service."""

    def create(self, draft: ProjectTestPlanDraft) -> ProjectTestPlanDraft:
        """Persist a draft."""

    def get(self, draft_id: str) -> ProjectTestPlanDraft | None:
        """Return a draft by id."""

    def list_by_project(self, project_id: str) -> list[ProjectTestPlanDraft]:
        """Return drafts for one Project."""

    def list_by_project_and_source(
        self,
        project_id: str,
        source_document_path: str,
    ) -> list[ProjectTestPlanDraft]:
        """Return drafts for one Project/source pair."""

    def update(self, draft: ProjectTestPlanDraft) -> ProjectTestPlanDraft:
        """Update a draft."""


@dataclass(frozen=True, slots=True)
class CreateProjectTestPlanDraftCommand:
    """Input for creating a Project test-plan draft snapshot."""

    project_id: str
    source_document_path: str
    source_document_name: str
    source_format: str
    payload: dict[str, Any]
    status: ProjectTestPlanDraftStatus = ProjectTestPlanDraftStatus.DRAFT
    supersede_existing_active: bool = True
    source_asset_id: str | None = None
    source_case_id: str | None = None
    source_draft_id: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateProjectTestPlanDraftCommand:
    """Input for updating a Project test-plan draft snapshot."""

    project_id: str
    draft_id: str
    payload: dict[str, Any] | None = None
    status: ProjectTestPlanDraftStatus | None = None


class ProjectTestPlanDraftService:
    """Create, review, and read Project-stage test-plan draft snapshots."""

    _ACTIVE_STATUSES = {
        ProjectTestPlanDraftStatus.DRAFT,
        ProjectTestPlanDraftStatus.REVIEWED,
    }

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        draft_store: ProjectTestPlanDraftStore,
    ) -> None:
        """Create the service with repository ports."""
        self._projects = project_store
        self._drafts = draft_store

    def create_draft(
        self,
        command: CreateProjectTestPlanDraftCommand,
    ) -> ProjectTestPlanDraft:
        """Create a new draft and supersede prior active drafts for the same source."""
        self._require_project(command.project_id)
        source_document_path = _required_text(
            command.source_document_path,
            "source_document_path",
        )
        source_document_name = _required_text(
            command.source_document_name,
            "source_document_name",
        )
        source_format = _required_text(command.source_format, "source_format")
        if command.status is ProjectTestPlanDraftStatus.SUPERSEDED:
            raise ProjectTestPlanDraftError("New drafts cannot be created as superseded.")
        payload_json = _payload_json(command.payload)
        now = _utc_now()
        next_version = self._next_version(command.project_id, source_document_path)
        if command.supersede_existing_active:
            for existing in self._drafts.list_by_project_and_source(
                command.project_id,
                source_document_path,
            ):
                if existing.status in self._ACTIVE_STATUSES:
                    self._drafts.update(
                        _with_status(
                            existing,
                            ProjectTestPlanDraftStatus.SUPERSEDED,
                            now,
                        )
                    )
        draft = ProjectTestPlanDraft(
            draft_id=f"ptpd-{uuid4().hex}",
            project_id=command.project_id,
            source_document_path=source_document_path,
            source_document_name=source_document_name,
            source_format=source_format,
            source_asset_id=_optional_text(command.source_asset_id),
            source_case_id=_optional_text(command.source_case_id),
            source_draft_id=_optional_text(command.source_draft_id),
            status=command.status,
            version=next_version,
            payload_json=payload_json,
            created_at=now,
            updated_at=now,
            reviewed_at=now if command.status is ProjectTestPlanDraftStatus.REVIEWED else None,
        )
        return self._drafts.create(draft)

    def list_by_project(self, project_id: str) -> list[ProjectTestPlanDraft]:
        """List drafts for one Project after verifying Project ownership."""
        self._require_project(project_id)
        return self._drafts.list_by_project(project_id)

    def get_draft(self, project_id: str, draft_id: str) -> ProjectTestPlanDraft:
        """Return one Project-scoped draft."""
        self._require_project(project_id)
        draft = self._drafts.get(draft_id)
        if draft is None or draft.project_id != project_id:
            raise ProjectTestPlanDraftNotFoundError(
                f"Project test-plan draft not found for project: {project_id}"
            )
        return draft

    def update_draft(
        self,
        command: UpdateProjectTestPlanDraftCommand,
    ) -> ProjectTestPlanDraft:
        """Update draft payload and/or status within the owning Project."""
        existing = self.get_draft(command.project_id, command.draft_id)
        if existing.status is ProjectTestPlanDraftStatus.SUPERSEDED:
            raise ProjectTestPlanDraftError("Superseded drafts cannot be updated.")
        new_status = command.status or existing.status
        _validate_status_transition(existing.status, new_status)
        payload_json = (
            _payload_json(command.payload)
            if command.payload is not None
            else existing.payload_json
        )
        now = _utc_now()
        reviewed_at = existing.reviewed_at
        if (
            new_status is ProjectTestPlanDraftStatus.REVIEWED
            and existing.status is not ProjectTestPlanDraftStatus.REVIEWED
        ):
            reviewed_at = now
        updated = ProjectTestPlanDraft(
            draft_id=existing.draft_id,
            project_id=existing.project_id,
            source_document_path=existing.source_document_path,
            source_document_name=existing.source_document_name,
            source_format=existing.source_format,
            source_asset_id=existing.source_asset_id,
            source_case_id=existing.source_case_id,
            source_draft_id=existing.source_draft_id,
            status=new_status,
            version=existing.version,
            payload_json=payload_json,
            created_at=existing.created_at,
            updated_at=now,
            reviewed_at=reviewed_at,
        )
        return self._drafts.update(updated)

    def _require_project(self, project_id: str) -> Project:
        project = self._projects.get(project_id)
        if project is None:
            raise ProjectTestPlanDraftNotFoundError(f"Project not found: {project_id}")
        return project

    def _next_version(self, project_id: str, source_document_path: str) -> int:
        drafts = self._drafts.list_by_project_and_source(project_id, source_document_path)
        if not drafts:
            return 1
        return max(draft.version for draft in drafts) + 1


def _validate_status_transition(
    current: ProjectTestPlanDraftStatus,
    new_status: ProjectTestPlanDraftStatus,
) -> None:
    """Validate first-version draft lifecycle transitions."""
    allowed = {
        ProjectTestPlanDraftStatus.DRAFT: {
            ProjectTestPlanDraftStatus.DRAFT,
            ProjectTestPlanDraftStatus.REVIEWED,
            ProjectTestPlanDraftStatus.SUPERSEDED,
        },
        ProjectTestPlanDraftStatus.REVIEWED: {
            ProjectTestPlanDraftStatus.REVIEWED,
            ProjectTestPlanDraftStatus.SUPERSEDED,
        },
        ProjectTestPlanDraftStatus.SUPERSEDED: {ProjectTestPlanDraftStatus.SUPERSEDED},
    }
    if new_status not in allowed[current]:
        raise ProjectTestPlanDraftError(
            f"Invalid test-plan draft status transition: {current.value}->{new_status.value}"
        )


def _with_status(
    draft: ProjectTestPlanDraft,
    status: ProjectTestPlanDraftStatus,
    updated_at: str,
) -> ProjectTestPlanDraft:
    """Return a copy of a draft with an updated status."""
    return ProjectTestPlanDraft(
        draft_id=draft.draft_id,
        project_id=draft.project_id,
        source_document_path=draft.source_document_path,
        source_document_name=draft.source_document_name,
        source_format=draft.source_format,
        source_asset_id=draft.source_asset_id,
        source_case_id=draft.source_case_id,
        source_draft_id=draft.source_draft_id,
        status=status,
        version=draft.version,
        payload_json=draft.payload_json,
        created_at=draft.created_at,
        updated_at=updated_at,
        reviewed_at=draft.reviewed_at,
    )


def _required_text(value: str, field_name: str) -> str:
    text = value.strip()
    if not text:
        raise ProjectTestPlanDraftError(f"{field_name} is required.")
    return text


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _payload_json(payload: dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        raise ProjectTestPlanDraftError("payload must be an object.")
    try:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)
    except TypeError as exc:
        raise ProjectTestPlanDraftError("payload must be JSON serializable.") from exc


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
