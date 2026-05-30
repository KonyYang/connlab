"""Domain models for persisted Source Matrix import snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.domain.enums import SourceMatrixImportStatus


@dataclass(frozen=True, slots=True)
class SourceMatrixCellSnapshot:
    """One sparse non-empty cell in a Source Matrix snapshot."""

    cell_snapshot_id: str
    row_snapshot_id: str
    group_snapshot_id: str
    cell_value: str


@dataclass(frozen=True, slots=True)
class SourceMatrixRowSnapshot:
    """One row captured from imported Source Matrix structure."""

    row_snapshot_id: str
    row_order: int
    source_row_index: int | None
    test_item: str
    source_section: str | None = None
    is_sample_row: bool = False
    method: str | None = None
    condition: str | None = None
    requirement: str | None = None


@dataclass(frozen=True, slots=True)
class SourceMatrixGroupSnapshot:
    """One group column captured from imported Source Matrix structure."""

    group_snapshot_id: str
    group_order: int
    group_key: str
    group_label: str
    sample_size: int | None = None
    sample_quantity_expression: str | None = None
    sample_note: str | None = None


@dataclass(frozen=True, slots=True)
class SourceMatrixSnapshot:
    """Structured immutable Source Matrix snapshot body."""

    snapshot_id: str
    import_id: str
    project_id: str
    source_table_index: int | None
    rows: tuple[SourceMatrixRowSnapshot, ...] = field(default_factory=tuple)
    groups: tuple[SourceMatrixGroupSnapshot, ...] = field(default_factory=tuple)
    cells: tuple[SourceMatrixCellSnapshot, ...] = field(default_factory=tuple)
    created_at: str = ""


@dataclass(frozen=True, slots=True)
class SourceMatrixImportRecord:
    """Import metadata and identity for one Source Matrix snapshot."""

    import_id: str
    project_id: str
    draft_id: str | None
    source_document_path: str
    source_document_name: str
    source_format: str
    source_asset_id: str | None
    source_case_id: str | None
    source_draft_id: str | None
    import_status: SourceMatrixImportStatus
    source_spec_number: str | None
    source_spec_revision: str | None
    parse_time: str
    parser_version: str
    payload_schema_version: str
    source_preview_payload: dict[str, Any] | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)
    blockers: tuple[str, ...] = field(default_factory=tuple)
    selected_group_keys_at_import: tuple[str, ...] = field(default_factory=tuple)
    task261_commit_fingerprint: str | None = None
    created_at: str = ""
