"""Application service for Matrix Editor temporary session seed/confirm flow."""

from __future__ import annotations

from datetime import datetime
from typing import Callable, Literal

from backend.application.confirmed_matrix_authority_service import (
    ConfirmedMatrixAuthorityService,
)
from backend.application.matrix_import_commit_service import (
    MatrixImportCommitService,
)
from backend.application.matrix_sample_quantity_guard import (
    find_selected_sample_quantity_violations,
    format_sample_quantity_violation_message,
)
from backend.application.matrix_step_quantity_authority_comparison import (
    step_quantity_authority_matches,
)
from backend.application.matrix_revision_flow_service import (
    CreateMatrixRevisionDraftCommand,
    MatrixRevisionFlowConflictError,
    MatrixRevisionFlowService,
)
from backend.application.matrix_fee_pending_rebase_service import (
    DeletePendingRebaseForMatrixDraftCommand,
    RebaseAfterMatrixAutosaveCommand,
)
from backend.application.matrix_fee_rebase_promotion_service import PromoteMatrixFeeRebaseCommand
from backend.application.project_matrix_draft_persistence_service import (
    ProjectMatrixDraftPersistenceService,
)
from backend.application.project_lifecycle_write_guard import (
    LifecycleWriteOperation,
    ProjectLifecycleWriteGuard,
)
from backend.modules.fee_evaluation import load_active_fee_rule_library



from backend.application.matrix_editor_session_contracts import *
from backend.application.matrix_editor_session_projection import (
    _build_editor_draft_from_active,
    _build_editor_draft_from_project_draft,
    _confirm_command_from_save_command,
    _has_any_step_tokens,
    _resolve_source_preview_payload,
)
from backend.application.matrix_editor_session_signature import (
    _build_signature_from_confirmed,
    _build_signature_from_session_payload,
    _has_expected_saved_draft,
    _is_source_lineage_replaced,
    _validate_session_schedule,
    build_project_matrix_draft_payload_signature,
)
from backend.application.matrix_editor_session_publication import (
    MatrixEditorSessionPublicationMixin,
    _NullFeeRebasePromotionService,
    _NullPendingFeeRebaseService,
)
from backend.application.matrix_editor_session_draft_state import (
    MatrixEditorSessionDraftStateMixin,
)

class MatrixEditorSessionService(
    MatrixEditorSessionPublicationMixin,
    MatrixEditorSessionDraftStateMixin,
):
    """Load and publish temporary Matrix Editor sessions."""

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        confirmed_store: ConfirmedStore,
        source_store: SourceStore,
        draft_store: DraftStore,
        draft_persistence_service: ProjectMatrixDraftPersistenceService,
        matrix_import_commit_service: MatrixImportCommitService,
        matrix_revision_flow_service: MatrixRevisionFlowService,
        confirmed_matrix_authority_service: ConfirmedMatrixAuthorityService,
        pending_fee_rebase_service: PendingFeeRebaseService | None = None,
        fee_rebase_promotion_service: FeeRebasePromotionService | None = None,
        fee_rule_version_provider: Callable[[], str] | None = None,
        lifecycle_write_guard: ProjectLifecycleWriteGuard | None = None,
    ) -> None:
        self._projects = project_store
        self._confirmed = confirmed_store
        self._sources = source_store
        self._drafts = draft_store
        self._draft_persistence = draft_persistence_service
        self._matrix_import_commit = matrix_import_commit_service
        self._matrix_revision = matrix_revision_flow_service
        self._confirmed_authority = confirmed_matrix_authority_service
        self._pending_fee_rebase = pending_fee_rebase_service or _NullPendingFeeRebaseService()
        self._fee_rebase_promotion = (
            fee_rebase_promotion_service or _NullFeeRebasePromotionService()
        )
        self._fee_rule_version_provider = (
            fee_rule_version_provider or _active_fee_rule_version_id
        )
        self._lifecycle_write_guard = lifecycle_write_guard

    def get_seed(self, *, project_id: str) -> MatrixEditorSessionSeed:
        """Build one Matrix Editor seed from active authority and source snapshot lineage."""
        self._require_project(project_id)
        active = self._confirmed.get_active_by_project(project_id)
        stale_draft_present = self._has_stale_draft(project_id, active)
        current_draft = (
            self._get_current_editor_draft(active)
            if active is not None
            else self._get_unconfirmed_editor_draft(project_id)
        )
        if active is None and current_draft is None:
            return MatrixEditorSessionSeed(
                project_id=project_id,
                active_confirmed_matrix_id=None,
                active_confirmed_revision=None,
                active_source_import_id=None,
                active_source_snapshot_id=None,
                editor_source_import_id=None,
                editor_source_snapshot_id=None,
                editor_draft=None,
                source_preview_payload=None,
                source_status="not_required",
                source_unavailable_message=None,
                stale_draft_present=stale_draft_present,
            )
        if current_draft is not None:
            editor_draft = _build_editor_draft_from_project_draft(current_draft)
            editor_draft_id = current_draft.record.project_matrix_draft_id
            editor_source_import_id = current_draft.record.source_import_id
            editor_source_snapshot_id = current_draft.record.source_snapshot_id
            draft_status: Literal["missing", "current", "stale"] = "current"
            loaded_source: Literal["authority", "draft"] = "draft"
            draft_updated_at = current_draft.record.updated_at
            saved_payload_signature = build_project_matrix_draft_payload_signature(current_draft)
            schedule_source = current_draft.record
        else:
            assert active is not None
            editor_draft = _build_editor_draft_from_active(active)
            editor_draft_id = None
            editor_source_import_id = active.version.source_import_id
            editor_source_snapshot_id = active.version.source_snapshot_id
            draft_status = "missing"
            loaded_source = "authority"
            draft_updated_at = None
            saved_payload_signature = None
            schedule_source = active.version
        active_confirmed_matrix_id = (
            active.version.confirmed_matrix_id if active is not None else None
        )
        active_confirmed_revision = (
            active.version.confirmed_revision if active is not None else None
        )
        active_source_import_id = active.version.source_import_id if active is not None else None
        active_source_snapshot_id = active.version.source_snapshot_id if active is not None else None
        source_snapshot = (
            self._sources.get_snapshot(editor_source_snapshot_id)
            if editor_source_snapshot_id
            else None
        )
        if source_snapshot is None:
            return MatrixEditorSessionSeed(
                project_id=project_id,
                active_confirmed_matrix_id=active_confirmed_matrix_id,
                active_confirmed_revision=active_confirmed_revision,
                active_source_import_id=active_source_import_id,
                active_source_snapshot_id=active_source_snapshot_id,
                editor_source_import_id=editor_source_import_id,
                editor_source_snapshot_id=editor_source_snapshot_id,
                editor_draft=editor_draft,
                source_preview_payload=None,
                source_status="unavailable",
                source_unavailable_message=SOURCE_UNAVAILABLE_MESSAGE,
                pre_test_buffer_days=schedule_source.pre_test_buffer_days,
                post_test_buffer_days=schedule_source.post_test_buffer_days,
                sample_received_date=schedule_source.sample_received_date,
                planned_test_start_date=schedule_source.planned_test_start_date,
                planned_test_complete_date=schedule_source.planned_test_complete_date,
                estimated_completion_date=schedule_source.estimated_completion_date,
                editor_draft_id=editor_draft_id,
                draft_status=draft_status,
                loaded_source=loaded_source,
                stale_draft_present=stale_draft_present,
                draft_updated_at=draft_updated_at,
                saved_payload_signature=saved_payload_signature,
            )
        import_record = (
            self._sources.get_import(editor_source_import_id)
            if editor_source_import_id
            else None
        )
        source_preview_payload = _resolve_source_preview_payload(
            source_snapshot=source_snapshot,
            import_record=import_record,
        )
        return MatrixEditorSessionSeed(
            project_id=project_id,
            active_confirmed_matrix_id=active_confirmed_matrix_id,
            active_confirmed_revision=active_confirmed_revision,
            active_source_import_id=active_source_import_id,
            active_source_snapshot_id=active_source_snapshot_id,
            editor_source_import_id=editor_source_import_id,
            editor_source_snapshot_id=editor_source_snapshot_id,
            editor_draft=editor_draft,
            source_preview_payload=source_preview_payload,
            source_status="available",
            source_unavailable_message=None,
            pre_test_buffer_days=schedule_source.pre_test_buffer_days,
            post_test_buffer_days=schedule_source.post_test_buffer_days,
            sample_received_date=schedule_source.sample_received_date,
            planned_test_start_date=schedule_source.planned_test_start_date,
            planned_test_complete_date=schedule_source.planned_test_complete_date,
            estimated_completion_date=schedule_source.estimated_completion_date,
            editor_draft_id=editor_draft_id,
            draft_status=draft_status,
            loaded_source=loaded_source,
            stale_draft_present=stale_draft_present,
            draft_updated_at=draft_updated_at,
            saved_payload_signature=saved_payload_signature,
        )

    def save_editor_draft(
        self,
        command: MatrixEditorSessionDraftSaveCommand,
    ) -> MatrixEditorSessionDraftSaveResult:
        """Autosave one Matrix Editor payload into the current non-authority draft."""
        self._require_write_allowed(
            command.project_id,
            LifecycleWriteOperation.MATRIX_EDITOR_DRAFT_SAVE,
        )
        self._require_project(command.project_id)
        active = self._confirmed.get_active_by_project(command.project_id)
        if active is None:
            raise MatrixEditorSessionError(
                "Active confirmed matrix is required before Matrix autosave."
            )
        expected_command = _confirm_command_from_save_command(command, confirmed_by="autosave")
        self._validate_expected_active(expected_command, active)
        draft_record = self._get_current_editor_draft_record(active)
        if draft_record is None:
            try:
                created = self._matrix_revision.create_revision_draft(
                    CreateMatrixRevisionDraftCommand(project_id=command.project_id)
                )
            except MatrixRevisionFlowConflictError:
                draft_record = self._get_current_editor_draft_record(active)
                if draft_record is None:
                    raise
            else:
                draft_record = created.record
        saved = self._save_payload_to_draft(
            expected_command,
            draft_record.project_matrix_draft_id,
        )
        saved_payload_signature = build_project_matrix_draft_payload_signature(saved)
        fee_rebase_result = self._pending_fee_rebase.rebase_after_matrix_autosave(
            RebaseAfterMatrixAutosaveCommand(
                project_id=command.project_id,
                active_confirmed_matrix_id=active.version.confirmed_matrix_id,
                active_confirmed_revision=active.version.confirmed_revision,
                saved_matrix_draft=saved,
                saved_payload_signature=saved_payload_signature,
                fee_rule_version_id=self._fee_rule_version_provider(),
                generation=_generation_from_updated_at(saved.record.updated_at),
            )
        )
        return MatrixEditorSessionDraftSaveResult(
            editor_draft_id=saved.record.project_matrix_draft_id,
            draft_status="current",
            draft_updated_at=saved.record.updated_at,
            saved_payload_signature=saved_payload_signature,
            active_confirmed_matrix_id=active.version.confirmed_matrix_id,
            active_confirmed_revision=active.version.confirmed_revision,
            fee_rebase_status=fee_rebase_result.status,
            fee_rebase_summary=fee_rebase_result.summary,
            fee_rebase_error=fee_rebase_result.error,
        )

    def discard_editor_draft(
        self,
        command: MatrixEditorSessionDraftDiscardCommand,
    ) -> MatrixEditorSessionDraftDiscardResult:
        """Discard the current Matrix Editor non-authority draft."""
        self._require_write_allowed(
            command.project_id,
            LifecycleWriteOperation.MATRIX_EDITOR_DRAFT_DISCARD,
        )
        self._require_project(command.project_id)
        active = self._confirmed.get_active_by_project(command.project_id)
        expected_draft_id = (command.expected_editor_draft_id or "").strip()
        if expected_draft_id:
            draft = self._drafts.get(expected_draft_id)
            if draft is not None and (
                draft.record.project_id != command.project_id
                or draft.record.status != ProjectMatrixDraftStatus.DRAFT
            ):
                raise MatrixEditorSessionDraftConflictError(
                    "Matrix draft changed before cancel. Reload the latest Matrix."
                )
        elif active is not None:
            draft = self._get_current_editor_draft(active)
        else:
            draft = self._get_unconfirmed_editor_draft(command.project_id)
        if draft is None:
            return MatrixEditorSessionDraftDiscardResult(
                discarded=False,
                active_confirmed_matrix_id=(
                    active.version.confirmed_matrix_id if active is not None else None
                ),
                active_confirmed_revision=(
                    active.version.confirmed_revision if active is not None else None
                ),
            )
        self._validate_expected_draft_tokens(
            draft=draft,
            expected_editor_draft_id=command.expected_editor_draft_id,
            expected_saved_payload_signature=command.expected_saved_payload_signature,
        )
        if self._is_draft_referenced_by_confirmed_authority(
            command.project_id,
            draft.record.project_matrix_draft_id,
        ):
            raise MatrixEditorSessionDraftConflictError(
                "Matrix draft is referenced by confirmed authority and cannot be discarded."
            )
        try:
            self._pending_fee_rebase.delete_for_matrix_draft(
                DeletePendingRebaseForMatrixDraftCommand(
                    project_matrix_draft_id=draft.record.project_matrix_draft_id
                )
            )
        except Exception as exc:  # noqa: BLE001 - operator-facing cancel failure.
            raise MatrixEditorSessionDraftConflictError(
                "Matrix draft pending Fee rebase cleanup failed. "
                "Reload Matrix Editor before continuing."
            ) from exc
        discarded = self._drafts.delete(draft.record.project_matrix_draft_id)
        if discarded:
            try:
                self._pending_fee_rebase.delete_for_matrix_draft(
                    DeletePendingRebaseForMatrixDraftCommand(
                        project_matrix_draft_id=draft.record.project_matrix_draft_id
                    )
                )
            except Exception as exc:  # noqa: BLE001 - post-delete race cleanup.
                raise MatrixEditorSessionDraftConflictError(
                    "Matrix draft pending Fee rebase cleanup failed after discard. "
                    "Reload Matrix Editor before continuing."
                ) from exc
        return MatrixEditorSessionDraftDiscardResult(
            discarded=discarded,
            active_confirmed_matrix_id=(
                active.version.confirmed_matrix_id if active is not None else None
            ),
            active_confirmed_revision=(
                active.version.confirmed_revision if active is not None else None
            ),
        )

    def confirm_session(
        self,
        command: MatrixEditorSessionConfirmCommand,
    ) -> MatrixEditorSessionConfirmResult:
        """Confirm one temporary Matrix Editor session into active authority."""
        self._require_write_allowed(
            command.project_id,
            LifecycleWriteOperation.MATRIX_EDITOR_CONFIRM,
        )
        self._require_project(command.project_id)
        confirmed_by = command.confirmed_by.strip()
        if not confirmed_by:
            raise MatrixEditorSessionError("confirmed_by is required.")
        active = self._confirmed.get_active_by_project(command.project_id)
        self._validate_expected_active(command, active)
        if len(command.groups) == 0:
            raise MatrixEditorSessionError("At least one group is required.")
        if len(command.rows) == 0:
            raise MatrixEditorSessionError("At least one row is required.")
        selected_group_keys = tuple(
            group.group_key.strip()
            for group in command.groups
            if group.is_selected and group.group_key.strip()
        )
        if len(selected_group_keys) == 0:
            raise MatrixEditorSessionError("At least one selected group is required.")
        sample_violations = find_selected_sample_quantity_violations(command.groups)
        if sample_violations:
            raise MatrixEditorSessionError(
                format_sample_quantity_violation_message(sample_violations)
            )
        if not _has_any_step_tokens(command.cells):
            raise MatrixEditorSessionError("At least one step token is required.")
        _validate_session_schedule(command)
        payload_signature = _build_signature_from_session_payload(command)
        if active is not None:
            active_signature = _build_signature_from_confirmed(active)
            if payload_signature == active_signature:
                if _has_expected_saved_draft(command):
                    saved_draft = self._load_expected_saved_draft(command, active)
                    if not step_quantity_authority_matches(saved_draft, active):
                        if payload_signature != (
                            command.expected_saved_payload_signature or ""
                        ).strip():
                            raise MatrixEditorSessionDraftConflictError(
                                "Confirm payload differs from the saved Matrix draft. Save again before confirming."
                            )
                        return self._publish_saved_revision_result(
                            project_id=command.project_id,
                            saved_draft=saved_draft,
                            active=active,
                            confirmed_by=confirmed_by,
                        )
                return MatrixEditorSessionConfirmResult(
                    publish_status="no_change",
                    message="No Matrix changes to confirm.",
                    confirmed_snapshot=None,
                )
            if _is_source_lineage_replaced(command, active):
                confirmed = self._publish_with_source_replacement(
                    command=command,
                    active=active,
                    confirmed_by=confirmed_by,
                )
                return MatrixEditorSessionConfirmResult(
                    publish_status="published",
                    message=f"Matrix confirmed (v{confirmed.version.confirmed_revision}).",
                    confirmed_snapshot=confirmed,
                )
            saved_draft = self._load_expected_saved_draft(command, active)
            if payload_signature != (command.expected_saved_payload_signature or "").strip():
                raise MatrixEditorSessionDraftConflictError(
                    "Confirm payload differs from the saved Matrix draft. Save again before confirming."
                )
            return self._publish_saved_revision_result(
                project_id=command.project_id,
                saved_draft=saved_draft,
                active=active,
                confirmed_by=confirmed_by,
            )
        confirmed = self._publish_as_first_authority(command, selected_group_keys, confirmed_by)
        promotion = self._initialize_fee_after_first_matrix_confirm(
            project_id=command.project_id,
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



def _active_fee_rule_version_id() -> str:
    return load_active_fee_rule_library().version.version_id


_build_signature_from_project_draft = build_project_matrix_draft_payload_signature


def _generation_from_updated_at(updated_at: str) -> int:
    value = updated_at.strip()
    return int(datetime.fromisoformat(value).timestamp() * 1_000_000)
