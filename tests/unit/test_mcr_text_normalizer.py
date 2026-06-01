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
    assert result.requirement == "Initial <= 0.25 mΩ; ΔR <= 0.17 mΩ"


def test_temperature_rise_normalization_uses_symbolic_threshold() -> None:
    result = normalize_condition_requirement(
        test_item="Temperature rise (Via current cycling)",
        condition=None,
        requirement="shall not exceed 30 C",
        source_text="",
    )
    assert result.requirement == "<= 30 ℃"


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
    assert max_dot.requirement == "<= 30 ℃"
    assert unicode_le.requirement == "<= 30 ℃"


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
    assert result.requirement == "Mating Force <= 20 N; Un-mating Force >= 6 N"


def test_unsupported_family_remains_unchanged() -> None:
    original = "Custom requirement text without conversion"
    result = normalize_condition_requirement(
        test_item="Custom test item",
        condition=None,
        requirement=original,
        source_text=original,
    )
    assert result.requirement == original
