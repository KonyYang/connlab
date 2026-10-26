"""Append-only project report preparation snapshots; old LLCR rows stay unchanged."""
from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from backend.infrastructure.storage.database import Base


class ReportAuthoringRevisionModel(Base):
    __tablename__ = "report_authoring_revisions"
    __table_args__ = (UniqueConstraint("project_id", "revision", name="uq_report_authoring_revision"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False, index=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
