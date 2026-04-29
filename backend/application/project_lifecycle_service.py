"""Project lifecycle operation guards."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from backend.domain import Project, ProjectStatus


class LifecycleOperation(StrEnum):
    """Operations guarded by current project lifecycle state."""

    LTR_PREVIEW = "ltr_preview"
    LTR_COMMIT = "ltr_commit"
    FOLDER_PREVIEW = "folder_preview"
    FOLDER_GENERATE = "folder_generate"
    EVIDENCE_PREVIEW = "evidence_preview"
    EVIDENCE_PLACE = "evidence_place"


class ProjectLifecycleError(ValueError):
    """Raised when an operation is not allowed by lifecycle state."""


class ProjectLifecycleNotFoundError(LookupError):
    """Raised when lifecycle guard cannot load a project."""


@dataclass(frozen=True, slots=True)
class LifecycleGuardResult:
    """Result of checking whether an operation is allowed."""

    project_id: str
    operation: LifecycleOperation
    allowed: bool
    reason: str | None = None


class ProjectRepositoryPort(Protocol):
    """Project repository behavior required by lifecycle guards."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""


class ProjectLifecycleService:
    """Check operation-level guards against existing project statuses."""

    _CLOSED_STATUSES = {ProjectStatus.CLOSED, ProjectStatus.CANCELLED}
    _LTR_ALLOWED_STATUSES = {
        ProjectStatus.CONFIRMED,
        ProjectStatus.PRECHECK_PASSED,
    }
    _FOLDER_ALLOWED_STATUSES = {ProjectStatus.LTR_REGISTERED}
    _EVIDENCE_ALLOWED_STATUSES = {ProjectStatus.FOLDER_CREATED}

    def __init__(self, project_repository: ProjectRepositoryPort) -> None:
        """Create a lifecycle service with a project repository."""
        self._projects = project_repository

    def check_allowed(
        self,
        project_id: str,
        operation: LifecycleOperation,
    ) -> LifecycleGuardResult:
        """Return whether a lifecycle operation is currently allowed."""
        project = self._projects.get(project_id)
        if project is None:
            raise ProjectLifecycleNotFoundError(f"Project not found: {project_id}")
        reason = self._blocked_reason(project, operation)
        return LifecycleGuardResult(
            project_id=project_id,
            operation=operation,
            allowed=reason is None,
            reason=reason,
        )

    def require_allowed(
        self,
        project_id: str,
        operation: LifecycleOperation,
    ) -> None:
        """Raise a business-readable error when an operation is blocked."""
        result = self.check_allowed(project_id, operation)
        if not result.allowed:
            raise ProjectLifecycleError(result.reason or "Operation is not allowed.")

    def _blocked_reason(
        self,
        project: Project,
        operation: LifecycleOperation,
    ) -> str | None:
        """Return a blocking reason for a project operation, or None."""
        if project.status in self._CLOSED_STATUSES:
            return (
                f"Project is {project.status.value}; reopen or create a correction "
                "workflow before changing project records or files."
            )
        if operation in {
            LifecycleOperation.LTR_PREVIEW,
            LifecycleOperation.LTR_COMMIT,
        }:
            return self._ltr_reason(project)
        if operation in {
            LifecycleOperation.FOLDER_PREVIEW,
            LifecycleOperation.FOLDER_GENERATE,
        }:
            return self._folder_reason(project)
        if operation in {
            LifecycleOperation.EVIDENCE_PREVIEW,
            LifecycleOperation.EVIDENCE_PLACE,
        }:
            return self._evidence_reason(project, operation)
        return None

    def _ltr_reason(self, project: Project) -> str | None:
        """Return the LTR operation blocking reason, or None."""
        if project.status in {
            ProjectStatus.LTR_REGISTERED,
            ProjectStatus.FOLDER_CREATED,
        }:
            return (
                "Project already has a registered LTR; use renumber or correction "
                "workflow for changes."
            )
        if project.status not in self._LTR_ALLOWED_STATUSES:
            return (
                "LTR registration requires confirmed project data before preview "
                f"or commit. Current project status is {project.status.value}."
            )
        return None

    def _folder_reason(self, project: Project) -> str | None:
        """Return the folder operation blocking reason, or None."""
        if project.status is ProjectStatus.FOLDER_CREATED:
            return (
                "Project folder has already been created; use evidence or correction "
                "workflow for later changes."
            )
        if project.status not in self._FOLDER_ALLOWED_STATUSES:
            return (
                "Project folder generation requires a registered LTR first. "
                f"Current project status is {project.status.value}."
            )
        return None

    def _evidence_reason(
        self,
        project: Project,
        operation: LifecycleOperation,
    ) -> str | None:
        """Return the evidence operation blocking reason, or None."""
        if operation is LifecycleOperation.EVIDENCE_PLACE:
            if project.status not in self._EVIDENCE_ALLOWED_STATUSES:
                return (
                    "Evidence placement requires a generated project folder first. "
                    f"Current project status is {project.status.value}."
                )
        return None
