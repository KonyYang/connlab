"""Historical folder registrations, deliberately separate from business Projects."""
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.storage.database import Base


class LegacyProjectRecordModel(Base):
    __tablename__ = "legacy_project_records"

    record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    number: Mapped[str | None] = mapped_column(String(128))
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[str | None] = mapped_column(Text)
    folder_path: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_path: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    notes_json: Mapped[str] = mapped_column(Text, nullable=False)
    imported_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
