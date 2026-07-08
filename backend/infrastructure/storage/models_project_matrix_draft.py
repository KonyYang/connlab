"""SQLAlchemy models for Project Matrix draft working-copy persistence."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.storage.database import Base


class ProjectMatrixDraftRecordModel(Base):
    """Database row for one Project Matrix draft root."""

    __tablename__ = "project_matrix_draft_records"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "source_import_id",
            name="uq_project_matrix_draft_project_source_import",
        ),
        UniqueConstraint(
            "project_id",
            "base_confirmed_matrix_id",
            name="uq_project_matrix_draft_project_base_confirmed",
        ),
    )

    project_matrix_draft_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    source_import_id: Mapped[str | None] = mapped_column(
        ForeignKey("source_matrix_import_records.import_id"),
        nullable=True,
        index=True,
    )
    source_snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("source_matrix_snapshots.snapshot_id"),
        nullable=False,
    )
    base_confirmed_matrix_id: Mapped[str | None] = mapped_column(
        ForeignKey("confirmed_matrix_versions.confirmed_matrix_id"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)
    pre_test_buffer_days: Mapped[str | None] = mapped_column(String(64))
    post_test_buffer_days: Mapped[str | None] = mapped_column(String(64))
    sample_received_date: Mapped[str | None] = mapped_column(String(32))
    planned_test_start_date: Mapped[str | None] = mapped_column(String(32))
    planned_test_complete_date: Mapped[str | None] = mapped_column(String(32))
    estimated_completion_date: Mapped[str | None] = mapped_column(String(32))


class ProjectMatrixDraftGroupModel(Base):
    """Database row for one draft group."""

    __tablename__ = "project_matrix_draft_groups"
    __table_args__ = (
        UniqueConstraint(
            "project_matrix_draft_id",
            "group_order",
            name="uq_project_matrix_draft_group_order",
        ),
        UniqueConstraint(
            "project_matrix_draft_id",
            "source_group_snapshot_id",
            name="uq_project_matrix_draft_group_source_lineage",
        ),
    )

    draft_group_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_matrix_draft_id: Mapped[str] = mapped_column(
        ForeignKey("project_matrix_draft_records.project_matrix_draft_id"),
        nullable=False,
        index=True,
    )
    source_group_snapshot_id: Mapped[str | None] = mapped_column(
        ForeignKey("source_matrix_group_snapshots.group_snapshot_id"),
        nullable=True,
    )
    group_order: Mapped[int] = mapped_column(Integer, nullable=False)
    group_key: Mapped[str] = mapped_column(String(255), nullable=False)
    group_label: Mapped[str] = mapped_column(String(255), nullable=False)
    is_selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sample_quantity_expression: Mapped[str | None] = mapped_column(Text)
    sample_note: Mapped[str | None] = mapped_column(Text)


class ProjectMatrixDraftRowModel(Base):
    """Database row for one draft row."""

    __tablename__ = "project_matrix_draft_rows"
    __table_args__ = (
        UniqueConstraint(
            "project_matrix_draft_id",
            "row_order",
            name="uq_project_matrix_draft_row_order",
        ),
        UniqueConstraint(
            "project_matrix_draft_id",
            "source_row_snapshot_id",
            name="uq_project_matrix_draft_row_source_lineage",
        ),
    )

    draft_row_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_matrix_draft_id: Mapped[str] = mapped_column(
        ForeignKey("project_matrix_draft_records.project_matrix_draft_id"),
        nullable=False,
        index=True,
    )
    source_row_snapshot_id: Mapped[str | None] = mapped_column(
        ForeignKey("source_matrix_row_snapshots.row_snapshot_id"),
        nullable=True,
    )
    row_order: Mapped[int] = mapped_column(Integer, nullable=False)
    test_item: Mapped[str] = mapped_column(Text, nullable=False)
    source_section: Mapped[str | None] = mapped_column(Text)
    method: Mapped[str | None] = mapped_column(Text)
    condition: Mapped[str | None] = mapped_column(Text)
    requirement: Mapped[str | None] = mapped_column(Text)
    day_expression: Mapped[str | None] = mapped_column(String(64))
    is_sample_row: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ProjectMatrixDraftCellModel(Base):
    """Database row for one sparse non-empty draft cell."""

    __tablename__ = "project_matrix_draft_cells"
    __table_args__ = (
        UniqueConstraint(
            "project_matrix_draft_id",
            "draft_row_id",
            "draft_group_id",
            name="uq_project_matrix_draft_cell_identity",
        ),
    )

    draft_cell_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_matrix_draft_id: Mapped[str] = mapped_column(
        ForeignKey("project_matrix_draft_records.project_matrix_draft_id"),
        nullable=False,
        index=True,
    )
    draft_row_id: Mapped[str] = mapped_column(
        ForeignKey("project_matrix_draft_rows.draft_row_id"),
        nullable=False,
    )
    draft_group_id: Mapped[str] = mapped_column(
        ForeignKey("project_matrix_draft_groups.draft_group_id"),
        nullable=False,
    )
    cell_value: Mapped[str] = mapped_column(Text, nullable=False)


class ProjectMatrixDraftStepQuantityModel(Base):
    """Database row for one draft Matrix Step quantity setup record."""

    __tablename__ = "project_matrix_draft_step_quantities"
    __table_args__ = (
        UniqueConstraint(
            "project_matrix_draft_id",
            "draft_group_id",
            "draft_row_id",
            "step_sequence",
            "step_suffix_note",
            name="uq_project_matrix_draft_step_quantity_identity",
        ),
    )

    draft_step_quantity_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_matrix_draft_id: Mapped[str] = mapped_column(
        ForeignKey("project_matrix_draft_records.project_matrix_draft_id"),
        nullable=False,
        index=True,
    )
    draft_group_id: Mapped[str] = mapped_column(
        ForeignKey("project_matrix_draft_groups.draft_group_id"),
        nullable=False,
    )
    draft_row_id: Mapped[str] = mapped_column(
        ForeignKey("project_matrix_draft_rows.draft_row_id"),
        nullable=False,
    )
    step_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    step_suffix_note: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    raw_token: Mapped[str | None] = mapped_column(String(64))
    test_points_per_sample: Mapped[str | None] = mapped_column(String(64))
    readings_per_point: Mapped[str | None] = mapped_column(String(64))
    contact_points_per_sample: Mapped[str | None] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    review_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    review_reason: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)
