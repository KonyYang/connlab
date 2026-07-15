"""Confirmed Fee V2 pricing lineage envelope helpers."""

from __future__ import annotations

import json
from typing import Mapping

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftSnapshot,
)
from backend.application.fee_evaluation_pricing_draft_serialization import (
    edited_values_to_payload,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import canonical_json

_KIND = "confirmed_fee_pricing_v2"


class ConfirmedFeePricingSnapshotError(ValueError):
    """Raised when a Confirmed Fee V2 pricing snapshot is malformed."""


def encode_confirmed_fee_pricing_snapshot(
    *,
    snapshot: FeeEvaluationPricingDraftSnapshot,
    edited_values: FeeEvaluationEditedExportValues,
) -> str:
    """Persist server-validated V2 lineage with the confirmable values."""
    lineage = _lineage_from_snapshot(snapshot)
    return canonical_json(
        {
            "schema_version": 2,
            "kind": _KIND,
            "lineage": lineage,
            "edited_values": edited_values_to_payload(edited_values),
        }
    )


def matches_current_v2_pricing_snapshot(
    payload_json: str,
    snapshot: FeeEvaluationPricingDraftSnapshot,
) -> bool:
    """Return whether one Confirmed Fee retains the exact current V2 lineage."""
    try:
        payload = _object_payload(payload_json)
        return payload.get("kind") == _KIND and payload.get("lineage") == _lineage_from_snapshot(snapshot)
    except ConfirmedFeePricingSnapshotError:
        return False


def edited_values_json_from_confirmed_fee_snapshot(payload_json: str) -> str:
    """Extract values for a downstream consumer after its currentness gate passes."""
    payload = _object_payload(payload_json)
    if payload.get("kind") != _KIND:
        return canonical_json(payload)
    values = payload.get("edited_values")
    if not isinstance(values, dict):
        raise ConfirmedFeePricingSnapshotError("Confirmed Fee V2 edited values are invalid.")
    return canonical_json(values)


def edited_values_payload_from_confirmed_fee_snapshot(
    payload_json: str,
) -> Mapping[str, object] | None:
    """Read values for display-only review metadata, including legacy snapshots."""
    try:
        payload = _object_payload(payload_json)
    except ConfirmedFeePricingSnapshotError:
        return None
    if payload.get("kind") != _KIND:
        return payload
    values = payload.get("edited_values")
    return values if isinstance(values, dict) else None


def _lineage_from_snapshot(snapshot: FeeEvaluationPricingDraftSnapshot) -> dict[str, object]:
    required = {
        "draft_edit_id": snapshot.draft_edit_id,
        "generation": snapshot.generation,
        "source_context_fingerprint": snapshot.source_context_fingerprint,
        "payload_fingerprint": snapshot.payload_fingerprint,
        "validation_token": snapshot.validation_token,
    }
    if (
        not isinstance(required["generation"], int)
        or required["generation"] < 1
        or any(not isinstance(value, str) or not value for key, value in required.items() if key != "generation")
    ):
        raise ConfirmedFeePricingSnapshotError("Confirmed Fee requires a complete V2 pricing lineage.")
    return required


def _object_payload(payload_json: str) -> dict[str, object]:
    try:
        payload = json.loads(payload_json)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ConfirmedFeePricingSnapshotError("Confirmed Fee pricing snapshot is invalid JSON.") from exc
    if not isinstance(payload, dict):
        raise ConfirmedFeePricingSnapshotError("Confirmed Fee pricing snapshot must be an object.")
    return payload
