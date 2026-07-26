"""Render a Matrix Editor live snapshot to an in-memory XLSX workbook."""

from __future__ import annotations

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from backend.application.matrix_editor_live_xlsx_export_service import (
    MatrixEditorLiveXlsxExportProjection,
)


class MatrixEditorLiveXlsxWorkbookGateway:
    """Build the reference-shaped workbook without external templates."""

    def render(self, projection: MatrixEditorLiveXlsxExportProjection) -> bytes:
        """Return one macro-free workbook as bytes."""
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Sheet"
        headers = [
            "Test Item", "Section", "Test Method", "Condition", "Requirement",
            *(group.group_label for group in projection.groups), "Notes",
        ]
        sheet.append(headers)
        for column in range(6, 6 + len(projection.groups)):
            self._literalize(sheet.cell(1, column))
        for row in projection.rows:
            sheet.append([
                row.test_item, row.section, row.test_method, row.condition,
                row.requirement, *(cell.step_text for cell in row.cells), None,
            ])
            for column in range(1, 6 + len(projection.groups)):
                self._literalize(sheet.cell(sheet.max_row, column))
        for label, values in (
            ("Sample size", [group.sample_size or None for group in projection.groups]),
            ("Time", [group.time_display or None for group in projection.groups]),
            ("Fee", [None for _ in projection.groups]),
        ):
            sheet.append([label, None, None, None, None, *values, None])
            if label != "Fee":
                for column in range(6, 6 + len(projection.groups)):
                    self._literalize(sheet.cell(sheet.max_row, column))
        self._format(sheet)
        stream = BytesIO()
        workbook.save(stream)
        return stream.getvalue()

    @staticmethod
    def _literalize(cell) -> None:
        """Keep user-editable text from being interpreted as an Excel formula."""
        if isinstance(cell.value, str):
            cell.data_type = "s"

    @staticmethod
    def _format(sheet) -> None:
        gray = PatternFill("solid", fgColor="CCCCCC")
        thin = Side(style="thin", color="000000")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for row in sheet.iter_rows():
            for cell in row:
                cell.font = Font(name="Calibri", size=11)
                cell.alignment = alignment
                cell.border = border
            sheet.row_dimensions[row[0].row].height = 15
        for cell in sheet[1]:
            cell.fill = gray
        for row_number in range(2, sheet.max_row + 1):
            sheet.cell(row_number, 1).fill = gray
        sheet.column_dimensions["A"].width = 20
        sheet.column_dimensions["B"].width = 8
        sheet.column_dimensions["D"].width = 20
        sheet.column_dimensions["E"].width = 20
