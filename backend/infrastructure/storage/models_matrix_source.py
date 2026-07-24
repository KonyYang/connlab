"""SQLAlchemy models for Source Matrix import persistence."""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.storage.database import Base


class SourceMatrixImportRecordModel(Base):
    """Database row for one Source Matrix import metadata record."""

    __tablename__ = "source_matrix_import_records"

    import_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    draft_id: Mapped[str | None] = mapped_column(String(64), index=True)
    source_document_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    source_document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_format: Mapped[str] = mapped_column(String(64), nullable=False)
    source_asset_id: Mapped[str | None] = mapped_column(String(64))
    source_case_id: Mapped[str | None] = mapped_column(String(64))
    source_draft_id: Mapped[str | None] = mapped_column(String(64))
    import_status: Mapped[str] = mapped_column(String(64), nullable=False)
    source_spec_number: Mapped[str | None] = mapped_column(String(255))
    source_spec_revision: Mapped[str | None] = mapped_column(String(128))
    parse_time: Mapped[str] = mapped_column(String(64), nullable=False)
    parser_version: Mapped[str] = mapped_column(String(128), nullable=False)
    payload_schema_version: Mapped[str] = mapped_column(String(64), nullable=False)
    source_preview_payload_json: Mapped[str | None] = mapped_column(Text)
    warnings_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    blockers_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    selected_group_keys_at_import_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
    )
    task261_commit_fingerprint: Mapped[str | None] = mapped_column(
        String(128),
        index=True,
    )
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)


class SourceMatrixSnapshotModel(Base):
    """Database row for one persisted Source Matrix snapshot root."""

    __tablename__ = "source_matrix_snapshots"

    snapshot_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    import_id: Mapped[str] = mapped_column(
        ForeignKey("source_matrix_import_records.import_id"),
        nullable=False,
        index=True,
        unique=True,
    )
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    source_table_index: Mapped[int | None] = mapped_column(Integer)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    group_count: Mapped[int] = mapped_column(Integer, nullable=False)
    cell_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)


class SourceMatrixRowSnapshotModel(Base):
    """Database row for one Source Matrix snapshot row."""

    __tablename__ = "source_matrix_row_snapshots"
    __table_args__ = (
        UniqueConstraint("snapshot_id", "row_order", name="uq_source_matrix_row_order"),
    )

    row_snapshot_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("source_matrix_snapshots.snapshot_id"),
        nullable=False,
        index=True,
    )
    row_order: Mapped[int] = mapped_column(Integer, nullable=False)
    source_row_index: Mapped[int | None] = mapped_column(Integer)
    test_item: Mapped[str] = mapped_column(Text, nullable=False)
    source_section: Mapped[str | None] = mapped_column(Text)
    is_sample_row: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    method: Mapped[str | None] = mapped_column(Text)
    condition: Mapped[str | None] = mapped_column(Text)
    requirement: Mapped[str | None] = mapped_column(Text)


class SourceMatrixGroupSnapshotModel(Base):
    """Database row for one Source Matrix snapshot group column."""

    __tablename__ = "source_matrix_group_snapshots"
    __table_args__ = (
        UniqueConstraint("snapshot_id", "group_order", name="uq_source_matrix_group_order"),
    )

    group_snapshot_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("source_matrix_snapshots.snapshot_id"),
        nullable=False,
        index=True,
    )
    group_order: Mapped[int] = mapped_column(Integer, nullable=False)
    group_key: Mapped[str] = mapped_column(String(255), nullable=False)
    group_label: Mapped[str] = mapped_column(String(255), nullable=False)
    sample_size: Mapped[int | None] = mapped_column(Integer)
    sample_quantity_expression: Mapped[str | None] = mapped_column(Text)
    sample_note: Mapped[str | None] = mapped_column(Text)


class SourceMatrixCellSnapshotModel(Base):
    """Database row for one sparse non-empty Source Matrix cell."""

    __tablename__ = "source_matrix_cell_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "snapshot_id",
            "row_snapshot_id",
            "group_snapshot_id",
            name="uq_source_matrix_cell_identity",
        ),
    )

    cell_snapshot_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("source_matrix_snapshots.snapshot_id"),
        nullable=False,
        index=True,
    )
    row_snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("source_matrix_row_snapshots.row_snapshot_id"),
        nullable=False,
    )
    group_snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("source_matrix_group_snapshots.group_snapshot_id"),
        nullable=False,
    )
    cell_value: Mapped[str] = mapped_column(Text, nullable=False)


class SourceMatrixDurationAuthorityModel(Base):
    """Structured duration authority captured with one source snapshot."""

    __tablename__ = "source_matrix_duration_authorities"
    __table_args__ = (
        UniqueConstraint(
            "source_snapshot_id",
            "source_group_snapshot_id",
            "source_row_snapshot_id",
            "step_sequence",
            "step_suffix_note",
            name="uq_source_matrix_duration_authority_identity",
        ),
        CheckConstraint("step_sequence > 0", name="ck_source_duration_step_positive"),
        CheckConstraint("duration_value > 0", name="ck_source_duration_value_positive"),
        CheckConstraint(
            "normalized_hours > 0",
            name="ck_source_duration_hours_positive",
        ),
        CheckConstraint("status = 'usable'", name="ck_source_duration_status"),
    )

    source_duration_authority_id: Mapped[str] = mapped_column(
        String(64), primary_key=True
    )
    source_snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("source_matrix_snapshots.snapshot_id"),
        nullable=False,
        index=True,
    )
    source_group_snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("source_matrix_group_snapshots.group_snapshot_id"),
        nullable=False,
    )
    source_row_snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("source_matrix_row_snapshots.row_snapshot_id"),
        nullable=False,
    )
    step_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    step_suffix_note: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    duration_value: Mapped[object] = mapped_column(Numeric, nullable=False)
    duration_unit: Mapped[str] = mapped_column(String(16), nullable=False)
    normalized_hours: Mapped[object] = mapped_column(Numeric, nullable=False)
    source_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    source_field: Mapped[str] = mapped_column(String(128), nullable=False)
    source_import_id: Mapped[str | None] = mapped_column(String(64))
    source_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    lineage_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    authority_revision: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    diagnostic_code: Mapped[str | None] = mapped_column(String(64))
    diagnostic_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)
