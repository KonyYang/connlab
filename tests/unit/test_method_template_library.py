from __future__ import annotations

from backend.modules.test_plan.method_template_matcher import (
    apply_fill_empty_fallback,
    match_template,
)


def test_match_template_supports_visual_and_llcr_aliases() -> None:
    visual = match_template("Examination of Product")
    llcr = match_template("Contact Resistance (Low Level)")

    assert visual is not None
    assert visual.family == "visual"
    assert llcr is not None
    assert llcr.family == "llcr"


def test_apply_fill_empty_fallback_fills_only_empty_fields() -> None:
    filled = apply_fill_empty_fallback(
        test_item="Visual Inspection",
        method=None,
        condition=None,
        requirement=None,
    )

    assert filled.method == "EIA-364-18B"
    assert filled.condition == "10x min magnification"
    assert filled.requirement == "No detrimental condition"


def test_apply_fill_empty_fallback_does_not_override_non_empty_values() -> None:
    preserved = apply_fill_empty_fallback(
        test_item="Visual Inspection",
        method="IEC 60512-1-1",
        condition="custom condition",
        requirement="custom requirement",
    )

    assert preserved.method == "IEC 60512-1-1"
    assert preserved.condition == "custom condition"
    assert preserved.requirement == "custom requirement"


def test_thermal_shock_does_not_match_mechanical_shock_template() -> None:
    no_match = apply_fill_empty_fallback(
        test_item="Thermal Shock",
        method=None,
        condition=None,
        requirement=None,
    )

    assert no_match.method is None
    assert no_match.matched_family is None


def test_dimension_and_final_inspection_do_not_match_visual_template() -> None:
    dimension = apply_fill_empty_fallback(
        test_item="Dimension Inspection",
        method=None,
        condition=None,
        requirement=None,
    )
    final = apply_fill_empty_fallback(
        test_item="Final Inspection",
        method=None,
        condition=None,
        requirement=None,
    )

    assert dimension.method is None
    assert dimension.matched_family is None
    assert final.method is None
    assert final.matched_family is None
