"""Draft-state mixin for Matrix Editor sessions."""

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
    ProjectMatrixDurationAuthorityInput,
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
from backend.application.matrix_editor_confirmed_snapshot_builder import (
    _normalize_group_label,
)
from backend.application.matrix_editor_session_signature import (
    _is_same_source_lineage,
    build_project_matrix_draft_payload_signature,
)


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))


class MatrixEditorSessionDraftStateMixin:
    def _get_current_editor_draft_record(
        self,
        active: ConfirmedMatrixSnapshot,
    ) -> ProjectMatrixDraftRecord | None:
        records = [
            record
            for record in self._drafts.list_by_project(active.version.project_id)
            if (
                record.base_confirmed_matrix_id == active.version.confirmed_matrix_id
                or (
                    record.base_confirmed_matrix_id is None
                    and record.source_import_id != active.version.source_import_id
                    and _parse_timestamp(record.updated_at)
                    > _parse_timestamp(active.version.confirmed_at)
                )
            )
            and record.status == ProjectMatrixDraftStatus.DRAFT
        ]
        if not records:
            return None
        return sorted(
            records,
            key=lambda record: (record.updated_at, record.project_matrix_draft_id),
            reverse=True,
        )[0]

    def _get_current_editor_draft(
        self,
        active: ConfirmedMatrixSnapshot,
    ) -> ProjectMatrixDraftSnapshot | None:
        record = self._get_current_editor_draft_record(active)
        if record is None:
            return None
        draft = self._drafts.get(record.project_matrix_draft_id)
        if draft is None or draft.record.project_id != active.version.project_id:
            return None
        return draft
    def _get_unconfirmed_editor_draft(
        self,
        project_id: str,
    ) -> ProjectMatrixDraftSnapshot | None:
        records = [
            record
            for record in self._drafts.list_by_project(project_id)
            if record.base_confirmed_matrix_id is None
            and record.status == ProjectMatrixDraftStatus.DRAFT
        ]
        if not records:
            return None
        record = sorted(
            records,
            key=lambda item: (item.updated_at, item.project_matrix_draft_id),
            reverse=True,
        )[0]
        draft = self._drafts.get(record.project_matrix_draft_id)
        if draft is None or draft.record.project_id != project_id:
            return None
        return draft

    def _has_stale_draft(
        self,
        project_id: str,
        active: ConfirmedMatrixSnapshot | None,
    ) -> bool:
        active_id = active.version.confirmed_matrix_id if active is not None else None
        return any(
            record.base_confirmed_matrix_id is not None
            and record.base_confirmed_matrix_id != active_id
            and record.status == ProjectMatrixDraftStatus.DRAFT
            for record in self._drafts.list_by_project(project_id)
        )

    def _load_expected_saved_draft(
        self,
        command: MatrixEditorSessionConfirmCommand,
        active: ConfirmedMatrixSnapshot,
    ) -> ProjectMatrixDraftSnapshot:
        expected_id = (command.expected_editor_draft_id or "").strip()
        expected_signature = (command.expected_saved_payload_signature or "").strip()
        if not expected_id or not expected_signature:
            raise MatrixEditorSessionDraftConflictError(
                "Save Matrix changes before confirming."
            )
        draft = self._drafts.get(expected_id)
        if draft is None:
            raise MatrixEditorSessionDraftConflictError(
                "Saved Matrix draft is no longer available. Reload the latest Matrix."
            )
        if draft.record.project_id != command.project_id:
            raise MatrixEditorSessionDraftConflictError(
                "Saved Matrix draft project lineage mismatch."
            )
        if draft.record.base_confirmed_matrix_id != active.version.confirmed_matrix_id:
            raise MatrixEditorSessionDraftConflictError(
                "Saved Matrix draft is stale relative to current active Matrix."
            )
        if build_project_matrix_draft_payload_signature(draft) != expected_signature:
            raise MatrixEditorSessionDraftConflictError(
                "Saved Matrix draft changed. Reload or save again before confirming."
            )
        return draft

    def _validate_expected_draft_tokens(
        self,
        *,
        draft: ProjectMatrixDraftSnapshot,
        expected_editor_draft_id: str | None,
        expected_saved_payload_signature: str | None,
    ) -> None:
        expected_id = (expected_editor_draft_id or "").strip()
        expected_signature = (expected_saved_payload_signature or "").strip()
        if expected_id and expected_id != draft.record.project_matrix_draft_id:
            raise MatrixEditorSessionDraftConflictError(
                "Matrix draft changed before cancel. Reload the latest Matrix."
            )
        if expected_signature and build_project_matrix_draft_payload_signature(draft) != expected_signature:
            raise MatrixEditorSessionDraftConflictError(
                "Matrix draft changed before cancel. Reload the latest Matrix."
            )

    def _is_draft_referenced_by_confirmed_authority(
        self,
        project_id: str,
        project_matrix_draft_id: str,
    ) -> bool:
        return any(
            snapshot.version.project_matrix_draft_id == project_matrix_draft_id
            for snapshot in self._confirmed.list_by_project(project_id)
        )

    def _save_payload_to_draft(
        self,
        command: MatrixEditorSessionConfirmCommand,
        draft_id: str,
    ) -> ProjectMatrixDraftSnapshot:
        try:
            return self._draft_persistence.update_draft(
                UpdateProjectMatrixDraftCommand(
                    project_id=command.project_id,
                    project_matrix_draft_id=draft_id,
                    groups=tuple(
                        ProjectMatrixDraftGroupInput(
                            draft_group_id=group.draft_group_id,
                            source_group_snapshot_id=group.source_group_snapshot_id,
                            group_order=group.group_order,
                            group_key=group.group_key,
                            group_label=_normalize_group_label(
                                group.group_label, fallback=str(group.group_order)
                            ),
                            is_selected=group.is_selected,
                            sample_quantity_expression=group.sample_quantity_expression,
                            sample_note=group.sample_note,
                        )
                        for group in command.groups
                    ),
                    rows=tuple(
                        ProjectMatrixDraftRowInput(
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
                        for row in command.rows
                    ),
                    cells=tuple(
                        ProjectMatrixDraftCellInput(
                            draft_row_id=cell.draft_row_id,
                            draft_group_id=cell.draft_group_id,
                            cell_value=cell.cell_value,
                        )
                        for cell in command.cells
                    ),
                    duration_authorities_present=True,
                    duration_authorities=tuple(
                        ProjectMatrixDurationAuthorityInput(
                            draft_duration_authority_id=(
                                item.draft_duration_authority_id
                            ),
                            draft_group_id=item.draft_group_id,
                            draft_row_id=item.draft_row_id,
                            step_sequence=item.step_sequence,
                            step_suffix_note=item.step_suffix_note,
                            duration_value=item.duration_value,
                            duration_unit=item.duration_unit,
                            source_kind=item.source_kind,
                            source_field=item.source_field,
                            source_import_id=item.source_import_id,
                            source_fingerprint=item.source_fingerprint,
                            lineage_fingerprint=item.lineage_fingerprint,
                            authority_revision=item.authority_revision,
                        )
                        for item in command.duration_authorities
                    ),
                    pre_test_buffer_days=command.pre_test_buffer_days,
                    post_test_buffer_days=command.post_test_buffer_days,
                    sample_received_date=command.sample_received_date,
                    planned_test_start_date=command.planned_test_start_date,
                    planned_test_complete_date=command.planned_test_complete_date,
                    estimated_completion_date=command.estimated_completion_date,
                )
            )
        except (
            ProjectMatrixDraftPersistenceError,
            ProjectMatrixDraftPersistenceNotFoundError,
            LookupError,
        ) as exc:
            raise MatrixEditorSessionError(str(exc)) from exc

    def _validate_expected_active(
        self,
        command: MatrixEditorSessionConfirmCommand,
        active: ConfirmedMatrixSnapshot | None,
    ) -> None:
        expected_active_id = (command.expected_active_confirmed_matrix_id or "").strip()
        if not expected_active_id:
            if active is not None:
                raise MatrixEditorSessionActiveChangedError(
                    "Matrix was updated. Reload the latest Matrix to continue."
                )
            return
        if active is None:
            raise MatrixEditorSessionActiveChangedError(
                "Matrix was updated. Reload the latest Matrix to continue."
            )
        if active.version.confirmed_matrix_id != expected_active_id:
            if _is_same_source_lineage(command, active):
                return
            raise MatrixEditorSessionActiveChangedError(
                "Matrix was updated. Reload the latest Matrix to continue."
            )
        if (
            command.expected_active_confirmed_revision is not None
            and active.version.confirmed_revision
            != command.expected_active_confirmed_revision
        ):
            if _is_same_source_lineage(command, active):
                return
            raise MatrixEditorSessionActiveChangedError(
                "Matrix was updated. Reload the latest Matrix to continue."
            )

    def _require_project(self, project_id: str) -> None:
        project = self._projects.get(project_id)
        if project is None:
            raise MatrixEditorSessionNotFoundError(f"Project not found: {project_id}")

    def _require_write_allowed(
        self,
        project_id: str,
        operation: LifecycleWriteOperation,
    ) -> None:
        if self._lifecycle_write_guard is not None:
            self._lifecycle_write_guard.require_write_allowed(project_id, operation)
