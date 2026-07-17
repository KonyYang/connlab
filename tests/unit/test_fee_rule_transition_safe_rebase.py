from __future__ import annotations

from dataclasses import dataclass, replace

import pytest

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_serialization import edited_values_to_payload
from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    FeePricingDraftSourceContext,
    canonical_fingerprint,
    encode_pricing_draft_v2,
)
from backend.application.fee_rule_transition_safe_rebase import load_rebase_candidate


@dataclass(frozen=True)
class _Result:
    status: str
    current_context: object
    saved_snapshot: object | None


@dataclass(frozen=True)
class _Snapshot:
    generation: int
    source_context: FeePricingDraftSourceContext
    fee_rule_version_id: str
    payload_json: str
    edited_values: FeeEvaluationEditedExportValues


class _Provider:
    def __init__(self) -> None:
        self.rule_versions: list[str] = []

    def with_rule_library(self, library):
        self.rule_versions.append(library.version.version_id)
        return self


def _row(*, unit_price: str, units: str) -> FeeEvaluationEditedExportRow:
    return FeeEvaluationEditedExportRow(
        source_line_id="line-1",
        confirmed_group_id="group-1",
        confirmed_row_id="row-1",
        step_token="1",
        step_index=0,
        spend_time="1",
        unit_price=unit_price,
        unit_type="per reading",
        units=units,
        base_fee="0",
        discount="0%",
        testing_fee="10",
        notes="",
    )


def _values(*, unit_price: str = "10", units: str = "3") -> FeeEvaluationEditedExportValues:
    return FeeEvaluationEditedExportValues(
        rows=(_row(unit_price=unit_price, units=units),),
        summary=FeeEvaluationEditedExportSummary("0", "0", "", "200"),
    )


def _context(*, plan_fingerprint: str = "plan-1", defaults: str = "") -> FeePricingDraftSourceContext:
    return FeePricingDraftSourceContext(
        confirmed_matrix_id="matrix-1",
        confirmed_revision=2,
        fee_rule_version_id="fee_rules_v2026_07_16_r5",
        point_profile_status="confirmed",
        point_profile_revision_id="profile-1",
        point_profile_revision_sequence=1,
        point_profile_fingerprint="profile-fingerprint-1",
        automatic_defaults_fingerprint=defaults,
        measurement_plan_status="complete",
        measurement_plan_revision_id="plan-1",
        measurement_plan_revision_sequence=1,
        measurement_plan_fingerprint=plan_fingerprint,
    )


def _snapshot(values, context):
    payload = edited_values_to_payload(values)
    return _Snapshot(
        generation=1,
        source_context=context,
        fee_rule_version_id=context.fee_rule_version_id,
        payload_json=encode_pricing_draft_v2(
                generation=1,
                source_context=context,
                edited_values_payload=payload,
                row_provenance={"line-1": ("unit_price",)},
                summary_provenance=(),
            ),
        edited_values=values,
    )


def _current_context(**changes):
    values = {
        "confirmed_matrix_id": "matrix-1",
        "confirmed_revision": 2,
        "fee_rule_version_id": "fee_rules_v2026_07_17_r6",
        "point_profile_status": "confirmed",
        "point_profile_revision_id": "profile-1",
        "point_profile_revision_sequence": 1,
        "point_profile_fingerprint": "profile-fingerprint-1",
        "measurement_plan_status": "complete",
        "measurement_plan_revision_id": "plan-1",
        "measurement_plan_revision_sequence": 1,
        "measurement_plan_fingerprint": "plan-1",
    }
    values.update(changes)
    return type("Context", (), values)()


def test_changed_non_rule_lineage_is_blocked(monkeypatch) -> None:
    values = _values()
    source = _context(defaults=canonical_fingerprint(edited_values_to_payload(values)))
    snapshot = _snapshot(values, source)
    current = _current_context(measurement_plan_fingerprint="plan-2")

    result = load_rebase_candidate(
        snapshot=snapshot,
        context=current,
        project_id="P1",
        automatic_defaults_provider=_Provider(),
        current_source_context=current,
        result_type=_Result,
    )

    assert result.status == "blocked"
    assert result.saved_snapshot is None


@pytest.mark.parametrize("field", ["point_profile_fingerprint", "measurement_plan_revision_id"])
def test_missing_or_changed_lineage_is_blocked(field: str) -> None:
    values = _values()
    source = _context(defaults=canonical_fingerprint(edited_values_to_payload(values)))
    snapshot = _snapshot(values, source)
    current = _current_context(**{field: None})

    result = load_rebase_candidate(
        snapshot=snapshot,
        context=current,
        project_id="P1",
        automatic_defaults_provider=_Provider(),
        current_source_context=current,
        result_type=_Result,
    )

    assert result.status == "blocked"
    assert result.saved_snapshot is None


def test_prior_defaults_fingerprint_mismatch_is_blocked() -> None:
    values = _values()
    source = _context(defaults="wrong-prior-fingerprint")
    snapshot = _snapshot(values, source)
    current = _current_context()

    result = load_rebase_candidate(
        snapshot=snapshot,
        context=current,
        project_id="P1",
        automatic_defaults_provider=_Provider(),
        current_source_context=current,
        result_type=_Result,
    )

    assert result.status == "blocked"
    assert result.saved_snapshot is None


def test_prior_default_row_identity_mismatch_is_blocked(monkeypatch) -> None:
    values = _values()
    source = _context(defaults=canonical_fingerprint(edited_values_to_payload(values)))
    snapshot = _snapshot(values, source)
    different_identity = FeeEvaluationEditedExportValues(
        rows=(
            replace(_row(unit_price="10", units="3"), source_line_id="other"),
        ),
        summary=values.summary,
    )
    monkeypatch.setattr(
        "backend.application.fee_rule_transition_safe_rebase.current_automatic_values",
        lambda *args, **kwargs: different_identity,
    )

    result = load_rebase_candidate(
        snapshot=snapshot,
        context=_current_context(),
        project_id="P1",
        automatic_defaults_provider=_Provider(),
        current_source_context=_current_context(),
        result_type=_Result,
    )

    assert result.status == "blocked"
    assert result.saved_snapshot is None


def test_safe_rebase_retains_proven_manual_field(monkeypatch) -> None:
    prior = _values(unit_price="10", units="3")
    saved = _values(unit_price="999", units="3")
    current = _values(unit_price="20", units="9")
    source = _context(defaults=canonical_fingerprint(edited_values_to_payload(prior)))
    snapshot = _snapshot(saved, source)
    provider = _Provider()
    calls = iter((prior, current))
    monkeypatch.setattr(
        "backend.application.fee_rule_transition_safe_rebase.current_automatic_values",
        lambda *args, **kwargs: next(calls),
    )

    result = load_rebase_candidate(
        snapshot=snapshot,
        context=_current_context(),
        project_id="P1",
        automatic_defaults_provider=provider,
        current_source_context=_current_context(),
        result_type=_Result,
    )

    assert result.status == "rebase_required"
    assert result.saved_snapshot is not None
    assert result.saved_snapshot.edited_values.rows[0].unit_price == "999"
    assert result.saved_snapshot.edited_values.rows[0].units == "9"
    assert provider.rule_versions == ["fee_rules_v2026_07_16_r5"]
