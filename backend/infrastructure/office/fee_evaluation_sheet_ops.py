"""Small Excel sheet helpers for Fee Evaluation workbook writers."""

from __future__ import annotations

from typing import Any


WHITE_FILL = 0xFFFFFF
EXCEL_LINE_STYLE_NONE = -4142
EXCEL_LINE_STYLE_CONTINUOUS = 1
EXCEL_EDGE_LEFT = 7
EXCEL_EDGE_TOP = 8


def insert_rows(sheet: Any, row: int, count: int) -> None:
    if count <= 0:
        return
    if hasattr(sheet, "insert_rows"):
        sheet.insert_rows(row, count)
        return
    try:
        sheet.Rows(f"{row}:{row + count - 1}").Insert()
        return
    except Exception:
        pass
    try:
        sheet.Rows(row).Resize(count).Insert()
        return
    except Exception:
        pass
    for _ in range(count):
        sheet.Rows(row).Insert()


def set_a_column_fill(
    *,
    sheet: Any,
    start_row: int,
    end_row: int,
    color: int,
) -> None:
    if hasattr(sheet, "set_a_column_fill"):
        sheet.set_a_column_fill(start_row, end_row, color)
        return
    sheet.Range(sheet.Cells(start_row, 1), sheet.Cells(end_row, 1)).Interior.Color = color


def cell_fill_color(sheet: Any, row: int, column: int) -> int:
    return int(sheet.Cells(row, column).Interior.Color)


def set_cell_fill(*, sheet: Any, row_index: int, column: int, color: int) -> None:
    if hasattr(sheet, "set_cell_fill"):
        sheet.set_cell_fill(row_index, column, color)
        return
    sheet.Cells(row_index, column).Interior.Color = color


def clear_cell_fill(*, sheet: Any, row_index: int, column: int) -> None:
    if hasattr(sheet, "clear_cell_fill"):
        sheet.clear_cell_fill(row_index, column)
        return
    cell = sheet.Cells(row_index, column)
    if hasattr(cell.Interior, "ColorIndex"):
        cell.Interior.ColorIndex = EXCEL_LINE_STYLE_NONE
    else:
        cell.Interior.Color = WHITE_FILL


def set_a_column_bold(sheet: Any, start_row: int, end_row: int) -> None:
    if end_row < start_row:
        return
    if hasattr(sheet, "set_a_column_bold"):
        sheet.set_a_column_bold(start_row, end_row, True)
        return
    sheet.Range(sheet.Cells(start_row, 1), sheet.Cells(end_row, 1)).Font.Bold = True


def apply_a_column_group_borders(sheet: Any, start_row: int, end_row: int) -> None:
    if end_row < start_row:
        return
    if hasattr(sheet, "apply_a_column_group_borders"):
        sheet.apply_a_column_group_borders(start_row, end_row)
        return
    group_range = sheet.Range(sheet.Cells(start_row, 1), sheet.Cells(end_row, 1))
    group_range.Borders(EXCEL_EDGE_LEFT).LineStyle = EXCEL_LINE_STYLE_CONTINUOUS
    sheet.Cells(start_row, 1).Borders(EXCEL_EDGE_TOP).LineStyle = (
        EXCEL_LINE_STYLE_CONTINUOUS
    )


def set_row_values(
    sheet: Any,
    row_index: int,
    start_column: int,
    values: tuple[str | None, ...],
) -> None:
    """Write one row segment using one range assignment when available."""
    if hasattr(sheet, "set_row_values"):
        sheet.set_row_values(row_index, start_column, values)
        return
    end_column = start_column + len(values) - 1
    if len(values) == 1:
        sheet.Cells(row_index, start_column).Value = values[0]
        return
    sheet.Range(
        sheet.Cells(row_index, start_column),
        sheet.Cells(row_index, end_column),
    ).Value = (values,)


def set_block_values(
    sheet: Any,
    start_row: int,
    start_column: int,
    rows: tuple[tuple[str | None, ...], ...],
) -> None:
    """Write a rectangular cell block using one range assignment when possible."""
    if not rows:
        return
    if hasattr(sheet, "set_block_values"):
        sheet.set_block_values(start_row, start_column, rows)
        return
    end_row = start_row + len(rows) - 1
    end_column = start_column + len(rows[0]) - 1
    if len(rows) == 1:
        set_row_values(sheet, start_row, start_column, rows[0])
        return
    sheet.Range(
        sheet.Cells(start_row, start_column),
        sheet.Cells(end_row, end_column),
    ).Value = rows


def clear_cell_fill_range(
    *,
    sheet: Any,
    start_row: int,
    end_row: int,
    column: int,
) -> None:
    """Clear fill for one column across a contiguous row range."""
    if end_row < start_row:
        return
    if hasattr(sheet, "clear_cell_fill_range"):
        sheet.clear_cell_fill_range(start_row, end_row, column)
        return
    cell_range = sheet.Range(sheet.Cells(start_row, column), sheet.Cells(end_row, column))
    if hasattr(cell_range.Interior, "ColorIndex"):
        cell_range.Interior.ColorIndex = EXCEL_LINE_STYLE_NONE
        return
    cell_range.Interior.Color = WHITE_FILL


def set_formula_block(
    sheet: Any,
    start_row: int,
    column: int,
    formulas: tuple[str, ...],
) -> None:
    """Write one formula column across contiguous rows."""
    if not formulas:
        return
    if hasattr(sheet, "set_formula_block"):
        sheet.set_formula_block(start_row, column, formulas)
        return
    end_row = start_row + len(formulas) - 1
    if len(formulas) == 1:
        sheet.Cells(start_row, column).Formula = formulas[0]
        return
    sheet.Range(sheet.Cells(start_row, column), sheet.Cells(end_row, column)).Formula = tuple(
        (formula,) for formula in formulas
    )
