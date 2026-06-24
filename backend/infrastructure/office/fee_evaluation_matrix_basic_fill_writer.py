"""Matrix basic-fill writer for Fee Evaluation workbooks."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    MatrixBasicFillLine,
    MatrixBasicFillWorkbook,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportValues,
    REPORT_PREPARATION_MANUAL_IDENTITY,
    basic_fill_line_identity,
    edited_row_lookup,
    manual_row_lookup,
    sample_preparation_group_identity,
)
from backend.infrastructure.office.fee_evaluation_sheet_ops import (
    apply_a_column_group_borders as _apply_a_column_group_borders,
    cell_fill_color as _cell_fill_color,
    clear_cell_fill as _clear_cell_fill,
    clear_cell_fill_range as _clear_cell_fill_range,
    insert_rows as _insert_rows,
    set_a_column_bold as _set_a_column_bold,
    set_a_column_fill as _set_a_column_fill,
    set_block_values as _set_block_values,
    set_cell_fill as _set_cell_fill,
    set_formula_block as _set_formula_block,
    set_row_values as _set_row_values,
)
from backend.infrastructure.office.fee_evaluation_anchor_snapshot import (
    FeeEvaluationAnchorSnapshot,
)


DETAIL_START_ROW = 5
LIGHT_BLUE_FILL = 0xDDEBF7


@dataclass(frozen=True, slots=True)
class TemplateRow:
    """Captured values from one template row that must be preserved."""

    cells: tuple[str, ...]
    formula_columns: tuple[int, ...]


def write_matrix_basic_fill(
    *,
    sheet: Any,
    basic_fill: MatrixBasicFillWorkbook,
    edited_values: FeeEvaluationEditedExportValues | None,
    anchors: FeeEvaluationAnchorSnapshot | None = None,
) -> tuple[str, ...]:
    """Write Matrix basic-fill rows with batched writes for unedited detail rows."""
    anchors = anchors or FeeEvaluationAnchorSnapshot.from_sheet(sheet)
    warnings: list[str] = []
    edited_lookup = edited_row_lookup(edited_values, basic_fill)
    manual_lookup = manual_row_lookup(edited_values)
    report_row = anchors.find_required_row("Report preparation")
    condition_row = anchors.find_required_row("条件确认")
    total_row = anchors.find_required_row("Total")
    anchors.find_required_row("Grand Cost")
    external_cost_row = anchors.find_optional_row("External Cost")
    sample_template = _capture_template_row(sheet, DETAIL_START_ROW, anchors=anchors)
    report_template = _capture_template_row(sheet, report_row, anchors=anchors)
    condition_template = _capture_template_row(sheet, condition_row, anchors=anchors)
    ltr_number_fill = _cell_fill_color(sheet, 2, 3)
    group_fill_colors = (ltr_number_fill, LIGHT_BLUE_FILL)
    generated_detail_count = sum(1 + len(group.lines) for group in basic_fill.groups) + 2
    existing_detail_count = total_row - DETAIL_START_ROW
    inserted_row_count = max(generated_detail_count - existing_detail_count, 0)
    if generated_detail_count > existing_detail_count:
        _insert_rows(sheet, total_row, inserted_row_count)
    if external_cost_row is not None and external_cost_row >= total_row:
        external_cost_row += inserted_row_count

    row_index = DETAIL_START_ROW
    for group_index, group in enumerate(basic_fill.groups):
        group_start = row_index
        _write_template_row(
            sheet=sheet,
            template=sample_template,
            row_index=row_index,
            overrides={
                1: _display_group_label(group.group_label),
                2: "0",
                3: "Sample preparation",
                4: "0",
                5: "per sample",
                6: "1",
                7: "0",
                8: "0",
            },
        )
        _clear_cell_fill(sheet=sheet, row_index=row_index, column=2)
        _set_cell_fill(sheet=sheet, row_index=row_index, column=3, color=ltr_number_fill)
        sample_edit = manual_lookup.get(sample_preparation_group_identity(group))
        if sample_edit is not None:
            warnings.extend(
                _write_edited_values_to_row(
                    sheet=sheet,
                    row_index=row_index,
                    spend_time=sample_edit.spend_time,
                    unit_price=sample_edit.unit_price,
                    unit_type=sample_edit.unit_type,
                    units=sample_edit.units,
                    base_fee=sample_edit.base_fee,
                    discount=sample_edit.discount,
                    testing_fee=sample_edit.testing_fee,
                    notes=sample_edit.notes,
                    comment_warning=(
                        f"Sample preparation note for {group.group_label} "
                        "was not exported because Excel comment creation failed."
                    ),
                )
            )
        _set_formula(sheet, row_index, 9, _detail_fee_formula(row_index))
        row_index += 1
        line_index = 0
        group_lines = tuple(group.lines)
        while line_index < len(group_lines):
            line = group_lines[line_index]
            edited_row = edited_lookup.get(basic_fill_line_identity(line))
            if edited_row is not None:
                warnings.extend(
                    _write_matrix_detail_row(
                        sheet=sheet,
                        row_index=row_index,
                        line=line,
                        edited_row=edited_row,
                    )
                )
                row_index += 1
                line_index += 1
                continue
            block_start = line_index
            while line_index < len(group_lines):
                next_line = group_lines[line_index]
                if edited_lookup.get(basic_fill_line_identity(next_line)) is not None:
                    break
                line_index += 1
            block_lines = group_lines[block_start:line_index]
            _write_unedited_detail_rows(
                sheet=sheet,
                start_row=row_index,
                lines=block_lines,
            )
            row_index += len(block_lines)
        _set_a_column_fill(
            sheet=sheet,
            start_row=group_start,
            end_row=row_index - 1,
            color=group_fill_colors[group_index % len(group_fill_colors)],
        )
        _apply_a_column_group_borders(sheet, group_start, row_index - 1)

    report_row_index = row_index
    _write_template_row(
        sheet=sheet,
        template=report_template,
        row_index=report_row_index,
        overrides={1: "", 3: "Report preparation"},
    )
    report_edit = manual_lookup.get(REPORT_PREPARATION_MANUAL_IDENTITY)
    if report_edit is not None:
        warnings.extend(
            _write_edited_values_to_row(
                sheet=sheet,
                row_index=report_row_index,
                spend_time=report_edit.spend_time,
                unit_price=report_edit.unit_price,
                unit_type=report_edit.unit_type,
                units=report_edit.units,
                base_fee=report_edit.base_fee,
                discount=report_edit.discount,
                testing_fee=report_edit.testing_fee,
                notes=report_edit.notes,
                comment_warning="Report preparation note was not exported because Excel comment creation failed.",
            )
        )
    _clear_cell_fill(sheet=sheet, row_index=report_row_index, column=2)
    row_index += 1
    _write_template_row(
        sheet=sheet,
        template=condition_template,
        row_index=row_index,
        overrides={1: "条件确认"},
    )
    if edited_values is not None:
        sheet.Cells(row_index, 2).Value = _numeric_cell_value(
            edited_values.summary.condition_confirmation_spend_time,
            default="0",
        )
    _clear_cell_fill(sheet=sheet, row_index=row_index, column=2)
    if external_cost_row is not None and edited_values is not None:
        sheet.Cells(external_cost_row, 4).Value = _numeric_cell_value(
            edited_values.summary.external_cost,
            default="0",
        )
        external_note_warning = _set_cell_comment(
            sheet=sheet,
            row_index=external_cost_row,
            column=4,
            text=edited_values.summary.external_cost_note,
            failure_warning="External Cost note was not exported because Excel comment creation failed.",
        )
        if external_note_warning:
            warnings.append(external_note_warning)
    elif edited_values is not None:
        if _numeric_cell_value(edited_values.summary.external_cost, default="0") != "0":
            warnings.append(
                "External Cost was not exported because no stable template anchor was found."
            )
        if edited_values.summary.external_cost_note.strip():
            warnings.append(
                "External Cost note was not exported because no stable template anchor was found."
            )
    total_row_index = row_index + 1
    _write_total_formulas(
        sheet=sheet,
        total_row_index=total_row_index,
        last_detail_row=row_index,
    )
    _set_a_column_bold(sheet, DETAIL_START_ROW, total_row_index + 2)
    return tuple(warnings)


def _write_matrix_detail_row(
    *,
    sheet: Any,
    row_index: int,
    line: MatrixBasicFillLine,
    edited_row: FeeEvaluationEditedExportRow | None,
) -> tuple[str, ...]:
    if edited_row is None:
        _set_row_values(
            sheet,
            row_index,
            1,
            ("", "", line.test_item, "", "", "", "", ""),
        )
        _clear_cell_fill(sheet=sheet, row_index=row_index, column=2)
        warnings: tuple[str, ...] = ()
    else:
        sheet.Cells(row_index, 1).Value = ""
        sheet.Cells(row_index, 3).Value = line.test_item
        _clear_cell_fill(sheet=sheet, row_index=row_index, column=2)
        warnings = _write_edited_values_to_row(
            sheet=sheet,
            row_index=row_index,
            spend_time=edited_row.spend_time,
            unit_price=edited_row.unit_price,
            unit_type=edited_row.unit_type,
            units=edited_row.units,
            base_fee=edited_row.base_fee,
            discount=edited_row.discount,
            testing_fee=edited_row.testing_fee,
            notes=edited_row.notes,
            comment_warning=(
                f"Fee row note for {line.group_label} step {_line_step_label(line)} "
                "was not exported because Excel comment creation failed."
            ),
        )
    _set_formula(sheet, row_index, 9, _detail_fee_formula(row_index))
    return warnings


def _write_unedited_detail_rows(
    *,
    sheet: Any,
    start_row: int,
    lines: tuple[MatrixBasicFillLine, ...],
) -> None:
    """Write contiguous unedited Matrix detail rows with batched COM calls."""
    if not lines:
        return
    _set_block_values(
        sheet,
        start_row,
        1,
        tuple(("", "", line.test_item, "", "", "", "", "") for line in lines),
    )
    end_row = start_row + len(lines) - 1
    _clear_cell_fill_range(
        sheet=sheet,
        start_row=start_row,
        end_row=end_row,
        column=2,
    )
    _set_formula_block(
        sheet,
        start_row,
        9,
        tuple(_detail_fee_formula(row) for row in range(start_row, end_row + 1)),
    )


def _write_edited_values_to_row(
    *,
    sheet: Any,
    row_index: int,
    spend_time: str,
    unit_price: str,
    unit_type: str,
    units: str,
    base_fee: str,
    discount: str,
    testing_fee: str,
    notes: str,
    comment_warning: str,
) -> tuple[str, ...]:
    """Write TASK_300 editable values to one Testing Prices row."""
    sheet.Cells(row_index, 2).Value = _numeric_cell_value(spend_time, default="0")
    _set_row_values(
        sheet,
        row_index,
        4,
        (
            _numeric_cell_value(unit_price, default="0"),
            _unit_type_text(unit_type),
            _numeric_cell_value(units, default="1"),
            _numeric_cell_value(base_fee, default="0"),
            _discount_fraction(discount),
        ),
    )
    if not _supports_formula(sheet, row_index, 9):
        sheet.Cells(row_index, 9).Value = _numeric_cell_value(testing_fee, default="0")
    warning = _set_cell_comment(
        sheet=sheet,
        row_index=row_index,
        column=9,
        text=notes,
        failure_warning=comment_warning,
    )
    return (warning,) if warning else ()


def _write_template_row(
    *,
    sheet: Any,
    template: TemplateRow,
    row_index: int,
    overrides: dict[int, str],
) -> None:
    batch_start: int | None = None
    batch_values: list[str] = []
    for column, value in enumerate(template.cells, start=1):
        text = overrides.get(column, value)
        if column in template.formula_columns:
            if batch_start is not None:
                _set_row_values(sheet, row_index, batch_start, tuple(batch_values))
                batch_start = None
                batch_values = []
            _set_formula(sheet, row_index, column, _detail_fee_formula(row_index))
            continue
        if batch_start is None:
            batch_start = column
        batch_values.append(text)
    if batch_start is not None:
        _set_row_values(sheet, row_index, batch_start, tuple(batch_values))


def _set_row_values(
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


def _display_group_label(group_label: str) -> str:
    label = group_label.strip()
    if label.lower().startswith("group "):
        return label[6:].strip()
    return label


def _line_step_label(line: MatrixBasicFillLine) -> str:
    return ", ".join(token for token in line.step_tokens if token.strip()) or "-"


def _capture_template_row(
    sheet: Any,
    row_index: int,
    *,
    anchors: FeeEvaluationAnchorSnapshot,
) -> TemplateRow:
    cells: list[str] = []
    formula_columns: list[int] = []
    for column in range(1, 10):
        formula = anchors.cell_formula(row_index, column)
        if formula.startswith("="):
            cells.append(formula)
            formula_columns.append(column)
        else:
            cells.append(anchors.cell_value(row_index, column))
    return TemplateRow(cells=tuple(cells), formula_columns=tuple(formula_columns))


def _detail_fee_formula(row_index: int) -> str:
    return f"=D{row_index}*F{row_index}*(1-H{row_index})+G{row_index}"


def _write_total_formulas(
    *,
    sheet: Any,
    total_row_index: int,
    last_detail_row: int,
) -> None:
    _set_formula(sheet, total_row_index, 2, f"=SUM(B{DETAIL_START_ROW}:B{last_detail_row})")
    _set_formula(sheet, total_row_index, 9, f"=SUM(I{DETAIL_START_ROW}:I{last_detail_row})")


def _set_formula(sheet: Any, row: int, column: int, formula: str) -> None:
    sheet.Cells(row, column).Formula = formula


def _supports_formula(sheet: Any, row: int, column: int) -> bool:
    return hasattr(sheet.Cells(row, column), "Formula")


def _set_cell_comment(
    *,
    sheet: Any,
    row_index: int,
    column: int,
    text: str,
    failure_warning: str,
) -> str | None:
    normalized = text.strip()
    if hasattr(sheet, "set_cell_comment"):
        try:
            sheet.set_cell_comment(row_index, column, normalized)
        except Exception:
            return failure_warning if normalized else None
        return None
    cell = sheet.Cells(row_index, column)
    try:
        cell.ClearComments()
    except Exception:
        pass
    if not normalized:
        return None
    try:
        cell.AddComment(normalized)
    except Exception:
        return failure_warning
    return None


def _numeric_cell_value(value: str, *, default: str) -> str:
    normalized = value.strip()
    if not normalized or normalized.lower() == "pending":
        return default
    return normalized.replace("$", "").replace(",", "")


def _discount_fraction(value: str) -> str:
    normalized = value.strip().replace("%", "")
    if not normalized or normalized.lower() == "pending":
        return "0"
    try:
        return format(Decimal(normalized.replace(",", "")) / Decimal("100"), "f")
    except Exception:
        return "0"


def _unit_type_text(value: str) -> str:
    normalized = value.strip()
    return normalized if normalized else "per sample"
