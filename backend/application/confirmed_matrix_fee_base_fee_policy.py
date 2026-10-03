"""Apply the common automatic Base Fee policy to Matrix Fee lines."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from backend.application.confirmed_matrix_fee_draft_models import FeeLineStatus
from backend.modules.fee_evaluation import FeeDefaultField, FeeFieldMetadata, FeeRule

ZERO = Decimal("0")
AUTOMATIC_BASE_FEE_FALLBACK_SOURCE = "Matrix Fee automatic Base Fee fallback"


@dataclass(frozen=True, slots=True)
class FeeCalculationResult:
    """Internal calculation values before one Fee Evaluation line is rendered."""

    status: FeeLineStatus
    review_required: bool
    review_reason: str | None
    spend_time: Decimal | None
    unit_label: str
    unit_price: Decimal | None
    units: Decimal | None
    base_fee: Decimal | None
    discount_percent: Decimal | None
    testing_fee: Decimal | None
    field_metadata: tuple[FeeFieldMetadata, ...]


def apply_matrix_fee_line_policies(
    *,
    calculation: FeeCalculationResult,
    rule: FeeRule | None,
    testing_fee_source: str,
    confirmed_group_count: int = 1,
) -> FeeCalculationResult:
    """Select the automatic Base Fee and derive Testing Fee when safe."""
    if confirmed_group_count > 1:
        base_fee, base_fee_source = ZERO, "Multiple confirmed Matrix groups: default Base Fee is 0"
    else:
        base_fee, base_fee_source = _automatic_base_fee(calculation, rule)
    testing_fee = _testing_fee(calculation, base_fee)
    metadata = _replace_derived_metadata(
        calculation=calculation,
        base_fee=base_fee,
        base_fee_source=base_fee_source,
        testing_fee=testing_fee,
        testing_fee_source=testing_fee_source,
    )
    status, review_required, review_reason = _review_state(calculation, metadata)
    return FeeCalculationResult(
        status=status,
        review_required=review_required,
        review_reason=review_reason,
        spend_time=calculation.spend_time,
        unit_label=calculation.unit_label,
        unit_price=calculation.unit_price,
        units=calculation.units,
        base_fee=base_fee,
        discount_percent=calculation.discount_percent,
        testing_fee=testing_fee,
        field_metadata=metadata,
    )


def _automatic_base_fee(
    calculation: FeeCalculationResult,
    rule: FeeRule | None,
) -> tuple[Decimal | None, str]:
    revised_hourly_base = (
        rule is not None
        and rule.base_fee.amount == Decimal("200")
        and 4 <= (rule.source_row or 0) <= 10
    )
    if revised_hourly_base:
        calculated = next(
            (item for item in calculation.field_metadata if item.field == "base_fee" and item.state == "auto_filled"),
            None,
        )
        if calculation.base_fee is not None and calculated is not None:
            return calculation.base_fee, calculated.source or "Confirmed Matrix duration authority"
        return None, rule.display_name
    if (
        rule is not None
        and (
            (rule.rule_id == "fee_rule_insulation_resistance" and rule.source_row == 31)
            or (rule.rule_id == "fee_rule_dielectric_withstanding_voltage" and rule.source_row == 32)
        )
        and any(item.field == "base_fee" and item.state == "manual_required" for item in calculation.field_metadata)
    ):
        return None, rule.display_name
    if rule is not None and rule.base_fee.amount is not None:
        return rule.base_fee.amount, rule.display_name
    calculated_metadata = next(
        (
            item
            for item in calculation.field_metadata
            if item.field == "base_fee" and item.state == "auto_filled"
        ),
        None,
    )
    if (
        calculation.base_fee is not None
        and calculation.base_fee != ZERO
        and calculated_metadata is not None
    ):
        return (
            calculation.base_fee,
            calculated_metadata.source or "Rule calculation",
        )
    return ZERO, AUTOMATIC_BASE_FEE_FALLBACK_SOURCE


def _testing_fee(
    calculation: FeeCalculationResult,
    base_fee: Decimal | None,
) -> Decimal | None:
    if (
        calculation.unit_price is None
        or calculation.units is None
        or calculation.discount_percent is None
        or base_fee is None
    ):
        return None
    return (
        calculation.unit_price
        * calculation.units
        * (Decimal("1") - calculation.discount_percent / Decimal("100"))
        + base_fee
    )


def _replace_derived_metadata(
    *,
    calculation: FeeCalculationResult,
    base_fee: Decimal | None,
    base_fee_source: str,
    testing_fee: Decimal | None,
    testing_fee_source: str,
) -> tuple[FeeFieldMetadata, ...]:
    metadata: list[FeeFieldMetadata] = []
    testing_fee_recorded = False
    for item in calculation.field_metadata:
        if item.field == "base_fee" and base_fee is not None:
            continue
        if item.field == "testing_fee":
            if testing_fee is not None:
                continue
            if testing_fee_recorded:
                continue
            testing_fee_recorded = True
        metadata.append(item)
    if base_fee is not None:
        metadata.append(_automatic("base_fee", base_fee_source))
    if testing_fee is not None:
        metadata.append(_automatic("testing_fee", testing_fee_source))
    return tuple(metadata)


def _review_state(
    calculation: FeeCalculationResult,
    metadata: tuple[FeeFieldMetadata, ...],
) -> tuple[FeeLineStatus, bool, str | None]:
    if calculation.status == "no_rule_match":
        return (
            calculation.status,
            calculation.review_required,
            calculation.review_reason,
        )
    review_fields = tuple(
        item
        for item in metadata
        if item.state in {"manual_required", "suggested_review"}
    )
    if review_fields:
        return (
            "review_required",
            True,
            next(
                (item.message for item in review_fields if item.message),
                calculation.review_reason,
            ),
        )
    if calculation.review_required and not calculation.field_metadata:
        return calculation.status, True, calculation.review_reason
    return "calculated", False, None


def _automatic(field: FeeDefaultField, source: str) -> FeeFieldMetadata:
    return FeeFieldMetadata(
        field=field,
        state="auto_filled",
        source=source,
        message=None,
    )
