"""Persist and reload Fee Evaluation pricing draft edits."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
from typing import Literal, Protocol
from uuid import uuid4

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    BuildMatrixBasicFeeTemplateCommand,
    ConfirmedMatrixFeeTemplateBasicFillService,
    MatrixBasicFillWorkbook,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedInactiveRow,
    FeeEvaluationEditedInactiveRowKey,
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedManualRow,
    edited_row_lookup,
    validate_supported_manual_rows,
)
from backend.application.project_lifecycle_write_guard import (
    LifecycleWriteOperation,
    ProjectLifecycleWriteGuard,
)
from backend.modules.fee_evaluation import load_active_fee_rule_library

FeeEvaluationPricingDraftStatus = Literal["missing", "current", "stale"]


@dataclass(frozen=True, slots=True)
class SaveFeeEvaluationPricingDraftCommand:
    """Input for saving one project's current Fee Evaluation pricing draft."""

    project_id: str
    edited_values: FeeEvaluationEditedExportValues
    expected_confirmed_matrix_id: str | None = None
    expected_confirmed_revision: int | None = None
    expected_fee_rule_version_id: str | None = None


@dataclass(frozen=True, slots=True)
class DiscardFeeEvaluationPricingDraftCommand:
    """Input for discarding one project's current Fee Evaluation pricing draft."""

    project_id: str
    expected_pricing_draft_edit_id: str | None = None
    expected_confirmed_matrix_id: str | None = None
    expected_confirmed_revision: int | None = None
    expected_fee_rule_version_id: str | None = None


@dataclass(frozen=True, slots=True)
class FeeEvaluationPricingDraftContext:
    """Current authority context used to bind a saved pricing draft."""

    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    fee_rule_version_id: str


@dataclass(frozen=True, slots=True)
class FeeEvaluationPricingDraftSnapshot:
    """Persisted Fee Evaluation pricing draft edit payload."""

    draft_edit_id: str
    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    fee_rule_version_id: str
    edited_values: FeeEvaluationEditedExportValues
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class FeeEvaluationPricingDraftLoadResult:
    """Load result for the current project's saved pricing draft."""

    status: FeeEvaluationPricingDraftStatus
    current_context: FeeEvaluationPricingDraftContext
    saved_snapshot: FeeEvaluationPricingDraftSnapshot | None


@dataclass(frozen=True, slots=True)
class FeeEvaluationPricingDraftDiscardResult:
    """Discard result for the current project's saved pricing draft."""

    discarded: bool
    current_context: FeeEvaluationPricingDraftContext


class FeeEvaluationPricingDraftConflictError(ValueError):
    """Raised when pricing draft optimistic context tokens do not match."""


class FeeEvaluationPricingDraftStore(Protocol):
    """Persistence operations required by the pricing draft service."""

    def upsert_current(
        self, snapshot: FeeEvaluationPricingDraftSnapshot
    ) -> FeeEvaluationPricingDraftSnapshot:
        """Create or replace the current draft for one authority/rule tuple."""

    def get_latest_by_project(
        self, project_id: str
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        """Return the latest saved draft for one project, if any."""

    def get_by_context(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        """Return the saved draft for an exact project/Matrix/rule context."""

    def delete_current(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> bool:
        """Delete the saved draft for an exact project/Matrix/rule context."""


class FeeEvaluationPricingDraftPersistenceService:
    """Save and reload Fee Evaluation pricing draft edits."""

    def __init__(
        self,
        *,
        basic_fill_service: ConfirmedMatrixFeeTemplateBasicFillService,
        draft_store: FeeEvaluationPricingDraftStore,
        lifecycle_write_guard: ProjectLifecycleWriteGuard | None = None,
    ) -> None:
        self._basic_fill_service = basic_fill_service
        self._draft_store = draft_store
        self._lifecycle_write_guard = lifecycle_write_guard

    def save(
        self, command: SaveFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftLoadResult:
        """Validate and persist one pricing draft for the current authority context."""
        self._require_write_allowed(
            command.project_id,
            LifecycleWriteOperation.FEE_PRICING_DRAFT_SAVE,
        )
        basic_fill = self._build_basic_fill(command.project_id)
        _validate_edited_values(command.edited_values, basic_fill)
        context = _context_from_basic_fill(basic_fill)
        _validate_save_expectations(command, context)
        now = datetime.now(timezone.utc).isoformat()
        existing = self._draft_store.get_by_context(
            project_id=context.project_id,
            confirmed_matrix_id=context.confirmed_matrix_id,
            confirmed_revision=context.confirmed_revision,
            fee_rule_version_id=context.fee_rule_version_id,
        )
        draft_edit_id = existing.draft_edit_id if existing is not None else uuid4().hex
        created_at = existing.created_at if existing is not None else now
        edited_values = _merge_existing_inactive_rows(
            incoming=command.edited_values,
            existing=existing.edited_values if existing is not None else None,
        )
        snapshot = FeeEvaluationPricingDraftSnapshot(
            draft_edit_id=draft_edit_id,
            project_id=context.project_id,
            confirmed_matrix_id=context.confirmed_matrix_id,
            confirmed_revision=context.confirmed_revision,
            fee_rule_version_id=context.fee_rule_version_id,
            edited_values=edited_values,
            created_at=created_at,
            updated_at=now,
        )
        saved = self._draft_store.upsert_current(snapshot)
        return FeeEvaluationPricingDraftLoadResult(
            status="current",
            current_context=context,
            saved_snapshot=saved,
        )

    def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
        """Load the saved pricing draft for the current authority context."""
        basic_fill = self._build_basic_fill(project_id)
        context = _context_from_basic_fill(basic_fill)
        snapshot = self._draft_store.get_by_context(
            project_id=context.project_id,
            confirmed_matrix_id=context.confirmed_matrix_id,
            confirmed_revision=context.confirmed_revision,
            fee_rule_version_id=context.fee_rule_version_id,
        )
        if snapshot is None:
            return FeeEvaluationPricingDraftLoadResult(
                status="missing",
                current_context=context,
                saved_snapshot=None,
            )
        return FeeEvaluationPricingDraftLoadResult(
            status="current",
            current_context=context,
            saved_snapshot=snapshot,
        )

    def discard(
        self, command: DiscardFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftDiscardResult:
        """Discard the saved pricing draft for the current authority context."""
        self._require_write_allowed(
            command.project_id,
            LifecycleWriteOperation.FEE_PRICING_DRAFT_DISCARD,
        )
        basic_fill = self._build_basic_fill(command.project_id)
        context = _context_from_basic_fill(basic_fill)
        snapshot = self._draft_store.get_by_context(
            project_id=context.project_id,
            confirmed_matrix_id=context.confirmed_matrix_id,
            confirmed_revision=context.confirmed_revision,
            fee_rule_version_id=context.fee_rule_version_id,
        )
        if snapshot is None:
            return FeeEvaluationPricingDraftDiscardResult(
                discarded=False,
                current_context=context,
            )
        _validate_discard_expectations(command, snapshot, context)
        discarded = self._draft_store.delete_current(
            project_id=context.project_id,
            confirmed_matrix_id=context.confirmed_matrix_id,
            confirmed_revision=context.confirmed_revision,
            fee_rule_version_id=context.fee_rule_version_id,
        )
        return FeeEvaluationPricingDraftDiscardResult(
            discarded=discarded,
            current_context=context,
        )

    def _require_write_allowed(
        self,
        project_id: str,
        operation: LifecycleWriteOperation,
    ) -> None:
        if self._lifecycle_write_guard is not None:
            self._lifecycle_write_guard.require_write_allowed(project_id, operation)

    def _build_basic_fill(self, project_id: str) -> MatrixBasicFillWorkbook:
        """Build current backend Matrix basic-fill rows for validation/context."""
        return self._basic_fill_service.build(
            BuildMatrixBasicFeeTemplateCommand(project_id=project_id)
        )


def edited_values_to_json(values: FeeEvaluationEditedExportValues) -> str:
    """Serialize edited values to a stable JSON payload."""
    payload = {
        "rows": [
            {
                "source_line_id": row.source_line_id,
                "confirmed_group_id": row.confirmed_group_id,
                "confirmed_row_id": row.confirmed_row_id,
                "step_token": row.step_token,
                "step_index": row.step_index,
                "spend_time": row.spend_time,
                "unit_price": row.unit_price,
                "unit_type": row.unit_type,
                "units": row.units,
                "base_fee": row.base_fee,
                "discount": row.discount,
                "testing_fee": row.testing_fee,
                "notes": row.notes,
            }
            for row in values.rows
        ],
        "summary": {
            "condition_confirmation_spend_time": (
                values.summary.condition_confirmation_spend_time
            ),
            "external_cost": values.summary.external_cost,
            "external_cost_note": values.summary.external_cost_note,
            "lab_manpower_hourly_rate": values.summary.lab_manpower_hourly_rate,
        },
        "manual_rows": [
            {
                "row_kind": row.row_kind,
                "spend_time": row.spend_time,
                "unit_price": row.unit_price,
                "unit_type": row.unit_type,
                "units": row.units,
                "base_fee": row.base_fee,
                "discount": row.discount,
                "testing_fee": row.testing_fee,
                "notes": row.notes,
                "confirmed_group_id": row.confirmed_group_id,
                "group_key": row.group_key,
                "group_label": row.group_label,
            }
            for row in values.manual_rows
        ],
        "inactive_rows": [
            {
                "previous_row": _row_to_dict(row.previous_row),
                "rebase_key": {
                    "group_identity": row.rebase_key.group_identity,
                    "row_identity": row.rebase_key.row_identity,
                    "step_token": row.rebase_key.step_token,
                    "step_index": row.rebase_key.step_index,
                },
                "group_key": row.group_key,
                "group_label": row.group_label,
                "group_signature": row.group_signature,
                "inactive_reason": row.inactive_reason,
            }
            for row in values.inactive_rows
        ],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def edited_values_from_json(payload_json: str) -> FeeEvaluationEditedExportValues:
    """Deserialize a saved JSON payload into application edited values."""
    payload = json.loads(payload_json)
    summary = payload["summary"]
    return FeeEvaluationEditedExportValues(
        rows=tuple(
            FeeEvaluationEditedExportRow(
                source_line_id=str(row["source_line_id"]),
                confirmed_group_id=str(row["confirmed_group_id"]),
                confirmed_row_id=str(row["confirmed_row_id"]),
                step_token=str(row.get("step_token", "")),
                step_index=int(row["step_index"]),
                spend_time=str(row["spend_time"]),
                unit_price=str(row["unit_price"]),
                unit_type=str(row["unit_type"]),
                units=str(row["units"]),
                base_fee=str(row["base_fee"]),
                discount=str(row["discount"]),
                testing_fee=str(row["testing_fee"]),
                notes=str(row.get("notes", "")),
            )
            for row in payload.get("rows", [])
        ),
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time=str(
                summary["condition_confirmation_spend_time"]
            ),
            external_cost=str(summary["external_cost"]),
            external_cost_note=str(summary.get("external_cost_note", "")),
            lab_manpower_hourly_rate=str(summary["lab_manpower_hourly_rate"]),
        ),
        manual_rows=tuple(
            FeeEvaluationEditedManualRow(
                row_kind=str(row["row_kind"]),
                spend_time=str(row["spend_time"]),
                unit_price=str(row["unit_price"]),
                unit_type=str(row["unit_type"]),
                units=str(row["units"]),
                base_fee=str(row["base_fee"]),
                discount=str(row["discount"]),
                testing_fee=str(row["testing_fee"]),
                notes=str(row.get("notes", "")),
                confirmed_group_id=str(row.get("confirmed_group_id", "")),
                group_key=str(row.get("group_key", "")),
                group_label=str(row.get("group_label", "")),
            )
            for row in payload.get("manual_rows", [])
        ),
        inactive_rows=tuple(
            _inactive_row_from_dict(row)
            for row in payload.get("inactive_rows", [])
        ),
    )


def _row_to_dict(row: FeeEvaluationEditedExportRow) -> dict[str, object]:
    """Serialize one edited active or inactive Fee row."""
    return {
        "source_line_id": row.source_line_id,
        "confirmed_group_id": row.confirmed_group_id,
        "confirmed_row_id": row.confirmed_row_id,
        "step_token": row.step_token,
        "step_index": row.step_index,
        "spend_time": row.spend_time,
        "unit_price": row.unit_price,
        "unit_type": row.unit_type,
        "units": row.units,
        "base_fee": row.base_fee,
        "discount": row.discount,
        "testing_fee": row.testing_fee,
        "notes": row.notes,
    }


def _inactive_row_from_dict(payload: dict[str, object]) -> FeeEvaluationEditedInactiveRow:
    """Deserialize one hidden inactive Fee row."""
    previous = payload.get("previous_row")
    key = payload.get("rebase_key") or payload.get("key")
    if not isinstance(previous, dict):
        previous = {}
    if not isinstance(key, dict):
        key = {}
    return FeeEvaluationEditedInactiveRow(
        previous_row=FeeEvaluationEditedExportRow(
            source_line_id=str(previous.get("source_line_id", "")),
            confirmed_group_id=str(previous.get("confirmed_group_id", "")),
            confirmed_row_id=str(previous.get("confirmed_row_id", "")),
            step_token=str(previous.get("step_token", "")),
            step_index=int(previous.get("step_index", 0)),
            spend_time=str(previous.get("spend_time", "")),
            unit_price=str(previous.get("unit_price", "")),
            unit_type=str(previous.get("unit_type", "")),
            units=str(previous.get("units", "")),
            base_fee=str(previous.get("base_fee", "")),
            discount=str(previous.get("discount", "")),
            testing_fee=str(previous.get("testing_fee", "")),
            notes=str(previous.get("notes", "")),
        ),
        rebase_key=FeeEvaluationEditedInactiveRowKey(
            group_identity=str(key.get("group_identity", "")),
            row_identity=str(key.get("row_identity", "")),
            step_token=str(key.get("step_token", "")),
            step_index=int(key.get("step_index", 0)),
        ),
        group_key=str(payload.get("group_key", "")),
        group_label=str(payload.get("group_label", "")),
        group_signature=str(payload.get("group_signature", "")),
        inactive_reason=str(payload.get("inactive_reason", "removed_from_matrix")),
    )


def _validate_edited_values(
    values: FeeEvaluationEditedExportValues,
    basic_fill: MatrixBasicFillWorkbook,
) -> None:
    edited_row_lookup(values, basic_fill)
    validate_supported_manual_rows(values.manual_rows, basic_fill)


def _merge_existing_inactive_rows(
    *,
    incoming: FeeEvaluationEditedExportValues,
    existing: FeeEvaluationEditedExportValues | None,
) -> FeeEvaluationEditedExportValues:
    """Preserve server-side hidden rows when clients save active Fee rows only."""
    if incoming.inactive_rows or existing is None or not existing.inactive_rows:
        return incoming
    return replace(incoming, inactive_rows=existing.inactive_rows)


def _context_from_basic_fill(
    basic_fill: MatrixBasicFillWorkbook,
) -> FeeEvaluationPricingDraftContext:
    library = load_active_fee_rule_library()
    return FeeEvaluationPricingDraftContext(
        project_id=basic_fill.header.project_id,
        confirmed_matrix_id=basic_fill.header.confirmed_matrix_id,
        confirmed_revision=basic_fill.header.confirmed_revision,
        fee_rule_version_id=library.version.version_id,
    )


def _snapshot_matches_context(
    snapshot: FeeEvaluationPricingDraftSnapshot,
    context: FeeEvaluationPricingDraftContext,
) -> bool:
    return (
        snapshot.project_id == context.project_id
        and snapshot.confirmed_matrix_id == context.confirmed_matrix_id
        and snapshot.confirmed_revision == context.confirmed_revision
        and snapshot.fee_rule_version_id == context.fee_rule_version_id
    )


def _validate_discard_expectations(
    command: DiscardFeeEvaluationPricingDraftCommand,
    snapshot: FeeEvaluationPricingDraftSnapshot,
    context: FeeEvaluationPricingDraftContext,
) -> None:
    """Validate optimistic discard tokens against the current saved draft."""
    if (
        command.expected_pricing_draft_edit_id
        and command.expected_pricing_draft_edit_id != snapshot.draft_edit_id
    ):
        raise FeeEvaluationPricingDraftConflictError(
            "Pricing draft changed before discard. Reload Fee Evaluation."
        )
    if (
        command.expected_confirmed_matrix_id
        and command.expected_confirmed_matrix_id != context.confirmed_matrix_id
    ):
        raise FeeEvaluationPricingDraftConflictError(
            "Pricing draft Matrix context changed before discard."
        )
    if (
        command.expected_confirmed_revision is not None
        and command.expected_confirmed_revision != context.confirmed_revision
    ):
        raise FeeEvaluationPricingDraftConflictError(
            "Pricing draft Matrix revision changed before discard."
        )
    if (
        command.expected_fee_rule_version_id
        and command.expected_fee_rule_version_id != context.fee_rule_version_id
    ):
        raise FeeEvaluationPricingDraftConflictError(
            "Pricing draft fee rule version changed before discard."
        )


def _validate_save_expectations(
    command: SaveFeeEvaluationPricingDraftCommand,
    context: FeeEvaluationPricingDraftContext,
) -> None:
    """Validate optimistic save tokens before writing the current draft."""
    if (
        command.expected_confirmed_matrix_id
        and command.expected_confirmed_matrix_id != context.confirmed_matrix_id
    ):
        raise FeeEvaluationPricingDraftConflictError(
            "Pricing draft Matrix context changed before save."
        )
    if (
        command.expected_confirmed_revision is not None
        and command.expected_confirmed_revision != context.confirmed_revision
    ):
        raise FeeEvaluationPricingDraftConflictError(
            "Pricing draft Matrix revision changed before save."
        )
    if (
        command.expected_fee_rule_version_id
        and command.expected_fee_rule_version_id != context.fee_rule_version_id
    ):
        raise FeeEvaluationPricingDraftConflictError(
            "Pricing draft fee rule version changed before save."
        )
