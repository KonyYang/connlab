"""Reviewed ConnLab defaults that extend the source fee-rule table."""

from __future__ import annotations

from decimal import Decimal
import re

from backend.modules.fee_evaluation.fee_default_fill_common import (
    ZERO,
    auto,
    calculated_result,
    manual_required,
)
from backend.modules.fee_evaluation.fee_default_fill_models import (
    FeeDefaultFillContext,
    FeeDefaultFillResult,
    FeeFieldMetadata,
)
from backend.modules.fee_evaluation.fee_rule_models import FeeRule
from backend.modules.fee_evaluation.fee_rule_matcher import normalize_fee_rule_text
from backend.modules.fee_evaluation.fee_step_quantity_defaults import (
    READING_PATTERN,
    build_reading_result,
    matrix_step_readings_per_sample,
)


_PLAIN_NON_NEGATIVE_DECIMAL = re.compile(r"^\d+(?:\.\d+)?$")
_HOUR_PATTERN = re.compile(r"(?<![a-z])(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours)\b", re.I)
_READING_DURATION_PATTERN = re.compile(
    r"(?<![a-z0-9.])(?P<value>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>minutes?|mins?|seconds?|secs?|s)(?![a-z0-9])",
    re.I,
)
_DURATION_READING_RULE_IDS = {
    "fee_rule_insulation_resistance",
    "fee_rule_dielectric_withstanding_voltage",
}


def build_reviewed_extension_default_fill(
    *,
    rule: FeeRule,
    context: FeeDefaultFillContext,
) -> FeeDefaultFillResult | None:
    """Return a reviewed extension result, or None for source-generic handling."""
    if rule.rule_id == "fee_rule_contact_resistance_specified_current":
        return _specified_current_resistance_result(rule=rule, context=context)
    if rule.rule_id == "fee_rule_dust_benign":
        return _dust_hour_result(rule=rule, context=context)
    if rule.rule_id == "fee_rule_mechanical_force":
        return _mechanical_force_result(rule=rule, context=context)
    if rule.rule_id in _DURATION_READING_RULE_IDS:
        return _duration_reading_result(rule=rule, context=context)
    return None


def _duration_reading_result(
    *,
    rule: FeeRule,
    context: FeeDefaultFillContext,
) -> FeeDefaultFillResult | None:
    """Select an explicit IR/DWV tier or leave its duration price pending."""
    durations = _duration_seconds(context.condition)
    if not durations:
        return _pending_duration_reading_result(rule=rule)
    if durations == {Decimal("60")}:
        duration_seconds = Decimal("60")
    elif durations == {Decimal("120")}:
        duration_seconds = Decimal("120")
    else:
        return None
    unit_price = Decimal("5") if duration_seconds == Decimal("60") else Decimal("10")
    return calculated_result(
        spend_time=None,
        unit_label="reading",
        unit_price=unit_price,
        units=Decimal("1"),
        base_fee=ZERO,
        discount_percent=ZERO,
        source=rule.display_name,
    )


def _pending_duration_reading_result(*, rule: FeeRule) -> FeeDefaultFillResult:
    """Keep the duration-dependent price pending while retaining known fields."""
    review_reason = "Confirm 1-minute/2-minute price."
    return FeeDefaultFillResult(
        status="review_required",
        review_required=True,
        review_reason=review_reason,
        spend_time=None,
        unit_label="reading",
        unit_price=None,
        units=Decimal("1"),
        base_fee=ZERO,
        discount_percent=ZERO,
        testing_fee=None,
        field_metadata=(
            FeeFieldMetadata(
                field="unit_price",
                state="manual_required",
                source=rule.display_name,
                message=review_reason,
            ),
            auto("unit_label", rule.display_name),
            auto("units", rule.display_name),
            auto("base_fee", rule.display_name),
            auto("discount_percent", rule.display_name),
            FeeFieldMetadata(
                field="testing_fee",
                state="manual_required",
                source=rule.display_name,
                message=review_reason,
            ),
        ),
    )


def _duration_seconds(condition: str) -> set[Decimal]:
    """Return every explicit minute/second duration found in one Matrix condition."""
    durations: set[Decimal] = set()
    for match in _READING_DURATION_PATTERN.finditer(condition or ""):
        value = Decimal(match.group("value"))
        unit = match.group("unit").lower()
        durations.add(value * Decimal("60") if unit.startswith("min") else value)
    return durations


def _mechanical_force_result(
    *,
    rule: FeeRule,
    context: FeeDefaultFillContext,
) -> FeeDefaultFillResult:
    """Apply the reviewed per-sample or per-reading mechanical-force path."""
    if _is_mechanical_force_per_sample(context):
        return _mechanical_force_per_sample_result(rule=rule, context=context)
    reading_result = build_reading_result(
        rule=rule,
        sample_quantity_expression=context.sample_quantity_expression,
        source_text=_combined_text(context),
        step_quantities=context.step_quantities,
    )
    unit_price = rule.unit_price.amount or Decimal("20")
    if reading_result.unit_price is None or reading_result.units is None:
        return manual_required(
            rule=rule,
            unit_label="reading",
            unit_price=unit_price,
            base_fee=rule.base_fee.amount or ZERO,
            review_reason=reading_result.review_reason or "Confirm readings/specimen",
            manual_fields=("units", "testing_fee"),
        )
    return calculated_result(
        spend_time=reading_result.spend_time,
        unit_label="reading",
        unit_price=unit_price,
        units=reading_result.units,
        base_fee=rule.base_fee.amount or ZERO,
        discount_percent=reading_result.discount_percent or ZERO,
        source=rule.display_name,
    )


def _mechanical_force_per_sample_result(
    *,
    rule: FeeRule,
    context: FeeDefaultFillContext,
) -> FeeDefaultFillResult:
    """Apply the reviewed 50-per-sample mating and latch force path."""
    sample_quantity = _plain_decimal(context.sample_quantity_expression)
    if sample_quantity is None:
        return manual_required(
            rule=rule,
            unit_label="sample",
            unit_price=Decimal("50"),
            base_fee=rule.base_fee.amount or ZERO,
            review_reason="Confirm sample quantity",
            manual_fields=("units", "testing_fee"),
        )
    return calculated_result(
        spend_time=None,
        unit_label="sample",
        unit_price=Decimal("50"),
        units=sample_quantity,
        base_fee=rule.base_fee.amount or ZERO,
        discount_percent=ZERO,
        source=rule.display_name,
    )


def _specified_current_resistance_result(
    *,
    rule: FeeRule,
    context: FeeDefaultFillContext,
) -> FeeDefaultFillResult:
    """Apply the reviewed CR 10-per-reading fallback without LLCR tiers."""
    unit_price = rule.unit_price.amount or Decimal("10")
    sample_quantity = _plain_decimal(context.sample_quantity_expression)
    readings_per_specimen, quantity_review, selected_source = matrix_step_readings_per_sample(
        context.step_quantities
    )
    source = selected_source or rule.display_name
    if quantity_review is not None:
        return manual_required(
            rule=rule,
            unit_label="reading",
            unit_price=unit_price,
            base_fee=ZERO,
            review_reason=quantity_review,
            manual_fields=("units", "testing_fee"),
        )
    if readings_per_specimen is None:
        readings_per_specimen = _first_decimal(READING_PATTERN, _combined_text(context))
    if readings_per_specimen is None:
        return manual_required(
            rule=rule,
            unit_label="reading",
            unit_price=unit_price,
            base_fee=ZERO,
            review_reason="Enter readings/specimen",
            manual_fields=("units", "testing_fee"),
        )
    if sample_quantity is None:
        return manual_required(
            rule=rule,
            unit_label="reading",
            unit_price=unit_price,
            base_fee=ZERO,
            review_reason="Confirm sample quantity",
            manual_fields=("units", "testing_fee"),
        )
    return calculated_result(
        spend_time=None,
        unit_label="reading",
        unit_price=unit_price,
        units=sample_quantity * readings_per_specimen,
        base_fee=ZERO,
        discount_percent=ZERO,
        source=source,
    )


def _dust_hour_result(
    *,
    rule: FeeRule,
    context: FeeDefaultFillContext,
) -> FeeDefaultFillResult:
    """Apply the reviewed one-hour Dust default unless duration is explicit."""
    hours = _first_decimal(_HOUR_PATTERN, _combined_text(context)) or Decimal("1")
    return calculated_result(
        spend_time=None,
        unit_label="hour",
        unit_price=rule.unit_price.amount or Decimal("1800"),
        units=hours,
        base_fee=rule.base_fee.amount or ZERO,
        discount_percent=ZERO,
        source=rule.display_name,
    )


def _is_mechanical_force_per_sample(context: FeeDefaultFillContext) -> bool:
    """Keep the 50/sample path for the one approved exact business label."""
    return normalize_fee_rule_text(context.test_item) == "mating un mating force"


def _combined_text(context: FeeDefaultFillContext) -> str:
    """Combine Matrix text fields used by reviewed extension parsing."""
    return " ".join(
        value
        for value in (
            context.test_item,
            context.method,
            context.condition,
            context.requirement,
            context.spend_time,
        )
        if value
    )


def _plain_decimal(value: str | None) -> Decimal | None:
    """Parse one plain non-negative decimal expression."""
    normalized = (value or "").strip()
    if not _PLAIN_NON_NEGATIVE_DECIMAL.fullmatch(normalized):
        return None
    return Decimal(normalized)


def _first_decimal(pattern: re.Pattern[str], text: str) -> Decimal | None:
    """Return the first decimal captured by a reviewed text pattern."""
    match = pattern.search(text)
    return Decimal(match.group(1)) if match else None
