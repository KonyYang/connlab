"""Promote pending Matrix-to-Fee rebase output after Matrix Confirm."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Literal, Protocol
from uuid import uuid4

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    build_basic_fill_from_confirmed_snapshot,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedManualRow,
    edited_row_lookup,
    validate_supported_manual_rows,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftSnapshot,
)
from backend.application.matrix_fee_draft_rebase_service import (
    MatrixFeeDraftRebaseService,
    MatrixFeeRebaseResult,
    MatrixFeeRebaseSummary,
)
from backend.application.matrix_fee_pending_rebase_service import (
    MatrixFeePendingRebaseSnapshot,
    _source_rows_from_basic_fill,
    _target_groups_from_matrix_draft,
    _target_rows_from_matrix_draft,
    pending_rebase_payload_from_json,
)
from backend.domain import ConfirmedMatrixSnapshot, ProjectMatrixDraftSnapshot

MatrixFeeRebasePromotionStatus = Literal[
    "not_required",
    "promoted",
    "fallback_promoted",
    "skipped",
    "failed",
]


@dataclass(frozen=True, slots=True)
class PromoteMatrixFeeRebaseCommand:
    """Input for promoting a Matrix autosave rebase after Matrix Confirm."""

    project_id: str
    saved_matrix_draft: ProjectMatrixDraftSnapshot
    saved_matrix_draft_payload_signature: str
    previous_confirmed_matrix: ConfirmedMatrixSnapshot
    new_confirmed_matrix: ConfirmedMatrixSnapshot
    fee_rule_version_id: str


@dataclass(frozen=True, slots=True)
class MatrixFeeRebasePromotionResult:
    """Non-fatal Matrix Confirm promotion result."""

    status: MatrixFeeRebasePromotionStatus
    summary: MatrixFeeRebaseSummary | None = None
    error: str | None = None


class MatrixFeePendingRebaseReadStore(Protocol):
    """Pending rebase read/delete operations needed by promotion."""

    def get_by_context(
        self,
        *,
        project_matrix_draft_id: str,
        fee_rule_version_id: str,
    ) -> MatrixFeePendingRebaseSnapshot | None:
        """Return pending rebase for one Matrix draft/rule context."""

    def delete_by_matrix_draft(self, project_matrix_draft_id: str) -> int:
        """Delete pending rebase rows for one Matrix draft."""


class FeePricingDraftPromotionStore(Protocol):
    """Pricing draft operations needed by promotion."""

    def get_by_context(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        """Return pricing draft for one exact context."""

    def upsert_current(
        self, snapshot: FeeEvaluationPricingDraftSnapshot
    ) -> FeeEvaluationPricingDraftSnapshot:
        """Create or replace pricing draft for one exact context."""


class MatrixFeeRebasePromotionService:
    """Promote pending or fallback Matrix-to-Fee rebase output."""

    def __init__(
        self,
        *,
        pending_store: MatrixFeePendingRebaseReadStore,
        pricing_draft_store: FeePricingDraftPromotionStore,
        rebase_service: MatrixFeeDraftRebaseService | None = None,
    ) -> None:
        self._pending_store = pending_store
        self._pricing_draft_store = pricing_draft_store
        self._rebase = rebase_service or MatrixFeeDraftRebaseService()

    def promote_after_matrix_confirm(
        self,
        command: PromoteMatrixFeeRebaseCommand,
    ) -> MatrixFeeRebasePromotionResult:
        """Best-effort promotion that never fails Matrix Confirm."""
        try:
            previous_pricing = self._load_previous_pricing(command)
            pending = self._pending_store.get_by_context(
                project_matrix_draft_id=(
                    command.saved_matrix_draft.record.project_matrix_draft_id
                ),
                fee_rule_version_id=command.fee_rule_version_id,
            )
            if _pending_matches_command(pending, command):
                if previous_pricing is None:
                    return MatrixFeeRebasePromotionResult(status="skipped")
                result = pending_rebase_payload_from_json(pending.payload_json)
                edited_values = remap_rebase_result_to_confirmed_matrix(
                    rebase_result=result,
                    previous_pricing_draft=previous_pricing,
                    new_confirmed_matrix=command.new_confirmed_matrix,
                )
                self._save_promoted_draft(command, edited_values)
                self._pending_store.delete_by_matrix_draft(
                    command.saved_matrix_draft.record.project_matrix_draft_id
                )
                return MatrixFeeRebasePromotionResult(
                    status="promoted",
                    summary=result.summary,
                )
            if previous_pricing is None:
                return MatrixFeeRebasePromotionResult(status="skipped")
            result = self._fallback_rebase(command, previous_pricing)
            edited_values = remap_rebase_result_to_confirmed_matrix(
                rebase_result=result,
                previous_pricing_draft=previous_pricing,
                new_confirmed_matrix=command.new_confirmed_matrix,
            )
            self._save_promoted_draft(command, edited_values)
            return MatrixFeeRebasePromotionResult(
                status="fallback_promoted",
                summary=result.summary,
            )
        except Exception as exc:  # noqa: BLE001 - non-fatal Matrix Confirm boundary.
            return MatrixFeeRebasePromotionResult(
                status="failed",
                error=f"Fee rebase promotion failed: {exc}",
            )

    def _load_previous_pricing(
        self,
        command: PromoteMatrixFeeRebaseCommand,
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        previous = command.previous_confirmed_matrix.version
        return self._pricing_draft_store.get_by_context(
            project_id=command.project_id,
            confirmed_matrix_id=previous.confirmed_matrix_id,
            confirmed_revision=previous.confirmed_revision,
            fee_rule_version_id=command.fee_rule_version_id,
        )

    def _fallback_rebase(
        self,
        command: PromoteMatrixFeeRebaseCommand,
        previous_pricing: FeeEvaluationPricingDraftSnapshot,
    ) -> MatrixFeeRebaseResult:
        previous_basic_fill = build_basic_fill_from_confirmed_snapshot(
            command.previous_confirmed_matrix
        )
        return self._rebase.rebase(
            source_rows=_source_rows_from_basic_fill(
                previous_basic_fill.groups,
                source_values=previous_pricing.edited_values,
            ),
            target_rows=_target_rows_from_matrix_draft(command.saved_matrix_draft),
            source_manual_rows=previous_pricing.edited_values.manual_rows,
            target_groups=_target_groups_from_matrix_draft(command.saved_matrix_draft),
        )

    def _save_promoted_draft(
        self,
        command: PromoteMatrixFeeRebaseCommand,
        edited_values: FeeEvaluationEditedExportValues,
    ) -> FeeEvaluationPricingDraftSnapshot:
        new_version = command.new_confirmed_matrix.version
        existing = self._pricing_draft_store.get_by_context(
            project_id=command.project_id,
            confirmed_matrix_id=new_version.confirmed_matrix_id,
            confirmed_revision=new_version.confirmed_revision,
            fee_rule_version_id=command.fee_rule_version_id,
        )
        now = datetime.now(timezone.utc).isoformat()
        snapshot = FeeEvaluationPricingDraftSnapshot(
            draft_edit_id=existing.draft_edit_id if existing else uuid4().hex,
            project_id=command.project_id,
            confirmed_matrix_id=new_version.confirmed_matrix_id,
            confirmed_revision=new_version.confirmed_revision,
            fee_rule_version_id=command.fee_rule_version_id,
            edited_values=edited_values,
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        return self._pricing_draft_store.upsert_current(snapshot)


def remap_rebase_result_to_confirmed_matrix(
    *,
    rebase_result: MatrixFeeRebaseResult,
    previous_pricing_draft: FeeEvaluationPricingDraftSnapshot | None,
    new_confirmed_matrix: ConfirmedMatrixSnapshot,
) -> FeeEvaluationEditedExportValues:
    """Project rebased rows onto the new Confirmed Matrix basic-fill identity."""
    basic_fill = build_basic_fill_from_confirmed_snapshot(new_confirmed_matrix)
    line_by_draft_identity = _index_new_basic_fill_by_draft_identity(
        new_confirmed_matrix
    )
    rows = tuple(
        _remap_row(row, line_by_draft_identity)
        for row in rebase_result.active_rows
    )
    manual_rows = tuple(
        _remap_manual_row(row, new_confirmed_matrix) for row in rebase_result.manual_rows
    )
    values = FeeEvaluationEditedExportValues(
        rows=rows,
        summary=(
            previous_pricing_draft.edited_values.summary
            if previous_pricing_draft is not None
            else _blank_summary()
        ),
        manual_rows=manual_rows,
    )
    edited_row_lookup(values, basic_fill)
    validate_supported_manual_rows(values.manual_rows, basic_fill)
    return values


def _pending_matches_command(
    pending: MatrixFeePendingRebaseSnapshot | None,
    command: PromoteMatrixFeeRebaseCommand,
) -> bool:
    if pending is None:
        return False
    previous = command.previous_confirmed_matrix.version
    return (
        pending.project_id == command.project_id
        and pending.project_matrix_draft_id
        == command.saved_matrix_draft.record.project_matrix_draft_id
        and pending.base_confirmed_matrix_id == previous.confirmed_matrix_id
        and pending.base_confirmed_revision == previous.confirmed_revision
        and pending.fee_rule_version_id == command.fee_rule_version_id
        and pending.matrix_draft_payload_signature
        == command.saved_matrix_draft_payload_signature
    )


def _index_new_basic_fill_by_draft_identity(
    snapshot: ConfirmedMatrixSnapshot,
) -> dict[tuple[str, str, str, int], FeeEvaluationEditedExportRow]:
    group_draft_by_confirmed = {
        group.confirmed_group_id: group.draft_group_id for group in snapshot.groups
    }
    row_draft_by_confirmed = {
        row.confirmed_row_id: row.draft_row_id for row in snapshot.rows
    }
    basic_fill = build_basic_fill_from_confirmed_snapshot(snapshot)
    lookup: dict[tuple[str, str, str, int], FeeEvaluationEditedExportRow] = {}
    for group in basic_fill.groups:
        draft_group_id = group_draft_by_confirmed.get(group.confirmed_group_id, "")
        for line in group.lines:
            draft_row_id = row_draft_by_confirmed.get(line.confirmed_row_id, "")
            step_token = line.step_tokens[0] if line.step_tokens else ""
            lookup[(draft_group_id, draft_row_id, step_token, line.step_index)] = (
                FeeEvaluationEditedExportRow(
                    source_line_id=line.line_id,
                    confirmed_group_id=line.confirmed_group_id,
        confirmed_row_id=line.confirmed_row_id,
        step_token=step_token,
        step_index=line.step_index,
        spend_time="0",
        unit_price="0",
        unit_type="Pending",
        units="1",
        base_fee="0",
        discount="0%",
        testing_fee="0",
        notes="",
    )
            )
    return lookup


def _remap_row(
    row: FeeEvaluationEditedExportRow,
    line_by_draft_identity: dict[tuple[str, str, str, int], FeeEvaluationEditedExportRow],
) -> FeeEvaluationEditedExportRow:
    identity = (
        row.confirmed_group_id,
        row.confirmed_row_id,
        row.step_token,
        row.step_index,
    )
    target = line_by_draft_identity.get(identity)
    if target is None:
        raise ValueError("Rebased Fee row identity was not found in new Confirmed Matrix.")
    return replace(
        target,
        spend_time=row.spend_time,
        unit_price=row.unit_price,
        unit_type=_saveable_unit_type(row.unit_type),
        units=row.units,
        base_fee=row.base_fee,
        discount=row.discount,
        testing_fee=row.testing_fee,
        notes=row.notes,
    )


def _remap_manual_row(
    row: FeeEvaluationEditedManualRow,
    snapshot: ConfirmedMatrixSnapshot,
) -> FeeEvaluationEditedManualRow:
    if row.row_kind.strip() != "sample_preparation":
        return row
    target = _find_group_for_manual_row(row, snapshot)
    if target is None:
        return row
    return replace(
        row,
        confirmed_group_id=target.confirmed_group_id,
        group_key=target.group_key,
        group_label=target.group_label,
    )


def _find_group_for_manual_row(
    row: FeeEvaluationEditedManualRow,
    snapshot: ConfirmedMatrixSnapshot,
):
    by_draft = {group.draft_group_id.strip(): group for group in snapshot.groups}
    draft_id = row.confirmed_group_id.strip()
    if draft_id in by_draft:
        return by_draft[draft_id]
    row_key = row.group_key.strip().casefold()
    row_label = row.group_label.strip().casefold()
    for group in snapshot.groups:
        if row_key and group.group_key.strip().casefold() == row_key:
            return group
        if row_label and group.group_label.strip().casefold() == row_label:
            return group
    return None


def _saveable_unit_type(value: str) -> str:
    normalized = value.strip()
    return normalized if normalized else "Pending"


def _blank_summary() -> FeeEvaluationEditedExportSummary:
    return FeeEvaluationEditedExportSummary(
        condition_confirmation_spend_time="",
        external_cost="",
        external_cost_note="",
        lab_manpower_hourly_rate="",
    )
