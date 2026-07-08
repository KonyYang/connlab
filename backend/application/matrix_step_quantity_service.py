"""Application service for Matrix Step quantity setup."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Protocol

from backend.application.project_basic_information_service import (
    ProjectBasicInformationRecord,
)
from backend.domain import (
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStepQuantity,
)
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens


SOURCE_BASIC_INFORMATION_CONFIRMED = "basic_information_confirmed"
SOURCE_BASIC_INFORMATION_DRAFT = "basic_information_draft"
SOURCE_MATRIX_STEP_OVERRIDE = "matrix_step_override"
SOURCE_MANUAL_REQUIRED = "manual_required"
SOURCE_CONFIRMED_MATRIX_CARRY_FORWARD = "confirmed_matrix_carry_forward"
_VALID_SOURCES = {
    SOURCE_BASIC_INFORMATION_CONFIRMED,
    SOURCE_BASIC_INFORMATION_DRAFT,
    SOURCE_MATRIX_STEP_OVERRIDE,
    SOURCE_MANUAL_REQUIRED,
    SOURCE_CONFIRMED_MATRIX_CARRY_FORWARD,
}
_NON_NEGATIVE_DECIMAL = re.compile(r"^\d+(?:\.\d+)?$")


class MatrixStepQuantityError(ValueError):
    """Base error for Matrix Step quantity setup."""


class MatrixStepQuantityNotFoundError(LookupError):
    """Raised when the requested Matrix draft does not exist."""


class MatrixStepQuantityValidationError(MatrixStepQuantityError):
    """Raised when Step quantity input is invalid."""


class ProjectMatrixDraftStore(Protocol):
    """Draft operations required by the quantity setup service."""

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        """Return one Matrix draft aggregate."""

    def replace_step_quantities(
        self,
        project_matrix_draft_id: str,
        quantities: tuple[ProjectMatrixDraftStepQuantity, ...],
    ) -> tuple[ProjectMatrixDraftStepQuantity, ...]:
        """Replace Step quantity records for one Matrix draft."""


class BasicInformationStore(Protocol):
    """Read-only Basic Information defaults required by this service."""

    def get_latest_confirmed(
        self,
        project_id: str,
    ) -> ProjectBasicInformationRecord | None:
        """Return latest confirmed Basic Information."""

    def get_latest_draft(self, project_id: str) -> ProjectBasicInformationRecord | None:
        """Return latest draft Basic Information."""


@dataclass(frozen=True, slots=True)
class MatrixStepQuantityItem:
    """Read model for one Matrix Step quantity setup row."""

    draft_group_id: str
    draft_row_id: str
    step_sequence: int
    step_suffix_note: str | None
    raw_token: str | None
    test_item: str
    test_points_per_sample: str | None
    readings_per_point: str | None
    contact_points_per_sample: str | None
    total_readings: str | None
    source: str
    review_required: bool
    review_reason: str | None


@dataclass(frozen=True, slots=True)
class MatrixStepQuantityDraftResponse:
    """Draft Step quantity setup response."""

    project_id: str
    project_matrix_draft_id: str
    items: tuple[MatrixStepQuantityItem, ...]


@dataclass(frozen=True, slots=True)
class MatrixStepQuantitySaveItem:
    """Save payload for one Matrix Step quantity setup row."""

    draft_group_id: str
    draft_row_id: str
    step_sequence: int
    step_suffix_note: str | None
    raw_token: str | None
    test_points_per_sample: str | None
    readings_per_point: str | None
    contact_points_per_sample: str | None
    source: str
    review_required: bool
    review_reason: str | None


@dataclass(frozen=True, slots=True)
class MatrixStepQuantitySaveCommand:
    """Command to save draft Step quantity setup records."""

    project_id: str
    project_matrix_draft_id: str
    items: tuple[MatrixStepQuantitySaveItem, ...]


@dataclass(frozen=True, slots=True)
class _ParsedStep:
    draft_group_id: str
    draft_row_id: str
    step_sequence: int
    step_suffix_note: str | None
    raw_token: str | None
    test_item: str

    @property
    def identity(self) -> tuple[str, str, int, str]:
        return (
            self.draft_group_id,
            self.draft_row_id,
            self.step_sequence,
            _suffix_identity_value(self.step_suffix_note),
        )


class MatrixStepQuantityService:
    """Build and persist Matrix Step quantity setup for one draft."""

    def __init__(
        self,
        *,
        draft_store: ProjectMatrixDraftStore,
        basic_information_store: BasicInformationStore,
        clock: Callable[[], str],
        id_factory: Callable[[], str],
    ) -> None:
        self._drafts = draft_store
        self._basic_information = basic_information_store
        self._clock = clock
        self._id_factory = id_factory

    def get_draft(
        self,
        *,
        project_id: str,
        project_matrix_draft_id: str,
    ) -> MatrixStepQuantityDraftResponse:
        """Return quantity setup rows for all selected Matrix draft Steps."""
        draft = self._require_draft(project_id, project_matrix_draft_id)
        parsed_steps = _parse_draft_steps(draft)
        persisted_by_identity = {
            (
                item.draft_group_id,
                item.draft_row_id,
                item.step_sequence,
                _suffix_identity_value(item.step_suffix_note),
            ): item
            for item in draft.step_quantities
        }
        default_values, default_source = self._basic_information_defaults(project_id)
        items = tuple(
            _to_response_item(
                step=step,
                persisted=persisted_by_identity.get(step.identity),
                defaults=default_values,
                default_source=default_source,
            )
            for step in parsed_steps
        )
        return MatrixStepQuantityDraftResponse(
            project_id=project_id,
            project_matrix_draft_id=project_matrix_draft_id,
            items=items,
        )

    def save_draft(
        self,
        command: MatrixStepQuantitySaveCommand,
    ) -> MatrixStepQuantityDraftResponse:
        """Persist operator quantity setup records and return the updated rows."""
        draft = self._require_draft(command.project_id, command.project_matrix_draft_id)
        valid_identities = {step.identity for step in _parse_draft_steps(draft)}
        seen_identities: set[tuple[str, str, int, str]] = set()
        now = self._clock()
        quantities: list[ProjectMatrixDraftStepQuantity] = []
        for item in command.items:
            identity = (
                item.draft_group_id,
                item.draft_row_id,
                item.step_sequence,
                _suffix_identity_value(item.step_suffix_note),
            )
            if identity in seen_identities:
                raise MatrixStepQuantityValidationError(
                    "Duplicate Step quantity identity in save payload."
                )
            seen_identities.add(identity)
            if identity not in valid_identities:
                raise MatrixStepQuantityValidationError(
                    "Step quantity identity is not part of this Matrix draft."
                )
            _validate_source(item.source)
            test_points = _clean_quantity(
                item.test_points_per_sample,
                "Test points / sample",
            )
            readings = _clean_quantity(item.readings_per_point, "Readings / point")
            contacts = _clean_quantity(
                item.contact_points_per_sample,
                "Contact points / sample",
            )
            quantities.append(
                ProjectMatrixDraftStepQuantity(
                    draft_step_quantity_id=self._id_factory(),
                    project_matrix_draft_id=command.project_matrix_draft_id,
                    draft_group_id=item.draft_group_id,
                    draft_row_id=item.draft_row_id,
                    step_sequence=item.step_sequence,
                    step_suffix_note=_normalize_optional_text(item.step_suffix_note),
                    raw_token=_normalize_optional_text(item.raw_token),
                    test_points_per_sample=test_points,
                    readings_per_point=readings,
                    contact_points_per_sample=contacts,
                    source=item.source,
                    review_required=item.review_required
                    or _requires_review(test_points, readings),
                    review_reason=_review_reason(
                        item.review_reason,
                        test_points=test_points,
                        readings=readings,
                    ),
                    updated_at=now,
                )
            )
        self._drafts.replace_step_quantities(
            command.project_matrix_draft_id,
            tuple(quantities),
        )
        return self.get_draft(
            project_id=command.project_id,
            project_matrix_draft_id=command.project_matrix_draft_id,
        )

    def _require_draft(
        self,
        project_id: str,
        project_matrix_draft_id: str,
    ) -> ProjectMatrixDraftSnapshot:
        draft = self._drafts.get(project_matrix_draft_id)
        if draft is None or draft.record.project_id != project_id:
            raise MatrixStepQuantityNotFoundError("Project matrix draft not found.")
        return draft

    def _basic_information_defaults(
        self,
        project_id: str,
    ) -> tuple[dict[str, str | None], str]:
        confirmed = self._basic_information.get_latest_confirmed(project_id)
        if confirmed is not None:
            return _quantity_defaults(confirmed), SOURCE_BASIC_INFORMATION_CONFIRMED
        draft = self._basic_information.get_latest_draft(project_id)
        if draft is not None:
            return _quantity_defaults(draft), SOURCE_BASIC_INFORMATION_DRAFT
        return {}, SOURCE_MANUAL_REQUIRED


def _parse_draft_steps(draft: ProjectMatrixDraftSnapshot) -> tuple[_ParsedStep, ...]:
    selected_group_ids = {group.draft_group_id for group in draft.groups if group.is_selected}
    row_by_id = {row.draft_row_id: row for row in draft.rows if not row.is_sample_row}
    steps: list[_ParsedStep] = []
    for cell in draft.cells:
        if cell.draft_group_id not in selected_group_ids:
            continue
        row = row_by_id.get(cell.draft_row_id)
        if row is None:
            continue
        parsed_tokens, _warnings = parse_step_tokens(cell.cell_value)
        for token in parsed_tokens:
            steps.append(
                _ParsedStep(
                    draft_group_id=cell.draft_group_id,
                    draft_row_id=cell.draft_row_id,
                    step_sequence=token.sequence,
                    step_suffix_note=token.suffix_note,
                    raw_token=token.raw_token,
                    test_item=row.test_item,
                )
            )
    return tuple(
        sorted(
            steps,
            key=lambda item: (item.draft_group_id, item.step_sequence, item.draft_row_id),
        )
    )


def _to_response_item(
    *,
    step: _ParsedStep,
    persisted: ProjectMatrixDraftStepQuantity | None,
    defaults: dict[str, str | None],
    default_source: str,
) -> MatrixStepQuantityItem:
    if persisted is not None:
        test_points = persisted.test_points_per_sample
        readings = persisted.readings_per_point
        contacts = persisted.contact_points_per_sample
        source = persisted.source
        review_required = persisted.review_required
        review_reason = persisted.review_reason
    else:
        test_points = defaults.get("test_points_per_sample")
        readings = defaults.get("readings_per_point")
        contacts = defaults.get("contact_points_per_sample")
        source = default_source
        review_required = _requires_review(test_points, readings)
        review_reason = _review_reason(None, test_points=test_points, readings=readings)
    return MatrixStepQuantityItem(
        draft_group_id=step.draft_group_id,
        draft_row_id=step.draft_row_id,
        step_sequence=step.step_sequence,
        step_suffix_note=step.step_suffix_note,
        raw_token=step.raw_token,
        test_item=step.test_item,
        test_points_per_sample=test_points,
        readings_per_point=readings,
        contact_points_per_sample=contacts,
        total_readings=_derive_total_readings(test_points, readings),
        source=source,
        review_required=review_required,
        review_reason=review_reason,
    )


def _quantity_defaults(record: ProjectBasicInformationRecord) -> dict[str, str | None]:
    return {
        "test_points_per_sample": _normalize_optional_text(
            record.values.get("test_points_per_sample")
        ),
        "readings_per_point": _normalize_optional_text(record.values.get("readings_per_point")),
        "contact_points_per_sample": _normalize_optional_text(
            record.values.get("contact_points_per_sample")
        ),
    }


def _clean_quantity(value: str | None, label: str) -> str | None:
    text = _normalize_optional_text(value)
    if text is None:
        return None
    if not _NON_NEGATIVE_DECIMAL.fullmatch(text):
        raise MatrixStepQuantityValidationError(f"{label} must be a non-negative number.")
    return text


def _validate_source(source: str) -> None:
    if source not in _VALID_SOURCES:
        raise MatrixStepQuantityValidationError("Step quantity source is not supported.")


def _derive_total_readings(
    test_points_per_sample: str | None,
    readings_per_point: str | None,
) -> str | None:
    if not test_points_per_sample or not readings_per_point:
        return None
    total = Decimal(test_points_per_sample) * Decimal(readings_per_point)
    return format(total.normalize(), "f")


def _requires_review(
    test_points_per_sample: str | None,
    readings_per_point: str | None,
) -> bool:
    return not test_points_per_sample or not readings_per_point


def _review_reason(
    existing: str | None,
    *,
    test_points: str | None,
    readings: str | None,
) -> str | None:
    normalized = _normalize_optional_text(existing)
    if normalized:
        return normalized
    if _requires_review(test_points, readings):
        return "Confirm Step quantity values."
    return None


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _suffix_identity_value(value: str | None) -> str:
    return _normalize_optional_text(value) or ""
