from __future__ import annotations

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_v2_rebase import (
    rebase_reviewed_values,
)


def test_rebase_refreshes_automatic_llcr_units_and_testing_fee_but_keeps_manual_price_fields() -> None:
    saved = _values(units="1", testing_fee="1", unit_price="9", base_fee="7", discount="15%", notes="operator note")
    defaults = _values(units="15", testing_fee="135", unit_price="3", base_fee="0", discount="0%", notes="")

    rebased = rebase_reviewed_values(saved=saved, current_defaults=defaults)
    row = rebased.rows[0]

    assert row.units == "15"
    assert row.testing_fee == "135"
    assert row.unit_price == "9"
    assert row.base_fee == "7"
    assert row.discount == "15%"
    assert row.notes == "operator note"


def test_rebase_provenance_refreshes_only_system_fields() -> None:
    saved = _values(
        units="1",
        testing_fee="1",
        unit_price="9",
        base_fee="7",
        discount="15%",
        notes="operator note",
    )
    defaults = _values(
        units="15",
        testing_fee="135",
        unit_price="3",
        base_fee="0",
        discount="0%",
        notes="",
    )

    rebased = rebase_reviewed_values(
        saved=saved,
        current_defaults=defaults,
        row_provenance={"line-llcr": ("unit_price", "base_fee", "discount", "notes")},
    )
    row = rebased.rows[0]

    assert row.units == "15"
    assert row.testing_fee == "135"
    assert row.unit_price == "9"
    assert row.base_fee == "7"
    assert row.discount == "15%"
    assert row.notes == "operator note"


def _values(*, units: str, testing_fee: str, unit_price: str, base_fee: str, discount: str, notes: str) -> FeeEvaluationEditedExportValues:
    return FeeEvaluationEditedExportValues(
        rows=(
            FeeEvaluationEditedExportRow(
                source_line_id="line-llcr",
                confirmed_group_id="group-1",
                confirmed_row_id="row-llcr",
                step_token="1",
                step_index=0,
                spend_time="2",
                unit_price=unit_price,
                unit_type="per reading",
                units=units,
                base_fee=base_fee,
                discount=discount,
                testing_fee=testing_fee,
                notes=notes,
            ),
        ),
        summary=FeeEvaluationEditedExportSummary("0", "0", "", "200"),
    )
