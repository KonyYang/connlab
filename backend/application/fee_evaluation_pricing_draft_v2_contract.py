"""Pure V2 pricing-draft envelope, fingerprint, and token helpers."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Literal, Mapping


class FeePricingDraftEnvelopeError(ValueError):
    """Raised when a persisted V2 pricing-draft envelope is malformed."""


@dataclass(frozen=True, slots=True)
class FeePricingDraftSourceContext:
    """Machine-readable authority facts that seed automatic Fee defaults."""

    confirmed_matrix_id: str
    confirmed_revision: int
    fee_rule_version_id: str
    point_profile_status: str
    point_profile_revision_id: str | None
    point_profile_revision_sequence: int | None
    point_profile_fingerprint: str | None
    automatic_defaults_fingerprint: str
    measurement_plan_status: str = "not_started"
    measurement_plan_revision_id: str | None = None
    measurement_plan_revision_sequence: int | None = None
    measurement_plan_fingerprint: str | None = None


@dataclass(frozen=True, slots=True)
class DecodedFeePricingDraftPayload:
    """Decoded legacy or V2 payload without making persistence decisions."""

    kind: Literal["legacy", "v2"]
    edited_values_payload: Mapping[str, object]
    generation: int | None = None
    source_context: FeePricingDraftSourceContext | None = None
    row_provenance: Mapping[str, tuple[str, ...]] = None  # type: ignore[assignment]
    summary_provenance: tuple[str, ...] = ()
    payload_fingerprint: str | None = None
    source_context_fingerprint: str | None = None

    def __post_init__(self) -> None:
        if self.row_provenance is None:
            object.__setattr__(self, "row_provenance", {})


def encode_pricing_draft_v2(
    *,
    generation: int,
    source_context: FeePricingDraftSourceContext,
    edited_values_payload: Mapping[str, object],
    row_provenance: Mapping[str, tuple[str, ...]],
    summary_provenance: tuple[str, ...],
) -> str:
    """Return canonical JSON for a V2 pricing draft."""
    if generation < 1:
        raise FeePricingDraftEnvelopeError("Pricing draft generation must be positive.")
    payload = {
        "schema_version": 2,
        "generation": generation,
        "source_context": _source_context_payload(source_context),
        "edited_values": dict(edited_values_payload),
        "operator_provenance": {
            "rows": {
                key: sorted({str(field) for field in fields})
                for key, fields in sorted(row_provenance.items())
            },
            "summary": sorted({str(field) for field in summary_provenance}),
        },
    }
    payload["canonical_payload_fingerprint"] = canonical_fingerprint(payload)
    return canonical_json(payload)


def decode_pricing_draft_payload(payload_json: str) -> DecodedFeePricingDraftPayload:
    """Decode V2 strictly, or classify an older values-only document as legacy."""
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        raise FeePricingDraftEnvelopeError("Pricing draft payload is invalid JSON.") from exc
    if not isinstance(payload, dict):
        raise FeePricingDraftEnvelopeError("Pricing draft payload must be an object.")
    if payload.get("schema_version") != 2:
        return DecodedFeePricingDraftPayload(
            kind="legacy",
            edited_values_payload=payload,
        )
    return _decode_v2(payload)


def canonical_fingerprint(value: Mapping[str, object]) -> str:
    """Hash canonical UTF-8 JSON without display-only formatting variation."""
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def validation_token_for(
    *,
    draft_edit_id: str,
    generation: int,
    source_context_fingerprint: str,
    payload_fingerprint: str,
) -> str:
    """Return a currentness attestation, not a consumed-token credential."""
    return canonical_fingerprint(
        {
            "draft_edit_id": draft_edit_id,
            "generation": generation,
            "source_context_fingerprint": source_context_fingerprint,
            "payload_fingerprint": payload_fingerprint,
        }
    )


def canonical_json(value: Mapping[str, object]) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _decode_v2(payload: Mapping[str, object]) -> DecodedFeePricingDraftPayload:
    generation = payload.get("generation")
    context_payload = payload.get("source_context")
    values = payload.get("edited_values")
    provenance = payload.get("operator_provenance")
    expected_fingerprint = payload.get("canonical_payload_fingerprint")
    if not isinstance(generation, int) or generation < 1:
        raise FeePricingDraftEnvelopeError("Pricing draft V2 generation is invalid.")
    if not isinstance(context_payload, dict) or not isinstance(values, dict):
        raise FeePricingDraftEnvelopeError("Pricing draft V2 context or values are invalid.")
    if not isinstance(provenance, dict) or not isinstance(expected_fingerprint, str):
        raise FeePricingDraftEnvelopeError("Pricing draft V2 provenance is invalid.")
    payload_without_fingerprint = dict(payload)
    payload_without_fingerprint.pop("canonical_payload_fingerprint", None)
    if canonical_fingerprint(payload_without_fingerprint) != expected_fingerprint:
        raise FeePricingDraftEnvelopeError("Pricing draft V2 fingerprint is invalid.")
    context = _source_context_from_payload(context_payload)
    rows = provenance.get("rows", {})
    summary = provenance.get("summary", [])
    if not isinstance(rows, dict) or not isinstance(summary, list):
        raise FeePricingDraftEnvelopeError("Pricing draft V2 provenance is invalid.")
    normalized_rows = {
        str(key): tuple(sorted({str(field) for field in fields}))
        for key, fields in rows.items()
        if isinstance(fields, list)
    }
    if len(normalized_rows) != len(rows):
        raise FeePricingDraftEnvelopeError("Pricing draft V2 row provenance is invalid.")
    source_context_fingerprint = canonical_fingerprint(_source_context_payload(context))
    return DecodedFeePricingDraftPayload(
        kind="v2",
        edited_values_payload=values,
        generation=generation,
        source_context=context,
        row_provenance=normalized_rows,
        summary_provenance=tuple(sorted({str(field) for field in summary})),
        payload_fingerprint=expected_fingerprint,
        source_context_fingerprint=source_context_fingerprint,
    )


def _source_context_payload(context: FeePricingDraftSourceContext) -> dict[str, object]:
    return {
        "confirmed_matrix_id": context.confirmed_matrix_id,
        "confirmed_revision": context.confirmed_revision,
        "fee_rule_version_id": context.fee_rule_version_id,
        "point_profile_status": context.point_profile_status,
        "point_profile_revision_id": context.point_profile_revision_id,
        "point_profile_revision_sequence": context.point_profile_revision_sequence,
        "point_profile_fingerprint": context.point_profile_fingerprint,
        "automatic_defaults_fingerprint": context.automatic_defaults_fingerprint,
        "measurement_plan_status": context.measurement_plan_status,
        "measurement_plan_revision_id": context.measurement_plan_revision_id,
        "measurement_plan_revision_sequence": context.measurement_plan_revision_sequence,
        "measurement_plan_fingerprint": context.measurement_plan_fingerprint,
    }


def _source_context_from_payload(payload: Mapping[str, object]) -> FeePricingDraftSourceContext:
    try:
        return FeePricingDraftSourceContext(
            confirmed_matrix_id=str(payload["confirmed_matrix_id"]),
            confirmed_revision=int(payload["confirmed_revision"]),
            fee_rule_version_id=str(payload["fee_rule_version_id"]),
            point_profile_status=str(payload["point_profile_status"]),
            point_profile_revision_id=_optional_text(payload.get("point_profile_revision_id")),
            point_profile_revision_sequence=_optional_int(
                payload.get("point_profile_revision_sequence")
            ),
            point_profile_fingerprint=_optional_text(payload.get("point_profile_fingerprint")),
            automatic_defaults_fingerprint=str(payload["automatic_defaults_fingerprint"]),
            measurement_plan_status=str(payload.get("measurement_plan_status", "not_started")),
            measurement_plan_revision_id=_optional_text(payload.get("measurement_plan_revision_id")),
            measurement_plan_revision_sequence=_optional_int(
                payload.get("measurement_plan_revision_sequence")
            ),
            measurement_plan_fingerprint=_optional_text(payload.get("measurement_plan_fingerprint")),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise FeePricingDraftEnvelopeError("Pricing draft V2 source context is invalid.") from exc


def _optional_text(value: object) -> str | None:
    return str(value) if value is not None else None


def _optional_int(value: object) -> int | None:
    return int(value) if value is not None else None
