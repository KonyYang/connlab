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


class MaterialReceiptSettingsModel(Base):
    __tablename__ = "material_receipt_settings"
    settings_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    root_path: Mapped[str] = mapped_column(Text, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class MaterialReceiptEntryModel(Base):
    __tablename__ = "material_receipt_entries"
    receipt_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    number: Mapped[str | None] = mapped_column(String(128))
    product_name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    material_state: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    test_keywords: Mapped[str] = mapped_column(Text, nullable=False, default="")
    folder_path: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    batch_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class MaterialReceiptBatchModel(Base):
    __tablename__ = "material_receipt_batches"
    batch_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)


class ReportShortcutModel(Base):
    __tablename__ = "library_report_shortcuts"
    catalog_key: Mapped[str] = mapped_column(String(256), primary_key=True)
    role: Mapped[str] = mapped_column(String(16), primary_key=True)
    relative_path: Mapped[str] = mapped_column(Text, nullable=False)
