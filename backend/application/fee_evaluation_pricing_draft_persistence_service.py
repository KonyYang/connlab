"""Persist and reload Fee Evaluation pricing draft edits."""

from __future__ import annotations

from dataclasses import dataclass
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
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedManualRow,
    edited_row_lookup,
    validate_supported_manual_rows,
)
from backend.modules.fee_evaluation import load_active_fee_rule_library

FeeEvaluationPricingDraftStatus = Literal["missing", "current", "stale"]


@dataclass(frozen=True, slots=True)
class SaveFeeEvaluationPricingDraftCommand:
    """Input for saving one project's current Fee Evaluation pricing draft."""

    project_id: str
    edited_values: FeeEvaluationEditedExportValues


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


class FeeEvaluationPricingDraftPersistenceService:
    """Save and reload Fee Evaluation pricing draft edits."""

    def __init__(
        self,
        *,
        basic_fill_service: ConfirmedMatrixFeeTemplateBasicFillService,
        draft_store: FeeEvaluationPricingDraftStore,
    ) -> None:
        self._basic_fill_service = basic_fill_service
        self._draft_store = draft_store

    def save(
        self, command: SaveFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftLoadResult:
        """Validate and persist one pricing draft for the current authority context."""
        basic_fill = self._build_basic_fill(command.project_id)
        _validate_edited_values(command.edited_values, basic_fill)
        context = _context_from_basic_fill(basic_fill)
        now = datetime.now(timezone.utc).isoformat()
        existing = self._draft_store.get_latest_by_project(command.project_id)
        draft_edit_id = (
            existing.draft_edit_id
            if existing is not None and _snapshot_matches_context(existing, context)
            else uuid4().hex
        )
        created_at = (
            existing.created_at
            if existing is not None and _snapshot_matches_context(existing, context)
            else now
        )
        snapshot = FeeEvaluationPricingDraftSnapshot(
            draft_edit_id=draft_edit_id,
            project_id=context.project_id,
            confirmed_matrix_id=context.confirmed_matrix_id,
            confirmed_revision=context.confirmed_revision,
            fee_rule_version_id=context.fee_rule_version_id,
            edited_values=command.edited_values,
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
        """Load the latest saved pricing draft and classify it against current context."""
        basic_fill = self._build_basic_fill(project_id)
        context = _context_from_basic_fill(basic_fill)
        snapshot = self._draft_store.get_latest_by_project(project_id)
        if snapshot is None:
            return FeeEvaluationPricingDraftLoadResult(
                status="missing",
                current_context=context,
                saved_snapshot=None,
            )
        return FeeEvaluationPricingDraftLoadResult(
            status="current" if _snapshot_matches_context(snapshot, context) else "stale",
            current_context=context,
            saved_snapshot=snapshot,
        )

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
            }
            for row in values.manual_rows
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
            )
            for row in payload.get("manual_rows", [])
        ),
    )


def _validate_edited_values(
    values: FeeEvaluationEditedExportValues,
    basic_fill: MatrixBasicFillWorkbook,
) -> None:
    edited_row_lookup(values, basic_fill)
    validate_supported_manual_rows(values.manual_rows)


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
