"""Pure response and command mappers for Matrix Editor session routes."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_matrix_editor_session_service
from backend.api.lifecycle_errors import (
    lifecycle_guard_not_found,
    lifecycle_readonly_conflict,
)
from backend.api.routes_project_matrix_drafts import (
    ConfirmedMatrixSnapshotResponse,
    _to_confirmed_response,
)
from backend.application.project_lifecycle_write_guard import (
    ProjectLifecycleReadonlyError,
    ProjectLifecycleWriteGuardNotFoundError,
)
from backend.application.matrix_editor_session_service import (
    MatrixEditorSessionActiveChangedError,
    MatrixEditorSessionConfirmCommand,
    MatrixEditorSessionCell,
    MatrixEditorSessionDurationAuthority,
    MatrixEditorSessionDraftConflictError,
    MatrixEditorSessionDraftDiscardCommand,
    MatrixEditorSessionDraftSaveCommand,
    MatrixEditorSessionError,
    MatrixEditorSessionGroup,
    MatrixEditorSessionNotFoundError,
    MatrixEditorSessionRow,
    MatrixEditorSessionService,
)


router = APIRouter(tags=["matrix-editor-session"])



from backend.api.matrix_editor_session_dtos import *

def _to_session_groups(
    groups: list[MatrixEditorSessionGroupRequest],
) -> tuple[MatrixEditorSessionGroup, ...]:
    return tuple(
        MatrixEditorSessionGroup(
            draft_group_id=item.draft_group_id,
            source_group_snapshot_id=item.source_group_snapshot_id,
            group_order=item.group_order,
            group_key=item.group_key,
            group_label=item.group_label,
            is_selected=item.is_selected,
            sample_quantity_expression=item.sample_quantity_expression,
            sample_note=item.sample_note,
        )
        for item in groups
    )


def _to_session_rows(
    rows: list[MatrixEditorSessionRowRequest],
) -> tuple[MatrixEditorSessionRow, ...]:
    return tuple(
        MatrixEditorSessionRow(
            draft_row_id=item.draft_row_id,
            source_row_snapshot_id=item.source_row_snapshot_id,
            row_order=item.row_order,
            test_item=item.test_item,
            source_section=item.source_section,
            method=item.method,
            condition=item.condition,
            requirement=item.requirement,
            day_expression=item.day_expression,
            is_sample_row=item.is_sample_row,
        )
        for item in rows
    )


def _to_session_cells(
    cells: list[MatrixEditorSessionCellRequest],
) -> tuple[MatrixEditorSessionCell, ...]:
    return tuple(
        MatrixEditorSessionCell(
            draft_row_id=item.draft_row_id,
            draft_group_id=item.draft_group_id,
            cell_value=item.cell_value,
        )
        for item in cells
    )


def _to_session_duration_authorities(
    items: list[MatrixEditorSessionDurationAuthorityRequest],
) -> tuple[MatrixEditorSessionDurationAuthority, ...]:
    return tuple(
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
        for item in items
    )
