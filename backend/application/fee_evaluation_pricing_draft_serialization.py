"""Stable serialization for Fee Evaluation pricing-draft value payloads."""

from __future__ import annotations

import json

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedInactiveRow,
    FeeEvaluationEditedInactiveRowKey,
    FeeEvaluationEditedManualRow,
)


def edited_values_to_payload(values: FeeEvaluationEditedExportValues) -> dict[str, object]:
    """Return the legacy-compatible values document used inside V2 envelopes."""
    return {
        "rows": [_row_to_dict(row) for row in values.rows],
        "summary": {
            "condition_confirmation_spend_time": values.summary.condition_confirmation_spend_time,
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


def edited_values_to_json(values: FeeEvaluationEditedExportValues) -> str:
    """Serialize edited values to a stable legacy-compatible JSON document."""
    return json.dumps(edited_values_to_payload(values), ensure_ascii=False, sort_keys=True)


def edited_values_from_json(payload_json: str) -> FeeEvaluationEditedExportValues:
    """Deserialize one legacy-compatible values document."""
    payload = json.loads(payload_json)
    if not isinstance(payload, dict):
        raise ValueError("Fee Evaluation pricing draft payload must be an object.")
    return edited_values_from_payload(payload)


def edited_values_from_payload(payload: dict[str, object]) -> FeeEvaluationEditedExportValues:
    """Deserialize the values portion of a legacy or V2 pricing draft."""
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("Fee Evaluation pricing draft summary is invalid.")
    rows = payload.get("rows", [])
    manual_rows = payload.get("manual_rows", [])
    inactive_rows = payload.get("inactive_rows", [])
    if not all(isinstance(value, list) for value in (rows, manual_rows, inactive_rows)):
        raise ValueError("Fee Evaluation pricing draft rows are invalid.")
    return FeeEvaluationEditedExportValues(
        rows=tuple(_row_from_dict(row) for row in rows if isinstance(row, dict)),
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time=str(summary["condition_confirmation_spend_time"]),
            external_cost=str(summary["external_cost"]),
            external_cost_note=str(summary.get("external_cost_note", "")),
            lab_manpower_hourly_rate=str(summary["lab_manpower_hourly_rate"]),
        ),
        manual_rows=tuple(_manual_row_from_dict(row) for row in manual_rows if isinstance(row, dict)),
        inactive_rows=tuple(_inactive_row_from_dict(row) for row in inactive_rows if isinstance(row, dict)),
    )


def _row_to_dict(row: FeeEvaluationEditedExportRow) -> dict[str, object]:
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


def _row_from_dict(row: dict[str, object]) -> FeeEvaluationEditedExportRow:
    return FeeEvaluationEditedExportRow(
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


def _manual_row_from_dict(row: dict[str, object]) -> FeeEvaluationEditedManualRow:
    return FeeEvaluationEditedManualRow(
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


def _inactive_row_from_dict(payload: dict[str, object]) -> FeeEvaluationEditedInactiveRow:
    previous = payload.get("previous_row")
    key = payload.get("rebase_key") or payload.get("key")
    if not isinstance(previous, dict):
        previous = {}
    if not isinstance(key, dict):
        key = {}
    return FeeEvaluationEditedInactiveRow(
        previous_row=_row_from_dict(previous),
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
