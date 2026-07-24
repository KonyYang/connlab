from decimal import Decimal

import pytest

from backend.modules.fee_evaluation.fee_default_fill import build_fee_default_fill
from backend.modules.fee_evaluation.fee_default_fill_models import FeeDefaultFillContext
from backend.modules.fee_evaluation.fee_rule_models import FeeAmount, FeeRule


def test_temperature_rise_keeps_sample_units_when_current_is_pending() -> None:
    result = build_fee_default_fill(
        rule=_rule(),
        context=_context(sample_quantity="5", condition="Confirm current"),
    )

    assert result.status == "review_required"
    assert result.review_reason == "Confirm current"
    assert result.units == Decimal("5")
    assert result.unit_price is None
    assert result.testing_fee is None
    metadata = {item.field: item for item in result.field_metadata}
    assert metadata["units"].state == "auto_filled"
    assert metadata["unit_price"].state == "manual_required"


@pytest.mark.parametrize("sample_quantity", ("", "0", "-1", "five"))
def test_temperature_rise_invalid_sample_quantity_never_fabricates_units(
    sample_quantity: str,
) -> None:
    result = build_fee_default_fill(
        rule=_rule(),
        context=_context(sample_quantity=sample_quantity, condition="300A"),
    )

    assert result.status == "review_required"
    assert result.units is None
    assert result.testing_fee is None


def _context(*, sample_quantity: str, condition: str) -> FeeDefaultFillContext:
    return FeeDefaultFillContext(
        test_item="CURRENT RATING",
        method="",
        condition=condition,
        requirement="",
        sample_quantity_expression=sample_quantity,
    )


def _rule() -> FeeRule:
    return FeeRule(
        rule_id="fee_rule_temperature_rise",
        display_name="Temperature Rise",
        aliases=("CURRENT RATING",),
        base_fee=FeeAmount(amount=Decimal("500"), text="500"),
        unit_price=FeeAmount(amount=None, text="Pending"),
        unit_label="sample",
        applicable_standard="N/A",
        range_condition="N/A",
        calculation_strategy="manual",
        review_required=True,
        review_reason="Review base fee",
    )
