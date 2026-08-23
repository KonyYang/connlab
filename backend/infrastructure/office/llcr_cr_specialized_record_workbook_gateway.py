"""Macro-free openpyxl workbook writer for LLCR/CR specialized records."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordProjection,
)
from backend.infrastructure.office.llcr_cr_record_workbook_layout import (
    write_macro_style_contact_resistance_category_sheet,
    write_macro_style_contact_resistance_summary,
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
        self._write_macro_style_workbook(workbook, projection)
        workbook.save(target)
        return target

    def _write_macro_style_workbook(
        self,
        workbook: Workbook,
        projection: LlcrCrRecordProjection,
    ) -> None:
        summary = workbook.create_sheet("Summary")
        grouped: dict[str, list] = {}
        for section in projection.sections:
            if section.record_type != projection.record_type:
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
            stats_cells = write_macro_style_contact_resistance_category_sheet(
                sheet,
                sections,
                record_type=projection.record_type,
                delta_r_enabled=projection.delta_r_enabled,
                ltr_number=projection.ltr_number,
            )
            category_outputs.append((
                sheet_name,
                tuple(sections),
                stats_cells,
                sections[0].category_label or sections[0].record_prefix or "Statistics",
            ))
        write_macro_style_contact_resistance_summary(
            summary,
            category_outputs,
            parameter_labels=projection.summary_parameter_labels,
            record_type=projection.record_type,
            delta_r_enabled=projection.delta_r_enabled,
        )


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
