"""Shared fixed sheet layout for confirmed and draft LLCR/CR workbooks."""

from __future__ import annotations

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

LLCR_CR_RECORD_LAYOUT_V1 = {
    "summary_sheet": "Record Summary",
    "llcr_sheet": "LLCR Record",
    "cr_sheet": "CR Record",
    "record_headers": (
        "Type", "Group", "Source Step", "Sample", "Contact ID", "Contact Label",
        "Initial", "After", "Final", "Result", "Remarks",
    ),
}

LLCR_CR_RECORD_LAYOUT_V2 = {
    "summary_sheet": "Record Summary",
    "summary_headers": (
        "Type", "Point category", "Group", "Samples", "Points / sample",
        "Stages", "Generated rows",
    ),
}

_BORDER = Border(
    left=Side(style="thin", color="B8C2CE"),
    right=Side(style="thin", color="B8C2CE"),
    top=Side(style="thin", color="B8C2CE"),
    bottom=Side(style="thin", color="B8C2CE"),
)


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


def write_specialized_category_sheet(
    sheet,
    sections,
    *,
    record_type: str,
    delta_r_enabled: bool,
) -> None:
    """Write one point-category sheet with one shared correction input set."""
    sections = tuple(sections)
    if not sections:
        return
    first = sections[0]
    points = []
    seen = set()
    for row in first.rows:
        if row.contact_id not in seen:
            seen.add(row.contact_id)
            points.append(row.contact_id)

    max_columns = max(
        10,
        max(
            3 + sum(
                _stage_width(record_type, delta_r_enabled, stage_index)
                for stage_index, _stage in enumerate(section.stages)
            )
            for section in sections
        ),
    )
    sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max_columns)
    sheet.cell(1, 1, f"{record_type.upper()} Test Record · {first.category_label or first.record_prefix or 'Points'}")
    sheet.cell(1, 1).font = Font(bold=True, size=16, color="17324D")
    sheet.cell(3, 1, "Point category")
    sheet.cell(3, 2, first.category_label or "")
    sheet.cell(4, 1, "Point prefix")
    sheet.cell(4, 2, first.record_prefix or "")
    sheet.cell(5, 1, "Point range")
    sheet.cell(5, 2, first.point_expression or "")
    sheet.cell(6, 1, "Correction")
    sheet.cell(6, 2, "Bulk Resistance" if record_type == "llcr" else "Bulk Voltage")
    write_header_row(
        sheet,
        8,
        ("Point ID", "Bulk Resistance (mΩ)" if record_type == "llcr" else "Bulk Voltage (mV)"),
    )
    for offset, point_id in enumerate(points, start=9):
        sheet.cell(offset, 1, point_id)
        sheet.cell(offset, 2, None)
        _apply_row_border(sheet, offset, 1, 2)
    bulk_first = 9
    bulk_last = 8 + len(points)
    next_row = bulk_last + 3
    for section in sections:
        next_row = _write_group_block(
            sheet,
            section,
            start_row=next_row,
            bulk_first=bulk_first,
            bulk_last=bulk_last,
            record_type=record_type,
            delta_r_enabled=delta_r_enabled,
        )
    sheet.freeze_panes = "D9"
    sheet.column_dimensions["A"].width = 14
    sheet.column_dimensions["B"].width = 18
    sheet.column_dimensions["C"].width = 22
    for column in range(4, max_columns + 1):
        sheet.column_dimensions[get_column_letter(column)].width = 18


def _write_group_block(
    sheet,
    section,
    *,
    start_row: int,
    bulk_first: int,
    bulk_last: int,
    record_type: str,
    delta_r_enabled: bool,
) -> int:
    last_column = max(
        10,
        3 + sum(
            _stage_width(record_type, delta_r_enabled, stage_index)
            for stage_index, _stage in enumerate(section.stages)
        ),
    )
    sheet.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=last_column)
    sheet.cell(start_row, 1, f"{section.group_label} · {section.sample_count} samples")
    sheet.cell(start_row, 1).font = Font(bold=True, color="FFFFFF")
    sheet.cell(start_row, 1).fill = PatternFill("solid", fgColor="3B5B7A")
    environment_row = start_row + 1
    for column, label in ((1, "Date"), (3, "Temperature (°C)"), (5, "RH (%)"), (7, "Tester"), (9, "Equipment")):
        sheet.cell(environment_row, column, label).font = Font(bold=True)
        sheet.cell(environment_row, column + 1, None)

    heading_row = start_row + 2
    current_row = heading_row + 1 if record_type == "cr" else None
    subheader_row = heading_row + (2 if record_type == "cr" else 1)
    data_start = subheader_row + 1
    write_header_row(sheet, subheader_row, ("Sample", "Point ID", "Point category"))
    corrected_columns: list[int] = []
    delta_columns: list[int] = []
    initial_corrected_column: int | None = None
    column = 4
    for stage_index, stage in enumerate(section.stages):
        stage_width = _stage_width(record_type, delta_r_enabled, stage_index)
        end_column = column + stage_width - 1
        sheet.merge_cells(
            start_row=heading_row, start_column=column,
            end_row=heading_row, end_column=end_column,
        )
        heading = sheet.cell(heading_row, column, f"{stage.label} · Step {stage.source_step}")
        heading.font = Font(bold=True)
        heading.fill = PatternFill("solid", fgColor="D8E6F3")
        heading.alignment = Alignment(horizontal="center")
        if record_type == "cr":
            assert current_row is not None
            sheet.cell(current_row, column, "Test current (A)").font = Font(bold=True)
            sheet.cell(current_row, column + 1, _number(stage.test_current_ampere))
            headers = ("Raw voltage (mV)", "Corrected (mΩ)")
        else:
            headers = (
                "Raw resistance (mΩ)",
                "Corrected (mΩ)",
                "ΔR (mΩ)",
            ) if delta_r_enabled and stage_index > 0 else (
                "Raw resistance (mΩ)", "Corrected (mΩ)"
            )
        for offset, value in enumerate(headers):
            cell = sheet.cell(subheader_row, column + offset, value)
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="E8EEF6")
            cell.alignment = Alignment(horizontal="center", wrap_text=True)
        corrected_column = column + 1
        corrected_columns.append(corrected_column)
        if initial_corrected_column is None:
            initial_corrected_column = corrected_column
        if record_type == "llcr" and delta_r_enabled and stage_index > 0:
            delta_columns.append(column + 2)
        column = end_column + 1

    bulk_range = f"$A${bulk_first}:$B${bulk_last}"
    for offset, record in enumerate(section.rows):
        row = data_start + offset
        sheet.cell(row, 1, record.sample_index)
        sheet.cell(row, 2, record.contact_id)
        sheet.cell(row, 3, record.contact_label)
        column = 4
        for stage_index, _stage in enumerate(section.stages):
            stage_width = _stage_width(record_type, delta_r_enabled, stage_index)
            raw = f"{get_column_letter(column)}{row}"
            corrected_column = column + 1
            corrected = f"{get_column_letter(corrected_column)}{row}"
            correction_present = (
                f'COUNTIFS($A${bulk_first}:$A${bulk_last},$B{row},'
                f'$B${bulk_first}:$B${bulk_last},"<>")>0'
            )
            if record_type == "llcr":
                sheet.cell(
                    row,
                    corrected_column,
                    f'=IF(OR({raw}="",NOT({correction_present})),"",{raw}-VLOOKUP($B{row},{bulk_range},2,FALSE))',
                )
                if delta_r_enabled and stage_index > 0 and initial_corrected_column is not None:
                    initial = f"{get_column_letter(initial_corrected_column)}{row}"
                    sheet.cell(
                        row,
                        column + 2,
                        f'=IF(OR({corrected}="",{initial}=""),"",{corrected}-{initial})',
                    )
            else:
                assert current_row is not None
                current = f"${get_column_letter(corrected_column)}${current_row}"
                sheet.cell(
                    row,
                    corrected_column,
                    f'=IF(OR({raw}="",{current}="",NOT({correction_present})),"",({raw}-VLOOKUP($B{row},{bulk_range},2,FALSE))/{current})',
                )
            column += stage_width
        _apply_row_border(sheet, row, 1, last_column)

    data_last = data_start + len(section.rows) - 1
    stats_start = data_last + 2
    for offset, label in enumerate(("Minimum", "Maximum", "Average", "Stdev")):
        sheet.cell(stats_start + offset, 3, label).font = Font(bold=True)
    for numeric_column in corrected_columns + delta_columns:
        letter = get_column_letter(numeric_column)
        source = f"{letter}{data_start}:{letter}{data_last}"
        sheet.cell(stats_start, numeric_column, f'=IF(COUNT({source})=0,"",MIN({source}))')
        sheet.cell(stats_start + 1, numeric_column, f'=IF(COUNT({source})=0,"",MAX({source}))')
        sheet.cell(stats_start + 2, numeric_column, f'=IF(COUNT({source})=0,"",AVERAGE({source}))')
        sheet.cell(stats_start + 3, numeric_column, f'=IF(COUNT({source})<2,"",STDEV.S({source}))')
    return stats_start + 6


def _stage_width(record_type: str, delta_r_enabled: bool, stage_index: int) -> int:
    return 3 if record_type == "llcr" and delta_r_enabled and stage_index > 0 else 2


def _apply_row_border(sheet, row: int, first_column: int, last_column: int) -> None:
    for column in range(first_column, last_column + 1):
        sheet.cell(row, column).border = _BORDER


def _number(value: str | None):
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
