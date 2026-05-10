"""Controlled cleanup execution for projects without registered LTR records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from backend.domain import LtrRecord, LtrStatus, Project, ProjectStatus


NO_LTR_PROJECT_RESIDUE = "no_ltr_project_residue"


@dataclass(frozen=True, slots=True)
class ProjectCleanupAuditRecord:
    """Audit record for one project cleanup action."""

    cleanup_id: str
    project_id: str
    cleanup_type: str
    previous_status: str
    new_status: str
    reason: str
    operator: str | None
    created_at: str
    details_json: str | None = None


@dataclass(frozen=True, slots=True)
class NoLtrProjectCleanupCommand:
    """Operator request to cancel selected no-LTR projects."""

    project_ids: tuple[str, ...]
    reason: str
    operator: str | None = None


@dataclass(frozen=True, slots=True)
class NoLtrProjectCleanupChangedProject:
    """One project changed by the cleanup execution."""

    project_id: str
    previous_status: str
    new_status: str
    cleanup_id: str


@dataclass(frozen=True, slots=True)
class NoLtrProjectCleanupRejectedProject:
    """One project rejected by the cleanup execution."""

    project_id: str
    reason: str


@dataclass(frozen=True, slots=True)
class NoLtrProjectCleanupResult:
    """Summary of one cleanup execution request."""

    cancelled_count: int
    skipped_count: int
    changed: tuple[NoLtrProjectCleanupChangedProject, ...]
    rejected: tuple[NoLtrProjectCleanupRejectedProject, ...]


class NoLtrProjectCleanupError(ValueError):
    """Raised when the cleanup request itself is invalid."""


class ProjectStore(Protocol):
    """Persistence operations needed by the cleanup service."""

    def get(self, project_id: str) -> Project | None: ...

    def update(self, project: Project) -> Project: ...


class LtrStore(Protocol):
    """LTR lookup operations needed by the cleanup service."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]: ...


class ProjectCleanupAuditStore(Protocol):
    """Audit persistence operations needed by the cleanup service."""

    def create(self, record: ProjectCleanupAuditRecord) -> ProjectCleanupAuditRecord: ...


class NoLtrProjectCleanupService:
    """Cancel selected historical projects only when they have no registered LTR."""

    def __init__(
        self,
        project_store: ProjectStore,
        ltr_store: LtrStore,
        audit_store: ProjectCleanupAuditStore,
    ) -> None:
        self._project_store = project_store
        self._ltr_store = ltr_store
        self._audit_store = audit_store

    def execute(
        self,
        command: NoLtrProjectCleanupCommand,
    ) -> NoLtrProjectCleanupResult:
        """Cancel eligible selected projects and record audit rows."""
        project_ids = _unique_project_ids(command.project_ids)
        reason = command.reason.strip()
        if not project_ids:
            raise NoLtrProjectCleanupError("At least one project_id is required.")
        if not reason:
            raise NoLtrProjectCleanupError("Cleanup reason is required.")

        changed: list[NoLtrProjectCleanupChangedProject] = []
        rejected: list[NoLtrProjectCleanupRejectedProject] = []
        skipped_count = 0
        operator = command.operator.strip() if command.operator else None

        for project_id in project_ids:
            project = self._project_store.get(project_id)
            if project is None:
                rejected.append(
                    NoLtrProjectCleanupRejectedProject(
                        project_id=project_id,
                        reason="Project not found.",
                    )
                )
                continue

            if _has_registered_ltr(self._ltr_store.list_by_project(project_id)):
                rejected.append(
                    NoLtrProjectCleanupRejectedProject(
                        project_id=project_id,
                        reason="Project has registered LTR and cannot be cleaned as no-LTR residue.",
                    )
                )
                continue

            if project.status is ProjectStatus.CANCELLED:
                skipped_count += 1
                continue

            cleanup_id = uuid4().hex
            previous_status = project.status.value
            updated_project = project.with_status(ProjectStatus.CANCELLED)
            self._project_store.update(updated_project)
            self._audit_store.create(
                ProjectCleanupAuditRecord(
                    cleanup_id=cleanup_id,
                    project_id=project_id,
                    cleanup_type=NO_LTR_PROJECT_RESIDUE,
                    previous_status=previous_status,
                    new_status=ProjectStatus.CANCELLED.value,
                    reason=reason,
                    operator=operator,
                    created_at=datetime.now(UTC).isoformat(),
                    details_json=json.dumps(
                        {
                            "product_name": project.product_name,
                            "requestor": project.requestor,
                            "business_unit": project.business_unit,
                        },
                        ensure_ascii=False,
                    ),
                )
            )
            changed.append(
                NoLtrProjectCleanupChangedProject(
                    project_id=project_id,
                    previous_status=previous_status,
                    new_status=ProjectStatus.CANCELLED.value,
                    cleanup_id=cleanup_id,
                )
            )

        return NoLtrProjectCleanupResult(
            cancelled_count=len(changed),
            skipped_count=skipped_count,
            changed=tuple(changed),
            rejected=tuple(rejected),
        )


def _unique_project_ids(project_ids: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    unique: list[str] = []
    for raw_project_id in project_ids:
        project_id = raw_project_id.strip()
        if project_id and project_id not in seen:
            seen.add(project_id)
            unique.append(project_id)
    return tuple(unique)


def _has_registered_ltr(ltrs: list[LtrRecord]) -> bool:
    return any(ltr.status is LtrStatus.REGISTERED for ltr in ltrs)
