from __future__ import annotations

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
    assert "0.17" in result.requirement
