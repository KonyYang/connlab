"""Domain models for structured Project Matrix draft working copies."""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.domain.enums import ProjectMatrixDraftStatus


@dataclass(frozen=True, slots=True)
class ProjectMatrixDraftRecord:
    """Draft root metadata and lineage to Source Matrix snapshot."""

    project_matrix_draft_id: str
    project_id: str
    source_import_id: str | None
    source_snapshot_id: str
    status: ProjectMatrixDraftStatus
    created_at: str
    updated_at: str
    base_confirmed_matrix_id: str | None = None
    pre_test_buffer_days: str | None = None
    post_test_buffer_days: str | None = None
    sample_received_date: str | None = None
    planned_test_start_date: str | None = None
    planned_test_complete_date: str | None = None
    estimated_completion_date: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectMatrixDraftGroup:
    """Draft group working-copy record."""

    draft_group_id: str
    project_matrix_draft_id: str
    source_group_snapshot_id: str | None
    group_order: int
    group_key: str
    group_label: str
    is_selected: bool
    sample_quantity_expression: str | None = None
    sample_note: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectMatrixDraftRow:
    """Draft row working-copy record."""

    draft_row_id: str
    project_matrix_draft_id: str
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
class ProjectMatrixDraftCell:
    """Sparse non-empty draft cell for one row/group intersection."""

    draft_cell_id: str
    project_matrix_draft_id: str
    draft_row_id: str
    draft_group_id: str
    cell_value: str


@dataclass(frozen=True, slots=True)
class ProjectMatrixDraftSnapshot:
    """Aggregate structured Project Matrix draft snapshot."""

    record: ProjectMatrixDraftRecord
    groups: tuple[ProjectMatrixDraftGroup, ...] = field(default_factory=tuple)
    rows: tuple[ProjectMatrixDraftRow, ...] = field(default_factory=tuple)
    cells: tuple[ProjectMatrixDraftCell, ...] = field(default_factory=tuple)
