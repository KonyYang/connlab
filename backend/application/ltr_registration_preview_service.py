"""Application service for no-write LTR registration preview."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import Protocol

from backend.application.ltr_readiness_service import (
    LtrReadinessResult,
    LtrReadinessService,
)
from backend.application.project_lifecycle_service import LifecycleOperation
from backend.domain import LtrRecord, LtrStatus
from backend.infrastructure.office.models import LtrWorkbookSnapshot
from backend.modules.ltr import (
    LtrNumberError,
    base_ltr_number,
    family_stem,
    next_monthly_dl_number,
    parse_ltr_number,
)


class LtrPreviewError(ValueError):
    """Raised when an LTR preview request is invalid."""


class LtrPreviewMode(StrEnum):
    """Supported LTR preview modes."""

    LOCAL_ONLY = "local_only"
    EXCEL_READONLY = "excel_readonly"


class LtrRegistrationType(StrEnum):
    """Supported LTR registration types."""

    NORMAL = "normal"
    ASSOCIATED = "associated"


@dataclass(frozen=True, slots=True)
class PreviewLtrRegistrationCommand:
    """Input command for previewing an LTR registration."""

    year: int
    month: int
    registration_type: LtrRegistrationType = LtrRegistrationType.NORMAL
    mode: LtrPreviewMode = LtrPreviewMode.LOCAL_ONLY
    proposed_ltr_number: str | None = None


@dataclass(frozen=True, slots=True)
class LtrRegistrationPreview:
    """No-write preview of an LTR registration."""

    project_id: str
    status: str
    proposed_ltr_number: str | None
    registration_type: LtrRegistrationType
    mode: LtrPreviewMode
    target_write_year_sheet: str
    number_preflight_required: bool
    number_preview_allowed: bool
    final_number_reserved: bool
    target_sheet: str | None
    target_row: int | None
    snapshot_fingerprint: str | None
    source_numbers: tuple[str, ...]
    readiness: LtrReadinessResult
    conflicts: tuple[str, ...]
    warnings: tuple[str, ...]
    parsed_base_number: str | None = None
    base_year_sheet: str | None = None
    family_numbers: tuple[str, ...] = ()


class LtrRepositoryPort(Protocol):
    """LTR repository behavior required by the preview service."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return LTR records for a project."""

    def search(self, query: str) -> list[LtrRecord]:
        """Search LTR records."""


class LtrReadinessServicePort(Protocol):
    """Readiness behavior required by the preview service."""

    def evaluate_project(
        self,
        project_id: str,
        proposed_ltr_number: str | None = None,
    ) -> LtrReadinessResult:
        """Evaluate readiness for a project and proposed LTR number."""


class LtrWorkbookSnapshotProviderPort(Protocol):
    """Optional provider for read-only workbook snapshot data."""

    def get_snapshot(self) -> LtrWorkbookSnapshot | None:
        """Return the latest available workbook snapshot."""


class ProjectLifecycleGuardPort(Protocol):
    """Lifecycle guard behavior required by the preview service."""

    def require_allowed(
        self,
        project_id: str,
        operation: LifecycleOperation,
    ) -> None:
        """Raise when an operation is not allowed."""


class LtrRegistrationPreviewService:
    """Build no-write previews before LTR registration commit."""

    def __init__(
        self,
        ltr_repository: LtrRepositoryPort,
        readiness_service: LtrReadinessServicePort | LtrReadinessService,
        workbook_snapshot_provider: LtrWorkbookSnapshotProviderPort | None = None,
        lifecycle_guard: ProjectLifecycleGuardPort | None = None,
    ) -> None:
        """Create a preview service with repository and readiness ports."""
        self._ltrs = ltr_repository
        self._readiness = readiness_service
        self._snapshot_provider = workbook_snapshot_provider
        self._lifecycle = lifecycle_guard

    def preview_project(
        self,
        project_id: str,
        command: PreviewLtrRegistrationCommand,
    ) -> LtrRegistrationPreview:
        """Return a no-write LTR registration preview."""
        if self._lifecycle is not None:
            self._lifecycle.require_allowed(project_id, LifecycleOperation.LTR_PREVIEW)
        _validate_year_month(command.year, command.month)
        if command.registration_type is LtrRegistrationType.NORMAL:
            return self._preview_normal(project_id, command)
        return self._preview_associated(project_id, command)

    def _preview_normal(
        self,
        project_id: str,
        command: PreviewLtrRegistrationCommand,
    ) -> LtrRegistrationPreview:
        """Return readiness-only preflight for normal registration."""
        readiness = self._readiness.evaluate_project(project_id, None)
        warnings = tuple(field.operator_action for field in readiness.warnings)
        return LtrRegistrationPreview(
            project_id=project_id,
            status=_preview_status(readiness, ()),
            proposed_ltr_number=None,
            registration_type=LtrRegistrationType.NORMAL,
            mode=command.mode,
            target_write_year_sheet=f"{command.year:04d}",
            number_preflight_required=False,
            number_preview_allowed=False,
            final_number_reserved=False,
            target_sheet=f"{command.year:04d}",
            target_row=None,
            snapshot_fingerprint=None,
            source_numbers=(),
            readiness=readiness,
            conflicts=(),
            warnings=warnings,
        )

    def _preview_associated(
        self,
        project_id: str,
        command: PreviewLtrRegistrationCommand,
    ) -> LtrRegistrationPreview:
        """Return read-only association preflight for an associated LTR."""
        if not command.proposed_ltr_number:
            raise LtrPreviewError("Associated LTR preflight requires an LTR number.")
        snapshot = self._snapshot(command.mode)
        associated_number = _associated_ltr_number(command.proposed_ltr_number)
        base_number = base_ltr_number(associated_number)
        base_year = parse_ltr_number(base_number).year or command.year
        local_numbers = _normalized_ltr_numbers(ltr.ltr_number for ltr in self._ltrs.search("DL-"))
        workbook_numbers = snapshot.existing_ltr_numbers if snapshot else ()
        source_numbers = tuple(dict.fromkeys((*local_numbers, *workbook_numbers)))
        readiness = self._readiness.evaluate_project(project_id, associated_number)
        project_ltrs = self._ltrs.list_by_project(project_id)
        family_numbers = tuple(
            number for number in source_numbers if _is_family_number(number, base_number)
        )
        conflicts = _conflicts(
            proposed_number=associated_number,
            project_ltrs=project_ltrs,
            local_numbers=local_numbers,
            workbook_numbers=workbook_numbers,
        )
        warnings = _warnings(command.mode, snapshot, readiness)
        if base_number not in source_numbers:
            warnings = (*warnings, f"Associated base LTR was not found: {base_number}")
        return LtrRegistrationPreview(
            project_id=project_id,
            status=_preview_status(readiness, conflicts),
            proposed_ltr_number=associated_number,
            registration_type=LtrRegistrationType.ASSOCIATED,
            mode=command.mode,
            target_write_year_sheet=f"{command.year:04d}",
            number_preflight_required=True,
            number_preview_allowed=True,
            final_number_reserved=False,
            target_sheet=f"{command.year:04d}",
            target_row=_target_row(snapshot),
            snapshot_fingerprint=_snapshot_fingerprint(snapshot),
            source_numbers=source_numbers,
            readiness=readiness,
            conflicts=conflicts,
            warnings=warnings,
            parsed_base_number=base_number,
            base_year_sheet=f"{base_year:04d}",
            family_numbers=family_numbers,
        )

    def _snapshot(self, mode: LtrPreviewMode) -> LtrWorkbookSnapshot | None:
        """Return a workbook snapshot only for workbook-aware preview modes."""
        if mode is LtrPreviewMode.LOCAL_ONLY or self._snapshot_provider is None:
            return None
        return self._snapshot_provider.get_snapshot()


def _validate_year_month(year: int, month: int) -> None:
    """Validate preview year/month input."""
    try:
        next_monthly_dl_number(year=year, month=month, existing_numbers=())
    except LtrNumberError as exc:
        raise LtrPreviewError(str(exc)) from exc


def _monthly_prefix(command: PreviewLtrRegistrationCommand) -> str:
    """Return the local search prefix for a standard monthly DL sequence."""
    return f"DL-{command.year:04d}-{command.month:02d}-"


def _normalized_ltr_numbers(values) -> tuple[str, ...]:
    """Normalize supported LTR numbers and ignore unrelated text."""
    numbers: list[str] = []
    for value in values:
        try:
            numbers.append(parse_ltr_number(value).normalized)
        except LtrNumberError:
            continue
    return tuple(dict.fromkeys(numbers))


def _associated_ltr_number(value: str) -> str:
    """Return a normalized associated LTR number."""
    try:
        parsed = parse_ltr_number(value)
    except LtrNumberError as exc:
        raise LtrPreviewError(str(exc)) from exc
    if not parsed.is_associated_dl:
        raise LtrPreviewError("Associated LTR preflight requires a DL suffix number.")
    return parsed.normalized


def _is_family_number(value: str, stem: str) -> bool:
    """Return whether a number belongs to an associated DL family."""
    try:
        return family_stem(value) == stem
    except LtrNumberError:
        return False


def _conflicts(
    *,
    proposed_number: str,
    project_ltrs: list[LtrRecord],
    local_numbers: tuple[str, ...],
    workbook_numbers: tuple[str, ...],
) -> tuple[str, ...]:
    """Return preview conflicts that must block commit."""
    conflicts: list[str] = []
    if any(ltr.status is LtrStatus.REGISTERED for ltr in project_ltrs):
        conflicts.append("Project already has an active registered LTR.")
    if proposed_number in local_numbers:
        conflicts.append(f"Proposed LTR already exists in local records: {proposed_number}")
    if proposed_number in workbook_numbers:
        conflicts.append(f"Proposed LTR already exists in workbook snapshot: {proposed_number}")
    return tuple(conflicts)


def _warnings(
    mode: LtrPreviewMode,
    snapshot: LtrWorkbookSnapshot | None,
    readiness: LtrReadinessResult,
) -> tuple[str, ...]:
    """Return non-conflict preview warnings."""
    warnings = [field.operator_action for field in readiness.warnings]
    if mode is LtrPreviewMode.EXCEL_READONLY and snapshot is None:
        warnings.append("Workbook snapshot is not available; preview used local records only.")
    return tuple(warnings)


def _preview_status(
    readiness: LtrReadinessResult,
    conflicts: tuple[str, ...],
) -> str:
    """Return aggregate preview status."""
    if readiness.blockers:
        return "blocked"
    if conflicts:
        return "conflict"
    if readiness.warnings:
        return "review_required"
    return "ready"


def _target_sheet(
    command: PreviewLtrRegistrationCommand,
    snapshot: LtrWorkbookSnapshot | None,
) -> str | None:
    """Return the likely workbook sheet for the preview."""
    if snapshot is None:
        return None
    year_sheet = f"{command.year:04d}"
    month_sheet = f"{command.year:04d}-{command.month:02d}"
    if year_sheet in snapshot.sheet_names:
        return year_sheet
    if month_sheet in snapshot.sheet_names:
        return month_sheet
    return snapshot.readable_sheet_names[0] if snapshot.readable_sheet_names else None


def _target_row(snapshot: LtrWorkbookSnapshot | None) -> int | None:
    """Return the next likely workbook row when a snapshot is available."""
    if snapshot is None:
        return None
    return len(snapshot.existing_ltr_numbers) + 2


def _snapshot_fingerprint(snapshot: LtrWorkbookSnapshot | None) -> str | None:
    """Return a stable fingerprint for stale-snapshot checks."""
    if snapshot is None:
        return None
    payload = "|".join(
        (
            str(snapshot.workbook_path),
            str(snapshot.size_bytes),
            snapshot.modified_time.isoformat(),
            ",".join(snapshot.existing_ltr_numbers),
        )
    )
    return sha256(payload.encode("utf-8")).hexdigest()
