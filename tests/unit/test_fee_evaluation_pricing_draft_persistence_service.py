from __future__ import annotations

from dataclasses import replace
import pytest

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    ConfirmedMatrixFeeTemplateBasicFillService,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedManualRow,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftPersistenceService,
    FeeEvaluationPricingDraftSnapshot,
    SaveFeeEvaluationPricingDraftCommand,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)


def test_save_then_load_current_pricing_draft_preserves_notes() -> None:
    store = _DraftStore()
    service = _service(store=store)
    values = _edited_values(notes="discount reason")

    saved = service.save(
        SaveFeeEvaluationPricingDraftCommand(project_id="P1", edited_values=values)
    )
    loaded = service.load("P1")

    assert saved.status == "current"
    assert loaded.status == "current"
    assert loaded.saved_snapshot is not None
    assert loaded.saved_snapshot.confirmed_matrix_id == "cmv-1"
    assert loaded.saved_snapshot.confirmed_revision == 1
    assert loaded.saved_snapshot.fee_rule_version_id == "fee_rules_v2026_06_03"
    assert loaded.saved_snapshot.edited_values.rows[0].notes == "discount reason"
    assert loaded.saved_snapshot.edited_values.manual_rows[0].row_kind == (
        "sample_preparation"
    )
    assert loaded.saved_snapshot.edited_values.manual_rows[0].confirmed_group_id == "cmg-1"
    assert loaded.saved_snapshot.edited_values.manual_rows[0].notes == "sample prep note"
    assert loaded.saved_snapshot.edited_values.summary.external_cost_note == "tooling"


def test_load_missing_pricing_draft_returns_missing() -> None:
    result = _service(store=_DraftStore()).load("P1")

    assert result.status == "missing"
    assert result.saved_snapshot is None


def test_load_reports_stale_when_confirmed_matrix_revision_differs() -> None:
    store = _DraftStore()
    current = _service(store=store)
    current.save(
        SaveFeeEvaluationPricingDraftCommand(
            project_id="P1",
            edited_values=_edited_values(),
        )
    )
    revised = _service(store=store, snapshot=_snapshot(confirmed_revision=2))

    result = revised.load("P1")

    assert result.status == "stale"
    assert result.current_context.confirmed_revision == 2
    assert result.saved_snapshot is not None
    assert result.saved_snapshot.confirmed_revision == 1


def test_load_reports_stale_when_fee_rule_version_differs() -> None:
    store = _DraftStore()
    current = _service(store=store)
    current.save(
        SaveFeeEvaluationPricingDraftCommand(
            project_id="P1",
            edited_values=_edited_values(),
        )
    )
    assert store.snapshot is not None
    store.snapshot = replace(store.snapshot, fee_rule_version_id="old_fee_rules")

    result = current.load("P1")

    assert result.status == "stale"
    assert result.current_context.fee_rule_version_id == "fee_rules_v2026_06_03"
    assert result.saved_snapshot is not None
    assert result.saved_snapshot.fee_rule_version_id == "old_fee_rules"
    assert result.saved_snapshot.edited_values.rows[0].unit_price == "20"


def test_save_rejects_unknown_row_identity() -> None:
    service = _service(store=_DraftStore())

    with pytest.raises(ValueError, match="not found"):
        service.save(
            SaveFeeEvaluationPricingDraftCommand(
                project_id="P1",
                edited_values=_edited_values(confirmed_row_id="missing"),
            )
        )


def test_save_rejects_duplicate_row_identity() -> None:
    row = _edited_row()
    service = _service(store=_DraftStore())

    with pytest.raises(ValueError, match="Duplicate"):
        service.save(
            SaveFeeEvaluationPricingDraftCommand(
                project_id="P1",
                edited_values=FeeEvaluationEditedExportValues(
                    rows=(row, row),
                    summary=_summary(),
                ),
            )
        )


def _service(
    *,
    store: "_DraftStore",
    snapshot: ConfirmedMatrixSnapshot | None = None,
) -> FeeEvaluationPricingDraftPersistenceService:
    return FeeEvaluationPricingDraftPersistenceService(
        basic_fill_service=ConfirmedMatrixFeeTemplateBasicFillService(
            confirmed_store=_ConfirmedStore(snapshot or _snapshot())
        ),
        draft_store=store,
    )


def _edited_values(
    *,
    confirmed_row_id: str = "cmr-visual",
    notes: str = "",
) -> FeeEvaluationEditedExportValues:
    return FeeEvaluationEditedExportValues(
        rows=(_edited_row(confirmed_row_id=confirmed_row_id, notes=notes),),
        summary=_summary(),
        manual_rows=(
            FeeEvaluationEditedManualRow(
                row_kind="sample_preparation",
                confirmed_group_id="cmg-1",
                group_key="g1",
                group_label="Group 1",
                spend_time="0.25",
                unit_price="15",
                unit_type="per sample",
                units="5",
                base_fee="2",
                discount="5%",
                testing_fee="73.25",
                notes="sample prep note",
            ),
        ),
    )


def _edited_row(
    *,
    confirmed_row_id: str = "cmr-visual",
    notes: str = "",
) -> FeeEvaluationEditedExportRow:
    return FeeEvaluationEditedExportRow(
        source_line_id=f"cmv-1:g1:{confirmed_row_id}:1:0",
        confirmed_group_id="cmg-1",
        confirmed_row_id=confirmed_row_id,
        step_token="1",
        step_index=0,
        spend_time="1.5",
        unit_price="20",
        unit_type="per sample",
        units="2",
        base_fee="5",
        discount="10%",
        testing_fee="41",
        notes=notes,
    )


def _summary() -> FeeEvaluationEditedExportSummary:
    return FeeEvaluationEditedExportSummary(
        condition_confirmation_spend_time="0.5",
        external_cost="150",
        external_cost_note="tooling",
        lab_manpower_hourly_rate="200",
    )


def _snapshot(*, confirmed_revision: int = 1) -> ConfirmedMatrixSnapshot:
    row = ConfirmedMatrixRow(
        confirmed_row_id="cmr-visual",
        confirmed_matrix_id="cmv-1",
        draft_row_id="pmdr-visual",
        source_row_snapshot_id="smr-visual",
        row_order=1,
        test_item="Visual Examination",
    )
    group = ConfirmedMatrixGroup(
        confirmed_group_id="cmg-1",
        confirmed_matrix_id="cmv-1",
        draft_group_id="pmdg-1",
        source_group_snapshot_id="smg-1",
        group_order=1,
        group_key="g1",
        group_label="Group 1",
        sample_quantity_expression="5",
    )
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="cmv-1",
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            confirmed_revision=confirmed_revision,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-06-04T10:00:00+08:00",
            sample_received_date="2026-06-03",
        ),
        groups=(group,),
        rows=(row,),
        cells=(
            ConfirmedMatrixCell(
                confirmed_cell_id="cmc-visual",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id=row.confirmed_row_id,
                confirmed_group_id=group.confirmed_group_id,
                draft_row_id=row.draft_row_id,
                draft_group_id=group.draft_group_id,
                cell_value="1 X",
            ),
        ),
    )


class _ConfirmedStore:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot) -> None:
        self.snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        return self.snapshot


class _DraftStore:
    def __init__(self) -> None:
        self.snapshot: FeeEvaluationPricingDraftSnapshot | None = None

    def upsert_current(
        self, snapshot: FeeEvaluationPricingDraftSnapshot
    ) -> FeeEvaluationPricingDraftSnapshot:
        self.snapshot = snapshot
        return snapshot

    def get_latest_by_project(
        self, project_id: str
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        return self.snapshot if self.snapshot and self.snapshot.project_id == project_id else None
