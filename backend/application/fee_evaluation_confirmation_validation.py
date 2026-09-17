"""Validate reviewed fee content, not incomplete autosaved input."""

from decimal import Decimal, DecimalException, ROUND_HALF_UP

from backend.application.fee_evaluation_edited_export_values import FeeEvaluationEditedExportValues


def fee_number(value: str, label: str, *, optional: bool = False) -> Decimal:
    text = str(value).strip().replace("$", "").replace(",", "")
    if not text and optional:
        return Decimal("0")
    try:
        number = Decimal(text)
    except DecimalException as exc:
        raise ValueError(f"{label} must be a finite non-negative number.") from exc
    if not number.is_finite() or number < 0:
        raise ValueError(f"{label} must be a finite non-negative number.")
    return number


def validate_confirmable_fee_values(values: FeeEvaluationEditedExportValues) -> None:
    """Independently check each row; a matching client grand total is insufficient."""
    for index, row in enumerate((*values.rows, *values.manual_rows), start=1):
        label = f"Fee row {index}"
        fee_number(row.spend_time, f"{label} Man-hour")
        price = fee_number(row.unit_price, f"{label} Unit Price")
        units = fee_number(row.units, f"{label} Units")
        base = fee_number(row.base_fee, f"{label} Base Fee", optional=True)
        discount = fee_number(row.discount.replace("%", ""), f"{label} Discount", optional=True)
        if discount > 100:
            raise ValueError(f"{label} Discount must be between 0% and 100%.")
        if not row.unit_type.strip() or row.unit_type.strip().lower() == "pending":
            raise ValueError(f"{label} Unit Type is required.")
        fee = fee_number(row.testing_fee, f"{label} Testing Fee")
        try:
            expected = price * units * (1 - discount / 100) + base
            rounded = expected.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        except DecimalException as exc:
            raise ValueError(f"{label} contains numbers too large to calculate.") from exc
        # Default/imported workbooks can retain cents; the editable UI displays whole amounts.
        # Both must derive from the same actual inputs, never an arbitrary supplied total.
        if fee not in (expected, rounded):
            raise ValueError(f"{label} Testing Fee does not match its price, units, base fee and discount. Recalculate before Confirm.")
    summary = values.summary
    fee_number(summary.condition_confirmation_spend_time, "Condition confirmation", optional=True)
    fee_number(summary.external_cost, "External Cost", optional=True)
    fee_number(summary.lab_manpower_hourly_rate, "Lab hourly rate")
