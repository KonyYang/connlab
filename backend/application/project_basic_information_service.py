"""Project Basic Information authority data/API service."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Protocol
from uuid import uuid4

from backend.application.project_identity import (
    select_registered_ltr,
    setup_payload_from_ltr_notes,
)
from backend.application.sample_description import format_description_pn
from backend.domain import ApplicationForm, LtrRecord, Project, SampleInfo


REQUIRED_FIELD_LABELS: dict[str, str] = {
    "dl_number": "DL/LTR Number",
    "project_type": "Project Type",
    "test_item": "Test Item",
    "requested_by": "Requested By",
    "project_leader": "Project Leader",
    "lab_performing_tests": "Lab Performing the Tests",
}

PRODUCT_DESCRIPTION_RULE_KEY = "product_description_or_description_pn"
PRODUCT_DESCRIPTION_RULE_LABEL = "Product Description or Description P/N"


@dataclass(frozen=True, slots=True)
class ProjectBasicInformationRecord:
    """Persisted Project Basic Information record."""

    record_id: str
    project_id: str
    status: str
    version: int
    values: dict[str, str]
    source_signature: str
    created_at: str
    updated_at: str
    confirmed_at: str | None = None
    confirmed_by: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectBasicInformationDraft:
    """Assembled or saved Basic Information draft."""

    values: dict[str, str]


@dataclass(frozen=True, slots=True)
class ProjectBasicInformationFieldSuggestion:
    """Source suggestion for one Basic Information field."""

    field_key: str
    source: str
    source_value: str
    needs_review: bool


@dataclass(frozen=True, slots=True)
class ProjectBasicInformationResult:
    """Read model returned by Basic Information service/API."""

    project_id: str
    status: str
    draft: ProjectBasicInformationDraft
    latest_confirmed: ProjectBasicInformationRecord | None
    field_suggestions: dict[str, ProjectBasicInformationFieldSuggestion]
    changed_source_fields: tuple[str, ...]
    missing_required_fields: tuple[str, ...]
    missing_required_labels: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SaveProjectBasicInformationDraftCommand:
    """Command to save an operator draft."""

    project_id: str
    values: dict[str, str]


@dataclass(frozen=True, slots=True)
class ConfirmProjectBasicInformationCommand:
    """Command to confirm Basic Information authority."""

    project_id: str
    values: dict[str, str]
    confirmed_by: str


class ProjectBasicInformationError(ValueError):
    """Base error for Project Basic Information operations."""


class ProjectBasicInformationVersionConflictError(ProjectBasicInformationError):
    """Raised when a confirmed version cannot be created due to a version conflict."""


class ProjectBasicInformationProjectNotFoundError(LookupError):
    """Raised when the target project does not exist."""


class ProjectBasicInformationMissingRequiredError(ProjectBasicInformationError):
    """Raised when confirmation misses required business fields."""

    def __init__(self, *, missing_fields: tuple[str, ...], missing_labels: tuple[str, ...]):
        """Create a missing-required-field error."""
        super().__init__("Basic Information is missing required fields.")
        self.missing_fields = missing_fields
        self.missing_labels = missing_labels


class ProjectRepositoryPort(Protocol):
    """Project lookup port."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


class LtrRecordRepositoryPort(Protocol):
    """LTR lookup port."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return LTR records for a project."""


class ApplicationFormRepositoryPort(Protocol):
    """Application form lookup port."""

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        """Return application forms for a project."""


class SampleInfoRepositoryPort(Protocol):
    """Application-form sample info lookup port."""

    def list_by_project(self, project_id: str) -> list[SampleInfo]:
        """Return sample rows for a project."""


class ProjectBasicInformationRepositoryPort(Protocol):
    """Persistence port for Basic Information records."""

    def get_latest_draft(self, project_id: str) -> ProjectBasicInformationRecord | None:
        """Return the current draft for one project."""

    def get_latest_confirmed(
        self, project_id: str
    ) -> ProjectBasicInformationRecord | None:
        """Return the latest confirmed record for one project."""

    def list_confirmed_by_project(
        self, project_id: str
    ) -> list[ProjectBasicInformationRecord]:
        """Return confirmed records ordered by version."""

    def save_draft(
        self, record: ProjectBasicInformationRecord
    ) -> ProjectBasicInformationRecord:
        """Create or update the project draft record."""

    def create_confirmed(
        self, record: ProjectBasicInformationRecord
    ) -> ProjectBasicInformationRecord:
        """Persist a new confirmed record."""

    def next_confirmed_version(self, project_id: str) -> int:
        """Return the next confirmed version number for one project."""


class ProjectBasicInformationService:
    """Application service for Project Basic Information authority."""

    def __init__(
        self,
        *,
        project_store: ProjectRepositoryPort,
        ltr_store: LtrRecordRepositoryPort,
        application_form_store: ApplicationFormRepositoryPort,
        sample_store: SampleInfoRepositoryPort,
        basic_information_store: ProjectBasicInformationRepositoryPort,
        clock: Callable[[], str],
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        """Create the service with explicit persistence/source dependencies."""
        self._projects = project_store
        self._records = basic_information_store
        self._clock = clock
        self._id_factory = id_factory or (lambda: uuid4().hex)
        self._source_assembler = ProjectBasicInformationSourceAssembler(
            ltr_store=ltr_store,
            application_form_store=application_form_store,
            sample_store=sample_store,
        )

    def get(self, project_id: str) -> ProjectBasicInformationResult:
        """Return the current Basic Information read model."""
        project = self._require_project(project_id)
        latest_draft = self._records.get_latest_draft(project_id)
        latest_confirmed = self._records.get_latest_confirmed(project_id)
        suggestions = self._source_assembler.assemble(project)
        base_values = self._merge_values(
            draft=latest_draft,
            confirmed=latest_confirmed,
            suggestions=suggestions,
        )
        changed_fields = _changed_source_fields(latest_confirmed, suggestions)
        suggestions = _mark_review_suggestions(suggestions, changed_fields)
        status = _result_status(latest_confirmed, changed_fields)
        missing_fields = _missing_required_fields(base_values)
        return ProjectBasicInformationResult(
            project_id=project_id,
            status=status,
            draft=ProjectBasicInformationDraft(values=base_values),
            latest_confirmed=latest_confirmed,
            field_suggestions=suggestions,
            changed_source_fields=changed_fields,
            missing_required_fields=missing_fields,
            missing_required_labels=_missing_required_labels(missing_fields),
            blockers=tuple(),
            warnings=tuple(),
        )

    def save_draft(
        self, command: SaveProjectBasicInformationDraftCommand
    ) -> ProjectBasicInformationResult:
        """Persist an operator draft and return the updated read model."""
        self._require_project(command.project_id)
        now = self._clock()
        existing = self._records.get_latest_draft(command.project_id)
        project = self._require_project(command.project_id)
        source_signature = _source_signature(
            self._source_assembler.assemble(project)
        )
        record = ProjectBasicInformationRecord(
            record_id=existing.record_id if existing else self._id_factory(),
            project_id=command.project_id,
            status="draft",
            version=0,
            values=_clean_values(command.values),
            source_signature=source_signature,
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        self._records.save_draft(record)
        return self.get(command.project_id)

    def confirm(
        self, command: ConfirmProjectBasicInformationCommand
    ) -> ProjectBasicInformationResult:
        """Create a new confirmed Basic Information version."""
        self._require_project(command.project_id)
        values = _clean_values(command.values)
        missing_fields = _missing_required_fields(values)
        if missing_fields:
            raise ProjectBasicInformationMissingRequiredError(
                missing_fields=missing_fields,
                missing_labels=_missing_required_labels(missing_fields),
            )
        now = self._clock()
        project = self._require_project(command.project_id)
        source_signature = _source_signature(
            self._source_assembler.assemble(project)
        )
        next_version = self._records.next_confirmed_version(command.project_id)
        self._records.create_confirmed(
            ProjectBasicInformationRecord(
                record_id=self._id_factory(),
                project_id=command.project_id,
                status="confirmed",
                version=next_version,
                values=values,
                source_signature=source_signature,
                created_at=now,
                updated_at=now,
                confirmed_at=now,
                confirmed_by=command.confirmed_by,
            )
        )
        return self.get(command.project_id)

    def _require_project(self, project_id: str) -> Project:
        project = self._projects.get(project_id)
        if project is None:
            raise ProjectBasicInformationProjectNotFoundError(
                f"Project not found: {project_id}"
            )
        return project

    def _merge_values(
        self,
        *,
        draft: ProjectBasicInformationRecord | None,
        confirmed: ProjectBasicInformationRecord | None,
        suggestions: dict[str, ProjectBasicInformationFieldSuggestion],
    ) -> dict[str, str]:
        if draft is not None:
            values = dict(draft.values)
        elif confirmed is not None:
            values = dict(confirmed.values)
        else:
            values = {}
        for key, suggestion in suggestions.items():
            values.setdefault(key, suggestion.source_value)
        return values


class ProjectBasicInformationSourceAssembler:
    """Assemble Basic Information source suggestions from current 330A providers."""

    def __init__(
        self,
        *,
        ltr_store: LtrRecordRepositoryPort,
        application_form_store: ApplicationFormRepositoryPort,
        sample_store: SampleInfoRepositoryPort,
    ) -> None:
        """Create a source assembler for Project/LTR/ApplicationForm sources."""
        self._ltrs = ltr_store
        self._forms = application_form_store
        self._samples = sample_store

    def assemble(self, project: Project) -> dict[str, ProjectBasicInformationFieldSuggestion]:
        """Return current source suggestions for a project."""
        forms = self._forms.list_by_project(project.project_id)
        latest_form = forms[-1] if forms else None
        samples = self._samples.list_by_project(project.project_id)
        ltrs = self._ltrs.list_by_project(project.project_id)
        latest_ltr = ltrs[-1] if ltrs else None
        registered_ltr = select_registered_ltr(ltrs)
        setup_payload = setup_payload_from_ltr_notes(
            registered_ltr.notes if registered_ltr else None
        )
        raw_values: dict[str, tuple[str, str | None]] = {
            "dl_number": (
                "project_identity",
                (latest_ltr.ltr_number if latest_ltr else None) or project.project_no,
            ),
            "project_type": ("application_form", latest_form.project_type if latest_form else None),
            "product_description": ("project_identity", project.product_name),
            "description_pn": ("sample_info", format_description_pn(samples)),
            "test_item": (
                "application_form",
                latest_form.requested_testing if latest_form else None,
            ),
            "requested_by": (
                "application_form",
                (latest_form.requester if latest_form else None) or project.requestor,
            ),
            "project_leader": (
                "application_form",
                latest_form.assigned_personnel if latest_form else None,
            ),
            "lab_performing_tests": (
                "application_form",
                latest_form.lab if latest_form else None,
            ),
            "phone": ("application_form", latest_form.phone if latest_form else None),
            "requestor_email": (
                "application_form",
                latest_form.email if latest_form else None,
            ),
            "location": (
                "application_form",
                latest_form.manufacturing_site if latest_form else None,
            ),
            "business_unit": (
                "application_form",
                (latest_form.business_unit if latest_form else None) or project.business_unit,
            ),
            "test_type": ("application_form", latest_form.test_type if latest_form else None),
            "test_type_in_sheet": (
                "project_setup_confirmation",
                _text_from_payload(setup_payload.get("test_type_in_sheet")),
            ),
            "sub_contract": (
                "application_form",
                latest_form.subcontract if latest_form else None,
            ),
            "condition_of_samples_when_received": (
                "application_form",
                latest_form.sample_condition if latest_form else None,
            ),
            "date_lab_received_samples": (
                "application_form",
                latest_form.received_date if latest_form else None,
            ),
            "estimated_completion_date": (
                "application_form",
                latest_form.estimated_completion_date if latest_form else None,
            ),
        }
        return {
            key: ProjectBasicInformationFieldSuggestion(
                field_key=key,
                source=source,
                source_value=value.strip(),
                needs_review=False,
            )
            for key, (source, value) in raw_values.items()
            if value is not None and value.strip()
        }


def _text_from_payload(value: object) -> str | None:
    """Return stripped setup payload text."""
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _result_status(
    latest_confirmed: ProjectBasicInformationRecord | None,
    changed_fields: tuple[str, ...],
) -> str:
    if latest_confirmed is None:
        return "unconfirmed"
    if changed_fields:
        return "needs_review"
    return "confirmed"


def _changed_source_fields(
    latest_confirmed: ProjectBasicInformationRecord | None,
    suggestions: dict[str, ProjectBasicInformationFieldSuggestion],
) -> tuple[str, ...]:
    if latest_confirmed is None:
        return tuple()
    confirmed_source_values = _source_values_from_signature(
        latest_confirmed.source_signature
    )
    current_source_values = _source_values_from_suggestions(suggestions)
    return tuple(
        key
        for key in sorted(set(confirmed_source_values) | set(current_source_values))
        if confirmed_source_values.get(key, "").strip()
        != current_source_values.get(key, "").strip()
    )


def _mark_review_suggestions(
    suggestions: dict[str, ProjectBasicInformationFieldSuggestion],
    changed_fields: tuple[str, ...],
) -> dict[str, ProjectBasicInformationFieldSuggestion]:
    changed = set(changed_fields)
    return {
        key: ProjectBasicInformationFieldSuggestion(
            field_key=suggestion.field_key,
            source=suggestion.source,
            source_value=suggestion.source_value,
            needs_review=key in changed,
        )
        for key, suggestion in suggestions.items()
    }


def _missing_required_fields(values: dict[str, str]) -> tuple[str, ...]:
    missing = [
        key for key in REQUIRED_FIELD_LABELS if not values.get(key, "").strip()
    ]
    if not (
        values.get("product_description", "").strip()
        or values.get("description_pn", "").strip()
    ):
        missing.insert(2, PRODUCT_DESCRIPTION_RULE_KEY)
    return tuple(missing)


def _missing_required_labels(missing_fields: tuple[str, ...]) -> tuple[str, ...]:
    labels: list[str] = []
    for key in missing_fields:
        if key == PRODUCT_DESCRIPTION_RULE_KEY:
            labels.append(PRODUCT_DESCRIPTION_RULE_LABEL)
        else:
            labels.append(REQUIRED_FIELD_LABELS[key])
    return tuple(labels)


def _clean_values(values: dict[str, str]) -> dict[str, str]:
    return {
        str(key): str(value).strip()
        for key, value in values.items()
        if value is not None and str(value).strip()
    }


def _source_signature(
    suggestions: dict[str, ProjectBasicInformationFieldSuggestion],
) -> str:
    return _signature(_source_values_from_suggestions(suggestions))


def _source_values_from_suggestions(
    suggestions: dict[str, ProjectBasicInformationFieldSuggestion],
) -> dict[str, str]:
    return {key: suggestion.source_value for key, suggestion in suggestions.items()}


def _source_values_from_signature(signature: str) -> dict[str, str]:
    try:
        loaded = json.loads(signature)
    except json.JSONDecodeError:
        return {}
    if not isinstance(loaded, dict):
        return {}
    return {
        str(key): str(value).strip()
        for key, value in loaded.items()
        if value is not None and str(value).strip()
    }


def _signature(values: dict[str, str]) -> str:
    return json.dumps(_clean_values(values), ensure_ascii=False, sort_keys=True)
