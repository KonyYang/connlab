from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from backend.modules.fee_evaluation import FeeRuleMatcher, load_active_fee_rule_library
from backend.modules.fee_evaluation.fee_rule_seed_loader import load_fee_rule_library
from backend.modules.fee_evaluation.fee_default_fill import (
    FeeDefaultFillContext,
    build_fee_default_fill,
)
from backend.modules.fee_evaluation.fee_default_fill_models import FeeStepQuantityContext

_SEEDS = Path(__file__).parents[2] / "backend" / "modules" / "fee_evaluation" / "seeds"


def test_manifest_activates_new_seed_without_rewriting_prior_versions() -> None:
    active = load_active_fee_rule_library()
    old_r5 = load_fee_rule_library(_SEEDS / "fee_rules_v2026_07_16.json")
    old_r6 = load_fee_rule_library(_SEEDS / "fee_rules_v2026_07_17.json")
    old_r7 = load_fee_rule_library(_SEEDS / "fee_rules_v2026_08_22.json")
    old_r8 = load_fee_rule_library(_SEEDS / "fee_rules_v2026_08_22_r8.json")
    old_r9 = load_fee_rule_library(_SEEDS / "fee_rules_v2026_08_23_r9.json")
    old_r10 = load_fee_rule_library(_SEEDS / "fee_rules_v2026_08_23_r10.json")

    assert active.version.version_id == "fee_rules_v2026_08_23_r11"
    assert old_r5.version.version_id == "fee_rules_v2026_07_16_r5"
    assert old_r6.version.version_id == "fee_rules_v2026_07_17_r6"
    assert old_r7.version.version_id == "fee_rules_v2026_08_22_r7"
    assert old_r8.version.version_id == "fee_rules_v2026_08_22_r8"
    assert old_r9.version.version_id == "fee_rules_v2026_08_23_r9"
    assert old_r10.version.version_id == "fee_rules_v2026_08_23_r10"
    assert old_r5.version.source_hash == active.version.source_hash
    assert old_r6.version.source_hash == active.version.source_hash
    assert old_r7.version.source_hash == active.version.source_hash
    assert old_r8.version.source_hash == active.version.source_hash
    assert old_r9.version.source_hash == active.version.source_hash
    assert old_r10.version.source_hash == active.version.source_hash


@pytest.mark.parametrize(
    "text",
    [
        "Temperature life",
        "Temperature-life",
        "  TEMPERATURE\nLIFE ",
    ],
)
def test_temperature_life_is_an_exact_high_temperature_alias(text: str) -> None:
    result = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(text)

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_high_temperature_life"


@pytest.mark.parametrize(
    "text",
    [
        "Lateral Force",
        "contact retention force",
        "Single Pin Mating Force",
        "Single Pin Unmating Force",
    ],
)
def test_approved_force_aliases_match_mechanical_force(text: str) -> None:
    result = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(text)

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_mechanical_force"


@pytest.mark.parametrize(
    "text",
    [
        "Mating Force",
        "Unmating Force",
        "Insertion Force",
        "Withdrawal Force",
        "Latch Force",
        "Latch retention force",
    ],
)
def test_generic_force_families_do_not_use_sample_exception(text: str) -> None:
    result = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(text)

    assert result.rule is not None
    filled = build_fee_default_fill(
        rule=result.rule,
        context=FeeDefaultFillContext(
            test_item=text,
            method="",
            condition="",
            requirement="",
            sample_quantity_expression="5",
        ),
    )

    assert filled.unit_label != "sample"
    assert filled.unit_price != Decimal("50")


@pytest.mark.parametrize("text", ["CPA force", "TPA force", "Automotive mechanical force"])
def test_automotive_force_aliases_remain_manual(text: str) -> None:
    result = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(text)

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_automotive_mechanical_force"
    assert result.review_required is True


@pytest.mark.parametrize(
    ("text", "expected_units"),
    [
        ("Lateral Force", Decimal("30")),
        ("contact retention force", Decimal("5")),
        ("Single Pin Mating Force", Decimal("30")),
        ("Single Pin Unmating Force", Decimal("30")),
    ],
)
def test_approved_force_aliases_use_reading_defaults(
    text: str,
    expected_units: Decimal,
) -> None:
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item(text)
    assert match.rule is not None

    result = build_fee_default_fill(
        rule=match.rule,
        context=FeeDefaultFillContext(
            test_item=text,
            method="",
            condition="",
            requirement="",
            sample_quantity_expression="5",
            step_quantities=(
                FeeStepQuantityContext(
                    step_token="1",
                    step_sequence=1,
                    step_suffix_note=None,
                    test_points_per_sample="3",
                    readings_per_point="2",
                    contact_points_per_sample=None,
                    total_readings=None,
                    source="matrix_step_override",
                    review_required=False,
                    review_reason=None,
                    matched=True,
                ),
            ),
        ),
    )

    assert result.unit_price == Decimal("20")
    assert result.unit_label == "reading"
    assert result.units == expected_units
