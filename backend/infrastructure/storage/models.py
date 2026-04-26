"""SQLAlchemy table models for ConnLab MVP persistence."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.infrastructure.storage.database import Base


class ProjectModel(Base):
    """Database row for a project."""

    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_no: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    requestor: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    business_unit: Mapped[str | None] = mapped_column(String(255))
    created_on: Mapped[date | None] = mapped_column(Date)


class ApplicationFormModel(Base):
    """Database row for an application form."""

    __tablename__ = "application_forms"

    form_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    form_no: Mapped[str] = mapped_column(String(128), nullable=False)
    revision: Mapped[str] = mapped_column(String(64), nullable=False)
    requester: Mapped[str] = mapped_column(String(255), nullable=False)
    request_date: Mapped[date | None] = mapped_column(Date)
    phone: Mapped[str | None] = mapped_column(String(128))
    email: Mapped[str | None] = mapped_column(String(255))
    business_unit: Mapped[str | None] = mapped_column(String(255))
    manufacturing_site: Mapped[str | None] = mapped_column(String(255))
    requested_testing: Mapped[str | None] = mapped_column(Text)
    subcontract_allowed: Mapped[bool | None] = mapped_column(Boolean)


class SampleInfoModel(Base):
    """Database row for project sample information."""

    __tablename__ = "sample_infos"

    sample_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    part_number: Mapped[str] = mapped_column(String(255), nullable=False)
    revision: Mapped[str | None] = mapped_column(String(64))
    lot_or_traceability: Mapped[str | None] = mapped_column(String(255))
    material: Mapped[str | None] = mapped_column(String(255))
    plating: Mapped[str | None] = mapped_column(String(255))
    housing_material: Mapped[str | None] = mapped_column(String(255))
    quantity: Mapped[int | None] = mapped_column(Integer)


class PrecheckResultModel(Base):
    """Database row for a precheck result."""

    __tablename__ = "precheck_results"

    result_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    application_form_id: Mapped[str] = mapped_column(
        ForeignKey("application_forms.form_id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    checked_on: Mapped[date | None] = mapped_column(Date)
    issues: Mapped[list["PrecheckIssueModel"]] = relationship(
        back_populates="result",
        cascade="all, delete-orphan",
    )


class PrecheckIssueModel(Base):
    """Database row for a precheck issue."""

    __tablename__ = "precheck_issues"

    issue_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    result_id: Mapped[str] = mapped_column(ForeignKey("precheck_results.result_id"))
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    level: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    field_name: Mapped[str | None] = mapped_column(String(255))
    result: Mapped[PrecheckResultModel] = relationship(back_populates="issues")


class LtrRecordModel(Base):
    """Database row for an LTR record."""

    __tablename__ = "ltr_records"

    ltr_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    ltr_number: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    registered_on: Mapped[date | None] = mapped_column(Date)


class ProjectFolderRecordModel(Base):
    """Database row for a generated project folder."""

    __tablename__ = "project_folder_records"

    folder_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    folder_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_on: Mapped[date | None] = mapped_column(Date)


class FileAssetModel(Base):
    """Database row for a project file asset."""

    __tablename__ = "file_assets"

    asset_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(64), nullable=False)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    original_name: Mapped[str | None] = mapped_column(String(255))
    registered_on: Mapped[date | None] = mapped_column(Date)
