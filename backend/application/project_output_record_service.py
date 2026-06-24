"""Application service for persisted project output lineage and status."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from backend.domain import (
    Project,
    ProjectOutputKind,
    ProjectOutputRecord,
    ProjectOutputSource,
    ProjectOutputStatus,
    ProjectTestPlanDraft,
    ProjectTestPlanDraftStatus,
)


class ProjectOutputRecordError(ValueError):
    """Raised when a project output record request is invalid."""


class ProjectOutputRecordNotFoundError(LookupError):
    """Raised when project or draft cannot be found."""


class ProjectStore(Protocol):
    def get(self, project_id: str) -> Project | None:
        """Return project by id."""


class ProjectOutputRecordStore(Protocol):
    def create(self, record: ProjectOutputRecord) -> ProjectOutputRecord:
        """Persist one output record."""

    def list_by_project(self, project_id: str) -> list[ProjectOutputRecord]:
        """List output records by project."""


class ProjectTestPlanDraftStore(Protocol):
    def get(self, draft_id: str) -> ProjectTestPlanDraft | None:
        """Return one Project test-plan draft by id."""

    def list_by_project(self, project_id: str) -> list[ProjectTestPlanDraft]:
        """List drafts for one project."""


@dataclass(frozen=True, slots=True)
class RegisterProjectOutputCommand:
    """Input command for output record registration."""

    project_id: str
    output_kind: ProjectOutputKind
    status: ProjectOutputStatus
    source: ProjectOutputSource
    output_path: str | None = None
    draft_id: str | None = None
    note: str | None = None
    output_sha256: str | None = None
    output_size_bytes: int | None = None
    source_context_signature: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectOutputStatusItem:
    """One output kind status item for Workbench."""

    output_kind: ProjectOutputKind
    status: ProjectOutputStatus
    output_path: str | None
    source: ProjectOutputSource | None
    draft_id: str | None
    draft_version: int | None
    reason: str
    updated_at: str | None
    output_sha256: str | None = None
    output_size_bytes: int | None = None
    source_context_signature: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectOutputStatusSummary:
    """Project-level read model for output status and active draft linkage."""

    project_id: str
    active_draft_id: str | None
    active_draft_version: int | None
    items: tuple[ProjectOutputStatusItem, ...]


class ProjectOutputRecordService:
    """Register and read persisted project output lineage/status."""

    _ORDERED_KINDS = (
        ProjectOutputKind.SECTION2_WRITE_BACK,
        ProjectOutputKind.TEST_RECORD_FORM,
        ProjectOutputKind.FEE_EVALUATION,
        ProjectOutputKind.CUSTOMER_FEEDBACK_FORM,
        ProjectOutputKind.APPROVAL_PACKAGE,
    )

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        draft_store: ProjectTestPlanDraftStore,
        output_store: ProjectOutputRecordStore,
    ) -> None:
        self._projects = project_store
        self._drafts = draft_store
        self._outputs = output_store

    def register_output(self, command: RegisterProjectOutputCommand) -> ProjectOutputRecord:
        self._require_project(command.project_id)
        draft_id = _normalize_optional_text(command.draft_id)
        draft_version: int | None = None
        if draft_id is not None:
            draft = self._drafts.get(draft_id)
            if draft is None or draft.project_id != command.project_id:
                raise ProjectOutputRecordNotFoundError(
                    f"Project test-plan draft not found for project: {command.project_id}"
                )
            draft_version = draft.version
        elif (
            command.status not in {ProjectOutputStatus.MANUAL, ProjectOutputStatus.FAILED}
            and not _is_context_bound_system_output(command)
        ):
            raise ProjectOutputRecordError(
                "draft_id is required unless status is manual or failed."
            )
        now = _utc_now()
        record = ProjectOutputRecord(
            output_record_id=f"por-{uuid4().hex}",
            project_id=command.project_id,
            draft_id=draft_id,
            draft_version=draft_version,
            output_kind=command.output_kind,
            output_path=_normalize_optional_text(command.output_path),
            output_sha256=_normalize_optional_text(command.output_sha256),
            output_size_bytes=command.output_size_bytes,
            source_context_signature=_normalize_optional_text(
                command.source_context_signature
            ),
            status=command.status,
            source=command.source,
            created_at=now,
            updated_at=now,
            note=_normalize_optional_text(command.note),
        )
        return self._outputs.create(record)

    def list_records(self, project_id: str) -> list[ProjectOutputRecord]:
        self._require_project(project_id)
        return self._outputs.list_by_project(project_id)

    def get_status_summary(self, project_id: str) -> ProjectOutputStatusSummary:
        self._require_project(project_id)
        drafts = self._drafts.list_by_project(project_id)
        active_draft = _latest_reviewed_draft(drafts)
        active_draft_id = active_draft.draft_id if active_draft else None
        active_draft_version = active_draft.version if active_draft else None
        records = self._outputs.list_by_project(project_id)
        latest_by_kind = _latest_record_by_kind(records)
        items = tuple(
            _status_item(kind, latest_by_kind.get(kind), active_draft_id, active_draft_version)
            for kind in self._ORDERED_KINDS
        )
        return ProjectOutputStatusSummary(
            project_id=project_id,
            active_draft_id=active_draft_id,
            active_draft_version=active_draft_version,
            items=items,
        )

    def _require_project(self, project_id: str) -> Project:
        project = self._projects.get(project_id)
        if project is None:
            raise ProjectOutputRecordNotFoundError(f"Project not found: {project_id}")
        return project


def _latest_record_by_kind(
    records: list[ProjectOutputRecord],
) -> dict[ProjectOutputKind, ProjectOutputRecord]:
    latest: dict[ProjectOutputKind, ProjectOutputRecord] = {}
    for item in records:
        latest[item.output_kind] = item
    return latest


def _latest_reviewed_draft(
    drafts: list[ProjectTestPlanDraft],
) -> ProjectTestPlanDraft | None:
    reviewed = [item for item in drafts if item.status is ProjectTestPlanDraftStatus.REVIEWED]
    if not reviewed:
        return None

    def _sort_key(item: ProjectTestPlanDraft) -> tuple[str, int, str]:
        return (item.reviewed_at or "", item.version, item.updated_at)

    reviewed.sort(key=_sort_key, reverse=True)
    return reviewed[0]


def _status_item(
    kind: ProjectOutputKind,
    record: ProjectOutputRecord | None,
    active_draft_id: str | None,
    active_draft_version: int | None,
) -> ProjectOutputStatusItem:
    if record is None:
        return ProjectOutputStatusItem(
            output_kind=kind,
            status=ProjectOutputStatus.MISSING,
            output_path=None,
            source=None,
            draft_id=None,
            draft_version=None,
            reason="No persisted output record exists.",
            updated_at=None,
            output_sha256=None,
            output_size_bytes=None,
            source_context_signature=None,
        )
    if record.status in {ProjectOutputStatus.MANUAL, ProjectOutputStatus.FAILED}:
        reason = (
            "Operator-managed output path." if record.status is ProjectOutputStatus.MANUAL
            else "Last persisted output attempt failed."
        )
        return ProjectOutputStatusItem(
            output_kind=kind,
            status=record.status,
            output_path=record.output_path,
            source=record.source,
            draft_id=record.draft_id,
            draft_version=record.draft_version,
            reason=reason,
            updated_at=record.updated_at,
            output_sha256=record.output_sha256,
            output_size_bytes=record.output_size_bytes,
            source_context_signature=record.source_context_signature,
        )
    if (
        active_draft_id is not None
        and record.draft_id is not None
        and (record.draft_id != active_draft_id or record.draft_version != active_draft_version)
    ):
        return ProjectOutputStatusItem(
            output_kind=kind,
            status=ProjectOutputStatus.STALE,
            output_path=record.output_path,
            source=record.source,
            draft_id=record.draft_id,
            draft_version=record.draft_version,
            reason=(
                f"Output was recorded for draft v{record.draft_version}; "
                f"active draft is v{active_draft_version}."
            ),
            updated_at=record.updated_at,
            output_sha256=record.output_sha256,
            output_size_bytes=record.output_size_bytes,
            source_context_signature=record.source_context_signature,
        )
    return ProjectOutputStatusItem(
        output_kind=kind,
        status=ProjectOutputStatus.CURRENT,
        output_path=record.output_path,
        source=record.source,
        draft_id=record.draft_id,
        draft_version=record.draft_version,
        reason="Persisted output is aligned with active draft context.",
        updated_at=record.updated_at,
        output_sha256=record.output_sha256,
        output_size_bytes=record.output_size_bytes,
        source_context_signature=record.source_context_signature,
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _is_context_bound_system_output(command: RegisterProjectOutputCommand) -> bool:
    return (
        command.status is ProjectOutputStatus.CURRENT
        and command.source is ProjectOutputSource.SYSTEM_GENERATED
        and _normalize_optional_text(command.source_context_signature) is not None
    )


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
