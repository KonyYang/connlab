"""Backend-owned manual Fee Evaluation default rows."""

from __future__ import annotations

from decimal import Decimal

from backend.application.confirmed_matrix_fee_draft_models import FeeEvaluationLineItem
from backend.domain import ConfirmedMatrixGroup, ConfirmedMatrixSnapshot
from backend.modules.fee_evaluation import (
    FeeAmount,
    FeeDefaultFillContext,
    FeeRule,
    build_fee_default_fill,
)

_SAMPLE_PREPARATION_RULE = FeeRule(
    rule_id="fee_rule_sample_preparation",
    display_name="Sample preparation",
    aliases=("Sample preparation",),
    base_fee=FeeAmount(amount=Decimal("0"), text="0"),
    unit_price=FeeAmount(amount=Decimal("50"), text="50"),
    unit_label="sample",
    applicable_standard="V1 default",
    range_condition="Matrix group sample quantity",
    calculation_strategy="per_sample",
    review_required=False,
    review_reason=None,
)
_REPORT_PREPARATION_RULE = FeeRule(
    rule_id="fee_rule_report_preparation",
    display_name="Report preparation",
    aliases=("Report preparation", "Report"),
    base_fee=FeeAmount(amount=Decimal("0"), text="0"),
    unit_price=FeeAmount(amount=Decimal("600"), text="600"),
    unit_label="report",
    applicable_standard="V1 default",
    range_condition="One report per Fee Evaluation",
    calculation_strategy="fixed_per_group",
    review_required=False,
    review_reason=None,
)


def build_sample_preparation_line(
    *,
    group: ConfirmedMatrixGroup,
    snapshot: ConfirmedMatrixSnapshot,
    rule_version_id: str,
) -> FeeEvaluationLineItem:
    result = build_fee_default_fill(
        rule=_SAMPLE_PREPARATION_RULE,
        context=FeeDefaultFillContext(
            test_item="Sample preparation",
            method="",
            condition="",
            requirement="",
            sample_quantity_expression=_text(group.sample_quantity_expression),
        ),
    )
    return FeeEvaluationLineItem(
        line_id=f"sample-preparation:{group.group_key.strip()}",
        status=result.status,
        review_required=result.review_required,
        review_reason=result.review_reason,
        confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
        confirmed_revision=snapshot.version.confirmed_revision,
        group_key=group.group_key.strip(),
        group_label=group.group_label.strip(),
        confirmed_group_id=group.confirmed_group_id,
        sample_quantity_expression=_text(group.sample_quantity_expression),
        spend_time=_decimal_text(result.spend_time),
        confirmed_row_id="",
        source_row_id=None,
        row_order=0,
        test_item="Sample preparation",
        section="",
        method="",
        condition="",
        requirement="",
        step_tokens=(),
        matched_rule_id=_SAMPLE_PREPARATION_RULE.rule_id,
        matched_rule_version_id=rule_version_id,
        matched_rule_name=_SAMPLE_PREPARATION_RULE.display_name,
        match_reason="backend_manual_default",
        calculation_strategy=_SAMPLE_PREPARATION_RULE.calculation_strategy,
        unit_label=result.unit_label,
        unit_price=result.unit_price,
        units=result.units,
        base_fee=result.base_fee,
        discount_percent=result.discount_percent,
        testing_fee=result.testing_fee,
        field_metadata=result.field_metadata,
        warnings=(),
    )


def build_report_preparation_line(
    *,
    snapshot: ConfirmedMatrixSnapshot,
    rule_version_id: str,
) -> FeeEvaluationLineItem:
    result = build_fee_default_fill(
        rule=_REPORT_PREPARATION_RULE,
        context=FeeDefaultFillContext(
            test_item="Report preparation",
            method="",
            condition="",
            requirement="",
            sample_quantity_expression="1",
        ),
    )
    return FeeEvaluationLineItem(
        line_id="manual-report-preparation",
        status=result.status,
        review_required=result.review_required,
        review_reason=result.review_reason,
        confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
        confirmed_revision=snapshot.version.confirmed_revision,
        group_key="",
        group_label="",
        confirmed_group_id="",
        sample_quantity_expression="",
        spend_time=_decimal_text(result.spend_time),
        confirmed_row_id="",
        source_row_id=None,
        row_order=0,
        test_item="Report preparation",
        section="",
        method="",
        condition="",
        requirement="",
        step_tokens=(),
        matched_rule_id=_REPORT_PREPARATION_RULE.rule_id,
        matched_rule_version_id=rule_version_id,
        matched_rule_name=_REPORT_PREPARATION_RULE.display_name,
        match_reason="backend_manual_default",
        calculation_strategy=_REPORT_PREPARATION_RULE.calculation_strategy,
        unit_label=result.unit_label,
        unit_price=result.unit_price,
        units=result.units,
        base_fee=result.base_fee,
        discount_percent=result.discount_percent,
        testing_fee=result.testing_fee,
        field_metadata=result.field_metadata,
        warnings=(),
    )


def _text(value: str | None) -> str:
    return (value or "").strip()


def _decimal_text(value: Decimal | None) -> str:
    if value is None:
        return ""
    return format(value, "f")
