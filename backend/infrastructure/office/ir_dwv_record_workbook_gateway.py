"""Template-driven openpyxl writer for IR/DWV record workbooks."""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re
from typing import Any, Iterable

from openpyxl import load_workbook
from openpyxl.formula.translate import Translator
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from backend.infrastructure.office.ir_dwv_record_workbook_layout import (
    IrDwvBlockLayout,
    TEMPLATE_PAIR_ROW_COUNT,
    TEMPLATE_SAMPLE_COUNT,
    block_layout,
    dynamic_merge_ranges,
    plan_block_placements,
)


@dataclass(frozen=True, slots=True)
class IrDwvEquipment:
    instrument: str = ""
    gage_id: str = ""
    last_calibration: date | datetime | str | None = None
    calibration_due: date | datetime | str | None = None


@dataclass(frozen=True, slots=True)
class IrDwvRecordStep:
    label: str
    ir_condition: str
    dwv_condition: str
    measurement_pairs: tuple[str, ...] = ()
    expected_fee_quantity: int | None = None
    description_is_override: bool = False


@dataclass(frozen=True, slots=True)
class IrDwvRecordGroup:
    label: str
    sample_count: int
    steps: tuple[IrDwvRecordStep, ...]


@dataclass(frozen=True, slots=True)
class IrDwvRecordProjection:
    request_number: str
    product_name: str
    tested_by: str = ""
    checked_by: str = ""
    approved_by: str = ""
    requestor: str = ""
    start_date: date | datetime | str | None = None
    finish_date: date | datetime | str | None = None
    ambient_temperature: str = ""
    relative_humidity: str = ""
    equipment: tuple[IrDwvEquipment, ...] = ()
    groups: tuple[IrDwvRecordGroup, ...] = ()


class IrDwvRecordWorkbookGateway:
    """Build a blank record workbook without mutating its registered template."""

    def __init__(self, template_path: Path) -> None:
        self._template_path = Path(template_path)

    def write(
        self,
        *,
        output_path: Path,
        projection: IrDwvRecordProjection,
    ) -> Path:
        target = Path(output_path)
        if target.suffix.lower() != ".xlsx":
            raise ValueError("IR/DWV record output must be .xlsx.")
        if not target.parent.is_dir():
            raise FileNotFoundError(f"Output directory does not exist: {target.parent}")
        self._validate_template_available()

        workbook = load_workbook(self._template_path, data_only=False)
        try:
            prototype = workbook.worksheets[0]
            _validate_template_fingerprint(prototype)
            generated: list[Worksheet] = []
            generated_names: list[tuple[Worksheet, str]] = []
            used_names: set[str] = set()
            for group in projection.groups:
                sample_count = _positive_integer(group.sample_count)
                if not group.steps:
                    continue
                pair_sets = {
                    tuple(item.strip() for item in step.measurement_pairs if item.strip())
                    for step in group.steps
                }
                if len(pair_sets) != 1:
                    raise ValueError(
                        f"{group.label} IR/DWV steps must share one measurement-pair list."
                    )
                pairs = next(iter(pair_sets))
                for step in group.steps:
                    if (
                        step.expected_fee_quantity is not None
                        and step.expected_fee_quantity != sample_count * len(pairs)
                    ):
                        raise ValueError(
                            f"Fee quantity mismatch for {group.label} {step.label}: "
                            f"expected {sample_count * len(pairs)}, got "
                            f"{step.expected_fee_quantity}."
                        )
                placements = plan_block_placements(
                    sample_count=sample_count,
                    pair_count=len(pairs),
                    step_count=len(group.steps),
                )
                group_sheets: dict[int, Worksheet] = {}
                for placement, step in zip(placements, group.steps, strict=True):
                    sheet = group_sheets.get(placement.sheet_index)
                    if sheet is None:
                        suffix = (
                            ""
                            if placement.sheet_index == 0
                            else f" ({placement.sheet_index + 1})"
                        )
                        final_name = _unique_sheet_name(
                            f"{group.label}{suffix}", used_names
                        )
                        sheet = workbook.create_sheet(
                            f"__ir_dwv_generated_{len(generated) + 1}"
                        )
                        _copy_sheet_settings(prototype, sheet)
                        group_sheets[placement.sheet_index] = sheet
                        generated.append(sheet)
                        generated_names.append((sheet, final_name))
                    layout = block_layout(
                        origin_column=placement.origin_column,
                        sample_count=sample_count,
                        pair_count=len(pairs),
                    )
                    _copy_resized_template_block(prototype, sheet, layout)
                    _fill_block(
                        sheet=sheet,
                        layout=layout,
                        projection=projection,
                        group=group,
                        step=step,
                        pairs=pairs,
                    )
            if not generated:
                raise ValueError("IR/DWV record projection contains no test steps.")
            for sheet in tuple(workbook.worksheets):
                if sheet not in generated:
                    workbook.remove(sheet)
            for sheet, final_name in generated_names:
                sheet.title = final_name
            workbook.calculation.fullCalcOnLoad = True
            workbook.calculation.forceFullCalc = True
            workbook.save(target)
        finally:
            workbook.close()
        return target

    def _validate_template_available(self) -> None:
        if not self._template_path.is_file():
            raise FileNotFoundError(
                f"IR/DWV record template does not exist: {self._template_path}"
            )
        lock = self._template_path.with_name(f"~${self._template_path.name}")
        if lock.exists():
            raise ValueError("blocked: 请关闭 Excel 中的 IR&DWV Template.xlsx")


def _positive_integer(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("IR/DWV sample count must be a positive integer.")
    return value


def _validate_template_fingerprint(sheet: Worksheet) -> None:
    anchors = {
        "B1": "AP Product Test Laboratory",
        "E1": "Equipment Used",
        "B13": "Test/Test Condition",
        "H13": "Test/Test Condition",
        "B20": "UNITS",
        "L39": "FDQF-E-033",
        "L40": "G",
    }
    changed = [
        coordinate
        for coordinate, expected in anchors.items()
        if sheet[coordinate].value != expected
    ]
    required_merges = {
        "B1:D2",
        "E1:J1",
        "B10:H10",
        "I10:L10",
        "B13:G13",
        "H13:L13",
        "C36:G37",
        "H37:L37",
    }
    actual_merges = {str(item) for item in sheet.merged_cells.ranges}
    if changed or not required_merges.issubset(actual_merges):
        detail = ", ".join(changed) or "merged-cell topology"
        raise ValueError(f"IR/DWV template fingerprint mismatch: {detail}.")


def copy_block(
    source: Worksheet,
    target: Worksheet,
    *,
    source_min_row: int,
    source_max_row: int,
    source_min_column: int,
    source_max_column: int,
    target_min_row: int,
    target_min_column: int,
) -> None:
    """Copy a rectangular block with styles, formulas, merges and dimensions."""
    row_offset = target_min_row - source_min_row
    column_offset = target_min_column - source_min_column
    for row in range(source_min_row, source_max_row + 1):
        _copy_row_dimension(source, target, row, row + row_offset)
        for column in range(source_min_column, source_max_column + 1):
            _copy_cell(
                source.cell(row, column),
                target.cell(row + row_offset, column + column_offset),
            )
    for column in range(source_min_column, source_max_column + 1):
        _copy_column_dimension(source, target, column, column + column_offset)
    for merged in source.merged_cells.ranges:
        if (
            source_min_row <= merged.min_row <= merged.max_row <= source_max_row
            and source_min_column
            <= merged.min_col
            <= merged.max_col
            <= source_max_column
        ):
            target.merge_cells(
                start_row=merged.min_row + row_offset,
                start_column=merged.min_col + column_offset,
                end_row=merged.max_row + row_offset,
                end_column=merged.max_col + column_offset,
            )


def _copy_cell(source: Any, target: Any) -> None:
    value = source.value
    if isinstance(value, str) and value.startswith("="):
        value = Translator(value, origin=source.coordinate).translate_formula(
            target.coordinate
        )
    target.value = value
    if source.has_style:
        target._style = copy(source._style)
    if source.number_format:
        target.number_format = source.number_format
    if source.hyperlink:
        target._hyperlink = copy(source.hyperlink)
    if source.comment:
        target.comment = copy(source.comment)


def _copy_row_dimension(
    source: Worksheet,
    target: Worksheet,
    source_row: int,
    target_row: int,
) -> None:
    if source_row not in source.row_dimensions:
        return
    source_dimension = source.row_dimensions[source_row]
    target_dimension = target.row_dimensions[target_row]
    target_dimension.height = source_dimension.height
    target_dimension.hidden = source_dimension.hidden
    target_dimension.outlineLevel = source_dimension.outlineLevel
    target_dimension.collapsed = source_dimension.collapsed


def _copy_column_dimension(
    source: Worksheet,
    target: Worksheet,
    source_column: int,
    target_column: int,
) -> None:
    source_letter = get_column_letter(source_column)
    if source_letter not in source.column_dimensions:
        return
    source_dimension = source.column_dimensions[source_letter]
    target_dimension = target.column_dimensions[get_column_letter(target_column)]
    target_dimension.width = source_dimension.width
    target_dimension.hidden = source_dimension.hidden
    target_dimension.outlineLevel = source_dimension.outlineLevel
    target_dimension.collapsed = source_dimension.collapsed


def _copy_sheet_settings(source: Worksheet, target: Worksheet) -> None:
    target.sheet_format = copy(source.sheet_format)
    target.sheet_properties = copy(source.sheet_properties)
    target.page_margins = copy(source.page_margins)
    target.page_setup = copy(source.page_setup)
    target.print_options = copy(source.print_options)
    target.sheet_view.showGridLines = source.sheet_view.showGridLines
    target.freeze_panes = source.freeze_panes
    target.oddHeader = copy(source.oddHeader)
    target.oddFooter = copy(source.oddFooter)
    target.evenHeader = copy(source.evenHeader)
    target.evenFooter = copy(source.evenFooter)
    target.firstHeader = copy(source.firstHeader)
    target.firstFooter = copy(source.firstFooter)


def _copy_resized_template_block(
    source: Worksheet,
    target: Worksheet,
    layout: IrDwvBlockLayout,
) -> None:
    if (
        layout.sample_count == TEMPLATE_SAMPLE_COUNT
        and layout.pair_count <= TEMPLATE_PAIR_ROW_COUNT
    ):
        copy_block(
            source,
            target,
            source_min_row=1,
            source_max_row=40,
            source_min_column=2,
            source_max_column=12,
            target_min_row=1,
            target_min_column=layout.origin_column,
        )
        return

    source_columns = [2]
    source_columns.extend(
        3 + min(index, TEMPLATE_SAMPLE_COUNT - 1)
        for index in range(layout.sample_count)
    )
    source_columns.extend(
        8 + min(index, TEMPLATE_SAMPLE_COUNT - 1)
        for index in range(layout.sample_count)
    )
    source_rows = _source_rows(layout)
    for target_row, source_row in source_rows:
        _copy_row_dimension(source, target, source_row, target_row)
        for target_column, source_column in zip(
            range(layout.origin_column, layout.last_column + 1),
            source_columns,
            strict=True,
        ):
            _copy_cell(
                source.cell(source_row, source_column),
                target.cell(target_row, target_column),
            )
    for target_column, source_column in zip(
        range(layout.origin_column, layout.last_column + 1),
        source_columns,
        strict=True,
    ):
        _copy_column_dimension(source, target, source_column, target_column)
    for merged in dynamic_merge_ranges(layout):
        target.merge_cells(merged)


def _source_rows(layout: IrDwvBlockLayout) -> tuple[tuple[int, int], ...]:
    rows: list[tuple[int, int]] = [(row, row) for row in range(1, 14)]
    rows.extend(
        (
            row,
            14 + min(row - layout.conditions_start_row, TEMPLATE_SAMPLE_COUNT - 1),
        )
        for row in range(
            layout.conditions_start_row,
            layout.conditions_end_row + 1,
        )
    )
    rows.extend(
        (target, source)
        for target, source in (
            (layout.sequence_row, 19),
            (layout.units_row, 20),
            (layout.sample_id_row, 21),
        )
    )
    rows.extend(
        (
            row,
            22 + min(row - layout.data_start_row, TEMPLATE_PAIR_ROW_COUNT - 1),
        )
        for row in range(layout.data_start_row, layout.data_end_row + 1)
    )
    rows.extend(
        (layout.stats_min_row + offset, 34 + offset)
        for offset in range(7)
    )
    return tuple(rows)


def _fill_block(
    *,
    sheet: Worksheet,
    layout: IrDwvBlockLayout,
    projection: IrDwvRecordProjection,
    group: IrDwvRecordGroup,
    step: IrDwvRecordStep,
    pairs: tuple[str, ...],
) -> None:
    origin = layout.origin_column
    last = layout.last_column
    _fill_equipment(sheet, layout, projection.equipment)
    sheet.cell(8, origin, f"Start Date:{_text(projection.start_date)}")
    sheet.cell(9, origin, f"Finish Date: {_text(projection.finish_date)}")
    sheet.cell(8, max(origin, last - 1), f"Amb Temp: {projection.ambient_temperature}")
    sheet.cell(9, max(origin, last - 1), f"Rel. Hum.:{projection.relative_humidity}")

    first_header_end = min(
        last,
        layout.ir_end_column + (1 if layout.sample_count > 1 else 0),
    )
    second_header_start = min(last, first_header_end + 1)
    sheet.cell(10, origin, f"Item/Process: {group.label}  IR&DWV-{step.label}")
    sheet.cell(10, second_header_start, f"Request  No.:  {projection.request_number}")
    sheet.cell(11, origin, "Remarks:")
    sheet.cell(11, second_header_start, f"Product Name: {projection.product_name}")

    personnel_columns = _personnel_columns(layout)
    for column, text in zip(
        personnel_columns,
        (
            f"Tested By: {projection.tested_by}",
            f"Checked By:{projection.checked_by}",
            f"Approved By:{projection.approved_by}",
            f"Requestor:{projection.requestor}",
        ),
        strict=True,
    ):
        sheet.cell(12, column, text)

    sheet.cell(13, origin, "Test/Test Condition")
    sheet.cell(13, layout.dwv_start_column, "Test/Test Condition")
    for index in range(layout.sample_count):
        row = layout.conditions_start_row + index
        sheet.cell(
            row,
            origin,
            f"{index + 1}. IR testing/ {index + 1}# {step.ir_condition}",
        )
        sheet.cell(
            row,
            layout.dwv_start_column,
            (
                f"{layout.sample_count + index + 1}. DWV testing/ "
                f"{index + 1}# {step.dwv_condition}"
            ),
        )

    sheet.cell(layout.sequence_row, origin).value = None
    for index, column in enumerate(
        range(layout.ir_start_column, layout.dwv_end_column + 1),
        start=1,
    ):
        sheet.cell(layout.sequence_row, column, index)
    sheet.cell(layout.units_row, origin, "UNITS")
    for column in range(layout.ir_start_column, layout.ir_end_column + 1):
        sheet.cell(layout.units_row, column, "GΩ")
    for column in range(layout.dwv_start_column, layout.dwv_end_column + 1):
        sheet.cell(layout.units_row, column, "nA")
    sheet.cell(layout.sample_id_row, origin, "SAMPLE ID      \n +&-")
    for index in range(layout.sample_count):
        sheet.cell(layout.sample_id_row, layout.ir_start_column + index, f"{index + 1}#")
        sheet.cell(layout.sample_id_row, layout.dwv_start_column + index, f"{index + 1}#")

    for row in range(layout.data_start_row, layout.data_end_row + 1):
        pair_index = row - layout.data_start_row
        sheet.cell(row, origin).value = pairs[pair_index] if pair_index < len(pairs) else None
        for column in range(layout.ir_start_column, layout.dwv_end_column + 1):
            sheet.cell(row, column).value = None

    data_range = (
        f"{get_column_letter(layout.dwv_start_column)}{layout.data_start_row}:"
        f"{get_column_letter(layout.dwv_end_column)}{layout.data_end_row}"
    )
    for row, label in (
        (layout.stats_min_row, "Min"),
        (layout.stats_max_row, "Max"),
        (layout.stats_average_row, "Average"),
        (layout.stats_stdev_row, "Stdev"),
    ):
        sheet.cell(row, origin, label)
    sheet.cell(layout.stats_min_row, layout.ir_start_column, "/")
    sheet.cell(layout.stats_max_row, layout.ir_start_column, "/")
    sheet.cell(layout.stats_average_row, layout.ir_start_column, "/")
    sheet.cell(layout.stats_min_row, layout.dwv_start_column, f"=MIN({data_range})")
    sheet.cell(layout.stats_max_row, layout.dwv_start_column, f"=MAX({data_range})")
    sheet.cell(
        layout.stats_average_row,
        layout.dwv_start_column,
        f"=AVERAGE({data_range})",
    )
    sheet.cell(layout.stats_stdev_row, layout.dwv_start_column, f"=STDEV({data_range})")
    sheet.cell(layout.footer_form_row, origin, "此表为DGLAB-LNP-11之附件")
    sheet.cell(layout.footer_form_row, last - 1, "Form No:")
    sheet.cell(layout.footer_form_row, last, "FDQF-E-033")
    sheet.cell(layout.footer_revision_row, last - 1, "Rev:")
    sheet.cell(layout.footer_revision_row, last, "G")


def _fill_equipment(
    sheet: Worksheet,
    layout: IrDwvBlockLayout,
    equipment: Iterable[IrDwvEquipment],
) -> None:
    origin = layout.origin_column
    instrument_column = min(layout.last_column, origin + 3)
    if layout.sample_count >= TEMPLATE_SAMPLE_COUNT:
        gage_column = min(layout.last_column, origin + 6)
    else:
        gage_column = min(layout.last_column, instrument_column + 1)
    last_cal_column = min(layout.last_column, gage_column + 1)
    due_column = min(layout.last_column, last_cal_column + 1)
    for row in range(3, 8):
        for column in {
            instrument_column,
            gage_column,
            last_cal_column,
            due_column,
        }:
            sheet.cell(row, column).value = None
    for row, item in zip(range(3, 8), equipment):
        sheet.cell(row, instrument_column, item.instrument)
        sheet.cell(row, gage_column, item.gage_id)
        sheet.cell(row, last_cal_column, item.last_calibration)
        sheet.cell(row, due_column, item.calibration_due)


def _personnel_columns(layout: IrDwvBlockLayout) -> tuple[int, int, int, int]:
    base, remainder = divmod(layout.width, 4)
    sizes = [base + (1 if index < remainder else 0) for index in range(4)]
    columns: list[int] = []
    cursor = layout.origin_column
    for size in sizes:
        columns.append(min(layout.last_column, cursor))
        cursor += size
    return tuple(columns)  # type: ignore[return-value]


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y/%m/%d")
    return str(value)


def _unique_sheet_name(value: str, used: set[str]) -> str:
    base = re.sub(r"[\\/*?:\[\]]+", "_", value.strip())[:31] or "Group"
    candidate = base
    suffix = 2
    while candidate in used:
        tail = f" ({suffix})"
        candidate = f"{base[:31 - len(tail)]}{tail}"
        suffix += 1
    used.add(candidate)
    return candidate
