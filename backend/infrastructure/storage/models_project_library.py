"""Library membership and recoverable intake batches, separate from lifecycle."""
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from backend.infrastructure.storage.database import Base


class ProjectLibraryMemberModel(Base):
    __tablename__ = "project_library_members"
    member_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.project_id"), unique=True)
    ltr_number: Mapped[str | None] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    folder_path: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    source_project_id: Mapped[str | None] = mapped_column(String(64))
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    batch_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    disposition: Mapped[str] = mapped_column(String(32), nullable=False, default="working", server_default="working")
    snapshot_fingerprint: Mapped[str | None] = mapped_column(String(64))


class ProjectLibraryBatchModel(Base):
    __tablename__ = "project_library_batches"
    batch_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
