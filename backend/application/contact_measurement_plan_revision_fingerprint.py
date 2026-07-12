"""Deterministic optimistic-concurrency fingerprints for editable plan revisions."""

from __future__ import annotations

import json
from hashlib import sha256

from backend.infrastructure.storage.repositories.contact_measurement_plan_authority import (
    ContactMeasurementPlanAuthorityRepository,
)


def editable_revision_fingerprint(
    repository: ContactMeasurementPlanAuthorityRepository,
    revision_id: str,
) -> str:
    """Hash target and family data without including mutable database identifiers."""
    payload = []
    for target in repository.targets(revision_id):
        payload.append(
            {
                "stable_target_key": target.stable_target_key,
                "included": target.included,
                "coverage_state": target.coverage_state,
                "exclusion_reason": target.exclusion_reason,
                "is_override": target.is_override,
                "readings_per_sample": target.readings_per_sample,
                "families": [
                    {
                        "family_id": family.family_id,
                        "ordinal": family.family_ordinal,
                        "label": family.label,
                        "count": family.count_per_sample,
                        "record_label": family.record_label,
                        "record_prefix": family.record_prefix,
                        "included": family.included,
                        "is_custom": family.is_custom,
                    }
                    for family in repository.families(
                        target.measurement_plan_target_snapshot_id
                    )
                ],
            }
        )
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()
