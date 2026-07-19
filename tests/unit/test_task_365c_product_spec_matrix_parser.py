from __future__ import annotations

from backend.modules.test_plan import ProductSpecMatrixParser


def test_product_spec_parser_applies_thermal_and_voltage_surge_mcr_rules() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1"],
                ["Voltage surge", "8.3", "1"],
                ["Temperature life", "8.5", "2"],
                ["Thermal Shock", "8.6", "3"],
            ]
        ],
        paragraphs=[
            (
                "8.3 Voltage surge. Power Pin: Differential Mode: 10 kA, "
                "Common Mode: 20 kA, Waveform: 8/20 us Signal Pin: Not involved"
            ),
            "8.5 Temperature life. Test temperature 105 C for 1000 hours.",
            (
                "8.6 Thermal Shock - EIA-364-32. Method A, -40 C (30 min), "
                "+105 C (30 min); repeat 25 cycles."
            ),
        ],
    )

    surge, temperature_life, thermal_shock = result.rows
    assert surge.condition == (
        "Power Pin: Differential Mode 10 kA; Common Mode 20 kA; "
        "Waveform 8/20 μs; Signal Pin: Not involved"
    )
    assert surge.requirement is None
    assert temperature_life.requirement == "No damage"
    assert thermal_shock.method == "EIA-364-32"
    assert thermal_shock.condition is not None
    assert thermal_shock.condition.endswith("total 25 hours")
    assert thermal_shock.requirement == "No damage"
