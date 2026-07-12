from __future__ import annotations

from decimal import Decimal

from backend.modules.fee_evaluation import FeeStepQuantityContext
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


def test_llcr_prefers_matrix_step_quantity_over_text_readings() -> None:
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
            step_quantities=(
                _step_quantity(
                    test_points_per_sample="3",
                    readings_per_point="2",
                ),
            ),
        ),
    )

    assert result.review_required is False
    assert result.unit_price == Decimal("1.5")
    assert result.units == Decimal("30")
    assert result.testing_fee == Decimal("45")
    assert _field_source(result, "units") == "Matrix Step quantity"


def test_llcr_marks_review_when_matrix_step_quantities_conflict() -> None:
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
            step_quantities=(
                _step_quantity(
                    step_token="1",
                    test_points_per_sample="3",
                    readings_per_point="2",
                ),
                _step_quantity(
                    step_token="2",
                    test_points_per_sample="4",
                    readings_per_point="2",
                ),
            ),
        ),
    )

    assert result.review_required is True
    assert result.units is None
    assert result.testing_fee is None
    assert result.review_reason == "Confirm Matrix Step quantity"
    assert _field_state(result, "units") == "manual_required"


def test_contact_resistance_specified_current_uses_matrix_step_quantity() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_contact_resistance_specified_current",
            unit_label="reading",
            unit_price=None,
            strategy="per_reading",
            review_required=True,
        ),
        context=_context(
            test_item="Contact Resistance (Power)",
            sample_quantity_expression="5",
            step_quantities=(
                _step_quantity(
                    test_points_per_sample="5",
                    readings_per_point="5",
                ),
            ),
        ),
    )

    assert result.review_required is False
    assert result.unit_price == Decimal("1")
    assert result.units == Decimal("125")
    assert result.testing_fee == Decimal("125")


def test_llcr_marks_review_when_matrix_step_quantity_requires_review() -> None:
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
            step_quantities=(
                _step_quantity(
                    test_points_per_sample="3",
                    readings_per_point="2",
                    review_required=True,
                ),
            ),
        ),
    )

    assert result.review_required is True
    assert result.units is None
    assert result.testing_fee is None
    assert result.review_reason == "Confirm Matrix Step quantity"


def test_llcr_accepts_multiple_steps_with_same_matrix_step_quantity() -> None:
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
            sample_quantity_expression="5",
            step_quantities=(
                _step_quantity(
                    step_token="1",
                    test_points_per_sample="3",
                    readings_per_point="2",
                ),
                _step_quantity(
                    step_token="2",
                    test_points_per_sample="2",
                    readings_per_point="3",
                ),
            ),
        ),
    )

    assert result.review_required is False
    assert result.unit_price == Decimal("1.5")
    assert result.units == Decimal("30")
    assert result.testing_fee == Decimal("45")


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


def test_reseating_uses_explicit_cycles_with_sample_multiplier() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_reseating",
            unit_label="cycle",
            unit_price=Decimal("2"),
            strategy="per_cycle",
            review_required=False,
        ),
        context=_context(
            test_item="Reseating",
            condition="Manual 10 cycles",
            sample_quantity_expression="5",
        ),
    )

    assert result.review_required is False
    assert result.unit_price == Decimal("2")
    assert result.unit_label == "cycle"
    assert result.units == Decimal("50")
    assert result.testing_fee == Decimal("100")


def test_reseating_defaults_to_three_cycles_when_cycles_are_absent() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_reseating",
            unit_label="cycle",
            unit_price=Decimal("2"),
            strategy="per_cycle",
            review_required=False,
        ),
        context=_context(
            test_item="Reseating",
            condition="Manual",
            sample_quantity_expression="5",
        ),
    )

    assert result.review_required is False
    assert result.unit_label == "cycle"
    assert result.units == Decimal("15")
    assert result.testing_fee == Decimal("30")


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


def _field_source(result, field: str) -> str | None:
    return next(metadata.source for metadata in result.field_metadata if metadata.field == field)


def _context(
    *,
    test_item: str,
    method: str = "",
    condition: str = "",
    requirement: str = "",
    sample_quantity_expression: str = "5",
    spend_time: str = "",
    step_quantities: tuple[FeeStepQuantityContext, ...] = (),
) -> FeeDefaultFillContext:
    return FeeDefaultFillContext(
        test_item=test_item,
        method=method,
        condition=condition,
        requirement=requirement,
        sample_quantity_expression=sample_quantity_expression,
        spend_time=spend_time,
        step_quantities=step_quantities,
    )


def _step_quantity(
    *,
    step_token: str = "1",
    test_points_per_sample: str | None,
    readings_per_point: str | None,
    contact_points_per_sample: str | None = None,
    review_required: bool = False,
    matched: bool = True,
) -> FeeStepQuantityContext:
    return FeeStepQuantityContext(
        step_token=step_token,
        step_sequence=1,
        step_suffix_note=None,
        test_points_per_sample=test_points_per_sample,
        readings_per_point=readings_per_point,
        contact_points_per_sample=contact_points_per_sample,
        total_readings=None,
        source="matrix_step_override",
        review_required=review_required,
        review_reason=None,
        matched=matched,
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
