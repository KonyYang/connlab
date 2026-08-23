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
    LLCR_CR_RECORD_LAYOUT_V2,
    set_column_widths,
    write_header_row,
    write_macro_style_llcr_category_sheet,
    write_macro_style_llcr_summary,
    write_specialized_category_sheet,
)



class LlcrCrSpecializedRecordWorkbookGateway:
    """Write one fresh macro-free `.xlsx` workbook from a ready projection."""

    def write(self, *, output_path: Path, projection: LlcrCrRecordProjection) -> Path:
        """Create the fixed workbook layout without mutating source authority."""
        target = Path(output_path)
        if target.suffix.lower() != ".xlsx":
            raise ValueError("LLCR/CR specialized record output must be .xlsx.")
        if projection.status not in {"ready", "complete", "partial_compatible"}:
            raise ValueError("A ready LLCR/CR record preview is required for generation.")
        if projection.record_type not in {"llcr", "cr"}:
            raise ValueError("A single LLCR or CR record type is required for generation.")
        if not target.parent.is_dir():
            raise FileNotFoundError(f"Output directory does not exist: {target.parent}")

        workbook = Workbook()
        workbook.remove(workbook.active)
        if projection.record_type == "llcr":
            self._write_llcr_workbook(workbook, projection)
            workbook.save(target)
            return target
        summary = workbook.create_sheet(LLCR_CR_RECORD_LAYOUT_V2["summary_sheet"])
        _write_summary(summary, projection)
        grouped: dict[str, list] = {}
        for section in projection.sections:
            if section.record_type != projection.record_type:
                raise ValueError("Record projection mixes LLCR and CR sections.")
            key = section.category_id or section.record_prefix or section.category_label or "Points"
            grouped.setdefault(key, []).append(section)
        used_names = {LLCR_CR_RECORD_LAYOUT_V2["summary_sheet"]}
        for sections in grouped.values():
            sheet_name = _sheet_name(
                sections[0].record_prefix or sections[0].category_label or "Points",
                used_names,
            )
            used_names.add(sheet_name)
            sheet = workbook.create_sheet(sheet_name)
            write_specialized_category_sheet(
                sheet,
                sections,
                record_type=projection.record_type,
                delta_r_enabled=projection.delta_r_enabled,
            )
        workbook.save(target)
        return target

    def _write_llcr_workbook(self, workbook: Workbook, projection: LlcrCrRecordProjection) -> None:
        summary = workbook.create_sheet("Summary")
        grouped: dict[str, list] = {}
        for section in projection.sections:
            if section.record_type != "llcr":
                raise ValueError("Record projection mixes LLCR and CR sections.")
            key = section.category_id or section.record_prefix or section.category_label or "Points"
            grouped.setdefault(key, []).append(section)
        used_names = {"Summary"}
        category_outputs = []
        for sections in grouped.values():
            sheet_name = _sheet_name(
                sections[0].record_prefix or sections[0].category_label or "Points",
                used_names,
            )
            used_names.add(sheet_name)
            sheet = workbook.create_sheet(sheet_name)
            stats_cells = write_macro_style_llcr_category_sheet(
                sheet,
                sections,
                delta_r_enabled=projection.delta_r_enabled,
                ltr_number=projection.ltr_number,
            )
            category_outputs.append((
                sheet_name,
                tuple(sections),
                stats_cells,
                sections[0].category_label or sections[0].record_prefix or "Statistics",
            ))
        write_macro_style_llcr_summary(
            summary,
            category_outputs,
            parameter_labels=projection.summary_parameter_labels,
            delta_r_enabled=projection.delta_r_enabled,
        )


def _write_summary(sheet, projection: LlcrCrRecordProjection) -> None:
    display_type = (projection.record_type or "llcr").upper()
    sheet["A1"] = f"{display_type} Test Record"
    sheet["A3"] = "Project ID"
    sheet["B3"] = projection.project_id
    is_live_draft = projection.matrix_source == "matrix_editor_current_ui_state"
    sheet["A4"] = "Matrix source" if is_live_draft else "Confirmed Matrix"
    sheet["B4"] = projection.confirmed_matrix_id
    sheet["A5"] = "Snapshot" if is_live_draft else "Confirmed revision"
    sheet["B5"] = (
        "Current unconfirmed UI draft" if is_live_draft else projection.confirmed_revision
    )
    sheet["A6"] = "Point Profile"
    sheet["B6"] = projection.point_profile_revision_id or "Legacy Matrix contact plan"
    sheet["A7"] = "Profile revision"
    sheet["B7"] = projection.point_profile_revision_sequence or ""
    sheet["A8"] = "ΔR"
    sheet["B8"] = (
        "Enabled" if projection.record_type == "llcr" and projection.delta_r_enabled
        else "Disabled" if projection.record_type == "llcr"
        else "Not used for CR"
    )
    write_header_row(sheet, 10, LLCR_CR_RECORD_LAYOUT_V2["summary_headers"])
    for index, section in enumerate(projection.sections, start=11):
        sheet.cell(index, 1, _display_type(section.record_type))
        sheet.cell(index, 2, section.category_label or section.record_prefix or "Points")
        sheet.cell(index, 3, section.group_label)
        sheet.cell(index, 4, section.sample_count)
        sheet.cell(index, 5, section.readings_per_sample)
        sheet.cell(index, 6, len(section.stages))
        sheet.cell(index, 7, len(section.rows))
    set_column_widths(sheet, (18, 24, 18, 12, 18, 16, 14))
def _display_type(record_type: str) -> str:
    return "CR" if record_type in {"cr", "cr_specified_current"} else "LLCR"


def _sheet_name(value: str, used: set[str]) -> str:
    import re

    base = re.sub(r"[\\/*?:\[\]]+", "_", value.strip())[:31] or "Points"
    candidate = base
    suffix = 2
    while candidate in used:
        tail = f"_{suffix}"
        candidate = f"{base[:31 - len(tail)]}{tail}"
        suffix += 1
    return candidate
