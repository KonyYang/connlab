"""Resolve exact confirmed CR specified-current Measurement Plan targets."""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal, InvalidOperation

from backend.application.contact_measurement_plan_confirmed_consumer_adapter import (
    EffectiveContactMeasurementPlan,
)
from backend.domain import ConfirmedMatrixGroup, ConfirmedMatrixRow
from backend.modules.fee_evaluation import FeeStepQuantityContext
from backend.modules.fee_evaluation import CrSpecifiedCurrentAuthority
from backend.modules.test_plan.matrix_step_sequence_validation import ParsedStepToken
from backend.application.fee_evaluation_pricing_draft_v2_contract import canonical_fingerprint

_ALLOWED_STATUSES = {"complete", "partial_compatible", "needs_review"}


def resolve_cr_specified_current_readings(
    *,
    group: ConfirmedMatrixGroup,
    row: ConfirmedMatrixRow,
    parsed_tokens: tuple[ParsedStepToken, ...],
    effective_plan: EffectiveContactMeasurementPlan | None,
) -> tuple[FeeStepQuantityContext, ...]:
    """Return one homogeneous exact-target authority, never a fallback value."""
    if effective_plan is None:
        return _blocked(parsed_tokens, "Confirmed CR Measurement Plan authority is unavailable.")

    status = str(getattr(effective_plan, "status", "authority_corrupt"))
    revision_id = getattr(effective_plan, "revision_id", None)
    revision_sequence = getattr(effective_plan, "revision_sequence", None)
    if not revision_id or revision_sequence is None:
        return _blocked(parsed_tokens, "Confirmed CR Measurement Plan lineage is unavailable.")
    fingerprint = _plan_fingerprint(effective_plan)
    if not fingerprint:
        return _blocked(parsed_tokens, "Confirmed CR Measurement Plan lineage is unavailable.")
    if status not in _ALLOWED_STATUSES:
        return _blocked(parsed_tokens, f"Confirmed CR Measurement Plan status '{status}' requires review.")
    if getattr(effective_plan, "diagnostics", ()):
        return _blocked(parsed_tokens, "Confirmed CR Measurement Plan diagnostics require review.")
    lookup = getattr(effective_plan, "lookup", None)
    if lookup is None:
        return _blocked(parsed_tokens, "Confirmed CR Measurement Plan target lookup is unavailable.")

    authorities: list[CrSpecifiedCurrentAuthority] = []
    for token in parsed_tokens:
        target = lookup.get(
            (group.confirmed_group_id, row.confirmed_row_id, token.sequence, _suffix(token.suffix_note))
        )
        if target is None:
            return _blocked(parsed_tokens, "Confirmed CR Measurement Plan target is missing.")
        plan = target.contact_plan
        if not plan.included or plan.coverage_status != "included":
            return _blocked(parsed_tokens, "Confirmed CR Measurement Plan target is excluded.")
        if plan.contact_kind != "cr_specified_current":
            return _blocked(parsed_tokens, "Confirmed CR Measurement Plan target kind is not specified-current CR.")
        value = (plan.readings_per_sample or "").strip()
        try:
            parsed = Decimal(value)
        except (InvalidOperation, ValueError):
            return _blocked(parsed_tokens, "Confirmed CR readings/specimen are invalid.")
        if not parsed.is_finite() or parsed <= 0:
            return _blocked(parsed_tokens, "Confirmed CR readings/specimen must be positive.")
        authorities.append(CrSpecifiedCurrentAuthority(
            confirmed_group_id=group.confirmed_group_id,
            confirmed_row_id=row.confirmed_row_id,
            step_sequence=token.sequence,
            step_suffix_note=_suffix(token.suffix_note),
            contact_kind=plan.contact_kind,
            readings_per_sample=format(parsed, "f"),
            revision_id=revision_id,
            revision_sequence=revision_sequence,
            fingerprint=fingerprint,
        ))

    if len({item.readings_per_sample for item in authorities}) != 1:
        return _blocked(parsed_tokens, "Confirmed CR readings/source lineage must be homogeneous.")
    return tuple(_context(token, authority) for token, authority in zip(parsed_tokens, authorities))


def _plan_fingerprint(plan: EffectiveContactMeasurementPlan) -> str | None:
    status = str(getattr(plan, "status", "authority_corrupt"))
    revision_id = getattr(plan, "revision_id", None)
    revision_sequence = getattr(plan, "revision_sequence", None)
    targets = getattr(plan, "targets", None)
    diagnostics = getattr(plan, "diagnostics", None)
    if status == "not_started" and revision_id is None:
        return None
    if not revision_id or revision_sequence is None or targets is None or diagnostics is None:
        return None
    try:
        serialized_targets = [asdict(target) for target in targets]
    except (TypeError, ValueError):
        return None
    return canonical_fingerprint({
        "status": status,
        "revision_id": revision_id,
        "revision_sequence": revision_sequence,
        "targets": serialized_targets,
        "diagnostics": list(diagnostics),
    })


def _blocked(
    tokens: tuple[ParsedStepToken, ...], reason: str
) -> tuple[FeeStepQuantityContext, ...]:
    return tuple(_context(token, _blocked_authority(token, reason)) for token in tokens)


def _context(
    token: ParsedStepToken,
    authority: CrSpecifiedCurrentAuthority,
) -> FeeStepQuantityContext:
    return FeeStepQuantityContext(
        step_token=token.raw_token,
        step_sequence=token.sequence,
        step_suffix_note=token.suffix_note,
        test_points_per_sample=authority.readings_per_sample,
        readings_per_point="1" if authority.readings_per_sample is not None else None,
        contact_points_per_sample=authority.readings_per_sample,
        total_readings=authority.readings_per_sample,
        source="confirmed_cr_measurement_plan",
        review_required=not authority.is_valid,
        review_reason=authority.diagnostic,
        matched=True,
        cr_authority=authority,
    )


def _blocked_authority(token: ParsedStepToken, reason: str) -> CrSpecifiedCurrentAuthority:
    return CrSpecifiedCurrentAuthority(
        confirmed_group_id="",
        confirmed_row_id="",
        step_sequence=token.sequence,
        step_suffix_note=_suffix(token.suffix_note),
        contact_kind="cr_specified_current",
        readings_per_sample=None,
        revision_id=None,
        revision_sequence=None,
        fingerprint=None,
        diagnostic=reason,
    )


def _suffix(value: str | None) -> str:
    return (value or "").strip()
