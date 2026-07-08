"""Read-only confirmed Matrix Step quantity projection for downstream outputs."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStepQuantity,
)
from backend.modules.test_plan.matrix_step_sequence_validation import ParsedStepToken

_MISSING_REASON = "Confirm Matrix Step quantity."


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordStepQuantity:
    """Read-only Step quantity facts projected into Test Record consumers."""

    test_points_per_sample: str | None
    readings_per_point: str | None
    contact_points_per_sample: str | None
    total_readings: str | None
    status: str
    source: str | None
    review_reason: str | None


StepQuantityProjectionLookup = dict[tuple[str, str, int, str], ConfirmedMatrixStepQuantity]


def build_step_quantity_projection_lookup(
    snapshot: ConfirmedMatrixSnapshot,
) -> StepQuantityProjectionLookup:
    lookup: StepQuantityProjectionLookup = {}
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


def project_test_record_step_quantity(
    *,
    group: ConfirmedMatrixGroup,
    row: ConfirmedMatrixRow,
    token: ParsedStepToken,
    lookup: StepQuantityProjectionLookup,
) -> ConfirmedMatrixTestRecordStepQuantity | None:
    if not lookup:
        return None
    quantity = lookup.get(
        (
            group.confirmed_group_id,
            row.confirmed_row_id,
            token.sequence,
            _suffix_identity_value(token.suffix_note),
        )
    )
    if quantity is None:
        return ConfirmedMatrixTestRecordStepQuantity(
            test_points_per_sample=None,
            readings_per_point=None,
            contact_points_per_sample=None,
            total_readings=None,
            status="missing",
            source=None,
            review_reason=_MISSING_REASON,
        )
    return _matched_projection(quantity)


def _matched_projection(
    quantity: ConfirmedMatrixStepQuantity,
) -> ConfirmedMatrixTestRecordStepQuantity:
    total_readings = _step_total_readings(quantity)
    status = "review_required" if quantity.review_required else "ready"
    review_reason = quantity.review_reason
    if status == "ready" and total_readings is None:
        status = "review_required"
        review_reason = review_reason or _MISSING_REASON
    return ConfirmedMatrixTestRecordStepQuantity(
        test_points_per_sample=_text(quantity.test_points_per_sample),
        readings_per_point=_text(quantity.readings_per_point),
        contact_points_per_sample=_text(quantity.contact_points_per_sample),
        total_readings=total_readings,
        status=status,
        source=quantity.source,
        review_reason=review_reason,
    )


def _step_total_readings(quantity: ConfirmedMatrixStepQuantity) -> str | None:
    test_points = _quantity_decimal(quantity.test_points_per_sample)
    readings = _quantity_decimal(quantity.readings_per_point)
    if test_points is None or readings is None:
        return None
    return _decimal_text(test_points * readings)


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


def _suffix_identity_value(value: str | None) -> str:
    return _text(value)


def _text(value: str | None) -> str:
    return (value or "").strip()
