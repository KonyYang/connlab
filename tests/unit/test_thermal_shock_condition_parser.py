from __future__ import annotations

from backend.modules.test_plan.thermal_shock_condition_parser import (
    extract_thermal_shock_condition,
)


def test_extract_thermal_shock_condition_derives_total_dwell_hours() -> None:
    source = (
        "EIA-364-32, Method A, -40℃ (30 min), +105℃ (30 min); "
        "repeat 25 cycles."
    )

    assert extract_thermal_shock_condition(source) == (
        "Method A, -40 ℃ (30 min), +105 ℃ (30 min); "
        "repeat 25 cycles; total 25 hours"
    )


def test_extract_thermal_shock_condition_does_not_derive_incomplete_duration() -> None:
    condition = extract_thermal_shock_condition(
        "Method A, -40 C (30 min), +105 C; repeat 25 cycles."
    )

    assert condition is not None
    assert "Method A" in condition
    assert "repeat 25 cycles" in condition
    assert "total" not in condition


def test_extract_thermal_shock_condition_omits_conflicting_cycle_fact() -> None:
    condition = extract_thermal_shock_condition(
        "Method A, -40 C (30 min), +105 C (30 min); "
        "repeat 25 cycles, repeat 30 cycles."
    )

    assert condition is not None
    assert "repeat" not in condition
    assert "total" not in condition
