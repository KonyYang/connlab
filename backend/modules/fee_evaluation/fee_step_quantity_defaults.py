"""Matrix Step quantity helpers for Fee Evaluation default-fill."""

from __future__ import annotations

from decimal import Decimal
import re

from backend.modules.fee_evaluation.fee_default_fill_common import (
    ZERO,
    calculated_result,
    manual_required,
)
from backend.modules.fee_evaluation.fee_default_fill_models import FeeStepQuantityContext
from backend.modules.fee_evaluation.fee_rule_models import FeeRule

MATRIX_STEP_QUANTITY_SOURCE = "Matrix Step quantity"

_PLAIN_NON_NEGATIVE_DECIMAL = re.compile(r"^\d+(?:\.\d+)?$")
_READING_PATTERN = re.compile(
    r"(?<![a-z])(\d+(?:\.\d+)?)\s*(?:reading|readings|point|points|contact|contacts)"
    r"\s*(?:/|per)\s*(?:specimen|sample)\b",
    re.I,
)


def build_reading_result(
    *,
    rule: FeeRule,
    sample_quantity_expression: str,
    source_text: str,
    step_quantities: tuple[FeeStepQuantityContext, ...],
):
    sample_qty = _plain_decimal(sample_quantity_expression)
    readings_per_specimen, matrix_quantity_review, selected_source = matrix_step_readings_per_sample(
        step_quantities
    )
    source = rule.display_name
    if matrix_quantity_review is not None:
        return manual_required(
            rule=rule,
            unit_label="reading",
            unit_price=None,
            base_fee=ZERO,
            review_reason=matrix_quantity_review,
            manual_fields=("unit_price", "units", "testing_fee"),
        )
    if readings_per_specimen is not None:
        assert selected_source is not None
        source = selected_source
    else:
        readings_per_specimen = _first_decimal(_READING_PATTERN, source_text)
    if readings_per_specimen is None:
        return manual_required(
            rule=rule,
            unit_label="reading",
            unit_price=None,
            base_fee=ZERO,
            review_reason="Enter readings/specimen",
            manual_fields=("unit_price", "units", "testing_fee"),
        )
    if sample_qty is None:
        return manual_required(
            rule=rule,
            unit_label="reading",
            unit_price=None,
            base_fee=ZERO,
            review_reason="Confirm sample quantity",
            manual_fields=("unit_price", "units", "testing_fee"),
        )
    unit_price = Decimal("1.5") if readings_per_specimen <= Decimal("20") else Decimal("1")
    return calculated_result(
        spend_time=None,
        unit_label="reading",
        unit_price=unit_price,
        units=sample_qty * readings_per_specimen,
        base_fee=ZERO,
        discount_percent=ZERO,
        source=source,
    )


def matrix_step_readings_per_sample(
    step_quantities: tuple[FeeStepQuantityContext, ...],
) -> tuple[Decimal | None, str | None, str | None]:
    if not step_quantities:
        return None, None, None
    readings: list[Decimal] = []
    sources: list[str] = []
    for quantity in step_quantities:
        if not quantity.matched or quantity.review_required:
            return None, "Confirm Matrix Step quantity", None
        value = _matrix_step_total_readings(quantity)
        if value is None:
            return None, "Confirm Matrix Step quantity", None
        source = _selected_context_source(quantity.source)
        if source is None:
            return None, "Confirm one readings authority source.", None
        readings.append(value)
        sources.append(source)
    if not readings:
        return None, None, None
    first = readings[0]
    if any(value != first for value in readings[1:]):
        return None, "Confirm Matrix Step quantity", None
    if any(source != sources[0] for source in sources[1:]):
        return None, "Confirm one readings authority source.", None
    return first, None, sources[0]


def _selected_context_source(source: str | None) -> str | None:
    value = (source or "").strip()
    if not value:
        return None
    if value == "confirmed_measurement_plan":
        return value
    if value.startswith("Confirmed Project Point Profile: revision "):
        return value
    return MATRIX_STEP_QUANTITY_SOURCE


def _matrix_step_total_readings(quantity: FeeStepQuantityContext) -> Decimal | None:
    if quantity.total_readings:
        return _plain_decimal(quantity.total_readings)
    test_points = _plain_decimal(quantity.test_points_per_sample or "")
    readings_per_point = _plain_decimal(quantity.readings_per_point or "")
    if test_points is None or readings_per_point is None:
        return None
    return test_points * readings_per_point


def _plain_decimal(value: str) -> Decimal | None:
    text = value.strip()
    if not _PLAIN_NON_NEGATIVE_DECIMAL.fullmatch(text):
        return None
    return Decimal(text)


def _first_decimal(pattern: re.Pattern[str], text: str) -> Decimal | None:
    match = pattern.search(text)
    if match is None:
        return None
    return Decimal(match.group(1))
