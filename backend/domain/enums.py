"""Domain enums for ConnLab MVP records."""

from __future__ import annotations

from enum import StrEnum


class ProjectStatus(StrEnum):
    """Lifecycle status for an MVP project."""

    DRAFT = "draft"
    INTAKE_RECEIVED = "intake_received"
    PRECHECK_PASSED = "precheck_passed"
    CONFIRMED = "confirmed"
    LTR_REGISTERED = "ltr_registered"
    FOLDER_CREATED = "folder_created"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class PrecheckStatus(StrEnum):
    """Overall deterministic precheck result status."""

    PENDING = "pending"
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


class IssueLevel(StrEnum):
    """Severity level for a precheck issue."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class IssueCategory(StrEnum):
    """MVP categories for deterministic application-form precheck issues."""

    FORM_METADATA = "form_metadata"
    REQUESTOR = "requestor"
    SAMPLE = "sample"
    TESTING_REQUEST = "testing_request"
    SUBCONTRACT = "subcontract"
    LAB_SECTION = "lab_section"
    ATTACHMENT = "attachment"


class LtrStatus(StrEnum):
    """Lifecycle status for an LTR record."""

    DRAFT = "draft"
    REGISTERED = "registered"
    CANCELLED = "cancelled"


class FileAssetType(StrEnum):
    """Structured type for files attached to the MVP project lifecycle."""

    APPLICATION_FORM = "application_form"
    ATTACHMENT = "attachment"
    LTR = "ltr"
    FOLDER_TEMPLATE = "folder_template"
    GENERATED_FOLDER = "generated_folder"
    OTHER = "other"


class IntakePackageSourceType(StrEnum):
    """Source type for a Phase 6 intake package."""

    OUTLOOK_MSG = "outlook_msg"
    DIRECT_APPLICATION_FORM = "direct_application_form"
    MANUAL = "manual"
    FUTURE_OUTLOOK_ITEM = "future_outlook_item"


class IntakePackageStatus(StrEnum):
    """Lifecycle status for an intake package."""

    IMPORTED = "imported"
    DRAFT_SAVED = "draft_saved"
    NEEDS_APPLICATION_FORM_SELECTION = "needs_application_form_selection"
    READY_FOR_REVIEW = "ready_for_review"
    PARTIALLY_CONFIRMED = "partially_confirmed"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class IntakeAssetRole(StrEnum):
    """Role assigned to an intake asset before project confirmation."""

    UNKNOWN = "unknown"
    EMAIL_SOURCE = "email_source"
    APPLICATION_FORM_CANDIDATE = "application_form_candidate"
    SELECTED_APPLICATION_FORM = "selected_application_form"
    SPECIFICATION = "specification"
    SUPPORTING_ATTACHMENT = "supporting_attachment"
    INLINE_IMAGE = "inline_image"
    IGNORED = "ignored"


class IntakeCaseStatus(StrEnum):
    """Lifecycle status for one selected application form case."""

    DRAFT_CREATED = "draft_created"
    NEEDS_REVIEW = "needs_review"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class ExternalResourceType(StrEnum):
    """Supported external resource registry entries."""

    LTR_WORKBOOK = "ltr_workbook"
    APPLICATION_FORM_TEMPLATE = "application_form_template"
    PROJECT_FOLDER_TEMPLATE = "project_folder_template"
    PROJECT_OUTPUT_ROOT = "project_output_root"
    OFFICIAL_PUBLIC_DRIVE_ROOT = "official_public_drive_root"
    STANDARD_RECORD_EXCEL = "standard_record_excel"
    EQUIPMENT_CALIBRATION_EXCEL = "equipment_calibration_excel"


class ExternalResourceValidationStatus(StrEnum):
    """Validation state for an external resource path."""

    NOT_VALIDATED = "not_validated"
    VALID = "valid"
    INVALID = "invalid"


class FrozenFieldRevisionRequestStatus(StrEnum):
    """Lifecycle status for one frozen-field revision request record."""

    REQUESTED = "requested"
    CANCELLED = "cancelled"


class ProjectTestPlanDraftStatus(StrEnum):
    """Lifecycle status for a Project-stage test-plan draft snapshot."""

    DRAFT = "draft"
    REVIEWED = "reviewed"
    SUPERSEDED = "superseded"


class ProjectOutputKind(StrEnum):
    """Supported persisted output kinds linked to Project test-plan drafts."""

    SECTION2_WRITE_BACK = "section2_write_back"
    TEST_RECORD_FORM = "test_record_form"
    FEE_EVALUATION = "fee_evaluation"
    CUSTOMER_FEEDBACK_FORM = "customer_feedback_form"
    APPROVAL_PACKAGE = "approval_package"


class ProjectOutputStatus(StrEnum):
    """Persisted output freshness status for Workbench traceability."""

    MISSING = "missing"
    CURRENT = "current"
    STALE = "stale"
    MANUAL = "manual"
    FAILED = "failed"


class ProjectOutputSource(StrEnum):
    """Source classification for one output status record."""

    SYSTEM_GENERATED = "system_generated"
    SYSTEM_EXECUTED = "system_executed"
    MANUAL = "manual"


class SourceMatrixImportStatus(StrEnum):
    """Lifecycle status for one persisted Source Matrix import snapshot."""

    IMPORTED = "imported"
    BLOCKED = "blocked"


class ProjectMatrixDraftStatus(StrEnum):
    """Lifecycle status for one structured Project Matrix draft working copy."""

    DRAFT = "draft"
    SUPERSEDED = "superseded"


class ConfirmedMatrixStatus(StrEnum):
    """Lifecycle status for one immutable confirmed Matrix authority version."""

    CONFIRMED = "confirmed"
    SUPERSEDED = "superseded"
