from __future__ import annotations

from decimal import Decimal

from backend.modules.fee_evaluation import FeeRuleMatcher, load_active_fee_rule_library
from backend.modules.fee_evaluation.fee_default_fill import (
    FeeDefaultFillContext,
    build_fee_default_fill,
)


def test_thermal_shock_canonical_condition_uses_existing_hourly_fee_rule() -> None:
    match = FeeRuleMatcher(load_active_fee_rule_library()).match_test_item("Thermal Shock")
    assert match.rule is not None
    assert match.rule.rule_id == "fee_rule_thermal_shock"

    result = build_fee_default_fill(
        rule=match.rule,
        context=FeeDefaultFillContext(
            test_item="Thermal Shock",
            method="EIA-364-32",
            condition=(
                "Method A, -40 ℃ (30 min), +105 ℃ (30 min); "
                "repeat 25 cycles; total 25 hours"
            ),
            requirement="No damage",
            sample_quantity_expression="5",
        ),
    )

    assert result.unit_price == Decimal("30")
    assert result.unit_label == "hour"
    assert result.units == Decimal("25")
    assert result.base_fee == Decimal("0")
    assert result.testing_fee == Decimal("750")
