"""Application service for immutable Confirmed Matrix authority creation."""

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
from backend.application.matrix_step_quantity_authority_builder import (
    build_confirmed_step_quantities,
)
from backend.application.matrix_revision_snapshot_builder import (
    build_confirmed_duration_authorities,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    Project,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftSnapshot,
)


class ConfirmedMatrixAuthorityError(ValueError):
    """Raised when a confirm request is invalid."""


class ConfirmedMatrixAuthorityConflictError(ConfirmedMatrixAuthorityError):
    """Raised when a confirm request conflicts with active authority constraints."""


class ConfirmedMatrixAuthorityNotFoundError(LookupError):
    """Raised when required project or draft lineage cannot be found."""


class ProjectStore(Protocol):
    """Project lookup operations required by this service."""

    def get(self, project_id: str) -> Project | None:
        """Return one project by id."""


class ProjectMatrixDraftStore(Protocol):
    """Draft lookup operations required by this service."""

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        """Return one Project Matrix draft aggregate."""


class ConfirmedMatrixAuthorityStore(Protocol):
    """Confirmed Matrix authority operations required by this service."""

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return one active confirmed authority aggregate in one project."""

    def create_snapshot(self, snapshot: ConfirmedMatrixSnapshot) -> ConfirmedMatrixSnapshot:
        """Persist one confirmed authority aggregate."""


@dataclass(frozen=True, slots=True)
class ConfirmProjectMatrixDraftCommand:
    """Input payload for confirming one saved Project Matrix draft."""

    project_id: str
    project_matrix_draft_id: str
    confirmed_by: str


class ConfirmedMatrixAuthorityService:
    """Confirm one saved Project Matrix draft into immutable active authority state."""

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        draft_store: ProjectMatrixDraftStore,
        confirmed_store: ConfirmedMatrixAuthorityStore,
    ) -> None:
        self._projects = project_store
        self._drafts = draft_store
        self._confirmed = confirmed_store

    def confirm_draft(self, command: ConfirmProjectMatrixDraftCommand) -> ConfirmedMatrixSnapshot:
        """Create one immutable confirmed Matrix authority snapshot from a saved draft."""
        confirmed_by = command.confirmed_by.strip()
        if not confirmed_by:
            raise ConfirmedMatrixAuthorityError("confirmed_by is required.")
        project = self._projects.get(command.project_id)
        if project is None:
            raise ConfirmedMatrixAuthorityNotFoundError(
                f"Project not found: {command.project_id}"
            )
        draft = self._drafts.get(command.project_matrix_draft_id)
        if draft is None or draft.record.project_id != command.project_id:
            raise ConfirmedMatrixAuthorityNotFoundError("Project matrix draft not found.")
        if self._confirmed.get_active_by_project(command.project_id) is not None:
            raise ConfirmedMatrixAuthorityConflictError(
                "Project already has an active confirmed matrix authority."
            )
        selected_groups = tuple(
            group for group in draft.groups if bool(group.is_selected)
        )
        if not selected_groups:
            raise ConfirmedMatrixAuthorityError(
                "At least one selected group is required for confirmation."
            )
        for group in selected_groups:
            if not group.group_key.strip() or not group.group_label.strip():
                raise ConfirmedMatrixAuthorityError(
                    "Selected groups must have nonblank group_key and group_label."
                )
            if not (group.sample_quantity_expression or "").strip():
                raise ConfirmedMatrixAuthorityError(
                    "Selected groups must have nonblank sample quantity expression."
                )
        _validate_draft_schedule(draft, selected_groups)
        snapshot = _build_confirmed_snapshot(
            draft=draft,
            selected_groups=selected_groups,
            confirmed_by=confirmed_by,
        )
        try:
            return self._confirmed.create_snapshot(snapshot)
        except IntegrityError as exc:
            raise ConfirmedMatrixAuthorityConflictError(
                "Project already has an active confirmed matrix authority."
            ) from exc

    def get_active_snapshot(self, project_id: str) -> ConfirmedMatrixSnapshot:
        """Return one active confirmed Matrix snapshot in project scope."""
        project = self._projects.get(project_id)
        if project is None:
            raise ConfirmedMatrixAuthorityNotFoundError(f"Project not found: {project_id}")
        snapshot = self._confirmed.get_active_by_project(project_id)
        if snapshot is None:
            raise ConfirmedMatrixAuthorityNotFoundError("Active confirmed matrix not found.")
        return snapshot


def _build_confirmed_snapshot(
    *,
    draft: ProjectMatrixDraftSnapshot,
    selected_groups: tuple[ProjectMatrixDraftGroup, ...],
    confirmed_by: str,
) -> ConfirmedMatrixSnapshot:
    confirmed_matrix_id = f"cmv-{uuid4().hex}"
    confirmed_at = _utc_now()
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id=confirmed_matrix_id,
        project_id=draft.record.project_id,
        project_matrix_draft_id=draft.record.project_matrix_draft_id,
        source_import_id=draft.record.source_import_id,
        source_snapshot_id=draft.record.source_snapshot_id,
        confirmed_revision=1,
        is_active_authority=True,
        status=ConfirmedMatrixStatus.CONFIRMED,
        confirmed_by=confirmed_by,
        confirmed_at=confirmed_at,
        pre_test_buffer_days=_normalize_optional_text(draft.record.pre_test_buffer_days),
        post_test_buffer_days=_normalize_optional_text(draft.record.post_test_buffer_days),
        sample_received_date=_normalize_optional_text(draft.record.sample_received_date),
        planned_test_start_date=_normalize_optional_text(draft.record.planned_test_start_date),
        planned_test_complete_date=_normalize_optional_text(
            draft.record.planned_test_complete_date
        ),
        estimated_completion_date=_normalize_optional_text(draft.record.estimated_completion_date),
    )
    sorted_groups = sorted(selected_groups, key=lambda item: item.group_order)
    groups: list[ConfirmedMatrixGroup] = []
    confirmed_group_id_by_draft_group: dict[str, str] = {}
    for index, group in enumerate(sorted_groups, start=1):
        confirmed_group_id = f"cmg-{uuid4().hex}"
        confirmed_group_id_by_draft_group[group.draft_group_id] = confirmed_group_id
        groups.append(
            ConfirmedMatrixGroup(
                confirmed_group_id=confirmed_group_id,
                confirmed_matrix_id=confirmed_matrix_id,
                draft_group_id=group.draft_group_id,
                source_group_snapshot_id=group.source_group_snapshot_id,
                group_order=index,
                group_key=group.group_key.strip(),
                group_label=group.group_label.strip(),
                sample_quantity_expression=(group.sample_quantity_expression or "").strip(),
                sample_note=_normalize_optional_text(group.sample_note),
            )
        )
    non_sample_rows = sorted(
        (row for row in draft.rows if not bool(row.is_sample_row)),
        key=lambda item: item.row_order,
    )
    rows: list[ConfirmedMatrixRow] = []
    confirmed_row_id_by_draft_row: dict[str, str] = {}
    for index, row in enumerate(non_sample_rows, start=1):
        confirmed_row_id = f"cmr-{uuid4().hex}"
        confirmed_row_id_by_draft_row[row.draft_row_id] = confirmed_row_id
        rows.append(
            ConfirmedMatrixRow(
                confirmed_row_id=confirmed_row_id,
                confirmed_matrix_id=confirmed_matrix_id,
                draft_row_id=row.draft_row_id,
                source_row_snapshot_id=row.source_row_snapshot_id,
                row_order=index,
                test_item=row.test_item,
                source_section=_normalize_optional_text(row.source_section),
                method=_normalize_optional_text(row.method),
                condition=_normalize_optional_text(row.condition),
                requirement=_normalize_optional_text(row.requirement),
                day_expression=_normalize_optional_text(row.day_expression),
            )
        )
    cells: list[ConfirmedMatrixCell] = []
    seen_identity: set[tuple[str, str]] = set()
    for cell in draft.cells:
        confirmed_group_id = confirmed_group_id_by_draft_group.get(cell.draft_group_id)
        confirmed_row_id = confirmed_row_id_by_draft_row.get(cell.draft_row_id)
        if confirmed_group_id is None or confirmed_row_id is None:
            continue
        cell_value = cell.cell_value.strip()
        if not cell_value:
            continue
        identity = (confirmed_row_id, confirmed_group_id)
        if identity in seen_identity:
            continue
        seen_identity.add(identity)
        cells.append(
            ConfirmedMatrixCell(
                confirmed_cell_id=f"cmc-{uuid4().hex}",
                confirmed_matrix_id=confirmed_matrix_id,
                confirmed_row_id=confirmed_row_id,
                confirmed_group_id=confirmed_group_id,
                draft_row_id=cell.draft_row_id,
                draft_group_id=cell.draft_group_id,
                cell_value=cell_value,
            )
        )
    step_quantities = build_confirmed_step_quantities(
        draft=draft,
        confirmed_matrix_id=confirmed_matrix_id,
        confirmed_at=confirmed_at,
        confirmed_group_id_by_draft_group=confirmed_group_id_by_draft_group,
        confirmed_row_id_by_draft_row=confirmed_row_id_by_draft_row,
    )
    return ConfirmedMatrixSnapshot(
        version=version,
        groups=tuple(groups),
        rows=tuple(rows),
        cells=tuple(cells),
        step_quantities=tuple(step_quantities),
        duration_authorities=build_confirmed_duration_authorities(
            draft=draft,
            confirmed_matrix_id=confirmed_matrix_id,
            confirmed_at=confirmed_at,
            confirmed_group_id_by_draft_group=confirmed_group_id_by_draft_group,
            confirmed_row_id_by_draft_row=confirmed_row_id_by_draft_row,
        ),
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _validate_draft_schedule(
    draft: ProjectMatrixDraftSnapshot,
    selected_groups: tuple[ProjectMatrixDraftGroup, ...],
) -> None:
    """Validate Matrix planning fields before confirming authority."""
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
        raise ConfirmedMatrixAuthorityError(str(exc)) from exc


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
