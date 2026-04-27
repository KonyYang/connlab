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
