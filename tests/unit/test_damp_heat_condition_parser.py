from __future__ import annotations

from importlib import import_module, util

import pytest


def _parser():
    module_name = "backend.modules.test_plan.damp_heat_condition_parser"
    assert util.find_spec(module_name) is not None, "Damp Heat parser module is required"
    return import_module(module_name)


def test_extract_damp_heat_condition_returns_explicit_temperature_rh_duration() -> None:
    parser = _parser()

    result = parser.extract_damp_heat_condition(
        "Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)."
    )

    assert result == "Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)"


def test_extract_damp_heat_condition_normalizes_spacing_without_rewriting_values() -> None:
    parser = _parser()

    result = parser.extract_damp_heat_condition(
        "  Damp   Heat Condition: 40 ℃, 93 % RH, 21 days  "
    )

    assert result == "Damp Heat Condition: 40 ℃, 93 % RH, 21 days"


@pytest.mark.parametrize(
    "text",
    (
        "",
        "Long-term damp heat without stated condition facts.",
        "Damp Heat Condition:   ",
        "EIA-364-31 applies to this damp heat test.",
    ),
)
def test_extract_damp_heat_condition_returns_none_without_explicit_condition_fact(
    text: str,
) -> None:
    parser = _parser()

    assert parser.extract_damp_heat_condition(text) is None


def test_extract_damp_heat_condition_excludes_eia_method_segment() -> None:
    parser = _parser()

    result = parser.extract_damp_heat_condition(
        "In accordance with EIA-364-31 for humidity; Duration: 1000 hours"
    )

    assert result == "Duration: 1000 hours"


@pytest.mark.parametrize(
    "text",
    (
        "Humidity exposure shall not cause damage.",
        "Damp Heat Condition shall be reviewed.",
        "Unsupported damp heat procedure.",
        "Humidity exposure is required; Damp Heat Condition: pending review.",
    ),
)
def test_extract_damp_heat_condition_rejects_non_condition_prose(text: str) -> None:
    parser = _parser()

    assert parser.extract_damp_heat_condition(text) is None


@pytest.mark.parametrize(
    ("text", "expected"),
    (
        ("Temperature: 85℃", "Temperature: 85℃"),
        ("Humidity: 85% RH", "Humidity: 85% RH"),
        ("Duration: 1000 hours", "Duration: 1000 hours"),
        ("Duration: 24 cycles", "Duration: 24 cycles"),
        ("Damp Heat Condition: A", "Damp Heat Condition: A"),
    ),
)
def test_extract_damp_heat_condition_accepts_explicit_source_facts(
    text: str,
    expected: str,
) -> None:
    parser = _parser()

    assert parser.extract_damp_heat_condition(text) == expected


def test_extract_damp_heat_condition_drops_prose_beside_valid_fact() -> None:
    parser = _parser()

    result = parser.extract_damp_heat_condition(
        "Humidity: 85% RH; Humidity exposure shall not cause damage"
    )

    assert result == "Humidity: 85% RH"
