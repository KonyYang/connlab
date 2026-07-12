"""Confirmed Matrix Step quantity facts for Fee Evaluation default-fill."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStepQuantity,
    MatrixStepContactPlan,
)
from backend.modules.fee_evaluation import FeeStepQuantityContext
from backend.modules.test_plan.matrix_step_sequence_validation import ParsedStepToken

StepQuantityLookup = dict[tuple[str, str, int, str], ConfirmedMatrixStepQuantity]


def build_step_quantity_lookup(snapshot: ConfirmedMatrixSnapshot) -> StepQuantityLookup:
    lookup: StepQuantityLookup = {}
    for quantity in snapshot.step_quantities:
        lookup[
            (
                quantity.confirmed_group_id,
                quantity.confirmed_row_id,
                quantity.step_sequence,
                _suffix_identity_value(quantity.step_suffix_note),
            )
        ] = quantity
    return lookup


def build_step_quantity_contexts(
    *,
    group: ConfirmedMatrixGroup,
    row: ConfirmedMatrixRow,
    parsed_tokens: tuple[ParsedStepToken, ...],
    step_quantity_lookup: StepQuantityLookup,
    effective_contact_targets: dict[tuple[str, str, int, str], MatrixStepContactPlan] | None = None,
    effective_contact_status: str | None = None,
    is_llcr_or_specified_current: bool = False,
) -> tuple[FeeStepQuantityContext, ...]:
    contexts: list[FeeStepQuantityContext] = []
    matched_any = False
    for token in parsed_tokens:
        quantity = step_quantity_lookup.get(
            (
                group.confirmed_group_id,
                row.confirmed_row_id,
                token.sequence,
                _suffix_identity_value(token.suffix_note),
            )
        )
        if quantity is None:
            contexts.append(_unmatched_context(token))
            continue
        matched_any = True
        if is_llcr_or_specified_current and effective_contact_targets is not None:
            plan = effective_contact_targets.get(
                (
                    group.confirmed_group_id,
                    row.confirmed_row_id,
                    token.sequence,
                    _suffix_identity_value(token.suffix_note),
                )
            )
            if plan is None or not plan.included:
                contexts.append(_authority_review_context(token, effective_contact_status))
                continue
            contexts.append(
                _matched_context(
                    token=token,
                    quantity=quantity,
                    contact_plan=plan,
                    source="confirmed_measurement_plan",
                )
            )
            continue
        contexts.append(_matched_context(token=token, quantity=quantity))
    return tuple(contexts) if matched_any else ()


def _matched_context(
    *,
    token: ParsedStepToken,
    quantity: ConfirmedMatrixStepQuantity,
    contact_plan: MatrixStepContactPlan | None = None,
    source: str | None = None,
) -> FeeStepQuantityContext:
    contact_readings = _contact_plan_readings(contact_plan or quantity.contact_plan)
    test_points = contact_readings or _text(quantity.test_points_per_sample)
    readings_per_point = "1" if contact_readings else _text(quantity.readings_per_point)
    return FeeStepQuantityContext(
        step_token=token.raw_token,
        step_sequence=token.sequence,
        step_suffix_note=token.suffix_note,
        test_points_per_sample=test_points,
        readings_per_point=readings_per_point,
        contact_points_per_sample=contact_readings or _text(quantity.contact_points_per_sample),
        total_readings=contact_readings or _step_total_readings(quantity),
        source=source or quantity.source,
        review_required=quantity.review_required,
        review_reason=quantity.review_reason,
        matched=True,
    )


def _unmatched_context(token: ParsedStepToken) -> FeeStepQuantityContext:
    return FeeStepQuantityContext(
        step_token=token.raw_token,
        step_sequence=token.sequence,
        step_suffix_note=token.suffix_note,
        test_points_per_sample=None,
        readings_per_point=None,
        contact_points_per_sample=None,
        total_readings=None,
        source=None,
        review_required=True,
        review_reason="Confirm Matrix Step quantity",
        matched=False,
    )


def _authority_review_context(
    token: ParsedStepToken,
    status: str | None,
) -> FeeStepQuantityContext:
    return FeeStepQuantityContext(
        step_token=token.raw_token,
        step_sequence=token.sequence,
        step_suffix_note=token.suffix_note,
        test_points_per_sample=None,
        readings_per_point=None,
        contact_points_per_sample=None,
        total_readings=None,
        source="confirmed_measurement_plan",
        review_required=True,
        review_reason=(
            "Confirmed Measurement Plan does not include this contact target."
            if status in {"complete", "partial_compatible", "needs_review", "empty"}
            else "Confirmed Measurement Plan authority requires review."
        ),
        matched=True,
    )


def _text(value: str | None) -> str:
    return (value or "").strip()


def _suffix_identity_value(value: str | None) -> str:
    return _text(value)


def _step_total_readings(quantity: ConfirmedMatrixStepQuantity) -> str | None:
    test_points = _quantity_decimal(quantity.test_points_per_sample)
    readings = _quantity_decimal(quantity.readings_per_point)
    if test_points is None or readings is None:
        return None
    return _decimal_text(test_points * readings)


def _contact_plan_readings(plan: MatrixStepContactPlan | None) -> str | None:
    if plan is None or not plan.included:
        return None
    return _text(plan.readings_per_sample) or None


def _quantity_decimal(value: str | None) -> Decimal | None:
    text = _text(value)
    if not text:
        return None
    try:
        parsed = Decimal(text)
    except InvalidOperation:
        return None
    if parsed < 0:
        return None
    return parsed


def _decimal_text(value: Decimal | None) -> str:
    if value is None:
        return ""
    return format(value, "f")
