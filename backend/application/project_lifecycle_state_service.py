"""Project lifecycle overlay service for stop, resume, and closure actions."""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from backend.domain import (
    LtrRecord,
    Project,
    ProjectClosureType,
    ProjectLifecycleEvent,
    ProjectLifecycleEventType,
    ProjectLifecycleState,
    ProjectStatus,
)


class ProjectStore(Protocol):
    """Persistence boundary for project lifecycle state changes."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID, or None."""

    def update(self, project: Project) -> Project:
        """Persist a changed project."""


class LtrStore(Protocol):
    """Read boundary for registered LTR presence checks."""

    def list_by_project(self, project_id: str) -> Sequence[LtrRecord]:
        """Return LTR records linked to the project."""


class ProjectLifecycleEventStore(Protocol):
    """Persistence boundary for lifecycle transition events."""

    def create(self, event: ProjectLifecycleEvent) -> ProjectLifecycleEvent:
        """Persist a lifecycle event."""

    def list_by_project(self, project_id: str) -> Sequence[ProjectLifecycleEvent]:
        """Return events linked to the project."""


class OutputStatusService(Protocol):
    """Read boundary for Project output status summary."""

    def get_status_summary(self, project_id: str) -> object:
        """Return the current Project output status summary."""


@dataclass(frozen=True, slots=True)
class StopProjectLifecycleCommand:
    """Command for stopping one project."""

    project_id: str
    reason: str | None = None
    operator: str | None = None


@dataclass(frozen=True, slots=True)
class ResumeProjectLifecycleCommand:
    """Command for resuming one stopped project."""

    project_id: str
    reason: str | None = None
    operator: str | None = None


@dataclass(frozen=True, slots=True)
class CloseCompletedProjectCommand:
    """Command for completed project closure."""

    project_id: str
    close_note: str
    manual_completion_confirmed: bool
    output_summary_acknowledged: bool
    operator: str | None = None


@dataclass(frozen=True, slots=True)
class CloseAdministrativeProjectCommand:
    """Command for administrative project closure."""

    project_id: str
    reason: str
    operator: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectLifecycleView:
    """API-facing lifecycle state view."""

    project_id: str
    lifecycle_state: ProjectLifecycleState
    closure_type: ProjectClosureType | None
    status: str
    status_label: str
    readonly: bool
    allowed_actions: tuple[str, ...]
    stopped_at: str | None = None
    stopped_reason: str | None = None
    closed_at: str | None = None
    closed_reason: str | None = None
    completion_summary: dict[str, object] | None = None
    warnings: tuple[str, ...] = ()
    previous_status: str | None = None
    audit_recorded: bool = False


class ProjectLifecycleStateError(RuntimeError):
    """Raised when a lifecycle transition is invalid."""


class ProjectLifecycleStateNotFoundError(ProjectLifecycleStateError):
    """Raised when a lifecycle action targets a missing project."""


class ProjectLifecycleStateService:
    """Coordinate Project lifecycle overlay transitions."""

    def __init__(
        self,
        project_store: ProjectStore,
        ltr_store: LtrStore,
        event_store: ProjectLifecycleEventStore,
        output_status_service: OutputStatusService | None = None,
        *,
        clock: Callable[[], str] | None = None,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._project_store = project_store
        self._ltr_store = ltr_store
        self._event_store = event_store
        self._output_status_service = output_status_service
        self._clock = clock or (lambda: datetime.now(timezone.utc).isoformat())
        self._id_factory = id_factory or (lambda: uuid4().hex)

    def get_lifecycle(self, project_id: str) -> ProjectLifecycleView:
        """Return lifecycle state for one project."""
        return self._view(self._get_project(project_id))

    def stop_project(
        self,
        command: StopProjectLifecycleCommand,
    ) -> ProjectLifecycleView:
        """Stop an active project and preserve the previous compatibility status."""
        project = self._get_project(command.project_id)
        if project.lifecycle_state is ProjectLifecycleState.CLOSED:
            raise ProjectLifecycleStateError("closed projects cannot be stopped.")
        if project.lifecycle_state is ProjectLifecycleState.STOPPED:
            return self._view(project, previous_status=project.status.value)

        now = self._clock()
        reason = _required_or_default(command.reason, "Stopped by operator.")
        updated = project.with_status(ProjectStatus.CANCELLED).with_lifecycle(
            lifecycle_state=ProjectLifecycleState.STOPPED,
            stopped_reason=reason,
            stopped_at=now,
            stopped_by=command.operator,
        )
        self._project_store.update(updated)
        self._event_store.create(
            self._event(
                project=project,
                event_type=ProjectLifecycleEventType.STOP,
                new_state=ProjectLifecycleState.STOPPED,
                reason=reason,
                operator=command.operator,
                metadata={"previous_project_status": project.status.value},
                created_at=now,
            )
        )
        return self._view(
            updated,
            previous_status=project.status.value,
            audit_recorded=True,
        )

    def record_legacy_stop_result(
        self,
        *,
        project_id: str,
        previous_status: str,
        reason: str,
        operator: str | None,
    ) -> ProjectLifecycleView:
        """Synchronize lifecycle overlay after the legacy stop API writes its audit."""
        project = self._get_project(project_id)
        if project.lifecycle_state is ProjectLifecycleState.STOPPED:
            return self._view(
                project,
                previous_status=previous_status,
                audit_recorded=True,
            )
        if project.lifecycle_state is ProjectLifecycleState.CLOSED:
            raise ProjectLifecycleStateError("closed projects cannot be stopped.")
        try:
            ProjectStatus(previous_status)
        except ValueError as exc:
            raise ProjectLifecycleStateError(
                "Cannot record stop because previous project status is invalid."
            ) from exc

        now = self._clock()
        updated = project.with_lifecycle(
            lifecycle_state=ProjectLifecycleState.STOPPED,
            stopped_reason=reason,
            stopped_at=now,
            stopped_by=operator,
        )
        self._project_store.update(updated)
        self._event_store.create(
            self._event(
                project=project,
                event_type=ProjectLifecycleEventType.STOP,
                new_state=ProjectLifecycleState.STOPPED,
                reason=reason,
                operator=operator,
                metadata={"previous_project_status": previous_status},
                created_at=now,
            )
        )
        return self._view(
            updated,
            previous_status=previous_status,
            audit_recorded=True,
        )

    def resume_project(
        self,
        command: ResumeProjectLifecycleCommand,
    ) -> ProjectLifecycleView:
        """Resume a stopped project using recorded previous status metadata."""
        project = self._get_project(command.project_id)
        if project.lifecycle_state is ProjectLifecycleState.CLOSED:
            raise ProjectLifecycleStateError("closed projects cannot be resumed.")
        if project.lifecycle_state is ProjectLifecycleState.ACTIVE:
            return self._view(project)

        previous_status = self._latest_previous_status(project.project_id)
        if previous_status is None:
            raise ProjectLifecycleStateError(
                "Cannot resume project because previous project status is unavailable."
            )

        now = self._clock()
        reason = _required_or_default(command.reason, "Resumed by operator.")
        updated = replace(
            project.with_status(previous_status),
            lifecycle_state=ProjectLifecycleState.ACTIVE,
            closure_type=None,
            resumed_reason=reason,
            resumed_at=now,
            resumed_by=command.operator,
            closed_reason=None,
            closed_at=None,
            closed_by=None,
            completion_summary_json=None,
        )
        self._project_store.update(updated)
        self._event_store.create(
            self._event(
                project=project,
                event_type=ProjectLifecycleEventType.RESUME,
                new_state=ProjectLifecycleState.ACTIVE,
                reason=reason,
                operator=command.operator,
                metadata={"restored_project_status": previous_status.value},
                created_at=now,
            )
        )
        return self._view(updated, audit_recorded=True)

    def close_completed_project(
        self,
        command: CloseCompletedProjectCommand,
    ) -> ProjectLifecycleView:
        """Close a formal project as completed with explicit manual confirmation."""
        project = self._get_project(command.project_id)
        if project.lifecycle_state is ProjectLifecycleState.CLOSED:
            raise ProjectLifecycleStateError("Project is already closed.")
        close_note = _required_text(command.close_note, "Close completed note")
        if not command.manual_completion_confirmed:
            raise ProjectLifecycleStateError(
                "Manual completion confirmation is required."
            )
        if not command.output_summary_acknowledged:
            raise ProjectLifecycleStateError(
                "Output summary acknowledgement is required."
            )
        if not self._has_formal_identity(project):
            raise ProjectLifecycleStateError(
                "Completed closure requires a formal or registered project."
            )

        ltrs = list(self._ltr_store.list_by_project(project.project_id))
        output_summary = self._output_status_summary(project.project_id)
        summary = {
            "close_note": close_note,
            "manual_completion_confirmed": True,
            "output_summary_acknowledged": True,
            "signals": {
                "project_identity": project.project_no or _first_ltr_identity(ltrs),
                "registered_ltr": bool(ltrs),
                "output_status_summary_available": output_summary is not None,
            },
            "output_status_summary": output_summary,
            "warning": (
                "Testing completion is manually confirmed in this phase because "
                "StepInstance does not exist."
            ),
        }
        now = self._clock()
        updated = project.with_status(ProjectStatus.CLOSED).with_lifecycle(
            lifecycle_state=ProjectLifecycleState.CLOSED,
            closure_type=ProjectClosureType.COMPLETED,
            closed_reason=close_note,
            closed_at=now,
            closed_by=command.operator,
            completion_summary_json=json.dumps(summary, ensure_ascii=False),
        )
        self._project_store.update(updated)
        self._event_store.create(
            self._event(
                project=project,
                event_type=ProjectLifecycleEventType.CLOSE_COMPLETED,
                new_state=ProjectLifecycleState.CLOSED,
                new_closure_type=ProjectClosureType.COMPLETED,
                reason=close_note,
                operator=command.operator,
                metadata=summary,
                created_at=now,
            )
        )
        return self._view(updated, audit_recorded=True)

    def close_administrative_project(
        self,
        command: CloseAdministrativeProjectCommand,
    ) -> ProjectLifecycleView:
        """Close any project administratively with a required reason."""
        project = self._get_project(command.project_id)
        if project.lifecycle_state is ProjectLifecycleState.CLOSED:
            raise ProjectLifecycleStateError("Project is already closed.")
        reason = _required_text(command.reason, "Administrative closure reason")
        now = self._clock()
        updated = project.with_status(ProjectStatus.CLOSED).with_lifecycle(
            lifecycle_state=ProjectLifecycleState.CLOSED,
            closure_type=ProjectClosureType.ADMINISTRATIVE,
            closed_reason=reason,
            closed_at=now,
            closed_by=command.operator,
        )
        self._project_store.update(updated)
        self._event_store.create(
            self._event(
                project=project,
                event_type=ProjectLifecycleEventType.CLOSE_ADMINISTRATIVE,
                new_state=ProjectLifecycleState.CLOSED,
                new_closure_type=ProjectClosureType.ADMINISTRATIVE,
                reason=reason,
                operator=command.operator,
                created_at=now,
            )
        )
        return self._view(updated, audit_recorded=True)

    def close_completed(
        self,
        command: CloseCompletedProjectCommand,
    ) -> ProjectLifecycleView:
        """Compatibility alias for completed closure."""
        return self.close_completed_project(command)

    def close_administrative(
        self,
        command: CloseAdministrativeProjectCommand,
    ) -> ProjectLifecycleView:
        """Compatibility alias for administrative closure."""
        return self.close_administrative_project(command)

    def _get_project(self, project_id: str) -> Project:
        project = self._project_store.get(project_id)
        if project is None:
            raise ProjectLifecycleStateNotFoundError(f"Project not found: {project_id}")
        return project

    def _has_formal_identity(self, project: Project) -> bool:
        return bool(project.project_no and project.project_no.strip()) or bool(
            self._ltr_store.list_by_project(project.project_id)
        )

    def _output_status_summary(self, project_id: str) -> dict[str, object] | None:
        if self._output_status_service is None:
            return None
        summary = self._output_status_service.get_status_summary(project_id)
        return {
            "project_id": getattr(summary, "project_id", project_id),
            "active_draft_id": getattr(summary, "active_draft_id", None),
            "active_draft_version": getattr(summary, "active_draft_version", None),
            "items": [
                {
                    "output_kind": _enum_value(getattr(item, "output_kind", None)),
                    "status": _enum_value(getattr(item, "status", None)),
                    "output_path": getattr(item, "output_path", None),
                    "source": _optional_enum_value(getattr(item, "source", None)),
                    "draft_id": getattr(item, "draft_id", None),
                    "draft_version": getattr(item, "draft_version", None),
                    "reason": getattr(item, "reason", None),
                    "updated_at": getattr(item, "updated_at", None),
                    "output_sha256": getattr(item, "output_sha256", None),
                    "output_size_bytes": getattr(item, "output_size_bytes", None),
                    "source_context_signature": getattr(
                        item,
                        "source_context_signature",
                        None,
                    ),
                }
                for item in getattr(summary, "items", ())
            ],
        }

    def _latest_previous_status(self, project_id: str) -> ProjectStatus | None:
        for event in reversed(list(self._event_store.list_by_project(project_id))):
            if _enum_value(event.event_type) != ProjectLifecycleEventType.STOP.value:
                continue
            payload = _metadata(event.metadata_json)
            value = payload.get("previous_project_status")
            if isinstance(value, str):
                try:
                    return ProjectStatus(value)
                except ValueError:
                    return None
        return None

    def _event(
        self,
        *,
        project: Project,
        event_type: ProjectLifecycleEventType,
        new_state: ProjectLifecycleState,
        reason: str | None,
        operator: str | None,
        created_at: str,
        new_closure_type: ProjectClosureType | None = None,
        metadata: dict[str, object] | None = None,
    ) -> ProjectLifecycleEvent:
        return ProjectLifecycleEvent(
            event_id=self._id_factory(),
            project_id=project.project_id,
            event_type=event_type,
            previous_lifecycle_state=project.lifecycle_state,
            new_lifecycle_state=new_state,
            previous_closure_type=project.closure_type,
            new_closure_type=new_closure_type,
            reason=reason,
            operator=operator,
            created_at=created_at,
            metadata_json=(
                json.dumps(metadata, ensure_ascii=False) if metadata is not None else None
            ),
        )

    def _view(
        self,
        project: Project,
        *,
        previous_status: str | None = None,
        audit_recorded: bool = False,
    ) -> ProjectLifecycleView:
        return ProjectLifecycleView(
            project_id=project.project_id,
            lifecycle_state=project.lifecycle_state,
            closure_type=project.closure_type,
            status=project.status.value,
            status_label=_status_label(project),
            readonly=project.lifecycle_state is not ProjectLifecycleState.ACTIVE,
            allowed_actions=_allowed_actions(project),
            stopped_at=project.stopped_at,
            stopped_reason=project.stopped_reason,
            closed_at=project.closed_at,
            closed_reason=project.closed_reason,
            completion_summary=_metadata(project.completion_summary_json),
            warnings=_warnings(project),
            previous_status=previous_status,
            audit_recorded=audit_recorded,
        )


def _required_text(value: str | None, label: str) -> str:
    text = (value or "").strip()
    if not text:
        if label == "Administrative closure reason":
            raise ProjectLifecycleStateError("reason is required.")
        raise ProjectLifecycleStateError(f"{label} is required.")
    return text


def _required_or_default(value: str | None, default: str) -> str:
    return (value or "").strip() or default


def _metadata(value: str | None) -> dict[str, object]:
    if not value:
        return {}
    try:
        payload = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _enum_value(value: object) -> str:
    return getattr(value, "value", str(value))


def _optional_enum_value(value: object) -> str | None:
    return None if value is None else _enum_value(value)


def _first_ltr_identity(ltrs: Sequence[object]) -> str | None:
    if not ltrs:
        return None
    return getattr(ltrs[0], "ltr_number", None)


def _status_label(project: Project) -> str:
    if project.lifecycle_state is ProjectLifecycleState.STOPPED:
        return "Stopped"
    if project.closure_type is ProjectClosureType.COMPLETED:
        return "Closed: Completed"
    if project.closure_type is ProjectClosureType.ADMINISTRATIVE:
        return "Closed: Administrative"
    return "Active"


def _allowed_actions(project: Project) -> tuple[str, ...]:
    if project.lifecycle_state is ProjectLifecycleState.CLOSED:
        return ()
    if project.lifecycle_state is ProjectLifecycleState.STOPPED:
        return ("resume", "close")
    return ("stop", "close")


def _warnings(project: Project) -> tuple[str, ...]:
    if (
        project.lifecycle_state is ProjectLifecycleState.CLOSED
        and project.closure_type is ProjectClosureType.COMPLETED
    ):
        return ("Completion is manually confirmed until execution records exist.",)
    if project.lifecycle_state is ProjectLifecycleState.STOPPED:
        return ("Stopped projects are read-only outside lifecycle actions.",)
    return ()
