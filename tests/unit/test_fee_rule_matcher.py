from __future__ import annotations

from decimal import Decimal
from typing import get_args

import pytest

from backend.modules.fee_evaluation import FeeRuleMatcher, load_active_fee_rule_library, normalize_fee_rule_text
from backend.modules.fee_evaluation.fee_rule_models import (
    FeeAmount,
    FeeRule,
    FeeRuleLibrary,
    FeeRuleMatchStatus,
    FeeRuleVersion,
)


def test_normalize_fee_rule_text_handles_mixed_language_punctuation() -> None:
    normalized = normalize_fee_rule_text("  Visual Examination, 外观检查  ")

    assert normalized == "visual examination 外观检查"


def test_fee_rule_matcher_supports_exact_alias_match() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("LLCR")

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_llcr"
    assert result.review_required is True


@pytest.mark.parametrize(
    ("test_item", "expected_rule_id"),
    [
        ("Mixed Flowing Gas corrosion (MFG)", "fee_rule_mfg_class_iia"),
        ("Mixed Flowing Gas Class IIA", "fee_rule_mfg_class_iia"),
        ("MFG Class IIIA", "fee_rule_mfg_class_iiia"),
        ("VW75174 TG19", "fee_rule_mfg_class_iiia"),
        (
            "CR at Specified Current (HP contacts only)",
            "fee_rule_contact_resistance_specified_current",
        ),
    ],
)
def test_fee_rule_matcher_supports_reviewed_fee_evaluation_aliases(
    test_item: str,
    expected_rule_id: str,
) -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item(test_item)

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == expected_rule_id


def test_fee_rule_matcher_supports_conservative_token_match() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("Visual examination after environmental test")

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_visual_exam"
    assert result.match_reason.startswith("token_alias_match:")


def test_fee_rule_matcher_treats_examination_of_product_as_visual_exam() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("Examination of Product")

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_visual_exam"
    assert result.match_reason == "exact_alias_match"


def test_fee_rule_matcher_treats_preconditioning_durability_as_durability() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("Durability (Preconditioning 20 cycles)")

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_durability"
    assert result.match_reason.startswith("token_alias_match:")


def test_fee_rule_matcher_treats_reseating_as_reseating_rule() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("Reseating")

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_reseating"
    assert result.match_reason == "exact_alias_match"


def test_fee_rule_matcher_treats_dust_exposure_as_dust_benign_rule() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("Dust exposure")

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_dust_benign"
    assert result.match_reason == "exact_alias_match"


def test_fee_rule_matcher_treats_dust_as_dust_benign_rule() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("Dust")

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_dust_benign"
    assert result.match_reason == "exact_alias_match"


def test_fee_rule_matcher_treats_current_rating_as_temperature_rise() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("CURRENT RATING")

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_temperature_rise"
    assert result.match_reason == "exact_alias_match"


def test_fee_rule_matcher_treats_normal_force_as_mechanical_force_rule() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("Normal Force")

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_mechanical_force"
    assert result.match_reason == "exact_alias_match"


def test_fee_rule_matcher_treats_force_variants_as_mechanical_force_rule() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    for test_item in (
        "Terminal force",
        "Terminal extraction force",
        "Floater Displacement Force (Side Force)",
        "Offset mating insertion force into floater",
        "Latch retention force",
    ):
        result = matcher.match_test_item(test_item)

        assert result.status == "matched"
        assert result.rule is not None
        assert result.rule.rule_id == "fee_rule_mechanical_force"


def test_fee_rule_matcher_returns_no_match_for_ambiguous_token_match() -> None:
    matcher = FeeRuleMatcher(_ambiguous_library())

    result = matcher.match_test_item("connector visual inspection package")

    assert result.status == "no_rule_match"
    assert result.rule is None
    assert result.review_required is True
    assert "Ambiguous token match" in result.match_reason
    assert result.review_reason == "Multiple fee rules matched the same test item text."


def test_fee_rule_matcher_prefers_longest_contains_alias() -> None:
    matcher = FeeRuleMatcher(_longest_alias_library())

    result = matcher.match_test_item("Visual inspection package after conditioning")

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "rule_visual_package"
    assert result.match_reason == "token_alias_match:visual inspection package"


def test_fee_rule_match_status_values_remain_unchanged() -> None:
    assert set(get_args(FeeRuleMatchStatus)) == {"matched", "no_rule_match"}


def test_fee_rule_matcher_returns_stable_no_match_when_unmatched() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("Laser welding simulation")

    assert result.status == "no_rule_match"
    assert result.rule is None
    assert result.review_reason == "No fee rule match."


@pytest.mark.parametrize(
    "test_item",
    [
        "high temperature life",
        "Low temperature life",
        "Temperature & Humidity",
        "Steam aging",
        "Thermal shock",
        "Thermal cycling (Ramp rating 3.5C/min)",
        "Thermal cycling (Ramp rating 5C/min)",
        "Whisker testing (Environmental stress)",
        "Salt spray (NSS)",
        "MFG (Class IIA)",
        "MFG (Class IIIA) VW75174 TG19",
        "Dust (Benign)",
        "Vibration",
        "Shock (half sine)",
        "Shock (Trapzoidal)",
        "Vibration + Temp cycling",
        "Microsecond discontinuity",
        "Nanosecond dicontinuity",
        "Mechanical force",
        "Automotive connector Mechanical force",
        "Offset durability",
        "Cable bending",
        "Durability",
        "LLCR",
        "DCR",
        "Contact resistance (CR)",
        "Insulation Resistance (IR)",
        "Dielectric withstanding voltage (DWV)",
        "Capacitance/Inductance",
        "Temperature rise",
        "Temperature rise with thermography",
        "Current cycling (Current ON and OFF)",
        "Solderability",
        "Resistance to solder heat",
        "Porosity",
        "SEM/EDS analysis",
        "FTIR analysis",
        "Cross section",
        "Compressive Whisker (Mechanical Stress)",
        "Hardness Testing",
        "Plating Thickness Measuring",
        "Visual exam",
        "PCB and test fixture design",
        "Report preparation",
    ],
)
def test_every_effective_source_description_matches(test_item: str) -> None:
    result = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(test_item)

    assert result.status == "matched"
    assert result.rule is not None


def _ambiguous_library() -> FeeRuleLibrary:
    version = FeeRuleVersion(
        version_id="fee_rules_v2026_06_03",
        source_file_name="Testing Fee Evaluation-Even.xls",
        source_sheet="Unit Price Reference",
        source_hash="sha256:b19cce35f774ad3a83260805f7b717d5446f23ca1a90c209a08d8cb7f91fe226",
        effective_from_basis="project.sample_received_date",
        created_at="2026-06-03T00:00:00+08:00",
    )
    amount = FeeAmount(amount=Decimal("0"), text="0")
    return FeeRuleLibrary(
        version=version,
        rules=(
            FeeRule(
                rule_id="rule_visual_a",
                display_name="Visual A",
                aliases=("connector visual inspection",),
                base_fee=amount,
                unit_price=amount,
                unit_label="sample",
                applicable_standard="N/A",
                range_condition="N/A",
                calculation_strategy="per_sample",
                review_required=False,
                review_reason=None,
            ),
            FeeRule(
                rule_id="rule_visual_b",
                display_name="Visual B",
                aliases=("visual inspection package",),
                base_fee=amount,
                unit_price=amount,
                unit_label="sample",
                applicable_standard="N/A",
                range_condition="N/A",
                calculation_strategy="per_sample",
                review_required=False,
                review_reason=None,
            ),
        ),
    )


def _longest_alias_library() -> FeeRuleLibrary:
    version = FeeRuleVersion(
        version_id="fee_rules_v2026_06_03",
        source_file_name="Testing Fee Evaluation-Even.xls",
        source_sheet="Unit Price Reference",
        source_hash="sha256:b19cce35f774ad3a83260805f7b717d5446f23ca1a90c209a08d8cb7f91fe226",
        effective_from_basis="project.sample_received_date",
        created_at="2026-06-03T00:00:00+08:00",
    )
    amount = FeeAmount(amount=Decimal("0"), text="0")
    return FeeRuleLibrary(
        version=version,
        rules=(
            FeeRule(
                rule_id="rule_visual",
                display_name="Visual",
                aliases=("visual inspection",),
                base_fee=amount,
                unit_price=amount,
                unit_label="sample",
                applicable_standard="N/A",
                range_condition="N/A",
                calculation_strategy="per_sample",
                review_required=False,
                review_reason=None,
            ),
            FeeRule(
                rule_id="rule_visual_package",
                display_name="Visual Package",
                aliases=("visual inspection package",),
                base_fee=amount,
                unit_price=amount,
                unit_label="sample",
                applicable_standard="N/A",
                range_condition="N/A",
                calculation_strategy="per_sample",
                review_required=False,
                review_reason=None,
            ),
        ),
    )
