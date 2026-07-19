from __future__ import annotations

import pytest

from backend.application.fee_evaluation_pricing_draft_prior_defaults_attestation import (
    FeePricingDraftAutomaticFieldSafety,
    FeePricingDraftAutomaticRowSafety,
    FeePricingDraftPriorDefaultsAttestationError,
    attestation_from_payload,
    attestation_to_payload,
    build_prior_defaults_attestation,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    FeePricingDraftSourceContext,
    decode_pricing_draft_payload,
    encode_pricing_draft_v2,
)


def test_v2_attestation_round_trips_all_canonical_bindings() -> None:
    context = _context()
    attestation = build_prior_defaults_attestation(
        generation=3,
        source_context=context,
        automatic_values_payload=_values_payload(),
        ordered_row_identities=(_row_identity(), _manual_identity()),
        row_safety=(_safe_row(),),
    )

    encoded = encode_pricing_draft_v2(
        generation=3,
        source_context=context,
        edited_values_payload=_values_payload(),
        row_provenance={"line-1:Step 1:0": ("unit_price",)},
        summary_provenance=(),
        automatic_defaults_attestation=attestation,
    )
    decoded = decode_pricing_draft_payload(encoded)

    assert decoded.automatic_defaults_attestation == attestation
    assert attestation.attested_generation == 3
    assert attestation.automatic_defaults_fingerprint == context.automatic_defaults_fingerprint
    assert attestation.ordered_row_identities == (_row_identity(), _manual_identity())
    assert attestation.row_safety == (_safe_row(),)


def test_attestation_rejects_duplicate_automatic_row_identity() -> None:
    context = _context()

    with pytest.raises(
        FeePricingDraftPriorDefaultsAttestationError,
        match="Duplicate automatic-default row identity",
    ):
        build_prior_defaults_attestation(
            generation=1,
            source_context=context,
            automatic_values_payload=_values_payload(),
            ordered_row_identities=(_row_identity(), _row_identity()),
            row_safety=(_safe_row(),),
        )


def test_attestation_rejects_oversized_canonical_payload() -> None:
    values = _values_payload()
    values["summary"] = {"external_cost_note": "x" * 1_048_576}

    with pytest.raises(FeePricingDraftPriorDefaultsAttestationError, match="too large"):
        build_prior_defaults_attestation(
            generation=1,
            source_context=_context(values),
            automatic_values_payload=values,
            ordered_row_identities=(_row_identity(),),
            row_safety=(_safe_row(),),
        )


def test_attestation_rejects_more_than_two_thousand_rows() -> None:
    values = _values_payload()
    values["rows"] = [values["rows"][0]] * 2_001  # type: ignore[index]

    with pytest.raises(FeePricingDraftPriorDefaultsAttestationError, match="row count"):
        build_prior_defaults_attestation(
            generation=1,
            source_context=_context(values),
            automatic_values_payload=values,
            ordered_row_identities=(_row_identity(),),
            row_safety=(_safe_row(),),
        )


def test_attestation_rejects_tampered_safety_fingerprint() -> None:
    context = _context()
    attestation = build_prior_defaults_attestation(
        generation=1,
        source_context=context,
        automatic_values_payload=_values_payload(),
        ordered_row_identities=(_row_identity(),),
        row_safety=(_safe_row(),),
    )
    payload = attestation_to_payload(attestation)
    payload["row_safety"][0]["diagnostic_code"] = "tampered"  # type: ignore[index]

    with pytest.raises(FeePricingDraftPriorDefaultsAttestationError, match="fingerprint"):
        attestation_from_payload(payload, generation=1, source_context=context)


def _context(values: dict[str, object] | None = None) -> FeePricingDraftSourceContext:
    from backend.application.fee_evaluation_pricing_draft_v2_contract import (
        canonical_fingerprint,
    )

    values = values or _values_payload()
    return FeePricingDraftSourceContext(
        confirmed_matrix_id="matrix-1",
        confirmed_revision=2,
        fee_rule_version_id="rules-1",
        point_profile_status="complete",
        point_profile_revision_id="profile-1",
        point_profile_revision_sequence=1,
        point_profile_fingerprint="profile-fp",
        automatic_defaults_fingerprint=canonical_fingerprint(values),
        measurement_plan_status="complete",
        measurement_plan_revision_id="plan-1",
        measurement_plan_revision_sequence=4,
        measurement_plan_fingerprint="plan-fp",
    )


def _values_payload() -> dict[str, object]:
    return {
        "rows": [
            {
                "source_line_id": "line-1:Step 1:0",
                "confirmed_group_id": "group-1",
                "confirmed_row_id": "row-1",
                "step_token": "Step 1",
                "step_index": 0,
                "spend_time": "0",
                "unit_price": "10",
                "unit_type": "reading",
                "units": "40",
                "base_fee": "0",
                "discount": "0%",
                "testing_fee": "400",
                "notes": "",
            }
        ],
        "summary": {
            "condition_confirmation_spend_time": "",
            "external_cost": "",
            "external_cost_note": "",
            "lab_manpower_hourly_rate": "",
        },
        "manual_rows": [],
        "inactive_rows": [],
    }


def _row_identity() -> tuple[str, str, str, str, int]:
    return ("line-1:Step 1:0", "group-1", "row-1", "Step 1", 0)


def _manual_identity() -> tuple[str, str, str, str]:
    return ("report_preparation", "", "", "")


def _safe_row() -> FeePricingDraftAutomaticRowSafety:
    return FeePricingDraftAutomaticRowSafety(
        identity=_row_identity(),
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
