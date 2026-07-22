from __future__ import annotations

from importlib import import_module, util

import pytest


def _collectors():
    module_name = "backend.modules.test_plan.condition_text_collectors"
    assert util.find_spec(module_name) is not None, "condition collector module is required"
    return import_module(module_name)


def test_collect_condition_segments_preserves_order_filtering_and_two_segment_cap() -> None:
    module = _collectors()

    result = module.collect_condition_segments(
        "Temperature: 85 C; Humidity: 85% RH; Duration: 1000 hours",
        ("temperature", "humidity", "rh", "duration", "hours"),
    )

    assert result == "Temperature: 85 C; Humidity: 85% RH"


def test_collect_condition_segments_excludes_eia_method_clauses() -> None:
    module = _collectors()

    result = module.collect_condition_segments(
        "EIA-364-31; In accordance with EIA 364-31; Temperature: 85 C",
        ("eia", "temperature"),
    )

    assert result == "Temperature: 85 C"


def test_collect_condition_tokens_preserves_deduplication_cap_and_numeric_a_filter() -> None:
    module = _collectors()

    result = module.collect_condition_tokens(
        "20 mV, 100 mA, 5 A, 20 mV, 3 cycles, 4 hours"
    )

    assert result == "20 mV, 100 mA, 3 cycles"


@pytest.mark.parametrize(
    ("name", "args", "expected"),
    (
        (
            "extract_electrical_condition",
            ("Test voltage: 500 VDC. Test duration: 60 seconds",),
            "500VDC, 60 seconds",
        ),
        (
            "extract_temperature_rise_current",
            ("Apply 12 amperes to the sample",),
            "12A",
        ),
        (
            "extract_dust_exposure_condition",
            ("Benign dust composition 2#, 4 hours, unmated for both connectors",),
            "Benign dust composition 2#, 4 hour, unmated for both connectors",
        ),
        (
            "extract_durability_condition",
            ("200 mating/un-mating cycles, Displacement Speed - 25.4 mm/min.",),
            "200 cycles, 25.4 mm/min",
        ),
    ),
)
def test_moved_condition_helpers_preserve_existing_outputs(
    name: str,
    args: tuple[str, ...],
    expected: str,
) -> None:
    module = _collectors()
    function = getattr(module, name)
    kwargs = {"duration_labels": ("test duration",)} if name == "extract_electrical_condition" else {}

    assert function(*args, **kwargs) == expected
