"""Common builders for deterministic Fee Evaluation default-fill results."""

from __future__ import annotations

from decimal import Decimal
import re

from backend.modules.fee_evaluation.fee_default_fill_models import (
    FeeDefaultField,
    FeeDefaultFillResult,
    FeeFieldMetadata,
)
from backend.modules.fee_evaluation.fee_rule_models import FeeRule

ZERO = Decimal("0")
ONE_HUNDRED = Decimal("100")
_HOUR_PATTERN = re.compile(
    r"(?<![a-z])(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours)\b",
    re.I,
)


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
    units: Decimal | None = None,
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
    if units is not None and "units" not in manual_fields:
        metadata.append(auto("units", rule.display_name))
    return FeeDefaultFillResult(
        status="review_required",
        review_required=True,
        review_reason=review_reason,
        spend_time=None,
        unit_label=unit_label,
        unit_price=unit_price,
        units=units,
        base_fee=base_fee,
        discount_percent=ZERO,
        testing_fee=None,
        field_metadata=tuple(metadata),
    )


def auto(field: FeeDefaultField, source: str) -> FeeFieldMetadata:
    return FeeFieldMetadata(field=field, state="auto_filled", source=source, message=None)


def build_legacy_duration_hour_result(
    *,
    rule: FeeRule,
    source_text: str,
) -> FeeDefaultFillResult:
    """Preserve accepted text-hour defaults for rules outside typed authority."""
    match = _HOUR_PATTERN.search(source_text)
    if match is None:
        return manual_required(
            rule=rule,
            unit_label="hour",
            unit_price=hour_unit_price(rule),
            base_fee=ZERO,
            review_reason="Confirm duration",
            manual_fields=("units", "testing_fee"),
        )
    return calculated_result(
        spend_time=None,
        unit_label="hour",
        unit_price=hour_unit_price(rule),
        units=Decimal(match.group(1)),
        base_fee=ZERO,
        discount_percent=ZERO,
        source=rule.display_name,
    )


def hour_unit_price(rule: FeeRule) -> Decimal:
    if rule.rule_id == "fee_rule_temperature_humidity":
        return Decimal("25")
    if rule.rule_id == "fee_rule_thermal_shock":
        return Decimal("30")
    if rule.rule_id in {
        "fee_rule_high_temperature_life",
        "fee_rule_pre_high_temperature_life",
    }:
        return Decimal("15")
    if rule.rule_id == "fee_rule_vibration":
        return Decimal("300")
    return rule.unit_price.amount or ZERO
