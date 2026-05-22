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


@dataclass(frozen=True, slots=True)
class CreateProjectMatrixDraftFromSourceImportCommand:
    """Input payload for creating one draft from source import snapshot."""

    project_id: str
    source_import_id: str
    selected_group_keys: tuple[str, ...] | None = None


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


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
