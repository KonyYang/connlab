"""Application service for LTR readiness evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.domain import ApplicationForm, FileAsset, Project, SampleInfo
from backend.modules.ltr import (
    LtrFieldDefinition,
    LtrNumberError,
    ReadinessSeverity,
    get_ltr_field_catalog,
    parse_ltr_number,
)


class LtrReadinessError(ValueError):
    """Raised when readiness input is invalid."""


class LtrReadinessNotFoundError(LookupError):
    """Raised when readiness cannot be evaluated for a missing project."""


@dataclass(frozen=True, slots=True)
class LtrReadinessField:
    """Readiness state for one LTR field."""

    key: str
    label: str
    value: str | None
    source: str | None
    severity: ReadinessSeverity
    state: str
    operator_action: str
    placeholder_policy: str | None = None


@dataclass(frozen=True, slots=True)
class LtrReadinessResult:
    """Readiness evaluation result for one project."""

    project_id: str
    status: str
    fields: tuple[LtrReadinessField, ...]
    blockers: tuple[LtrReadinessField, ...]
    warnings: tuple[LtrReadinessField, ...]


class ProjectRepositoryPort(Protocol):
    """Project repository behavior required by readiness service."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""


class ApplicationFormRepositoryPort(Protocol):
    """Application form repository behavior required by readiness service."""

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        """Return application forms for a project."""


class SampleInfoRepositoryPort(Protocol):
    """Sample repository behavior required by readiness service."""

    def list_by_project(self, project_id: str) -> list[SampleInfo]:
        """Return sample rows for a project."""


class FileAssetRepositoryPort(Protocol):
    """File asset repository behavior required by readiness service."""

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        """Return file assets for a project."""


class LtrReadinessService:
    """Evaluate LTR readiness fields before preview or registration."""

    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        form_repository: ApplicationFormRepositoryPort,
        sample_repository: SampleInfoRepositoryPort,
        file_asset_repository: FileAssetRepositoryPort,
    ) -> None:
        """Create a readiness service with repository ports."""
        self._projects = project_repository
        self._forms = form_repository
        self._samples = sample_repository
        self._assets = file_asset_repository

    def evaluate_project(
        self,
        project_id: str,
        proposed_ltr_number: str | None = None,
    ) -> LtrReadinessResult:
        """Evaluate LTR readiness for one project."""
        project = self._projects.get(project_id)
        if project is None:
            raise LtrReadinessNotFoundError(f"Project not found: {project_id}")
        normalized_ltr_number = _normalize_proposed_ltr_number(proposed_ltr_number)
        forms = self._forms.list_by_project(project_id)
        samples = self._samples.list_by_project(project_id)
        assets = self._assets.list_by_project(project_id)
        context = _ReadinessContext(
            project=project,
            form=forms[-1] if forms else None,
            samples=samples,
            assets=assets,
            proposed_ltr_number=normalized_ltr_number,
        )
        fields = tuple(
            _evaluate_field(definition, context)
            for definition in get_ltr_field_catalog()
        )
        blockers = tuple(
            field
            for field in fields
            if field.severity is ReadinessSeverity.BLOCKER and field.state == "missing"
        )
        warnings = tuple(field for field in fields if field.state == "needs_review")
        return LtrReadinessResult(
            project_id=project_id,
            status=_readiness_status(blockers, warnings),
            fields=fields,
            blockers=blockers,
            warnings=warnings,
        )


@dataclass(frozen=True, slots=True)
class _ReadinessContext:
    """Data available to readiness field resolvers."""

    project: Project
    form: ApplicationForm | None
    samples: list[SampleInfo]
    assets: list[FileAsset]
    proposed_ltr_number: str | None


def _evaluate_field(
    definition: LtrFieldDefinition,
    context: _ReadinessContext,
) -> LtrReadinessField:
    """Evaluate one catalog definition."""
    if definition.severity is ReadinessSeverity.PLACEHOLDER_ALLOWED:
        return LtrReadinessField(
            key=definition.key,
            label=definition.display_label,
            value=_placeholder_value(definition.placeholder_policy),
            source="placeholder_policy",
            severity=definition.severity,
            state="placeholder",
            operator_action=definition.operator_action,
            placeholder_policy=definition.placeholder_policy,
        )
    if definition.key == "dl" and context.proposed_ltr_number is None:
        return LtrReadinessField(
            key=definition.key,
            label=definition.display_label,
            value=None,
            source="ltr.preview.pending_generation",
            severity=definition.severity,
            state="pending_preview",
            operator_action=definition.operator_action,
            placeholder_policy=definition.placeholder_policy,
        )
    value, source = _resolve_value(definition.key, context)
    state = _field_state(definition.severity, value)
    return LtrReadinessField(
        key=definition.key,
        label=definition.display_label,
        value=value,
        source=source,
        severity=definition.severity,
        state=state,
        operator_action=definition.operator_action,
        placeholder_policy=definition.placeholder_policy,
    )


def _field_state(severity: ReadinessSeverity, value: str | None) -> str:
    """Return readiness state for a field."""
    if severity is ReadinessSeverity.REVIEW_REQUIRED:
        return "needs_review"
    return "confirmed" if value else "missing"


def _readiness_status(
    blockers: tuple[LtrReadinessField, ...],
    warnings: tuple[LtrReadinessField, ...],
) -> str:
    """Return aggregate readiness status."""
    if blockers:
        return "blocked"
    if warnings:
        return "review_required"
    return "ready"


def _resolve_value(key: str, context: _ReadinessContext) -> tuple[str | None, str | None]:
    """Resolve a catalog field value from confirmed project data."""
    resolvers = {
        "project_type": lambda: _form_value(context.form, "project_type"),
        "description_pn": lambda: _sample_description(context.samples),
        "test_item": lambda: _form_value(context.form, "requested_testing"),
        "applicable_specifications": lambda: _specification_value(
            context.assets,
            context.form,
        ),
        "test_type": lambda: _form_value(context.form, "test_type"),
        "requested_by": lambda: _first_value(
            _form_value(context.form, "requester"),
            _string_value(context.project.requestor, "project.requestor"),
        ),
        "location": lambda: _first_value(
            _form_value(context.form, "manufacturing_site"),
            _form_value(context.form, "lab"),
        ),
        "project_leader": lambda: _form_value(context.form, "assigned_personnel"),
        "sample_deposition": lambda: _form_value(context.form, "post_testing_disposition"),
        "sub_contract": lambda: _first_value(
            _bool_form_value(context.form, "subcontract_allowed"),
            _form_value(context.form, "subcontract"),
        ),
        "remarks_po": lambda: _form_value(context.form, "additional_information"),
        "phone": lambda: _form_value(context.form, "phone"),
        "requestor_email": lambda: _form_value(context.form, "email"),
        "product_description": lambda: _first_value(
            _string_value(context.project.product_name, "project.product_name"),
            _sample_product(context.samples),
        ),
        "lab_performing_tests": lambda: _form_value(context.form, "lab"),
        "dl": lambda: _string_value(
            context.proposed_ltr_number,
            "ltr.preview.proposed_ltr_number",
        ),
        "test_fee": lambda: (None, None),
    }
    return resolvers.get(key, lambda: (None, None))()


def _normalize_proposed_ltr_number(value: str | None) -> str | None:
    """Validate and normalize an optional proposed LTR number."""
    if value is None:
        return None
    try:
        return parse_ltr_number(value).normalized
    except LtrNumberError as exc:
        raise LtrReadinessError(str(exc)) from exc


def _form_value(form: ApplicationForm | None, field_name: str) -> tuple[str | None, str | None]:
    """Return a non-empty application form value."""
    if form is None:
        return None, None
    return _string_value(getattr(form, field_name), f"application_form.{field_name}")


def _bool_form_value(
    form: ApplicationForm | None,
    field_name: str,
) -> tuple[str | None, str | None]:
    """Return a boolean application form value as Yes/No."""
    if form is None:
        return None, None
    value = getattr(form, field_name)
    if value is None:
        return None, None
    return ("Yes" if value else "No"), f"application_form.{field_name}"


def _string_value(value: object, source: str) -> tuple[str | None, str | None]:
    """Return a stripped string value with source path."""
    if value is None:
        return None, None
    text = str(value).strip()
    return (text, source) if text else (None, None)


def _first_value(*values: tuple[str | None, str | None]) -> tuple[str | None, str | None]:
    """Return the first non-empty value/source pair."""
    for value, source in values:
        if value:
            return value, source
    return None, None


def _sample_description(samples: list[SampleInfo]) -> tuple[str | None, str | None]:
    """Return part number and product name from the first sample."""
    if not samples:
        return None, None
    sample = samples[0]
    parts = [sample.part_number, sample.product_name]
    value = " / ".join(part for part in parts if part)
    return _string_value(value, "sample_info.part_number")


def _sample_product(samples: list[SampleInfo]) -> tuple[str | None, str | None]:
    """Return product name from the first sample."""
    if not samples:
        return None, None
    return _string_value(samples[0].product_name, "sample_info.product_name")


def _specification_value(
    assets: list[FileAsset],
    form: ApplicationForm | None,
) -> tuple[str | None, str | None]:
    """Return a supporting specification or attachment asset name."""
    for asset in assets:
        label = asset.original_name or asset.path.name
        lowered = label.lower()
        if "spec" in lowered or asset.path.suffix.lower() == ".pdf":
            return label, "file_assets.specification"
    value, source = _form_value(form, "requested_testing")
    if value and ("spec" in value.lower() or "standard" in value.lower()):
        return value, source
    return None, None


def _placeholder_value(placeholder_policy: str | None) -> str | None:
    """Extract the placeholder token from the policy text when present."""
    if not placeholder_policy:
        return None
    if '"Pending"' in placeholder_policy:
        return "Pending"
    if '"N/A"' in placeholder_policy:
        return "N/A"
    return placeholder_policy
