"""Build the shared Matrix-to-Test-Status workbook projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from backend.domain import ConfirmedMatrixSnapshot


@dataclass(frozen=True, slots=True)
class TestStatusGroup:
    """One selected Matrix group represented as one Test Status column."""

    __test__ = False
    group_key: str
    group_label: str
    sample_quantity_expression: str


@dataclass(frozen=True, slots=True)
class TestStatusRow:
    """One Matrix test item and its unmodified per-group step expressions."""

    __test__ = False
    test_item: str
    group_values: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class TestStatusProjection:
    """Workbook-ready Test Status data shared by draft and authority outputs."""

    __test__ = False
    groups: tuple[TestStatusGroup, ...]
    rows: tuple[TestStatusRow, ...]


def build_test_status_projection(
    *,
    groups: tuple[TestStatusGroup, ...],
    rows: tuple[TestStatusRow, ...],
) -> TestStatusProjection:
    """Normalize current Matrix grid data without interpreting its cell expressions."""
    normalized_groups = tuple(
        TestStatusGroup(
            group_key=group.group_key.strip(),
            group_label=group.group_label.strip(),
            sample_quantity_expression=group.sample_quantity_expression.strip(),
        )
        for group in groups
    )
    if not normalized_groups:
        raise ValueError("Test Status requires at least one selected Matrix group.")
    keys = [group.group_key for group in normalized_groups]
    if any(not key for key in keys):
        raise ValueError("Test Status group keys must not be blank.")
    if len(keys) != len(set(keys)):
        raise ValueError("Test Status group keys must be unique.")

    normalized_rows = tuple(
        TestStatusRow(
            test_item=row.test_item.strip(),
            group_values={
                group.group_key: str(row.group_values.get(group.group_key, "") or "").strip()
                for group in normalized_groups
            },
        )
        for row in rows
        if row.test_item.strip()
    )
    if not normalized_rows:
        raise ValueError("Test Status requires at least one Matrix test item.")
    return TestStatusProjection(
        groups=normalized_groups,
        rows=normalized_rows,
    )


def build_confirmed_test_status_projection(
    snapshot: ConfirmedMatrixSnapshot,
) -> TestStatusProjection:
    """Project one immutable confirmed Matrix snapshot into Test Status grid data."""
    groups = tuple(
        TestStatusGroup(
            group_key=group.group_key,
            group_label=group.group_label,
            sample_quantity_expression=group.sample_quantity_expression,
        )
        for group in sorted(snapshot.groups, key=lambda item: item.group_order)
    )
    group_keys_by_id = {
        group.confirmed_group_id: group.group_key.strip() for group in snapshot.groups
    }
    rows_by_id = {row.confirmed_row_id: row for row in snapshot.rows}
    values: dict[tuple[str, str], str] = {}
    for cell in snapshot.cells:
        group_key = group_keys_by_id.get(cell.confirmed_group_id)
        if group_key is None or cell.confirmed_row_id not in rows_by_id:
            raise ValueError("Confirmed Matrix cell lineage is invalid for Test Status.")
        values[(cell.confirmed_row_id, group_key)] = cell.cell_value
    rows = tuple(
        TestStatusRow(
            test_item=row.test_item,
            group_values={
                group.group_key.strip(): values.get(
                    (row.confirmed_row_id, group.group_key.strip()), ""
                )
                for group in groups
            },
        )
        for row in sorted(snapshot.rows, key=lambda item: item.row_order)
    )
    return build_test_status_projection(
        groups=groups,
        rows=rows,
    )
