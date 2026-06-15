from __future__ import annotations

import json

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedExportRow,
)
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    MatrixBasicFillGroup,
    MatrixBasicFillHeader,
    MatrixBasicFillLine,
    MatrixBasicFillWorkbook,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftSnapshot,
)
from backend.application.matrix_fee_draft_rebase_service import (
    MatrixFeeRebaseResult,
    MatrixFeeRebaseSummary,
)
from backend.application.matrix_fee_pending_rebase_service import (
    DeletePendingRebaseForMatrixDraftCommand,
    DefaultMatrixFeePendingRebaseBuilder,
    MatrixFeePendingRebaseService,
    MatrixFeePendingRebaseSnapshot,
    RebaseAfterMatrixAutosaveCommand,
)
from backend.domain.enums import ProjectMatrixDraftStatus
from backend.domain.project_matrix_draft_models import (
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
)


def test_pending_rebase_service_saves_current_payload() -> None:
    draft = _draft()
    draft_store = _DraftStore(draft)
    pending_store = _PendingStore()
    service = MatrixFeePendingRebaseService(
        draft_store=draft_store,
        pending_store=pending_store,
        rebase_builder=_RebaseBuilder(_rebase_result()),
        draft_signature_builder=lambda _: "sig-current",
    )

    result = service.rebase_after_matrix_autosave(
        RebaseAfterMatrixAutosaveCommand(
            project_id="P1",
            active_confirmed_matrix_id="cmv-1",
            active_confirmed_revision=2,
            saved_matrix_draft=draft,
            saved_payload_signature="sig-current",
            fee_rule_version_id="fee-rules-v1",
            generation=10,
        )
    )

    assert result.status == "current"
    assert result.summary == MatrixFeeRebaseSummary(
        preserved_count=1,
        added_count=1,
        removed_count=0,
    )
    assert pending_store.saved is not None
    assert pending_store.saved.project_matrix_draft_id == "pmd-1"
    assert pending_store.saved.matrix_draft_payload_signature == "sig-current"
    payload = json.loads(pending_store.saved.payload_json)
    assert payload["summary"]["preserved_count"] == 1
    assert payload["active_rows"][0]["source_line_id"] == "line-1"


def test_default_builder_preserves_pricing_edits_for_unchanged_matrix_tokens() -> None:
    draft = _draft()
    builder = DefaultMatrixFeePendingRebaseBuilder(
        basic_fill_service=_BasicFillService(),
        pricing_draft_store=_PricingDraftStore(
            FeeEvaluationPricingDraftSnapshot(
                draft_edit_id="pricing-draft-1",
                project_id="P1",
                confirmed_matrix_id="cmv-1",
                confirmed_revision=2,
                fee_rule_version_id="fee-rules-v1",
                edited_values=FeeEvaluationEditedExportValues(
                    rows=(
                        FeeEvaluationEditedExportRow(
                            source_line_id="line-source",
                            confirmed_group_id="dg-1",
                            confirmed_row_id="dr-1",
                            step_token="1",
                            step_index=0,
                            spend_time="3.5",
                            unit_price="120",
                            unit_type="hour",
                            units="1",
                            base_fee="420",
                            discount="10%",
                            testing_fee="378",
                            notes="preserve me",
                        ),
                    ),
                    summary=FeeEvaluationEditedExportSummary(
                        condition_confirmation_spend_time="",
                        external_cost="",
                        external_cost_note="",
                        lab_manpower_hourly_rate="",
                    ),
                ),
                created_at="2026-06-14T09:00:00+00:00",
                updated_at="2026-06-14T09:01:00+00:00",
            )
        ),
    )

    result = builder.build_and_rebase(
        RebaseAfterMatrixAutosaveCommand(
            project_id="P1",
            active_confirmed_matrix_id="cmv-1",
            active_confirmed_revision=2,
            saved_matrix_draft=draft,
            saved_payload_signature="sig-current",
            fee_rule_version_id="fee-rules-v1",
            generation=10,
        )
    )

    assert result.summary.preserved_count == 1
    assert result.summary.added_count == 0
    assert result.summary.removed_count == 0
    assert result.active_rows[0].step_index == 0
    assert result.active_rows[0].unit_price == "120"
    assert result.active_rows[0].testing_fee == "378"
    assert result.active_rows[0].notes == "preserve me"


def test_default_builder_uses_saveable_defaults_for_new_matrix_rows() -> None:
    draft = _draft_with_added_row()
    builder = DefaultMatrixFeePendingRebaseBuilder(
        basic_fill_service=_BasicFillService(),
        pricing_draft_store=_PricingDraftStore(
            FeeEvaluationPricingDraftSnapshot(
                draft_edit_id="pricing-draft-1",
                project_id="P1",
                confirmed_matrix_id="cmv-1",
                confirmed_revision=2,
                fee_rule_version_id="fee-rules-v1",
                edited_values=FeeEvaluationEditedExportValues(
                    rows=(
                        FeeEvaluationEditedExportRow(
                            source_line_id="line-source",
                            confirmed_group_id="dg-1",
                            confirmed_row_id="dr-1",
                            step_token="1",
                            step_index=0,
                            spend_time="3.5",
                            unit_price="120",
                            unit_type="hour",
                            units="1",
                            base_fee="420",
                            discount="10%",
                            testing_fee="378",
                            notes="preserve me",
                        ),
                    ),
                    summary=FeeEvaluationEditedExportSummary(
                        condition_confirmation_spend_time="",
                        external_cost="",
                        external_cost_note="",
                        lab_manpower_hourly_rate="",
                    ),
                ),
                created_at="2026-06-14T09:00:00+00:00",
                updated_at="2026-06-14T09:01:00+00:00",
            )
        ),
    )

    result = builder.build_and_rebase(
        RebaseAfterMatrixAutosaveCommand(
            project_id="P1",
            active_confirmed_matrix_id="cmv-1",
            active_confirmed_revision=2,
            saved_matrix_draft=draft,
            saved_payload_signature="sig-current",
            fee_rule_version_id="fee-rules-v1",
            generation=10,
        )
    )

    added = next(row for row in result.active_rows if row.confirmed_row_id == "dr-added")
    assert added.unit_type == "Pending"
    assert added.spend_time == "0"
    assert added.unit_price == "0"
    assert added.units == "1"
    assert added.base_fee == "0"
    assert added.discount == "0%"


def test_pending_rebase_service_returns_failed_when_builder_fails() -> None:
    draft = _draft()
    pending_store = _PendingStore()
    service = MatrixFeePendingRebaseService(
        draft_store=_DraftStore(draft),
        pending_store=pending_store,
        rebase_builder=_FailingRebaseBuilder(),
        draft_signature_builder=lambda _: "sig-current",
    )

    result = service.rebase_after_matrix_autosave(
        RebaseAfterMatrixAutosaveCommand(
            project_id="P1",
            active_confirmed_matrix_id="cmv-1",
            active_confirmed_revision=2,
            saved_matrix_draft=draft,
            saved_payload_signature="sig-current",
            fee_rule_version_id="fee-rules-v1",
            generation=10,
        )
    )

    assert result.status == "failed"
    assert "Fee rebase failed" in (result.error or "")
    assert pending_store.saved is None


def test_pending_rebase_service_skips_when_draft_base_changed() -> None:
    draft = _draft(base_confirmed_matrix_id="cmv-old")
    pending_store = _PendingStore()
    service = MatrixFeePendingRebaseService(
        draft_store=_DraftStore(draft),
        pending_store=pending_store,
        rebase_builder=_RebaseBuilder(_rebase_result()),
        draft_signature_builder=lambda _: "sig-current",
    )

    result = service.rebase_after_matrix_autosave(
        RebaseAfterMatrixAutosaveCommand(
            project_id="P1",
            active_confirmed_matrix_id="cmv-1",
            active_confirmed_revision=2,
            saved_matrix_draft=draft,
            saved_payload_signature="sig-current",
            fee_rule_version_id="fee-rules-v1",
            generation=10,
        )
    )

    assert result.status == "not_required"
    assert pending_store.saved is None


def test_pending_rebase_service_does_not_save_after_draft_deleted() -> None:
    draft = _draft()
    pending_store = _PendingStore()
    service = MatrixFeePendingRebaseService(
        draft_store=_DraftStore(None),
        pending_store=pending_store,
        rebase_builder=_RebaseBuilder(_rebase_result()),
        draft_signature_builder=lambda _: "sig-current",
    )

    result = service.rebase_after_matrix_autosave(
        RebaseAfterMatrixAutosaveCommand(
            project_id="P1",
            active_confirmed_matrix_id="cmv-1",
            active_confirmed_revision=2,
            saved_matrix_draft=draft,
            saved_payload_signature="sig-current",
            fee_rule_version_id="fee-rules-v1",
            generation=10,
        )
    )

    assert result.status == "not_required"
    assert pending_store.saved is None


def test_pending_rebase_service_does_not_save_signature_mismatch() -> None:
    draft = _draft()
    pending_store = _PendingStore()
    service = MatrixFeePendingRebaseService(
        draft_store=_DraftStore(draft),
        pending_store=pending_store,
        rebase_builder=_RebaseBuilder(_rebase_result()),
        draft_signature_builder=lambda _: "sig-newer",
    )

    result = service.rebase_after_matrix_autosave(
        RebaseAfterMatrixAutosaveCommand(
            project_id="P1",
            active_confirmed_matrix_id="cmv-1",
            active_confirmed_revision=2,
            saved_matrix_draft=draft,
            saved_payload_signature="sig-current",
            fee_rule_version_id="fee-rules-v1",
            generation=10,
        )
    )

    assert result.status == "not_required"
    assert pending_store.saved is None


def test_pending_rebase_service_reports_not_required_for_stale_generation() -> None:
    draft = _draft()
    pending_store = _PendingStore(
        existing=MatrixFeePendingRebaseSnapshot(
            pending_rebase_id="pending-existing",
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            base_confirmed_matrix_id="cmv-1",
            base_confirmed_revision=2,
            fee_rule_version_id="fee-rules-v1",
            matrix_draft_payload_signature="sig-newer",
            generation=20,
            payload_json='{"summary": {"preserved_count": 99}}',
            created_at="2026-06-14T09:00:00+00:00",
            updated_at="2026-06-14T09:02:00+00:00",
        )
    )
    service = MatrixFeePendingRebaseService(
        draft_store=_DraftStore(draft),
        pending_store=pending_store,
        rebase_builder=_RebaseBuilder(_rebase_result()),
        draft_signature_builder=lambda _: "sig-current",
    )

    result = service.rebase_after_matrix_autosave(
        RebaseAfterMatrixAutosaveCommand(
            project_id="P1",
            active_confirmed_matrix_id="cmv-1",
            active_confirmed_revision=2,
            saved_matrix_draft=draft,
            saved_payload_signature="sig-current",
            fee_rule_version_id="fee-rules-v1",
            generation=20,
        )
    )

    assert result.status == "not_required"
    assert pending_store.saved is not None
    assert pending_store.saved.generation == 20
    assert "preserved_count" in pending_store.saved.payload_json
    assert "99" in pending_store.saved.payload_json


def test_pending_rebase_service_deletes_pending_by_matrix_draft() -> None:
    pending_store = _PendingStore()
    service = MatrixFeePendingRebaseService(
        draft_store=_DraftStore(_draft()),
        pending_store=pending_store,
        rebase_builder=_RebaseBuilder(_rebase_result()),
        draft_signature_builder=lambda _: "sig-current",
    )

    result = service.delete_for_matrix_draft(
        DeletePendingRebaseForMatrixDraftCommand(project_matrix_draft_id="pmd-1")
    )

    assert result.deleted_count == 1
    assert pending_store.deleted_matrix_draft_id == "pmd-1"


class _DraftStore:
    def __init__(self, draft: ProjectMatrixDraftSnapshot | None) -> None:
        self._draft = draft

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        return self._draft if project_matrix_draft_id == "pmd-1" else None


class _BasicFillService:
    def build(self, command) -> MatrixBasicFillWorkbook:
        return MatrixBasicFillWorkbook(
            header=MatrixBasicFillHeader(
                project_id="P1",
                confirmed_matrix_id="cmv-1",
                confirmed_revision=2,
                generated_at="2026-06-14T09:00:00+00:00",
            ),
            status="ready",
            groups=(
                MatrixBasicFillGroup(
                    group_key="G1",
                    group_label="Group 1",
                    confirmed_group_id="dg-1",
                    sample_quantity_expression="",
                    lines=(
                        MatrixBasicFillLine(
                            line_id="line-source",
                            group_key="G1",
                            group_label="Group 1",
                            confirmed_group_id="dg-1",
                            confirmed_row_id="dr-1",
                            source_row_id="src-row-1",
                            row_order=1,
                            step_index=0,
                            test_item="Visual inspection",
                            cell_value="1",
                            step_tokens=("1",),
                        ),
                    ),
                ),
            ),
        )


class _PricingDraftStore:
    def __init__(self, snapshot: FeeEvaluationPricingDraftSnapshot | None) -> None:
        self._snapshot = snapshot

    def get_by_context(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        return self._snapshot


class _PendingStore:
    def __init__(self, existing: MatrixFeePendingRebaseSnapshot | None = None) -> None:
        self.saved = existing
        self.deleted_matrix_draft_id: str | None = None

    def upsert_current(
        self, snapshot: MatrixFeePendingRebaseSnapshot
    ) -> MatrixFeePendingRebaseSnapshot:
        if self.saved is not None and snapshot.generation <= self.saved.generation:
            return self.saved
        self.saved = snapshot
        return snapshot

    def delete_by_matrix_draft(self, project_matrix_draft_id: str) -> int:
        self.deleted_matrix_draft_id = project_matrix_draft_id
        self.saved = None
        return 1


class _RebaseBuilder:
    def __init__(self, result: MatrixFeeRebaseResult) -> None:
        self._result = result

    def build_and_rebase(self, command: RebaseAfterMatrixAutosaveCommand) -> MatrixFeeRebaseResult:
        return self._result


class _FailingRebaseBuilder:
    def build_and_rebase(self, command: RebaseAfterMatrixAutosaveCommand) -> MatrixFeeRebaseResult:
        raise RuntimeError("pricing context exploded")


def _draft(base_confirmed_matrix_id: str = "cmv-1") -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="pmd-1",
            project_id="P1",
            source_import_id=None,
            source_snapshot_id="sms-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-06-14T09:00:00+00:00",
            updated_at="2026-06-14T09:01:00+00:00",
            base_confirmed_matrix_id=base_confirmed_matrix_id,
        ),
        groups=(
            ProjectMatrixDraftGroup(
                draft_group_id="dg-1",
                project_matrix_draft_id="pmd-1",
                source_group_snapshot_id=None,
                group_order=1,
                group_key="G1",
                group_label="Group 1",
                is_selected=True,
            ),
        ),
        rows=(
            ProjectMatrixDraftRow(
                draft_row_id="dr-1",
                project_matrix_draft_id="pmd-1",
                source_row_snapshot_id="src-row-1",
                row_order=1,
                test_item="Visual inspection",
            ),
        ),
        cells=(
            ProjectMatrixDraftCell(
                draft_cell_id="dc-1",
                project_matrix_draft_id="pmd-1",
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )


def _draft_with_added_row() -> ProjectMatrixDraftSnapshot:
    draft = _draft()
    return ProjectMatrixDraftSnapshot(
        record=draft.record,
        groups=draft.groups,
        rows=draft.rows
        + (
            ProjectMatrixDraftRow(
                draft_row_id="dr-added",
                project_matrix_draft_id="pmd-1",
                source_row_snapshot_id="src-row-added",
                row_order=2,
                test_item="Added inspection",
            ),
        ),
        cells=draft.cells
        + (
            ProjectMatrixDraftCell(
                draft_cell_id="dc-added",
                project_matrix_draft_id="pmd-1",
                draft_row_id="dr-added",
                draft_group_id="dg-1",
                cell_value="2",
            ),
        ),
    )


def _rebase_result() -> MatrixFeeRebaseResult:
    return MatrixFeeRebaseResult(
        active_rows=(
            FeeEvaluationEditedExportRow(
                source_line_id="line-1",
                confirmed_group_id="dg-1",
                confirmed_row_id="dr-1",
                step_token="1",
                step_index=1,
                spend_time="1",
                unit_price="10",
                unit_type="hour",
                units="1",
                base_fee="10",
                discount="",
                testing_fee="10",
                notes="",
            ),
        ),
        inactive_removed_rows=(),
        manual_rows=(),
        summary=MatrixFeeRebaseSummary(
            preserved_count=1,
            added_count=1,
            removed_count=0,
        ),
    )
