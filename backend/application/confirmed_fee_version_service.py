"""Create and read Confirmed Fee authority versions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Callable, Protocol
from uuid import uuid4

from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftContext,
    FeeEvaluationPricingDraftLoadResult,
    edited_values_to_json,
)
from backend.domain.confirmed_fee import (
    ConfirmedFeeStatus,
    ConfirmedFeeSummary,
    ConfirmedFeeVersion,
)


class ConfirmedFeePricingDraftMissingError(ValueError):
    """Raised when no saved Fee Evaluation pricing draft can be confirmed."""


class ConfirmedFeePricingDraftStaleError(ValueError):
    """Raised when the saved Fee Evaluation pricing draft is stale."""


class ConfirmedFeePricingDraftChangedError(ValueError):
    """Raised when the expected saved pricing draft no longer matches latest."""


class ConfirmedFeeSummaryValidationError(ValueError):
    """Raised when confirmation totals are incomplete or non-numeric."""


@dataclass(frozen=True, slots=True)
class ConfirmFeeVersionCommand:
    """Input for confirming the current saved Fee Evaluation pricing draft."""

    project_id: str
    confirmed_by: str
    expected_pricing_draft_edit_id: str
    summary: ConfirmedFeeSummary
    confirmation_note: str | None = None


@dataclass(frozen=True, slots=True)
class ConfirmedFeeVersionReadResult:
    """Latest Confirmed Fee status for the current project context."""

    status: ConfirmedFeeStatus
    current_context: FeeEvaluationPricingDraftContext
    latest_confirmed_fee: ConfirmedFeeVersion | None


class ConfirmedFeeVersionStore(Protocol):
    """Persistence operations required by Confirmed Fee service."""

    def create(self, version: ConfirmedFeeVersion) -> ConfirmedFeeVersion:
        """Persist one Confirmed Fee version."""

    def get_latest_by_project(self, project_id: str) -> ConfirmedFeeVersion | None:
        """Return latest Confirmed Fee version for one project."""

    def list_by_project(self, project_id: str) -> tuple[ConfirmedFeeVersion, ...]:
        """Return Confirmed Fee versions for one project ordered ascending."""


class FeeEvaluationPricingDraftLoader(Protocol):
    """Load current saved Fee Evaluation pricing draft status."""

    def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
        """Return the saved pricing draft status for one project."""


class ConfirmedFeeVersionService:
    """Confirm and read versioned Fee Evaluation pricing authority."""

    def __init__(
        self,
        *,
        pricing_draft_loader: FeeEvaluationPricingDraftLoader,
        confirmed_fee_store: ConfirmedFeeVersionStore,
        clock: Callable[[], str] | None = None,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._pricing_draft_loader = pricing_draft_loader
        self._confirmed_fee_store = confirmed_fee_store
        self._clock = clock or _utc_now_iso
        self._id_factory = id_factory or (lambda: uuid4().hex)

    def confirm(self, command: ConfirmFeeVersionCommand) -> ConfirmedFeeVersion:
        """Create a Confirmed Fee version from the current saved pricing draft."""
        confirmed_by = _validate_confirmed_by(command.confirmed_by)
        load_result = self._pricing_draft_loader.load(command.project_id)
        snapshot = _require_current_pricing_snapshot(load_result)
        if snapshot.draft_edit_id != command.expected_pricing_draft_edit_id:
            raise ConfirmedFeePricingDraftChangedError(
                "Fee Evaluation draft changed after totals were prepared. "
                "Reload and confirm again."
            )
        _validate_summary(command.summary)
        versions = self._confirmed_fee_store.list_by_project(command.project_id)
        next_revision = (versions[-1].confirmed_fee_revision + 1) if versions else 1
        version = ConfirmedFeeVersion(
            confirmed_fee_id=self._id_factory(),
            project_id=command.project_id,
            confirmed_fee_revision=next_revision,
            confirmed_matrix_id=snapshot.confirmed_matrix_id,
            confirmed_revision=snapshot.confirmed_revision,
            fee_rule_version_id=snapshot.fee_rule_version_id,
            pricing_draft_edit_id=snapshot.draft_edit_id,
            pricing_effective_from=None,
            summary=command.summary,
            pricing_snapshot_json=edited_values_to_json(snapshot.edited_values),
            confirmed_by=confirmed_by,
            confirmed_at=self._clock(),
            confirmation_note=_normalize_optional_text(command.confirmation_note),
        )
        return self._confirmed_fee_store.create(version)

    def get_latest(self, project_id: str) -> ConfirmedFeeVersionReadResult:
        """Return the latest Confirmed Fee version and current/stale status."""
        load_result = self._pricing_draft_loader.load(project_id)
        latest = self._confirmed_fee_store.get_latest_by_project(project_id)
        if latest is None:
            return ConfirmedFeeVersionReadResult(
                status="missing",
                current_context=load_result.current_context,
                latest_confirmed_fee=None,
            )
        return ConfirmedFeeVersionReadResult(
            status=(
                "current"
                if _version_matches_context(latest, load_result.current_context)
                else "stale"
            ),
            current_context=load_result.current_context,
            latest_confirmed_fee=latest,
        )


def _require_current_pricing_snapshot(
    load_result: FeeEvaluationPricingDraftLoadResult,
):
    if load_result.status == "missing" or load_result.saved_snapshot is None:
        raise ConfirmedFeePricingDraftMissingError(
            "Save Fee Evaluation pricing before confirming fee."
        )
    if load_result.status == "stale":
        raise ConfirmedFeePricingDraftStaleError(
            "Fee Evaluation pricing draft is stale. refresh and save it for the "
            "current Matrix and fee rules before confirming."
        )
    return load_result.saved_snapshot


def _validate_summary(summary: ConfirmedFeeSummary) -> None:
    for field_name in (
        "testing_fee_total",
        "working_hours",
        "lab_manpower_cost",
        "external_cost",
        "grand_cost",
    ):
        value = getattr(summary, field_name)
        if str(value).strip() == "":
            raise ConfirmedFeeSummaryValidationError(f"{field_name} is required.")
        try:
            Decimal(str(value).strip())
        except InvalidOperation as exc:
            raise ConfirmedFeeSummaryValidationError(
                f"{field_name} must be numeric."
            ) from exc


def _validate_confirmed_by(value: str) -> str:
    text = value.strip()
    if not text:
        raise ConfirmedFeeSummaryValidationError("confirmed_by is required.")
    return text


def _version_matches_context(
    version: ConfirmedFeeVersion,
    context: FeeEvaluationPricingDraftContext,
) -> bool:
    return (
        version.project_id == context.project_id
        and version.confirmed_matrix_id == context.confirmed_matrix_id
        and version.confirmed_revision == context.confirmed_revision
        and version.fee_rule_version_id == context.fee_rule_version_id
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
