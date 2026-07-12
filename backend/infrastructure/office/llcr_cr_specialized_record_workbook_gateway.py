"""Macro-free openpyxl workbook writer for LLCR/CR specialized records."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordProjection,
)
from backend.infrastructure.office.llcr_cr_record_workbook_layout import (
    LLCR_CR_RECORD_LAYOUT_V1,
    set_column_widths,
    write_header_row,
    write_record_sheet,
)



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
        write_record_sheet(llcr, tuple(section for section in projection.sections if section.record_type == "llcr"))
        write_record_sheet(cr, tuple(section for section in projection.sections if section.record_type == "cr_specified_current"))
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
    write_header_row(sheet, 8, headers)
    for index, section in enumerate(projection.sections, start=9):
        sheet.cell(index, 1, _display_type(section.record_type))
        sheet.cell(index, 2, section.group_label)
        sheet.cell(index, 3, section.source_step)
        sheet.cell(index, 4, section.sample_count)
        sheet.cell(index, 5, section.readings_per_sample)
        sheet.cell(index, 6, len(section.rows))
        sheet.cell(index, 7, "Ready")
    set_column_widths(sheet, (18, 24, 18, 12, 18, 16, 14))
def _display_type(record_type: str) -> str:
    return "CR" if record_type == "cr_specified_current" else "LLCR"
