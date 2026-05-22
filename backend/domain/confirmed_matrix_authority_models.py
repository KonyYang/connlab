"""Domain models for immutable Confirmed Matrix authority snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.domain.enums import ConfirmedMatrixStatus


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixVersion:
    """Root metadata for one immutable confirmed Matrix authority version."""

    confirmed_matrix_id: str
    project_id: str
    project_matrix_draft_id: str
    source_import_id: str
    source_snapshot_id: str
    confirmed_revision: int
    is_active_authority: bool
    status: ConfirmedMatrixStatus
    confirmed_by: str
    confirmed_at: str


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixGroup:
    """Confirmed selected group authority data."""

    confirmed_group_id: str
    confirmed_matrix_id: str
    draft_group_id: str
    source_group_snapshot_id: str | None
    group_order: int
    group_key: str
    group_label: str
    sample_quantity_expression: str
    sample_note: str | None = None


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixRow:
    """Confirmed non-sample row authority data."""

    confirmed_row_id: str
    confirmed_matrix_id: str
    draft_row_id: str
    source_row_snapshot_id: str | None
    row_order: int
    test_item: str
    source_section: str | None = None
    method: str | None = None
    condition: str | None = None
    requirement: str | None = None


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixCell:
    """Sparse non-empty confirmed cell for one confirmed row/group pair."""

    confirmed_cell_id: str
    confirmed_matrix_id: str
    confirmed_row_id: str
    confirmed_group_id: str
    draft_row_id: str
    draft_group_id: str
    cell_value: str


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixSnapshot:
    """Aggregate immutable confirmed Matrix authority snapshot."""

    version: ConfirmedMatrixVersion
    groups: tuple[ConfirmedMatrixGroup, ...] = field(default_factory=tuple)
    rows: tuple[ConfirmedMatrixRow, ...] = field(default_factory=tuple)
    cells: tuple[ConfirmedMatrixCell, ...] = field(default_factory=tuple)
