from __future__ import annotations

from backend.infrastructure.office.application_form_word_targets import (
    ApplicationFormWordTargetIndex,
)


def test_target_index_scans_body_tables_once_for_multiple_fields() -> None:
    table = _CountingTable(
        [
            ["Lab Performing the Tests", "Dongguan", ""],
            ["Lab Personnel Assigned", "Even Yang", ""],
        ],
    )
    document = _FakeDocument([table])

    index = ApplicationFormWordTargetIndex.build(
        document,
        field_keys={"lab", "project_leader"},
    )

    assert index.target_for("lab") is not None
    assert index.target_for("project_leader") is not None
    assert table.cell_call_count <= 8

    index.target_for("lab")
    index.target_for("project_leader")

    assert table.cell_call_count <= 8


def test_target_index_applies_location_fallback_once_for_known_business_unit_shape() -> None:
    table = _CountingTable(
        [["Business Unit:", "Mobility", "", "Project #:", "DL-1", "Dongguan"]],
    )
    document = _FakeDocument([table])

    index = ApplicationFormWordTargetIndex.build(document, field_keys={"location"})
    target = index.target_for("location")

    assert target is not None
    assert target.label == "Business Unit row site"
    assert target.location == "table[1].cell[1,6]"
    assert target.visible_text() == "Dongguan"
    assert table.cell_call_count == 12

    index.target_for("location")

    assert table.cell_call_count == 12


class _FakeCount:
    def __init__(self, count: int) -> None:
        self.Count = count


class _FakeCollection:
    def __init__(self, items: list[object]) -> None:
        self._items = items
        self.Count = len(items)

    def Item(self, index: int) -> object:
        return self._items[index - 1]


class _FakeRange:
    def __init__(self, text: str) -> None:
        self.Text = f"{text}\r\x07"


class _FakeCell:
    def __init__(self, text: str) -> None:
        self.Range = _FakeRange(text)


class _CountingTable:
    def __init__(self, rows: list[list[str]]) -> None:
        self._rows = rows
        self.Rows = _FakeCount(len(rows))
        self.Columns = _FakeCount(max((len(row) for row in rows), default=0))
        self.cell_call_count = 0

    def Cell(self, row: int, column: int) -> _FakeCell:
        self.cell_call_count += 1
        return _FakeCell(self._rows[row - 1][column - 1])


class _FakeDocument:
    def __init__(self, tables: list[_CountingTable]) -> None:
        self.Tables = _FakeCollection(tables)
