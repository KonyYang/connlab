"""Additive persistence model for independent Project Schedule authority."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.storage.database import Base


class ProjectScheduleRevisionModel(Base):
    __tablename__ = "project_schedule_revisions"
    __table_args__ = (
        UniqueConstraint("project_id", "revision_sequence", name="uq_project_schedule_revision_sequence"),
        CheckConstraint("revision_sequence > 0", name="ck_project_schedule_revision_positive"),
        CheckConstraint("state IN ('confirmed','superseded')", name="ck_project_schedule_revision_state"),
        Index(
            "uq_project_schedule_active_per_project",
            "project_id",
            unique=True,
            sqlite_where=text("state = 'confirmed'"),
        ),
    )

    revision_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False, index=True)
    revision_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    matrix_input_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    based_on_confirmed_matrix_id: Mapped[str | None] = mapped_column(
        ForeignKey("confirmed_matrix_versions.confirmed_matrix_id"), nullable=True
    )
    based_on_confirmed_matrix_revision: Mapped[int | None] = mapped_column(Integer, nullable=True)
    based_on_basic_information_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sample_received_date: Mapped[str] = mapped_column(String(32), nullable=False)
    post_test_buffer_days: Mapped[str] = mapped_column(String(64), nullable=False)
    test_start_date: Mapped[str] = mapped_column(String(32), nullable=False)
    test_complete_date: Mapped[str] = mapped_column(String(32), nullable=False)
    estimated_completion_date: Mapped[str] = mapped_column(String(32), nullable=False)
    confirmed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    confirmed_at: Mapped[str] = mapped_column(String(64), nullable=False)
    superseded_at: Mapped[str | None] = mapped_column(String(64))
    superseded_reason: Mapped[str | None] = mapped_column(Text)
