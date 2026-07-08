"""Deterministic V1 Fee Evaluation default-fill rules."""

from __future__ import annotations

from decimal import Decimal
import re

from backend.modules.fee_evaluation.fee_default_fill_common import (
    ONE_HUNDRED,
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
from backend.modules.fee_evaluation.fee_step_quantity_defaults import (
    build_reading_result,
)

_PLAIN_NON_NEGATIVE_DECIMAL = re.compile(r"^\d+(?:\.\d+)?$")
_HOUR_PATTERN = re.compile(r"(?<![a-z])(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours)\b", re.I)
_DAY_PATTERN = re.compile(r"(?<![a-z])(\d+(?:\.\d+)?)\s*(?:d|day|days)\b", re.I)
_CYCLE_PATTERN = re.compile(r"(?<![a-z])(\d+(?:\.\d+)?)\s*(?:cycle|cycles)\b", re.I)
_CURRENT_PATTERN = re.compile(r"(?<![a-z])(\d+(?:\.\d+)?)\s*(?:a|amp|amps)\b", re.I)
def build_fee_default_fill(
    *,
    rule: FeeRule,
    context: FeeDefaultFillContext,
) -> FeeDefaultFillResult:
    """Return V1 deterministic defaults or review-required partial values."""
    if rule.rule_id == "fee_rule_sample_preparation":
        return _sample_preparation_result(rule=rule, context=context)
    if rule.rule_id == "fee_rule_report_preparation":
        return calculated_result(
            spend_time=Decimal("4"),
            unit_label="report",
            unit_price=rule.unit_price.amount or Decimal("600"),
            units=Decimal("1"),
            base_fee=ZERO,
            discount_percent=ONE_HUNDRED,
            source=rule.display_name,
        )
    if rule.rule_id == "fee_rule_visual_exam":
        return calculated_result(
            spend_time=Decimal("0.5"),
            unit_label="photo",
            unit_price=rule.unit_price.amount or Decimal("10"),
            units=Decimal("3"),
            base_fee=ZERO,
            discount_percent=ONE_HUNDRED,
            source=rule.display_name,
        )
    if rule.rule_id in {"fee_rule_llcr", "fee_rule_contact_resistance_specified_current"}:
        return build_reading_result(
            rule=rule,
            sample_quantity_expression=context.sample_quantity_expression,
            source_text=_combined_text(context),
            step_quantities=context.step_quantities,
        )
    if rule.rule_id == "fee_rule_durability":
        return _cycle_result(rule=rule, context=context)
    if rule.rule_id in {
        "fee_rule_high_temperature_life",
        "fee_rule_pre_high_temperature_life",
        "fee_rule_thermal_shock",
        "fee_rule_temperature_humidity",
        "fee_rule_vibration",
    }:
        return _duration_hour_result(rule=rule, context=context)
    if rule.rule_id == "fee_rule_mfg_class_iia":
        return _duration_day_result(rule=rule, context=context)
    if rule.rule_id == "fee_rule_microsecond_discontinuity":
        return calculated_result(
            spend_time=None,
            unit_label="time",
            unit_price=Decimal("300"),
            units=Decimal("1"),
            base_fee=ZERO,
            discount_percent=ZERO,
            source=rule.display_name,
        )
    if rule.rule_id == "fee_rule_mechanical_shock":
        return manual_required(
            rule=rule,
            unit_label="time",
            unit_price=Decimal("30"),
            base_fee=ZERO,
            review_reason="Confirm units",
            manual_fields=("units", "testing_fee"),
        )
    if rule.rule_id == "fee_rule_mechanical_force":
        return _per_sample_result(rule=rule, context=context, unit_price=Decimal("50"))
    if rule.rule_id == "fee_rule_temperature_rise":
        return _temperature_rise_result(rule=rule, context=context)
    return _fallback_result(rule=rule, context=context)


def _cycle_result(*, rule: FeeRule, context: FeeDefaultFillContext) -> FeeDefaultFillResult:
    sample_qty = _plain_decimal(context.sample_quantity_expression)
    cycles = _first_decimal(_CYCLE_PATTERN, _combined_text(context))
    if cycles is None:
        return manual_required(
            rule=rule,
            unit_label="cycle",
            unit_price=None,
            base_fee=None,
            review_reason="Confirm cycles",
            manual_fields=("unit_price", "units", "base_fee", "testing_fee"),
        )
    if sample_qty is None:
        return manual_required(
            rule=rule,
            unit_label="cycle",
            unit_price=None,
            base_fee=None,
            review_reason="Confirm sample quantity",
            manual_fields=("unit_price", "units", "base_fee", "testing_fee"),
        )
    if cycles <= Decimal("50"):
        unit_price = Decimal("2")
    elif cycles <= Decimal("250"):
        unit_price = Decimal("1")
    else:
        unit_price = Decimal("0.5")
    units = sample_qty * cycles
    testing_fee = unit_price * units
    return FeeDefaultFillResult(
        status="calculated",
        review_required=False,
        review_reason=None,
        spend_time=None,
        unit_label="cycle",
        unit_price=unit_price,
        units=units,
        base_fee=None,
        discount_percent=ZERO,
        testing_fee=testing_fee,
        field_metadata=(
            auto("unit_price", rule.display_name),
            auto("unit_label", rule.display_name),
            auto("units", rule.display_name),
            auto("discount_percent", rule.display_name),
            auto("testing_fee", rule.display_name),
        ),
    )


def _duration_hour_result(*, rule: FeeRule, context: FeeDefaultFillContext) -> FeeDefaultFillResult:
    hours = _first_decimal(_HOUR_PATTERN, _combined_text(context))
    if hours is None:
        return manual_required(
            rule=rule,
            unit_label="hour",
            unit_price=_hour_unit_price(rule),
            base_fee=None,
            review_reason="Confirm duration",
            manual_fields=("units", "base_fee", "testing_fee"),
        )
    return calculated_result(
        spend_time=None,
        unit_label="hour",
        unit_price=_hour_unit_price(rule),
        units=hours,
        base_fee=ZERO,
        discount_percent=ZERO,
        source=rule.display_name,
    )


def _duration_day_result(*, rule: FeeRule, context: FeeDefaultFillContext) -> FeeDefaultFillResult:
    days = _first_decimal(_DAY_PATTERN, _combined_text(context))
    if days is None:
        return manual_required(
            rule=rule,
            unit_label="day",
            unit_price=Decimal("1000"),
            base_fee=None,
            review_reason="Confirm duration",
            manual_fields=("units", "base_fee", "discount_percent", "testing_fee"),
        )
    return calculated_result(
        spend_time=None,
        unit_label="day",
        unit_price=Decimal("1000"),
        units=days,
        base_fee=ZERO,
        discount_percent=ZERO,
        source=rule.display_name,
    )


def _per_sample_result(
    *,
    rule: FeeRule,
    context: FeeDefaultFillContext,
    unit_price: Decimal,
) -> FeeDefaultFillResult:
    sample_qty = _plain_decimal(context.sample_quantity_expression)
    if sample_qty is None:
        return manual_required(
            rule=rule,
            unit_label="sample",
            unit_price=unit_price,
            base_fee=None,
            review_reason="Confirm sample quantity",
            manual_fields=("units", "base_fee", "testing_fee"),
        )
    return calculated_result(
        spend_time=None,
        unit_label="sample",
        unit_price=unit_price,
        units=sample_qty,
        base_fee=ZERO,
        discount_percent=ZERO,
        source=rule.display_name,
    )


def _sample_preparation_result(
    *,
    rule: FeeRule,
    context: FeeDefaultFillContext,
) -> FeeDefaultFillResult:
    sample_qty = _plain_decimal(context.sample_quantity_expression)
    if sample_qty is None:
        return manual_required(
            rule=rule,
            unit_label="sample",
            unit_price=rule.unit_price.amount or Decimal("50"),
            base_fee=ZERO,
            review_reason="Confirm sample quantity",
            manual_fields=("units", "testing_fee"),
        )
    return calculated_result(
        spend_time=Decimal("0.5"),
        unit_label="sample",
        unit_price=rule.unit_price.amount or Decimal("50"),
        units=sample_qty,
        base_fee=ZERO,
        discount_percent=ONE_HUNDRED,
        source=rule.display_name,
    )


def _temperature_rise_result(
    *,
    rule: FeeRule,
    context: FeeDefaultFillContext,
) -> FeeDefaultFillResult:
    sample_qty = _plain_decimal(context.sample_quantity_expression)
    current = _first_decimal(_CURRENT_PATTERN, _combined_text(context))
    if current is None:
        return manual_required(
            rule=rule,
            unit_label="sample",
            unit_price=None,
            base_fee=Decimal("500"),
            review_reason="Confirm current",
            manual_fields=("unit_price", "units", "base_fee", "testing_fee"),
        )
    if sample_qty is None:
        return manual_required(
            rule=rule,
            unit_label="sample",
            unit_price=None,
            base_fee=Decimal("500"),
            review_reason="Confirm sample quantity",
            manual_fields=("unit_price", "units", "base_fee", "testing_fee"),
        )
    if current <= Decimal("240"):
        unit_price = Decimal("500")
    elif current <= Decimal("500"):
        unit_price = Decimal("600")
    elif current <= Decimal("1000"):
        unit_price = Decimal("700")
    else:
        unit_price = Decimal("800")
    base_fee = Decimal("500")
    units = sample_qty
    return FeeDefaultFillResult(
        status="review_required",
        review_required=True,
        review_reason="Review base fee",
        spend_time=Decimal("4"),
        unit_label="sample",
        unit_price=unit_price,
        units=units,
        base_fee=base_fee,
        discount_percent=ZERO,
        testing_fee=unit_price * units + base_fee,
        field_metadata=(
            auto("spend_time", rule.display_name),
            auto("unit_price", rule.display_name),
            auto("unit_label", rule.display_name),
            auto("units", rule.display_name),
            FeeFieldMetadata(
                field="base_fee",
                state="suggested_review",
                source=rule.display_name,
                message="Review base fee",
            ),
            auto("discount_percent", rule.display_name),
            auto("testing_fee", rule.display_name),
        ),
    )


def _fallback_result(*, rule: FeeRule, context: FeeDefaultFillContext) -> FeeDefaultFillResult:
    if rule.review_required:
        return manual_required(
            rule=rule,
            unit_label=rule.unit_label,
            unit_price=rule.unit_price.amount,
            base_fee=rule.base_fee.amount,
            review_reason=rule.review_reason or "Review pricing",
            manual_fields=("units", "testing_fee"),
        )
    if rule.unit_price.amount is None:
        return manual_required(
            rule=rule,
            unit_label=rule.unit_label,
            unit_price=None,
            base_fee=rule.base_fee.amount,
            review_reason="Review unit price",
            manual_fields=("unit_price", "testing_fee"),
        )
    if rule.base_fee.amount is None:
        return manual_required(
            rule=rule,
            unit_label=rule.unit_label,
            unit_price=rule.unit_price.amount,
            base_fee=None,
            review_reason="Review base fee",
            manual_fields=("base_fee", "testing_fee"),
        )
    if rule.calculation_strategy in {"per_sample", "per_specimen"}:
        sample_qty = _plain_decimal(context.sample_quantity_expression)
        if sample_qty is None:
            return manual_required(
                rule=rule,
                unit_label=rule.unit_label,
                unit_price=rule.unit_price.amount,
                base_fee=rule.base_fee.amount,
                review_reason="Confirm sample quantity",
                manual_fields=("units", "testing_fee"),
            )
        return calculated_result(
            spend_time=None,
            unit_label=rule.unit_label,
            unit_price=rule.unit_price.amount,
            units=sample_qty,
            base_fee=rule.base_fee.amount,
            discount_percent=ZERO,
            source=rule.display_name,
        )
    if rule.calculation_strategy == "fixed_per_group":
        if not context.step_tokens:
            return manual_required(
                rule=rule,
                unit_label=rule.unit_label,
                unit_price=rule.unit_price.amount,
                base_fee=rule.base_fee.amount,
                review_reason="Confirm selected steps",
                manual_fields=("units", "testing_fee"),
            )
        return calculated_result(
            spend_time=None,
            unit_label=rule.unit_label,
            unit_price=rule.unit_price.amount,
            units=Decimal("1"),
            base_fee=rule.base_fee.amount,
            discount_percent=ZERO,
            source=rule.display_name,
        )
    return manual_required(
        rule=rule,
        unit_label=rule.unit_label,
        unit_price=rule.unit_price.amount,
        base_fee=rule.base_fee.amount,
        review_reason=rule.review_reason or "Review pricing",
        manual_fields=("units", "testing_fee"),
    )


def _hour_unit_price(rule: FeeRule) -> Decimal:
    if rule.rule_id in {"fee_rule_temperature_humidity"}:
        return Decimal("25")
    if rule.rule_id in {"fee_rule_thermal_shock"}:
        return Decimal("30")
    if rule.rule_id in {"fee_rule_high_temperature_life", "fee_rule_pre_high_temperature_life"}:
        return Decimal("15")
    if rule.rule_id == "fee_rule_vibration":
        return Decimal("300")
    return rule.unit_price.amount or ZERO

def _combined_text(context: FeeDefaultFillContext) -> str:
    return " ".join(
        part
        for part in (
            context.test_item,
            context.method,
            context.condition,
            context.requirement,
            context.spend_time,
        )
        if part
    )


def _first_decimal(pattern: re.Pattern[str], text: str) -> Decimal | None:
    match = pattern.search(text)
    if match is None:
        return None
    return Decimal(match.group(1))


def _plain_decimal(value: str) -> Decimal | None:
    text = value.strip()
    if not _PLAIN_NON_NEGATIVE_DECIMAL.fullmatch(text):
        return None
    return Decimal(text)
