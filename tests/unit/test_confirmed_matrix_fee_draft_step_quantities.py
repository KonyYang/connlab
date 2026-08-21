from __future__ import annotations

from decimal import Decimal

from backend.application.confirmed_matrix_fee_draft_service import (
    BuildConfirmedMatrixFeeDraftCommand,
    ConfirmedMatrixFeeDraftService,
)
from tests.unit.test_confirmed_matrix_fee_draft_service import (
    _ConfirmedStore,
    _fixture_row,
    _single_rule_library,
    _snapshot,
    _step_quantity,
)


def test_fee_draft_marks_marker_sample_quantity_review_required_for_per_sample() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                sample_quantity_expression="5+(5e)",
                row=_fixture_row("Sample preparation"),
            )
        ),
        rule_library=_single_rule_library(
            rule_id="fee_rule_sample_prep",
            display_name="Sample preparation",
            aliases=("Sample preparation",),
            unit_price=Decimal("50"),
            base_fee=Decimal("0"),
            strategy="per_sample",
            review_required=False,
        ),
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "review_required"
    assert line.units is None
    assert line.testing_fee is None
    assert "sample quantity" in (line.review_reason or "").lower()


def test_fee_draft_uses_confirmed_step_quantities_for_llcr_units() -> None:
    row = _fixture_row("Contact Resistance (Low Level)", requirement="5 readings/specimen")
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                row=row,
                step_quantities=(
                    _step_quantity(
                        row=row,
                        test_points_per_sample="3",
                        readings_per_point="2",
                    ),
                ),
            )
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "calculated"
    assert line.review_required is False
    assert line.unit_label == "reading"
    assert line.unit_price == Decimal("1.5")
    assert line.units == Decimal("30")
    assert line.testing_fee == Decimal("45")
    assert any(
        metadata.field == "units" and metadata.source == "Matrix Step quantity"
        for metadata in line.field_metadata
    )


def test_fee_draft_marks_conflicting_step_quantities_review_required() -> None:
    row = _fixture_row("Contact Resistance (Low Level)")
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                row=row,
                cell_value="1 2",
                step_quantities=(
                    _step_quantity(
                        row=row,
                        step_sequence=1,
                        raw_token="1",
                        test_points_per_sample="3",
                        readings_per_point="2",
                    ),
                    _step_quantity(
                        row=row,
                        step_sequence=2,
                        raw_token="2",
                        test_points_per_sample="4",
                        readings_per_point="2",
                    ),
                ),
            )
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "review_required"
    assert line.review_required is True
    assert line.units is None
    assert line.testing_fee is None
    assert line.review_reason == "Confirm Matrix Step quantity"
