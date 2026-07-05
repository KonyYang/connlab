from __future__ import annotations

from decimal import Decimal

from backend.modules.fee_evaluation.fee_default_fill import (
    FeeDefaultFillContext,
    build_fee_default_fill,
)
from backend.modules.fee_evaluation.fee_rule_models import FeeAmount, FeeRule


def test_visual_examination_default_fill_is_deterministic() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_visual_exam",
            unit_label="photo",
            unit_price=Decimal("10"),
            strategy="per_photo",
            review_required=True,
        ),
        context=_context(test_item="Visual Examination"),
    )

    assert result.review_required is False
    assert result.spend_time == Decimal("0.5")
    assert result.unit_price == Decimal("10")
    assert result.unit_label == "photo"
    assert result.units == Decimal("3")
    assert result.discount_percent == Decimal("100")
    assert result.testing_fee == Decimal("0")
    assert _field_state(result, "units") == "auto_filled"


def test_llcr_derives_total_readings_when_readings_per_specimen_is_explicit() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_llcr",
            unit_label="reading",
            unit_price=None,
            strategy="per_reading",
            review_required=True,
        ),
        context=_context(
            test_item="Contact Resistance (Low Level)",
            requirement="5 readings/specimen",
            sample_quantity_expression="5",
        ),
    )

    assert result.review_required is False
    assert result.unit_price == Decimal("1.5")
    assert result.units == Decimal("25")
    assert result.testing_fee == Decimal("37.5")


def test_llcr_marks_units_review_required_when_readings_are_missing() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_llcr",
            unit_label="reading",
            unit_price=None,
            strategy="per_reading",
            review_required=True,
        ),
        context=_context(test_item="LLCR", requirement="Resistance after conditioning"),
    )

    assert result.review_required is True
    assert result.unit_label == "reading"
    assert result.unit_price is None
    assert result.units is None
    assert result.testing_fee is None
    assert result.review_reason == "Enter readings/specimen"
    assert _field_state(result, "units") == "manual_required"


def test_durability_parses_cycles_and_applies_cycle_tier() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_durability",
            unit_label="cycle",
            unit_price=None,
            strategy="per_cycle",
            review_required=True,
        ),
        context=_context(
            test_item="Durability, 50 Cycles",
            sample_quantity_expression="5",
        ),
    )

    assert result.review_required is False
    assert result.unit_price == Decimal("2")
    assert result.units == Decimal("250")
    assert result.testing_fee == Decimal("500")


def test_temperature_rise_prefills_current_tier_and_flags_base_fee_review() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_temperature_rise",
            unit_label="specimen",
            unit_price=None,
            strategy="per_specimen",
            review_required=True,
        ),
        context=_context(
            test_item="Temperature Rise",
            condition="300A",
            sample_quantity_expression="5",
        ),
    )

    assert result.review_required is True
    assert result.review_reason == "Review base fee"
    assert result.spend_time == Decimal("4")
    assert result.unit_price == Decimal("600")
    assert result.unit_label == "sample"
    assert result.units == Decimal("5")
    assert result.base_fee == Decimal("500")
    assert result.testing_fee == Decimal("3500")
    assert _field_state(result, "base_fee") == "suggested_review"


def test_sample_preparation_default_fill_uses_group_sample_quantity() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_sample_preparation",
            unit_label="sample",
            unit_price=Decimal("50"),
            strategy="per_sample",
            review_required=False,
        ),
        context=_context(test_item="Sample preparation", sample_quantity_expression="5"),
    )

    assert result.review_required is False
    assert result.spend_time == Decimal("0.5")
    assert result.unit_price == Decimal("50")
    assert result.unit_label == "sample"
    assert result.units == Decimal("5")
    assert result.discount_percent == Decimal("100")
    assert result.testing_fee == Decimal("0")
    assert _field_state(result, "units") == "auto_filled"


def test_report_preparation_default_fill_is_backend_owned() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_report_preparation",
            unit_label="report",
            unit_price=Decimal("600"),
            strategy="fixed_per_group",
            review_required=False,
        ),
        context=_context(test_item="Report preparation"),
    )

    assert result.review_required is False
    assert result.spend_time == Decimal("4")
    assert result.unit_price == Decimal("600")
    assert result.unit_label == "report"
    assert result.units == Decimal("1")
    assert result.discount_percent == Decimal("100")
    assert result.testing_fee == Decimal("0")
    assert _field_state(result, "testing_fee") == "auto_filled"


def _field_state(result, field: str) -> str:
    return next(metadata.state for metadata in result.field_metadata if metadata.field == field)


def _context(
    *,
    test_item: str,
    method: str = "",
    condition: str = "",
    requirement: str = "",
    sample_quantity_expression: str = "5",
    spend_time: str = "",
) -> FeeDefaultFillContext:
    return FeeDefaultFillContext(
        test_item=test_item,
        method=method,
        condition=condition,
        requirement=requirement,
        sample_quantity_expression=sample_quantity_expression,
        spend_time=spend_time,
    )


def _rule(
    rule_id: str,
    *,
    unit_label: str,
    unit_price: Decimal | None,
    strategy: str,
    review_required: bool,
) -> FeeRule:
    return FeeRule(
        rule_id=rule_id,
        display_name=rule_id,
        aliases=(rule_id,),
        base_fee=FeeAmount(amount=Decimal("0"), text="0"),
        unit_price=FeeAmount(
            amount=unit_price,
            text="" if unit_price is None else format(unit_price, "f"),
        ),
        unit_label=unit_label,
        applicable_standard="N/A",
        range_condition="N/A",
        calculation_strategy=strategy,
        review_required=review_required,
        review_reason="Review required",
    )
