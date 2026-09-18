"""Shared acceptance samples for the Fee Evaluation summary derivation seam.

Authority: docs/fee_confirmation_contract.md. The JSON fixture in
tests/contract_fixtures is the common acceptance oracle: the backend and the
frontend both independently derive the five summary fields and both must
reproduce these samples.

Scope rules (per review):
- Calculation results are compared numerically after normalization.
- Display fields use exact strings only where the contract specifies display
  format (hours one decimal, totals two decimals, manpower whole amount); the
  backend-side canonical derivation output is the display authority.
- The real confirmation path (service.confirm) must accept every golden
  summary through its saved-draft guard; that exercises the production
  recomputation instead of a private helper alone.
- This test never modifies business formulas. A mismatch is reported as a
  contract violation instead of being "fixed" here.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from backend.application.confirmed_fee_version_service import (
    ConfirmFeeVersionCommand,
    ConfirmedFeeVersionService,
    _summary_from_saved_pricing_snapshot,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedManualRow,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftContext,
    FeeEvaluationPricingDraftLoadResult,
    FeeEvaluationPricingDraftSnapshot,
)
from backend.domain.confirmed_fee import ConfirmedFeeSummary

_FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "contract_fixtures"
    / "fee_summary_acceptance_cases.json"
)
_CASES = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))["cases"]
_SUMMARY_FIELDS = (
    "testing_fee_total",
    "working_hours",
    "lab_manpower_cost",
    "external_cost",
    "grand_cost",
)


def _numeric(value: str) -> Decimal:
    normalized = str(value).strip().replace("$", "").replace(",", "")
    return Decimal(normalized or "0")


def _snapshot_from_case(case: dict) -> FeeEvaluationPricingDraftSnapshot:
    matrix_rows = tuple(
        FeeEvaluationEditedExportRow(
            source_line_id=f"line-{index}",
            confirmed_group_id=row.get("confirmed_group_id", f"cmg-{index}"),
            confirmed_row_id=f"row-{index}",
            step_token="1",
            step_index=0,
            spend_time=row["spend_time"],
            unit_price=row["unit_price"],
            unit_type="hour",
            units=row["units"],
            base_fee=row["base_fee"],
            discount=row["discount"],
            testing_fee=row["testing_fee"],
            notes="",
        )
        for index, row in enumerate(case["matrix_rows"], start=1)
    )
    manual_rows = tuple(
        FeeEvaluationEditedManualRow(
            row_kind=row["row_kind"],
            spend_time=row["spend_time"],
            unit_price=row["unit_price"],
            unit_type="hour",
            units=row["units"],
            base_fee=row["base_fee"],
            discount=row["discount"],
            testing_fee=row["testing_fee"],
            notes="",
            group_label=row.get("group_label", ""),
        )
        for row in case.get("manual_rows", [])
    )
    return FeeEvaluationPricingDraftSnapshot(
        draft_edit_id="fed-1",
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id="fee_rules_v2026_06_03",
        edited_values=FeeEvaluationEditedExportValues(
            rows=matrix_rows,
            summary=FeeEvaluationEditedExportSummary(
                condition_confirmation_spend_time=case["condition_confirmation_spend_time"],
                external_cost=case["external_cost"],
                external_cost_note="",
                lab_manpower_hourly_rate=case["lab_manpower_hourly_rate"],
            ),
            manual_rows=manual_rows,
        ),
        created_at="2026-06-09T09:00:00+00:00",
        updated_at="2026-06-09T09:10:00+00:00",
    )


def _golden_summary(case: dict) -> ConfirmedFeeSummary:
    expected = case["expected_summary"]
    return ConfirmedFeeSummary(
        testing_fee_total=expected["testing_fee_total"],
        working_hours=expected["working_hours"],
        lab_manpower_cost=expected["lab_manpower_cost"],
        external_cost=expected["external_cost"],
        grand_cost=expected["grand_cost"],
    )


class _PricingDraftLoader:
    def __init__(self, result: FeeEvaluationPricingDraftLoadResult) -> None:
        self.result = result

    def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
        return self.result


class _ConfirmedFeeStore:
    def __init__(self) -> None:
        self.versions: list = []

    def create(self, version):
        self.versions.append(version)
        return version

    def get_latest_by_project(self, project_id: str):
        matches = [item for item in self.versions if item.project_id == project_id]
        return matches[-1] if matches else None

    def list_by_project(self, project_id: str) -> tuple:
        return tuple(item for item in self.versions if item.project_id == project_id)


def _service(snapshot: FeeEvaluationPricingDraftSnapshot) -> ConfirmedFeeVersionService:
    return ConfirmedFeeVersionService(
        pricing_draft_loader=_PricingDraftLoader(
            FeeEvaluationPricingDraftLoadResult(
                status="current",
                current_context=FeeEvaluationPricingDraftContext(
                    project_id="P1",
                    confirmed_matrix_id="cmv-1",
                    confirmed_revision=1,
                    fee_rule_version_id="fee_rules_v2026_06_03",
                ),
                saved_snapshot=snapshot,
            )
        ),
        confirmed_fee_store=_ConfirmedFeeStore(),
        clock=lambda: "2026-06-10T09:00:00+00:00",
        id_factory=lambda: "cfv-id",
    )


@pytest.mark.parametrize("case", _CASES, ids=[case["id"] for case in _CASES])
def test_confirm_accepts_golden_summary_for_acceptance_sample(case: dict) -> None:
    """Real path: the saved-draft guard must accept the shared golden summary.

    The guard recomputes all five fields from the saved pricing snapshot and
    compares numerically, so a passing confirm proves backend derivation
    agrees with the acceptance sample within the contract's normalization
    and rounding rules.
    """
    snapshot = _snapshot_from_case(case)
    service = _service(snapshot)

    created = service.confirm(
        ConfirmFeeVersionCommand(
            project_id="P1",
            confirmed_by="Lab User",
            expected_pricing_draft_edit_id="fed-1",
            summary=_golden_summary(case),
        )
    )

    expected = case["expected_summary"]
    for field in _SUMMARY_FIELDS:
        assert _numeric(getattr(created.summary, field)) == _numeric(expected[field]), (
            f"{case['id']}: {field} mismatch between confirmed summary and sample"
        )


@pytest.mark.parametrize("case", _CASES, ids=[case["id"] for case in _CASES])
def test_canonical_summary_derivation_matches_sample_display_format(case: dict) -> None:
    """Display authority: canonical backend derivation strings match exactly.

    The contract fixes the display format (hours one decimal, totals two
    decimals, manpower whole amount, external cost canonicalized). Exact
    string equality is required here; numeric equivalence is covered by the
    confirmation-path test above.
    """
    derived = _summary_from_saved_pricing_snapshot(_snapshot_from_case(case))
    expected = case["expected_summary"]
    assert derived.testing_fee_total == expected["testing_fee_total"]
    assert derived.working_hours == expected["working_hours"]
    assert derived.lab_manpower_cost == expected["lab_manpower_cost"]
    assert derived.external_cost == expected["external_cost"]
    assert derived.grand_cost == expected["grand_cost"]
