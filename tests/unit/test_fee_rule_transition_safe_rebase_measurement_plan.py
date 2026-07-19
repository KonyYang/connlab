from __future__ import annotations

from dataclasses import replace

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    edited_row_identity,
)
from backend.application.fee_evaluation_pricing_draft_automatic_build import (
    FeePricingDraftAutomaticBuildResult,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftContext,
    FeeEvaluationPricingDraftLoadResult,
    FeeEvaluationPricingDraftSnapshot,
)
from backend.application.fee_evaluation_pricing_draft_prior_defaults_attestation import (
    FeePricingDraftAutomaticFieldSafety,
    FeePricingDraftAutomaticRowSafety,
    build_prior_defaults_attestation,
)
from backend.application.fee_evaluation_pricing_draft_serialization import (
    edited_values_to_payload,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    FeePricingDraftSourceContext,
    decode_pricing_draft_payload,
    encode_pricing_draft_v2,
)
from backend.application.fee_rule_transition_safe_rebase import load_rebase_candidate

_RULE_VERSION = "fee_rules_v2026_07_17_r6"


def test_attested_measurement_plan_change_rebases_without_second_provider_read() -> None:
    saved_context = _source_context(plan_id="plan-1", plan_fingerprint="plan-fp-1")
    current_context = _source_context(
        plan_id="plan-2",
        plan_fingerprint="plan-fp-2",
        automatic_defaults=_values(units="36", testing_fee="180"),
    )
    snapshot = _snapshot(saved_context, attested=True)
    current_build = _automatic_build(current_context, _values(units="36", testing_fee="180"))
    provider = _ForbiddenProvider()

    result = load_rebase_candidate(
        snapshot=snapshot,
        context=_pricing_context(),
        project_id="P1",
        automatic_defaults_provider=provider,
        current_source_context=current_context,
        current_automatic_build=current_build,
        result_type=FeeEvaluationPricingDraftLoadResult,
    )

    assert result.status == "rebase_required"
    assert result.saved_snapshot is not None
    row = result.saved_snapshot.edited_values.rows[0]
    assert row.units == "36"
    assert row.testing_fee == "180"
    assert row.unit_price == "12"
    assert provider.calls == 0


def test_unsafe_current_row_blocks_without_provider_read() -> None:
    saved_context = _source_context(plan_id="plan-1", plan_fingerprint="plan-fp-1")
    current_context = _source_context(plan_id="plan-2", plan_fingerprint="plan-fp-2")
    snapshot = _snapshot(saved_context, attested=True)
    unsafe = replace(_safe_row(), safe_for_rebase=False, diagnostic_code="cr_target_excluded")
    current_build = replace(_automatic_build(current_context, _values()), row_safety=(unsafe,))
    provider = _ForbiddenProvider()

    result = load_rebase_candidate(
        snapshot=snapshot,
        context=_pricing_context(),
        project_id="P1",
        automatic_defaults_provider=provider,
        current_source_context=current_context,
        current_automatic_build=current_build,
        result_type=FeeEvaluationPricingDraftLoadResult,
    )

    assert result.status == "blocked"
    assert provider.calls == 0


def test_unsafe_saved_row_blocks_without_provider_read() -> None:
    saved_context = _source_context(plan_id="plan-1", plan_fingerprint="plan-fp-1")
    current_context = _source_context(plan_id="plan-2", plan_fingerprint="plan-fp-2")
    unsafe = replace(_safe_row(), safe_for_rebase=False, diagnostic_code="cr_target_omitted")
    snapshot = _snapshot(saved_context, attested=True, saved_safety=unsafe)
    provider = _ForbiddenProvider()

    result = load_rebase_candidate(
        snapshot=snapshot,
        context=_pricing_context(),
        project_id="P1",
        automatic_defaults_provider=provider,
        current_source_context=current_context,
        current_automatic_build=_automatic_build(current_context, _values()),
        result_type=FeeEvaluationPricingDraftLoadResult,
    )

    assert result.status == "blocked"
    assert provider.calls == 0


def test_changed_row_identity_blocks_without_provider_read() -> None:
    saved_context = _source_context(plan_id="plan-1", plan_fingerprint="plan-fp-1")
    current_context = _source_context(plan_id="plan-2", plan_fingerprint="plan-fp-2")
    current_values = replace(
        _values(),
        rows=(replace(_values().rows[0], source_line_id="matrix-1:changed:row"),),
    )
    provider = _ForbiddenProvider()

    result = load_rebase_candidate(
        snapshot=_snapshot(saved_context, attested=True),
        context=_pricing_context(),
        project_id="P1",
        automatic_defaults_provider=provider,
        current_source_context=current_context,
        current_automatic_build=_automatic_build(current_context, current_values),
        result_type=FeeEvaluationPricingDraftLoadResult,
    )

    assert result.status == "blocked"
    assert provider.calls == 0


def test_non_measurement_plan_lineage_change_remains_blocked() -> None:
    saved_context = _source_context(plan_id="plan-1", plan_fingerprint="plan-fp-1")
    current_context = replace(
        _source_context(plan_id="plan-2", plan_fingerprint="plan-fp-2"),
        point_profile_fingerprint="changed-profile",
    )
    provider = _ForbiddenProvider()

    result = load_rebase_candidate(
        snapshot=_snapshot(saved_context, attested=True),
        context=_pricing_context(),
        project_id="P1",
        automatic_defaults_provider=provider,
        current_source_context=current_context,
        current_automatic_build=_automatic_build(current_context, _values()),
        result_type=FeeEvaluationPricingDraftLoadResult,
    )

    assert result.status == "blocked"
    assert provider.calls == 0


def test_malformed_attestation_envelope_remains_blocked() -> None:
    saved_context = _source_context(plan_id="plan-1", plan_fingerprint="plan-fp-1")
    current_context = _source_context(plan_id="plan-2", plan_fingerprint="plan-fp-2")
    snapshot = _snapshot(saved_context, attested=True)
    provider = _ForbiddenProvider()

    result = load_rebase_candidate(
        snapshot=replace(
            snapshot,
            payload_json=(snapshot.payload_json or "").replace(
                '"safe_for_rebase":true', '"safe_for_rebase":false', 1
            ),
        ),
        context=_pricing_context(),
        project_id="P1",
        automatic_defaults_provider=provider,
        current_source_context=current_context,
        current_automatic_build=_automatic_build(current_context, _values()),
        result_type=FeeEvaluationPricingDraftLoadResult,
    )

    assert result.status == "blocked"
    assert provider.calls == 0


def test_unattested_measurement_plan_change_remains_blocked() -> None:
    saved_context = _source_context(plan_id="plan-1", plan_fingerprint="plan-fp-1")
    current_context = _source_context(plan_id="plan-2", plan_fingerprint="plan-fp-2")
    provider = _ForbiddenProvider()

    result = load_rebase_candidate(
        snapshot=_snapshot(saved_context, attested=False),
        context=_pricing_context(),
        project_id="P1",
        automatic_defaults_provider=provider,
        current_source_context=current_context,
        current_automatic_build=_automatic_build(current_context, _values()),
        result_type=FeeEvaluationPricingDraftLoadResult,
    )

    assert result.status == "blocked"
    assert provider.calls == 0


class _ForbiddenProvider:
    def __init__(self) -> None:
        self.calls = 0

    def build_draft(self, command):
        self.calls += 1
        raise AssertionError("current defaults provider must not be called again")


def _snapshot(
    context: FeePricingDraftSourceContext,
    *,
    attested: bool,
    saved_safety: FeePricingDraftAutomaticRowSafety | None = None,
) -> FeeEvaluationPricingDraftSnapshot:
    defaults = _values(unit_price="10")
    attestation = (
        build_prior_defaults_attestation(
            generation=1,
            source_context=context,
            automatic_values_payload=edited_values_to_payload(defaults),
            ordered_row_identities=(edited_row_identity(defaults.rows[0]),),
            row_safety=(saved_safety or _safe_row(),),
        )
        if attested
        else None
    )
    saved = _values(unit_price="12")
    payload = encode_pricing_draft_v2(
        generation=1,
        source_context=context,
        edited_values_payload=edited_values_to_payload(saved),
        row_provenance={saved.rows[0].source_line_id: ("unit_price",)},
        summary_provenance=(),
        automatic_defaults_attestation=attestation,
    )
    decoded = decode_pricing_draft_payload(payload)
    return FeeEvaluationPricingDraftSnapshot(
        draft_edit_id="draft-1",
        project_id="P1",
        confirmed_matrix_id="matrix-1",
        confirmed_revision=1,
        fee_rule_version_id=_RULE_VERSION,
        edited_values=saved,
        created_at="2026-07-19T00:00:00+00:00",
        updated_at="2026-07-19T00:00:00+00:00",
        generation=1,
        payload_json=payload,
        payload_fingerprint=decoded.payload_fingerprint,
        source_context_fingerprint=decoded.source_context_fingerprint,
        source_context=context,
    )


def _automatic_build(
    context: FeePricingDraftSourceContext,
    values: FeeEvaluationEditedExportValues,
) -> FeePricingDraftAutomaticBuildResult:
    return FeePricingDraftAutomaticBuildResult(
        fee_draft=None,  # type: ignore[arg-type]
        confirmed_matrix=None,  # type: ignore[arg-type]
        automatic_values=values,
        ordered_row_identities=(edited_row_identity(values.rows[0]),),
        row_safety=(_safe_row(),),
        source_context=context,
    )


def _source_context(
    *,
    plan_id: str,
    plan_fingerprint: str,
    automatic_defaults: FeeEvaluationEditedExportValues | None = None,
) -> FeePricingDraftSourceContext:
    from backend.application.fee_evaluation_pricing_draft_v2_contract import (
        canonical_fingerprint,
    )

    return FeePricingDraftSourceContext(
        confirmed_matrix_id="matrix-1",
        confirmed_revision=1,
        fee_rule_version_id=_RULE_VERSION,
        point_profile_status="complete",
        point_profile_revision_id="profile-1",
        point_profile_revision_sequence=1,
        point_profile_fingerprint="profile-fp",
        automatic_defaults_fingerprint=canonical_fingerprint(
            edited_values_to_payload(automatic_defaults or _values(unit_price="10"))
        ),
        measurement_plan_status="complete",
        measurement_plan_revision_id=plan_id,
        measurement_plan_revision_sequence=1 if plan_id == "plan-1" else 2,
        measurement_plan_fingerprint=plan_fingerprint,
    )


def _pricing_context() -> FeeEvaluationPricingDraftContext:
    return FeeEvaluationPricingDraftContext(
        project_id="P1",
        confirmed_matrix_id="matrix-1",
        confirmed_revision=1,
        fee_rule_version_id=_RULE_VERSION,
    )


def _values(
    *,
    unit_price: str = "10",
    units: str = "40",
    testing_fee: str = "400",
) -> FeeEvaluationEditedExportValues:
    return FeeEvaluationEditedExportValues(
        rows=(
            FeeEvaluationEditedExportRow(
                source_line_id="matrix-1:group-1:row-1:1:0",
                confirmed_group_id="group-1",
                confirmed_row_id="row-1",
                step_token="1",
                step_index=0,
                spend_time="0",
                unit_price=unit_price,
                unit_type="reading",
                units=units,
                base_fee="0",
                discount="5%",
                testing_fee=testing_fee,
                notes="manual note",
            ),
        ),
        summary=FeeEvaluationEditedExportSummary("", "", "", ""),
    )


def _safe_row() -> FeePricingDraftAutomaticRowSafety:
    return FeePricingDraftAutomaticRowSafety(
        identity=edited_row_identity(_values().rows[0]),
        row_kind="matrix",
        matched_rule_id="fee_rule_contact_resistance_specified_current",
        automatic_fields=(
            FeePricingDraftAutomaticFieldSafety(
                field="units",
                state="auto_filled",
                source="Confirmed CR Measurement Plan",
                required_for_rebase=True,
            ),
        ),
        safe_for_rebase=True,
        diagnostic_code="safe",
        diagnostic_text=None,
    )
