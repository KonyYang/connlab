from __future__ import annotations

from decimal import Decimal

from backend.application.confirmed_matrix_fee_base_fee_policy import (
    FeeCalculationResult,
    apply_matrix_fee_line_policies,
)
from backend.modules.fee_evaluation import FeeAmount, FeeFieldMetadata, FeeRule

_FALLBACK_SOURCE = "Matrix Fee automatic Base Fee fallback"


def test_common_fallback_sets_zero_and_recalculates_testing_fee() -> None:
    result = _apply(_calculation(), rule=_rule(base_fee=None))

    assert result.base_fee == Decimal("0")
    assert result.testing_fee == Decimal("18")
    assert _metadata(result, "base_fee") == (
        "auto_filled",
        _FALLBACK_SOURCE,
    )
    assert _metadata(result, "testing_fee") == (
        "auto_filled",
        "Rule calculation",
    )


def test_explicit_rule_base_fee_takes_precedence_over_fallback() -> None:
    result = _apply(_calculation(), rule=_rule(base_fee=Decimal("5")))

    assert result.base_fee == Decimal("5")
    assert result.testing_fee == Decimal("23")
    assert _metadata(result, "base_fee") == ("auto_filled", "Rule display")


def test_explicit_rule_zero_retains_rule_specific_source() -> None:
    result = _apply(_calculation(), rule=_rule(base_fee=Decimal("0")))

    assert result.base_fee == Decimal("0")
    assert _metadata(result, "base_fee") == ("auto_filled", "Rule display")


def test_missing_dependency_keeps_testing_fee_pending_without_stale_value() -> None:
    calculation = _calculation(
        units=None,
        testing_fee=Decimal("999"),
        status="review_required",
        review_required=True,
        review_reason="Confirm units",
        metadata=(
            _field("unit_price", "auto_filled", "Rule display"),
            _field("units", "manual_required", None, "Confirm units"),
            _field("base_fee", "manual_required", None, "Confirm base fee"),
            _field("testing_fee", "manual_required", None, "Confirm units"),
        ),
    )

    result = _apply(calculation, rule=_rule(base_fee=None))

    assert result.base_fee == Decimal("0")
    assert result.testing_fee is None
    assert result.status == "review_required"
    assert result.review_reason == "Confirm units"
    assert _metadata(result, "units") == ("manual_required", None)
    assert _metadata(result, "testing_fee") == ("manual_required", None)


def test_unrelated_manual_metadata_is_preserved() -> None:
    manual_unit_price = _field(
        "unit_price",
        "manual_required",
        None,
        "Confirm unit price",
    )
    calculation = _calculation(
        unit_price=None,
        testing_fee=None,
        status="review_required",
        review_required=True,
        review_reason="Confirm unit price",
        metadata=(
            manual_unit_price,
            _field("base_fee", "manual_required", None, "Confirm base fee"),
            _field("testing_fee", "manual_required", None, "Confirm unit price"),
        ),
    )

    result = _apply(calculation, rule=_rule(base_fee=None))

    assert manual_unit_price in result.field_metadata
    assert result.base_fee == Decimal("0")
    assert result.testing_fee is None
    assert result.review_required is True


def test_no_rule_line_still_receives_fallback_without_losing_review_state() -> None:
    calculation = _calculation(
        status="no_rule_match",
        review_required=True,
        review_reason="No fee rule match.",
        unit_price=None,
        units=None,
        discount=None,
        testing_fee=None,
        metadata=(),
    )

    result = _apply(calculation, rule=None)

    assert result.status == "no_rule_match"
    assert result.review_required is True
    assert result.review_reason == "No fee rule match."
    assert result.base_fee == Decimal("0")
    assert result.testing_fee is None
    assert _metadata(result, "base_fee") == (
        "auto_filled",
        _FALLBACK_SOURCE,
    )


def _apply(calculation: FeeCalculationResult, *, rule: FeeRule | None):
    return apply_matrix_fee_line_policies(
        calculation=calculation,
        rule=rule,
        testing_fee_source="Rule calculation",
    )


def _calculation(
    *,
    status="calculated",
    review_required=False,
    review_reason=None,
    unit_price=Decimal("10"),
    units=Decimal("2"),
    discount=Decimal("10"),
    testing_fee=Decimal("18"),
    metadata=None,
) -> FeeCalculationResult:
    return FeeCalculationResult(
        status=status,
        review_required=review_required,
        review_reason=review_reason,
        spend_time=None,
        unit_label="sample",
        unit_price=unit_price,
        units=units,
        base_fee=None,
        discount_percent=discount,
        testing_fee=testing_fee,
        field_metadata=metadata
        if metadata is not None
        else (
            _field("unit_price", "auto_filled", "Rule display"),
            _field("units", "auto_filled", "Rule display"),
            _field("base_fee", "manual_required", None, "Confirm base fee"),
            _field("discount_percent", "auto_filled", "Rule display"),
            _field("testing_fee", "manual_required", None, "Confirm base fee"),
        ),
    )


def _rule(*, base_fee: Decimal | None) -> FeeRule:
    return FeeRule(
        rule_id="rule-1",
        display_name="Rule display",
        aliases=("Rule display",),
        base_fee=FeeAmount(amount=base_fee, text="" if base_fee is None else str(base_fee)),
        unit_price=FeeAmount(amount=Decimal("10"), text="10"),
        unit_label="sample",
        applicable_standard="N/A",
        range_condition="N/A",
        calculation_strategy="per_sample",
        review_required=False,
        review_reason=None,
    )


def _field(field, state, source, message=None) -> FeeFieldMetadata:
    return FeeFieldMetadata(field=field, state=state, source=source, message=message)


def _metadata(result: FeeCalculationResult, field: str) -> tuple[str, str | None]:
    matches = [item for item in result.field_metadata if item.field == field]
    assert len(matches) == 1
    return matches[0].state, matches[0].source
