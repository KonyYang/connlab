from __future__ import annotations

import pytest

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    BuildMatrixBasicFeeTemplateCommand,
    ConfirmedMatrixFeeTemplateBasicFillNotFoundError,
    ConfirmedMatrixFeeTemplateBasicFillService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)


def test_basic_fill_expands_confirmed_matrix_step_tokens_in_preview_order() -> None:
    service = ConfirmedMatrixFeeTemplateBasicFillService(
        confirmed_store=_Store(_snapshot_with_malformed_cells())
    )

    result = service.build(
        BuildMatrixBasicFeeTemplateCommand(project_id="P1")
    )

    assert result.header.project_id == "P1"
    assert result.header.confirmed_matrix_id == "cmv-1"
    assert [group.group_label for group in result.groups] == ["Group A", "Group B"]
    assert [line.test_item for line in result.groups[0].lines] == [
        "Visual Examination",
        "LLCR",
        "Visual Examination",
        "Dust Test",
    ]
    assert [line.step_tokens for line in result.groups[0].lines] == [
        ("1",),
        ("2",),
        ("3",),
        (),
    ]
    assert [line.cell_value for line in result.groups[0].lines] == [
        "1 3 X",
        "2",
        "1 3 X",
        "abc",
    ]
    assert [line.test_item for line in result.groups[1].lines] == ["Visual Examination"]
    assert result.groups[1].lines[0].step_tokens == ("1",)


def test_basic_fill_skips_empty_confirmed_matrix_cells() -> None:
    service = ConfirmedMatrixFeeTemplateBasicFillService(
        confirmed_store=_Store(_snapshot_with_empty_only_cell())
    )

    result = service.build(BuildMatrixBasicFeeTemplateCommand(project_id="P1"))

    assert result.status == "empty"
    assert result.groups == ()


def test_basic_fill_raises_when_active_confirmed_matrix_is_missing() -> None:
    service = ConfirmedMatrixFeeTemplateBasicFillService(confirmed_store=_Store(None))

    with pytest.raises(
        ConfirmedMatrixFeeTemplateBasicFillNotFoundError,
        match="Active confirmed matrix",
    ):
        service.build(BuildMatrixBasicFeeTemplateCommand(project_id="P1"))


def _snapshot_with_malformed_cells() -> ConfirmedMatrixSnapshot:
    rows = (
        _row("cmr-visual", 1, "Visual Examination"),
        _row("cmr-llcr", 2, "LLCR"),
        _row("cmr-dust", 3, "Dust Test"),
    )
    groups = (
        _group("cmg-a", 1, "g-a", "Group A"),
        _group("cmg-b", 2, "g-b", "Group B"),
    )
    return _snapshot(
        groups=groups,
        rows=rows,
        cells=(
            _cell("cmc-a1", groups[0], rows[0], "1 3 X"),
            _cell("cmc-a2", groups[0], rows[1], "2"),
            _cell("cmc-a3", groups[0], rows[2], "abc"),
            _cell("cmc-b1", groups[1], rows[0], "1"),
        ),
    )


def _snapshot_with_empty_only_cell() -> ConfirmedMatrixSnapshot:
    row = _row("cmr-visual", 1, "Visual Examination")
    group = _group("cmg-a", 1, "g-a", "Group A")
    return _snapshot(
        groups=(group,),
        rows=(row,),
        cells=(_cell("cmc-a1", group, row, " "),),
    )


def _snapshot(
    *,
    groups: tuple[ConfirmedMatrixGroup, ...],
    rows: tuple[ConfirmedMatrixRow, ...],
    cells: tuple[ConfirmedMatrixCell, ...],
) -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="cmv-1",
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-06-05T10:00:00+08:00",
            sample_received_date="2026-06-03",
        ),
        groups=groups,
        rows=rows,
        cells=cells,
    )


def _group(
    confirmed_group_id: str,
    group_order: int,
    group_key: str,
    group_label: str,
) -> ConfirmedMatrixGroup:
    return ConfirmedMatrixGroup(
        confirmed_group_id=confirmed_group_id,
        confirmed_matrix_id="cmv-1",
        draft_group_id=f"draft-{confirmed_group_id}",
        source_group_snapshot_id=f"source-{confirmed_group_id}",
        group_order=group_order,
        group_key=group_key,
        group_label=group_label,
        sample_quantity_expression="3",
    )


def _row(confirmed_row_id: str, row_order: int, test_item: str) -> ConfirmedMatrixRow:
    return ConfirmedMatrixRow(
        confirmed_row_id=confirmed_row_id,
        confirmed_matrix_id="cmv-1",
        draft_row_id=f"draft-{confirmed_row_id}",
        source_row_snapshot_id=f"source-{confirmed_row_id}",
        row_order=row_order,
        test_item=test_item,
    )


def _cell(
    confirmed_cell_id: str,
    group: ConfirmedMatrixGroup,
    row: ConfirmedMatrixRow,
    cell_value: str,
) -> ConfirmedMatrixCell:
    return ConfirmedMatrixCell(
        confirmed_cell_id=confirmed_cell_id,
        confirmed_matrix_id="cmv-1",
        confirmed_group_id=group.confirmed_group_id,
        confirmed_row_id=row.confirmed_row_id,
        draft_group_id=group.draft_group_id,
        draft_row_id=row.draft_row_id,
        cell_value=cell_value,
    )


class _Store:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot | None) -> None:
        self.snapshot = snapshot
        self.project_ids: list[str] = []

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        self.project_ids.append(project_id)
        return self.snapshot
