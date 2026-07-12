"""Shared fixed sheet layout for confirmed and draft LLCR/CR workbooks."""

from __future__ import annotations

from openpyxl.styles import Alignment, Font, PatternFill

LLCR_CR_RECORD_LAYOUT_V1 = {
    "summary_sheet": "Record Summary",
    "llcr_sheet": "LLCR Record",
    "cr_sheet": "CR Record",
    "record_headers": (
        "Type", "Group", "Source Step", "Sample", "Contact ID", "Contact Label",
        "Initial", "After", "Final", "Result", "Remarks",
    ),
}


def write_record_sheet(sheet, sections, *, banner: str | None = None) -> None:
    """Write fixed Group-Step blocks, manual cells, formulas, and widths."""
    row_index = 1
    if banner:
        sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=11)
        sheet.cell(1, 1, banner)
        sheet.cell(1, 1).font = Font(bold=True, size=14)
        sheet.cell(1, 1).fill = PatternFill("solid", fgColor="E8EEF6")
        row_index = 3
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
        write_header_row(sheet, header_row, LLCR_CR_RECORD_LAYOUT_V1["record_headers"])
        first_row = header_row + 1
        for offset, record in enumerate(section.rows):
            current = first_row + offset
            values = (_display_type(section.record_type), section.group_label, section.source_step, record.sample_index, record.contact_id, record.contact_label)
            for column, value in enumerate(values, start=1):
                sheet.cell(current, column, value)
        last_row = first_row + len(section.rows) - 1
        summary_row = last_row + 1
        sheet.cell(summary_row, 6, "Statistics")
        sheet.cell(summary_row, 7, _average_formula("G", first_row, last_row))
        sheet.cell(summary_row, 8, _average_formula("H", first_row, last_row))
        sheet.cell(summary_row, 9, _average_formula("I", first_row, last_row))
        sheet.cell(summary_row, 10, _result_formula(first_row, last_row))
        row_index = summary_row + 2
    set_column_widths(sheet, (14, 22, 16, 10, 16, 24, 14, 14, 14, 16, 28))


def write_header_row(sheet, row: int, headers: tuple[str, ...]) -> None:
    for column, value in enumerate(headers, start=1):
        cell = sheet.cell(row, column, value)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="E8EEF6")
        cell.alignment = Alignment(horizontal="center")


def set_column_widths(sheet, widths: tuple[int, ...]) -> None:
    for index, width in enumerate(widths, start=1):
        sheet.column_dimensions[chr(64 + index)].width = width


def _average_formula(column: str, first_row: int, last_row: int) -> str:
    return f'=IF(COUNT({column}{first_row}:{column}{last_row})=0,"",AVERAGE({column}{first_row}:{column}{last_row}))'


def _result_formula(first_row: int, last_row: int) -> str:
    return f'=IF(COUNTA(J{first_row}:J{last_row})=0,"",COUNTIF(J{first_row}:J{last_row},"PASS")&"/"&COUNTA(J{first_row}:J{last_row}))'


def _display_type(record_type: str) -> str:
    return "CR" if record_type == "cr_specified_current" else "LLCR"
