"""Pure projections for Matrix Editor sessions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from typing import Any, Callable, Literal, Protocol
from uuid import uuid4

from backend.application.confirmed_matrix_authority_service import (
    ConfirmProjectMatrixDraftCommand,
    ConfirmedMatrixAuthorityConflictError,
    ConfirmedMatrixAuthorityError,
    ConfirmedMatrixAuthorityNotFoundError,
    ConfirmedMatrixAuthorityService,
)
from backend.application.matrix_import_commit_service import (
    MatrixImportCommitCommand,
    MatrixImportCommitError,
    MatrixImportCommitNotFoundError,
    MatrixImportCommitService,
)
from backend.application.matrix_schedule_planning import (
    MatrixScheduleFields,
    MatrixScheduleValidationError,
    calculate_group_test_days,
    validate_planned_schedule,
)
from backend.application.matrix_sample_quantity_guard import (
    find_selected_sample_quantity_violations,
    format_sample_quantity_violation_message,
)
from backend.application.matrix_step_quantity_authority_builder import (
    build_confirmed_step_quantities,
)
from backend.application.matrix_step_quantity_authority_comparison import (
    step_quantity_authority_matches,
)
from backend.application.matrix_revision_flow_service import (
    CreateMatrixRevisionDraftCommand,
    MatrixRevisionFlowConflictError,
    MatrixRevisionFlowService,
)
from backend.application.matrix_fee_draft_rebase_service import MatrixFeeRebaseSummary
from backend.application.matrix_fee_pending_rebase_service import (
    DeletePendingRebaseForMatrixDraftCommand,
    MatrixFeePendingRebaseResult,
    RebaseAfterMatrixAutosaveCommand,
)
from backend.application.matrix_fee_rebase_promotion_service import (
    MatrixFeeRebasePromotionResult,
    MatrixFeeRebasePromotionStatus,
    PromoteMatrixFeeRebaseCommand,
)
from backend.application.project_matrix_draft_persistence_service import (
    ProjectMatrixDraftCellInput,
    ProjectMatrixDraftGroupInput,
    ProjectMatrixDraftPersistenceError,
    ProjectMatrixDraftPersistenceNotFoundError,
    ProjectMatrixDraftPersistenceService,
    ProjectMatrixDraftRowInput,
    UpdateProjectMatrixDraftCommand,
)
from backend.application.project_lifecycle_write_guard import (
    LifecycleWriteOperation,
    ProjectLifecycleWriteGuard,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    Project,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftStatus,
    SourceMatrixImportRecord,
    SourceMatrixSnapshot,
)
from backend.modules.fee_evaluation import load_active_fee_rule_library



from backend.application.matrix_editor_session_contracts import (
    SOURCE_UNAVAILABLE_MESSAGE,
    MatrixEditorSessionError,
    MatrixEditorSessionNotFoundError,
    MatrixEditorSessionActiveChangedError,
    MatrixEditorSessionDraftConflictError,
    ProjectStore,
    ConfirmedStore,
    SourceStore,
    DraftStore,
    PendingFeeRebaseService,
    FeeRebasePromotionService,
    MatrixEditorSessionGroup,
    MatrixEditorSessionRow,
    MatrixEditorSessionCell,
    MatrixEditorSessionDraft,
    MatrixEditorSessionDurationAuthority,
    MatrixEditorSessionSeed,
    MatrixEditorSessionConfirmCommand,
    MatrixEditorSessionDraftSaveCommand,
    MatrixEditorSessionDraftSaveResult,
    MatrixEditorSessionDraftDiscardCommand,
    MatrixEditorSessionDraftDiscardResult,
    MatrixEditorSessionConfirmResult,
)
from backend.application.matrix_editor_confirmed_snapshot_builder import (
    _normalize_group_label,
    _utc_now,
)

def _build_editor_draft_from_active(
    active: ConfirmedMatrixSnapshot,
) -> MatrixEditorSessionDraft:
    groups = tuple(
        MatrixEditorSessionGroup(
            draft_group_id=group.draft_group_id,
            source_group_snapshot_id=group.source_group_snapshot_id,
            group_order=group.group_order,
            group_key=group.group_key,
            group_label=_normalize_group_label(
                group.group_label, fallback=str(group.group_order)
            ),
            is_selected=True,
            sample_quantity_expression=group.sample_quantity_expression,
            sample_note=group.sample_note,
        )
        for group in sorted(active.groups, key=lambda item: item.group_order)
    )
    rows = tuple(
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
            is_sample_row=False,
        )
        for row in sorted(active.rows, key=lambda item: item.row_order)
    )
    cells = tuple(
        MatrixEditorSessionCell(
            draft_row_id=cell.draft_row_id,
            draft_group_id=cell.draft_group_id,
            cell_value=cell.cell_value,
        )
        for cell in active.cells
    )
    group_by_confirmed = {
        group.confirmed_group_id: group.draft_group_id for group in active.groups
    }
    row_by_confirmed = {
        row.confirmed_row_id: row.draft_row_id for row in active.rows
    }
    return MatrixEditorSessionDraft(
        groups=groups,
        rows=rows,
        cells=cells,
        duration_authorities=tuple(
            MatrixEditorSessionDurationAuthority(
                draft_duration_authority_id=None,
                draft_group_id=group_by_confirmed[item.confirmed_group_id],
                draft_row_id=row_by_confirmed[item.confirmed_row_id],
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
            for item in active.duration_authorities
            if item.confirmed_group_id in group_by_confirmed
            and item.confirmed_row_id in row_by_confirmed
        ),
    )


def _build_editor_draft_from_project_draft(
    draft: ProjectMatrixDraftSnapshot,
) -> MatrixEditorSessionDraft:
    groups = tuple(
        MatrixEditorSessionGroup(
            draft_group_id=group.draft_group_id,
            source_group_snapshot_id=group.source_group_snapshot_id,
            group_order=group.group_order,
            group_key=group.group_key,
            group_label=_normalize_group_label(group.group_label, fallback=str(group.group_order)),
            is_selected=group.is_selected,
            sample_quantity_expression=group.sample_quantity_expression,
            sample_note=group.sample_note,
        )
        for group in sorted(draft.groups, key=lambda item: item.group_order)
    )
    rows = tuple(
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
        for row in sorted(draft.rows, key=lambda item: item.row_order)
    )
    cells = tuple(
        MatrixEditorSessionCell(
            draft_row_id=cell.draft_row_id,
            draft_group_id=cell.draft_group_id,
            cell_value=cell.cell_value,
        )
        for cell in draft.cells
    )
    return MatrixEditorSessionDraft(
        groups=groups,
        rows=rows,
        cells=cells,
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
    )


def _confirm_command_from_save_command(
    command: MatrixEditorSessionDraftSaveCommand,
    *,
    confirmed_by: str,
) -> MatrixEditorSessionConfirmCommand:
    return MatrixEditorSessionConfirmCommand(
        project_id=command.project_id,
        expected_active_confirmed_matrix_id=command.expected_active_confirmed_matrix_id,
        expected_active_confirmed_revision=command.expected_active_confirmed_revision,
        source_document_path=command.source_document_path,
        source_document_name=command.source_document_name,
        source_format=command.source_format,
        source_import_id=command.source_import_id,
        source_snapshot_id=command.source_snapshot_id,
        confirmed_by=confirmed_by,
        groups=command.groups,
        rows=command.rows,
        cells=command.cells,
        duration_authorities=command.duration_authorities,
        pre_test_buffer_days=command.pre_test_buffer_days,
        post_test_buffer_days=command.post_test_buffer_days,
        sample_received_date=command.sample_received_date,
        planned_test_start_date=command.planned_test_start_date,
        planned_test_complete_date=command.planned_test_complete_date,
        estimated_completion_date=command.estimated_completion_date,
    )


def _build_source_preview_payload(
    *,
    source_snapshot: SourceMatrixSnapshot,
    import_record: SourceMatrixImportRecord | None,
) -> dict[str, Any]:
    sorted_groups = sorted(source_snapshot.groups, key=lambda item: item.group_order)
    sorted_rows = sorted(source_snapshot.rows, key=lambda item: item.row_order)
    token_map: dict[tuple[str, str], str] = {}
    for cell in source_snapshot.cells:
        token_map[(cell.row_snapshot_id, cell.group_snapshot_id)] = cell.cell_value
    rows: list[dict[str, Any]] = []
    for row in sorted_rows:
        row_tokens: dict[str, str] = {}
        for group in sorted_groups:
            value = token_map.get((row.row_snapshot_id, group.group_snapshot_id), "")
            row_tokens[group.group_label] = value
            row_tokens[group.group_key] = value
        rows.append(
            {
                "source_row_index": row.source_row_index if row.source_row_index is not None else row.row_order,
                "test_item": row.test_item,
                "source_section": row.source_section,
                "method": row.method,
                "condition": row.condition,
                "requirement": row.requirement,
                "group_tokens": row_tokens,
                "is_sample_row": bool(row.is_sample_row),
                "duration_authorities": [
                    {
                        "owning_group_key": next(
                            group.group_key
                            for group in sorted_groups
                            if group.group_snapshot_id
                            == item.source_group_snapshot_id
                        ),
                        "step_sequence": item.step_sequence,
                        "step_suffix_note": item.step_suffix_note,
                        "duration_value": format(item.duration_value, "f"),
                        "duration_unit": item.duration_unit,
                        "source_field": item.source_field,
                        "source_identity": {
                            "row_snapshot_id": row.row_snapshot_id,
                            "group_key": next(
                                group.group_key
                                for group in sorted_groups
                                if group.group_snapshot_id
                                == item.source_group_snapshot_id
                            ),
                        },
                    }
                    for item in source_snapshot.duration_authorities
                    if item.source_row_snapshot_id == row.row_snapshot_id
                    and any(
                        group.group_snapshot_id == item.source_group_snapshot_id
                        for group in sorted_groups
                    )
                ],
            }
        )
    groups = [
        {
            "group_key": group.group_key,
            "group_label": group.group_label,
            "source_table_index": source_snapshot.source_table_index or 0,
            "extraction_status": "loaded",
            "sample_size": group.sample_size,
            "sample_quantity_expression": group.sample_quantity_expression,
            "sample_note": group.sample_note,
            "steps": [],
        }
        for group in sorted_groups
    ]
    return {
        "project_id": source_snapshot.project_id,
        "source_document_path": import_record.source_document_path if import_record else "unknown://source",
        "source_document_name": import_record.source_document_name if import_record else "Source Matrix",
        "source_format": import_record.source_format if import_record else "unknown",
        "capability_status": "supported",
        "generated_at": _utc_now(),
        "selected_table_index": source_snapshot.source_table_index,
        "selected_page_number": None,
        "selected_page_table_index": None,
        "candidate_tables": [],
        "preview_pdf_token": None,
        "rows": rows,
        "groups": groups,
        "warnings": [],
        "blockers": [],
    }


def _resolve_source_preview_payload(
    *,
    source_snapshot: SourceMatrixSnapshot,
    import_record: SourceMatrixImportRecord | None,
) -> dict[str, Any]:
    cached_payload = _normalize_cached_source_preview_payload(import_record)
    if cached_payload is not None:
        return cached_payload
    return _build_source_preview_payload(
        source_snapshot=source_snapshot,
        import_record=import_record,
    )


def _normalize_cached_source_preview_payload(
    import_record: SourceMatrixImportRecord | None,
) -> dict[str, Any] | None:
    if import_record is None or import_record.source_preview_payload is None:
        return None
    payload = import_record.source_preview_payload
    groups = payload.get("groups")
    rows = payload.get("rows")
    if not isinstance(groups, list) or not isinstance(rows, list):
        return None
    try:
        normalized = json.loads(json.dumps(payload, ensure_ascii=False))
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(normalized, dict):
        return None
    normalized.setdefault("source_document_path", import_record.source_document_path)
    normalized.setdefault("source_document_name", import_record.source_document_name)
    normalized.setdefault("source_format", import_record.source_format)
    normalized.setdefault("warnings", [])
    normalized.setdefault("blockers", [])
    normalized.setdefault("candidate_tables", [])
    return normalized


def _has_any_step_tokens(cells: tuple[MatrixEditorSessionCell, ...]) -> bool:
    return any((cell.cell_value or "").strip() for cell in cells)
