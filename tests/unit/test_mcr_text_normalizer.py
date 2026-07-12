from __future__ import annotations

import pytest

from backend.modules.test_plan.mcr_text_normalizer import normalize_condition_requirement


def test_llcr_normalization_compacts_initial_and_delta_r() -> None:
    result = normalize_condition_requirement(
        test_item="Contact Resistance (Low Level)",
        condition="20mV max, 100mA max",
        requirement="shall not exceed 0.25 milliohms initially",
        source_text=(
            "The low level contact resistance shall not exceed 0.25 milliohms initially "
            "and maximum change is 0.17 milliohms after treatment."
        ),
    )
    assert result.requirement == "Initial ≤ 0.25 mΩ; ΔR ≤ 0.17 mΩ"


def test_llcr_initial_only_normalization() -> None:
    result = normalize_condition_requirement(
        test_item="Contact Resistance (Low Level)",
        condition=None,
        requirement="shall not exceed 25mΩ initially",
        source_text="",
    )
    assert result.requirement == "Initial ≤ 25mΩ"


def test_llcr_single_threshold_without_initial_normalization() -> None:
    result = normalize_condition_requirement(
        test_item="Contact Resistance (Low Level)",
        condition=None,
        requirement="shall not exceed 0.6mΩ",
        source_text="",
    )
    assert result.requirement == "≤ 0.6mΩ"


def test_contact_resistance_power_uses_same_split_rules_as_llcr() -> None:
    result = normalize_condition_requirement(
        test_item="CONTACT RESISTANCE (Power)",
        condition=None,
        requirement="shall not exceed 0.25mΩ initially and maximum change is 0.17mΩ",
        source_text="",
    )
    assert result.requirement == "Initial ≤ 0.25 mΩ; ΔR ≤ 0.17 mΩ"


def test_llcr_delta_value_before_change_phrase_is_normalized() -> None:
    result = normalize_condition_requirement(
        test_item="CONTACT RESISTANCE AT LOW LEVEL (Signal)",
        condition=None,
        requirement=(
            "The low level contact resistance shall not exceed 25mΩ initially. "
            "The low level contact resistance shall also not exceed 10mΩ change in resistance"
        ),
        source_text="",
    )
    assert result.requirement == "Initial ≤ 25 mΩ; ΔR ≤ 10 mΩ"


def test_resistance_change_only_is_normalized() -> None:
    result = normalize_condition_requirement(
        test_item="Contact Resistance",
        condition=None,
        requirement="10mΩ change in resistance",
        source_text="10mΩ change in resistance",
    )
    assert result.requirement == "ΔR ≤ 10 mΩ"


def test_temperature_rise_normalization_uses_symbolic_threshold() -> None:
    result = normalize_condition_requirement(
        test_item="Temperature rise (Via current cycling)",
        condition=None,
        requirement="shall not exceed 30 C",
        source_text="",
    )
    assert result.requirement == "≤ 30 ℃"


def test_temperature_rise_normalization_supports_max_dot_and_unicode_le() -> None:
    max_dot = normalize_condition_requirement(
        test_item="Temperature rise",
        condition=None,
        requirement="Max. 30 C",
        source_text="",
    )
    unicode_le = normalize_condition_requirement(
        test_item="Temperature rise",
        condition=None,
        requirement="≤ 30 C",
        source_text="",
    )
    assert max_dot.requirement == "≤ 30 ℃"
    assert unicode_le.requirement == "≤ 30 ℃"


def test_temperature_rise_keeps_concise_threshold_not_report_curve_text() -> None:
    result = normalize_condition_requirement(
        test_item="Temperature rise (Via current cycling)",
        condition=None,
        requirement="The temperature rise shall not exceed 30 ℃",
        source_text="Output temperature vs. Current and Voltage Drop vs. Current curve.",
    )
    assert result.requirement == "≤ 30 ℃"


def test_mating_unmating_normalization_requires_both_values() -> None:
    text = (
        "The force to mate a pin to socket connector shall not exceed 20N. "
        "The un-mating force shall not less than 6N."
    )
    result = normalize_condition_requirement(
        test_item="Mating/Un-mating Force",
        condition=None,
        requirement="shall not exceed 20N",
        source_text=text,
    )
    assert result.requirement == "Mating Force ≤ 20 N; Un-mating Force ≥ 6 N"


def test_mating_unmating_normalization_supports_equals_max_min_style() -> None:
    text = (
        "Mating/Un-mating Force - EIA 364-13. "
        "Mating force = 55N MAX. "
        "Un-mating force = 30N MIN."
    )
    result = normalize_condition_requirement(
        test_item="Mating/Un-mating Force",
        condition=None,
        requirement="",
        source_text=text,
    )
    assert result.requirement == "Mating Force ≤ 55 N; Un-mating Force ≥ 30 N"


def test_ir_requirement_normalization_extracts_minimum_megohm_threshold() -> None:
    text = (
        "The insulation resistance of unsoldered, unmated connectors shall not be less than 1000MΩ "
        "(mega ohms)."
    )
    result = normalize_condition_requirement(
        test_item="Insulation Resistance",
        condition=None,
        requirement="",
        source_text=text,
    )
    assert result.requirement == "≥1,000MΩ (1GΩ)"


def test_ir_requirement_normalization_supports_reverse_megohm_minimum_order() -> None:
    for text in ["1000 megohms minimum", "1000 mega ohms minimum"]:
        result = normalize_condition_requirement(
            test_item="Insulation Resistance",
            condition=None,
            requirement=text,
            source_text=text,
        )

        assert result.requirement == "≥1,000MΩ (1GΩ)"


def test_dwv_requirement_normalization_extracts_no_evidence_and_leakage_limit() -> None:
    text = (
        "There shall be no evidence of arc-over, insulation breakdown, or excessive leakage current > 1 mA "
        "when tested in accordance with EIA 364-20."
    )
    result = normalize_condition_requirement(
        test_item="Dielectric Withstanding Voltage",
        condition=None,
        requirement="",
        source_text=text,
    )
    assert result.requirement == "No evidence of arc-over, insulation breakdown, or leakage current >1mA"


@pytest.mark.parametrize(
    ("test_item", "source_text"),
    [
        ("Pre-Durability", "Number Cycles - 20 cycles."),
        ("Pe-Durability", "Number Cycles - 20 cycles."),
        ("Durability", "Number Cycles - 200 cycles. Maximum Change: 0.17 mΩ."),
        ("Durability (Preconditioning 20 cycles)", "Number Cycles - 20 cycles."),
        ("Reseating", "Failure Criteria - No evidence of physical damage."),
        ("Thermal Shock", "Temperature Range - from -55 to +85 ℃."),
        ("Cycling Temperature& Humidity", "Duration - 24 cycles."),
        ("Cyclic Temperature and Humidity", "Duration - 24 cycles."),
        ("High temperature Life", "Test Temperature - 125℃. Maximum Change: 0.17 mΩ."),
        ("Pre-High Temperature Life", "Test Temperature - 125℃."),
        ("Thermal Disturbance", "Temperature range between 15 ℃ and 85 ℃."),
        ("MFG", "Class IIA. Maximum Change: 0.17 mΩ."),
        ("Mixed Flowing Gas corrosion", "Class IIA. Maximum Change: 0.17 mΩ."),
        ("Dust exposure", "Benign Dust Composition. Maximum Change: 0.17 mΩ."),
    ],
)
def test_report_style_treatment_families_normalize_requirement_to_no_damage(
    test_item: str,
    source_text: str,
) -> None:
    result = normalize_condition_requirement(
        test_item=test_item,
        condition=None,
        requirement="Maximum Change: 0.17 mΩ",
        source_text=source_text,
    )
    assert result.requirement == "No damage"


@pytest.mark.parametrize(
    ("test_item", "micro_symbol"),
    [
        ("Random Vibration", "µs"),
        ("Vibration (Random)", "μs"),
        ("Mechanical Shock", "us"),
    ],
)
def test_report_style_discontinuity_families_include_no_discontinuity(
    test_item: str,
    micro_symbol: str,
) -> None:
    result = normalize_condition_requirement(
        test_item=test_item,
        condition=None,
        requirement=f"No discontinuities greater than 1 {micro_symbol}",
        source_text=f"No discontinuities greater than 1 {micro_symbol}. Maximum Change: 0.17 mΩ.",
    )
    assert result.requirement == "No damage, No discontinuity >1us"


def test_unrelated_numeric_requirement_is_not_replaced_with_no_damage() -> None:
    original = "Displacement Force ≤ 40 N"
    result = normalize_condition_requirement(
        test_item="Floater Displacement Force",
        condition=None,
        requirement=original,
        source_text=original,
    )
    assert result.requirement == original


def test_report_style_allowlist_does_not_guess_from_section_text_only() -> None:
    original = "Maximum force ≤ 40 N"
    result = normalize_condition_requirement(
        test_item="Custom Force Requirement",
        condition=None,
        requirement=original,
        source_text="Thermal shock and vibration wording appears here, but row item is not allowlisted.",
    )
    assert result.requirement == original


def test_unsupported_family_remains_unchanged() -> None:
    original = "Custom requirement text without conversion"
    result = normalize_condition_requirement(
        test_item="Custom test item",
        condition=None,
        requirement=original,
        source_text=original,
    )
    assert result.requirement == original


def test_initial_voltage_requirement_normalizes_to_initial_symbolic_form() -> None:
    result = normalize_condition_requirement(
        test_item="Contact Resistance (specified current)",
        condition=None,
        requirement="shall not exceed 0.015V initially",
        source_text="",
    )
    assert result.requirement == "Initial ≤ 15mV"


def test_initial_millivolt_requirement_keeps_millivolt_unit() -> None:
    result = normalize_condition_requirement(
        test_item="Contact Resistance (specified current)",
        condition=None,
        requirement="shall not exceed 15mV initially",
        source_text="",
    )
    assert result.requirement == "Initial ≤ 15mV"


def test_initial_voltage_requirement_supports_not_to_exceed_variant() -> None:
    result = normalize_condition_requirement(
        test_item="Contact Resistance (specified current)",
        condition=None,
        requirement="voltage drop not to exceed 0.020V initially",
        source_text="",
    )
    assert result.requirement == "Initial ≤ 20mV"


def test_initial_voltage_requirement_supports_symbolic_le_variant() -> None:
    result = normalize_condition_requirement(
        test_item="Contact Resistance (specified current)",
        condition=None,
        requirement="<= 0.015V initial",
        source_text="",
    )
    assert result.requirement == "Initial ≤ 15mV"


def test_llcr_alias_works_without_llcr_keyword_in_source_text() -> None:
    result = normalize_condition_requirement(
        test_item="Contact Resistance (Low Level)",
        condition="20mV max, 100mA max",
        requirement="shall not exceed 0.25 milliohms initially",
        source_text="maximum change is 0.17 milliohms after treatment.",
    )
    assert result.requirement is not None
    assert result.requirement.startswith("Initial ≤")
    assert "0.25" in result.requirement


def test_specified_current_condition_uses_adc_unit() -> None:
    result = normalize_condition_requirement(
        test_item="Contact Resistance, Specified Current",
        condition="75 a",
        requirement="≤15mV",
        source_text="Test Current - 75 amperes DC.",
    )

    assert result.condition == "75 ADC"
