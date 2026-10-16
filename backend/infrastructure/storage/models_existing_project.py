"""Local location/provenance links, never generated-folder or LTR authority."""
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.infrastructure.storage.database import Base


class ExistingProjectLocationModel(Base):
    __tablename__ = "existing_project_locations"
    location_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    root_path: Mapped[str] = mapped_column(Text, unique=True)
    management_number: Mapped[str] = mapped_column(String(128))
    source_number: Mapped[str | None] = mapped_column(String(128))
    source_project_id: Mapped[str | None] = mapped_column(String(64))
    source_kind: Mapped[str] = mapped_column(String(32))
    source_fingerprint: Mapped[str] = mapped_column(String(64))
    root_identity: Mapped[str] = mapped_column(String(64))
    relocation_history: Mapped[str] = mapped_column(Text, default="[]")
    decision_fingerprint: Mapped[str] = mapped_column(String(64))
    approval_token: Mapped[str] = mapped_column(String(64))
    revision: Mapped[int] = mapped_column(Integer, default=0)
    registered_at: Mapped[str] = mapped_column(String(64))

