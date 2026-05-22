"""SQLAlchemy models for immutable Confirmed Matrix authority persistence."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.storage.database import Base


class ConfirmedMatrixVersionModel(Base):
    """Database row for one confirmed Matrix authority root."""

    __tablename__ = "confirmed_matrix_versions"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "confirmed_revision",
            name="uq_confirmed_matrix_project_revision",
        ),
        Index(
            "uq_confirmed_matrix_active_authority_per_project",
            "project_id",
            unique=True,
            sqlite_where=text("is_active_authority = 1"),
        ),
    )

    confirmed_matrix_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    project_matrix_draft_id: Mapped[str] = mapped_column(
        ForeignKey("project_matrix_draft_records.project_matrix_draft_id"),
        nullable=False,
        index=True,
    )
    source_import_id: Mapped[str] = mapped_column(
        ForeignKey("source_matrix_import_records.import_id"),
        nullable=False,
    )
    source_snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("source_matrix_snapshots.snapshot_id"),
        nullable=False,
    )
    confirmed_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active_authority: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    confirmed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    confirmed_at: Mapped[str] = mapped_column(String(64), nullable=False)


class ConfirmedMatrixGroupModel(Base):
    """Database row for one selected confirmed group authority record."""

    __tablename__ = "confirmed_matrix_groups"
    __table_args__ = (
        UniqueConstraint(
            "confirmed_matrix_id",
            "group_order",
            name="uq_confirmed_matrix_group_order",
        ),
        UniqueConstraint(
            "confirmed_matrix_id",
            "draft_group_id",
            name="uq_confirmed_matrix_group_draft_lineage",
        ),
    )

    confirmed_group_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    confirmed_matrix_id: Mapped[str] = mapped_column(
        ForeignKey("confirmed_matrix_versions.confirmed_matrix_id"),
        nullable=False,
        index=True,
    )
    draft_group_id: Mapped[str] = mapped_column(
        ForeignKey("project_matrix_draft_groups.draft_group_id"),
        nullable=False,
    )
    source_group_snapshot_id: Mapped[str | None] = mapped_column(
        ForeignKey("source_matrix_group_snapshots.group_snapshot_id"),
        nullable=True,
    )
    group_order: Mapped[int] = mapped_column(Integer, nullable=False)
    group_key: Mapped[str] = mapped_column(String(255), nullable=False)
    group_label: Mapped[str] = mapped_column(String(255), nullable=False)
    sample_quantity_expression: Mapped[str] = mapped_column(Text, nullable=False)
    sample_note: Mapped[str | None] = mapped_column(Text)


class ConfirmedMatrixRowModel(Base):
    """Database row for one non-sample confirmed row authority record."""

    __tablename__ = "confirmed_matrix_rows"
    __table_args__ = (
        UniqueConstraint(
            "confirmed_matrix_id",
            "row_order",
            name="uq_confirmed_matrix_row_order",
        ),
        UniqueConstraint(
            "confirmed_matrix_id",
            "draft_row_id",
            name="uq_confirmed_matrix_row_draft_lineage",
        ),
    )

    confirmed_row_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    confirmed_matrix_id: Mapped[str] = mapped_column(
        ForeignKey("confirmed_matrix_versions.confirmed_matrix_id"),
        nullable=False,
        index=True,
    )
    draft_row_id: Mapped[str] = mapped_column(
        ForeignKey("project_matrix_draft_rows.draft_row_id"),
        nullable=False,
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


class ConfirmedMatrixCellModel(Base):
    """Database row for one sparse non-empty confirmed row/group cell."""

    __tablename__ = "confirmed_matrix_cells"
    __table_args__ = (
        UniqueConstraint(
            "confirmed_matrix_id",
            "confirmed_row_id",
            "confirmed_group_id",
            name="uq_confirmed_matrix_cell_identity",
        ),
    )

    confirmed_cell_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    confirmed_matrix_id: Mapped[str] = mapped_column(
        ForeignKey("confirmed_matrix_versions.confirmed_matrix_id"),
        nullable=False,
        index=True,
    )
    confirmed_row_id: Mapped[str] = mapped_column(
        ForeignKey("confirmed_matrix_rows.confirmed_row_id"),
        nullable=False,
    )
    confirmed_group_id: Mapped[str] = mapped_column(
        ForeignKey("confirmed_matrix_groups.confirmed_group_id"),
        nullable=False,
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
