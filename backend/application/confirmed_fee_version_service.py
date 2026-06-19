"""Create and read Confirmed Fee authority versions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from typing import Callable, Protocol
from uuid import uuid4

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportValues,
)
from backend.application.confirmed_fee_review_markers import AUTO_REBASE_FEE_CONFIRMATION_NOTE
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftContext,
    FeeEvaluationPricingDraftLoadResult,
    FeeEvaluationPricingDraftSnapshot,
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
    fee_review_required_count: int = 0


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
        _validate_summary_matches_saved_pricing_snapshot(command.summary, snapshot)
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
            pricing_snapshot_json=edited_values_to_json(
                _active_only_edited_values(snapshot.edited_values)
            ),
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
        status: ConfirmedFeeStatus = (
            "current"
            if _version_matches_context(latest, load_result.current_context)
            else "stale"
        )
        return ConfirmedFeeVersionReadResult(
            status=status,
            current_context=load_result.current_context,
            latest_confirmed_fee=latest,
            fee_review_required_count=(
                _auto_rebase_fee_review_required_count(latest)
                if status == "current"
                else 0
            ),
        )


def _active_only_edited_values(
    values: FeeEvaluationEditedExportValues,
) -> FeeEvaluationEditedExportValues:
    """Return the confirmable Fee snapshot without hidden recovery rows."""
    return FeeEvaluationEditedExportValues(
        rows=values.rows,
        summary=values.summary,
        manual_rows=values.manual_rows,
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


def _validate_summary_matches_saved_pricing_snapshot(
    summary: ConfirmedFeeSummary,
    snapshot: FeeEvaluationPricingDraftSnapshot,
) -> None:
    expected = _summary_from_saved_pricing_snapshot(snapshot)
    mismatches = [
        field_name
        for field_name in (
            "testing_fee_total",
            "working_hours",
            "lab_manpower_cost",
            "external_cost",
            "grand_cost",
        )
        if _decimal_value(getattr(summary, field_name))
        != _decimal_value(getattr(expected, field_name))
    ]
    if mismatches:
        raise ConfirmedFeePricingDraftChangedError(
            "Fee Evaluation summary does not match the saved pricing draft. "
            "Reload and confirm again."
        )


def _summary_from_saved_pricing_snapshot(
    snapshot: FeeEvaluationPricingDraftSnapshot,
) -> ConfirmedFeeSummary:
    rows = (*snapshot.edited_values.rows, *snapshot.edited_values.manual_rows)
    testing_fee_total = sum((_decimal_value(row.testing_fee) for row in rows), Decimal("0"))
    working_hours = sum((_decimal_value(row.spend_time) for row in rows), Decimal("0"))
    condition_hours = _decimal_value(
        snapshot.edited_values.summary.condition_confirmation_spend_time or "0"
    )
    working_hours += condition_hours
    hourly_rate = _decimal_value(snapshot.edited_values.summary.lab_manpower_hourly_rate)
    lab_manpower_cost = working_hours * hourly_rate
    external_cost = _decimal_value(snapshot.edited_values.summary.external_cost or "0")
    grand_cost = testing_fee_total + external_cost
    return ConfirmedFeeSummary(
        testing_fee_total=_format_decimal(testing_fee_total, Decimal("0.01")),
        working_hours=_format_decimal(working_hours, Decimal("0.1")),
        lab_manpower_cost=_format_decimal(
            lab_manpower_cost,
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        ),
        external_cost=_format_decimal(external_cost, Decimal("0.01")),
        grand_cost=_format_decimal(grand_cost, Decimal("0.01")),
    )


def _auto_rebase_fee_review_required_count(version: ConfirmedFeeVersion) -> int:
    """Return rows that still need operator review after an automatic Matrix Fee rebase."""
    if (version.confirmation_note or "").strip() != AUTO_REBASE_FEE_CONFIRMATION_NOTE:
        return 0
    try:
        payload = json.loads(version.pricing_snapshot_json)
    except (TypeError, json.JSONDecodeError):
        return 0
    if not isinstance(payload, dict):
        return 0
    rows = payload.get("rows")
    manual_rows = payload.get("manual_rows")
    return sum(
        1
        for row in _iter_row_payloads(rows, manual_rows)
        if _row_requires_fee_review(row)
    )


def _iter_row_payloads(*collections: object):
    for collection in collections:
        if not isinstance(collection, list):
            continue
        for item in collection:
            if isinstance(item, dict):
                yield item


def _row_requires_fee_review(row: dict[str, object]) -> bool:
    unit_type = str(row.get("unit_type") or "").strip()
    if unit_type.casefold() == "pending":
        return True
    return (
        _decimal_value_for_review(row.get("unit_price")) == Decimal("0")
        and _decimal_value_for_review(row.get("base_fee")) == Decimal("0")
        and _decimal_value_for_review(row.get("testing_fee")) == Decimal("0")
        and not str(row.get("notes") or "").strip()
    )


def _decimal_value_for_review(value: object) -> Decimal:
    try:
        return _decimal_value(str(value or "0"))
    except ConfirmedFeeSummaryValidationError:
        return Decimal("0")


def _decimal_value(value: str) -> Decimal:
    normalized = str(value).strip().replace("$", "").replace(",", "")
    if not normalized:
        return Decimal("0")
    try:
        return Decimal(normalized)
    except InvalidOperation as exc:
        raise ConfirmedFeeSummaryValidationError(
            "Saved Fee Evaluation pricing draft totals are incomplete."
        ) from exc


def _format_decimal(value: Decimal, quantum: Decimal, *, rounding=None) -> str:
    if rounding is not None:
        return str(value.quantize(quantum, rounding=rounding))
    return str(value.quantize(quantum))


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
