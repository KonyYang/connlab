from __future__ import annotations

import pytest

from backend.application.confirmed_fee_version_service import (
    ConfirmFeeVersionCommand,
    ConfirmedFeePricingDraftChangedError,
    ConfirmedFeePricingDraftMissingError,
    ConfirmedFeePricingDraftStaleError,
    ConfirmedFeeSummaryValidationError,
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


def test_confirm_fee_creates_revision_bound_to_expected_saved_pricing_draft() -> None:
    store = _ConfirmedFeeStore()
    service = _service(store=store)

    created = service.confirm(
        ConfirmFeeVersionCommand(
            project_id="P1",
            confirmed_by="Lab User",
            expected_pricing_draft_edit_id="fed-1",
            summary=_summary(testing_fee_total="41"),
            confirmation_note="ready",
        )
    )

    assert created.confirmed_fee_revision == 1
    assert created.confirmed_matrix_id == "cmv-1"
    assert created.confirmed_revision == 1
    assert created.fee_rule_version_id == "fee_rules_v2026_06_03"
    assert created.pricing_draft_edit_id == "fed-1"
    assert created.pricing_effective_from is None
    assert created.summary.testing_fee_total == "41"
    assert created.confirmed_by == "Lab User"
    assert created.confirmed_at == "2026-06-10T09:00:00+00:00"
    assert created.confirmation_note == "ready"
    assert '"operator note"' in created.pricing_snapshot_json


def test_confirm_fee_creates_ordered_revision_history() -> None:
    store = _ConfirmedFeeStore()
    service = _service(store=store)

    first = service.confirm(_command(testing_fee_total="41"))
    second = service.confirm(_command(testing_fee_total="52"))

    assert first.confirmed_fee_revision == 1
    assert second.confirmed_fee_revision == 2
    assert store.list_by_project("P1") == (first, second)


def test_confirm_fee_rejects_missing_pricing_draft() -> None:
    service = _service(
        load_result=FeeEvaluationPricingDraftLoadResult(
            status="missing",
            current_context=_context(),
            saved_snapshot=None,
        )
    )

    with pytest.raises(ConfirmedFeePricingDraftMissingError, match="Save Fee Evaluation"):
        service.confirm(_command())


def test_confirm_fee_rejects_stale_pricing_draft() -> None:
    service = _service(
        load_result=FeeEvaluationPricingDraftLoadResult(
            status="stale",
            current_context=_context(confirmed_revision=2),
            saved_snapshot=_pricing_snapshot(),
        )
    )

    with pytest.raises(ConfirmedFeePricingDraftStaleError, match="refresh"):
        service.confirm(_command())


def test_confirm_fee_rejects_changed_pricing_draft_id() -> None:
    service = _service()

    with pytest.raises(ConfirmedFeePricingDraftChangedError, match="changed"):
        service.confirm(
            ConfirmFeeVersionCommand(
                project_id="P1",
                confirmed_by="Lab User",
                expected_pricing_draft_edit_id="old-fed",
                summary=_summary(),
            )
        )


def test_confirm_fee_rejects_non_numeric_summary() -> None:
    service = _service()

    with pytest.raises(ConfirmedFeeSummaryValidationError, match="grand_cost"):
        service.confirm(_command(grand_cost="Pending"))


def test_confirm_fee_rejects_blank_confirmed_by() -> None:
    service = _service()

    with pytest.raises(ConfirmedFeeSummaryValidationError, match="confirmed_by"):
        service.confirm(
            ConfirmFeeVersionCommand(
                project_id="P1",
                confirmed_by="   ",
                expected_pricing_draft_edit_id="fed-1",
                summary=_summary(),
            )
        )


def test_confirm_fee_read_model_reports_missing_current_and_stale() -> None:
    store = _ConfirmedFeeStore()
    service = _service(store=store)

    missing = service.get_latest("P1")
    created = service.confirm(_command())
    current = service.get_latest("P1")
    stale = _service(
        store=store,
        load_result=FeeEvaluationPricingDraftLoadResult(
            status="current",
            current_context=_context(fee_rule_version_id="fee_rules_vNEXT"),
            saved_snapshot=_pricing_snapshot(fee_rule_version_id="fee_rules_vNEXT"),
        ),
    ).get_latest("P1")

    assert missing.status == "missing"
    assert missing.latest_confirmed_fee is None
    assert current.status == "current"
    assert current.latest_confirmed_fee == created
    assert stale.status == "stale"
    assert stale.latest_confirmed_fee == created


def _service(
    *,
    store: "_ConfirmedFeeStore | None" = None,
    load_result: FeeEvaluationPricingDraftLoadResult | None = None,
) -> ConfirmedFeeVersionService:
    return ConfirmedFeeVersionService(
        pricing_draft_loader=_PricingDraftLoader(load_result or _current_load_result()),
        confirmed_fee_store=store or _ConfirmedFeeStore(),
        clock=lambda: "2026-06-10T09:00:00+00:00",
        id_factory=lambda: "cfv-id",
    )


def _command(
    *,
    testing_fee_total: str = "41",
    grand_cost: str = "191",
) -> ConfirmFeeVersionCommand:
    return ConfirmFeeVersionCommand(
        project_id="P1",
        confirmed_by="Lab User",
        expected_pricing_draft_edit_id="fed-1",
        summary=_summary(testing_fee_total=testing_fee_total, grand_cost=grand_cost),
    )


def _summary(
    *,
    testing_fee_total: str = "41",
    grand_cost: str = "191",
) -> ConfirmedFeeSummary:
    return ConfirmedFeeSummary(
        testing_fee_total=testing_fee_total,
        working_hours="1.5",
        lab_manpower_cost="300",
        external_cost="150",
        grand_cost=grand_cost,
    )


def _current_load_result() -> FeeEvaluationPricingDraftLoadResult:
    return FeeEvaluationPricingDraftLoadResult(
        status="current",
        current_context=_context(),
        saved_snapshot=_pricing_snapshot(),
    )


def _context(
    *,
    confirmed_revision: int = 1,
    fee_rule_version_id: str = "fee_rules_v2026_06_03",
) -> FeeEvaluationPricingDraftContext:
    return FeeEvaluationPricingDraftContext(
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=confirmed_revision,
        fee_rule_version_id=fee_rule_version_id,
    )


def _pricing_snapshot(
    *,
    fee_rule_version_id: str = "fee_rules_v2026_06_03",
) -> FeeEvaluationPricingDraftSnapshot:
    return FeeEvaluationPricingDraftSnapshot(
        draft_edit_id="fed-1",
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id=fee_rule_version_id,
        edited_values=FeeEvaluationEditedExportValues(
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
        ),
        created_at="2026-06-09T09:00:00+00:00",
        updated_at="2026-06-09T09:10:00+00:00",
    )


class _PricingDraftLoader:
    def __init__(self, result: FeeEvaluationPricingDraftLoadResult) -> None:
        self.result = result

    def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
        return self.result


class _ConfirmedFeeStore:
    def __init__(self) -> None:
        self.versions: list[ConfirmedFeeVersion] = []

    def create(self, version: ConfirmedFeeVersion) -> ConfirmedFeeVersion:
        self.versions.append(version)
        return version

    def get_latest_by_project(self, project_id: str) -> ConfirmedFeeVersion | None:
        matches = [item for item in self.versions if item.project_id == project_id]
        return matches[-1] if matches else None

    def list_by_project(self, project_id: str) -> tuple[ConfirmedFeeVersion, ...]:
        return tuple(item for item in self.versions if item.project_id == project_id)
