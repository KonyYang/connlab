"""Persist manual group-completion events with their Matrix content signature."""
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from backend.infrastructure.storage.database import Base


class GroupCompletionEventModel(Base):
    __tablename__ = "group_completion_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False, index=True)
    group_lineage: Mapped[str] = mapped_column(String(64), nullable=False)
    group_key: Mapped[str] = mapped_column(String(255), nullable=False)
    matrix_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    signature: Mapped[str] = mapped_column(String(64), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    completed_at: Mapped[str | None] = mapped_column(String(64))
    recorded_at: Mapped[str] = mapped_column(String(64), nullable=False)
