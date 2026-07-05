"""Common builders for deterministic Fee Evaluation default-fill results."""

from __future__ import annotations

from decimal import Decimal

from backend.modules.fee_evaluation.fee_default_fill_models import (
    FeeDefaultField,
    FeeDefaultFillResult,
    FeeFieldMetadata,
)
from backend.modules.fee_evaluation.fee_rule_models import FeeRule

ZERO = Decimal("0")
ONE_HUNDRED = Decimal("100")


def calculated_result(
    *,
    spend_time: Decimal | None,
    unit_label: str,
    unit_price: Decimal,
    units: Decimal,
    base_fee: Decimal,
    discount_percent: Decimal,
    source: str,
) -> FeeDefaultFillResult:
    testing_fee = unit_price * units * (Decimal("1") - discount_percent / Decimal("100")) + base_fee
    metadata: list[FeeFieldMetadata] = [
        auto("unit_price", source),
        auto("unit_label", source),
        auto("units", source),
        auto("base_fee", source),
        auto("discount_percent", source),
        auto("testing_fee", source),
    ]
    if spend_time is not None:
        metadata.insert(0, auto("spend_time", source))
    return FeeDefaultFillResult(
        status="calculated",
        review_required=False,
        review_reason=None,
        spend_time=spend_time,
        unit_label=unit_label,
        unit_price=unit_price,
        units=units,
        base_fee=base_fee,
        discount_percent=discount_percent,
        testing_fee=testing_fee,
        field_metadata=tuple(metadata),
    )


def manual_required(
    *,
    rule: FeeRule,
    unit_label: str,
    unit_price: Decimal | None,
    base_fee: Decimal | None,
    review_reason: str,
    manual_fields: tuple[FeeDefaultField, ...],
) -> FeeDefaultFillResult:
    metadata = [
        auto("unit_label", rule.display_name),
        *(
            FeeFieldMetadata(
                field=field,
                state="manual_required",
                source=rule.display_name,
                message=review_reason,
            )
            for field in manual_fields
        ),
    ]
    if unit_price is not None and "unit_price" not in manual_fields:
        metadata.append(auto("unit_price", rule.display_name))
    if base_fee is not None and "base_fee" not in manual_fields:
        metadata.append(auto("base_fee", rule.display_name))
    return FeeDefaultFillResult(
        status="review_required",
        review_required=True,
        review_reason=review_reason,
        spend_time=None,
        unit_label=unit_label,
        unit_price=unit_price,
        units=None,
        base_fee=base_fee,
        discount_percent=ZERO,
        testing_fee=None,
        field_metadata=tuple(metadata),
    )


def auto(field: FeeDefaultField, source: str) -> FeeFieldMetadata:
    return FeeFieldMetadata(field=field, state="auto_filled", source=source, message=None)
