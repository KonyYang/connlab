"""JSON payload helpers for pending Matrix-to-Fee rebase results."""

from __future__ import annotations

import json

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedManualRow,
)
from backend.application.matrix_fee_draft_rebase_service import (
    MatrixFeeInactiveRemovedRow,
    MatrixFeeRebaseKey,
    MatrixFeeRebaseResult,
    MatrixFeeRebaseSummary,
)


def pending_rebase_payload_to_json(result: MatrixFeeRebaseResult) -> str:
    """Serialize a pending rebase result as self-contained JSON."""
    payload = {
        "active_rows": [_row_to_dict(row) for row in result.active_rows],
        "inactive_removed_rows": [
            _inactive_removed_row_to_dict(row)
            for row in result.inactive_removed_rows
        ],
        "manual_rows": [_manual_row_to_dict(row) for row in result.manual_rows],
        "summary": {
            "preserved_count": result.summary.preserved_count,
            "added_count": result.summary.added_count,
            "removed_count": result.summary.removed_count,
            "preserved_manual_count": result.summary.preserved_manual_count,
            "removed_manual_count": result.summary.removed_manual_count,
        },
        "warnings": list(result.warnings),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pending_rebase_payload_from_json(payload_json: str) -> MatrixFeeRebaseResult:
    """Deserialize one persisted pending Matrix-to-Fee rebase payload."""
    payload = json.loads(payload_json)
    summary = payload.get("summary") or {}
    return MatrixFeeRebaseResult(
        active_rows=tuple(_row_from_dict(row) for row in payload.get("active_rows", [])),
        inactive_removed_rows=tuple(
            _inactive_removed_row_from_dict(row)
            for row in payload.get("inactive_removed_rows", [])
        ),
        manual_rows=tuple(
            _manual_row_from_dict(row) for row in payload.get("manual_rows", [])
        ),
        summary=MatrixFeeRebaseSummary(
            preserved_count=int(summary.get("preserved_count", 0)),
            added_count=int(summary.get("added_count", 0)),
            removed_count=int(summary.get("removed_count", 0)),
            preserved_manual_count=int(summary.get("preserved_manual_count", 0)),
            removed_manual_count=int(summary.get("removed_manual_count", 0)),
        ),
        warnings=tuple(str(item) for item in payload.get("warnings", [])),
    )


def _row_to_dict(row: FeeEvaluationEditedExportRow) -> dict[str, object]:
    """Serialize one Fee Evaluation row."""
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


def _manual_row_to_dict(row: FeeEvaluationEditedManualRow) -> dict[str, object]:
    """Serialize one manual Fee Evaluation row."""
    return {
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


def _inactive_removed_row_to_dict(
    row: MatrixFeeInactiveRemovedRow,
) -> dict[str, object]:
    """Serialize one hidden recoverable removed row."""
    return {
        "previous_row": _row_to_dict(row.previous_row),
        "rebase_key": {
            "group_identity": row.rebase_key.group_identity,
            "row_identity": row.rebase_key.row_identity,
            "step_token": row.rebase_key.step_token,
            "step_index": row.rebase_key.step_index,
        },
        "previous_group_key": row.previous_group_key,
        "previous_group_label": row.previous_group_label,
        "previous_row_signature": row.previous_row_signature,
        "inactive_reason": row.inactive_reason,
    }


def _row_from_dict(payload: dict[str, object]) -> FeeEvaluationEditedExportRow:
    """Deserialize one Fee Evaluation row."""
    return FeeEvaluationEditedExportRow(
        source_line_id=str(payload.get("source_line_id", "")),
        confirmed_group_id=str(payload.get("confirmed_group_id", "")),
        confirmed_row_id=str(payload.get("confirmed_row_id", "")),
        step_token=str(payload.get("step_token", "")),
        step_index=int(payload.get("step_index", 0)),
        spend_time=str(payload.get("spend_time", "")),
        unit_price=str(payload.get("unit_price", "")),
        unit_type=str(payload.get("unit_type", "")),
        units=str(payload.get("units", "")),
        base_fee=str(payload.get("base_fee", "")),
        discount=str(payload.get("discount", "")),
        testing_fee=str(payload.get("testing_fee", "")),
        notes=str(payload.get("notes", "")),
    )


def _manual_row_from_dict(payload: dict[str, object]) -> FeeEvaluationEditedManualRow:
    """Deserialize one manual Fee Evaluation row."""
    return FeeEvaluationEditedManualRow(
        row_kind=str(payload.get("row_kind", "")),
        spend_time=str(payload.get("spend_time", "")),
        unit_price=str(payload.get("unit_price", "")),
        unit_type=str(payload.get("unit_type", "")),
        units=str(payload.get("units", "")),
        base_fee=str(payload.get("base_fee", "")),
        discount=str(payload.get("discount", "")),
        testing_fee=str(payload.get("testing_fee", "")),
        notes=str(payload.get("notes", "")),
        confirmed_group_id=str(payload.get("confirmed_group_id", "")),
        group_key=str(payload.get("group_key", "")),
        group_label=str(payload.get("group_label", "")),
    )


def _inactive_removed_row_from_dict(
    payload: dict[str, object],
) -> MatrixFeeInactiveRemovedRow:
    """Deserialize one hidden recoverable removed row."""
    previous = payload.get("previous_row")
    key = payload.get("rebase_key")
    if not isinstance(previous, dict):
        previous = {}
    if not isinstance(key, dict):
        key = {}
    return MatrixFeeInactiveRemovedRow(
        previous_row=_row_from_dict(previous),
        rebase_key=MatrixFeeRebaseKey(
            group_identity=str(key.get("group_identity", "")),
            row_identity=str(key.get("row_identity", "")),
            step_token=str(key.get("step_token", "")),
            step_index=int(key.get("step_index", 0)),
        ),
        previous_group_key=str(payload.get("previous_group_key", "")),
        previous_group_label=str(payload.get("previous_group_label", "")),
        previous_row_signature=str(payload.get("previous_row_signature", "")),
        inactive_reason=str(payload.get("inactive_reason", "removed_from_matrix")),
    )
