"""SQLAlchemy table models for ConnLab MVP persistence."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.infrastructure.storage.database import Base


class ProjectModel(Base):
    """Database row for a project."""

    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
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
    reference_doc: Mapped[str | None] = mapped_column(String(255))
    lab_test_request_number: Mapped[str | None] = mapped_column(String(128))
    project_number: Mapped[str | None] = mapped_column(String(128))
    requested_completion_date: Mapped[str | None] = mapped_column(String(128))
    results_format: Mapped[str | None] = mapped_column(String(128))
    test_type: Mapped[str | None] = mapped_column(String(128))
    sample_status: Mapped[str | None] = mapped_column(String(128))
    project_type: Mapped[str | None] = mapped_column(String(128))
    post_testing_disposition: Mapped[str | None] = mapped_column(Text)
    confidential: Mapped[str | None] = mapped_column(String(128))
    subcontract: Mapped[str | None] = mapped_column(String(128))
    additional_information: Mapped[str | None] = mapped_column(Text)
    send_copies_recipients: Mapped[str | None] = mapped_column(Text)
    lab: Mapped[str | None] = mapped_column(String(128))
    assigned_personnel: Mapped[str | None] = mapped_column(String(255))
    received_date: Mapped[str | None] = mapped_column(String(128))
    estimated_completion_date: Mapped[str | None] = mapped_column(String(128))
    sample_condition: Mapped[str | None] = mapped_column(Text)


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
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    result: Mapped[PrecheckResultModel] = relationship(back_populates="issues")


class LtrRecordModel(Base):
    """Database row for an LTR record."""

    __tablename__ = "ltr_records"

    ltr_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    ltr_number: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    registered_on: Mapped[date | None] = mapped_column(Date)
    requested_by: Mapped[str | None] = mapped_column(String(255))
    requested_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)


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


class IntakePackageModel(Base):
    """Database row for a pre-project intake package."""

    __tablename__ = "intake_packages"

    package_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    source_original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_stored_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(512))
    sender_name: Mapped[str | None] = mapped_column(String(255))
    sender_email: Mapped[str | None] = mapped_column(String(255))
    recipients_json: Mapped[str | None] = mapped_column(Text)
    cc_json: Mapped[str | None] = mapped_column(Text)
    received_at: Mapped[str | None] = mapped_column(String(64))
    body_text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str | None] = mapped_column(String(64))
    updated_at: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)


class IntakeAssetModel(Base):
    """Database row for an intake asset before project confirmation."""

    __tablename__ = "intake_assets"

    asset_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    package_id: Mapped[str] = mapped_column(
        ForeignKey("intake_packages.package_id"),
        nullable=False,
    )
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    extension: Mapped[str] = mapped_column(String(64), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(255))
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    asset_role: Mapped[str] = mapped_column(String(64), nullable=False)
    candidate_score: Mapped[int | None] = mapped_column(Integer)
    content_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[str | None] = mapped_column(String(64))


class IntakeCaseModel(Base):
    """Database row for one selected intake application form."""

    __tablename__ = "intake_cases"

    case_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    package_id: Mapped[str] = mapped_column(
        ForeignKey("intake_packages.package_id"),
        nullable=False,
    )
    selected_form_asset_id: Mapped[str | None] = mapped_column(
        ForeignKey("intake_assets.asset_id"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmed_project_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[str | None] = mapped_column(String(64))
    updated_at: Mapped[str | None] = mapped_column(String(64))
    reviewer_notes: Mapped[str | None] = mapped_column(Text)


class IntakeDraftModel(Base):
    """Database row for an editable parser draft."""

    __tablename__ = "intake_drafts"

    draft_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("intake_cases.case_id"), nullable=False)
    parsed_fields_json: Mapped[str] = mapped_column(Text, nullable=False)
    sample_rows_json: Mapped[str | None] = mapped_column(Text)
    requested_testing_json: Mapped[str | None] = mapped_column(Text)
    field_confidence_json: Mapped[str | None] = mapped_column(Text)
    parser_warnings_json: Mapped[str | None] = mapped_column(Text)
    manual_overrides_json: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[str | None] = mapped_column(String(64))


class LookupOptionModel(Base):
    """Database row for backend-managed UI lookup options."""

    __tablename__ = "lookup_options"
    __table_args__ = (
        UniqueConstraint("group_key", "value", name="uq_lookup_options_group_value"),
    )

    option_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    group_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
