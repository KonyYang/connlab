"""Pure helpers for safe fee-rule-version pricing-draft transitions."""

from __future__ import annotations

from dataclasses import replace
from copy import copy
from typing import Any

from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    decode_pricing_draft_payload,
    canonical_fingerprint,
)
from backend.application.fee_evaluation_pricing_draft_v2_rebase import (
    rebase_reviewed_values,
)
from backend.application.fee_evaluation_pricing_draft_v2_authority_context import (
    current_automatic_values,
)
from backend.application.fee_evaluation_edited_export_values import (
    edited_row_identity,
    manual_row_identity,
)
from backend.application.fee_evaluation_pricing_draft_serialization import (
    edited_values_from_payload,
)


class FeeRuleRebaseAttestationError(ValueError):
    """Raised when a saved V2 draft cannot be safely attributed."""


def rebase_snapshot_values(
    *,
    snapshot: Any,
    project_id: str,
    automatic_defaults_provider: object | None,
):
    """Rebuild current defaults and preserve only proven operator-owned fields."""
    provenance = None
    if snapshot.payload_json:
        decoded = decode_pricing_draft_payload(snapshot.payload_json)
        provenance = decoded.row_provenance
    return rebase_reviewed_values(
        saved=snapshot.edited_values,
        current_defaults=current_automatic_values(
            project_id,
            automatic_defaults_provider,
            snapshot.edited_values,
        ),
        row_provenance=provenance,
    )


def load_rebase_candidate(
    *,
    snapshot: Any,
    context: Any,
    project_id: str,
    automatic_defaults_provider: object | None,
    current_source_context: Any | None = None,
    current_automatic_build: Any | None = None,
    result_type: type,
):
    """Build a typed read-only load result for an eligible old V2 draft."""
    source = snapshot.source_context
    if snapshot.generation is None or source is None:
        return result_type(
            status="legacy_unclassified",
            current_context=context,
            saved_snapshot=snapshot,
        )
    if (
        source.confirmed_matrix_id != context.confirmed_matrix_id
        or source.confirmed_revision != context.confirmed_revision
        or snapshot.fee_rule_version_id != source.fee_rule_version_id
        or _bundled_version_missing(snapshot.fee_rule_version_id)
        or _bundled_version_missing(source.fee_rule_version_id)
    ):
        return _blocked(result_type, context)
    try:
        decoded = decode_pricing_draft_payload(snapshot.payload_json or "")
        if decoded.kind != "v2" or decoded.source_context is None:
            raise FeeRuleRebaseAttestationError("Saved pricing draft V2 attestation is missing.")
        if _is_attested_measurement_plan_transition(
            source, current_source_context, current_automatic_build
        ):
            rebased = _rebase_attested_measurement_plan(
                snapshot=snapshot,
                decoded=decoded,
                current_automatic_build=current_automatic_build,
            )
        else:
            if current_source_context is not None and not _same_non_rule_lineage(
                source, current_source_context
            ):
                raise FeeRuleRebaseAttestationError("Non-rule authority lineage changed.")
            prior_defaults = _rebuild_prior_defaults(
                snapshot=snapshot,
                project_id=project_id,
                automatic_defaults_provider=automatic_defaults_provider,
            )
            expected_defaults_fingerprint = source.automatic_defaults_fingerprint
            actual_defaults_fingerprint = canonical_fingerprint(
                _values_payload(prior_defaults)
            )
            if actual_defaults_fingerprint != expected_defaults_fingerprint:
                raise FeeRuleRebaseAttestationError("Prior automatic defaults fingerprint changed.")
            if _row_identities(prior_defaults) != _row_identities(snapshot.edited_values):
                raise FeeRuleRebaseAttestationError("Prior automatic default row identity changed.")
            current_defaults = (
                current_automatic_build.automatic_values
                if current_automatic_build is not None
                else current_automatic_values(
                    project_id,
                    automatic_defaults_provider,
                    snapshot.edited_values,
                )
            )
            rebased = rebase_reviewed_values(
                saved=snapshot.edited_values,
                current_defaults=current_defaults,
                row_provenance=decoded.row_provenance,
            )
    except (
        FeeRuleRebaseAttestationError,
        ValueError,
        TypeError,
        KeyError,
        LookupError,
        AttributeError,
    ):
        return _blocked(result_type, context)
    return result_type(
        status="rebase_required", current_context=context, saved_snapshot=replace(snapshot, edited_values=rebased)
    )


def _blocked(result_type: type, context: Any):
    return result_type(status="blocked", current_context=context, saved_snapshot=None)


def _same_non_rule_lineage(saved: Any, current: Any) -> bool:
    fields = (
        "confirmed_matrix_id", "confirmed_revision",
        "point_profile_status", "point_profile_revision_id",
        "point_profile_revision_sequence", "point_profile_fingerprint",
        "measurement_plan_status", "measurement_plan_revision_id",
        "measurement_plan_revision_sequence", "measurement_plan_fingerprint",
    )
    return all(getattr(saved, field, None) == getattr(current, field, None) for field in fields)


def _is_attested_measurement_plan_transition(
    saved: Any,
    current: Any | None,
    current_build: Any | None,
) -> bool:
    if current is None or current_build is None:
        return False
    stable_fields = (
        "confirmed_matrix_id",
        "confirmed_revision",
        "fee_rule_version_id",
        "point_profile_status",
        "point_profile_revision_id",
        "point_profile_revision_sequence",
        "point_profile_fingerprint",
    )
    if any(getattr(saved, field, None) != getattr(current, field, None) for field in stable_fields):
        return False
    measurement_fields = (
        "measurement_plan_status",
        "measurement_plan_revision_id",
        "measurement_plan_revision_sequence",
        "measurement_plan_fingerprint",
    )
    return any(
        getattr(saved, field, None) != getattr(current, field, None)
        for field in measurement_fields
    )


def _rebase_attested_measurement_plan(
    *,
    snapshot: Any,
    decoded: Any,
    current_automatic_build: Any,
):
    attestation = decoded.automatic_defaults_attestation
    if attestation is None or snapshot.generation != attestation.attested_generation:
        raise FeeRuleRebaseAttestationError("Prior automatic defaults attestation is missing.")
    if attestation.source_context_fingerprint != decoded.source_context_fingerprint:
        raise FeeRuleRebaseAttestationError("Prior automatic source context changed.")
    saved_identities = _flat_row_identities(snapshot.edited_values)
    if attestation.ordered_row_identities != saved_identities:
        raise FeeRuleRebaseAttestationError("Prior automatic default row identity changed.")
    current_identities = tuple(current_automatic_build.ordered_row_identities)
    if current_identities != saved_identities:
        raise FeeRuleRebaseAttestationError("Current automatic default row identity changed.")
    if not attestation.row_safety or not all(
        row.safe_for_rebase for row in attestation.row_safety
    ):
        raise FeeRuleRebaseAttestationError("Prior automatic authority is unsafe.")
    if not current_automatic_build.row_safety or not all(
        row.safe_for_rebase for row in current_automatic_build.row_safety
    ):
        raise FeeRuleRebaseAttestationError("Current automatic authority is unsafe.")
    saved_safety_identity = tuple(
        (row.identity, row.matched_rule_id) for row in attestation.row_safety
    )
    current_safety_identity = tuple(
        (row.identity, row.matched_rule_id) for row in current_automatic_build.row_safety
    )
    if saved_safety_identity != current_safety_identity:
        raise FeeRuleRebaseAttestationError("Automatic authority safety identity changed.")
    prior_defaults = edited_values_from_payload(
        dict(attestation.automatic_values_payload)
    )
    if _flat_row_identities(prior_defaults) != saved_identities:
        raise FeeRuleRebaseAttestationError("Attested automatic row identity changed.")
    return rebase_reviewed_values(
        saved=snapshot.edited_values,
        current_defaults=current_automatic_build.automatic_values,
        row_provenance=decoded.row_provenance,
    )


def _flat_row_identities(values: Any) -> tuple[object, ...]:
    matrix_rows, manual_rows = _row_identities(values)
    return (*matrix_rows, *manual_rows)


def _rebuild_prior_defaults(*, snapshot: Any, project_id: str, automatic_defaults_provider: object):
    from backend.modules.fee_evaluation.fee_rule_seed_loader import load_bundled_fee_rule_library

    library = load_bundled_fee_rule_library(snapshot.fee_rule_version_id)
    if library is None:
        raise FeeRuleRebaseAttestationError("Prior fee-rule seed is unavailable.")
    clone = getattr(automatic_defaults_provider, "with_rule_library", None)
    if clone is not None:
        prior_provider = clone(library)
    else:
        try:
            prior_provider = copy(automatic_defaults_provider)
            setattr(prior_provider, "_rule_library", library)
        except (AttributeError, TypeError) as exc:
            raise FeeRuleRebaseAttestationError(
                "Prior fee-rule default builder is unavailable."
            ) from exc
    return current_automatic_values(project_id, prior_provider, snapshot.edited_values)


def _values_payload(values: Any) -> dict[str, object]:
    from backend.application.fee_evaluation_pricing_draft_serialization import edited_values_to_payload

    return edited_values_to_payload(values)


def _row_identities(values: Any) -> tuple[object, ...]:
    return (
        tuple(edited_row_identity(row) for row in values.rows),
        tuple(manual_row_identity(row) for row in values.manual_rows),
    )


def _bundled_version_missing(version_id: str) -> bool:
    from backend.modules.fee_evaluation.fee_rule_seed_loader import (
        load_bundled_fee_rule_library,
    )

    return load_bundled_fee_rule_library(version_id) is None
