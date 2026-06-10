"""Sync structured Application Form Section 2 dates from Confirmed Matrix authority."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from typing import Literal, Protocol

from backend.domain import ApplicationForm, ConfirmedMatrixSnapshot, Project


Section2FieldKey = Literal["received_date", "estimated_completion_date"]
Section2SourceFieldKey = Literal["sample_received_date", "estimated_completion_date"]
Section2FieldStatus = Literal[
    "will_change",
    "changed",
    "unchanged",
    "skipped_missing_source",
    "blocked_invalid_source",
]
Section2SyncStatus = Literal["ready", "up_to_date", "partial", "blocked", "synced"]


class ProjectSection2SyncError(Exception):
    """Base error for Section 2 sync failures."""


class ProjectSection2SyncReadinessError(ProjectSection2SyncError):
    """Raised when required source or target readiness is missing."""


class ProjectSection2SyncProjectNotFoundError(ProjectSection2SyncReadinessError):
    """Raised when the project id is unknown."""


class ProjectSection2SyncAmbiguousTargetError(ProjectSection2SyncReadinessError):
    """Raised when Application Form target selection would be guessed."""


class ProjectSection2SyncConflictError(ProjectSection2SyncError):
    """Raised when previewed Confirmed Matrix identity is no longer current."""


class ProjectSection2SyncValidationError(ProjectSection2SyncError):
    """Raised when source values are invalid for structured date sync."""


@dataclass(frozen=True, slots=True)
class ProjectSection2SyncCommand:
    """Command for previewing or syncing Section 2 dates."""

    project_id: str
    expected_confirmed_matrix_id: str | None = None
    expected_confirmed_revision: int | None = None
    operator: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectSection2FieldSync:
    """One Section 2 field sync decision."""

    field_key: Section2FieldKey
    source_field_key: Section2SourceFieldKey
    source_value: str | None
    current_value: str | None
    next_value: str | None
    status: Section2FieldStatus
    message: str


@dataclass(frozen=True, slots=True)
class ProjectSection2SyncResult:
    """Preview or sync result for Application Form Section 2 date fields."""

    project_id: str
    application_form_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    fields: tuple[ProjectSection2FieldSync, ...]
    status: Section2SyncStatus
    synced_at: str | None = None
    operator: str | None = None


class Section2SyncProjectStore(Protocol):
    """Project lookup port."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id, or None."""


class Section2SyncConfirmedMatrixStore(Protocol):
    """Confirmed Matrix authority lookup port."""

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return the active Confirmed Matrix authority snapshot for a project."""


class Section2SyncApplicationFormStore(Protocol):
    """Application Form target lookup/update port."""

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        """Return Application Forms for a project."""

    def update(self, form: ApplicationForm) -> ApplicationForm:
        """Persist an updated Application Form."""


class ProjectSection2SyncService:
    """Preview and sync structured Section 2 dates from active Confirmed Matrix."""

    def __init__(
        self,
        *,
        project_store: Section2SyncProjectStore,
        confirmed_matrix_store: Section2SyncConfirmedMatrixStore,
        application_form_store: Section2SyncApplicationFormStore,
        clock: Callable[[], str] | None = None,
    ) -> None:
        self._project_store = project_store
        self._confirmed_matrix_store = confirmed_matrix_store
        self._application_form_store = application_form_store
        self._clock = clock or _utc_now_iso

    def preview(self, command: ProjectSection2SyncCommand) -> ProjectSection2SyncResult:
        """Return field-level Section 2 sync decisions without mutation."""
        snapshot, form = self._load_context(command.project_id)
        return self._build_result(command.project_id, snapshot, form, synced=False, operator=None)

    def sync(self, command: ProjectSection2SyncCommand) -> ProjectSection2SyncResult:
        """Sync valid changed Section 2 fields after preview identity is confirmed."""
        snapshot, form = self._load_context(command.project_id)
        self._validate_expected_identity(command, snapshot)
        preview = self._build_result(command.project_id, snapshot, form, synced=False, operator=None)
        blocked_fields = [field for field in preview.fields if field.status == "blocked_invalid_source"]
        if blocked_fields:
            raise ProjectSection2SyncValidationError(
                "Confirmed Matrix contains invalid Section 2 date values."
            )

        updates: dict[str, str] = {
            field.field_key: field.next_value
            for field in preview.fields
            if field.status == "will_change" and field.next_value is not None
        }
        if updates:
            form = replace(form, **updates)
            self._application_form_store.update(form)

        fields = tuple(
            replace(field, status="changed", current_value=field.current_value)
            if field.status == "will_change"
            else field
            for field in preview.fields
        )
        status = _sync_status(fields)
        return ProjectSection2SyncResult(
            project_id=preview.project_id,
            application_form_id=preview.application_form_id,
            confirmed_matrix_id=preview.confirmed_matrix_id,
            confirmed_revision=preview.confirmed_revision,
            fields=fields,
            status=status,
            synced_at=self._clock() if updates else None,
            operator=_normalize_optional(command.operator),
        )

    def _load_context(
        self,
        project_id: str,
    ) -> tuple[ConfirmedMatrixSnapshot, ApplicationForm]:
        project = self._project_store.get(project_id)
        if project is None:
            raise ProjectSection2SyncProjectNotFoundError(f"Project not found: {project_id}")
        snapshot = self._confirmed_matrix_store.get_active_by_project(project_id)
        if snapshot is None:
            raise ProjectSection2SyncReadinessError(
                "Confirm Matrix authority before syncing Section 2 dates."
            )
        forms = self._application_form_store.list_by_project(project_id)
        if not forms:
            raise ProjectSection2SyncReadinessError(
                "Application Form is required before syncing Section 2 dates."
            )
        if len(forms) > 1:
            raise ProjectSection2SyncAmbiguousTargetError(
                "Multiple Application Forms exist. Select the current Application Form before syncing Section 2 dates."
            )
        return snapshot, forms[0]

    def _build_result(
        self,
        project_id: str,
        snapshot: ConfirmedMatrixSnapshot,
        form: ApplicationForm,
        *,
        synced: bool,
        operator: str | None,
    ) -> ProjectSection2SyncResult:
        fields = (
            _field_sync(
                field_key="received_date",
                source_field_key="sample_received_date",
                source_value=snapshot.version.sample_received_date,
                current_value=form.received_date,
            ),
            _field_sync(
                field_key="estimated_completion_date",
                source_field_key="estimated_completion_date",
                source_value=snapshot.version.estimated_completion_date,
                current_value=form.estimated_completion_date,
            ),
        )
        return ProjectSection2SyncResult(
            project_id=project_id,
            application_form_id=form.form_id,
            confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
            confirmed_revision=snapshot.version.confirmed_revision,
            fields=fields,
            status=_preview_status(fields),
            synced_at=self._clock() if synced else None,
            operator=operator,
        )

    def _validate_expected_identity(
        self,
        command: ProjectSection2SyncCommand,
        snapshot: ConfirmedMatrixSnapshot,
    ) -> None:
        if not command.expected_confirmed_matrix_id or command.expected_confirmed_revision is None:
            raise ProjectSection2SyncValidationError(
                "Expected Confirmed Matrix id and revision are required for Section 2 sync."
            )
        version = snapshot.version
        if (
            command.expected_confirmed_matrix_id != version.confirmed_matrix_id
            or command.expected_confirmed_revision != version.confirmed_revision
        ):
            raise ProjectSection2SyncConflictError(
                "Confirmed Matrix changed after preview. Refresh Section 2 dates before syncing."
            )


def _field_sync(
    *,
    field_key: Section2FieldKey,
    source_field_key: Section2SourceFieldKey,
    source_value: str | None,
    current_value: str | None,
) -> ProjectSection2FieldSync:
    normalized_source = _normalize_optional(source_value)
    normalized_current = _normalize_optional(current_value)
    if normalized_source is None:
        return ProjectSection2FieldSync(
            field_key=field_key,
            source_field_key=source_field_key,
            source_value=source_value,
            current_value=current_value,
            next_value=current_value,
            status="skipped_missing_source",
            message="Confirmed Matrix source date is blank; existing Section 2 value is preserved.",
        )
    try:
        next_value = date.fromisoformat(normalized_source).isoformat()
    except ValueError:
        return ProjectSection2FieldSync(
            field_key=field_key,
            source_field_key=source_field_key,
            source_value=source_value,
            current_value=current_value,
            next_value=current_value,
            status="blocked_invalid_source",
            message="Confirmed Matrix source date must use YYYY-MM-DD.",
        )
    if normalized_current == next_value:
        return ProjectSection2FieldSync(
            field_key=field_key,
            source_field_key=source_field_key,
            source_value=source_value,
            current_value=current_value,
            next_value=next_value,
            status="unchanged",
            message="Section 2 already matches Confirmed Matrix.",
        )
    return ProjectSection2FieldSync(
        field_key=field_key,
        source_field_key=source_field_key,
        source_value=source_value,
        current_value=current_value,
        next_value=next_value,
        status="will_change",
        message="Section 2 will be updated from Confirmed Matrix.",
    )


def _preview_status(fields: tuple[ProjectSection2FieldSync, ...]) -> Section2SyncStatus:
    statuses = {field.status for field in fields}
    if "blocked_invalid_source" in statuses:
        return "blocked"
    if "will_change" in statuses:
        return "partial" if "skipped_missing_source" in statuses else "ready"
    if "skipped_missing_source" in statuses:
        return "partial"
    return "up_to_date"


def _sync_status(fields: tuple[ProjectSection2FieldSync, ...]) -> Section2SyncStatus:
    statuses = {field.status for field in fields}
    if "changed" in statuses:
        return "synced"
    if "skipped_missing_source" in statuses:
        return "partial"
    return "up_to_date"


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _utc_now_iso() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
