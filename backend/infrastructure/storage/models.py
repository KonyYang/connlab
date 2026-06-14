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


class ProjectTemporaryContextModel(Base):
    """Planning context captured for a no-LTR temporary project."""

    __tablename__ = "project_temporary_contexts"

    context_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        unique=True,
        index=True,
    )
    request_summary: Mapped[str | None] = mapped_column(Text)
    sample_description: Mapped[str | None] = mapped_column(Text)
    test_item: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    source_asset_ids_json: Mapped[str | None] = mapped_column(Text)


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


class ProjectCleanupAuditRecordModel(Base):
    """Database row for one controlled project cleanup action."""

    __tablename__ = "project_cleanup_audit_records"

    cleanup_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    cleanup_type: Mapped[str] = mapped_column(String(128), nullable=False)
    previous_status: Mapped[str] = mapped_column(String(64), nullable=False)
    new_status: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    operator: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    details_json: Mapped[str | None] = mapped_column(Text)


class ProjectFolderRecordModel(Base):
    """Database row for a generated project folder."""

    __tablename__ = "project_folder_records"

    folder_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    folder_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_on: Mapped[date | None] = mapped_column(Date)


class ProjectOfficialWorkspaceRecordModel(Base):
    """Database row for a local official project workspace."""

    __tablename__ = "project_official_workspace_records"

    workspace_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        unique=True,
        index=True,
    )
    dl_number: Mapped[str] = mapped_column(String(128), nullable=False)
    local_workspace_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    source_book_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    official_folder_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    manifest_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    template_source_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)


class FileAssetModel(Base):
    """Database row for a project file asset."""

    __tablename__ = "file_assets"

    asset_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(64), nullable=False)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    original_name: Mapped[str | None] = mapped_column(String(255))
    registered_on: Mapped[date | None] = mapped_column(Date)
    source_package_id: Mapped[str | None] = mapped_column(String(64))
    source_intake_asset_id: Mapped[str | None] = mapped_column(String(64))
    source_role: Mapped[str | None] = mapped_column(String(64))
    sha256: Mapped[str | None] = mapped_column(String(64))


class ProjectRequestMaterialCollectionModel(Base):
    """Database row for one request-material collection run."""

    __tablename__ = "project_request_material_collections"

    collection_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    workspace_id: Mapped[str | None] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    item_count: Mapped[int] = mapped_column(Integer, nullable=False)
    copied_count: Mapped[int] = mapped_column(Integer, nullable=False)
    already_present_count: Mapped[int] = mapped_column(Integer, nullable=False)
    conflict_count: Mapped[int] = mapped_column(Integer, nullable=False)
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False)
    missing_source_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)
    warnings_json: Mapped[str | None] = mapped_column(Text)


class ProjectRequestMaterialCollectionItemModel(Base):
    """Database row for one planned or executed request-material copy target."""

    __tablename__ = "project_request_material_collection_items"

    item_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    collection_id: Mapped[str] = mapped_column(
        ForeignKey("project_request_material_collections.collection_id"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    source_asset_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_asset_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_role: Mapped[str | None] = mapped_column(String(64))
    dedupe_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    original_name: Mapped[str | None] = mapped_column(String(255))
    target_area: Mapped[str] = mapped_column(String(64), nullable=False)
    target_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    review_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    sha256: Mapped[str | None] = mapped_column(String(64))


class PublicDriveUploadFileRecordModel(Base):
    """Database row for one ConnLab-managed public-drive uploaded file."""

    __tablename__ = "public_drive_upload_file_records"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        primary_key=True,
    )
    relative_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    public_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    local_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    public_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    uploaded_at: Mapped[str] = mapped_column(String(64), nullable=False)
    operation_id: Mapped[str] = mapped_column(String(64), nullable=False)


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


class ExternalResourceModel(Base):
    """Database row for operator-configured external resources."""

    __tablename__ = "external_resources"

    resource_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    resource_type: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    validation_status: Mapped[str] = mapped_column(String(64), nullable=False)
    last_validated_at: Mapped[str | None] = mapped_column(String(64))
    validation_failure_reason: Mapped[str | None] = mapped_column(Text)


class FrozenFieldRevisionRequestModel(Base):
    """Database row for one frozen-field revision request."""

    __tablename__ = "frozen_field_revision_requests"

    request_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    intake_case_id: Mapped[str] = mapped_column(
        ForeignKey("intake_cases.case_id"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str | None] = mapped_column(String(64), index=True)
    ltr_record_id: Mapped[str | None] = mapped_column(
        ForeignKey("ltr_records.ltr_id"),
        nullable=True,
    )
    ltr_number: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    requested_by: Mapped[str | None] = mapped_column(String(255))
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    field_changes_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)


class ProjectTestPlanDraftModel(Base):
    """Database row for one Project-stage test-plan draft snapshot."""

    __tablename__ = "project_test_plan_drafts"

    draft_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    source_document_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    source_document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_format: Mapped[str] = mapped_column(String(64), nullable=False)
    source_asset_id: Mapped[str | None] = mapped_column(String(64))
    source_case_id: Mapped[str | None] = mapped_column(String(64))
    source_draft_id: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)
    reviewed_at: Mapped[str | None] = mapped_column(String(64))


class ProjectOutputRecordModel(Base):
    """Database row for one persisted project output lineage/status record."""

    __tablename__ = "project_output_records"

    output_record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    draft_id: Mapped[str | None] = mapped_column(String(64), index=True)
    draft_version: Mapped[int | None] = mapped_column(Integer)
    output_kind: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    output_path: Mapped[str | None] = mapped_column(String(1024))
    output_sha256: Mapped[str | None] = mapped_column(String(128))
    output_size_bytes: Mapped[int | None] = mapped_column(Integer)
    source_context_signature: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)


class FeeEvaluationPricingDraftEditModel(Base):
    """Database row for one saved Fee Evaluation pricing draft edit payload."""

    __tablename__ = "fee_evaluation_pricing_draft_edits"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "confirmed_matrix_id",
            "confirmed_revision",
            "fee_rule_version_id",
            name="uq_fee_evaluation_pricing_draft_current",
        ),
    )

    draft_edit_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    confirmed_matrix_id: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmed_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    fee_rule_version_id: Mapped[str] = mapped_column(String(128), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)


class MatrixFeePendingRebaseModel(Base):
    """Pending Fee rebase payload produced by Matrix Editor autosave."""

    __tablename__ = "matrix_fee_pending_rebases"
    __table_args__ = (
        UniqueConstraint(
            "project_matrix_draft_id",
            "fee_rule_version_id",
            name="uq_matrix_fee_pending_rebase_draft_rule",
        ),
    )

    pending_rebase_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    project_matrix_draft_id: Mapped[str] = mapped_column(
        ForeignKey("project_matrix_draft_records.project_matrix_draft_id"),
        nullable=False,
        index=True,
    )
    base_confirmed_matrix_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    base_confirmed_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    fee_rule_version_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )
    matrix_draft_payload_signature: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    generation: Mapped[int] = mapped_column(Integer, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)


class ConfirmedFeeVersionModel(Base):
    """Database row for one immutable Confirmed Fee authority version."""

    __tablename__ = "confirmed_fee_versions"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "confirmed_fee_revision",
            name="uq_confirmed_fee_project_revision",
        ),
    )

    confirmed_fee_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    confirmed_fee_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    confirmed_matrix_id: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmed_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    fee_rule_version_id: Mapped[str] = mapped_column(String(128), nullable=False)
    pricing_draft_edit_id: Mapped[str] = mapped_column(String(64), nullable=False)
    pricing_effective_from: Mapped[str | None] = mapped_column(String(64))
    summary_json: Mapped[str] = mapped_column(Text, nullable=False)
    pricing_snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    confirmed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    confirmed_at: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmation_note: Mapped[str | None] = mapped_column(Text)
