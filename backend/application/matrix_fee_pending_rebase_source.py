"""Source-row helpers for pending Matrix-to-Fee rebase."""

from __future__ import annotations

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    MatrixBasicFillGroup,
    MatrixBasicFillLine,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportValues,
    edited_row_identity,
)
from backend.application.matrix_fee_draft_rebase_service import (
    MatrixFeeRebaseKey,
    MatrixFeeRebaseLineage,
    MatrixFeeRebaseSourceRow,
    matrix_fee_rebase_key_for_lineage,
)


def source_rows_from_basic_fill(
    groups: tuple[MatrixBasicFillGroup, ...],
    *,
    source_values: FeeEvaluationEditedExportValues | None,
    structural_keys: set[MatrixFeeRebaseKey],
) -> tuple[MatrixFeeRebaseSourceRow, ...]:
    """Build rebase source rows from current basic-fill plus hidden rows."""
    edited_by_identity = (
        {edited_row_identity(row): row for row in source_values.rows}
        if source_values is not None
        else {}
    )
    hidden_by_key = _hidden_rows_by_key(
        source_values,
        structural_keys=structural_keys,
    )
    consumed_hidden_keys: set[MatrixFeeRebaseKey] = set()
    rows: list[MatrixFeeRebaseSourceRow] = []
    for group in groups:
        for line in group.lines:
            default_row = _default_row_from_basic_fill_line(line)
            lineage = MatrixFeeRebaseLineage(
                group_key=group.group_key,
                group_label=group.group_label,
                confirmed_group_id=line.confirmed_group_id,
                confirmed_row_id=line.confirmed_row_id,
                source_row_snapshot_id=line.source_row_id,
                draft_row_id=None,
                step_token=line.step_tokens[0] if line.step_tokens else "",
                step_index=line.step_index,
                test_item=line.test_item,
            )
            active_edit = edited_by_identity.get(edited_row_identity(default_row))
            key = matrix_fee_rebase_key_for_lineage(lineage)
            hidden_edit = hidden_by_key.get(key)
            if hidden_edit is not None:
                consumed_hidden_keys.add(key)
            rows.append(
                MatrixFeeRebaseSourceRow(
                    lineage=lineage,
                    edited_row=active_edit or hidden_edit or default_row,
                )
            )
    rows.extend(
        _source_rows_from_hidden_rows(
            source_values,
            hidden_by_key=hidden_by_key,
            consumed_hidden_keys=consumed_hidden_keys,
        )
    )
    return tuple(rows)


def _hidden_rows_by_key(
    source_values: FeeEvaluationEditedExportValues | None,
    *,
    structural_keys: set[MatrixFeeRebaseKey],
) -> dict[MatrixFeeRebaseKey, FeeEvaluationEditedExportRow]:
    """Return structurally valid hidden rows keyed for rebase matching."""
    if source_values is None:
        return {}
    rows: dict[MatrixFeeRebaseKey, FeeEvaluationEditedExportRow] = {}
    for row in source_values.inactive_rows:
        key = MatrixFeeRebaseKey(
            group_identity=row.rebase_key.group_identity,
            row_identity=row.rebase_key.row_identity,
            step_token=row.rebase_key.step_token,
            step_index=row.rebase_key.step_index,
        )
        if key in structural_keys:
            rows[key] = row.previous_row
    return rows


def _source_rows_from_hidden_rows(
    source_values: FeeEvaluationEditedExportValues | None,
    *,
    hidden_by_key: dict[MatrixFeeRebaseKey, FeeEvaluationEditedExportRow],
    consumed_hidden_keys: set[MatrixFeeRebaseKey],
) -> tuple[MatrixFeeRebaseSourceRow, ...]:
    """Convert hidden rows missing from current basic-fill into source rows."""
    if source_values is None:
        return ()
    rows: list[MatrixFeeRebaseSourceRow] = []
    for row in source_values.inactive_rows:
        key = MatrixFeeRebaseKey(
            group_identity=row.rebase_key.group_identity,
            row_identity=row.rebase_key.row_identity,
            step_token=row.rebase_key.step_token,
            step_index=row.rebase_key.step_index,
        )
        if key not in hidden_by_key or key in consumed_hidden_keys:
            continue
        rows.append(
            MatrixFeeRebaseSourceRow(
                lineage=MatrixFeeRebaseLineage(
                    group_key=row.group_key,
                    group_label=row.group_label,
                    confirmed_group_id=row.previous_row.confirmed_group_id,
                    confirmed_row_id=row.previous_row.confirmed_row_id,
                    source_row_snapshot_id=None,
                    draft_row_id=None,
                    step_token=row.previous_row.step_token,
                    step_index=row.previous_row.step_index,
                    test_item=row.group_signature,
                ),
                edited_row=row.previous_row,
                rebase_key=key,
            )
        )
    return tuple(rows)


def _default_row_from_basic_fill_line(line: MatrixBasicFillLine) -> FeeEvaluationEditedExportRow:
    """Return saveable defaults for one current basic-fill line."""
    return FeeEvaluationEditedExportRow(
        source_line_id=line.line_id,
        confirmed_group_id=line.confirmed_group_id,
        confirmed_row_id=line.confirmed_row_id,
        step_token=line.step_tokens[0] if line.step_tokens else "",
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
