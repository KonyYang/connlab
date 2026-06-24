"""Cached worksheet anchors for Fee Evaluation workbook writers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class FeeEvaluationAnchorSnapshot:
    """Cached values/formulas from a bounded Fee Form worksheet region."""

    start_row: int
    start_column: int
    values: tuple[tuple[str, ...], ...]
    formulas: tuple[tuple[str, ...], ...]

    @classmethod
    def from_sheet(
        cls,
        sheet: Any,
        *,
        max_row: int = 200,
        max_column: int = 9,
    ) -> "FeeEvaluationAnchorSnapshot":
        """Read the anchor scan region once from Excel."""
        value_range = sheet.Range(sheet.Cells(1, 1), sheet.Cells(max_row, max_column))
        values = _normalize_2d(value_range.Value, max_row, max_column)
        formulas = _normalize_2d(getattr(value_range, "Formula", None), max_row, max_column)
        if not any(any(cell for cell in row) for row in formulas):
            formulas = values
        return cls(start_row=1, start_column=1, values=values, formulas=formulas)

    def cell_value(self, row: int, column: int) -> str:
        """Return cached display value for a 1-based worksheet cell."""
        return self._cell(self.values, row, column)

    def cell_formula(self, row: int, column: int) -> str:
        """Return cached formula text for a 1-based worksheet cell."""
        return self._cell(self.formulas, row, column)

    def find_required_row(self, text: str) -> int:
        """Return the row containing an exact normalized label."""
        row = self.find_optional_row(text)
        if row is None:
            raise ValueError(f"Testing Prices anchor was not found: {text}")
        return row

    def find_optional_row(self, text: str) -> int | None:
        """Return the row containing an exact normalized label when present."""
        target = _normalize_label(text)
        for row_index, row_values in enumerate(self.values, start=self.start_row):
            for value in row_values:
                if _normalize_label(value) == target:
                    return row_index
        return None

    def find_identity_target(
        self,
        aliases: tuple[str, ...],
        *,
        max_row: int,
    ) -> tuple[int, int] | None:
        """Return the cell immediately right of a matching identity label."""
        normalized_aliases = {_normalize_label(alias) for alias in aliases}
        for row_index, row_values in enumerate(self.values, start=self.start_row):
            if row_index > max_row:
                break
            for offset, value in enumerate(row_values):
                if _normalize_label(value) in normalized_aliases:
                    return row_index, self.start_column + offset + 1
        return None

    def _cell(
        self,
        matrix: tuple[tuple[str, ...], ...],
        row: int,
        column: int,
    ) -> str:
        row_index = row - self.start_row
        column_index = column - self.start_column
        if row_index < 0 or column_index < 0:
            return ""
        if row_index >= len(matrix):
            return ""
        if column_index >= len(matrix[row_index]):
            return ""
        return matrix[row_index][column_index]


def _normalize_2d(value: Any, rows: int, columns: int) -> tuple[tuple[str, ...], ...]:
    """Normalize COM range values into a fixed 2D string matrix."""
    if value is None:
        return tuple(tuple("" for _ in range(columns)) for _ in range(rows))
    if not isinstance(value, tuple):
        return ((str(value),),)
    if value and not isinstance(value[0], tuple):
        return (tuple(_text(cell) for cell in value),)
    return tuple(tuple(_text(cell) for cell in row) for row in value)


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _normalize_label(value: str) -> str:
    return " ".join(value.replace(":", " ").split()).strip().lower()
