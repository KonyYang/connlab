from __future__ import annotations

from dataclasses import replace
import pytest

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    ConfirmedMatrixFeeTemplateBasicFillService,
)
from backend.application import fee_evaluation_edited_export_values as edited_values_module
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedManualRow,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    DiscardFeeEvaluationPricingDraftCommand,
    FeeEvaluationPricingDraftConflictError,
    FeeEvaluationPricingDraftPersistenceService,
    FeeEvaluationPricingDraftSnapshot,
    SaveFeeEvaluationPricingDraftCommand,
    edited_values_from_json,
    edited_values_to_json,
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

    assert saved.status == "current_v2"
    assert loaded.status == "current_v2"
    assert loaded.saved_snapshot is not None
    assert loaded.saved_snapshot.confirmed_matrix_id == "cmv-1"
    assert loaded.saved_snapshot.confirmed_revision == 1
    assert loaded.saved_snapshot.fee_rule_version_id == "fee_rules_v2026_08_23_r11"
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


def test_load_blocks_when_only_old_confirmed_matrix_revision_draft_exists() -> None:
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

    assert result.status == "blocked"
    assert result.current_context.confirmed_revision == 2
    assert result.saved_snapshot is None


def test_load_blocks_when_only_unknown_fee_rule_version_draft_exists() -> None:
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

    assert result.status == "blocked"
    assert result.current_context.fee_rule_version_id == "fee_rules_v2026_08_23_r11"
    assert result.saved_snapshot is None


def test_load_uses_current_context_when_newer_stale_row_exists() -> None:
    current_snapshot = _pricing_snapshot(updated_at="2026-06-14T09:00:00+00:00")
    stale_snapshot = _pricing_snapshot(
        draft_edit_id="fed-stale",
        confirmed_matrix_id="old-cmv",
        updated_at="2026-06-14T10:00:00+00:00",
    )
    store = _DraftStore(snapshots=(current_snapshot, stale_snapshot))
    service = _service(store=store)

    result = service.load("P1")

    assert result.status == "legacy_unclassified"
    assert result.saved_snapshot is not None
    assert result.saved_snapshot.draft_edit_id == "fed-1"


def test_save_rejects_mismatched_expected_context_before_upsert() -> None:
    store = _DraftStore()
    service = _service(store=store)

    with pytest.raises(
        FeeEvaluationPricingDraftConflictError,
        match="Matrix context changed before save",
    ):
        service.save(
            SaveFeeEvaluationPricingDraftCommand(
                project_id="P1",
                edited_values=_edited_values(),
                expected_confirmed_matrix_id="cmv-old",
                expected_confirmed_revision=1,
                expected_fee_rule_version_id="fee_rules_v2026_08_23_r11",
            )
        )

    assert store.snapshot is None


def test_discard_current_pricing_draft_deletes_matching_context() -> None:
    store = _DraftStore(snapshots=(_pricing_snapshot(),))
    service = _service(store=store)

    result = service.discard(
        DiscardFeeEvaluationPricingDraftCommand(
            project_id="P1",
            expected_pricing_draft_edit_id="fed-1",
            expected_confirmed_matrix_id="cmv-1",
            expected_confirmed_revision=1,
                expected_fee_rule_version_id="fee_rules_v2026_08_23_r11",
        )
    )

    assert result.discarded is True
    assert store.deleted_context == (
        "P1",
        "cmv-1",
        1,
        "fee_rules_v2026_08_23_r11",
    )


def test_discard_rejects_mismatched_pricing_draft_id() -> None:
    service = _service(store=_DraftStore(snapshots=(_pricing_snapshot(),)))

    with pytest.raises(FeeEvaluationPricingDraftConflictError):
        service.discard(
            DiscardFeeEvaluationPricingDraftCommand(
                project_id="P1",
                expected_pricing_draft_edit_id="fed-other",
            )
        )


def test_discard_uses_current_context_when_newer_stale_row_exists() -> None:
    current_snapshot = _pricing_snapshot(updated_at="2026-06-14T09:00:00+00:00")
    stale_snapshot = _pricing_snapshot(
        draft_edit_id="fed-stale",
        confirmed_matrix_id="old-cmv",
        updated_at="2026-06-14T10:00:00+00:00",
    )
    store = _DraftStore(snapshots=(current_snapshot, stale_snapshot))
    service = _service(store=store)

    result = service.discard(DiscardFeeEvaluationPricingDraftCommand(project_id="P1"))

    assert result.discarded is True
    assert store.deleted_context == ("P1", "cmv-1", 1, "fee_rules_v2026_08_23_r11")


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


def test_save_preserves_existing_hidden_inactive_rows_when_request_has_active_rows_only() -> None:
    existing_values = FeeEvaluationEditedExportValues(
        rows=(_edited_row(notes="existing active"),),
        summary=_summary(),
        inactive_rows=(
            _inactive_row(notes="hidden from matrix soft remove"),
        ),
    )
    store = _DraftStore(
        snapshots=(
            _pricing_snapshot_with_values(
                draft_edit_id="fed-existing",
                edited_values=existing_values,
            ),
        )
    )
    service = _service(store=store)
    incoming_values = FeeEvaluationEditedExportValues(
        rows=(_edited_row(notes="autosaved active"),),
        summary=_summary(),
        manual_rows=(),
    )

    saved = service.save(
        SaveFeeEvaluationPricingDraftCommand(
            project_id="P1",
            edited_values=incoming_values,
        )
    )

    assert saved.saved_snapshot is not None
    assert saved.saved_snapshot.draft_edit_id == "fed-existing"
    assert saved.saved_snapshot.edited_values.rows[0].notes == "autosaved active"
    assert saved.saved_snapshot.edited_values.inactive_rows == (
        _inactive_row(notes="hidden from matrix soft remove"),
    )


def test_edited_values_json_round_trips_hidden_inactive_rows() -> None:
    inactive_row_type = getattr(
        edited_values_module,
        "FeeEvaluationEditedInactiveRow",
        None,
    )
    inactive_key_type = getattr(
        edited_values_module,
        "FeeEvaluationEditedInactiveRowKey",
        None,
    )
    assert inactive_row_type is not None
    assert inactive_key_type is not None
    values = FeeEvaluationEditedExportValues(
        rows=(_edited_row(notes="active"),),
        summary=_summary(),
        inactive_rows=(
            inactive_row_type(
                previous_row=_edited_row(confirmed_row_id="old-row", notes="hidden"),
                rebase_key=inactive_key_type(
                    group_identity="key:g1",
                    row_identity="source:smr-1",
                    step_token="1",
                    step_index=0,
                ),
                group_key="g1",
                group_label="Group 1",
                group_signature="group 1",
            ),
        ),
    )

    loaded = edited_values_from_json(edited_values_to_json(values))

    assert loaded.rows == values.rows
    assert loaded.summary == values.summary
    assert loaded.manual_rows == values.manual_rows
    assert loaded.inactive_rows == values.inactive_rows


def test_edited_values_json_defaults_legacy_payload_to_no_inactive_rows() -> None:
    values = FeeEvaluationEditedExportValues(
        rows=(_edited_row(),),
        summary=_summary(),
        manual_rows=(),
    )

    loaded = edited_values_from_json(edited_values_to_json(values))

    assert loaded.inactive_rows == ()


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


def _inactive_row(*, notes: str = "hidden") -> edited_values_module.FeeEvaluationEditedInactiveRow:
    inactive_row_type = getattr(edited_values_module, "FeeEvaluationEditedInactiveRow")
    inactive_key_type = getattr(edited_values_module, "FeeEvaluationEditedInactiveRowKey")
    return inactive_row_type(
        previous_row=_edited_row(confirmed_row_id="old-row", notes=notes),
        rebase_key=inactive_key_type(
            group_identity="key:g1",
            row_identity="source:smr-1",
            step_token="1",
            step_index=0,
        ),
        group_key="g1",
        group_label="Group 1",
        group_signature="group 1",
    )


def _summary() -> FeeEvaluationEditedExportSummary:
    return FeeEvaluationEditedExportSummary(
        condition_confirmation_spend_time="0.5",
        external_cost="150",
        external_cost_note="tooling",
        lab_manpower_hourly_rate="200",
    )


def _pricing_snapshot(
    *,
    draft_edit_id: str = "fed-1",
    project_id: str = "P1",
    confirmed_matrix_id: str = "cmv-1",
    confirmed_revision: int = 1,
    fee_rule_version_id: str = "fee_rules_v2026_08_23_r11",
    updated_at: str = "2026-06-09T09:10:00+00:00",
) -> FeeEvaluationPricingDraftSnapshot:
    return FeeEvaluationPricingDraftSnapshot(
        draft_edit_id=draft_edit_id,
        project_id=project_id,
        confirmed_matrix_id=confirmed_matrix_id,
        confirmed_revision=confirmed_revision,
        fee_rule_version_id=fee_rule_version_id,
        edited_values=_edited_values(),
        created_at="2026-06-09T09:00:00+00:00",
        updated_at=updated_at,
    )


def _pricing_snapshot_with_values(
    *,
    draft_edit_id: str,
    edited_values: FeeEvaluationEditedExportValues,
) -> FeeEvaluationPricingDraftSnapshot:
    return FeeEvaluationPricingDraftSnapshot(
        draft_edit_id=draft_edit_id,
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id="fee_rules_v2026_08_23_r11",
        edited_values=edited_values,
        created_at="2026-06-09T09:00:00+00:00",
        updated_at="2026-06-09T09:10:00+00:00",
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
    def __init__(
        self, snapshots: tuple[FeeEvaluationPricingDraftSnapshot, ...] = ()
    ) -> None:
        self.snapshots = {
            (
                snapshot.project_id,
                snapshot.confirmed_matrix_id,
                snapshot.confirmed_revision,
                snapshot.fee_rule_version_id,
            ): snapshot
            for snapshot in snapshots
        }
        self.deleted_context: tuple[str, str, int, str] | None = None

    @property
    def snapshot(self) -> FeeEvaluationPricingDraftSnapshot | None:
        return self.get_latest_by_project("P1")

    @snapshot.setter
    def snapshot(self, value: FeeEvaluationPricingDraftSnapshot | None) -> None:
        self.snapshots.clear()
        if value is not None:
            self.upsert_current(value)

    def upsert_current(
        self, snapshot: FeeEvaluationPricingDraftSnapshot
    ) -> FeeEvaluationPricingDraftSnapshot:
        self.snapshots[
            (
                snapshot.project_id,
                snapshot.confirmed_matrix_id,
                snapshot.confirmed_revision,
                snapshot.fee_rule_version_id,
            )
        ] = snapshot
        return snapshot

    def get_latest_by_project(
        self, project_id: str
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        matching = [
            snapshot
            for snapshot in self.snapshots.values()
            if snapshot.project_id == project_id
        ]
        return max(matching, key=lambda snapshot: snapshot.updated_at, default=None)

    def get_by_context(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        return self.snapshots.get(
            (
                project_id,
                confirmed_matrix_id,
                confirmed_revision,
                fee_rule_version_id,
            )
        )

    def delete_current(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> bool:
        key = (
            project_id,
            confirmed_matrix_id,
            confirmed_revision,
            fee_rule_version_id,
        )
        self.deleted_context = key
        return self.snapshots.pop(key, None) is not None
