from __future__ import annotations

import pytest

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    MatrixBasicFillHeader,
    MatrixBasicFillWorkbook,
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
    FeeEvaluationPricingDraftPersistenceService,
    SaveFeeEvaluationPricingDraftCommand,
    FeeEvaluationPricingDraftSnapshot,
)
from backend.application.matrix_fee_draft_rebase_service import (
    MatrixFeeInactiveRemovedRow,
    MatrixFeeRebaseKey,
    MatrixFeeRebaseResult,
    MatrixFeeRebaseSummary,
)
from backend.application.matrix_fee_pending_rebase_service import (
    DefaultMatrixFeePendingRebaseBuilder,
    MatrixFeePendingRebaseSnapshot,
    RebaseAfterMatrixAutosaveCommand,
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
from backend.domain.confirmed_fee import ConfirmedFeeVersion


def test_pending_rebase_payload_roundtrips_rows_manual_rows_summary_and_warnings() -> None:
    result = _rebase_result(
        active_rows=(_draft_shaped_row(notes="kept"),),
        inactive_removed_rows=(
            _inactive_removed_row(
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


def test_remap_preserves_inactive_removed_rows_as_hidden_pricing_rows() -> None:
    values = remap_rebase_result_to_confirmed_matrix(
        rebase_result=_rebase_result(
            active_rows=(_draft_shaped_row(notes="active"),),
            inactive_removed_rows=(
                _inactive_removed_row(
                    previous_row=_previous_context_row(notes="hidden edit"),
                    previous_group_key="G1",
                    previous_group_label="Group 1",
                    previous_row_signature="visual inspection",
                ),
            ),
        ),
        previous_pricing_draft=_previous_pricing_draft(),
        new_confirmed_matrix=_confirmed_snapshot("cmv-new", 2, "cmg-new", "cmr-new"),
    )

    assert len(values.inactive_rows) == 1
    hidden = values.inactive_rows[0]
    assert hidden.previous_row.notes == "hidden edit"
    assert hidden.rebase_key.group_identity == "key:g1"
    assert hidden.rebase_key.row_identity == "source:sr-1"
    assert hidden.rebase_key.step_token == "1"
    assert hidden.rebase_key.step_index == 0
    assert hidden.group_key == "G1"
    assert hidden.group_label == "Group 1"
    assert hidden.group_signature == "visual inspection"


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


def test_soft_removed_hidden_rows_survive_autosave_and_restore_when_reselected() -> None:
    soft_removed_values = remap_rebase_result_to_confirmed_matrix(
        rebase_result=_rebase_result(
            active_rows=(),
            inactive_removed_rows=(
                _inactive_removed_row(
                    previous_row=_previous_context_row(notes="recover after autosave"),
                    previous_group_key="G1",
                    previous_group_label="Group 1",
                    previous_row_signature="visual inspection",
                ),
            ),
        ),
        previous_pricing_draft=_previous_pricing_draft(),
        new_confirmed_matrix=_empty_confirmed_snapshot("cmv-soft", 2),
    )
    pricing_store = _PricingStore(
        previous=FeeEvaluationPricingDraftSnapshot(
            draft_edit_id="pricing-soft",
            project_id="P1",
            confirmed_matrix_id="cmv-soft",
            confirmed_revision=2,
            fee_rule_version_id="fee_rules_v2026_08_23_r11",
            edited_values=soft_removed_values,
            created_at="2026-06-15T00:00:00+00:00",
            updated_at="2026-06-15T00:01:00+00:00",
        )
    )
    pricing_service = FeeEvaluationPricingDraftPersistenceService(
        basic_fill_service=_BasicFillService(
            confirmed_matrix_id="cmv-soft",
            confirmed_revision=2,
        ),
        draft_store=pricing_store,
    )

    autosaved = pricing_service.save(
        SaveFeeEvaluationPricingDraftCommand(
            project_id="P1",
            edited_values=FeeEvaluationEditedExportValues(
                rows=(),
                summary=soft_removed_values.summary,
            ),
        )
    )

    assert autosaved.saved_snapshot is not None
    assert autosaved.saved_snapshot.edited_values.inactive_rows == (
        soft_removed_values.inactive_rows
    )

    restored = DefaultMatrixFeePendingRebaseBuilder(
        basic_fill_service=_BasicFillService(
            confirmed_matrix_id="cmv-soft",
            confirmed_revision=2,
        ),
        pricing_draft_store=pricing_store,
    ).build_and_rebase(
        RebaseAfterMatrixAutosaveCommand(
            project_id="P1",
            active_confirmed_matrix_id="cmv-soft",
            active_confirmed_revision=2,
            saved_matrix_draft=_draft(base_confirmed_matrix_id="cmv-soft"),
            saved_payload_signature="sig",
            fee_rule_version_id="fee_rules_v2026_08_23_r11",
            generation=11,
        )
    )

    assert restored.summary.preserved_count == 1
    assert restored.active_rows[0].notes == "recover after autosave"
    assert restored.active_rows[0].unit_price == "50"


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


def test_service_creates_default_fee_authority_when_no_previous_pricing_draft() -> None:
    pricing_store = _PricingStore(previous=None)
    fee_store = _ConfirmedFeeStore()
    service = MatrixFeeRebasePromotionService(
        pending_store=_PendingStore(None),
        pricing_draft_store=pricing_store,
        confirmed_fee_store=fee_store,
    )

    result = service.promote_after_matrix_confirm(_promotion_command())

    assert result.status == "default_promoted"
    assert result.summary is None
    assert pricing_store.saved is not None
    assert pricing_store.saved.confirmed_matrix_id == "cmv-new"
    assert pricing_store.saved.confirmed_revision == 2
    assert pricing_store.saved.edited_values.rows[0].source_line_id == (
        "cmv-new:G1:cmr-new:1:0"
    )
    assert pricing_store.saved.edited_values.manual_rows[0].row_kind == (
        "sample_preparation"
    )
    assert fee_store.versions
    assert fee_store.versions[0].confirmed_matrix_id == "cmv-new"
    assert fee_store.versions[0].pricing_draft_edit_id == pricing_store.saved.draft_edit_id
    assert fee_store.versions[0].summary.testing_fee_total == "0.00"


def test_service_initializes_default_fee_authority_after_first_matrix_confirm() -> None:
    pricing_store = _PricingStore(previous=None)
    fee_store = _ConfirmedFeeStore()
    service = MatrixFeeRebasePromotionService(
        pending_store=_PendingStore(None),
        pricing_draft_store=pricing_store,
        confirmed_fee_store=fee_store,
    )

    result = service.initialize_after_first_matrix_confirm(
        project_id="P1",
        new_confirmed_matrix=_confirmed_snapshot("cmv-first", 1, "cmg-first", "cmr-first"),
        fee_rule_version_id="fee-rules-v1",
    )

    assert result.status == "default_promoted"
    assert pricing_store.saved is not None
    assert pricing_store.saved.confirmed_matrix_id == "cmv-first"
    assert pricing_store.saved.confirmed_revision == 1
    assert fee_store.versions[0].confirmed_matrix_id == "cmv-first"
    assert fee_store.versions[0].confirmed_fee_revision == 1


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


def _inactive_removed_row(
    *,
    previous_row: FeeEvaluationEditedExportRow,
    previous_group_key: str,
    previous_group_label: str,
    previous_row_signature: str,
) -> MatrixFeeInactiveRemovedRow:
    return MatrixFeeInactiveRemovedRow(
        previous_row=previous_row,
        rebase_key=MatrixFeeRebaseKey(
            group_identity="key:g1",
            row_identity="source:sr-1",
            step_token="1",
            step_index=0,
        ),
        previous_group_key=previous_group_key,
        previous_group_label=previous_group_label,
        previous_row_signature=previous_row_signature,
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


def _draft(
    *,
    base_confirmed_matrix_id: str = "cmv-old",
) -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="pmd-1",
            project_id="P1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-06-15T00:00:00+00:00",
            updated_at="2026-06-15T00:01:00+00:00",
            base_confirmed_matrix_id=base_confirmed_matrix_id,
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


def _empty_confirmed_snapshot(matrix_id: str, revision: int) -> ConfirmedMatrixSnapshot:
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
        groups=(),
        rows=(),
        cells=(),
    )


class _BasicFillService:
    def __init__(
        self,
        *,
        confirmed_matrix_id: str,
        confirmed_revision: int,
    ) -> None:
        self._confirmed_matrix_id = confirmed_matrix_id
        self._confirmed_revision = confirmed_revision

    def build(self, command) -> MatrixBasicFillWorkbook:
        return MatrixBasicFillWorkbook(
            header=MatrixBasicFillHeader(
                project_id="P1",
                confirmed_matrix_id=self._confirmed_matrix_id,
                confirmed_revision=self._confirmed_revision,
                generated_at="2026-06-15T00:03:00+00:00",
            ),
            status="ready",
            groups=(),
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
        for candidate in (self.saved, self.previous):
            if candidate is not None and (
                project_id,
                confirmed_matrix_id,
                confirmed_revision,
                fee_rule_version_id,
            ) == (
                candidate.project_id,
                candidate.confirmed_matrix_id,
                candidate.confirmed_revision,
                candidate.fee_rule_version_id,
            ):
                return candidate
        return None

    def upsert_current(
        self, snapshot: FeeEvaluationPricingDraftSnapshot
    ) -> FeeEvaluationPricingDraftSnapshot:
        if self.fail_save:
            raise RuntimeError("database unavailable")
        self.saved = snapshot
        return snapshot


class _ConfirmedFeeStore:
    def __init__(self) -> None:
        self.versions: list[ConfirmedFeeVersion] = []

    def create(self, version: ConfirmedFeeVersion) -> ConfirmedFeeVersion:
        self.versions.append(version)
        return version

    def get_latest_by_project(self, project_id: str) -> ConfirmedFeeVersion | None:
        versions = [version for version in self.versions if version.project_id == project_id]
        return versions[-1] if versions else None

    def list_by_project(self, project_id: str) -> tuple[ConfirmedFeeVersion, ...]:
        return tuple(version for version in self.versions if version.project_id == project_id)
