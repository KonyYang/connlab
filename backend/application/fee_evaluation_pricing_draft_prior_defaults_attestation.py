"""Canonical server-owned prior automatic-default attestation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Literal, Mapping

from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    FeePricingDraftSourceContext,
    canonical_fingerprint,
)

_ATTESTATION_KIND = "fee-automatic-defaults:v1"
_MAX_AUTOMATIC_ROWS = 2_000
_MAX_CANONICAL_BYTES = 1_048_576
_FIELD_STATES = {"auto_filled", "suggested_review", "manual_required", "not_available"}


class FeePricingDraftPriorDefaultsAttestationError(ValueError):
    """Raised when prior automatic-default evidence is malformed."""


@dataclass(frozen=True, slots=True)
class FeePricingDraftAutomaticFieldSafety:
    """One pre-flattening automatic Fee field state."""

    field: str
    state: str
    source: str | None
    required_for_rebase: bool


@dataclass(frozen=True, slots=True)
class FeePricingDraftAutomaticRowSafety:
    """Canonical safety evidence for one automatic Matrix Fee row."""

    identity: tuple[str, str, str, str, int]
    row_kind: Literal["matrix"]
    matched_rule_id: str | None
    automatic_fields: tuple[FeePricingDraftAutomaticFieldSafety, ...]
    safe_for_rebase: bool
    diagnostic_code: str
    diagnostic_text: str | None


@dataclass(frozen=True, slots=True)
class FeePricingDraftPriorDefaultsAttestation:
    """Evidence binding saved automatic defaults to their authority build."""

    kind: Literal["fee-automatic-defaults:v1"]
    attested_generation: int
    source_context_fingerprint: str
    automatic_values_payload: Mapping[str, object]
    automatic_defaults_fingerprint: str
    ordered_row_identities: tuple[tuple[object, ...], ...]
    ordered_row_identity_fingerprint: str
    row_safety: tuple[FeePricingDraftAutomaticRowSafety, ...]
    row_safety_fingerprint: str


def build_prior_defaults_attestation(
    *,
    generation: int,
    source_context: FeePricingDraftSourceContext,
    automatic_values_payload: Mapping[str, object],
    ordered_row_identities: tuple[tuple[object, ...], ...],
    row_safety: tuple[FeePricingDraftAutomaticRowSafety, ...],
) -> FeePricingDraftPriorDefaultsAttestation:
    """Build and validate one canonical server-owned attestation."""
    if generation < 1:
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Prior automatic-default generation must be positive."
        )
    identities = tuple(_normalize_identity(value) for value in ordered_row_identities)
    if len(set(identities)) != len(identities):
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Duplicate automatic-default row identity."
        )
    automatic_rows = automatic_values_payload.get("rows")
    if not isinstance(automatic_rows, list) or len(automatic_rows) > _MAX_AUTOMATIC_ROWS:
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Prior automatic-default row count is invalid."
        )
    if len(row_safety) != len(automatic_rows):
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Prior automatic-default row safety count is invalid."
        )
    for index, safety in enumerate(row_safety):
        _validate_row_safety(safety)
        if index >= len(identities) or safety.identity != identities[index]:
            raise FeePricingDraftPriorDefaultsAttestationError(
                "Prior automatic-default row safety order is invalid."
            )
    defaults_fingerprint = canonical_fingerprint(automatic_values_payload)
    if defaults_fingerprint != source_context.automatic_defaults_fingerprint:
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Prior automatic-default fingerprint does not match source context."
        )
    attestation = FeePricingDraftPriorDefaultsAttestation(
        kind=_ATTESTATION_KIND,
        attested_generation=generation,
        source_context_fingerprint=canonical_fingerprint(asdict(source_context)),
        automatic_values_payload=dict(automatic_values_payload),
        automatic_defaults_fingerprint=defaults_fingerprint,
        ordered_row_identities=identities,
        ordered_row_identity_fingerprint=canonical_fingerprint(
            {"ordered_row_identities": [list(value) for value in identities]}
        ),
        row_safety=row_safety,
        row_safety_fingerprint=canonical_fingerprint(
            {"row_safety": [_row_safety_payload(value) for value in row_safety]}
        ),
    )
    if len(_canonical_json(attestation_to_payload(attestation)).encode("utf-8")) > _MAX_CANONICAL_BYTES:
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Prior automatic-default attestation is too large."
        )
    return attestation


def attestation_to_payload(
    attestation: FeePricingDraftPriorDefaultsAttestation,
) -> dict[str, object]:
    """Return the canonical JSON-compatible attestation mapping."""
    return {
        "kind": attestation.kind,
        "attested_generation": attestation.attested_generation,
        "source_context_fingerprint": attestation.source_context_fingerprint,
        "automatic_values_payload": dict(attestation.automatic_values_payload),
        "automatic_defaults_fingerprint": attestation.automatic_defaults_fingerprint,
        "ordered_row_identities": [list(value) for value in attestation.ordered_row_identities],
        "ordered_row_identity_fingerprint": attestation.ordered_row_identity_fingerprint,
        "row_safety": [_row_safety_payload(value) for value in attestation.row_safety],
        "row_safety_fingerprint": attestation.row_safety_fingerprint,
    }


def attestation_from_payload(
    payload: object,
    *,
    generation: int,
    source_context: FeePricingDraftSourceContext,
) -> FeePricingDraftPriorDefaultsAttestation:
    """Decode and fully read-verify one persisted attestation mapping."""
    if not isinstance(payload, dict) or payload.get("kind") != _ATTESTATION_KIND:
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Prior automatic-default attestation kind is invalid."
        )
    try:
        automatic_values = payload["automatic_values_payload"]
        identity_payload = payload["ordered_row_identities"]
        safety_payload = payload["row_safety"]
        if not isinstance(automatic_values, dict):
            raise TypeError
        if not isinstance(identity_payload, list) or not isinstance(safety_payload, list):
            raise TypeError
        row_safety = tuple(_row_safety_from_payload(value) for value in safety_payload)
        rebuilt = build_prior_defaults_attestation(
            generation=generation,
            source_context=source_context,
            automatic_values_payload=automatic_values,
            ordered_row_identities=tuple(tuple(value) for value in identity_payload),
            row_safety=row_safety,
        )
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, FeePricingDraftPriorDefaultsAttestationError):
            raise
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Prior automatic-default attestation is invalid."
        ) from exc
    if attestation_to_payload(rebuilt) != payload:
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Prior automatic-default attestation fingerprint is invalid."
        )
    return rebuilt


def _normalize_identity(value: tuple[object, ...]) -> tuple[object, ...]:
    if len(value) not in {4, 5} or not all(isinstance(item, str) for item in value[:4]):
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Prior automatic-default row identity is invalid."
        )
    if len(value) == 5 and not isinstance(value[4], int):
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Prior automatic-default row identity is invalid."
        )
    return tuple(value)


def _validate_row_safety(safety: FeePricingDraftAutomaticRowSafety) -> None:
    _normalize_identity(safety.identity)
    if safety.row_kind != "matrix" or not safety.diagnostic_code:
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Prior automatic-default row safety is invalid."
        )
    fields = [item.field for item in safety.automatic_fields]
    if len(fields) != len(set(fields)) or any(item.state not in _FIELD_STATES for item in safety.automatic_fields):
        raise FeePricingDraftPriorDefaultsAttestationError(
            "Prior automatic-default field safety is invalid."
        )


def _row_safety_payload(safety: FeePricingDraftAutomaticRowSafety) -> dict[str, object]:
    return {
        "identity": list(safety.identity),
        "row_kind": safety.row_kind,
        "matched_rule_id": safety.matched_rule_id,
        "automatic_fields": [asdict(value) for value in safety.automatic_fields],
        "safe_for_rebase": safety.safe_for_rebase,
        "diagnostic_code": safety.diagnostic_code,
        "diagnostic_text": safety.diagnostic_text,
    }


def _row_safety_from_payload(payload: object) -> FeePricingDraftAutomaticRowSafety:
    if not isinstance(payload, dict):
        raise TypeError
    fields = payload.get("automatic_fields")
    identity = payload.get("identity")
    if not isinstance(fields, list) or not isinstance(identity, list):
        raise TypeError
    return FeePricingDraftAutomaticRowSafety(
        identity=tuple(identity),  # type: ignore[arg-type]
        row_kind=str(payload["row_kind"]),  # type: ignore[arg-type]
        matched_rule_id=(
            str(payload["matched_rule_id"])
            if payload.get("matched_rule_id") is not None
            else None
        ),
        automatic_fields=tuple(
            FeePricingDraftAutomaticFieldSafety(
                field=str(value["field"]),
                state=str(value["state"]),
                source=str(value["source"]) if value.get("source") is not None else None,
                required_for_rebase=bool(value["required_for_rebase"]),
            )
            for value in fields
            if isinstance(value, dict)
        ),
        safe_for_rebase=bool(payload["safe_for_rebase"]),
        diagnostic_code=str(payload["diagnostic_code"]),
        diagnostic_text=(
            str(payload["diagnostic_text"])
            if payload.get("diagnostic_text") is not None
            else None
        ),
    )


def _canonical_json(value: Mapping[str, object]) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
