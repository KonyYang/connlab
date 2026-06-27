"""Lifecycle readonly guard for project-scoped write operations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from backend.domain import Project, ProjectClosureType, ProjectLifecycleState


class LifecycleWriteOperation(StrEnum):
    """Project-scoped write operations covered by TASK_338 first slice."""

    BASIC_INFORMATION_DRAFT = "basic_information_draft"
    BASIC_INFORMATION_CONFIRM = "basic_information_confirm"
    MATRIX_EDITOR_DRAFT_SAVE = "matrix_editor_draft_save"
    MATRIX_EDITOR_DRAFT_DISCARD = "matrix_editor_draft_discard"
    MATRIX_EDITOR_CONFIRM = "matrix_editor_confirm"
    FEE_PRICING_DRAFT_SAVE = "fee_pricing_draft_save"
    FEE_PRICING_DRAFT_DISCARD = "fee_pricing_draft_discard"
    REQUIRED_FORMS_GENERATE = "required_forms_generate"
    LTR_WORKBOOK_BASIC_INFORMATION_SYNC_COMMIT = (
        "ltr_workbook_basic_information_sync_commit"
    )


class ProjectLifecycleReadonlyError(ValueError):
    """Raised when a stopped or closed project rejects a write operation."""

    def __init__(
        self,
        *,
        project_id: str,
        lifecycle_state: ProjectLifecycleState,
        closure_type: ProjectClosureType | None,
        message: str,
        allowed_actions: tuple[str, ...],
    ) -> None:
        super().__init__(message)
        self.project_id = project_id
        self.lifecycle_state = lifecycle_state
        self.closure_type = closure_type
        self.message = message
        self.allowed_actions = allowed_actions


class ProjectLifecycleWriteGuardNotFoundError(LookupError):
    """Raised when a write guard cannot load the project."""


@dataclass(frozen=True, slots=True)
class ProjectLifecycleWriteGuardResult:
    """Readonly decision for one project write operation."""

    project_id: str
    lifecycle_state: ProjectLifecycleState
    closure_type: ProjectClosureType | None
    readonly: bool
    allowed_actions: tuple[str, ...]
    message: str | None = None


class ProjectStore(Protocol):
    """Project read behavior required by lifecycle write guards."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""


class ProjectLifecycleWriteGuard:
    """Block selected write operations for stopped and closed projects."""

    def __init__(self, project_store: ProjectStore) -> None:
        self._projects = project_store

    def check_write_allowed(
        self,
        project_id: str,
        operation: LifecycleWriteOperation,
    ) -> ProjectLifecycleWriteGuardResult:
        """Return readonly state for one write operation."""
        project = self._projects.get(project_id)
        if project is None:
            raise ProjectLifecycleWriteGuardNotFoundError(
                f"Project not found: {project_id}"
            )
        message, actions = _readonly_message_and_actions(project)
        return ProjectLifecycleWriteGuardResult(
            project_id=project.project_id,
            lifecycle_state=project.lifecycle_state,
            closure_type=project.closure_type,
            readonly=message is not None,
            allowed_actions=actions,
            message=message,
        )

    def require_write_allowed(
        self,
        project_id: str,
        operation: LifecycleWriteOperation,
    ) -> None:
        """Raise when a project lifecycle state is readonly for writes."""
        result = self.check_write_allowed(project_id, operation)
        if not result.readonly:
            return
        raise ProjectLifecycleReadonlyError(
            project_id=result.project_id,
            lifecycle_state=result.lifecycle_state,
            closure_type=result.closure_type,
            message=result.message or "This project is readonly.",
            allowed_actions=result.allowed_actions,
        )


def _readonly_message_and_actions(
    project: Project,
) -> tuple[str | None, tuple[str, ...]]:
    if project.lifecycle_state is ProjectLifecycleState.STOPPED:
        return (
            "This project is stopped. Resume it before making changes.",
            ("resume", "close"),
        )
    if project.lifecycle_state is ProjectLifecycleState.CLOSED:
        if project.closure_type is ProjectClosureType.COMPLETED:
            return "This project is closed as completed and is readonly.", ()
        if project.closure_type is ProjectClosureType.ADMINISTRATIVE:
            return "This project is closed administratively and is readonly.", ()
        return "This project is closed and is readonly.", ()
    return None, ()
