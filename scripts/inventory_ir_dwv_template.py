"""Emit a deterministic JSON inventory for the IR/DWV workbook template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _cell_inventory(cell: Any) -> dict[str, Any]:
    return {
        "coordinate": cell.coordinate,
        "value": _json_value(cell.value),
        "data_type": cell.data_type,
        "style_id": cell.style_id,
        "number_format": cell.number_format,
    }


def _conditional_formatting(sheet: Any) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for item in sheet.conditional_formatting:
        entries.append(
            {
                "sqref": str(item.sqref),
                "rules": [
                    {
                        "type": rule.type,
                        "priority": rule.priority,
                        "operator": rule.operator,
                        "formula": list(rule.formula or ()),
                        "stop_if_true": rule.stopIfTrue,
                    }
                    for rule in item.rules
                ],
            }
        )
    return entries


def _data_validations(sheet: Any) -> list[dict[str, Any]]:
    return [
        {
            "sqref": str(validation.sqref),
            "type": validation.type,
            "operator": validation.operator,
            "formula1": validation.formula1,
            "formula2": validation.formula2,
            "allow_blank": validation.allowBlank,
            "show_error_message": validation.showErrorMessage,
            "show_input_message": validation.showInputMessage,
        }
        for validation in sheet.data_validations.dataValidation
    ]


def inventory_workbook(path: Path) -> dict[str, Any]:
    workbook = load_workbook(path, data_only=False)
    try:
        sheets = []
        for sheet in workbook.worksheets:
            cells = [
                _cell_inventory(sheet.cell(row=row, column=column))
                for row in range(1, sheet.max_row + 1)
                for column in range(1, sheet.max_column + 1)
            ]
            sheets.append(
                {
                    "title": sheet.title,
                    "state": sheet.sheet_state,
                    "max_row": sheet.max_row,
                    "max_column": sheet.max_column,
                    "cells": cells,
                    "formulas": [
                        {"coordinate": cell["coordinate"], "formula": cell["value"]}
                        for cell in cells
                        if isinstance(cell["value"], str) and cell["value"].startswith("=")
                    ],
                    "merged_cells": sorted(str(item) for item in sheet.merged_cells.ranges),
                    "row_heights": {
                        str(index): dimension.height
                        for index, dimension in sheet.row_dimensions.items()
                        if dimension.height is not None
                    },
                    "column_widths": {
                        label: dimension.width
                        for label, dimension in sheet.column_dimensions.items()
                        if dimension.width is not None
                    },
                    "conditional_formatting": _conditional_formatting(sheet),
                    "data_validations": _data_validations(sheet),
                    "print": {
                        "print_area": str(sheet.print_area or ""),
                        "print_title_rows": sheet.print_title_rows,
                        "print_title_cols": sheet.print_title_cols,
                        "freeze_panes": str(sheet.freeze_panes or ""),
                        "sheet_view_show_grid_lines": sheet.sheet_view.showGridLines,
                        "page_setup": {
                            "orientation": sheet.page_setup.orientation,
                            "paper_size": sheet.page_setup.paperSize,
                            "fit_to_width": sheet.page_setup.fitToWidth,
                            "fit_to_height": sheet.page_setup.fitToHeight,
                            "scale": sheet.page_setup.scale,
                        },
                        "page_margins": {
                            "left": sheet.page_margins.left,
                            "right": sheet.page_margins.right,
                            "top": sheet.page_margins.top,
                            "bottom": sheet.page_margins.bottom,
                            "header": sheet.page_margins.header,
                            "footer": sheet.page_margins.footer,
                        },
                        "print_options": {
                            "horizontal_centered": sheet.print_options.horizontalCentered,
                            "vertical_centered": sheet.print_options.verticalCentered,
                            "headings": sheet.print_options.headings,
                            "grid_lines": sheet.print_options.gridLines,
                        },
                    },
                }
            )
        return {
            "schema": "connlab.ir-dwv-template-inventory",
            "version": 1,
            "workbook": {
                "sheet_names": workbook.sheetnames,
                "calculation_mode": workbook.calculation.calcMode,
                "full_calc_on_load": workbook.calculation.fullCalcOnLoad,
                "force_full_calc": workbook.calculation.forceFullCalc,
            },
            "sheets": sheets,
        }
    finally:
        workbook.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(
        inventory_workbook(args.workbook), ensure_ascii=False, indent=2, sort_keys=True
    )
    if args.output is None:
        print(payload)
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
