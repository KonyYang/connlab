from __future__ import annotations

from backend.infrastructure.office import application_form_word_gateway as gateway


def test_body_value_readback_requires_exact_visible_value() -> None:
    assert gateway._body_value_matches("DL-2026-05-011", "DL-2026-05-011")
    assert not gateway._body_value_matches(
        "Lab Test Request Number: DL-2026-05-011",
        "DL-2026-05-011",
    )


def test_header_value_readback_allows_label_value_mix() -> None:
    assert gateway._header_value_matches(
        "Lab Test Request Number: DL-2026-05-011 Page",
        "DL-2026-05-011",
    )


def test_label_matching_is_exact_after_normalization() -> None:
    aliases = ("requested testing", "tests to be performed")

    assert gateway.label_matches_aliases("Tests to be Performed:", aliases)
    assert not gateway.label_matches_aliases(
        "Requested Testing Completion Date",
        aliases,
    )


def test_business_unit_location_fallback_is_limited_to_known_six_column_shape() -> None:
    table = _FakeTable(
        [
            ["Business Unit:", "Mobility", "", "Project #:", "DL-1", "Dongguan"],
        ],
    )

    result = gateway._find_location_in_business_unit_table(table, table_index=2)

    assert result is not None
    cell, label, address = result
    assert label == "Business Unit row site"
    assert address == "table[2].cell[1,6]"
    assert gateway._com_clean(cell.Range.Text) == "Dongguan"


def test_business_unit_location_fallback_rejects_unknown_table_shape() -> None:
    table = _FakeTable([["Business Unit:", "Mobility", "Dongguan"]])

    assert gateway._find_location_in_business_unit_table(table, table_index=1) is None


class _FakeCount:
    def __init__(self, count: int) -> None:
        self.Count = count


class _FakeRange:
    def __init__(self, text: str) -> None:
        self.Text = f"{text}\r\x07"


class _FakeCell:
    def __init__(self, text: str) -> None:
        self.Range = _FakeRange(text)


class _FakeTable:
    def __init__(self, rows: list[list[str]]) -> None:
        self._rows = rows
        self.Rows = _FakeCount(len(rows))
        self.Columns = _FakeCount(max((len(row) for row in rows), default=0))

    def Cell(self, row: int, column: int) -> _FakeCell:
        return _FakeCell(self._rows[row - 1][column - 1])
