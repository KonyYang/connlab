"""Confirmed Matrix snapshot construction for Matrix Editor."""

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
from backend.application.matrix_revision_snapshot_builder import (
    build_confirmed_duration_authorities,
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
    MatrixEditorSessionSeed,
    MatrixEditorSessionConfirmCommand,
    MatrixEditorSessionDraftSaveCommand,
    MatrixEditorSessionDraftSaveResult,
    MatrixEditorSessionDraftDiscardCommand,
    MatrixEditorSessionDraftDiscardResult,
    MatrixEditorSessionConfirmResult,
)

def _build_confirmed_snapshot_from_session_draft(
    *,
    draft: ProjectMatrixDraftSnapshot,
    confirmed_by: str,
    confirmed_revision: int,
    source_import_id: str,
    source_snapshot_id: str,
) -> ConfirmedMatrixSnapshot:
    confirmed_matrix_id = f"cmv-{uuid4().hex}"
    confirmed_at = _utc_now()
    selected_groups = tuple(group for group in draft.groups if bool(group.is_selected))
    if not selected_groups:
        raise MatrixEditorSessionError(
            "At least one selected group is required for confirmation."
        )
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id=confirmed_matrix_id,
        project_id=draft.record.project_id,
        project_matrix_draft_id=draft.record.project_matrix_draft_id,
        source_import_id=source_import_id,
        source_snapshot_id=source_snapshot_id,
        confirmed_revision=confirmed_revision,
        is_active_authority=True,
        status=ConfirmedMatrixStatus.CONFIRMED,
        confirmed_by=confirmed_by,
        confirmed_at=confirmed_at,
        pre_test_buffer_days=_normalize_optional_text(draft.record.pre_test_buffer_days),
        post_test_buffer_days=_normalize_optional_text(draft.record.post_test_buffer_days),
        sample_received_date=_normalize_optional_text(draft.record.sample_received_date),
        planned_test_start_date=_normalize_optional_text(draft.record.planned_test_start_date),
        planned_test_complete_date=_normalize_optional_text(
            draft.record.planned_test_complete_date
        ),
        estimated_completion_date=_normalize_optional_text(draft.record.estimated_completion_date),
    )
    sorted_groups = sorted(selected_groups, key=lambda item: item.group_order)
    groups: list[ConfirmedMatrixGroup] = []
    confirmed_group_id_by_draft_group: dict[str, str] = {}
    for index, group in enumerate(sorted_groups, start=1):
        confirmed_group_id = f"cmg-{uuid4().hex}"
        confirmed_group_id_by_draft_group[group.draft_group_id] = confirmed_group_id
        groups.append(
            ConfirmedMatrixGroup(
                confirmed_group_id=confirmed_group_id,
                confirmed_matrix_id=confirmed_matrix_id,
                draft_group_id=group.draft_group_id,
                source_group_snapshot_id=group.source_group_snapshot_id,
                group_order=index,
                group_key=group.group_key.strip(),
                group_label=_normalize_group_label(
                    group.group_label, fallback=str(index)
                ),
                sample_quantity_expression=(group.sample_quantity_expression or "").strip(),
                sample_note=_normalize_optional_text(group.sample_note),
            )
        )
    non_sample_rows = sorted(
        (row for row in draft.rows if not bool(row.is_sample_row)),
        key=lambda item: item.row_order,
    )
    rows: list[ConfirmedMatrixRow] = []
    confirmed_row_id_by_draft_row: dict[str, str] = {}
    for index, row in enumerate(non_sample_rows, start=1):
        confirmed_row_id = f"cmr-{uuid4().hex}"
        confirmed_row_id_by_draft_row[row.draft_row_id] = confirmed_row_id
        rows.append(
            ConfirmedMatrixRow(
                confirmed_row_id=confirmed_row_id,
                confirmed_matrix_id=confirmed_matrix_id,
                draft_row_id=row.draft_row_id,
                source_row_snapshot_id=row.source_row_snapshot_id,
                row_order=index,
                test_item=row.test_item,
                source_section=_normalize_optional_text(row.source_section),
                method=_normalize_optional_text(row.method),
                condition=_normalize_optional_text(row.condition),
                requirement=_normalize_optional_text(row.requirement),
                day_expression=_normalize_optional_text(row.day_expression),
            )
        )
    cells: list[ConfirmedMatrixCell] = []
    seen_identity: set[tuple[str, str]] = set()
    for cell in draft.cells:
        confirmed_group_id = confirmed_group_id_by_draft_group.get(cell.draft_group_id)
        confirmed_row_id = confirmed_row_id_by_draft_row.get(cell.draft_row_id)
        if confirmed_group_id is None or confirmed_row_id is None:
            continue
        cell_value = cell.cell_value.strip()
        if not cell_value:
            continue
        identity = (confirmed_row_id, confirmed_group_id)
        if identity in seen_identity:
            continue
        seen_identity.add(identity)
        cells.append(
            ConfirmedMatrixCell(
                confirmed_cell_id=f"cmc-{uuid4().hex}",
                confirmed_matrix_id=confirmed_matrix_id,
                confirmed_row_id=confirmed_row_id,
                confirmed_group_id=confirmed_group_id,
                draft_row_id=cell.draft_row_id,
                draft_group_id=cell.draft_group_id,
                cell_value=cell_value,
            )
        )
    return ConfirmedMatrixSnapshot(
        version=version,
        groups=tuple(groups),
        rows=tuple(rows),
        cells=tuple(cells),
        step_quantities=tuple(
            build_confirmed_step_quantities(
                draft=draft,
                confirmed_matrix_id=confirmed_matrix_id,
                confirmed_at=confirmed_at,
                confirmed_group_id_by_draft_group=confirmed_group_id_by_draft_group,
                confirmed_row_id_by_draft_row=confirmed_row_id_by_draft_row,
            )
        ),
        duration_authorities=build_confirmed_duration_authorities(
            draft=draft,
            confirmed_matrix_id=confirmed_matrix_id,
            confirmed_at=confirmed_at,
            confirmed_group_id_by_draft_group=confirmed_group_id_by_draft_group,
            confirmed_row_id_by_draft_row=confirmed_row_id_by_draft_row,
        ),
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _normalize_group_label(value: str | None, *, fallback: str) -> str:
    text = (value or "").strip()
    if not text:
        return fallback
    normalized = text
    if len(text) >= 5 and text[:5].lower() == "group":
        normalized = text[5:].lstrip(" _-")
    normalized = normalized.strip()
    return normalized or fallback


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
