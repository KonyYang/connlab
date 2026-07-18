from __future__ import annotations

from decimal import Decimal

import pytest

from backend.application.confirmed_matrix_fee_draft_service import (
    BuildConfirmedMatrixFeeDraftCommand,
    ConfirmedMatrixFeeDraftService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
)


class _Store:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot) -> None:
        self.snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        if self.snapshot.version.project_id == project_id:
            return self.snapshot
        return None


def test_two_groups_use_only_their_own_sample_quantity() -> None:
    snapshot = _snapshot(("5", "9"), ("MATING /UNMATING FORCE", "Mating/Un-mating Force"))
    draft = ConfirmedMatrixFeeDraftService(confirmed_store=_Store(snapshot)).build_draft(
        BuildConfirmedMatrixFeeDraftCommand(project_id="P1")
    )

    lines = {line.confirmed_group_id: line for group in draft.groups for line in group.line_items}

    assert set(lines) == {"cmg-1", "cmg-2"}
    assert lines["cmg-1"].unit_price == Decimal("50")
    assert lines["cmg-1"].unit_label == "sample"
    assert lines["cmg-1"].units == Decimal("5")
    assert lines["cmg-1"].testing_fee == Decimal("250")
    assert lines["cmg-2"].unit_price == Decimal("50")
    assert lines["cmg-2"].unit_label == "sample"
    assert lines["cmg-2"].units == Decimal("9")
    assert lines["cmg-2"].testing_fee == Decimal("450")


@pytest.mark.parametrize("quantity", ["", "invalid"])
def test_missing_or_invalid_owning_quantity_stays_manual_review(quantity: str) -> None:
    snapshot = _snapshot((quantity,), ("Mating/Unmating Force",))
    draft = ConfirmedMatrixFeeDraftService(confirmed_store=_Store(snapshot)).build_draft(
        BuildConfirmedMatrixFeeDraftCommand(project_id="P1")
    )

    line = draft.groups[0].line_items[0]

    assert line.review_required is True
    assert line.status == "review_required"
    assert line.unit_price == Decimal("50")
    assert line.unit_label == "sample"
    assert line.units is None
    assert line.testing_fee is None


def _snapshot(quantities: tuple[str, ...], labels: tuple[str, ...]) -> ConfirmedMatrixSnapshot:
    groups = tuple(
        ConfirmedMatrixGroup(
            confirmed_group_id=f"cmg-{index}",
            confirmed_matrix_id="cmv-1",
            draft_group_id=f"draft-group-{index}",
            source_group_snapshot_id=f"source-group-{index}",
            group_order=index,
            group_key=f"g{index}",
            group_label=str(index),
            sample_quantity_expression=quantity,
        )
        for index, quantity in enumerate(quantities, start=1)
    )
    rows = tuple(
        ConfirmedMatrixRow(
            confirmed_row_id=f"cmr-{index}",
            confirmed_matrix_id="cmv-1",
            draft_row_id=f"draft-row-{index}",
            source_row_snapshot_id=f"source-row-{index}",
            row_order=index,
            test_item=label,
            source_section="6.1",
            method="EIA-364-18",
            condition="",
            requirement="",
        )
        for index, label in enumerate(labels, start=1)
    )
    cells = tuple(
        ConfirmedMatrixCell(
            confirmed_cell_id=f"cell-{index}",
            confirmed_matrix_id="cmv-1",
            confirmed_row_id=row.confirmed_row_id,
            confirmed_group_id=group.confirmed_group_id,
            draft_row_id=row.draft_row_id,
            draft_group_id=group.draft_group_id,
            cell_value="1",
        )
        for index, (group, row) in enumerate(zip(groups, rows), start=1)
    )
    step_quantities = tuple(
        ConfirmedMatrixStepQuantity(
            confirmed_step_quantity_id=f"step-{index}",
            confirmed_matrix_id="cmv-1",
            confirmed_group_id=group.confirmed_group_id,
            confirmed_row_id=row.confirmed_row_id,
            draft_group_id=group.draft_group_id,
            draft_row_id=row.draft_row_id,
            step_sequence=1,
            step_suffix_note=None,
            raw_token="1",
            test_points_per_sample=str(index + 1),
            readings_per_point=str(index + 2),
            contact_points_per_sample=None,
            source="matrix_step_override",
            review_required=False,
            review_reason=None,
            confirmed_at="2026-07-18T09:00:00+08:00",
        )
        for index, (group, row) in enumerate(zip(groups, rows), start=1)
    )
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="cmv-1",
            project_id="P1",
            project_matrix_draft_id="draft-1",
            source_import_id="import-1",
            source_snapshot_id="snapshot-1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-07-18T09:00:00+08:00",
            sample_received_date="2026-07-18",
        ),
        groups=groups,
        rows=rows,
        cells=cells,
        step_quantities=step_quantities,
    )
