from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pytest

from backend.application.project_lifecycle_state_service import (
    ActivateProjectLifecycleCommand,
    CloseAdministrativeProjectCommand,
    CloseCompletedProjectCommand,
    CloseProjectLifecycleCommand,
    ProjectLifecycleStateError,
    ProjectLifecycleStateService,
    ResumeProjectLifecycleCommand,
    StopProjectLifecycleCommand,
)
from backend.application.project_output_record_service import (
    ProjectOutputStatusItem,
    ProjectOutputStatusSummary,
)
from backend.domain import (
    Project,
    ProjectCloseReasonCategory,
    ProjectClosureType,
    ProjectLifecycleState,
    ProjectOutputKind,
    ProjectOutputSource,
    ProjectOutputStatus,
    ProjectStatus,
)


def test_stop_sets_stopped_overlay_cancelled_compatibility_and_event() -> None:
    stores = _Stores(project=_project(status=ProjectStatus.LTR_REGISTERED))
    service = stores.service()

    result = service.stop_project(
        StopProjectLifecycleCommand(project_id="P1", reason=None, operator="Lab User")
    )

    assert result.lifecycle_state is ProjectLifecycleState.STOPPED
    assert result.readonly is True
    assert result.allowed_actions == ("activate", "resume", "close")
    assert stores.projects.project.status is ProjectStatus.CANCELLED
    assert stores.events.items[-1].event_type == "stop"
    assert '"previous_project_status": "ltr_registered"' in stores.events.items[-1].metadata_json


def test_resume_restores_previous_status_from_stop_event_metadata() -> None:
    project = _project(status=ProjectStatus.CANCELLED).with_lifecycle(
        lifecycle_state=ProjectLifecycleState.STOPPED,
        stopped_reason="Paused",
        stopped_at="2026-06-27T01:00:00+00:00",
        stopped_by="Lab User",
    )
    stores = _Stores(
        project=project,
        events=[
            _event(
                event_type="stop",
                previous_lifecycle_state="active",
                new_lifecycle_state="stopped",
                metadata_json='{"previous_project_status": "ltr_registered"}',
            )
        ],
    )
    service = stores.service()

    result = service.resume_project(
        ResumeProjectLifecycleCommand(project_id="P1", operator="Lab User")
    )

    assert result.lifecycle_state is ProjectLifecycleState.ACTIVE
    assert stores.projects.project.status is ProjectStatus.LTR_REGISTERED
    assert stores.events.items[-1].event_type == "resume"


def test_resume_legacy_stopped_without_previous_status_is_blocked() -> None:
    project = _project(status=ProjectStatus.CANCELLED).with_lifecycle(
        lifecycle_state=ProjectLifecycleState.STOPPED,
    )
    service = _Stores(project=project).service()

    with pytest.raises(ProjectLifecycleStateError, match="previous project status"):
        service.resume_project(ResumeProjectLifecycleCommand(project_id="P1"))


def test_unified_close_completed_allows_temporary_project() -> None:
    service = _Stores(project=_project(project_no=None), ltrs=[]).service()

    result = service.close_project(
        CloseProjectLifecycleCommand(
            project_id="P1",
            reason_category=ProjectCloseReasonCategory.COMPLETED,
            note="Completed without formal LTR.",
        )
    )

    assert result.lifecycle_state is ProjectLifecycleState.CLOSED
    assert result.close_reason_category is ProjectCloseReasonCategory.COMPLETED
    assert result.allowed_actions == ("activate",)


def test_close_completed_records_manual_summary_for_formal_project() -> None:
    stores = _Stores(project=_project(project_no="DL-2026-06-001"))
    service = stores.service()

    result = service.close_completed(
        CloseCompletedProjectCommand(
            project_id="P1",
            close_note="All deliverables accepted.",
            manual_completion_confirmed=True,
            output_summary_acknowledged=True,
            operator="Lab User",
        )
    )

    assert result.lifecycle_state is ProjectLifecycleState.CLOSED
    assert result.closure_type == "completed"
    assert result.close_reason_category == "completed"
    assert result.readonly is True
    assert result.allowed_actions == ("activate",)
    assert result.completion_summary is not None
    assert result.completion_summary["manual_completion_confirmed"] is True
    assert result.completion_summary["signals"] == {
        "project_identity": "DL-2026-06-001",
        "registered_ltr": False,
        "output_status_summary_available": True,
    }
    output_summary = result.completion_summary["output_status_summary"]
    assert output_summary["active_draft_id"] == "DRAFT1"
    assert output_summary["items"][0]["output_kind"] == "approval_package"
    assert output_summary["items"][0]["status"] == "current"
    assert stores.events.items[-1].event_type == "close"


def test_activate_closed_project_restores_previous_status_and_preserves_close_metadata() -> None:
    project = _project(status=ProjectStatus.CLOSED).with_lifecycle(
        lifecycle_state=ProjectLifecycleState.CLOSED,
        closure_type=ProjectClosureType.COMPLETED,
        close_reason_category=ProjectCloseReasonCategory.COMPLETED,
        closed_reason="Finished.",
        closed_at="2026-06-27T01:00:00+00:00",
        closed_by="Lab User",
    )
    stores = _Stores(
        project=project,
        events=[
            _event(
                event_type="close",
                previous_lifecycle_state="active",
                new_lifecycle_state="closed",
                metadata_json='{"previous_project_status": "ltr_registered", '
                '"close_reason_category": "completed", "close_note": "Finished."}',
            )
        ],
    )
    service = stores.service()

    result = service.activate_project(
        ActivateProjectLifecycleCommand(
            project_id="P1",
            reason="Customer requested continuation.",
            operator="Lab User",
        )
    )

    assert result.lifecycle_state is ProjectLifecycleState.ACTIVE
    assert stores.projects.project.status is ProjectStatus.LTR_REGISTERED
    assert stores.events.items[-1].event_type == "activate"
    assert '"previous_close_reason_category": "completed"' in (
        stores.events.items[-1].metadata_json or ""
    )


def test_close_stopped_project_preserves_original_status_for_activation() -> None:
    project = _project(status=ProjectStatus.CANCELLED).with_lifecycle(
        lifecycle_state=ProjectLifecycleState.STOPPED,
        stopped_reason="Paused.",
    )
    stores = _Stores(
        project=project,
        events=[
            _event(
                event_type="stop",
                previous_lifecycle_state="active",
                new_lifecycle_state="stopped",
                metadata_json='{"previous_project_status": "ltr_registered"}',
            )
        ],
    )
    service = stores.service()

    service.close_project(
        CloseProjectLifecycleCommand(
            project_id="P1",
            reason_category=ProjectCloseReasonCategory.FAILED,
            note="Cannot continue.",
        )
    )
    result = service.activate_project(
        ActivateProjectLifecycleCommand(project_id="P1", reason="Retest approved.")
    )

    assert result.lifecycle_state is ProjectLifecycleState.ACTIVE
    assert stores.projects.project.status is ProjectStatus.LTR_REGISTERED


def test_close_administrative_requires_reason() -> None:
    service = _Stores(project=_project()).service()

    with pytest.raises(ProjectLifecycleStateError, match="reason is required"):
        service.close_administrative(
            CloseAdministrativeProjectCommand(project_id="P1", reason=" ")
        )


def test_closed_project_cannot_resume() -> None:
    project = _project(status=ProjectStatus.CLOSED).with_lifecycle(
        lifecycle_state=ProjectLifecycleState.CLOSED,
    )
    service = _Stores(project=project).service()

    with pytest.raises(ProjectLifecycleStateError, match="closed"):
        service.resume_project(ResumeProjectLifecycleCommand(project_id="P1"))


@dataclass
class _Stores:
    project: Project
    ltrs: list[object] | None = None
    events: list[object] | None = None

    def __post_init__(self) -> None:
        self.projects = _ProjectStore(self.project)
        self.events = _EventStore(self.events)

    def service(self) -> ProjectLifecycleStateService:
        return ProjectLifecycleStateService(
            project_store=self.projects,
            ltr_store=_LtrStore(self.ltrs),
            event_store=self.events,
            output_status_service=_OutputStatusService(),
            clock=lambda: "2026-06-27T02:00:00+00:00",
            id_factory=lambda: "EVT1",
        )


class _ProjectStore:
    def __init__(self, project: Project) -> None:
        self.project = project

    def get(self, project_id: str) -> Project | None:
        return self.project if self.project.project_id == project_id else None

    def update(self, project: Project) -> Project:
        self.project = project
        return project


class _LtrStore:
    def __init__(self, records: list[object] | None) -> None:
        self._records = records or []

    def list_by_project(self, project_id: str) -> list[object]:
        return self._records


class _EventStore:
    def __init__(self, records: list[object] | None) -> None:
        self.items = list(records or [])

    def create(self, event):
        self.items.append(event)
        return event

    def list_by_project(self, project_id: str):
        return list(self.items)


class _OutputStatusService:
    def get_status_summary(self, project_id: str) -> ProjectOutputStatusSummary:
        return ProjectOutputStatusSummary(
            project_id=project_id,
            active_draft_id="DRAFT1",
            active_draft_version=2,
            items=(
                ProjectOutputStatusItem(
                    output_kind=ProjectOutputKind.APPROVAL_PACKAGE,
                    status=ProjectOutputStatus.CURRENT,
                    output_path="D:/outputs/package.zip",
                    source=ProjectOutputSource.SYSTEM_GENERATED,
                    draft_id="DRAFT1",
                    draft_version=2,
                    reason="Current output record exists.",
                    updated_at="2026-06-27T02:00:00+00:00",
                ),
            ),
        )


def _project(
    *,
    project_no: str | None = "DL-2026-06-001",
    status: ProjectStatus = ProjectStatus.DRAFT,
) -> Project:
    return Project(
        project_id="P1",
        project_no=project_no,
        product_name="Connector",
        requestor="Alice",
        status=status,
        created_on=date(2026, 6, 27),
    )


def _event(
    *,
    event_type: str,
    previous_lifecycle_state: str,
    new_lifecycle_state: str,
    metadata_json: str,
):
    from backend.domain import ProjectLifecycleEvent

    return ProjectLifecycleEvent(
        event_id="OLD",
        project_id="P1",
        event_type=event_type,
        previous_lifecycle_state=previous_lifecycle_state,
        new_lifecycle_state=new_lifecycle_state,
        previous_closure_type=None,
        new_closure_type=None,
        reason=None,
        operator=None,
        created_at="2026-06-27T01:00:00+00:00",
        metadata_json=metadata_json,
    )
