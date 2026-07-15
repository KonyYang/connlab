"""Pure Fee draft value mapping helpers used by Matrix rebase promotion."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import TYPE_CHECKING

from backend.application.confirmed_matrix_fee_draft_service import (
    FeeEvaluationDraft,
    FeeEvaluationGroup,
    FeeEvaluationLineItem,
)
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    build_basic_fill_from_confirmed_snapshot,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedManualRow,
)
from backend.application.confirmed_fee_pricing_snapshot import (
    matches_current_v2_pricing_snapshot,
)
from backend.domain import ConfirmedMatrixSnapshot
from backend.domain.confirmed_fee import ConfirmedFeeSummary, ConfirmedFeeVersion

if TYPE_CHECKING:
    from backend.application.fee_evaluation_pricing_draft_persistence_service import (
        FeeEvaluationPricingDraftSnapshot,
    )


def edited_values_from_fee_draft(
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
        summary=blank_summary(),
        manual_rows=manual_rows,
    )


def confirmed_fee_matches_snapshot(
    version: ConfirmedFeeVersion,
    snapshot: FeeEvaluationPricingDraftSnapshot,
) -> bool:
    base_matches = (
        version.project_id == snapshot.project_id
        and version.confirmed_matrix_id == snapshot.confirmed_matrix_id
        and version.confirmed_revision == snapshot.confirmed_revision
        and version.fee_rule_version_id == snapshot.fee_rule_version_id
        and version.pricing_draft_edit_id == snapshot.draft_edit_id
    )
    if not base_matches:
        return False
    if snapshot.generation is None:
        return True
    return matches_current_v2_pricing_snapshot(version.pricing_snapshot_json, snapshot)


def active_only_edited_values(
    values: FeeEvaluationEditedExportValues,
) -> FeeEvaluationEditedExportValues:
    return FeeEvaluationEditedExportValues(
        rows=values.rows,
        summary=values.summary,
        manual_rows=values.manual_rows,
    )


def summary_from_edited_values(
    values: FeeEvaluationEditedExportValues,
) -> ConfirmedFeeSummary:
    rows = (*values.rows, *values.manual_rows)
    testing_fee_total = sum((_decimal_value(row.testing_fee) for row in rows), Decimal("0"))
    working_hours = sum((_decimal_value(row.spend_time) for row in rows), Decimal("0"))
    working_hours += _decimal_value(values.summary.condition_confirmation_spend_time or "0")
    hourly_rate = _decimal_value(values.summary.lab_manpower_hourly_rate or "0")
    lab_manpower_cost = working_hours * hourly_rate
    external_cost = _decimal_value(values.summary.external_cost or "0")
    grand_cost = testing_fee_total + external_cost
    return ConfirmedFeeSummary(
        testing_fee_total=_format_decimal(testing_fee_total, Decimal("0.01")),
        working_hours=_format_decimal(working_hours, Decimal("0.1")),
        lab_manpower_cost=_format_decimal(lab_manpower_cost, Decimal("1"), rounding=ROUND_HALF_UP),
        external_cost=_format_decimal(external_cost, Decimal("0.01")),
        grand_cost=_format_decimal(grand_cost, Decimal("0.01")),
    )


def _rows_from_fee_line(line: FeeEvaluationLineItem) -> tuple[FeeEvaluationEditedExportRow, ...]:
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


def _decimal_value(value: str) -> Decimal:
    normalized = str(value).strip().replace("$", "").replace(",", "")
    if not normalized or normalized.lower() == "pending":
        return Decimal("0")
    try:
        return Decimal(normalized.rstrip("%"))
    except InvalidOperation:
        return Decimal("0")


def _format_decimal(value: Decimal, quantum: Decimal, *, rounding=None) -> str:
    return str(value.quantize(quantum, rounding=rounding)) if rounding else str(value.quantize(quantum))


def _decimal_text(value: Decimal | None, fallback: str) -> str:
    return str(value) if value is not None else fallback


def _text_or_zero(value: str | None) -> str:
    return (value or "").strip() or "0"


def blank_summary() -> FeeEvaluationEditedExportSummary:
    return FeeEvaluationEditedExportSummary(
        condition_confirmation_spend_time="",
        external_cost="",
        external_cost_note="",
        lab_manpower_hourly_rate="",
    )


def index_new_basic_fill_by_draft_identity(
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


def remap_row(
    row: FeeEvaluationEditedExportRow,
    line_by_draft_identity: dict[tuple[str, str, str, int], FeeEvaluationEditedExportRow],
) -> FeeEvaluationEditedExportRow:
    identity = (row.confirmed_group_id, row.confirmed_row_id, row.step_token, row.step_index)
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


def remap_manual_row(
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


def _find_group_for_manual_row(row: FeeEvaluationEditedManualRow, snapshot: ConfirmedMatrixSnapshot):
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
    return value.strip() or "Pending"
