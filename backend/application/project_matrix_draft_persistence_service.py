"""Application service for Project Matrix draft working-copy persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from backend.domain import (
    Project,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    SourceMatrixImportRecord,
    SourceMatrixSnapshot,
)


class ProjectMatrixDraftPersistenceError(ValueError):
    """Raised when a Project Matrix draft persistence request is invalid."""


class ProjectMatrixDraftPersistenceConflictError(ProjectMatrixDraftPersistenceError):
    """Raised when draft creation violates uniqueness constraints."""


class ProjectMatrixDraftPersistenceNotFoundError(LookupError):
    """Raised when Project or Source Matrix lineage cannot be found."""


class ProjectStore(Protocol):
    """Project lookup operations required by this service."""

    def get(self, project_id: str) -> Project | None:
        """Return one project by id."""


class SourceMatrixImportStore(Protocol):
    """Source Matrix lineage lookups required by this service."""

    def get_import(self, import_id: str) -> SourceMatrixImportRecord | None:
        """Return one source matrix import record."""

    def get_snapshot_by_import(self, import_id: str) -> SourceMatrixSnapshot | None:
        """Return one source matrix snapshot aggregate."""


class ProjectMatrixDraftStore(Protocol):
    """Draft persistence operations required by this service."""

    def create_snapshot(self, snapshot: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftSnapshot:
        """Persist one draft aggregate."""

    def get_by_project_and_source_import(
        self,
        project_id: str,
        source_import_id: str,
    ) -> ProjectMatrixDraftRecord | None:
        """Return one draft record by project and source import lineage."""

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        """Return one draft aggregate by id."""

    def list_by_project(self, project_id: str) -> list[ProjectMatrixDraftRecord]:
        """Return draft records by project, newest first."""

    def replace_snapshot(self, snapshot: ProjectMatrixDraftSnapshot) -> ProjectMatrixDraftSnapshot:
        """Atomically replace one draft aggregate working copy."""


@dataclass(frozen=True, slots=True)
class CreateProjectMatrixDraftFromSourceImportCommand:
    """Input payload for creating one draft from source import snapshot."""

    project_id: str
    source_import_id: str
    selected_group_keys: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class ProjectMatrixDraftGroupInput:
    """Draft group payload used by save/update operations."""

    draft_group_id: str | None
    source_group_snapshot_id: str | None
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None = None
    sample_note: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectMatrixDraftRowInput:
    """Draft row payload used by save/update operations."""

    draft_row_id: str | None
    source_row_snapshot_id: str | None
    row_order: int
    test_item: str
    source_section: str | None = None
    method: str | None = None
    condition: str | None = None
    requirement: str | None = None
    day_expression: str | None = None
    is_sample_row: bool = False


@dataclass(frozen=True, slots=True)
class ProjectMatrixDraftCellInput:
    """Draft sparse cell payload used by save/update operations."""

    draft_row_id: str
    draft_group_id: str
    cell_value: str


@dataclass(frozen=True, slots=True)
class UpdateProjectMatrixDraftCommand:
    """Input payload for replacing one draft working copy."""

    project_id: str
    project_matrix_draft_id: str
    groups: tuple[ProjectMatrixDraftGroupInput, ...]
    rows: tuple[ProjectMatrixDraftRowInput, ...]
    cells: tuple[ProjectMatrixDraftCellInput, ...]
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None


class ProjectMatrixDraftPersistenceService:
    """Create structured Project Matrix draft working copies from Source Matrix snapshots."""

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        source_store: SourceMatrixImportStore,
        draft_store: ProjectMatrixDraftStore,
    ) -> None:
        self._projects = project_store
        self._source = source_store
        self._drafts = draft_store

    def create_from_source_import(
        self,
        command: CreateProjectMatrixDraftFromSourceImportCommand,
    ) -> ProjectMatrixDraftSnapshot:
        """Create one draft aggregate from immutable Source Matrix snapshot."""
        project = self._projects.get(command.project_id)
        if project is None:
            raise ProjectMatrixDraftPersistenceNotFoundError(
                f"Project not found: {command.project_id}"
            )
        import_record = self._source.get_import(command.source_import_id)
        if import_record is None or import_record.project_id != project.project_id:
            raise ProjectMatrixDraftPersistenceNotFoundError(
                f"Source matrix import not found: {command.source_import_id}"
            )
        if self._drafts.get_by_project_and_source_import(
            command.project_id,
            command.source_import_id,
        ):
            raise ProjectMatrixDraftPersistenceConflictError(
                "Project Matrix draft already exists for this source import."
            )
        source_snapshot = self._source.get_snapshot_by_import(command.source_import_id)
        if source_snapshot is None:
            raise ProjectMatrixDraftPersistenceNotFoundError(
                f"Source matrix snapshot not found for import: {command.source_import_id}"
            )
        if source_snapshot.project_id != command.project_id:
            raise ProjectMatrixDraftPersistenceError(
                "Source matrix snapshot project lineage mismatch."
            )
        selected_keys = _resolve_selected_group_keys(command, import_record, source_snapshot)
        draft_snapshot = _build_draft_snapshot(command, source_snapshot, selected_keys)
        return self._drafts.create_snapshot(draft_snapshot)

    def get_draft(
        self,
        *,
        project_id: str,
        project_matrix_draft_id: str,
    ) -> ProjectMatrixDraftSnapshot:
        """Return one Project-scoped draft aggregate."""
        project = self._projects.get(project_id)
        if project is None:
            raise ProjectMatrixDraftPersistenceNotFoundError(f"Project not found: {project_id}")
        draft = self._drafts.get(project_matrix_draft_id)
        if draft is None or draft.record.project_id != project_id:
            raise ProjectMatrixDraftPersistenceNotFoundError(
                "Project matrix draft not found."
            )
        return draft

    def list_drafts(self, *, project_id: str) -> list[ProjectMatrixDraftRecord]:
        """Return draft records in project scope."""
        project = self._projects.get(project_id)
        if project is None:
            raise ProjectMatrixDraftPersistenceNotFoundError(f"Project not found: {project_id}")
        return self._drafts.list_by_project(project_id)

    def update_draft(
        self,
        command: UpdateProjectMatrixDraftCommand,
    ) -> ProjectMatrixDraftSnapshot:
        """Replace one draft working copy aggregate while keeping draft identity."""
        existing = self.get_draft(
            project_id=command.project_id,
            project_matrix_draft_id=command.project_matrix_draft_id,
        )
        if len(command.groups) == 0:
            raise ProjectMatrixDraftPersistenceError("At least one group is required.")
        if len(command.rows) == 0:
            raise ProjectMatrixDraftPersistenceError("At least one row is required.")
        normalized = _build_updated_snapshot(existing, command)
        return self._drafts.replace_snapshot(normalized)


def _resolve_selected_group_keys(
    command: CreateProjectMatrixDraftFromSourceImportCommand,
    import_record: SourceMatrixImportRecord,
    source_snapshot: SourceMatrixSnapshot,
) -> set[str]:
    available_keys = {group.group_key for group in source_snapshot.groups}
    explicit = command.selected_group_keys
    if explicit is not None:
        selected = {item.strip() for item in explicit if item.strip()}
        unknown = sorted(selected - available_keys)
        if unknown:
            raise ProjectMatrixDraftPersistenceError(
                f"Unknown selected group keys: {', '.join(unknown)}"
            )
        return selected
    imported_keys = {item.strip() for item in import_record.selected_group_keys_at_import if item.strip()}
    if imported_keys:
        return imported_keys & available_keys
    return available_keys


def _build_draft_snapshot(
    command: CreateProjectMatrixDraftFromSourceImportCommand,
    source_snapshot: SourceMatrixSnapshot,
    selected_keys: set[str],
) -> ProjectMatrixDraftSnapshot:
    now = _utc_now()
    draft_id = f"pmd-{uuid4().hex}"
    record = ProjectMatrixDraftRecord(
        project_matrix_draft_id=draft_id,
        project_id=command.project_id,
        source_import_id=command.source_import_id,
        source_snapshot_id=source_snapshot.snapshot_id,
        status=ProjectMatrixDraftStatus.DRAFT,
        created_at=now,
        updated_at=now,
        base_confirmed_matrix_id=None,
    )
    groups = tuple(
        ProjectMatrixDraftGroup(
            draft_group_id=f"pmdg-{uuid4().hex}",
            project_matrix_draft_id=draft_id,
            source_group_snapshot_id=group.group_snapshot_id,
            group_order=group.group_order,
            group_key=group.group_key,
            group_label=group.group_label,
            is_selected=group.group_key in selected_keys,
            sample_quantity_expression=group.sample_quantity_expression,
            sample_note=group.sample_note,
        )
        for group in source_snapshot.groups
    )
    rows = tuple(
        ProjectMatrixDraftRow(
            draft_row_id=f"pmdr-{uuid4().hex}",
            project_matrix_draft_id=draft_id,
            source_row_snapshot_id=row.row_snapshot_id,
            row_order=row.row_order,
            test_item=row.test_item,
            source_section=row.source_section,
            method=None,
            condition=None,
            requirement=None,
            day_expression=None,
            is_sample_row=row.is_sample_row,
        )
        for row in source_snapshot.rows
    )
    row_by_source = {row.source_row_snapshot_id: row.draft_row_id for row in rows}
    group_by_source = {group.source_group_snapshot_id: group.draft_group_id for group in groups}
    cells: list[ProjectMatrixDraftCell] = []
    for source_cell in source_snapshot.cells:
        cell_value = source_cell.cell_value.strip()
        if not cell_value:
            continue
        mapped_row = row_by_source.get(source_cell.row_snapshot_id)
        mapped_group = group_by_source.get(source_cell.group_snapshot_id)
        if mapped_row is None or mapped_group is None:
            continue
        cells.append(
            ProjectMatrixDraftCell(
                draft_cell_id=f"pmdc-{uuid4().hex}",
                project_matrix_draft_id=draft_id,
                draft_row_id=mapped_row,
                draft_group_id=mapped_group,
                cell_value=cell_value,
            )
        )
    return ProjectMatrixDraftSnapshot(
        record=record,
        groups=groups,
        rows=rows,
        cells=tuple(cells),
    )


def _build_updated_snapshot(
    existing: ProjectMatrixDraftSnapshot,
    command: UpdateProjectMatrixDraftCommand,
) -> ProjectMatrixDraftSnapshot:
    draft_id = existing.record.project_matrix_draft_id
    existing_group_by_id = {group.draft_group_id: group for group in existing.groups}
    existing_row_by_id = {row.draft_row_id: row for row in existing.rows}
    existing_group_by_source = {
        group.source_group_snapshot_id: group
        for group in existing.groups
        if group.source_group_snapshot_id
    }
    existing_row_by_source = {
        row.source_row_snapshot_id: row
        for row in existing.rows
        if row.source_row_snapshot_id
    }
    group_id_map: dict[str, str] = {}
    row_id_map: dict[str, str] = {}
    groups: list[ProjectMatrixDraftGroup] = []
    rows: list[ProjectMatrixDraftRow] = []
    for index, group_input in enumerate(command.groups, start=1):
        group = _normalized_group(
            draft_id=draft_id,
            index=index,
            group_input=group_input,
            group_id_map=group_id_map,
            existing_group_by_id=existing_group_by_id,
            existing_group_by_source=existing_group_by_source,
        )
        groups.append(group)
    for index, row_input in enumerate(command.rows, start=1):
        row = _normalized_row(
            draft_id=draft_id,
            index=index,
            row_input=row_input,
            row_id_map=row_id_map,
            existing_row_by_id=existing_row_by_id,
            existing_row_by_source=existing_row_by_source,
        )
        rows.append(row)
    row_ids = {row.draft_row_id for row in rows}
    group_ids = {group.draft_group_id for group in groups}
    cells: list[ProjectMatrixDraftCell] = []
    seen_cell_identity: set[tuple[str, str]] = set()
    for cell_input in command.cells:
        raw_row_id = cell_input.draft_row_id.strip()
        raw_group_id = cell_input.draft_group_id.strip()
        mapped_row_id = row_id_map.get(raw_row_id, raw_row_id)
        mapped_group_id = group_id_map.get(raw_group_id, raw_group_id)
        if mapped_row_id not in row_ids:
            raise ProjectMatrixDraftPersistenceError(
                f"Cell references unknown row id: {cell_input.draft_row_id}"
            )
        if mapped_group_id not in group_ids:
            raise ProjectMatrixDraftPersistenceError(
                f"Cell references unknown group id: {cell_input.draft_group_id}"
            )
        cell_value = cell_input.cell_value.strip()
        if not cell_value:
            continue
        identity = (mapped_row_id, mapped_group_id)
        if identity in seen_cell_identity:
            continue
        seen_cell_identity.add(identity)
        cells.append(
            ProjectMatrixDraftCell(
                draft_cell_id=f"pmdc-{uuid4().hex}",
                project_matrix_draft_id=draft_id,
                draft_row_id=mapped_row_id,
                draft_group_id=mapped_group_id,
                cell_value=cell_value,
            )
        )
    now = _utc_now()
    updated_record = ProjectMatrixDraftRecord(
        project_matrix_draft_id=existing.record.project_matrix_draft_id,
        project_id=existing.record.project_id,
        source_import_id=existing.record.source_import_id,
        source_snapshot_id=existing.record.source_snapshot_id,
        status=existing.record.status,
        created_at=existing.record.created_at,
        updated_at=now,
        base_confirmed_matrix_id=existing.record.base_confirmed_matrix_id,
        pre_test_buffer_days=_normalize_optional_text(command.pre_test_buffer_days),
        post_test_buffer_days=_normalize_optional_text(command.post_test_buffer_days),
        sample_received_date=_normalize_optional_text(command.sample_received_date),
        planned_test_start_date=_normalize_optional_text(command.planned_test_start_date),
        planned_test_complete_date=_normalize_optional_text(command.planned_test_complete_date),
        estimated_completion_date=_normalize_optional_text(command.estimated_completion_date),
    )
    return ProjectMatrixDraftSnapshot(
        record=updated_record,
        groups=tuple(groups),
        rows=tuple(rows),
        cells=tuple(cells),
    )


def _normalized_group(
    *,
    draft_id: str,
    index: int,
    group_input: ProjectMatrixDraftGroupInput,
    group_id_map: dict[str, str],
    existing_group_by_id: dict[str, ProjectMatrixDraftGroup],
    existing_group_by_source: dict[str, ProjectMatrixDraftGroup],
) -> ProjectMatrixDraftGroup:
    raw_group_id = (group_input.draft_group_id or "").strip()
    raw_source_id = (group_input.source_group_snapshot_id or "").strip()
    candidate = existing_group_by_id.get(raw_group_id) if raw_group_id else None
    if candidate is None and raw_source_id:
        candidate = existing_group_by_source.get(raw_source_id)
    draft_group_id = candidate.draft_group_id if candidate else f"pmdg-{uuid4().hex}"
    source_group_snapshot_id = candidate.source_group_snapshot_id if candidate else (raw_source_id or None)
    if raw_group_id:
        group_id_map[raw_group_id] = draft_group_id
    normalized_group_key = group_input.group_key.strip() or f"group_{index}"
    normalized_group_label = group_input.group_label.strip() or normalized_group_key
    sample_quantity_expression = _normalize_optional_text(group_input.sample_quantity_expression)
    sample_note = _normalize_optional_text(group_input.sample_note)
    return ProjectMatrixDraftGroup(
        draft_group_id=draft_group_id,
        project_matrix_draft_id=draft_id,
        source_group_snapshot_id=source_group_snapshot_id,
        group_order=index,
        group_key=normalized_group_key,
        group_label=normalized_group_label,
        is_selected=bool(group_input.is_selected),
        sample_quantity_expression=sample_quantity_expression,
        sample_note=sample_note,
    )


def _normalized_row(
    *,
    draft_id: str,
    index: int,
    row_input: ProjectMatrixDraftRowInput,
    row_id_map: dict[str, str],
    existing_row_by_id: dict[str, ProjectMatrixDraftRow],
    existing_row_by_source: dict[str, ProjectMatrixDraftRow],
) -> ProjectMatrixDraftRow:
    raw_row_id = (row_input.draft_row_id or "").strip()
    raw_source_id = (row_input.source_row_snapshot_id or "").strip()
    candidate = existing_row_by_id.get(raw_row_id) if raw_row_id else None
    if candidate is None and raw_source_id:
        candidate = existing_row_by_source.get(raw_source_id)
    draft_row_id = candidate.draft_row_id if candidate else f"pmdr-{uuid4().hex}"
    source_row_snapshot_id = candidate.source_row_snapshot_id if candidate else (raw_source_id or None)
    if raw_row_id:
        row_id_map[raw_row_id] = draft_row_id
    test_item = row_input.test_item.strip()
    source_section = _normalize_optional_text(row_input.source_section)
    method = _normalize_optional_text(row_input.method)
    condition = _normalize_optional_text(row_input.condition)
    requirement = _normalize_optional_text(row_input.requirement)
    day_expression = _normalize_optional_text(row_input.day_expression)
    return ProjectMatrixDraftRow(
        draft_row_id=draft_row_id,
        project_matrix_draft_id=draft_id,
        source_row_snapshot_id=source_row_snapshot_id,
        row_order=index,
        test_item=test_item,
        source_section=source_section,
        method=method,
        condition=condition,
        requirement=requirement,
        day_expression=day_expression,
        is_sample_row=bool(row_input.is_sample_row),
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
