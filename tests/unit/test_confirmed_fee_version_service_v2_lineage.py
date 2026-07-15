from __future__ import annotations

import pytest

from backend.application.confirmed_fee_version_service import (
    ConfirmFeeVersionCommand,
    ConfirmedFeePricingDraftChangedError,
    ConfirmedFeeVersionService,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftContext,
    FeeEvaluationPricingDraftLoadResult,
    FeeEvaluationPricingDraftSnapshot,
)
from backend.domain.confirmed_fee import ConfirmedFeeSummary, ConfirmedFeeVersion


def test_missing_v2_attestation_rejects_confirm_without_write() -> None:
    store = _Store()

    with pytest.raises(ConfirmedFeePricingDraftChangedError, match="changed"):
        _service(store, _load_result()).confirm(_command(token=None))

    assert store.versions == []


def test_mismatched_v2_attestation_rejects_confirm_without_write() -> None:
    store = _Store()

    with pytest.raises(ConfirmedFeePricingDraftChangedError, match="changed"):
        _service(store, _load_result()).confirm(_command(generation=2))

    assert store.versions == []


def test_exact_v2_confirm_is_idempotent_and_persists_full_lineage() -> None:
    store = _Store()
    service = _service(store, _load_result())

    first = service.confirm(_command())
    repeated = service.confirm(_command())

    assert repeated == first
    assert len(store.versions) == 1
    assert '"generation":1' in first.pricing_snapshot_json
    assert '"source_context_fingerprint":"source-fingerprint-1"' in first.pricing_snapshot_json


def test_same_draft_newer_generation_blocks_required_forms_currentness_gate() -> None:
    store = _Store()
    confirmed = _service(store, _load_result()).confirm(_command())

    result = _service(store, _load_result(generation=2)).get_latest("P1")

    assert result.latest_confirmed_fee == confirmed
    assert result.status == "stale"


def _service(store: "_Store", load_result: FeeEvaluationPricingDraftLoadResult) -> ConfirmedFeeVersionService:
    return ConfirmedFeeVersionService(
        pricing_draft_loader=_Loader(load_result),
        confirmed_fee_store=store,
        clock=lambda: "2026-07-15T00:00:00+00:00",
        id_factory=lambda: "cfv-1",
    )


def _command(
    *, generation: int | None = 1, token: str | None = "validation-token-1"
) -> ConfirmFeeVersionCommand:
    return ConfirmFeeVersionCommand(
        project_id="P1",
        confirmed_by="Lab User",
        expected_pricing_draft_edit_id="fed-1",
        summary=ConfirmedFeeSummary(
            testing_fee_total="41",
            working_hours="1.5",
            lab_manpower_cost="300",
            external_cost="150",
            grand_cost="191",
        ),
        expected_generation=generation,
        expected_payload_fingerprint="payload-fingerprint-1",
        expected_validation_token=token,
    )


def _load_result(*, generation: int = 1) -> FeeEvaluationPricingDraftLoadResult:
    values = FeeEvaluationEditedExportValues(
        rows=(
            FeeEvaluationEditedExportRow(
                source_line_id="line-1",
                confirmed_group_id="group-1",
                confirmed_row_id="row-1",
                step_token="1",
                step_index=0,
                spend_time="1.5",
                unit_price="20",
                unit_type="per sample",
                units="2",
                base_fee="5",
                discount="10%",
                testing_fee="41",
                notes="operator note",
            ),
        ),
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time="0",
            external_cost="150",
            external_cost_note="tooling",
            lab_manpower_hourly_rate="200",
        ),
    )
    snapshot = FeeEvaluationPricingDraftSnapshot(
        draft_edit_id="fed-1",
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id="fee_rules_v2026_06_03",
        edited_values=values,
        created_at="2026-07-15T00:00:00+00:00",
        updated_at="2026-07-15T00:00:00+00:00",
        generation=generation,
        payload_fingerprint=f"payload-fingerprint-{generation}",
        source_context_fingerprint=f"source-fingerprint-{generation}",
        validation_token=f"validation-token-{generation}",
    )
    return FeeEvaluationPricingDraftLoadResult(
        status="current_v2",
        current_context=FeeEvaluationPricingDraftContext(
            project_id="P1",
            confirmed_matrix_id="cmv-1",
            confirmed_revision=1,
            fee_rule_version_id="fee_rules_v2026_06_03",
        ),
        saved_snapshot=snapshot,
    )


class _Loader:
    def __init__(self, result: FeeEvaluationPricingDraftLoadResult) -> None:
        self._result = result

    def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
        return self._result


class _Store:
    def __init__(self) -> None:
        self.versions: list[ConfirmedFeeVersion] = []

    def create(self, version: ConfirmedFeeVersion) -> ConfirmedFeeVersion:
        self.versions.append(version)
        return version

    def get_latest_by_project(self, project_id: str) -> ConfirmedFeeVersion | None:
        return self.versions[-1] if self.versions else None

    def list_by_project(self, project_id: str) -> tuple[ConfirmedFeeVersion, ...]:
        return tuple(self.versions)
