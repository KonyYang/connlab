from __future__ import annotations

from decimal import Decimal

import pytest

from backend.modules.fee_evaluation import FeeRuleMatcher, load_active_fee_rule_library
from backend.modules.fee_evaluation.fee_default_fill import (
    FeeDefaultFillContext,
    build_fee_default_fill,
)


_LIBRARY = load_active_fee_rule_library()


@pytest.mark.parametrize(
    "text",
    [
        "Mating/Un-mating Force",
        "MATING /UNMATING FORCE",
        "MATING/ UNMATING FORCE",
        "MATING / UNMATING FORCE",
        "mating/unmating force",
        "MATING/Un-mating FORCE",
        "mating/Un-mating force",
    ],
)
def test_complete_base_aliases_share_existing_canonical_key(text: str) -> None:
    matcher = FeeRuleMatcher(_LIBRARY)

    assert matcher.match_test_item(text).rule is not None
    assert matcher.match_test_item(text).rule.rule_id == "fee_rule_mechanical_force"

    result = build_fee_default_fill(
        rule=matcher.match_test_item(text).rule,
        context=FeeDefaultFillContext(
            test_item=text,
            method="",
            condition="",
            requirement="",
            sample_quantity_expression="7",
        ),
    )

    assert result.review_required is False
    assert result.unit_price == Decimal("50")
    assert result.unit_label == "sample"
    assert result.units == Decimal("7")


@pytest.mark.parametrize(
    "text",
    [
        "Single Pin Mating/Unmating Force",
        "SINGLE PIN MATING / UN-MATING FORCE",
        "single pin mating/ unmating force",
        "Single Pin Mating /Un-mating Force",
    ],
)
def test_single_pin_combined_aliases_keep_reading_path(text: str) -> None:
    match = FeeRuleMatcher(_LIBRARY).match_test_item(text)

    assert match.rule is not None
    assert match.rule.rule_id == "fee_rule_mechanical_force"
    result = build_fee_default_fill(
        rule=match.rule,
        context=FeeDefaultFillContext(
            test_item=text,
            method="",
            condition="",
            requirement="",
            sample_quantity_expression="7",
        ),
    )

    assert result.unit_price == Decimal("20")
    assert result.unit_label == "reading"
    assert result.review_required is True
    assert result.units is None


@pytest.mark.parametrize(
    "text",
    [
        "Mating/Unmating",
        "Mating Force",
        "Unmating Force",
        "Insertion Force",
        "Withdrawal Force",
        "Latch Force",
        "CPA force",
        "TPA force",
        "Automotive mechanical force",
    ],
)
def test_negative_force_families_do_not_enter_base_sample_exception(text: str) -> None:
    match = FeeRuleMatcher(_LIBRARY).match_test_item(text)

    if match.rule is None:
        assert match.review_required is True
        return
    result = build_fee_default_fill(
        rule=match.rule,
        context=FeeDefaultFillContext(
            test_item=text,
            method="",
            condition="",
            requirement="",
            sample_quantity_expression="7",
        ),
    )
    assert result.unit_label != "sample"
    assert result.unit_price != Decimal("50")


@pytest.mark.parametrize(
    ("text", "expected_units", "expected_review_required"),
    [
        ("contact retention force", Decimal("7"), False),
        ("Lateral Force", None, True),
    ],
)
def test_mechanical_reading_aliases_keep_their_reviewed_unit_policy(
    text: str,
    expected_units: Decimal | None,
    expected_review_required: bool,
) -> None:
    match = FeeRuleMatcher(_LIBRARY).match_test_item(text)

    assert match.rule is not None
    result = build_fee_default_fill(
        rule=match.rule,
        context=FeeDefaultFillContext(
            test_item=text,
            method="",
            condition="",
            requirement="",
            sample_quantity_expression="7",
        ),
    )

    assert result.unit_price == Decimal("20")
    assert result.unit_label == "reading"
    assert result.units == expected_units
    assert result.review_required is expected_review_required
