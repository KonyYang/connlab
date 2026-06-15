from __future__ import annotations

import pytest

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    build_basic_fill_from_confirmed_snapshot,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedManualRow,
    edited_row_lookup,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftSnapshot,
)
from backend.application.matrix_fee_draft_rebase_service import (
    MatrixFeeInactiveRemovedRow,
    MatrixFeeRebaseResult,
    MatrixFeeRebaseSummary,
)
from backend.application.matrix_fee_pending_rebase_service import (
    MatrixFeePendingRebaseSnapshot,
    pending_rebase_payload_from_json,
    pending_rebase_payload_to_json,
)
from backend.application.matrix_fee_rebase_promotion_service import (
    MatrixFeeRebasePromotionService,
    PromoteMatrixFeeRebaseCommand,
    remap_rebase_result_to_confirmed_matrix,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
)


def test_pending_rebase_payload_roundtrips_rows_manual_rows_summary_and_warnings() -> None:
    result = _rebase_result(
        active_rows=(_draft_shaped_row(notes="kept"),),
        inactive_removed_rows=(
            MatrixFeeInactiveRemovedRow(
                previous_row=_previous_context_row(notes="removed"),
                previous_group_key="G1",
                previous_group_label="Group 1",
                previous_row_signature="old-signature",
            ),
        ),
        manual_rows=(
            FeeEvaluationEditedManualRow(
                row_kind="report_preparation",
                spend_time="1",
                unit_price="2",
                unit_type="hour",
                units="3",
                base_fee="4",
                discount="5",
                testing_fee="6",
                notes="manual",
            ),
        ),
        summary=MatrixFeeRebaseSummary(
            preserved_count=1,
            added_count=2,
            removed_count=3,
            preserved_manual_count=4,
            removed_manual_count=5,
        ),
        warnings=("check removed rows",),
    )

    restored = pending_rebase_payload_from_json(pending_rebase_payload_to_json(result))

    assert restored == result


def test_remap_projects_pending_rows_to_new_basic_fill_identity_and_preserves_summary() -> None:
    previous_draft = _previous_pricing_draft(
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time="0.5",
            external_cost="120",
            external_cost_note="freight",
            lab_manpower_hourly_rate="80",
        )
    )
    values = remap_rebase_result_to_confirmed_matrix(
        rebase_result=_rebase_result(active_rows=(_draft_shaped_row(notes="pricing"),)),
        previous_pricing_draft=previous_draft,
        new_confirmed_matrix=_confirmed_snapshot("cmv-new", 2, "cmg-new", "cmr-new"),
    )

    assert values.rows == (
        FeeEvaluationEditedExportRow(
            source_line_id="cmv-new:G1:cmr-new:1:0",
            confirmed_group_id="cmg-new",
            confirmed_row_id="cmr-new",
            step_token="1",
            step_index=0,
            spend_time="2",
            unit_price="50",
            unit_type="hour",
            units="1",
            base_fee="100",
            discount="0",
            testing_fee="100",
            notes="pricing",
        ),
    )
    assert values.summary == previous_draft.edited_values.summary
    edited_row_lookup(values, build_basic_fill_from_confirmed_snapshot(
        _confirmed_snapshot("cmv-new", 2, "cmg-new", "cmr-new")
    ))


def test_remap_converts_blank_added_row_unit_type_to_saveable_pending() -> None:
    values = remap_rebase_result_to_confirmed_matrix(
        rebase_result=_rebase_result(
            active_rows=(
                _draft_shaped_row(notes="group 1 note"),
                _draft_shaped_row(
                    confirmed_row_id="dr-added",
                    step_token="2",
                    unit_type="",
                    notes="new group row",
                ),
            )
        ),
        previous_pricing_draft=_previous_pricing_draft(notes="group 1 note"),
        new_confirmed_matrix=_confirmed_snapshot_with_added_row(),
    )

    added = next(row for row in values.rows if row.confirmed_row_id == "cmr-added")
    assert added.unit_type == "Pending"
    assert added.notes == "new group row"
    edited_row_lookup(values, build_basic_fill_from_confirmed_snapshot(
        _confirmed_snapshot_with_added_row()
    ))


def test_remap_rejects_rows_that_do_not_exist_in_new_confirmed_matrix() -> None:
    with pytest.raises(ValueError, match="not found in new Confirmed Matrix"):
        remap_rebase_result_to_confirmed_matrix(
            rebase_result=_rebase_result(
                active_rows=(_draft_shaped_row(confirmed_row_id="missing-draft-row"),)
            ),
            previous_pricing_draft=_previous_pricing_draft(),
            new_confirmed_matrix=_confirmed_snapshot("cmv-new", 2, "cmg-new", "cmr-new"),
        )


def test_service_promotes_valid_pending_into_new_context_and_deletes_after_save() -> None:
    pending_store = _PendingStore(
        _pending_snapshot(
            payload_json=pending_rebase_payload_to_json(
                _rebase_result(active_rows=(_draft_shaped_row(notes="pending edit"),))
            )
        )
    )
    pricing_store = _PricingStore(previous=_previous_pricing_draft())
    service = MatrixFeeRebasePromotionService(
        pending_store=pending_store,
        pricing_draft_store=pricing_store,
    )

    result = service.promote_after_matrix_confirm(_promotion_command())

    assert result.status == "promoted"
    assert result.summary == MatrixFeeRebaseSummary(
        preserved_count=1,
        added_count=0,
        removed_count=0,
    )
    assert pricing_store.saved is not None
    assert pricing_store.saved.confirmed_matrix_id == "cmv-new"
    assert pricing_store.saved.confirmed_revision == 2
    assert pricing_store.saved.edited_values.rows[0].source_line_id == (
        "cmv-new:G1:cmr-new:1:0"
    )
    assert pricing_store.saved.edited_values.rows[0].notes == "pending edit"
    assert pricing_store.saved.edited_values.summary == (
        pricing_store.previous.edited_values.summary
    )
    assert pending_store.deleted_matrix_draft_id == "pmd-1"


def test_service_uses_fallback_when_pending_signature_is_stale() -> None:
    pending_store = _PendingStore(
        _pending_snapshot(
            payload_json=pending_rebase_payload_to_json(
                _rebase_result(active_rows=(_draft_shaped_row(notes="stale pending"),))
            ),
            matrix_draft_payload_signature="old-sig",
        )
    )
    pricing_store = _PricingStore(previous=_previous_pricing_draft(notes="fresh fallback"))
    service = MatrixFeeRebasePromotionService(
        pending_store=pending_store,
        pricing_draft_store=pricing_store,
    )

    result = service.promote_after_matrix_confirm(
        _promotion_command(saved_matrix_draft_payload_signature="new-sig")
    )

    assert result.status == "fallback_promoted"
    assert pricing_store.saved is not None
    assert pricing_store.saved.edited_values.rows[0].notes == "fresh fallback"
    assert pending_store.deleted_matrix_draft_id is None


def test_service_promotes_sample_preparation_manual_row_to_new_group_identity() -> None:
    pending_store = _PendingStore(
        _pending_snapshot(
            payload_json=pending_rebase_payload_to_json(
                _rebase_result(
                    active_rows=(_draft_shaped_row(notes="pending edit"),),
                    manual_rows=(
                        FeeEvaluationEditedManualRow(
                            row_kind="sample_preparation",
                            confirmed_group_id="dg-1",
                            group_key="G1",
                            group_label="Group 1",
                            spend_time="1",
                            unit_price="2",
                            unit_type="hour",
                            units="3",
                            base_fee="4",
                            discount="0",
                            testing_fee="4",
                            notes="manual prep",
                        ),
                    ),
                )
            )
        )
    )
    pricing_store = _PricingStore(previous=_previous_pricing_draft())
    service = MatrixFeeRebasePromotionService(
        pending_store=pending_store,
        pricing_draft_store=pricing_store,
    )

    result = service.promote_after_matrix_confirm(_promotion_command())

    assert result.status == "promoted"
    assert pricing_store.saved is not None
    manual_row = pricing_store.saved.edited_values.manual_rows[0]
    assert manual_row.confirmed_group_id == "cmg-new"
    assert manual_row.group_key == "G1"
    assert manual_row.group_label == "Group 1"
    assert manual_row.notes == "manual prep"


def test_service_does_not_delete_pending_when_save_fails() -> None:
    pending_store = _PendingStore(
        _pending_snapshot(
            payload_json=pending_rebase_payload_to_json(
                _rebase_result(active_rows=(_draft_shaped_row(),))
            )
        )
    )
    pricing_store = _PricingStore(previous=_previous_pricing_draft(), fail_save=True)
    service = MatrixFeeRebasePromotionService(
        pending_store=pending_store,
        pricing_draft_store=pricing_store,
    )

    result = service.promote_after_matrix_confirm(_promotion_command())

    assert result.status == "failed"
    assert "Fee rebase promotion failed" in (result.error or "")
    assert pending_store.deleted_matrix_draft_id is None


def test_service_fallback_uses_previous_context_rows_and_preserves_summary() -> None:
    pricing_store = _PricingStore(previous=_previous_pricing_draft(notes="old price"))
    service = MatrixFeeRebasePromotionService(
        pending_store=_PendingStore(None),
        pricing_draft_store=pricing_store,
    )

    result = service.promote_after_matrix_confirm(_promotion_command())

    assert result.status == "fallback_promoted"
    assert pricing_store.saved is not None
    assert pricing_store.saved.edited_values.rows[0].notes == "old price"
    assert pricing_store.saved.edited_values.rows[0].source_line_id == (
        "cmv-new:G1:cmr-new:1:0"
    )
    assert pricing_store.saved.edited_values.summary == (
        pricing_store.previous.edited_values.summary
    )


def test_service_skips_when_no_pending_and_no_previous_pricing_draft() -> None:
    service = MatrixFeeRebasePromotionService(
        pending_store=_PendingStore(None),
        pricing_draft_store=_PricingStore(previous=None),
    )

    result = service.promote_after_matrix_confirm(_promotion_command())

    assert result.status == "skipped"
    assert result.summary is None


def _promotion_command(
    *,
    saved_matrix_draft_payload_signature: str = "sig",
) -> PromoteMatrixFeeRebaseCommand:
    return PromoteMatrixFeeRebaseCommand(
        project_id="P1",
        saved_matrix_draft=_draft(),
        saved_matrix_draft_payload_signature=saved_matrix_draft_payload_signature,
        previous_confirmed_matrix=_confirmed_snapshot("cmv-old", 1, "cmg-old", "cmr-old"),
        new_confirmed_matrix=_confirmed_snapshot("cmv-new", 2, "cmg-new", "cmr-new"),
        fee_rule_version_id="fee-rules-v1",
    )


def _rebase_result(
    *,
    active_rows: tuple[FeeEvaluationEditedExportRow, ...],
    inactive_removed_rows: tuple[MatrixFeeInactiveRemovedRow, ...] = (),
    manual_rows: tuple[FeeEvaluationEditedManualRow, ...] = (),
    summary: MatrixFeeRebaseSummary | None = None,
    warnings: tuple[str, ...] = (),
) -> MatrixFeeRebaseResult:
    return MatrixFeeRebaseResult(
        active_rows=active_rows,
        inactive_removed_rows=inactive_removed_rows,
        manual_rows=manual_rows,
        summary=summary or MatrixFeeRebaseSummary(
            preserved_count=len(active_rows),
            added_count=0,
            removed_count=len(inactive_removed_rows),
        ),
        warnings=warnings,
    )


def _draft_shaped_row(
    *,
    confirmed_group_id: str = "dg-1",
    confirmed_row_id: str = "dr-1",
    step_token: str = "1",
    unit_type: str = "hour",
    notes: str = "",
) -> FeeEvaluationEditedExportRow:
    return FeeEvaluationEditedExportRow(
        source_line_id=f"{confirmed_group_id}:{confirmed_row_id}:{step_token}:0",
        confirmed_group_id=confirmed_group_id,
        confirmed_row_id=confirmed_row_id,
        step_token=step_token,
        step_index=0,
        spend_time="2",
        unit_price="50",
        unit_type=unit_type,
        units="1",
        base_fee="100",
        discount="0",
        testing_fee="100",
        notes=notes,
    )


def _previous_context_row(*, notes: str = "") -> FeeEvaluationEditedExportRow:
    return FeeEvaluationEditedExportRow(
        source_line_id="cmv-old:G1:cmr-old:1:0",
        confirmed_group_id="cmg-old",
        confirmed_row_id="cmr-old",
        step_token="1",
        step_index=0,
        spend_time="2",
        unit_price="50",
        unit_type="hour",
        units="1",
        base_fee="100",
        discount="0",
        testing_fee="100",
        notes=notes,
    )


def _previous_pricing_draft(
    *,
    notes: str = "previous edit",
    summary: FeeEvaluationEditedExportSummary | None = None,
) -> FeeEvaluationPricingDraftSnapshot:
    return FeeEvaluationPricingDraftSnapshot(
        draft_edit_id="pricing-old",
        project_id="P1",
        confirmed_matrix_id="cmv-old",
        confirmed_revision=1,
        fee_rule_version_id="fee-rules-v1",
        edited_values=FeeEvaluationEditedExportValues(
            rows=(_previous_context_row(notes=notes),),
            summary=summary or FeeEvaluationEditedExportSummary(
                condition_confirmation_spend_time="1",
                external_cost="2",
                external_cost_note="external",
                lab_manpower_hourly_rate="3",
            ),
        ),
        created_at="2026-06-15T00:00:00+00:00",
        updated_at="2026-06-15T00:01:00+00:00",
    )


def _pending_snapshot(
    *,
    payload_json: str,
    matrix_draft_payload_signature: str = "sig",
) -> MatrixFeePendingRebaseSnapshot:
    return MatrixFeePendingRebaseSnapshot(
        pending_rebase_id="pending-1",
        project_id="P1",
        project_matrix_draft_id="pmd-1",
        base_confirmed_matrix_id="cmv-old",
        base_confirmed_revision=1,
        fee_rule_version_id="fee-rules-v1",
        matrix_draft_payload_signature=matrix_draft_payload_signature,
        generation=10,
        payload_json=payload_json,
        created_at="2026-06-15T00:00:00+00:00",
        updated_at="2026-06-15T00:01:00+00:00",
    )


def _draft() -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="pmd-1",
            project_id="P1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-06-15T00:00:00+00:00",
            updated_at="2026-06-15T00:01:00+00:00",
            base_confirmed_matrix_id="cmv-old",
        ),
        groups=(
            ProjectMatrixDraftGroup(
                draft_group_id="dg-1",
                project_matrix_draft_id="pmd-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="G1",
                group_label="Group 1",
                is_selected=True,
                sample_quantity_expression="5",
            ),
        ),
        rows=(
            ProjectMatrixDraftRow(
                draft_row_id="dr-1",
                project_matrix_draft_id="pmd-1",
                source_row_snapshot_id="sr-1",
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


def _confirmed_snapshot(
    matrix_id: str,
    revision: int,
    group_id: str,
    row_id: str,
) -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id=matrix_id,
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            confirmed_revision=revision,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-06-15T00:02:00+00:00",
        ),
        groups=(
            ConfirmedMatrixGroup(
                confirmed_group_id=group_id,
                confirmed_matrix_id=matrix_id,
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="G1",
                group_label="Group 1",
                sample_quantity_expression="5",
            ),
        ),
        rows=(
            ConfirmedMatrixRow(
                confirmed_row_id=row_id,
                confirmed_matrix_id=matrix_id,
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual inspection",
            ),
        ),
        cells=(
            ConfirmedMatrixCell(
                confirmed_cell_id=f"cell-{matrix_id}",
                confirmed_matrix_id=matrix_id,
                confirmed_row_id=row_id,
                confirmed_group_id=group_id,
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )


def _confirmed_snapshot_with_added_row() -> ConfirmedMatrixSnapshot:
    snapshot = _confirmed_snapshot("cmv-new", 2, "cmg-new", "cmr-new")
    return ConfirmedMatrixSnapshot(
        version=snapshot.version,
        groups=snapshot.groups,
        rows=snapshot.rows
        + (
            ConfirmedMatrixRow(
                confirmed_row_id="cmr-added",
                confirmed_matrix_id="cmv-new",
                draft_row_id="dr-added",
                source_row_snapshot_id="sr-added",
                row_order=2,
                test_item="Added inspection",
            ),
        ),
        cells=snapshot.cells
        + (
            ConfirmedMatrixCell(
                confirmed_cell_id="cell-added",
                confirmed_matrix_id="cmv-new",
                confirmed_row_id="cmr-added",
                confirmed_group_id="cmg-new",
                draft_row_id="dr-added",
                draft_group_id="dg-1",
                cell_value="2",
            ),
        ),
    )


class _PendingStore:
    def __init__(self, snapshot: MatrixFeePendingRebaseSnapshot | None) -> None:
        self.snapshot = snapshot
        self.deleted_matrix_draft_id: str | None = None

    def get_by_context(
        self,
        *,
        project_matrix_draft_id: str,
        fee_rule_version_id: str,
    ) -> MatrixFeePendingRebaseSnapshot | None:
        if self.snapshot is None:
            return None
        if (
            self.snapshot.project_matrix_draft_id == project_matrix_draft_id
            and self.snapshot.fee_rule_version_id == fee_rule_version_id
        ):
            return self.snapshot
        return None

    def delete_by_matrix_draft(self, project_matrix_draft_id: str) -> int:
        self.deleted_matrix_draft_id = project_matrix_draft_id
        self.snapshot = None
        return 1


class _PricingStore:
    def __init__(
        self,
        *,
        previous: FeeEvaluationPricingDraftSnapshot | None,
        fail_save: bool = False,
    ) -> None:
        self.previous = previous
        self.saved: FeeEvaluationPricingDraftSnapshot | None = None
        self.fail_save = fail_save

    def get_by_context(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        if self.previous is not None and (
            project_id,
            confirmed_matrix_id,
            confirmed_revision,
            fee_rule_version_id,
        ) == (
            self.previous.project_id,
            self.previous.confirmed_matrix_id,
            self.previous.confirmed_revision,
            self.previous.fee_rule_version_id,
        ):
            return self.previous
        return None

    def upsert_current(
        self, snapshot: FeeEvaluationPricingDraftSnapshot
    ) -> FeeEvaluationPricingDraftSnapshot:
        if self.fail_save:
            raise RuntimeError("database unavailable")
        self.saved = snapshot
        return snapshot
