"""Promote pending Matrix-to-Fee rebase output after Matrix Confirm."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Literal, Protocol
from uuid import uuid4

from backend.application.confirmed_matrix_fee_draft_service import (
    BuildConfirmedMatrixFeeDraftCommand,
    ConfirmedMatrixFeeDraftService,
    FeeEvaluationDraft,
    FeeEvaluationGroup,
    FeeEvaluationLineItem,
)
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    build_basic_fill_from_confirmed_snapshot,
)
from backend.application.confirmed_fee_review_markers import AUTO_REBASE_FEE_CONFIRMATION_NOTE
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedInactiveRow,
    FeeEvaluationEditedInactiveRowKey,
    FeeEvaluationEditedManualRow,
    edited_row_lookup,
    validate_supported_manual_rows,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftSnapshot,
    edited_values_to_json,
)
from backend.application.matrix_fee_draft_rebase_service import (
    MatrixFeeDraftRebaseService,
    MatrixFeeInactiveRemovedRow,
    MatrixFeeRebaseResult,
    MatrixFeeRebaseSummary,
)
from backend.application.matrix_fee_pending_rebase_service import (
    MatrixFeePendingRebaseSnapshot,
    _filter_hard_deleted_inactive_rows,
    _source_rows_from_basic_fill,
    _structural_rebase_keys_from_matrix_draft,
    _target_groups_from_matrix_draft,
    _target_rows_from_matrix_draft,
    pending_rebase_payload_from_json,
)
from backend.domain import ConfirmedMatrixSnapshot, ProjectMatrixDraftSnapshot
from backend.domain.confirmed_fee import ConfirmedFeeSummary, ConfirmedFeeVersion

MatrixFeeRebasePromotionStatus = Literal[
    "not_required",
    "promoted",
    "fallback_promoted",
    "default_promoted",
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


class ConfirmedFeePromotionStore(Protocol):
    """Confirmed Fee authority operations needed by Matrix Confirm promotion."""

    def create(self, version: ConfirmedFeeVersion) -> ConfirmedFeeVersion:
        """Persist one Confirmed Fee authority version."""

    def get_latest_by_project(self, project_id: str) -> ConfirmedFeeVersion | None:
        """Return latest Confirmed Fee version for one project."""

    def list_by_project(self, project_id: str) -> tuple[ConfirmedFeeVersion, ...]:
        """Return Confirmed Fee versions for one project ordered ascending."""


class MatrixFeeRebasePromotionService:
    """Promote pending or fallback Matrix-to-Fee rebase output."""

    def __init__(
        self,
        *,
        pending_store: MatrixFeePendingRebaseReadStore,
        pricing_draft_store: FeePricingDraftPromotionStore,
        confirmed_fee_store: ConfirmedFeePromotionStore | None = None,
        rebase_service: MatrixFeeDraftRebaseService | None = None,
    ) -> None:
        self._pending_store = pending_store
        self._pricing_draft_store = pricing_draft_store
        self._confirmed_fee_store = confirmed_fee_store
        self._rebase = rebase_service or MatrixFeeDraftRebaseService()

    def initialize_after_first_matrix_confirm(
        self,
        *,
        project_id: str,
        new_confirmed_matrix: ConfirmedMatrixSnapshot,
        fee_rule_version_id: str,
    ) -> MatrixFeeRebasePromotionResult:
        """Create the default Matrix-bound Fee draft and authority after first confirm."""
        try:
            snapshot = self._save_default_draft(
                project_id=project_id,
                new_confirmed_matrix=new_confirmed_matrix,
                fee_rule_version_id=fee_rule_version_id,
            )
            self._confirm_default_fee(project_id=project_id, snapshot=snapshot)
            return MatrixFeeRebasePromotionResult(status="default_promoted")
        except Exception as exc:  # noqa: BLE001 - non-fatal Matrix Confirm boundary.
            return MatrixFeeRebasePromotionResult(
                status="failed",
                error=f"Fee default promotion failed: {exc}",
            )

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
                    snapshot = self._save_default_draft(
                        project_id=command.project_id,
                        new_confirmed_matrix=command.new_confirmed_matrix,
                        fee_rule_version_id=command.fee_rule_version_id,
                    )
                    self._confirm_default_fee(
                        project_id=command.project_id,
                        snapshot=snapshot,
                    )
                    return MatrixFeeRebasePromotionResult(status="default_promoted")
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
                new_version = command.new_confirmed_matrix.version
                snapshot = self._pricing_draft_store.get_by_context(
                    project_id=command.project_id,
                    confirmed_matrix_id=new_version.confirmed_matrix_id,
                    confirmed_revision=new_version.confirmed_revision,
                    fee_rule_version_id=command.fee_rule_version_id,
                )
                if snapshot is not None:
                    self._confirm_default_fee(
                        project_id=command.project_id,
                        snapshot=snapshot,
                    )
                return MatrixFeeRebasePromotionResult(
                    status="promoted",
                    summary=result.summary,
                )
            if previous_pricing is None:
                snapshot = self._save_default_draft(
                    project_id=command.project_id,
                    new_confirmed_matrix=command.new_confirmed_matrix,
                    fee_rule_version_id=command.fee_rule_version_id,
                )
                self._confirm_default_fee(project_id=command.project_id, snapshot=snapshot)
                return MatrixFeeRebasePromotionResult(status="default_promoted")
            result = self._fallback_rebase(command, previous_pricing)
            edited_values = remap_rebase_result_to_confirmed_matrix(
                rebase_result=result,
                previous_pricing_draft=previous_pricing,
                new_confirmed_matrix=command.new_confirmed_matrix,
            )
            snapshot = self._save_promoted_draft(command, edited_values)
            self._confirm_default_fee(project_id=command.project_id, snapshot=snapshot)
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
        structural_keys = _structural_rebase_keys_from_matrix_draft(
            command.saved_matrix_draft
        )
        result = self._rebase.rebase(
            source_rows=_source_rows_from_basic_fill(
                previous_basic_fill.groups,
                source_values=previous_pricing.edited_values,
                structural_keys=structural_keys,
            ),
            target_rows=_target_rows_from_matrix_draft(command.saved_matrix_draft),
            source_manual_rows=previous_pricing.edited_values.manual_rows,
            target_groups=_target_groups_from_matrix_draft(command.saved_matrix_draft),
        )
        return _filter_hard_deleted_inactive_rows(
            result,
            structural_keys=structural_keys,
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

    def _save_default_draft(
        self,
        *,
        project_id: str,
        new_confirmed_matrix: ConfirmedMatrixSnapshot,
        fee_rule_version_id: str,
    ) -> FeeEvaluationPricingDraftSnapshot:
        existing = self._pricing_draft_store.get_by_context(
            project_id=project_id,
            confirmed_matrix_id=new_confirmed_matrix.version.confirmed_matrix_id,
            confirmed_revision=new_confirmed_matrix.version.confirmed_revision,
            fee_rule_version_id=fee_rule_version_id,
        )
        now = datetime.now(timezone.utc).isoformat()
        draft = ConfirmedMatrixFeeDraftService(
            confirmed_store=_SingleConfirmedMatrixStore(new_confirmed_matrix)
        ).build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id=project_id))
        snapshot = FeeEvaluationPricingDraftSnapshot(
            draft_edit_id=existing.draft_edit_id if existing else uuid4().hex,
            project_id=project_id,
            confirmed_matrix_id=new_confirmed_matrix.version.confirmed_matrix_id,
            confirmed_revision=new_confirmed_matrix.version.confirmed_revision,
            fee_rule_version_id=fee_rule_version_id,
            edited_values=_edited_values_from_fee_draft(draft),
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        return self._pricing_draft_store.upsert_current(snapshot)

    def _confirm_default_fee(
        self,
        *,
        project_id: str,
        snapshot: FeeEvaluationPricingDraftSnapshot,
    ) -> ConfirmedFeeVersion | None:
        if self._confirmed_fee_store is None:
            return None
        latest = self._confirmed_fee_store.get_latest_by_project(project_id)
        if latest is not None and _confirmed_fee_matches_snapshot(latest, snapshot):
            return latest
        versions = self._confirmed_fee_store.list_by_project(project_id)
        next_revision = (versions[-1].confirmed_fee_revision + 1) if versions else 1
        version = ConfirmedFeeVersion(
            confirmed_fee_id=uuid4().hex,
            project_id=project_id,
            confirmed_fee_revision=next_revision,
            confirmed_matrix_id=snapshot.confirmed_matrix_id,
            confirmed_revision=snapshot.confirmed_revision,
            fee_rule_version_id=snapshot.fee_rule_version_id,
            pricing_draft_edit_id=snapshot.draft_edit_id,
            pricing_effective_from=None,
            summary=_summary_from_edited_values(snapshot.edited_values),
            pricing_snapshot_json=edited_values_to_json(
                _active_only_edited_values(snapshot.edited_values)
            ),
            confirmed_by="ConnLab Auto",
            confirmed_at=datetime.now(timezone.utc).isoformat(),
            confirmation_note=AUTO_REBASE_FEE_CONFIRMATION_NOTE,
        )
        return self._confirmed_fee_store.create(version)


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
        inactive_rows=tuple(
            _inactive_row_from_removed(row)
            for row in rebase_result.inactive_removed_rows
        ),
    )
    edited_row_lookup(values, basic_fill)
    validate_supported_manual_rows(values.manual_rows, basic_fill)
    return values


def _inactive_row_from_removed(
    row: MatrixFeeInactiveRemovedRow,
) -> FeeEvaluationEditedInactiveRow:
    """Convert one removed rebase row to hidden Fee draft recovery data."""
    return FeeEvaluationEditedInactiveRow(
        previous_row=row.previous_row,
        rebase_key=FeeEvaluationEditedInactiveRowKey(
            group_identity=row.rebase_key.group_identity,
            row_identity=row.rebase_key.row_identity,
            step_token=row.rebase_key.step_token,
            step_index=row.rebase_key.step_index,
        ),
        group_key=row.previous_group_key,
        group_label=row.previous_group_label,
        group_signature=row.previous_row_signature,
        inactive_reason=row.inactive_reason,
    )


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


class _SingleConfirmedMatrixStore:
    """Tiny adapter so the existing Fee Draft service can build from a fresh snapshot."""

    def __init__(self, snapshot: ConfirmedMatrixSnapshot) -> None:
        self._snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        if self._snapshot.version.project_id != project_id:
            return None
        return self._snapshot


def _edited_values_from_fee_draft(
    draft: FeeEvaluationDraft,
) -> FeeEvaluationEditedExportValues:
    rows = tuple(
        row
        for group in draft.groups
        for line in group.line_items
        for row in _rows_from_fee_line(line)
    )
    manual_rows = tuple(
        _sample_preparation_row(group)
        for group in draft.groups
        if group.line_items
    ) + (_report_preparation_row(),)
    return FeeEvaluationEditedExportValues(
        rows=rows,
        summary=_blank_summary(),
        manual_rows=manual_rows,
    )


def _rows_from_fee_line(
    line: FeeEvaluationLineItem,
) -> tuple[FeeEvaluationEditedExportRow, ...]:
    return tuple(
        FeeEvaluationEditedExportRow(
            source_line_id=f"{line.line_id}:{step_token}:{index}",
            confirmed_group_id=line.confirmed_group_id,
            confirmed_row_id=line.confirmed_row_id,
            step_token=step_token,
            step_index=index,
            spend_time=_text_or_zero(line.spend_time),
            unit_price=_decimal_text(line.unit_price, "0"),
            unit_type=line.unit_label or line.calculation_strategy or "Pending",
            units=_decimal_text(line.units, "1"),
            base_fee=_decimal_text(line.base_fee, "0"),
            discount=f"{_decimal_text(line.discount_percent, '0')}%",
            testing_fee=_decimal_text(line.testing_fee, "0"),
            notes="",
        )
        for index, step_token in enumerate(line.step_tokens)
    )


def _sample_preparation_row(group: FeeEvaluationGroup) -> FeeEvaluationEditedManualRow:
    first_line = group.line_items[0]
    return FeeEvaluationEditedManualRow(
        row_kind="sample_preparation",
        confirmed_group_id=first_line.confirmed_group_id,
        group_key=group.group_key,
        group_label=group.group_label,
        spend_time="0",
        unit_price="0",
        unit_type="per sample",
        units="1",
        base_fee="0",
        discount="0%",
        testing_fee="0",
        notes="",
    )


def _report_preparation_row() -> FeeEvaluationEditedManualRow:
    return FeeEvaluationEditedManualRow(
        row_kind="report_preparation",
        spend_time="0",
        unit_price="0",
        unit_type="per report",
        units="1",
        base_fee="0",
        discount="0%",
        testing_fee="0",
        notes="",
    )


def _confirmed_fee_matches_snapshot(
    version: ConfirmedFeeVersion,
    snapshot: FeeEvaluationPricingDraftSnapshot,
) -> bool:
    return (
        version.project_id == snapshot.project_id
        and version.confirmed_matrix_id == snapshot.confirmed_matrix_id
        and version.confirmed_revision == snapshot.confirmed_revision
        and version.fee_rule_version_id == snapshot.fee_rule_version_id
        and version.pricing_draft_edit_id == snapshot.draft_edit_id
    )


def _active_only_edited_values(
    values: FeeEvaluationEditedExportValues,
) -> FeeEvaluationEditedExportValues:
    return FeeEvaluationEditedExportValues(
        rows=values.rows,
        summary=values.summary,
        manual_rows=values.manual_rows,
    )


def _summary_from_edited_values(
    values: FeeEvaluationEditedExportValues,
) -> ConfirmedFeeSummary:
    rows = (*values.rows, *values.manual_rows)
    testing_fee_total = sum((_decimal_value(row.testing_fee) for row in rows), Decimal("0"))
    working_hours = sum((_decimal_value(row.spend_time) for row in rows), Decimal("0"))
    working_hours += _decimal_value(
        values.summary.condition_confirmation_spend_time or "0"
    )
    hourly_rate = _decimal_value(values.summary.lab_manpower_hourly_rate or "0")
    lab_manpower_cost = working_hours * hourly_rate
    external_cost = _decimal_value(values.summary.external_cost or "0")
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


def _decimal_value(value: str) -> Decimal:
    normalized = str(value).strip().replace("$", "").replace(",", "")
    if not normalized or normalized.lower() == "pending":
        return Decimal("0")
    try:
        return Decimal(normalized.rstrip("%"))
    except InvalidOperation:
        return Decimal("0")


def _format_decimal(value: Decimal, quantum: Decimal, *, rounding=None) -> str:
    if rounding is not None:
        return str(value.quantize(quantum, rounding=rounding))
    return str(value.quantize(quantum))


def _decimal_text(value: Decimal | None, fallback: str) -> str:
    return str(value) if value is not None else fallback


def _text_or_zero(value: str | None) -> str:
    text = (value or "").strip()
    return text or "0"


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
