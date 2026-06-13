"""Project stop and safe temporary delete use cases."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal, Protocol
from uuid import uuid4

from backend.application.no_ltr_project_cleanup_service import ProjectCleanupAuditRecord
from backend.domain import Project, ProjectStatus


@dataclass(frozen=True, slots=True)
class TemporaryProjectDeletePreview:
    """Safe-delete decision for one temporary planning project."""

    project_id: str
    can_delete: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    recommended_action: Literal["delete", "stop"]


@dataclass(frozen=True, slots=True)
class TemporaryProjectDeleteResult:
    """Result returned after deleting a safe temporary project."""

    project_id: str
    deleted: bool
    deleted_temporary_context: bool


@dataclass(frozen=True, slots=True)
class ProjectStopCommand:
    """Operator request to stop a project while preserving its history."""

    project_id: str
    reason: str | None = None
    operator: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectStopResult:
    """Result returned after a project is stopped."""

    project_id: str
    previous_status: str
    status: str
    status_label: str
    reason: str
    audit_recorded: bool


class ProjectLifecycleManagementError(ValueError):
    """Raised when a lifecycle management operation cannot be completed."""


class ProjectLifecycleManagementNotFoundError(ProjectLifecycleManagementError):
    """Raised when a lifecycle-managed project cannot be found."""


class ProjectStore(Protocol):
    """Project persistence operations needed by lifecycle management."""

    def get(self, project_id: str) -> Project | None:
        """Return one project by id."""

    def update(self, project: Project) -> Project:
        """Persist an updated project."""

    def delete(self, project_id: str) -> bool:
        """Delete one project row."""


class TemporaryContextStore(Protocol):
    """Temporary context operations needed by safe delete."""

    def get_by_project(self, project_id: str):
        """Return temporary context by project id."""

    def delete_by_project(self, project_id: str) -> bool:
        """Delete temporary context by project id."""


class ProjectArtifactStore(Protocol):
    """Project-scoped artifact lookup used by delete guards."""

    def list_by_project(self, project_id: str):
        """Return project-scoped artifacts."""


class ActiveMatrixStore(Protocol):
    """Confirmed Matrix lookup used by delete guards."""

    def get_active_by_project(self, project_id: str):
        """Return the active Confirmed Matrix, if any."""


class LatestByProjectStore(Protocol):
    """Latest project-scoped record lookup used by delete guards."""

    def get_latest_by_project(self, project_id: str):
        """Return the latest project-scoped record, if any."""


class WorkspaceStore(Protocol):
    """Official workspace lookup used by delete guards."""

    def get_by_project(self, project_id: str):
        """Return workspace record by project id."""


class RequestMaterialStore(Protocol):
    """Request-material collection lookup used by delete guards."""

    def latest_by_project(self, project_id: str):
        """Return latest request-material collection by project id."""


class CleanupAuditStore(Protocol):
    """Audit persistence for stopped projects."""

    def create(self, record: ProjectCleanupAuditRecord) -> ProjectCleanupAuditRecord:
        """Persist one audit record."""


class ProjectLifecycleManagementService:
    """Manage stopped projects and safe deletion for temporary planning projects."""

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        temporary_context_store: TemporaryContextStore,
        ltr_store: ProjectArtifactStore,
        confirmed_matrix_store: ActiveMatrixStore,
        official_workspace_store: WorkspaceStore,
        folder_store: ProjectArtifactStore,
        file_asset_store: ProjectArtifactStore,
        output_store: ProjectArtifactStore,
        request_material_store: RequestMaterialStore,
        confirmed_fee_store: LatestByProjectStore,
        matrix_draft_store: ProjectArtifactStore,
        audit_store: CleanupAuditStore,
    ) -> None:
        self._projects = project_store
        self._temporary_contexts = temporary_context_store
        self._ltrs = ltr_store
        self._confirmed_matrices = confirmed_matrix_store
        self._official_workspaces = official_workspace_store
        self._folders = folder_store
        self._file_assets = file_asset_store
        self._outputs = output_store
        self._request_material = request_material_store
        self._confirmed_fees = confirmed_fee_store
        self._matrix_drafts = matrix_draft_store
        self._audits = audit_store

    def preview_temporary_delete(self, project_id: str) -> TemporaryProjectDeletePreview:
        """Return whether one project can be safely deleted as a temporary record."""
        project = self._projects.get(project_id)
        if project is None:
            raise ProjectLifecycleManagementNotFoundError(f"Project not found: {project_id}")

        blockers = self._delete_blockers(project)
        warnings = (
            "Delete removes only ConnLab-owned temporary records. It does not touch public-drive files or LTR workbooks.",
        )
        return TemporaryProjectDeletePreview(
            project_id=project_id,
            can_delete=not blockers,
            blockers=tuple(blockers),
            warnings=warnings,
            recommended_action="delete" if not blockers else "stop",
        )

    def delete_temporary_project(self, project_id: str) -> TemporaryProjectDeleteResult:
        """Delete one safe temporary project after re-running server-side guards."""
        preview = self.preview_temporary_delete(project_id)
        if not preview.can_delete:
            raise ProjectLifecycleManagementError("; ".join(preview.blockers))
        deleted_context = self._temporary_contexts.delete_by_project(project_id)
        deleted_project = self._projects.delete(project_id)
        return TemporaryProjectDeleteResult(
            project_id=project_id,
            deleted=deleted_project,
            deleted_temporary_context=deleted_context,
        )

    def stop_project(self, command: ProjectStopCommand) -> ProjectStopResult:
        """Stop a project by mapping user-facing Stopped to internal cancelled status."""
        project = self._projects.get(command.project_id)
        if project is None:
            raise ProjectLifecycleManagementNotFoundError(
                f"Project not found: {command.project_id}"
            )
        reason = _reason(command.reason)
        if project.status is ProjectStatus.CANCELLED:
            return ProjectStopResult(
                project_id=project.project_id,
                previous_status=project.status.value,
                status=project.status.value,
                status_label="Stopped",
                reason=reason,
                audit_recorded=False,
            )
        previous_status = project.status.value
        updated = self._projects.update(project.with_status(ProjectStatus.CANCELLED))
        self._audits.create(
            ProjectCleanupAuditRecord(
                cleanup_id=uuid4().hex,
                project_id=project.project_id,
                cleanup_type="project_stopped",
                previous_status=previous_status,
                new_status=ProjectStatus.CANCELLED.value,
                reason=reason,
                operator=_optional_text(command.operator),
                created_at=datetime.now(UTC).isoformat(),
                details_json=json.dumps(
                    {
                        "source": "task_317e_project_lifecycle_management",
                        "user_facing_status": "Stopped",
                    },
                    sort_keys=True,
                ),
            )
        )
        return ProjectStopResult(
            project_id=updated.project_id,
            previous_status=previous_status,
            status=updated.status.value,
            status_label="Stopped",
            reason=reason,
            audit_recorded=True,
        )

    def _delete_blockers(self, project: Project) -> list[str]:
        blockers: list[str] = []
        if project.project_no:
            blockers.append("Project has a registered project number; stop it instead.")
        if project.status is ProjectStatus.CANCELLED:
            blockers.append("Project is already stopped and retained for review.")
        temporary_context = self._temporary_contexts.get_by_project(project.project_id)
        if temporary_context is None:
            blockers.append("Project is not a temporary planning project.")
        elif getattr(temporary_context, "source_asset_ids", ()):
            blockers.append("Temporary source material is linked; stop the project instead.")
        if self._ltrs.list_by_project(project.project_id):
            blockers.append("Registered LTR/DL records exist; stop the project instead.")
        if self._confirmed_matrices.get_active_by_project(project.project_id) is not None:
            blockers.append("Active Confirmed Matrix exists; stop the project instead.")
        if self._official_workspaces.get_by_project(project.project_id) is not None:
            blockers.append("Official project workspace exists; stop the project instead.")
        if self._folders.list_by_project(project.project_id):
            blockers.append("Formal project folder record exists; stop the project instead.")
        if self._file_assets.list_by_project(project.project_id):
            blockers.append("Project file assets exist; stop the project instead.")
        if self._outputs.list_by_project(project.project_id):
            blockers.append("Project output records exist; stop the project instead.")
        if self._request_material.latest_by_project(project.project_id) is not None:
            blockers.append("Request material collection exists; stop the project instead.")
        if self._confirmed_fees.get_latest_by_project(project.project_id) is not None:
            blockers.append("Confirmed Fee authority exists; stop the project instead.")
        if self._matrix_drafts.list_by_project(project.project_id):
            blockers.append("Temporary Matrix drafts exist; stop the project instead.")
        return blockers


def _reason(value: str | None) -> str:
    reason = _optional_text(value)
    return reason or "Stopped by operator."


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None
