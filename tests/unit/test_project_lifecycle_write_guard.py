from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pytest

from backend.application.project_lifecycle_write_guard import (
    LifecycleWriteOperation,
    ProjectLifecycleReadonlyError,
    ProjectLifecycleWriteGuard,
    ProjectLifecycleWriteGuardNotFoundError,
)
from backend.domain import (
    Project,
    ProjectClosureType,
    ProjectLifecycleState,
    ProjectStatus,
)


def test_active_project_write_is_allowed() -> None:
    guard = ProjectLifecycleWriteGuard(_ProjectStore(_project()))

    guard.require_write_allowed("P1", LifecycleWriteOperation.BASIC_INFORMATION_DRAFT)


def test_stopped_project_write_is_blocked_with_resume_and_close_actions() -> None:
    guard = ProjectLifecycleWriteGuard(
        _ProjectStore(_project(lifecycle_state=ProjectLifecycleState.STOPPED))
    )

    with pytest.raises(ProjectLifecycleReadonlyError) as exc_info:
        guard.require_write_allowed(
            "P1",
            LifecycleWriteOperation.BASIC_INFORMATION_DRAFT,
        )

    exc = exc_info.value
    assert exc.project_id == "P1"
    assert exc.lifecycle_state is ProjectLifecycleState.STOPPED
    assert exc.closure_type is None
    assert exc.allowed_actions == ("resume", "close")
    assert exc.message == "This project is stopped. Resume it before making changes."


def test_closed_completed_project_write_is_blocked_as_readonly_archive() -> None:
    guard = ProjectLifecycleWriteGuard(
        _ProjectStore(
            _project(
                lifecycle_state=ProjectLifecycleState.CLOSED,
                closure_type=ProjectClosureType.COMPLETED,
            )
        )
    )

    with pytest.raises(ProjectLifecycleReadonlyError) as exc_info:
        guard.require_write_allowed(
            "P1",
            LifecycleWriteOperation.REQUIRED_FORMS_GENERATE,
        )

    assert exc_info.value.lifecycle_state is ProjectLifecycleState.CLOSED
    assert exc_info.value.closure_type is ProjectClosureType.COMPLETED
    assert exc_info.value.allowed_actions == ()
    assert (
        exc_info.value.message
        == "This project is closed as completed and is readonly."
    )


def test_closed_administrative_project_write_is_blocked_as_readonly_archive() -> None:
    guard = ProjectLifecycleWriteGuard(
        _ProjectStore(
            _project(
                lifecycle_state=ProjectLifecycleState.CLOSED,
                closure_type=ProjectClosureType.ADMINISTRATIVE,
            )
        )
    )

    with pytest.raises(ProjectLifecycleReadonlyError) as exc_info:
        guard.require_write_allowed(
            "P1",
            LifecycleWriteOperation.LTR_WORKBOOK_BASIC_INFORMATION_SYNC_COMMIT,
        )

    assert exc_info.value.closure_type is ProjectClosureType.ADMINISTRATIVE
    assert exc_info.value.message == (
        "This project is closed administratively and is readonly."
    )


def test_missing_project_raises_not_found() -> None:
    guard = ProjectLifecycleWriteGuard(_ProjectStore(None))

    with pytest.raises(ProjectLifecycleWriteGuardNotFoundError):
        guard.require_write_allowed("P1", LifecycleWriteOperation.MATRIX_EDITOR_CONFIRM)


@dataclass
class _ProjectStore:
    project: Project | None

    def get(self, project_id: str) -> Project | None:
        if self.project is None or self.project.project_id != project_id:
            return None
        return self.project


def _project(
    *,
    lifecycle_state: ProjectLifecycleState = ProjectLifecycleState.ACTIVE,
    closure_type: ProjectClosureType | None = None,
) -> Project:
    return Project(
        project_id="P1",
        project_no="DL-2026-06-001",
        product_name="Connector",
        requestor="Alice",
        status=ProjectStatus.LTR_REGISTERED,
        created_on=date(2026, 6, 27),
        lifecycle_state=lifecycle_state,
        closure_type=closure_type,
    )
