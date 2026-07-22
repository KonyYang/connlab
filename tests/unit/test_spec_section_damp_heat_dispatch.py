from __future__ import annotations

import backend.modules.test_plan.spec_section_text_extractor as extractor


def test_damp_heat_dispatch_delegates_before_generic_humidity(monkeypatch) -> None:
    calls: list[str] = []

    def fake_parser(text: str) -> str:
        calls.append(text)
        return "delegated damp heat"

    monkeypatch.setattr(extractor, "extract_damp_heat_condition", fake_parser, raising=False)

    detail = extractor.extract_row_details(
        section="8.9",
        section_text=(
            "8.9 Long-term damp heat. "
            "Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)."
        ),
        test_item="Long-term damp heat and humidity",
    )

    assert detail.condition == "delegated damp heat"
    assert calls == [
        "8.9 Long-term damp heat. "
        "Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)."
    ]


def test_generic_humidity_does_not_enter_damp_heat_parser(monkeypatch) -> None:
    def fail_if_called(_: str) -> str:
        raise AssertionError("generic humidity must not use the Damp Heat parser")

    monkeypatch.setattr(extractor, "extract_damp_heat_condition", fail_if_called, raising=False)

    detail = extractor.extract_row_details(
        section="8.2",
        section_text=(
            "8.2 Cyclic Temperature and Humidity - EIA 364-31 and EIA 364-1000. "
            "temperature 25 +/- 3 C at 80 +/- 5% RH and 65 +/- 3 C at 50 +/- 5% RH. "
            "Duration 24 cycles. Dwell time 1.0 hour; ramp time 30 minutes."
        ),
        test_item="Cycling Temperature& Humidity",
    )

    assert detail.condition is not None
    assert detail.condition != "delegated damp heat"


def test_damp_heat_dispatch_does_not_infer_missing_method_or_requirement(monkeypatch) -> None:
    monkeypatch.setattr(
        extractor,
        "extract_damp_heat_condition",
        lambda _: "Damp Heat Condition: 85℃, 85% RH, 1000h",
        raising=False,
    )

    detail = extractor.extract_row_details(
        section="8.9",
        section_text="8.9 Long-term damp heat. Damp Heat Condition: 85℃, 85% RH, 1000h.",
        test_item="Long-term damp heat",
    )

    assert detail.condition == "Damp Heat Condition: 85℃, 85% RH, 1000h"
    assert detail.method is None
    assert detail.requirement is None
