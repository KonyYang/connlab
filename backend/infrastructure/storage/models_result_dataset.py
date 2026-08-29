"""SQLAlchemy rows for immutable result and report draft revisions."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.storage.database import Base


class ResultDatasetRevisionModel(Base):
    __tablename__ = "result_dataset_revisions"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "dataset_type",
            "revision",
            name="uq_result_dataset_project_type_revision",
        ),
    )

    dataset_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dataset_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"), nullable=False, index=True
    )
    confirmed_matrix_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    confirmed_matrix_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    source_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    source_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    imported_at: Mapped[str] = mapped_column(String(64), nullable=False)
    imported_by: Mapped[str] = mapped_column(String(255), nullable=False)
    confirmed_at: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    parser_profile_version: Mapped[str] = mapped_column(String(128), nullable=False)
    validation_status: Mapped[str] = mapped_column(String(32), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)


class ReportDraftRevisionModel(Base):
    __tablename__ = "report_draft_revisions"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "revision",
            name="uq_report_draft_project_revision",
        ),
    )

    report_revision_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"), nullable=False, index=True
    )
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    confirmed_matrix_id: Mapped[str] = mapped_column(String(64), nullable=False)
    result_dataset_id: Mapped[str | None] = mapped_column(
        ForeignKey("result_dataset_revisions.dataset_id"), nullable=True, index=True
    )
    base_report_revision_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
