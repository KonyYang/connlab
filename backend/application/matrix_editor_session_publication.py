"""Publication mixin for Matrix Editor sessions."""

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
    MatrixEditorSessionSeed,
    MatrixEditorSessionConfirmCommand,
    MatrixEditorSessionDraftSaveCommand,
    MatrixEditorSessionDraftSaveResult,
    MatrixEditorSessionDraftDiscardCommand,
    MatrixEditorSessionDraftDiscardResult,
    MatrixEditorSessionConfirmResult,
)
from backend.application.matrix_editor_confirmed_snapshot_builder import (
    _build_confirmed_snapshot_from_session_draft,
)
from backend.application.matrix_editor_session_signature import (
    _build_manual_preview_payload,
    build_project_matrix_draft_payload_signature,
)

class MatrixEditorSessionPublicationMixin:
    def _initialize_fee_after_first_matrix_confirm(
        self,
        *,
        project_id: str,
        confirmed: ConfirmedMatrixSnapshot,
    ) -> MatrixFeeRebasePromotionResult:
        try:
            return self._fee_rebase_promotion.initialize_after_first_matrix_confirm(
                project_id=project_id,
                new_confirmed_matrix=confirmed,
                fee_rule_version_id=self._fee_rule_version_provider(),
            )
        except Exception as exc:  # noqa: BLE001 - non-fatal Matrix Confirm hook.
            return MatrixFeeRebasePromotionResult(
                status="failed",
                error=f"Fee default promotion failed: {exc}",
            )

    def _promote_fee_rebase_after_matrix_confirm(
        self,
        *,
        project_id: str,
        saved_draft: ProjectMatrixDraftSnapshot,
        previous_active: ConfirmedMatrixSnapshot,
        confirmed: ConfirmedMatrixSnapshot,
    ) -> MatrixFeeRebasePromotionResult:
        try:
            return self._fee_rebase_promotion.promote_after_matrix_confirm(
                PromoteMatrixFeeRebaseCommand(
                    project_id=project_id,
                    saved_matrix_draft=saved_draft,
                    saved_matrix_draft_payload_signature=(
                        build_project_matrix_draft_payload_signature(saved_draft)
                    ),
                    previous_confirmed_matrix=previous_active,
                    new_confirmed_matrix=confirmed,
                    fee_rule_version_id=self._fee_rule_version_provider(),
                )
            )
        except Exception as exc:  # noqa: BLE001 - non-fatal Matrix Confirm hook.
            return MatrixFeeRebasePromotionResult(
                status="failed",
                error=f"Fee rebase promotion failed: {exc}",
            )

    def _publish_saved_revision_result(
        self,
        *,
        project_id: str,
        saved_draft: ProjectMatrixDraftSnapshot,
        active: ConfirmedMatrixSnapshot,
        confirmed_by: str,
    ) -> MatrixEditorSessionConfirmResult:
        confirmed = self._publish_saved_revision(
            draft=saved_draft,
            active=active,
            confirmed_by=confirmed_by,
        )
        promotion = self._promote_fee_rebase_after_matrix_confirm(
            project_id=project_id,
            saved_draft=saved_draft,
            previous_active=active,
            confirmed=confirmed,
        )
        return MatrixEditorSessionConfirmResult(
            publish_status="published",
            message=f"Matrix confirmed (v{confirmed.version.confirmed_revision}).",
            confirmed_snapshot=confirmed,
            fee_rebase_promotion_status=promotion.status,
            fee_rebase_promotion_summary=promotion.summary,
            fee_rebase_promotion_error=promotion.error,
        )

    def _publish_saved_revision(
        self,
        *,
        draft: ProjectMatrixDraftSnapshot,
        active: ConfirmedMatrixSnapshot,
        confirmed_by: str,
    ) -> ConfirmedMatrixSnapshot:
        revision_snapshot = _build_confirmed_snapshot_from_session_draft(
            draft=draft,
            confirmed_by=confirmed_by,
            confirmed_revision=active.version.confirmed_revision + 1,
            source_import_id=active.version.source_import_id,
            source_snapshot_id=active.version.source_snapshot_id,
        )
        try:
            return self._confirmed.supersede_active_and_create_snapshot(
                previous_active_confirmed_matrix_id=active.version.confirmed_matrix_id,
                snapshot=revision_snapshot,
                superseded_reason="Matrix Editor saved draft confirm.",
            )
        except LookupError as exc:
            raise MatrixEditorSessionActiveChangedError(
                "Matrix was updated. Reload the latest Matrix to continue."
            ) from exc

    def _publish_as_revision(
        self,
        command: MatrixEditorSessionConfirmCommand,
        active: ConfirmedMatrixSnapshot,
        confirmed_by: str,
    ) -> ConfirmedMatrixSnapshot:
        draft_record = self._drafts.get_by_project_and_base_confirmed_matrix(
            command.project_id,
            active.version.confirmed_matrix_id,
        )
        if draft_record is None:
            try:
                created = self._matrix_revision.create_revision_draft(
                    CreateMatrixRevisionDraftCommand(project_id=command.project_id)
                )
            except MatrixRevisionFlowConflictError as exc:
                raise MatrixEditorSessionActiveChangedError(
                    "Matrix was updated. Reload the latest Matrix to continue."
                ) from exc
            draft_id = created.record.project_matrix_draft_id
        else:
            draft_id = draft_record.project_matrix_draft_id
        saved_snapshot = self._save_payload_to_draft(command, draft_id)
        revision_snapshot = _build_confirmed_snapshot_from_session_draft(
            draft=saved_snapshot,
            confirmed_by=confirmed_by,
            confirmed_revision=active.version.confirmed_revision + 1,
            source_import_id=active.version.source_import_id,
            source_snapshot_id=active.version.source_snapshot_id,
        )
        try:
            return self._confirmed.supersede_active_and_create_snapshot(
                previous_active_confirmed_matrix_id=active.version.confirmed_matrix_id,
                snapshot=revision_snapshot,
                superseded_reason="Matrix Editor session confirm.",
            )
        except LookupError as exc:
            raise MatrixEditorSessionActiveChangedError(
                "Matrix was updated. Reload the latest Matrix to continue."
            ) from exc

    def _publish_with_source_replacement(
        self,
        *,
        command: MatrixEditorSessionConfirmCommand,
        active: ConfirmedMatrixSnapshot,
        confirmed_by: str,
    ) -> ConfirmedMatrixSnapshot:
        source_import_id = (command.source_import_id or "").strip()
        source_snapshot_id = (command.source_snapshot_id or "").strip()
        if not source_import_id or not source_snapshot_id:
            raise MatrixEditorSessionError(
                "Source matrix lineage is required after changing source."
            )
        draft_record = self._drafts.get_by_project_and_source_import(
            command.project_id,
            source_import_id,
        )
        if draft_record is None:
            raise MatrixEditorSessionError(
                "Source matrix draft is not available. Re-import and select groups again."
            )
        saved_snapshot = self._save_payload_to_draft(
            command,
            draft_record.project_matrix_draft_id,
        )
        replacement_snapshot = _build_confirmed_snapshot_from_session_draft(
            draft=saved_snapshot,
            confirmed_by=confirmed_by,
            confirmed_revision=active.version.confirmed_revision + 1,
            source_import_id=source_import_id,
            source_snapshot_id=source_snapshot_id,
        )
        try:
            return self._confirmed.supersede_active_and_create_snapshot(
                previous_active_confirmed_matrix_id=active.version.confirmed_matrix_id,
                snapshot=replacement_snapshot,
                superseded_reason="Matrix Editor source replacement confirm.",
            )
        except LookupError as exc:
            raise MatrixEditorSessionActiveChangedError(
                "Matrix was updated. Reload the latest Matrix to continue."
            ) from exc

    def _publish_as_first_authority(
        self,
        command: MatrixEditorSessionConfirmCommand,
        selected_group_keys: tuple[str, ...],
        confirmed_by: str,
    ) -> ConfirmedMatrixSnapshot:
        preview_payload = _build_manual_preview_payload(command)
        source_document_path = (
            (command.source_document_path or "").strip() or "manual://matrix-editor"
        )
        source_document_name = (
            (command.source_document_name or "").strip() or "Matrix Editor Manual Draft"
        )
        source_format = (command.source_format or "").strip() or "manual"
        try:
            committed = self._matrix_import_commit.commit(
                MatrixImportCommitCommand(
                    project_id=command.project_id,
                    source_document_path=source_document_path,
                    source_document_name=source_document_name,
                    source_format=source_format,
                    preview_payload=preview_payload,
                    selected_group_keys=selected_group_keys,
                )
            )
        except (MatrixImportCommitError, MatrixImportCommitNotFoundError) as exc:
            raise MatrixEditorSessionError(str(exc)) from exc
        draft_id = committed.project_matrix_draft.record.project_matrix_draft_id
        self._save_payload_to_draft(command, draft_id)
        try:
            return self._confirmed_authority.confirm_draft(
                ConfirmProjectMatrixDraftCommand(
                    project_id=command.project_id,
                    project_matrix_draft_id=draft_id,
                    confirmed_by=confirmed_by,
                )
            )
        except (
            ConfirmedMatrixAuthorityError,
            ConfirmedMatrixAuthorityConflictError,
            ConfirmedMatrixAuthorityNotFoundError,
        ) as exc:
            raise MatrixEditorSessionError(str(exc)) from exc


class _NullPendingFeeRebaseService:
    """Default no-op pending rebase hook for tests and narrow callers."""

    def rebase_after_matrix_autosave(
        self, command: RebaseAfterMatrixAutosaveCommand
    ) -> MatrixFeePendingRebaseResult:
        return MatrixFeePendingRebaseResult(status="not_required")

    def delete_for_matrix_draft(
        self, command: DeletePendingRebaseForMatrixDraftCommand
    ) -> object:
        return None


class _NullFeeRebasePromotionService:
    """Default no-op Matrix Confirm promotion hook for narrow callers."""

    def initialize_after_first_matrix_confirm(
        self,
        *,
        project_id: str,
        new_confirmed_matrix: ConfirmedMatrixSnapshot,
        fee_rule_version_id: str,
    ) -> MatrixFeeRebasePromotionResult:
        return MatrixFeeRebasePromotionResult(status="not_required")
    def promote_after_matrix_confirm(
        self, command: PromoteMatrixFeeRebaseCommand
    ) -> MatrixFeeRebasePromotionResult:
        return MatrixFeeRebasePromotionResult(status="not_required")
