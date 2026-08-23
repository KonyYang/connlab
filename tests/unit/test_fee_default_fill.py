from __future__ import annotations

from decimal import Decimal

import pytest

from backend.modules.fee_evaluation import (
    FeeRuleMatcher,
    FeeStepQuantityContext,
    load_active_fee_rule_library,
)
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


@pytest.mark.parametrize(
    ("test_item", "rule_id"),
    [
        ("INSULATION RESISTANCE", "fee_rule_insulation_resistance"),
        ("DIELECTRIC WITHSTANDING VOLTAGE", "fee_rule_dielectric_withstanding_voltage"),
    ],
)
@pytest.mark.parametrize("condition", ["", "1mA"])
def test_ir_and_dwv_leave_price_pending_without_duration_text(
    test_item: str,
    rule_id: str,
    condition: str,
) -> None:
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(test_item)
    assert match.rule is not None and match.rule.rule_id == rule_id

    result = build_fee_default_fill(
        rule=match.rule,
        context=_context(test_item=test_item, condition=condition),
    )

    assert result.unit_label == "reading"
    assert result.unit_price is None
    assert result.units == Decimal("1")
    assert result.base_fee == Decimal("0")
    assert result.testing_fee is None
    assert result.review_required is True
    assert result.review_reason == "Confirm 1-minute/2-minute price."
    assert _field_state(result, "unit_price") == "manual_required"


@pytest.mark.parametrize(
    ("condition", "expected_unit_price"),
    [
        ("1 minute", Decimal("5")),
        ("1 minutes", Decimal("5")),
        ("1 min", Decimal("5")),
        ("1 mins", Decimal("5")),
        ("60 second", Decimal("5")),
        ("60 seconds", Decimal("5")),
        ("60 sec", Decimal("5")),
        ("60 secs", Decimal("5")),
        ("60s", Decimal("5")),
        ("60 s", Decimal("5")),
        ("2 minute", Decimal("10")),
        ("2 minutes", Decimal("10")),
        ("2 min", Decimal("10")),
        ("2 mins", Decimal("10")),
        ("120 second", Decimal("10")),
        ("120 seconds", Decimal("10")),
        ("120 sec", Decimal("10")),
        ("120 secs", Decimal("10")),
        ("120s", Decimal("10")),
        ("TEST: 120 S; 500V", Decimal("10")),
    ],
)
@pytest.mark.parametrize(
    ("test_item", "rule_id"),
    [
        ("INSULATION RESISTANCE", "fee_rule_insulation_resistance"),
        ("DIELECTRIC WITHSTANDING VOLTAGE", "fee_rule_dielectric_withstanding_voltage"),
    ],
)
def test_ir_and_dwv_select_duration_price_from_matrix_condition(
    condition: str,
    expected_unit_price: Decimal,
    test_item: str,
    rule_id: str,
) -> None:
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(test_item)
    assert match.rule is not None and match.rule.rule_id == rule_id

    result = build_fee_default_fill(
        rule=match.rule,
        context=_context(test_item=test_item, condition=condition),
    )

    assert result.unit_label == "reading"
    assert result.unit_price == expected_unit_price
    assert result.units == Decimal("1")
    assert result.base_fee == Decimal("0")
    assert result.testing_fee == expected_unit_price
    assert result.review_required is False
    assert result.review_reason is None
    assert _field_state(result, "unit_price") == "auto_filled"
    assert _field_state(result, "base_fee") == "auto_filled"


@pytest.mark.parametrize("condition", ["90 seconds", "60 seconds / 120 seconds"])
@pytest.mark.parametrize(
    "test_item",
    ["INSULATION RESISTANCE", "DIELECTRIC WITHSTANDING VOLTAGE"],
)
def test_ir_and_dwv_keep_duration_price_for_review_when_condition_is_not_decisive(
    condition: str,
    test_item: str,
) -> None:
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(test_item)
    assert match.rule is not None

    result = build_fee_default_fill(
        rule=match.rule,
        context=_context(test_item=test_item, condition=condition),
    )

    assert result.unit_price is None
    assert result.review_required is True
    assert "1-minute/2-minute" in (result.review_reason or "")


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


def test_contact_resistance_specified_current_requires_typed_authority() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_contact_resistance_specified_current",
            unit_label="reading",
            unit_price=Decimal("10"),
            strategy="per_reading",
            review_required=False,
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

    assert result.review_required is True
    assert (result.unit_price, result.units, result.testing_fee) == (None, None, None)
    assert "CR Measurement Plan" in (result.review_reason or "")


def test_contact_resistance_specified_current_has_no_default_without_typed_authority() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_contact_resistance_specified_current",
            unit_label="reading",
            unit_price=Decimal("10"),
            strategy="per_reading",
            review_required=False,
        ),
        context=_context(test_item="Contact Resistance, Specified Current"),
    )

    assert result.review_required is True
    assert result.unit_label == "reading"
    assert (result.unit_price, result.units, result.testing_fee) == (None, None, None)
    assert "CR Measurement Plan" in (result.review_reason or "")


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


def test_llcr_preserves_confirmed_profile_lineage_in_calculated_metadata() -> None:
    lineage = "Confirmed Project Point Profile: revision 3 (revision-1; sha256:profile)"
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_llcr",
            unit_label="reading",
            unit_price=None,
            strategy="per_reading",
            review_required=True,
        ),
        context=_context(
            test_item="LLCR",
            step_quantities=(
                _step_quantity(
                    test_points_per_sample="4",
                    readings_per_point="1",
                    source=lineage,
                ),
            ),
        ),
    )

    assert result.units == Decimal("20")
    assert _field_source(result, "units") == lineage


def test_llcr_requires_one_homogeneous_selected_context_source() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_llcr",
            unit_label="reading",
            unit_price=None,
            strategy="per_reading",
            review_required=True,
        ),
        context=_context(
            test_item="LLCR",
            step_quantities=(
                _step_quantity(
                    step_token="1",
                    test_points_per_sample="4",
                    readings_per_point="1",
                    source="Confirmed Project Point Profile: revision 3 (revision-1; sha256:profile)",
                ),
                _step_quantity(
                    step_token="2",
                    test_points_per_sample="4",
                    readings_per_point="1",
                    source="confirmed_measurement_plan",
                ),
            ),
        ),
    )

    assert result.review_required is True
    assert result.units is None
    assert result.review_reason == "Confirm one readings authority source."


def test_llcr_preserves_confirmed_measurement_plan_source() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_llcr",
            unit_label="reading",
            unit_price=None,
            strategy="per_reading",
            review_required=True,
        ),
        context=_context(
            test_item="LLCR",
            step_quantities=(
                _step_quantity(
                    test_points_per_sample="4",
                    readings_per_point="1",
                    source="confirmed_measurement_plan",
                ),
            ),
        ),
    )

    assert result.units == Decimal("20")
    assert _field_source(result, "units") == "confirmed_measurement_plan"


def test_llcr_rejects_context_with_missing_source() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_llcr",
            unit_label="reading",
            unit_price=None,
            strategy="per_reading",
            review_required=True,
        ),
        context=_context(
            test_item="LLCR",
            step_quantities=(
                _step_quantity(
                    test_points_per_sample="4",
                    readings_per_point="1",
                    source="",
                ),
            ),
        ),
    )

    assert result.review_required is True
    assert result.units is None
    assert result.review_reason == "Confirm one readings authority source."


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


@pytest.mark.parametrize(
    ("rule_id", "test_item", "unit_price"),
    (
        ("fee_rule_high_temperature_life", "Temperature life", Decimal("15")),
        (
            "fee_rule_temperature_humidity",
            "Humidity- Temperature Cycling",
            Decimal("25"),
        ),
    ),
)
def test_temperature_named_duration_rules_default_base_fee_to_zero_without_duration(
    rule_id: str,
    test_item: str,
    unit_price: Decimal,
) -> None:
    result = build_fee_default_fill(
        rule=_rule(
            rule_id,
            unit_label="hour",
            unit_price=unit_price,
            strategy="per_hour",
            review_required=False,
        ),
        context=_context(test_item=test_item),
    )

    assert result.review_required is True
    assert result.review_reason == ("Missing confirmed duration authority" if rule_id == "fee_rule_high_temperature_life" else "Confirm duration")
    assert result.unit_price == unit_price
    assert result.unit_label == "hour"
    assert result.units is None
    assert result.base_fee == Decimal("0")
    assert result.testing_fee is None
    assert _field_state(result, "base_fee") == "auto_filled"
    assert _field_state(result, "units") == "manual_required"


@pytest.mark.parametrize(
    ("test_item", "expected_rule_id"),
    (
        ("High Temp. Life", "fee_rule_high_temperature_life"),
        ("Cycling Temperature & Humidity", "fee_rule_temperature_humidity"),
        ("Thermal distrubance", "fee_rule_temperature_humidity"),
        ("THERMAL CYCLING", "fee_rule_thermal_cycling_3_5c"),
        ("Vibration Random", "fee_rule_vibration"),
    ),
)
def test_reviewed_hour_duration_labels_default_to_per_hour(
    test_item: str,
    expected_rule_id: str,
) -> None:
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(test_item)

    assert match.rule is not None
    assert match.rule.rule_id == expected_rule_id
    result = build_fee_default_fill(
        rule=match.rule,
        context=_context(test_item=test_item),
    )

    assert result.unit_label == "hour"


def test_unqualified_thermal_cycling_keeps_rate_specific_price_pending() -> None:
    test_item = "THERMAL CYCLING"
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(test_item)

    assert match.rule is not None
    result = build_fee_default_fill(rule=match.rule, context=_context(test_item=test_item))

    assert result.unit_label == "hour"
    assert result.unit_price is None
    assert result.review_required is True


def test_salt_spray_uses_hour_duration_from_matrix_condition() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_salt_spray_nss",
            unit_label="hour",
            unit_price=Decimal("20"),
            strategy="per_hour",
            review_required=True,
        ),
        context=_context(
            test_item="Salt Spray",
            condition="72 hours",
        ),
    )

    assert (result.review_required, result.review_reason) == (True, "Missing confirmed duration authority")
    assert result.unit_price == Decimal("20")
    assert result.unit_label == "hour"
    assert result.units is None
    assert result.base_fee is None
    assert result.testing_fee is None
    assert _field_state(result, "units") == "manual_required"


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


def test_current_rating_fully_reuses_temperature_rise_defaults() -> None:
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item("Current Rating")
    assert match.rule is not None
    assert match.rule.rule_id == "fee_rule_temperature_rise"
    assert match.rule.source_row == 33

    result = build_fee_default_fill(
        rule=match.rule,
        context=_context(
            test_item="Current Rating",
            condition="300A",
            sample_quantity_expression="5",
        ),
    )

    assert result.unit_price == Decimal("600")
    assert result.unit_label == "sample"
    assert result.units == Decimal("5")
    assert result.base_fee == Decimal("500")
    assert result.testing_fee == Decimal("3500")


def test_temperature_rise_uses_group_sample_quantity_while_current_is_pending() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_temperature_rise",
            unit_label="specimen",
            unit_price=None,
            strategy="per_specimen",
            review_required=True,
        ),
        context=_context(
            test_item="CURRENT RATING",
            sample_quantity_expression="5",
        ),
    )

    assert result.review_required is True
    assert result.review_reason == "Confirm current"
    assert result.unit_price is None
    assert result.unit_label == "sample"
    assert result.units == Decimal("5")
    assert result.testing_fee is None
    assert _field_state(result, "unit_price") == "manual_required"
    assert _field_state(result, "units") == "auto_filled"


def test_dust_benign_defaults_to_one_hour() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_dust_benign",
            unit_label="hour",
            unit_price=Decimal("1800"),
            strategy="per_hour",
            review_required=False,
        ),
        context=_context(test_item="Dust exposure", step_tokens=("5",)),
    )

    assert result.review_required is False
    assert result.unit_price == Decimal("1800")
    assert result.unit_label == "hour"
    assert result.units == Decimal("1")
    assert result.base_fee == Decimal("0")
    assert result.testing_fee == Decimal("1800")


def test_dust_benign_uses_explicit_hour_duration() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_dust_benign",
            unit_label="hour",
            unit_price=Decimal("1800"),
            strategy="per_hour",
            review_required=False,
        ),
        context=_context(test_item="Dust", condition="2 hours", step_tokens=("5",)),
    )

    assert result.review_required is False
    assert result.unit_price == Decimal("1800")
    assert result.unit_label == "hour"
    assert result.units == Decimal("2")
    assert result.testing_fee == Decimal("3600")


def test_mechanical_force_defaults_to_per_reading_pricing() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_mechanical_force",
            unit_label="reading",
            unit_price=Decimal("20"),
            strategy="per_reading",
            review_required=False,
        ),
        context=_context(
            test_item="Normal Force",
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
    assert result.unit_price == Decimal("20")
    assert result.unit_label == "reading"
    assert result.units == Decimal("30")
    assert result.base_fee == Decimal("0")
    assert result.testing_fee == Decimal("600")


def test_contact_retention_force_uses_sample_quantity_as_reading_units() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_mechanical_force",
            unit_label="reading",
            unit_price=Decimal("20"),
            strategy="per_reading",
            review_required=False,
        ),
        context=_context(
            test_item="Contact Retention Force",
            sample_quantity_expression="5",
        ),
    )

    assert result.review_required is False
    assert result.unit_price == Decimal("20")
    assert result.unit_label == "reading"
    assert result.units == Decimal("5")
    assert result.base_fee == Decimal("0")
    assert result.testing_fee == Decimal("100")


def test_contact_retention_defaults_to_per_reading() -> None:
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(
        "Contact Retention"
    )

    assert match.rule is not None
    assert match.rule.rule_id == "fee_rule_mechanical_force"
    result = build_fee_default_fill(
        rule=match.rule,
        context=_context(
            test_item="Contact Retention",
            sample_quantity_expression="5",
        ),
    )

    assert result.unit_price == Decimal("20")
    assert result.unit_label == "reading"
    assert result.units == Decimal("5")


def test_contact_retention_power_and_signal_defaults_to_per_reading() -> None:
    test_item = "CONTACT RETENTION (Power & Signal)"
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(test_item)

    assert match.rule is not None
    assert match.rule.rule_id == "fee_rule_mechanical_force"
    result = build_fee_default_fill(
        rule=match.rule,
        context=_context(test_item=test_item, sample_quantity_expression="5"),
    )

    assert result.unit_price == Decimal("20")
    assert result.unit_label == "reading"
    assert result.units == Decimal("5")


def test_solder_ability_defaults_to_per_reading() -> None:
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(
        "Solder ability"
    )

    assert match.rule is not None
    assert match.rule.rule_id == "fee_rule_solderability"
    result = build_fee_default_fill(
        rule=match.rule,
        context=_context(test_item="Solder ability"),
    )

    assert result.unit_price == Decimal("100")
    assert result.unit_label == "reading"
    assert result.units is None


def test_resistance_to_soldering_heat_defaults_to_per_sample() -> None:
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(
        "Resistance to soldering heat"
    )

    assert match.rule is not None
    assert match.rule.rule_id == "fee_rule_resistance_to_solder_heat"
    result = build_fee_default_fill(
        rule=match.rule,
        context=_context(test_item="Resistance to soldering heat"),
    )

    assert result.unit_price == Decimal("100")
    assert result.unit_label == "sample"
    assert result.units is None


def test_crimp_wending_tensile_strength_uses_sample_quantity_as_reading_units() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_mechanical_force",
            unit_label="reading",
            unit_price=Decimal("20"),
            strategy="per_reading",
            review_required=False,
        ),
        context=_context(
            test_item="Crimping/Wending Tensile Strength",
            sample_quantity_expression="5",
        ),
    )

    assert result.review_required is False
    assert result.unit_price == Decimal("20")
    assert result.unit_label == "reading"
    assert result.units == Decimal("5")
    assert result.base_fee == Decimal("0")
    assert result.testing_fee == Decimal("100")


def test_mechanical_shock_uses_row_17_price_and_fixed_occurrence_count() -> None:
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(
        "Mechanical Shock"
    )
    assert match.rule is not None

    result = build_fee_default_fill(
        rule=match.rule,
        context=_context(test_item="Mechanical Shock"),
    )

    assert result.review_required is True
    assert result.review_reason == "Confirm base fee"
    assert result.unit_price == Decimal("30")
    assert result.unit_label == "time"
    assert result.units == Decimal("18")
    assert result.base_fee is None
    assert result.testing_fee is None
    assert _field_state(result, "unit_price") == "auto_filled"
    assert _field_state(result, "units") == "auto_filled"
    assert _field_state(result, "base_fee") == "manual_required"


def test_mechanical_force_mating_unmating_defaults_to_per_sample_pricing() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_mechanical_force",
            unit_label="reading",
            unit_price=Decimal("20"),
            strategy="per_reading",
            review_required=False,
        ),
        context=_context(
            test_item="Mating/Un-mating Force",
            sample_quantity_expression="5",
        ),
    )

    assert result.review_required is False
    assert result.unit_price == Decimal("50")
    assert result.unit_label == "sample"
    assert result.units == Decimal("5")
    assert result.base_fee == Decimal("0")
    assert result.testing_fee == Decimal("250")


def test_mechanical_force_latch_does_not_default_to_per_sample_pricing() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_mechanical_force",
            unit_label="reading",
            unit_price=Decimal("20"),
            strategy="per_reading",
            review_required=False,
        ),
        context=_context(
            test_item="Latch retention force",
            sample_quantity_expression="4",
        ),
    )

    assert result.review_required is True
    assert result.unit_price == Decimal("20")
    assert result.unit_label == "reading"
    assert result.units is None
    assert result.base_fee == Decimal("0")
    assert result.testing_fee is None


def test_mechanical_force_preserves_per_reading_price_when_units_need_review() -> None:
    result = build_fee_default_fill(
        rule=_rule(
            "fee_rule_mechanical_force",
            unit_label="reading",
            unit_price=Decimal("20"),
            strategy="per_reading",
            review_required=False,
        ),
        context=_context(test_item="Normal Force"),
    )

    assert result.review_required is True
    assert result.review_reason == "Enter readings/specimen"
    assert result.unit_price == Decimal("20")
    assert result.unit_label == "reading"
    assert result.base_fee == Decimal("0")
    assert result.units is None
    assert result.testing_fee is None


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
    step_tokens: tuple[str, ...] = (),
    step_quantities: tuple[FeeStepQuantityContext, ...] = (),
) -> FeeDefaultFillContext:
    return FeeDefaultFillContext(
        test_item=test_item,
        method=method,
        condition=condition,
        requirement=requirement,
        sample_quantity_expression=sample_quantity_expression,
        spend_time=spend_time,
        step_tokens=step_tokens,
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
    source: str = "matrix_step_override",
) -> FeeStepQuantityContext:
    return FeeStepQuantityContext(
        step_token=step_token,
        step_sequence=1,
        step_suffix_note=None,
        test_points_per_sample=test_points_per_sample,
        readings_per_point=readings_per_point,
        contact_points_per_sample=contact_points_per_sample,
        total_readings=None,
        source=source,
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
