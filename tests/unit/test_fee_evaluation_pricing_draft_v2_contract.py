from __future__ import annotations

from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    FeePricingDraftSourceContext,
    decode_pricing_draft_payload,
    encode_pricing_draft_v2,
    validation_token_for,
)


def test_v2_envelope_round_trips_generation_context_and_provenance() -> None:
    context = FeePricingDraftSourceContext(
        confirmed_matrix_id="matrix-1",
        confirmed_revision=2,
        fee_rule_version_id="rules-1",
        point_profile_status="confirmed",
        point_profile_revision_id="profile-revision-1",
        point_profile_revision_sequence=3,
        point_profile_fingerprint="profile-fingerprint",
        automatic_defaults_fingerprint="defaults-fingerprint",
    )

    payload_json = encode_pricing_draft_v2(
        generation=4,
        source_context=context,
        edited_values_payload={"rows": [], "summary": {}, "manual_rows": []},
        row_provenance={"row-1": ("unit_price", "notes")},
        summary_provenance=("external_cost",),
    )

    decoded = decode_pricing_draft_payload(payload_json)

    assert decoded.kind == "v2"
    assert decoded.generation == 4
    assert decoded.source_context == context
    assert decoded.row_provenance == {"row-1": ("notes", "unit_price")}
    assert decoded.summary_provenance == ("external_cost",)
    assert decoded.payload_fingerprint
    assert validation_token_for(
        draft_edit_id="draft-1",
        generation=decoded.generation,
        source_context_fingerprint=decoded.source_context_fingerprint,
        payload_fingerprint=decoded.payload_fingerprint,
    ) == validation_token_for(
        draft_edit_id="draft-1",
        generation=decoded.generation,
        source_context_fingerprint=decoded.source_context_fingerprint,
        payload_fingerprint=decoded.payload_fingerprint,
    )


def test_unversioned_payload_is_legacy_without_guessing_provenance() -> None:
    decoded = decode_pricing_draft_payload('{"rows": [], "summary": {}}')

    assert decoded.kind == "legacy"
    assert decoded.generation is None
    assert decoded.row_provenance == {}
    assert decoded.summary_provenance == ()
