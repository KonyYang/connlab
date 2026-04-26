"""Pure Python domain models for the ConnLab MVP."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path

from backend.domain.enums import (
    FileAssetType,
    IssueCategory,
    IssueLevel,
    LtrStatus,
    PrecheckStatus,
    ProjectStatus,
)


@dataclass(frozen=True, slots=True)
class Project:
    """Core project record at the center of the ConnLab MVP lifecycle."""

    project_id: str
    project_no: str
    product_name: str
    requestor: str
    status: ProjectStatus = ProjectStatus.DRAFT
    business_unit: str | None = None
    created_on: date | None = None

    def can_generate_folder(self) -> bool:
        """Return whether the project is ready for safe folder generation."""
        return self.status is ProjectStatus.CONFIRMED

    def with_status(self, status: ProjectStatus) -> "Project":
        """Return a copy of the project with an updated lifecycle status."""
        return replace(self, status=status)


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
