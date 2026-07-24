"""Canonical signatures and payload helpers for Matrix Editor sessions."""

from __future__ import annotations

from typing import Any

from backend.application.matrix_schedule_planning import (
    MatrixScheduleFields,
    MatrixScheduleValidationError,
    calculate_group_test_days,
    validate_planned_schedule,
)
from backend.domain import (
    ConfirmedMatrixSnapshot,
    ProjectMatrixDraftSnapshot,
)

from backend.application.matrix_editor_session_contracts import (
    MatrixEditorSessionError,
    MatrixEditorSessionGroup,
    MatrixEditorSessionRow,
    MatrixEditorSessionCell,
    MatrixEditorSessionDurationAuthority,
    MatrixEditorSessionConfirmCommand,
)
from backend.application.matrix_editor_confirmed_snapshot_builder import (
    _normalize_group_label,
    _utc_now,
)

def _validate_session_schedule(command: MatrixEditorSessionConfirmCommand) -> None:
    selected_group_ids = [
        group.draft_group_id
        for group in command.groups
        if group.is_selected and group.draft_group_id.strip()
    ]
    try:
        totals = calculate_group_test_days(
            rows=(
                {
                    "row_id": row.draft_row_id,
                    "day_expression": row.day_expression,
                    "is_sample_row": row.is_sample_row,
                }
                for row in command.rows
            ),
            cells=(
                {
                    "row_id": cell.draft_row_id,
                    "group_id": cell.draft_group_id,
                    "cell_value": cell.cell_value,
                }
                for cell in command.cells
            ),
            selected_group_ids=selected_group_ids,
        )
        validate_planned_schedule(
            fields=MatrixScheduleFields(
                pre_test_buffer_days=command.pre_test_buffer_days,
                post_test_buffer_days=command.post_test_buffer_days,
                sample_received_date=command.sample_received_date,
                planned_test_start_date=command.planned_test_start_date,
                planned_test_complete_date=command.planned_test_complete_date,
                estimated_completion_date=command.estimated_completion_date,
            ),
            group_test_days=totals,
        )
    except MatrixScheduleValidationError as exc:
        raise MatrixEditorSessionError(str(exc)) from exc


def _build_signature_from_session_payload(
    command: MatrixEditorSessionConfirmCommand,
) -> str:
    groups = sorted(
        (group for group in command.groups if group.is_selected),
        key=lambda item: item.group_order,
    )
    rows = sorted(
        (row for row in command.rows if not row.is_sample_row),
        key=lambda item: item.row_order,
    )
    group_index = {group.draft_group_id: idx for idx, group in enumerate(groups)}
    row_index = {row.draft_row_id: idx for idx, row in enumerate(rows)}
    cell_map: dict[tuple[int, int], str] = {}
    for cell in command.cells:
        r_index = row_index.get(cell.draft_row_id)
        g_index = group_index.get(cell.draft_group_id)
        if r_index is None or g_index is None:
            continue
        value = (cell.cell_value or "").strip()
        if not value:
            continue
        cell_map[(r_index, g_index)] = value
    payload = {
        "groups": [
            {
                "group_order": group_index + 1,
                "group_key": group.group_key.strip(),
                "group_label": _normalize_group_label(
                    group.group_label, fallback=str(group_index + 1)
                ),
                "sample_quantity_expression": (group.sample_quantity_expression or "").strip(),
                "sample_note": (group.sample_note or "").strip(),
                "is_selected": True,
            }
            for group_index, group in enumerate(groups)
        ],
        "rows": [
            {
                "row_order": row.row_order,
                "test_item": row.test_item.strip(),
                "source_section": (row.source_section or "").strip(),
                "method": (row.method or "").strip(),
                "condition": (row.condition or "").strip(),
                "requirement": (row.requirement or "").strip(),
                "day_expression": (row.day_expression or "").strip(),
                "cells": [
                    cell_map.get((row_idx, group_idx), "")
                    for group_idx, _ in enumerate(groups)
                ],
            }
            for row_idx, row in enumerate(rows)
        ],
        "schedule": _schedule_signature_from_command(command),
        "duration_authorities": sorted(
            (
                group_index[item.draft_group_id],
                row_index[item.draft_row_id],
                item.step_sequence,
                item.step_suffix_note.strip(),
                format(item.duration_value, "f"),
                item.duration_unit.strip().lower(),
                format(item.normalized_hours, "f"),
                item.source_kind,
                item.source_field,
                item.source_fingerprint,
                item.lineage_fingerprint,
                item.authority_revision,
                item.status,
            )
            for item in command.duration_authorities
            if item.draft_group_id in group_index and item.draft_row_id in row_index
        ),
    }
    return repr(payload)


def _has_expected_saved_draft(command: MatrixEditorSessionConfirmCommand) -> bool:
    return bool(
        (command.expected_editor_draft_id or "").strip()
        and (command.expected_saved_payload_signature or "").strip()
    )

def _schedule_signature_from_command(
    command: MatrixEditorSessionConfirmCommand,
) -> dict[str, str]:
    return {
        "pre_test_buffer_days": (command.pre_test_buffer_days or "").strip(),
        "post_test_buffer_days": (command.post_test_buffer_days or "").strip(),
        "sample_received_date": (command.sample_received_date or "").strip(),
        "planned_test_start_date": (command.planned_test_start_date or "").strip(),
        "planned_test_complete_date": (command.planned_test_complete_date or "").strip(),
        "estimated_completion_date": (command.estimated_completion_date or "").strip(),
    }


def _schedule_signature_from_confirmed(
    snapshot: ConfirmedMatrixSnapshot,
) -> dict[str, str]:
    return {
        "pre_test_buffer_days": (snapshot.version.pre_test_buffer_days or "").strip(),
        "post_test_buffer_days": (snapshot.version.post_test_buffer_days or "").strip(),
        "sample_received_date": (snapshot.version.sample_received_date or "").strip(),
        "planned_test_start_date": (snapshot.version.planned_test_start_date or "").strip(),
        "planned_test_complete_date": (
            snapshot.version.planned_test_complete_date or ""
        ).strip(),
        "estimated_completion_date": (snapshot.version.estimated_completion_date or "").strip(),
    }


def _build_signature_from_confirmed(snapshot: ConfirmedMatrixSnapshot) -> str:
    groups = sorted(snapshot.groups, key=lambda item: item.group_order)
    rows = sorted(snapshot.rows, key=lambda item: item.row_order)
    group_index = {group.confirmed_group_id: idx for idx, group in enumerate(groups)}
    row_index = {row.confirmed_row_id: idx for idx, row in enumerate(rows)}
    cell_map: dict[tuple[int, int], str] = {}
    for cell in snapshot.cells:
        r_index = row_index.get(cell.confirmed_row_id)
        g_index = group_index.get(cell.confirmed_group_id)
        if r_index is None or g_index is None:
            continue
        value = (cell.cell_value or "").strip()
        if not value:
            continue
        cell_map[(r_index, g_index)] = value
    payload = {
        "groups": [
            {
                "group_order": group.group_order,
                "group_key": group.group_key.strip(),
                "group_label": _normalize_group_label(
                    group.group_label, fallback=str(group.group_order)
                ),
                "sample_quantity_expression": (group.sample_quantity_expression or "").strip(),
                "sample_note": (group.sample_note or "").strip(),
                "is_selected": True,
            }
            for group in groups
        ],
        "rows": [
            {
                "row_order": row.row_order,
                "test_item": row.test_item.strip(),
                "source_section": (row.source_section or "").strip(),
                "method": (row.method or "").strip(),
                "condition": (row.condition or "").strip(),
                "requirement": (row.requirement or "").strip(),
                "day_expression": (row.day_expression or "").strip(),
                "cells": [
                    cell_map.get((row_idx, group_idx), "")
                    for group_idx, _ in enumerate(groups)
                ],
            }
            for row_idx, row in enumerate(rows)
        ],
        "schedule": _schedule_signature_from_confirmed(snapshot),
        "duration_authorities": sorted(
            (
                group_index[item.confirmed_group_id],
                row_index[item.confirmed_row_id],
                item.step_sequence,
                item.step_suffix_note.strip(),
                format(item.duration_value, "f"),
                item.duration_unit.strip().lower(),
                format(item.normalized_hours, "f"),
                item.source_kind,
                item.source_field,
                item.source_fingerprint,
                item.lineage_fingerprint,
                item.authority_revision,
                item.status,
            )
            for item in snapshot.duration_authorities
            if item.confirmed_group_id in group_index
            and item.confirmed_row_id in row_index
        ),
    }
    return repr(payload)


def build_project_matrix_draft_payload_signature(
    draft: ProjectMatrixDraftSnapshot,
) -> str:
    """Return the canonical saved-payload signature for one persisted draft."""
    command = MatrixEditorSessionConfirmCommand(
        project_id=draft.record.project_id,
        expected_active_confirmed_matrix_id=draft.record.base_confirmed_matrix_id,
        expected_active_confirmed_revision=None,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=draft.record.source_import_id,
        source_snapshot_id=draft.record.source_snapshot_id,
        confirmed_by="signature",
        groups=tuple(
            MatrixEditorSessionGroup(
                draft_group_id=group.draft_group_id,
                source_group_snapshot_id=group.source_group_snapshot_id,
                group_order=group.group_order,
                group_key=group.group_key,
                group_label=group.group_label,
                is_selected=group.is_selected,
                sample_quantity_expression=group.sample_quantity_expression,
                sample_note=group.sample_note,
            )
            for group in draft.groups
        ),
        rows=tuple(
            MatrixEditorSessionRow(
                draft_row_id=row.draft_row_id,
                source_row_snapshot_id=row.source_row_snapshot_id,
                row_order=row.row_order,
                test_item=row.test_item,
                source_section=row.source_section,
                method=row.method,
                condition=row.condition,
                requirement=row.requirement,
                day_expression=row.day_expression,
                is_sample_row=row.is_sample_row,
            )
            for row in draft.rows
        ),
        cells=tuple(
            MatrixEditorSessionCell(
                draft_row_id=cell.draft_row_id,
                draft_group_id=cell.draft_group_id,
                cell_value=cell.cell_value,
            )
            for cell in draft.cells
        ),
        duration_authorities=tuple(
            MatrixEditorSessionDurationAuthority(
                draft_duration_authority_id=item.draft_duration_authority_id,
                draft_group_id=item.draft_group_id,
                draft_row_id=item.draft_row_id,
                step_sequence=item.step_sequence,
                step_suffix_note=item.step_suffix_note,
                duration_value=item.duration_value,
                duration_unit=item.duration_unit,
                normalized_hours=item.normalized_hours,
                source_kind=item.source_kind,
                source_field=item.source_field,
                source_import_id=item.source_import_id,
                source_fingerprint=item.source_fingerprint,
                lineage_fingerprint=item.lineage_fingerprint,
                authority_revision=item.authority_revision,
                status=item.status,
            )
            for item in draft.duration_authorities
        ),
        pre_test_buffer_days=draft.record.pre_test_buffer_days,
        post_test_buffer_days=draft.record.post_test_buffer_days,
        sample_received_date=draft.record.sample_received_date,
        planned_test_start_date=draft.record.planned_test_start_date,
        planned_test_complete_date=draft.record.planned_test_complete_date,
        estimated_completion_date=draft.record.estimated_completion_date,
    )
    return _build_signature_from_session_payload(command)


_build_signature_from_project_draft = build_project_matrix_draft_payload_signature


def _build_manual_preview_payload(
    command: MatrixEditorSessionConfirmCommand,
) -> dict[str, Any]:
    sorted_groups = sorted(command.groups, key=lambda item: item.group_order)
    sorted_rows = sorted(command.rows, key=lambda item: item.row_order)
    cell_map: dict[tuple[str, str], str] = {}
    for cell in command.cells:
        value = (cell.cell_value or "").strip()
        if not value:
            continue
        cell_map[(cell.draft_row_id, cell.draft_group_id)] = value
    groups: list[dict[str, Any]] = []
    for group in sorted_groups:
        groups.append(
            {
                "group_key": group.group_key,
                "group_label": _normalize_group_label(
                    group.group_label, fallback=str(group.group_order)
                ),
                "source_table_index": 0,
                "extraction_status": "manual",
                "sample_size": None,
                "sample_quantity_expression": group.sample_quantity_expression,
                "sample_note": group.sample_note,
                "steps": [],
            }
        )
    rows: list[dict[str, Any]] = []
    group_by_id = {group.draft_group_id: group for group in sorted_groups}
    for row in sorted_rows:
        row_tokens: dict[str, str] = {}
        for group in sorted_groups:
            value = cell_map.get((row.draft_row_id, group.draft_group_id), "")
            normalized_label = _normalize_group_label(
                group.group_label, fallback=str(group.group_order)
            )
            row_tokens[normalized_label] = value
            row_tokens[group.group_key] = value
        rows.append(
            {
                "source_row_index": row.row_order,
                "test_item": row.test_item,
                "source_section": row.source_section,
                "group_tokens": row_tokens,
                "is_sample_row": bool(row.is_sample_row),
                "duration_authorities": [
                    {
                        "owning_group_key": group_by_id[
                            item.draft_group_id
                        ].group_key,
                        "step_sequence": item.step_sequence,
                        "step_suffix_note": item.step_suffix_note,
                        "duration_value": format(item.duration_value, "f"),
                        "duration_unit": item.duration_unit,
                        "source_field": item.source_field,
                        "source_identity": {
                            "group_key": group_by_id[
                                item.draft_group_id
                            ].group_key,
                        },
                    }
                    for item in command.duration_authorities
                    if item.draft_row_id == row.draft_row_id
                    and item.draft_group_id in group_by_id
                ],
            }
        )
    return {
        "project_id": command.project_id,
        "source_document_path": command.source_document_path or "manual://matrix-editor",
        "source_document_name": command.source_document_name
        or "Matrix Editor Manual Draft",
        "source_format": command.source_format or "manual",
        "capability_status": "supported",
        "generated_at": _utc_now(),
        "selected_table_index": 0,
        "selected_page_number": 1,
        "selected_page_table_index": 1,
        "candidate_tables": [],
        "preview_pdf_token": None,
        "rows": rows,
        "groups": groups,
        "warnings": [],
        "blockers": [],
    }


def _is_source_lineage_replaced(
    command: MatrixEditorSessionConfirmCommand,
    active: ConfirmedMatrixSnapshot,
) -> bool:
    source_import_id = (command.source_import_id or "").strip()
    source_snapshot_id = (command.source_snapshot_id or "").strip()
    if not source_import_id or not source_snapshot_id:
        return False
    return (
        source_import_id != active.version.source_import_id
        or source_snapshot_id != active.version.source_snapshot_id
    )


def _is_same_source_lineage(
    command: MatrixEditorSessionConfirmCommand,
    active: ConfirmedMatrixSnapshot,
) -> bool:
    source_import_id = (command.source_import_id or "").strip()
    source_snapshot_id = (command.source_snapshot_id or "").strip()
    if not source_import_id or not source_snapshot_id:
        return False
    return (
        source_import_id == active.version.source_import_id
        and source_snapshot_id == active.version.source_snapshot_id
    )
