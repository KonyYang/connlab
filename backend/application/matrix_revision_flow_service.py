"""Application service for backend Matrix revision flow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from backend.application.matrix_schedule_planning import (
    MatrixScheduleFields,
    MatrixScheduleValidationError,
    calculate_group_test_days,
    validate_planned_schedule,
)
from backend.application.matrix_sample_quantity_guard import (
    find_selected_sample_quantity_violations,
    format_sample_quantity_violation_message,
)
from backend.application.matrix_revision_snapshot_builder import (
    _build_confirmed_snapshot_from_revision_draft,
    _build_revision_draft_from_active,
)
from backend.domain import (
    ConfirmedMatrixSnapshot,
    Project,
    ProjectMatrixDraftSnapshot,
)


class MatrixRevisionFlowError(ValueError):
    """Raised when a Matrix revision flow request is invalid."""


class MatrixRevisionFlowConflictError(MatrixRevisionFlowError):
    """Raised when a Matrix revision flow request conflicts with active state."""


class MatrixRevisionFlowNotFoundError(LookupError):
    """Raised when required project, draft, or confirmed lineage cannot be found."""


class ProjectStore(Protocol):
    """Project lookup operations required by revision flow."""

    def get(self, project_id: str) -> Project | None:
        """Return one project by id."""


class DraftStore(Protocol):
    """Project Matrix draft persistence operations required by revision flow."""

    def create_snapshot(self, snapshot: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftSnapshot:
        """Persist one draft aggregate."""

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        """Return one draft aggregate by id."""

    def get_by_project_and_base_confirmed_matrix(
        self,
        project_id: str,
        base_confirmed_matrix_id: str,
    ) -> ProjectMatrixDraftRecord | None:
        """Return one draft record by project and base confirmed lineage."""


class ConfirmedStore(Protocol):
    """Confirmed Matrix authority operations required by revision flow."""

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return one active confirmed Matrix authority aggregate by project."""

    def supersede_active_and_create_snapshot(
        self,
        *,
        previous_active_confirmed_matrix_id: str,
        snapshot: ConfirmedMatrixSnapshot,
        superseded_reason: str | None = None,
    ) -> ConfirmedMatrixSnapshot:
        """Supersede active authority and persist new active authority atomically."""


@dataclass(frozen=True, slots=True)
class CreateMatrixRevisionDraftCommand:
    """Input payload for creating one revision draft from active authority."""

    project_id: str


@dataclass(frozen=True, slots=True)
class ConfirmMatrixRevisionDraftCommand:
    """Input payload for confirming one revision draft."""

    project_id: str
    project_matrix_draft_id: str
    confirmed_by: str
    superseded_reason: str | None = None


class MatrixRevisionFlowService:
    """Create and confirm Matrix revision drafts from active confirmed authority."""

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        draft_store: DraftStore,
        confirmed_store: ConfirmedStore,
    ) -> None:
        self._projects = project_store
        self._drafts = draft_store
        self._confirmed = confirmed_store

    def create_revision_draft(
        self,
        command: CreateMatrixRevisionDraftCommand,
    ) -> ProjectMatrixDraftSnapshot:
        """Create one editable revision draft from active confirmed authority."""
        project = self._projects.get(command.project_id)
        if project is None:
            raise MatrixRevisionFlowNotFoundError(f"Project not found: {command.project_id}")
        active = self._confirmed.get_active_by_project(command.project_id)
        if active is None:
            raise MatrixRevisionFlowNotFoundError("Active confirmed matrix not found.")
        if self._drafts.get_by_project_and_base_confirmed_matrix(
            command.project_id,
            active.version.confirmed_matrix_id,
        ):
            raise MatrixRevisionFlowConflictError(
                "Revision draft already exists for current active confirmed matrix."
            )
        draft = _build_revision_draft_from_active(active)
        try:
            return self._drafts.create_snapshot(draft)
        except IntegrityError as exc:
            raise MatrixRevisionFlowConflictError(
                "Revision draft already exists for current active confirmed matrix."
            ) from exc

    def confirm_revision_draft(
        self,
        command: ConfirmMatrixRevisionDraftCommand,
    ) -> ConfirmedMatrixSnapshot:
        """Confirm one revision draft and supersede previous active authority atomically."""
        confirmed_by = command.confirmed_by.strip()
        if not confirmed_by:
            raise MatrixRevisionFlowError("confirmed_by is required.")
        project = self._projects.get(command.project_id)
        if project is None:
            raise MatrixRevisionFlowNotFoundError(f"Project not found: {command.project_id}")
        active = self._confirmed.get_active_by_project(command.project_id)
        if active is None:
            raise MatrixRevisionFlowNotFoundError("Active confirmed matrix not found.")
        draft = self._drafts.get(command.project_matrix_draft_id)
        if draft is None or draft.record.project_id != command.project_id:
            raise MatrixRevisionFlowNotFoundError("Project matrix draft not found.")
        base_confirmed_matrix_id = (draft.record.base_confirmed_matrix_id or "").strip()
        if not base_confirmed_matrix_id:
            raise MatrixRevisionFlowError(
                "Revision draft must include base_confirmed_matrix_id."
            )
        if base_confirmed_matrix_id != active.version.confirmed_matrix_id:
            raise MatrixRevisionFlowConflictError(
                "Revision draft is stale relative to current active confirmed matrix."
            )
        selected_groups = tuple(group for group in draft.groups if bool(group.is_selected))
        if not selected_groups:
            raise MatrixRevisionFlowError(
                "At least one selected group is required for confirmation."
            )
        for group in selected_groups:
            if not group.group_key.strip() or not group.group_label.strip():
                raise MatrixRevisionFlowError(
                    "Selected groups must have nonblank group_key and group_label."
                )
        sample_violations = find_selected_sample_quantity_violations(selected_groups)
        if sample_violations:
            raise MatrixRevisionFlowError(
                format_sample_quantity_violation_message(sample_violations)
            )
        _validate_draft_schedule(draft, selected_groups)
        snapshot = _build_confirmed_snapshot_from_revision_draft(
            draft=draft,
            selected_groups=selected_groups,
            confirmed_by=confirmed_by,
            confirmed_revision=active.version.confirmed_revision + 1,
            source_import_id=active.version.source_import_id,
        )
        try:
            return self._confirmed.supersede_active_and_create_snapshot(
                previous_active_confirmed_matrix_id=active.version.confirmed_matrix_id,
                snapshot=snapshot,
                superseded_reason=command.superseded_reason,
            )
        except IntegrityError as exc:
            raise MatrixRevisionFlowConflictError(
                "Revision confirmation conflicts with active authority state."
            ) from exc
        except LookupError as exc:
            raise MatrixRevisionFlowConflictError(
                "Active confirmed matrix changed while confirming revision."
            ) from exc


def _validate_draft_schedule(
    draft: ProjectMatrixDraftSnapshot,
    selected_groups: tuple[ProjectMatrixDraftGroup, ...],
) -> None:
    """Validate Matrix planning fields before confirming a revision."""
    try:
        totals = calculate_group_test_days(
            rows=(
                {
                    "row_id": row.draft_row_id,
                    "day_expression": row.day_expression,
                    "is_sample_row": row.is_sample_row,
                }
                for row in draft.rows
            ),
            cells=(
                {
                    "row_id": cell.draft_row_id,
                    "group_id": cell.draft_group_id,
                    "cell_value": cell.cell_value,
                }
                for cell in draft.cells
            ),
            selected_group_ids=[group.draft_group_id for group in selected_groups],
        )
        validate_planned_schedule(
            fields=MatrixScheduleFields(
                pre_test_buffer_days=draft.record.pre_test_buffer_days,
                post_test_buffer_days=draft.record.post_test_buffer_days,
                sample_received_date=draft.record.sample_received_date,
                planned_test_start_date=draft.record.planned_test_start_date,
                planned_test_complete_date=draft.record.planned_test_complete_date,
                estimated_completion_date=draft.record.estimated_completion_date,
            ),
            group_test_days=totals,
        )
    except MatrixScheduleValidationError as exc:
        raise MatrixRevisionFlowError(str(exc)) from exc


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
