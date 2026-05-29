"""Application service for backend Matrix revision flow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from backend.application.matrix_sample_quantity_guard import (
    find_selected_sample_quantity_violations,
    format_sample_quantity_violation_message,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    Project,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
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


def _build_revision_draft_from_active(
    active: ConfirmedMatrixSnapshot,
) -> ProjectMatrixDraftSnapshot:
    draft_id = f"pmd-{uuid4().hex}"
    now = _utc_now()
    record = ProjectMatrixDraftRecord(
        project_matrix_draft_id=draft_id,
        project_id=active.version.project_id,
        source_import_id=None,
        source_snapshot_id=active.version.source_snapshot_id,
        status=ProjectMatrixDraftStatus.DRAFT,
        created_at=now,
        updated_at=now,
        base_confirmed_matrix_id=active.version.confirmed_matrix_id,
    )
    groups = tuple(
        ProjectMatrixDraftGroup(
            draft_group_id=f"pmdg-{uuid4().hex}",
            project_matrix_draft_id=draft_id,
            source_group_snapshot_id=group.source_group_snapshot_id,
            group_order=index,
            group_key=group.group_key,
            group_label=group.group_label,
            is_selected=True,
            sample_quantity_expression=group.sample_quantity_expression,
            sample_note=group.sample_note,
        )
        for index, group in enumerate(
            sorted(active.groups, key=lambda item: item.group_order),
            start=1,
        )
    )
    rows = tuple(
        ProjectMatrixDraftRow(
            draft_row_id=f"pmdr-{uuid4().hex}",
            project_matrix_draft_id=draft_id,
            source_row_snapshot_id=row.source_row_snapshot_id,
            row_order=index,
            test_item=row.test_item,
            source_section=row.source_section,
            method=row.method,
            condition=row.condition,
            requirement=row.requirement,
            is_sample_row=False,
        )
        for index, row in enumerate(
            sorted(active.rows, key=lambda item: item.row_order),
            start=1,
        )
    )
    group_id_map = {
        group_from_active.confirmed_group_id: draft_group.draft_group_id
        for group_from_active, draft_group in zip(
            sorted(active.groups, key=lambda item: item.group_order),
            groups,
            strict=False,
        )
    }
    row_id_map = {
        row_from_active.confirmed_row_id: draft_row.draft_row_id
        for row_from_active, draft_row in zip(
            sorted(active.rows, key=lambda item: item.row_order),
            rows,
            strict=False,
        )
    }
    cells: list[ProjectMatrixDraftCell] = []
    seen_identity: set[tuple[str, str]] = set()
    for cell in active.cells:
        draft_row_id = row_id_map.get(cell.confirmed_row_id)
        draft_group_id = group_id_map.get(cell.confirmed_group_id)
        if draft_row_id is None or draft_group_id is None:
            continue
        cell_value = cell.cell_value.strip()
        if not cell_value:
            continue
        identity = (draft_row_id, draft_group_id)
        if identity in seen_identity:
            continue
        seen_identity.add(identity)
        cells.append(
            ProjectMatrixDraftCell(
                draft_cell_id=f"pmdc-{uuid4().hex}",
                project_matrix_draft_id=draft_id,
                draft_row_id=draft_row_id,
                draft_group_id=draft_group_id,
                cell_value=cell_value,
            )
        )
    return ProjectMatrixDraftSnapshot(
        record=record,
        groups=groups,
        rows=rows,
        cells=tuple(cells),
    )


def _build_confirmed_snapshot_from_revision_draft(
    *,
    draft: ProjectMatrixDraftSnapshot,
    selected_groups: tuple[ProjectMatrixDraftGroup, ...],
    confirmed_by: str,
    confirmed_revision: int,
    source_import_id: str,
) -> ConfirmedMatrixSnapshot:
    confirmed_matrix_id = f"cmv-{uuid4().hex}"
    confirmed_at = _utc_now()
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id=confirmed_matrix_id,
        project_id=draft.record.project_id,
        project_matrix_draft_id=draft.record.project_matrix_draft_id,
        source_import_id=source_import_id,
        source_snapshot_id=draft.record.source_snapshot_id,
        confirmed_revision=confirmed_revision,
        is_active_authority=True,
        status=ConfirmedMatrixStatus.CONFIRMED,
        confirmed_by=confirmed_by,
        confirmed_at=confirmed_at,
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
    return ConfirmedMatrixSnapshot(
        version=version,
        groups=tuple(groups),
        rows=tuple(rows),
        cells=tuple(cells),
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
