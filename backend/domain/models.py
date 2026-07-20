"""Pure Python domain models for the ConnLab MVP."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path

from backend.domain.enums import (
    FrozenFieldRevisionRequestStatus,
    ExternalResourceType,
    ExternalResourceValidationStatus,
    FileAssetType,
    IntakeAssetRole,
    IntakeCaseStatus,
    IntakePackageSourceType,
    IntakePackageStatus,
    IssueCategory,
    IssueLevel,
    LtrStatus,
    PrecheckStatus,
    ProjectClosureType,
    ProjectCloseReasonCategory,
    ProjectLifecycleEventType,
    ProjectLifecycleState,
    ProjectStatus,
    ProjectTestPlanDraftStatus,
    ProjectOutputKind,
    ProjectOutputSource,
    ProjectOutputStatus,
)


@dataclass(frozen=True, slots=True)
class Project:
    """Core project record at the center of the ConnLab MVP lifecycle."""

    project_id: str
    project_no: str | None
    product_name: str
    requestor: str
    status: ProjectStatus = ProjectStatus.DRAFT
    business_unit: str | None = None
    created_on: date | None = None
    lifecycle_state: ProjectLifecycleState = ProjectLifecycleState.ACTIVE
    closure_type: ProjectClosureType | None = None
    close_reason_category: ProjectCloseReasonCategory | None = None
    stopped_reason: str | None = None
    stopped_at: str | None = None
    stopped_by: str | None = None
    resumed_reason: str | None = None
    resumed_at: str | None = None
    resumed_by: str | None = None
    closed_reason: str | None = None
    closed_at: str | None = None
    closed_by: str | None = None
    completion_summary_json: str | None = None

    def can_generate_folder(self) -> bool:
        """Return whether the project is ready for safe folder generation."""
        return self.status is ProjectStatus.CONFIRMED

    def with_status(self, status: ProjectStatus) -> "Project":
        """Return a copy of the project with an updated lifecycle status."""
        return replace(self, status=status)

    def with_lifecycle(
        self,
        *,
        lifecycle_state: ProjectLifecycleState,
        closure_type: ProjectClosureType | None = None,
        close_reason_category: ProjectCloseReasonCategory | None = None,
        stopped_reason: str | None = None,
        stopped_at: str | None = None,
        stopped_by: str | None = None,
        resumed_reason: str | None = None,
        resumed_at: str | None = None,
        resumed_by: str | None = None,
        closed_reason: str | None = None,
        closed_at: str | None = None,
        closed_by: str | None = None,
        completion_summary_json: str | None = None,
    ) -> "Project":
        """Return a copy of the project with updated lifecycle overlay fields."""
        return replace(
            self,
            lifecycle_state=lifecycle_state,
            closure_type=closure_type,
            close_reason_category=close_reason_category,
            stopped_reason=stopped_reason,
            stopped_at=stopped_at,
            stopped_by=stopped_by,
            resumed_reason=resumed_reason,
            resumed_at=resumed_at,
            resumed_by=resumed_by,
            closed_reason=closed_reason,
            closed_at=closed_at,
            closed_by=closed_by,
            completion_summary_json=completion_summary_json,
        )


@dataclass(frozen=True, slots=True)
class ProjectLifecycleEvent:
    """Audited lifecycle transition for one project."""

    event_id: str
    project_id: str
    event_type: ProjectLifecycleEventType
    previous_lifecycle_state: ProjectLifecycleState
    new_lifecycle_state: ProjectLifecycleState
    previous_closure_type: ProjectClosureType | None
    new_closure_type: ProjectClosureType | None
    reason: str | None
    operator: str | None
    created_at: str
    metadata_json: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectTemporaryContext:
    """Planning-only context captured before formal LTR/DL registration."""

    context_id: str
    project_id: str
    request_summary: str | None = None
    sample_description: str | None = None
    test_item: str | None = None
    notes: str | None = None
    source_asset_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ApplicationForm:
    """Structured application form data captured for a project."""

    form_id: str
    project_id: str
    form_no: str
    revision: str
    requester: str
    request_date: date | None = None
    phone: str | None = None
    email: str | None = None
    business_unit: str | None = None
    manufacturing_site: str | None = None
    requested_testing: str | None = None
    subcontract_allowed: bool | None = None
    reference_doc: str | None = None
    lab_test_request_number: str | None = None
    project_number: str | None = None
    requested_completion_date: str | None = None
    results_format: str | None = None
    test_type: str | None = None
    sample_status: str | None = None
    project_type: str | None = None
    post_testing_disposition: str | None = None
    confidential: str | None = None
    subcontract: str | None = None
    additional_information: str | None = None
    send_copies_recipients: str | None = None
    lab: str | None = None
    assigned_personnel: str | None = None
    received_date: str | None = None
    estimated_completion_date: str | None = None
    sample_condition: str | None = None


@dataclass(frozen=True, slots=True)
class SampleInfo:
    """Structured sample information extracted or confirmed for a project."""

    sample_id: str
    project_id: str
    product_name: str
    part_number: str
    revision: str | None = None
    lot_or_traceability: str | None = None
    material: str | None = None
    plating: str | None = None
    housing_material: str | None = None
    quantity: int | None = None


@dataclass(frozen=True, slots=True)
class PrecheckIssue:
    """Single deterministic precheck issue found on an application form."""

    issue_id: str
    category: IssueCategory
    level: IssueLevel
    message: str
    field_name: str | None = None
    resolved: bool = False


@dataclass(frozen=True, slots=True)
class PrecheckResult:
    """Precheck result and its issue list for an application form."""

    result_id: str
    application_form_id: str
    status: PrecheckStatus
    issues: tuple[PrecheckIssue, ...] = field(default_factory=tuple)
    checked_on: date | None = None

    def has_errors(self) -> bool:
        """Return whether the result contains any blocking error issue."""
        return any(issue.level is IssueLevel.ERROR for issue in self.issues)


@dataclass(frozen=True, slots=True)
class LtrRecord:
    """LTR registration record linked to a project."""

    ltr_id: str
    project_id: str
    ltr_number: str
    status: LtrStatus = LtrStatus.DRAFT
    registered_on: date | None = None
    requested_by: str | None = None
    requested_date: date | None = None
    notes: str | None = None
    is_current_owner: bool = True
    superseded_at: str | None = None
    superseded_by_ltr_id: str | None = None
    superseded_reason: str | None = None
    owner_version: int = 1


@dataclass(frozen=True, slots=True)
class LtrDuplicateResolutionToken:
    """One short-lived token for confirming a local LTR duplicate association."""

    token_id: str
    ltr_number: str
    existing_ltr_id: str
    existing_project_id: str
    current_case_id: str
    current_project_id: str
    conflict_fingerprint: str
    expires_at: str
    created_at: str
    created_by: str | None = None
    workbook_fingerprint: str | None = None
    used_at: str | None = None
    metadata_json: str | None = None


@dataclass(frozen=True, slots=True)
class LtrAssociationEvent:
    """Audited local LTR ownership association event."""

    event_id: str
    ltr_number: str
    event_type: str
    old_ltr_id: str | None
    old_project_id: str | None
    new_ltr_id: str | None
    new_project_id: str | None
    operator: str | None
    reason: str
    token_id: str | None
    created_at: str
    metadata_json: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectFolderRecord:
    """Record of a generated project folder path."""

    folder_id: str
    project_id: str
    folder_path: Path
    created_on: date | None = None


@dataclass(frozen=True, slots=True)
class FileAsset:
    """File asset registered against a project lifecycle stage."""

    asset_id: str
    project_id: str
    asset_type: FileAssetType
    path: Path
    original_name: str | None = None
    registered_on: date | None = None
    source_package_id: str | None = None
    source_intake_asset_id: str | None = None
    source_role: str | None = None
    sha256: str | None = None


@dataclass(frozen=True, slots=True)
class IntakePackage:
    """Imported request package before project confirmation."""

    package_id: str
    source_type: IntakePackageSourceType
    status: IntakePackageStatus
    source_original_name: str
    source_stored_path: Path
    subject: str | None = None
    sender_name: str | None = None
    sender_email: str | None = None
    recipients_json: str | None = None
    cc_json: str | None = None
    received_at: str | None = None
    body_text: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class IntakeAsset:
    """File asset registered before a project exists."""

    asset_id: str
    package_id: str
    original_name: str
    stored_path: Path
    extension: str
    mime_type: str | None
    size_bytes: int
    sha256: str
    asset_role: IntakeAssetRole = IntakeAssetRole.UNKNOWN
    candidate_score: int | None = None
    content_id: str | None = None
    created_at: str | None = None


@dataclass(frozen=True, slots=True)
class IntakeCase:
    """One selected application form before confirmation into a project."""

    case_id: str
    package_id: str
    selected_form_asset_id: str | None
    status: IntakeCaseStatus
    confirmed_project_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    reviewer_notes: str | None = None


@dataclass(frozen=True, slots=True)
class IntakeDraft:
    """Parser draft and human overrides for an intake case."""

    draft_id: str
    case_id: str
    parsed_fields_json: str
    sample_rows_json: str | None = None
    requested_testing_json: str | None = None
    field_confidence_json: str | None = None
    parser_warnings_json: str | None = None
    manual_overrides_json: str | None = None
    updated_at: str | None = None


@dataclass(frozen=True, slots=True)
class ExternalResource:
    """Registered external resource used by controlled ConnLab workflows."""

    resource_id: str
    resource_type: ExternalResourceType
    path: Path
    active: bool = True
    validation_status: ExternalResourceValidationStatus = (
        ExternalResourceValidationStatus.NOT_VALIDATED
    )
    last_validated_at: str | None = None
    validation_failure_reason: str | None = None
    worksheet_name: str | None = None


@dataclass(frozen=True, slots=True)
class FrozenFieldRevisionRequest:
    """Structured request to revise fields frozen after LTR registration."""

    request_id: str
    intake_case_id: str
    project_id: str | None
    ltr_record_id: str | None
    ltr_number: str | None
    status: FrozenFieldRevisionRequestStatus
    requested_by: str | None
    reason: str
    field_changes_json: str
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class ProjectTestPlanDraft:
    """Project-stage structured test-plan draft snapshot."""

    draft_id: str
    project_id: str
    source_document_path: str
    source_document_name: str
    source_format: str
    status: ProjectTestPlanDraftStatus
    version: int
    payload_json: str
    created_at: str
    updated_at: str
    source_asset_id: str | None = None
    source_case_id: str | None = None
    source_draft_id: str | None = None
    reviewed_at: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectOutputRecord:
    """Persisted output lineage and freshness record for one project output."""

    output_record_id: str
    project_id: str
    output_kind: ProjectOutputKind
    status: ProjectOutputStatus
    source: ProjectOutputSource
    created_at: str
    updated_at: str
    draft_id: str | None = None
    draft_version: int | None = None
    output_path: str | None = None
    output_sha256: str | None = None
    output_size_bytes: int | None = None
    source_context_signature: str | None = None
    note: str | None = None
