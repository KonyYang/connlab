"""Application service for external resource registration and validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ExternalResourceValidationStatus,
)
from backend.infrastructure.office import OfficeFacade
from backend.infrastructure.office.excel_tabular_layout import ExcelTabularLayout


class ExternalResourceNotFoundError(LookupError):
    """Raised when an external resource is not registered."""


class ExternalResourceWorksheetNameError(ValueError):
    """Raised when a worksheet-name update violates the resource contract."""


@dataclass(frozen=True, slots=True)
class WorksheetNameUpdate:
    """Preserve whether the nullable worksheet field was supplied by the caller."""

    supplied: bool
    value: str | None = None


STANDARD_RECORD_DEFAULT_WORKSHEET = "认可标准"


class ExternalResourceRepositoryPort(Protocol):
    """Storage behavior required by external resource service."""

    def list_all(self) -> list[ExternalResource]:
        """Return all registered resources."""

    def get_by_type(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource | None:
        """Return a registered resource by type."""

    def upsert(self, resource: ExternalResource) -> ExternalResource:
        """Create or update a registered resource."""


class ExternalResourceService:
    """Register and validate external resources without mutating them."""

    def __init__(
        self,
        repository: ExternalResourceRepositoryPort,
        office: OfficeFacade | None = None,
    ) -> None:
        """Create the service."""
        self._repository = repository
        self._office = office or OfficeFacade()

    def list_resources(self) -> list[ExternalResource]:
        """Return all registered external resources."""
        return self._repository.list_all()

    def upsert_resource(
        self,
        resource_type: ExternalResourceType,
        path: Path,
        active: bool,
        worksheet_name: WorksheetNameUpdate = WorksheetNameUpdate(supplied=False),
    ) -> ExternalResource:
        """Create or replace a resource path and reset validation state."""
        existing = self._repository.get_by_type(resource_type)
        normalized_worksheet = _resolve_worksheet_update(
            resource_type,
            worksheet_name,
            existing.worksheet_name if existing else None,
        )
        resource = ExternalResource(
            resource_id=existing.resource_id if existing else uuid4().hex,
            resource_type=resource_type,
            path=path,
            active=active,
            worksheet_name=normalized_worksheet,
        )
        return self._repository.upsert(resource)

    def effective_worksheet_name(self, resource: ExternalResource) -> str | None:
        """Return the operator-visible worksheet value for one resource."""
        return effective_standard_worksheet_name(resource)

    def validate_resource(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource:
        """Validate a registered resource and persist the validation result."""
        resource = self._repository.get_by_type(resource_type)
        if resource is None:
            raise ExternalResourceNotFoundError(
                f"External resource is not registered: {resource_type.value}"
            )
        failure = self._validation_failure(resource)
        validated = ExternalResource(
            resource_id=resource.resource_id,
            resource_type=resource.resource_type,
            path=resource.path,
            active=resource.active,
            validation_status=(
                ExternalResourceValidationStatus.INVALID
                if failure
                else ExternalResourceValidationStatus.VALID
            ),
            last_validated_at=_utc_now_text(),
            validation_failure_reason=failure,
            worksheet_name=resource.worksheet_name,
        )
        return self._repository.upsert(validated)

    def _validation_failure(self, resource: ExternalResource) -> str | None:
        """Return a failure reason, or None when the resource is valid."""
        path = resource.path
        if resource.resource_type is ExternalResourceType.PROJECT_FOLDER_TEMPLATE:
            return _folder_template_failure(path)
        if resource.resource_type is ExternalResourceType.PROJECT_OUTPUT_ROOT:
            return _directory_failure(path, "Project output root")
        if resource.resource_type is ExternalResourceType.OFFICIAL_PUBLIC_DRIVE_ROOT:
            return _directory_failure(path, "Public Project locations")
        if not path.is_file():
            return f"Expected an existing file: {path}"
        if resource.resource_type is ExternalResourceType.APPLICATION_FORM_TEMPLATE:
            return self._word_failure(path)
        if resource.resource_type in {
            ExternalResourceType.LTR_WORKBOOK,
            ExternalResourceType.STANDARD_RECORD_EXCEL,
            ExternalResourceType.EQUIPMENT_CALIBRATION_EXCEL,
        }:
            return self._excel_failure(resource)
        return f"Unsupported resource type: {resource.resource_type.value}"

    def _word_failure(self, path: Path) -> str | None:
        """Return why a Word template cannot be read."""
        if path.suffix.lower() != ".docx":
            return f"Expected a .docx Word file: {path}"
        try:
            self._office.read_word_document(path)
        except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
            return f"Word file is not readable: {exc}"
        return None

    def _excel_failure(
        self,
        resource: ExternalResource,
    ) -> str | None:
        """Return why an Excel resource cannot be read."""
        path = resource.path
        resource_type = resource.resource_type
        suffix = path.suffix.lower()
        if resource_type is ExternalResourceType.LTR_WORKBOOK:
            if suffix not in {".xlsx", ".xls"}:
                return f"Expected an Excel file (.xlsx or .xls): {path}"
            if suffix == ".xls":
                return None if path.stat().st_size > 0 else f"Excel file is empty: {path}"
        else:
            if suffix not in {".xlsx", ".xls"}:
                return f"Expected an Excel file (.xlsx or .xls): {path}"
        try:
            self._probe_excel_resource(path, resource)
        except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
            return f"Excel file is not readable: {exc}"
        return None

    def _probe_excel_resource(
        self,
        path: Path,
        resource: ExternalResource,
    ) -> None:
        """Probe expected external Excel structure without writing."""
        resource_type = resource.resource_type
        if resource_type is ExternalResourceType.LTR_WORKBOOK:
            snapshot = self._office.read_excel_workbook(path)
            if not getattr(snapshot, "readable_sheet_names", ()):
                raise ValueError("LTR workbook has no readable worksheets.")
            return
        rules = _excel_probe_rules(resource)
        result = self._office.probe_excel_structure(path, **rules)
        if not result.valid:
            raise ValueError(result.failure_reason or "Excel structure probe failed.")


def _folder_template_failure(path: Path) -> str | None:
    """Return why a project folder template directory is invalid."""
    directory_failure = _directory_failure(path, "Project folder template directory")
    if directory_failure:
        return directory_failure
    try:
        next(path.iterdir())
    except StopIteration:
        return f"Project folder template directory is empty: {path}"
    except OSError as exc:
        return f"Project folder template directory is not readable: {exc}"
    return None


def _directory_failure(path: Path, label: str) -> str | None:
    """Return why a directory resource is invalid."""
    if not path.is_dir():
        return f"Expected an existing directory: {path}"
    try:
        next(path.iterdir(), None)
    except OSError as exc:
        return f"{label} is not readable: {exc}"
    return None


def _utc_now_text() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def effective_standard_worksheet_name(resource: ExternalResource) -> str | None:
    """Resolve the stored nullable Standard worksheet to its effective value."""
    if resource.resource_type is not ExternalResourceType.STANDARD_RECORD_EXCEL:
        return None
    return resource.worksheet_name or STANDARD_RECORD_DEFAULT_WORKSHEET


def _resolve_worksheet_update(
    resource_type: ExternalResourceType,
    update: WorksheetNameUpdate,
    existing: str | None,
) -> str | None:
    if not update.supplied:
        return existing
    if resource_type is not ExternalResourceType.STANDARD_RECORD_EXCEL:
        raise ExternalResourceWorksheetNameError(
            "worksheet_name is supported only for the Standard record Excel resource."
        )
    value = (update.value or "").strip()
    if not value:
        return None
    if len(value) > 31:
        raise ExternalResourceWorksheetNameError(
            "Standard record sheet must be 31 characters or fewer."
        )
    if any(ord(character) < 32 for character in value):
        raise ExternalResourceWorksheetNameError(
            "Standard record sheet cannot contain control characters."
        )
    if any(character in "[]:*?/\\" for character in value):
        raise ExternalResourceWorksheetNameError(
            "Standard record sheet contains an invalid Excel worksheet character."
        )
    return value


def _excel_probe_rules(resource: ExternalResource) -> dict[str, object]:
    """Return expected read-only structure rules for an Excel resource."""
    resource_type = resource.resource_type
    if resource_type is ExternalResourceType.EQUIPMENT_CALIBRATION_EXCEL:
        return {
            "expected_headers": (
                "Equipment ID",
                "Equipment Name",
                "Calibration Due Date",
            ),
            "expected_date_headers": ("Calibration Due Date",),
            "expected_sheet_name_patterns": (r".*calibration.*", r".*equipment.*"),
        }
    return {
        "expected_headers": ("文 件 编 号",),
        "expected_sheet_names": (effective_standard_worksheet_name(resource),),
        "layout": ExcelTabularLayout(
            header_row_number=2,
            required_header_columns=(("文 件 编 号", 2),),
            optional_headers=("文 件 名 称", "备注"),
            include_row_number=True,
            require_unique_sheet_match=True,
        ),
    }
