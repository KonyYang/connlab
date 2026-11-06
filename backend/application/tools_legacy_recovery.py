"""Read-only transfer of retained temporary pricing to the current planning rows."""
from dataclasses import replace
from backend.application.fee_evaluation_edited_export_values import FeeEvaluationEditedExportValues
from backend.application.tools_matrix_snapshot import planning_snapshot
from backend.application.confirmed_matrix_fee_template_basic_fill_service import build_basic_fill_from_confirmed_snapshot


def recover_pricing(matrix: dict, saved, original_matrix):
    if saved is None:
        return None, []
    source = saved.edited_values
    groups = {g.confirmed_group_id:g.draft_group_id for g in original_matrix.groups} if original_matrix else {}
    rows = {r.confirmed_row_id:r.draft_row_id for r in original_matrix.rows} if original_matrix else {}
    try:
        current = build_basic_fill_from_confirmed_snapshot(planning_snapshot(matrix))
    except (ValueError, KeyError) as exc:
        return None, [f'Fee edits retained without transfer: {exc}']
    targets = {(line.confirmed_group_id,line.confirmed_row_id,line.step_tokens[0],line.step_index):line
               for group in current.groups for line in group.lines}
    copied, skipped = [], []
    for row in source.rows:
        key = (groups.get(row.confirmed_group_id,row.confirmed_group_id), rows.get(row.confirmed_row_id,row.confirmed_row_id),row.step_token,row.step_index)
        target = targets.get(key)
        if target is None:
            skipped.append(f'{row.confirmed_group_id} / {row.step_token}')
            continue
        copied.append(replace(row,source_line_id=target.line_id,confirmed_group_id=target.confirmed_group_id,confirmed_row_id=target.confirmed_row_id))
    group_lookup = {g.confirmed_group_id:g for g in current.groups}
    manual = []
    for row in source.manual_rows:
        if row.row_kind == 'report_preparation':
            manual.append(row)
            continue
        group = group_lookup.get(groups.get(row.confirmed_group_id,row.confirmed_group_id))
        if group is None:
            skipped.append(f'{row.row_kind} / {row.group_label or row.confirmed_group_id}')
        else:
            manual.append(replace(row,confirmed_group_id=group.confirmed_group_id,
                                  group_key=group.group_key,group_label=group.group_label))
    skipped.extend(f'Inactive fee row / {row.previous_row.step_token}' for row in source.inactive_rows)
    return FeeEvaluationEditedExportValues(tuple(copied),source.summary,tuple(manual)), skipped
