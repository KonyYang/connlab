"""Macro-free openpyxl workbook writer for LLCR/CR specialized records."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordProjection,
    LlcrCrRecordSection,
)

LLCR_CR_RECORD_LAYOUT_V1 = {
    "summary_sheet": "Record Summary",
    "llcr_sheet": "LLCR Record",
    "cr_sheet": "CR Record",
    "record_headers": (
        "Type",
        "Group",
        "Source Step",
        "Sample",
        "Contact ID",
        "Contact Label",
        "Initial",
        "After",
        "Final",
        "Result",
        "Remarks",
    ),
}


class LlcrCrSpecializedRecordWorkbookGateway:
    """Write one fresh macro-free `.xlsx` workbook from a ready projection."""

    def write(self, *, output_path: Path, projection: LlcrCrRecordProjection) -> Path:
        """Create the fixed workbook layout without mutating source authority."""
        target = Path(output_path)
        if target.suffix.lower() != ".xlsx":
            raise ValueError("LLCR/CR specialized record output must be .xlsx.")
        if projection.status != "ready":
            raise ValueError("A ready LLCR/CR record preview is required for generation.")
        if not target.parent.is_dir():
            raise FileNotFoundError(f"Output directory does not exist: {target.parent}")

        workbook = Workbook()
        workbook.remove(workbook.active)
        summary = workbook.create_sheet(LLCR_CR_RECORD_LAYOUT_V1["summary_sheet"])
        llcr = workbook.create_sheet(LLCR_CR_RECORD_LAYOUT_V1["llcr_sheet"])
        cr = workbook.create_sheet(LLCR_CR_RECORD_LAYOUT_V1["cr_sheet"])
        _write_summary(summary, projection)
        _write_record_sheet(llcr, tuple(section for section in projection.sections if section.record_type == "llcr"))
        _write_record_sheet(cr, tuple(section for section in projection.sections if section.record_type == "cr_specified_current"))
        workbook.save(target)
        return target


def _write_summary(sheet, projection: LlcrCrRecordProjection) -> None:
    sheet["A1"] = "LLCR/CR Specialized Record Workbook"
    sheet["A3"] = "Project ID"
    sheet["B3"] = projection.project_id
    sheet["A4"] = "Confirmed Matrix"
    sheet["B4"] = projection.confirmed_matrix_id
    sheet["A5"] = "Confirmed revision"
    sheet["B5"] = projection.confirmed_revision
    sheet["A6"] = "Generated rows"
    sheet["B6"] = projection.row_count
    headers = (
        "Type",
        "Group",
        "Source Step",
        "Samples",
        "Readings / sample",
        "Generated rows",
        "Status",
    )
    _write_header_row(sheet, 8, headers)
    for index, section in enumerate(projection.sections, start=9):
        sheet.cell(index, 1, _display_type(section.record_type))
        sheet.cell(index, 2, section.group_label)
        sheet.cell(index, 3, section.source_step)
        sheet.cell(index, 4, section.sample_count)
        sheet.cell(index, 5, section.readings_per_sample)
        sheet.cell(index, 6, len(section.rows))
        sheet.cell(index, 7, "Ready")
    _set_column_widths(sheet, (18, 24, 18, 12, 18, 16, 14))


def _write_record_sheet(sheet, sections: tuple[LlcrCrRecordSection, ...]) -> None:
    row_index = 1
    for section in sections:
        sheet.merge_cells(start_row=row_index, start_column=1, end_row=row_index, end_column=11)
        sheet.cell(row_index, 1, f"{_display_type(section.record_type)} | {section.group_label} | Step {section.source_step}")
        sheet.cell(row_index, 1).font = Font(bold=True)
        sheet.cell(row_index, 1).fill = PatternFill("solid", fgColor="D8E0EA")
        sheet.cell(row_index + 1, 1, "Samples")
        sheet.cell(row_index + 1, 2, section.sample_count)
        sheet.cell(row_index + 1, 3, "Readings / sample")
        sheet.cell(row_index + 1, 4, section.readings_per_sample)
        header_row = row_index + 2
        _write_header_row(sheet, header_row, LLCR_CR_RECORD_LAYOUT_V1["record_headers"])
        first_row = header_row + 1
        for offset, record in enumerate(section.rows):
            current = first_row + offset
            sheet.cell(current, 1, _display_type(section.record_type))
            sheet.cell(current, 2, section.group_label)
            sheet.cell(current, 3, section.source_step)
            sheet.cell(current, 4, record.sample_index)
            sheet.cell(current, 5, record.contact_id)
            sheet.cell(current, 6, record.contact_label)
        last_row = first_row + len(section.rows) - 1
        summary_row = last_row + 1
        sheet.cell(summary_row, 6, "Statistics")
        sheet.cell(summary_row, 7, _average_formula("G", first_row, last_row))
        sheet.cell(summary_row, 8, _average_formula("H", first_row, last_row))
        sheet.cell(summary_row, 9, _average_formula("I", first_row, last_row))
        sheet.cell(summary_row, 10, _result_formula(first_row, last_row))
        row_index = summary_row + 2
    _set_column_widths(sheet, (14, 22, 16, 10, 16, 24, 14, 14, 14, 16, 28))


def _write_header_row(sheet, row: int, headers: tuple[str, ...]) -> None:
    for column, value in enumerate(headers, start=1):
        cell = sheet.cell(row, column, value)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="E8EEF6")
        cell.alignment = Alignment(horizontal="center")


def _set_column_widths(sheet, widths: tuple[int, ...]) -> None:
    for index, width in enumerate(widths, start=1):
        sheet.column_dimensions[chr(64 + index)].width = width


def _average_formula(column: str, first_row: int, last_row: int) -> str:
    return f'=IF(COUNT({column}{first_row}:{column}{last_row})=0,"",AVERAGE({column}{first_row}:{column}{last_row}))'


def _result_formula(first_row: int, last_row: int) -> str:
    return f'=IF(COUNTA(J{first_row}:J{last_row})=0,"",COUNTIF(J{first_row}:J{last_row},"PASS")&"/"&COUNTA(J{first_row}:J{last_row}))'


def _display_type(record_type: str) -> str:
    return "CR" if record_type == "cr_specified_current" else "LLCR"
