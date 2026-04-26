"""Domain enums for ConnLab MVP records."""

from __future__ import annotations

from enum import StrEnum


class ProjectStatus(StrEnum):
    """Lifecycle status for an MVP project."""

    DRAFT = "draft"
    INTAKE_RECEIVED = "intake_received"
    PRECHECK_PASSED = "precheck_passed"
    CONFIRMED = "confirmed"
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
