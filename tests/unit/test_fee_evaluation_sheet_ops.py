from __future__ import annotations

from backend.infrastructure.office.fee_evaluation_sheet_ops import insert_rows


def test_insert_rows_uses_resize_fallback_before_single_row_loop() -> None:
    rows = _RowsWithResizeFallback()
    sheet = _Sheet(rows)

    insert_rows(sheet, 5, 4)

    assert rows.calls == ["5:8", 5]
    assert rows.resize_inserts == [4]
    assert rows.single_row_inserts == 0


class _Sheet:
    def __init__(self, rows: "_RowsWithResizeFallback") -> None:
        self.Rows = rows


class _RowsWithResizeFallback:
    def __init__(self) -> None:
        self.calls: list[int | str] = []
        self.resize_inserts: list[int] = []
        self.single_row_inserts = 0

    def __call__(self, row: int | str) -> "_RowSelection | _RangeSelection":
        self.calls.append(row)
        if isinstance(row, str):
            return _RangeSelection(should_fail=True)
        return _RowSelection(self)


class _RangeSelection:
    def __init__(self, *, should_fail: bool = False) -> None:
        self._should_fail = should_fail

    def Insert(self) -> None:
        if self._should_fail:
            raise RuntimeError("range insert failed")


class _RowSelection:
    def __init__(self, rows: _RowsWithResizeFallback) -> None:
        self._rows = rows

    def Resize(self, count: int) -> "_ResizedRows":
        return _ResizedRows(self._rows, count)

    def Insert(self) -> None:
        self._rows.single_row_inserts += 1


class _ResizedRows:
    def __init__(self, rows: _RowsWithResizeFallback, count: int) -> None:
        self._rows = rows
        self._count = count

    def Insert(self) -> None:
        self._rows.resize_inserts.append(self._count)
