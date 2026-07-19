from __future__ import annotations

import pytest

from backend.modules.test_plan.voltage_surge_condition_parser import (
    extract_voltage_surge_condition,
)


@pytest.mark.parametrize("waveform_unit", ("μs", "µs", "us"))
def test_extract_voltage_surge_condition_preserves_pin_scoped_facts(
    waveform_unit: str,
) -> None:
    source = (
        "Power Pin: Differential Mode: 10kA, Common Mode: 20 kA, "
        f"Waveform: 8/20 {waveform_unit} Signal Pin: Not involved"
    )

    assert extract_voltage_surge_condition(source) == (
        "Power Pin: Differential Mode 10 kA; Common Mode 20 kA; "
        "Waveform 8/20 μs; Signal Pin: Not involved"
    )


def test_extract_voltage_surge_condition_does_not_guess_detached_values() -> None:
    assert extract_voltage_surge_condition(
        "Power Pin: 10 kA, 20 kA, 8/20 μs. Signal Pin: Not involved"
    ) == "Power Pin; Signal Pin: Not involved"


def test_extract_voltage_surge_condition_omits_conflicting_mode_value() -> None:
    condition = extract_voltage_surge_condition(
        "Power Pin: Differential Mode: 10 kA; Differential Mode: 12 kA; "
        "Common Mode: 20 kA; Waveform: 8/20 us; Signal Pin: Not involved"
    )

    assert condition is not None
    assert "Differential Mode" not in condition
    assert "Common Mode 20 kA" in condition
