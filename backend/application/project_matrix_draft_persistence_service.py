"""Application service for Project Matrix draft working-copy persistence."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from backend.application.project_matrix_duration_authority_payload import (
    ProjectMatrixDraftPersistenceError,
    _build_draft_snapshot,
    _build_updated_snapshot,
    _resolve_selected_group_keys,
)

from backend.domain import (
    Project,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftSnapshot,
    SourceMatrixImportRecord,
    SourceMatrixSnapshot,
)


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
class ProjectMatrixDurationAuthorityInput:
    """Full replacement input for one draft duration authority."""

    draft_duration_authority_id: str | None
    draft_group_id: str
    draft_row_id: str
    step_sequence: int
    step_suffix_note: str | None
    duration_value: Decimal
    duration_unit: str
    source_kind: str
    source_field: str
    source_import_id: str | None
    source_fingerprint: str
    lineage_fingerprint: str
    authority_revision: str


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
    duration_authorities_present: bool = False
    duration_authorities: tuple[ProjectMatrixDurationAuthorityInput, ...] | None = None


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
