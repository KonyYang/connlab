from decimal import Decimal

import pytest

from backend.modules.fee_evaluation.fee_default_fill import build_fee_default_fill
from backend.modules.fee_evaluation.fee_default_fill_models import (
    FeeDefaultFillContext,
    FeeDurationAuthority,
)
from backend.modules.fee_evaluation.fee_rule_models import (
    FeeAmount,
    FeeRule,
)


def _rule(rule_id: str, price: str) -> FeeRule:
    return FeeRule(
        rule_id=rule_id,
        display_name="High temperature Life",
        aliases=(rule_id,),
        base_fee=FeeAmount(amount=Decimal("0"), text="0"),
        unit_price=FeeAmount(amount=Decimal(price), text=price),
        unit_label="hour",
        applicable_standard="N/A",
        range_condition="N/A",
        calculation_strategy="per_hour",
        review_required=False,
        review_reason=None,
    )


def _context(
    authority: FeeDurationAuthority | None,
    *,
    condition: str = "999 hours",
) -> FeeDefaultFillContext:
    return FeeDefaultFillContext(
        test_item="Long-term high temperature zone load",
        method="",
        condition=condition,
        requirement="",
        sample_quantity_expression="5",
        duration_authority=authority,
    )


def _authority(
    *,
    status: str = "usable",
    diagnostic: str | None = None,
) -> FeeDurationAuthority:
    return FeeDurationAuthority(
        confirmed_matrix_id="confirmed-1",
        confirmed_group_id="group-1",
        confirmed_row_id="row-1",
        step_sequence=1,
        step_suffix_note="",
        duration_value=Decimal("2"),
        duration_unit="days",
        normalized_hours=Decimal("48"),
        authority_revision="1",
        lineage_fingerprint="lineage-fp",
        status=status,
        diagnostic=diagnostic,
    )


def test_approved_high_temperature_rule_uses_typed_hours_only() -> None:
    result = build_fee_default_fill(
        rule=_rule("fee_rule_high_temperature_life", "15"),
        context=_context(_authority()),
    )

    assert result.status == "calculated"
    assert result.unit_price == Decimal("15")
    assert result.units == Decimal("48")
    assert result.testing_fee == Decimal("720")
    assert {item.field: item.source for item in result.field_metadata}["units"] == (
        "Confirmed Matrix duration authority: revision 1 "
        "(confirmed-1; lineage-fp)"
    )


def test_salt_spray_rule_uses_the_same_typed_hour_authority() -> None:
    result = build_fee_default_fill(
        rule=_rule("fee_rule_salt_spray_nss", "20"),
        context=_context(_authority(), condition="Salt spray prose says 999 hours"),
    )

    assert result.status == "calculated"
    assert result.unit_price == Decimal("20")
    assert result.units == Decimal("48")
    assert result.testing_fee == Decimal("960")


def test_duration_text_never_substitutes_for_missing_typed_authority() -> None:
    result = build_fee_default_fill(
        rule=_rule("fee_rule_high_temperature_life", "15"),
        context=_context(None, condition="Long-term high temperature at 999 hours"),
    )

    assert result.status == "review_required"
    assert result.units is None
    assert result.testing_fee is None
    assert result.review_reason == "Missing confirmed duration authority"


def test_unusable_typed_authority_is_review_required() -> None:
    result = build_fee_default_fill(
        rule=_rule("fee_rule_high_temperature_life", "15"),
        context=_context(_authority(status="stale", diagnostic="stale")),
    )

    assert result.status == "review_required"
    assert result.units is None
    assert result.testing_fee is None
    assert result.review_reason == "Duration authority is stale"


@pytest.mark.parametrize(
    ("rule_id", "unit_price"),
    (
        ("fee_rule_pre_high_temperature_life", "15"),
        ("fee_rule_thermal_shock", "30"),
        ("fee_rule_temperature_humidity", "25"),
        ("fee_rule_vibration", "300"),
    ),
)
def test_unrelated_duration_rules_keep_legacy_text_hours(
    rule_id: str,
    unit_price: str,
) -> None:
    rule = _rule(rule_id, unit_price)
    result = build_fee_default_fill(
        rule=rule,
        context=_context(None, condition="Legacy accepted duration: 10 hours"),
    )

    assert result.status == "calculated"
    assert result.review_required is False
    assert result.unit_price == Decimal(unit_price)
    assert result.units == Decimal("10")
    assert result.base_fee == Decimal("0")
    assert result.testing_fee == Decimal(unit_price) * Decimal("10")
    assert {item.field: item.source for item in result.field_metadata}["units"] == (
        rule.display_name
    )
