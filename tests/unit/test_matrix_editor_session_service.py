from __future__ import annotations

from datetime import date

import pytest

from backend.application.matrix_editor_session_service import (
    MatrixEditorSessionActiveChangedError,
    MatrixEditorSessionCell,
    MatrixEditorSessionConfirmCommand,
    MatrixEditorSessionDraftDiscardCommand,
    MatrixEditorSessionDraftConflictError,
    MatrixEditorSessionDraftSaveCommand,
    MatrixEditorSessionError,
    MatrixEditorSessionGroup,
    MatrixEditorSessionRow,
    MatrixEditorSessionService,
    SOURCE_UNAVAILABLE_MESSAGE,
    _build_signature_from_project_draft,
)
from backend.application.matrix_fee_draft_rebase_service import MatrixFeeRebaseSummary
from backend.application.matrix_fee_pending_rebase_service import (
    MatrixFeePendingRebaseResult,
)
from backend.application.matrix_fee_rebase_promotion_service import (
    MatrixFeeRebasePromotionResult,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    Project,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    ProjectStatus,
    SourceMatrixImportRecord,
    SourceMatrixImportStatus,
    SourceMatrixCellSnapshot,
    SourceMatrixGroupSnapshot,
    SourceMatrixRowSnapshot,
    SourceMatrixSnapshot,
)


def test_get_seed_when_source_snapshot_missing_returns_unavailable_message() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    seed = service.get_seed(project_id="P1")
    assert seed.active_confirmed_matrix_id == "cmv-1"
    assert seed.editor_draft is not None
    assert seed.source_status == "unavailable"
    assert seed.source_unavailable_message == SOURCE_UNAVAILABLE_MESSAGE
    assert seed.source_preview_payload is None


def test_get_seed_rebuilt_source_preview_payload_preserves_row_mcr() -> None:
    active = _build_active_snapshot()
    source_snapshot = SourceMatrixSnapshot(
        snapshot_id="sms-1",
        import_id="smi-1",
        project_id="P1",
        source_table_index=1,
        rows=(
            SourceMatrixRowSnapshot(
                row_snapshot_id="sr-1",
                row_order=1,
                source_row_index=3,
                test_item="Contact Resistance (Low Level)",
                source_section="6.1",
                method="EIA-364-23D",
                condition="20mV max, 100mA max",
                requirement="Initial <= 0.25 milliohms",
            ),
        ),
        groups=(
            SourceMatrixGroupSnapshot(
                group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                sample_quantity_expression="5",
            ),
        ),
        cells=(
            SourceMatrixCellSnapshot(
                cell_snapshot_id="sc-1",
                row_snapshot_id="sr-1",
                group_snapshot_id="sg-1",
                cell_value="1",
            ),
        ),
        created_at="2026-05-27T00:00:00Z",
    )
    service = _service(active=active, source_snapshot=source_snapshot)

    seed = service.get_seed(project_id="P1")

    assert seed.source_preview_payload is not None
    row = seed.source_preview_payload["rows"][0]
    assert row["method"] == "EIA-364-23D"
    assert row["condition"] == "20mV max, 100mA max"
    assert row["requirement"] == "Initial <= 0.25 milliohms"


def test_confirm_session_no_change_returns_http200_semantics() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id=None,
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )
    result = service.confirm_session(command)
    assert result.publish_status == "no_change"
    assert result.message == "No Matrix changes to confirm."
    assert result.confirmed_snapshot is None
    assert result.fee_rebase_promotion_status == "not_required"


def test_save_editor_draft_attaches_current_fee_rebase_status() -> None:
    active = _build_active_snapshot()
    pending = _RecordingPendingFeeRebaseService(
        MatrixFeePendingRebaseResult(
            status="current",
            summary=MatrixFeeRebaseSummary(
                preserved_count=1,
                added_count=2,
                removed_count=0,
            ),
        )
    )
    service = _service(
        active=active,
        source_snapshot=None,
        draft_persistence_service=_RecordingDraftPersistenceService(),
        matrix_revision_flow_service=_RecordingMatrixRevisionFlowService(),
        pending_fee_rebase_service=pending,
    )

    result = service.save_editor_draft(_save_command())

    assert result.editor_draft_id == "pmd-rev"
    assert result.fee_rebase_status == "current"
    assert result.fee_rebase_summary == MatrixFeeRebaseSummary(
        preserved_count=1,
        added_count=2,
        removed_count=0,
    )
    assert pending.rebase_command is not None
    assert pending.rebase_command.saved_matrix_draft.record.project_matrix_draft_id == "pmd-rev"


def test_save_editor_draft_keeps_matrix_success_when_fee_rebase_failed() -> None:
    pending = _RecordingPendingFeeRebaseService(
        MatrixFeePendingRebaseResult(
            status="failed",
            error="Fee rebase failed after Matrix autosave: pricing context exploded",
        )
    )
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_persistence_service=_RecordingDraftPersistenceService(),
        matrix_revision_flow_service=_RecordingMatrixRevisionFlowService(),
        pending_fee_rebase_service=pending,
    )

    result = service.save_editor_draft(_save_command())

    assert result.draft_status == "current"
    assert result.fee_rebase_status == "failed"
    assert "pricing context exploded" in (result.fee_rebase_error or "")


def test_confirm_saved_revision_attaches_fee_rebase_promotion_status() -> None:
    draft = _saved_revision_draft()
    promotion = _RecordingFeeRebasePromotionService(
        MatrixFeeRebasePromotionResult(
            status="promoted",
            summary=MatrixFeeRebaseSummary(
                preserved_count=1,
                added_count=0,
                removed_count=0,
            ),
        )
    )
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=_SavedDraftStore(draft),
        fee_rebase_promotion_service=promotion,
    )

    result = service.confirm_session(_confirm_saved_revision_command(draft))

    assert result.publish_status == "published"
    assert result.fee_rebase_promotion_status == "promoted"
    assert result.fee_rebase_promotion_summary == MatrixFeeRebaseSummary(
        preserved_count=1,
        added_count=0,
        removed_count=0,
    )
    assert promotion.command is not None
    assert promotion.command.saved_matrix_draft == draft
    assert promotion.command.saved_matrix_draft_payload_signature == (
        _build_signature_from_project_draft(draft)
    )
    assert promotion.command.previous_confirmed_matrix.version.confirmed_matrix_id == "cmv-1"
    assert promotion.command.new_confirmed_matrix is result.confirmed_snapshot


def test_confirm_saved_revision_keeps_published_when_fee_promotion_failed() -> None:
    draft = _saved_revision_draft()
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=_SavedDraftStore(draft),
        fee_rebase_promotion_service=_RecordingFeeRebasePromotionService(
            MatrixFeeRebasePromotionResult(
                status="failed",
                error="Fee rebase promotion failed: database unavailable",
            )
        ),
    )

    result = service.confirm_session(_confirm_saved_revision_command(draft))

    assert result.publish_status == "published"
    assert result.confirmed_snapshot is not None
    assert result.fee_rebase_promotion_status == "failed"
    assert "database unavailable" in (result.fee_rebase_promotion_error or "")


def test_discard_editor_draft_deletes_pending_fee_rebase() -> None:
    draft_store = _DiscardDraftStore(_active_editor_draft())
    pending = _RecordingPendingFeeRebaseService(MatrixFeePendingRebaseResult(status="not_required"))
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=draft_store,
        pending_fee_rebase_service=pending,
    )

    result = service.discard_editor_draft(
        MatrixEditorSessionDraftDiscardCommand(project_id="P1")
    )

    assert result.discarded is True
    assert pending.deleted_matrix_draft_id == "pmd-edit"


def test_discard_editor_draft_surfaces_pending_delete_failure() -> None:
    pending = _FailingPendingFeeRebaseService()
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=_DiscardDraftStore(_active_editor_draft()),
        pending_fee_rebase_service=pending,
    )

    with pytest.raises(MatrixEditorSessionDraftConflictError, match="pending Fee rebase"):
        service.discard_editor_draft(
            MatrixEditorSessionDraftDiscardCommand(project_id="P1")
        )


def test_discard_editor_draft_deletes_pending_again_after_matrix_delete_race() -> None:
    pending = _RacePendingFeeRebaseService()
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=_DiscardDraftStore(_active_editor_draft()),
        pending_fee_rebase_service=pending,
    )

    result = service.discard_editor_draft(
        MatrixEditorSessionDraftDiscardCommand(project_id="P1")
    )

    assert result.discarded is True
    assert pending.delete_calls == 2
    assert pending.pending_exists is False


def test_confirm_session_no_change_ignores_unselected_source_groups() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id=None,
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
            MatrixEditorSessionGroup(
                draft_group_id="dg-2",
                source_group_snapshot_id="sg-2",
                group_order=2,
                group_key="g2",
                group_label="2",
                is_selected=False,
                sample_quantity_expression=None,
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-2",
                cell_value="2",
            ),
        ),
    )
    result = service.confirm_session(command)
    assert result.publish_status == "no_change"
    assert result.message == "No Matrix changes to confirm."
    assert result.confirmed_snapshot is None


def test_confirm_session_treats_group_prefix_as_same_signature() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id=None,
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="Group 1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )
    result = service.confirm_session(command)
    assert result.publish_status == "no_change"
    assert result.message == "No Matrix changes to confirm."
    assert result.confirmed_snapshot is None


def test_confirm_session_when_active_id_changed_raises_conflict_message() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-old",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id=None,
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="2",
            ),
        ),
    )
    with pytest.raises(MatrixEditorSessionActiveChangedError) as exc:
        service.confirm_session(command)
    assert "Matrix was updated. Reload the latest Matrix to continue." in str(exc.value)


def test_confirm_session_rejects_selected_group_sample_without_digit() -> None:
    active = _build_active_snapshot(sample_quantity_expression="")
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id="smi-1",
        source_snapshot_id="sms-1",
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="sample only",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )
    with pytest.raises(MatrixEditorSessionError) as exc:
        service.confirm_session(command)
    assert "Sample quantity is required for selected groups: 1." in str(exc.value)


class _ProjectStore:
    def get(self, project_id: str):
        if project_id != "P1":
            return None
        return Project(
            project_id="P1",
            project_no="DL-2026-05-001",
            product_name="Connector",
            requestor="Alice",
            status=ProjectStatus.LTR_REGISTERED,
            created_on=date(2026, 5, 22),
        )


class _ConfirmedStore:
    def __init__(self, active: ConfirmedMatrixSnapshot | None) -> None:
        self._active = active

    def get_active_by_project(self, project_id: str):
        return self._active if project_id == "P1" else None

    def list_by_project(self, project_id: str):
        return (self._active,) if project_id == "P1" and self._active is not None else ()

    def supersede_active_and_create_snapshot(self, *, previous_active_confirmed_matrix_id: str, snapshot, superseded_reason=None):
        self._active = snapshot
        return snapshot


class _SourceStore:
    def __init__(self, *, source_snapshot) -> None:
        self._snapshot = source_snapshot
        self._import = SourceMatrixImportRecord(
            import_id="smi-1",
            project_id="P1",
            draft_id="ptpd-1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            source_asset_id=None,
            source_case_id=None,
            source_draft_id=None,
            import_status=SourceMatrixImportStatus.IMPORTED,
            source_spec_number=None,
            source_spec_revision=None,
            parse_time="2026-05-27T00:00:00Z",
            parser_version="parser-v1",
            payload_schema_version="1.0",
            warnings=(),
            blockers=(),
            selected_group_keys_at_import=("g1",),
            task261_commit_fingerprint=None,
            created_at="2026-05-27T00:00:00Z",
        )

    def get_import(self, import_id: str):
        return self._import if import_id == "smi-1" else None

    def get_snapshot(self, snapshot_id: str):
        return self._snapshot if snapshot_id == "sms-1" else None


class _DraftStore:
    def get(self, project_matrix_draft_id: str):
        return None

    def list_by_project(self, project_id: str):
        return ()

    def delete(self, project_matrix_draft_id: str):
        return None

    def get_by_project_and_base_confirmed_matrix(self, project_id: str, base_confirmed_matrix_id: str):
        return None

    def get_by_project_and_source_import(self, project_id: str, source_import_id: str):
        return None


class _DiscardDraftStore(_DraftStore):
    def __init__(self, draft: ProjectMatrixDraftSnapshot | None) -> None:
        self._draft = draft
        self.deleted: str | None = None

    def get(self, project_matrix_draft_id: str):
        if self._draft is None:
            return None
        return self._draft if project_matrix_draft_id == self._draft.record.project_matrix_draft_id else None

    def list_by_project(self, project_id: str):
        return [self._draft.record] if self._draft is not None else []

    def delete(self, project_matrix_draft_id: str):
        self.deleted = project_matrix_draft_id
        self._draft = None
        return True


class _SavedDraftStore(_DraftStore):
    def __init__(self, draft: ProjectMatrixDraftSnapshot) -> None:
        self._draft = draft

    def get(self, project_matrix_draft_id: str):
        if project_matrix_draft_id == self._draft.record.project_matrix_draft_id:
            return self._draft
        return None


class _DraftPersistenceService:
    def update_draft(self, command):
        raise AssertionError("update_draft should not be called in no-change tests")


class _MatrixImportCommitService:
    def commit(self, command):
        raise AssertionError("commit should not be called in no-change tests")


class _MatrixRevisionFlowService:
    def create_revision_draft(self, command):
        raise AssertionError("create_revision_draft should not be called in no-change tests")

    def confirm_revision_draft(self, command):
        raise AssertionError("confirm_revision_draft should not be called in no-change tests")


class _RecordingMatrixRevisionFlowService:
    def __init__(self) -> None:
        self.confirm_revision_called = False

    def create_revision_draft(self, command):
        return ProjectMatrixDraftSnapshot(
            record=ProjectMatrixDraftRecord(
                project_matrix_draft_id="pmd-rev",
                project_id="P1",
                source_import_id=None,
                source_snapshot_id="sms-1",
                status=ProjectMatrixDraftStatus.DRAFT,
                created_at="2026-05-27T00:00:00Z",
                updated_at="2026-05-27T00:00:00Z",
                base_confirmed_matrix_id="cmv-1",
            ),
            groups=(),
            rows=(),
            cells=(),
        )

    def confirm_revision_draft(self, command):
        self.confirm_revision_called = True
        raise AssertionError("Matrix Editor session confirm should not use legacy revision validation.")


class _RecordingDraftPersistenceService:
    def __init__(self) -> None:
        self.updated = False

    def update_draft(self, command):
        self.updated = True
        return ProjectMatrixDraftSnapshot(
            record=ProjectMatrixDraftRecord(
                project_matrix_draft_id=command.project_matrix_draft_id,
                project_id=command.project_id,
                source_import_id=None,
                source_snapshot_id="sms-1",
                status=ProjectMatrixDraftStatus.DRAFT,
                created_at="2026-05-27T00:00:00Z",
                updated_at="2026-05-27T00:00:01Z",
                base_confirmed_matrix_id="cmv-1",
            ),
            groups=tuple(
                ProjectMatrixDraftGroup(
                    draft_group_id=group.draft_group_id,
                    project_matrix_draft_id=command.project_matrix_draft_id,
                    source_group_snapshot_id=group.source_group_snapshot_id,
                    group_order=group.group_order,
                    group_key=group.group_key,
                    group_label=group.group_label,
                    is_selected=group.is_selected,
                    sample_quantity_expression=group.sample_quantity_expression,
                    sample_note=group.sample_note,
                )
                for group in command.groups
            ),
            rows=tuple(
                ProjectMatrixDraftRow(
                    draft_row_id=row.draft_row_id,
                    project_matrix_draft_id=command.project_matrix_draft_id,
                    source_row_snapshot_id=row.source_row_snapshot_id,
                    row_order=row.row_order,
                    test_item=row.test_item,
                    source_section=row.source_section,
                    method=row.method,
                    condition=row.condition,
                    requirement=row.requirement,
                    is_sample_row=row.is_sample_row,
                )
                for row in command.rows
            ),
            cells=tuple(
                ProjectMatrixDraftCell(
                    draft_cell_id=f"cell-{index}",
                    project_matrix_draft_id=command.project_matrix_draft_id,
                    draft_row_id=cell.draft_row_id,
                    draft_group_id=cell.draft_group_id,
                    cell_value=cell.cell_value,
                )
                for index, cell in enumerate(command.cells, start=1)
            ),
        )


class _ConfirmedAuthorityService:
    def confirm_draft(self, command):
        raise AssertionError("confirm_draft should not be called in no-change tests")


class _RecordingPendingFeeRebaseService:
    def __init__(self, result: MatrixFeePendingRebaseResult) -> None:
        self._result = result
        self.rebase_command = None
        self.deleted_matrix_draft_id: str | None = None

    def rebase_after_matrix_autosave(self, command):
        self.rebase_command = command
        return self._result

    def delete_for_matrix_draft(self, command):
        self.deleted_matrix_draft_id = command.project_matrix_draft_id
        return None


class _FailingPendingFeeRebaseService:
    def rebase_after_matrix_autosave(self, command):
        return MatrixFeePendingRebaseResult(status="not_required")

    def delete_for_matrix_draft(self, command):
        raise RuntimeError("storage busy")


class _RacePendingFeeRebaseService:
    def __init__(self) -> None:
        self.delete_calls = 0
        self.pending_exists = True

    def rebase_after_matrix_autosave(self, command):
        return MatrixFeePendingRebaseResult(status="not_required")

    def delete_for_matrix_draft(self, command):
        self.delete_calls += 1
        self.pending_exists = False
        if self.delete_calls == 1:
            self.pending_exists = True
        return None


class _RecordingFeeRebasePromotionService:
    def __init__(self, result: MatrixFeeRebasePromotionResult) -> None:
        self._result = result
        self.command = None

    def promote_after_matrix_confirm(self, command):
        self.command = command
        return self._result


def _service(
    *,
    active: ConfirmedMatrixSnapshot | None,
    source_snapshot,
    draft_store=None,
    draft_persistence_service=None,
    matrix_revision_flow_service=None,
    pending_fee_rebase_service=None,
    fee_rebase_promotion_service=None,
):
    return MatrixEditorSessionService(
        project_store=_ProjectStore(),
        confirmed_store=_ConfirmedStore(active),
        source_store=_SourceStore(source_snapshot=source_snapshot),
        draft_store=draft_store or _DraftStore(),
        draft_persistence_service=draft_persistence_service or _DraftPersistenceService(),
        matrix_import_commit_service=_MatrixImportCommitService(),
        matrix_revision_flow_service=matrix_revision_flow_service
        or _MatrixRevisionFlowService(),
        confirmed_matrix_authority_service=_ConfirmedAuthorityService(),
        pending_fee_rebase_service=pending_fee_rebase_service,
        fee_rebase_promotion_service=fee_rebase_promotion_service,
    )


def _save_command() -> MatrixEditorSessionDraftSaveCommand:
    return MatrixEditorSessionDraftSaveCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id="sms-1",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Contact Resistance",
                source_section="6.1",
                method="EIA-364-23D",
                condition="Initial",
                requirement="< 10 mohm",
                day_expression=None,
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )


def _active_editor_draft() -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="pmd-edit",
            project_id="P1",
            source_import_id=None,
            source_snapshot_id="sms-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-05-27T00:00:00Z",
            updated_at="2026-05-27T00:00:01Z",
            base_confirmed_matrix_id="cmv-1",
        ),
        groups=(),
        rows=(),
        cells=(),
    )


def _saved_revision_draft() -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="pmd-edit",
            project_id="P1",
            source_import_id=None,
            source_snapshot_id="sms-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-05-27T00:00:00Z",
            updated_at="2026-05-27T00:00:01Z",
            base_confirmed_matrix_id="cmv-1",
        ),
        groups=(
            ProjectMatrixDraftGroup(
                draft_group_id="dg-1",
                project_matrix_draft_id="pmd-edit",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            ProjectMatrixDraftRow(
                draft_row_id="dr-1",
                project_matrix_draft_id="pmd-edit",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Contact Resistance",
                source_section="6.1",
                method="EIA-364-23D",
                condition="Initial",
                requirement="< 10 mohm",
                is_sample_row=False,
            ),
        ),
        cells=(
            ProjectMatrixDraftCell(
                draft_cell_id="dc-1",
                project_matrix_draft_id="pmd-edit",
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )


def _confirm_saved_revision_command(
    draft: ProjectMatrixDraftSnapshot,
) -> MatrixEditorSessionConfirmCommand:
    return MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id="sms-1",
        confirmed_by="operator",
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
        expected_editor_draft_id=draft.record.project_matrix_draft_id,
        expected_saved_payload_signature=_build_signature_from_project_draft(draft),
    )


def _build_active_snapshot(sample_quantity_expression: str = "5") -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="cmv-1",
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-05-27T00:00:00Z",
        ),
        groups=(
            ConfirmedMatrixGroup(
                confirmed_group_id="cg-1",
                confirmed_matrix_id="cmv-1",
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                sample_quantity_expression=sample_quantity_expression,
                sample_note=None,
            ),
        ),
        rows=(
            ConfirmedMatrixRow(
                confirmed_row_id="cr-1",
                confirmed_matrix_id="cmv-1",
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
            ),
        ),
        cells=(
            ConfirmedMatrixCell(
                confirmed_cell_id="cc-1",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id="cr-1",
                confirmed_group_id="cg-1",
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )
