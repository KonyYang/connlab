"""Excel gateway for fee-evaluation workbook generation."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from backend.application.confirmed_matrix_fee_draft_service import FeeEvaluationDraft
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    MatrixBasicFillWorkbook,
)
from backend.application.test_record_fee_dataset_preview_service import (
    TestRecordFeeDatasetPreview,
)
from backend.infrastructure.office.models import FeeEvaluationWorkbookWriteResult
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable


_EXCEL_FILE_FORMATS = {
    ".xlsx": 51,
    ".xls": 56,
}
_EXCEL_CALCULATION_MANUAL = -4135
_DETAIL_START_ROW = 5
_LIGHT_BLUE_FILL = 0xDDEBF7
_WHITE_FILL = 0xFFFFFF
_EXCEL_LINE_STYLE_NONE = -4142
_EXCEL_LINE_STYLE_CONTINUOUS = 1
_EXCEL_EDGE_LEFT = 7
_EXCEL_EDGE_TOP = 8


@dataclass(frozen=True, slots=True)
class _TemplateRow:
    """Captured values from one template row that must be preserved."""

    cells: tuple[str, ...]
    formula_columns: tuple[int, ...]


class FeeEvaluationWorkbookGateway:
    """Generate fee-evaluation workbooks through a COM-only Excel boundary."""

    def __init__(self, excel_app_factory: Callable[[], Any] | None = None) -> None:
        self._excel_app_factory = excel_app_factory

    def generate(
        self,
        *,
        template_path: Path,
        output_path: Path,
        preview: TestRecordFeeDatasetPreview,
    ) -> FeeEvaluationWorkbookWriteResult:
        """Write fee-evaluation content using Excel COM when available."""
        template = Path(template_path)
        target = Path(output_path)
        if template.suffix.lower() not in {".xls", ".xlsx"}:
            raise ValueError(f"Unsupported fee template type: {template}")
        if not template.is_file():
            raise FileNotFoundError(f"Template does not exist: {template}")
        if not target.parent.exists():
            raise FileNotFoundError(f"Output directory does not exist: {target.parent}")

        excel = self._open_excel_application()
        workbook = None
        excel_state = None
        try:
            excel.Visible = False
            excel.DisplayAlerts = False
            excel_state = _begin_excel_batch(excel)
            workbook = excel.Workbooks.Open(str(template))
            summary = preview.fee_dataset.summary if preview.fee_dataset is not None else None
            sheet = workbook.Worksheets.Item(1)
            sheet.Cells(1, 1).Value = "ConnLab Generated Fee Evaluation"
            sheet.Cells(2, 1).Value = f"Project ID: {preview.project_id}"
            sheet.Cells(3, 1).Value = f"Draft ID: {preview.draft_id}"
            if summary is not None:
                sheet.Cells(4, 1).Value = f"Group count: {summary.group_count}"
                sheet.Cells(5, 1).Value = f"Step count: {summary.step_count}"
                sheet.Cells(6, 1).Value = (
                    f"Explicit duration days: {summary.explicit_duration_days}"
                )
            _save_as(workbook, target)
        finally:
            if workbook is not None:
                workbook.Close(SaveChanges=False)
            _restore_excel_batch(excel, excel_state)
            excel.Quit()

        return FeeEvaluationWorkbookWriteResult(
            output_path=target,
            status="generated",
            warnings=("Pricing values are not calculated by ConnLab.",),
        )

    def generate_from_draft(
        self,
        *,
        template_path: Path,
        output_path: Path,
        draft: FeeEvaluationDraft,
        prepared_by: str | None,
        approved_by: str | None,
    ) -> FeeEvaluationWorkbookWriteResult:
        """Write structured fee draft rows to the workbook Testing Prices sheet."""
        template = Path(template_path)
        target = Path(output_path)
        if template.suffix.lower() not in {".xls", ".xlsx"}:
            raise ValueError(f"Unsupported fee template type: {template}")
        if target.suffix.lower() not in {".xls", ".xlsx"}:
            raise ValueError(f"Unsupported fee output type: {target}")
        if not template.is_file():
            raise FileNotFoundError(f"Template does not exist: {template}")
        if not target.parent.exists():
            raise FileNotFoundError(f"Output directory does not exist: {target.parent}")

        excel = self._open_excel_application()
        workbook = None
        excel_state = None
        try:
            excel.Visible = False
            excel.DisplayAlerts = False
            excel_state = _begin_excel_batch(excel)
            workbook = excel.Workbooks.Open(str(template))
            sheet = _testing_prices_sheet(workbook)
            _write_structured_fee_draft(
                sheet=sheet,
                draft=draft,
                prepared_by=prepared_by,
                approved_by=approved_by,
            )
            _save_as(workbook, target)
        finally:
            if workbook is not None:
                workbook.Close(SaveChanges=False)
            _restore_excel_batch(excel, excel_state)
            excel.Quit()

        return FeeEvaluationWorkbookWriteResult(
            output_path=target,
            status="generated",
            warnings=(),
        )

    def generate_matrix_basic_fill(
        self,
        *,
        template_path: Path,
        output_path: Path,
        basic_fill: MatrixBasicFillWorkbook,
        review_required: bool,
        prepared_by: str | None,
        approved_by: str | None,
    ) -> FeeEvaluationWorkbookWriteResult:
        """Write Matrix basic-fill A/C rows to the Testing Prices sheet."""
        template = Path(template_path)
        target = Path(output_path)
        if template.suffix.lower() not in {".xls", ".xlsx"}:
            raise ValueError(f"Unsupported fee template type: {template}")
        if target.suffix.lower() not in {".xls", ".xlsx"}:
            raise ValueError(f"Unsupported fee output type: {target}")
        if not template.is_file():
            raise FileNotFoundError(f"Template does not exist: {template}")
        if not target.parent.exists():
            raise FileNotFoundError(f"Output directory does not exist: {target.parent}")

        excel = self._open_excel_application()
        workbook = None
        excel_state = None
        try:
            excel.Visible = False
            excel.DisplayAlerts = False
            excel_state = _begin_excel_batch(excel)
            workbook = excel.Workbooks.Open(str(template))
            sheet = _testing_prices_sheet(workbook)
            _write_matrix_basic_fill(sheet=sheet, basic_fill=basic_fill)
            _save_as(workbook, target)
        finally:
            if workbook is not None:
                workbook.Close(SaveChanges=False)
            _restore_excel_batch(excel, excel_state)
            excel.Quit()

        warnings = ["Matrix basic fill only."]
        if review_required:
            warnings.append("Pricing still requires review.")
        return FeeEvaluationWorkbookWriteResult(
            output_path=target,
            status="generated",
            warnings=tuple(warnings),
        )

    def _open_excel_application(self) -> Any:
        if self._excel_app_factory is not None:
            return self._excel_app_factory()
        try:
            import win32com.client  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise OfficeAutomationUnavailable(
                "Excel COM automation is required for fee template generation."
            ) from exc
        return win32com.client.DispatchEx("Excel.Application")


def _testing_prices_sheet(workbook: Any) -> Any:
    try:
        return workbook.Worksheets.Item("Testing Prices")
    except Exception as exc:
        raise ValueError("Workbook sheet 'Testing Prices' was not found.") from exc


def _begin_excel_batch(excel: Any) -> dict[str, Any]:
    state: dict[str, Any] = {}
    for name, value in (
        ("ScreenUpdating", False),
        ("EnableEvents", False),
        ("Calculation", _EXCEL_CALCULATION_MANUAL),
    ):
        try:
            state[name] = getattr(excel, name)
            setattr(excel, name, value)
        except Exception:
            state.pop(name, None)
    return state


def _restore_excel_batch(excel: Any, state: dict[str, Any] | None) -> None:
    if not state:
        return
    for name, value in state.items():
        try:
            setattr(excel, name, value)
        except Exception:
            continue


def _write_structured_fee_draft(
    *,
    sheet: Any,
    draft: FeeEvaluationDraft,
    prepared_by: str | None,
    approved_by: str | None,
) -> None:
    sheet.Cells(1, 1).Value = "ConnLab Generated Fee Evaluation"
    sheet.Cells(2, 1).Value = f"Project ID: {draft.header.project_id}"
    sheet.Cells(3, 1).Value = (
        f"Confirmed Matrix: {draft.header.confirmed_matrix_id} / "
        f"rev {draft.header.confirmed_revision}"
    )
    sheet.Cells(4, 1).Value = (
        f"Fee rule version: {draft.header.pricing_rule_version_id}"
    )
    sheet.Cells(5, 1).Value = (
        f"Pricing effective from: {draft.header.pricing_effective_from or ''}"
    )
    sheet.Cells(6, 1).Value = f"Prepared by: {prepared_by or ''}"
    sheet.Cells(7, 1).Value = f"Approved by: {approved_by or ''}"

    headers = (
        "Group",
        "Spend time",
        "Description",
        "Unit price",
        "Units",
        "Base fee",
        "Discount",
        "Testing fee",
        "Line ID",
        "Confirmed group ID",
        "Confirmed row ID",
        "Source row ID",
        "Matched rule ID",
        "Matched rule version ID",
        "Step tokens",
    )
    for index, header in enumerate(headers, start=1):
        sheet.Cells(9, index).Value = header

    row_index = 10
    for group in draft.groups:
        for line in group.line_items:
            sheet.Cells(row_index, 1).Value = group.group_label
            sheet.Cells(row_index, 2).Value = line.spend_time
            sheet.Cells(row_index, 3).Value = line.test_item
            sheet.Cells(row_index, 4).Value = _decimal_text(line.unit_price)
            sheet.Cells(row_index, 5).Value = _decimal_text(line.units)
            sheet.Cells(row_index, 6).Value = _decimal_text(line.base_fee)
            sheet.Cells(row_index, 7).Value = _decimal_text(line.discount_percent)
            sheet.Cells(row_index, 8).Value = _decimal_text(line.testing_fee)
            sheet.Cells(row_index, 9).Value = line.line_id
            sheet.Cells(row_index, 10).Value = line.confirmed_group_id
            sheet.Cells(row_index, 11).Value = line.confirmed_row_id
            sheet.Cells(row_index, 12).Value = line.source_row_id or ""
            sheet.Cells(row_index, 13).Value = line.matched_rule_id or ""
            sheet.Cells(row_index, 14).Value = line.matched_rule_version_id or ""
            sheet.Cells(row_index, 15).Value = ", ".join(line.step_tokens)
            row_index += 1

    sheet.Cells(row_index, 7).Value = "Total"
    sheet.Cells(row_index, 8).Value = _decimal_text(draft.total_fee)


def _write_matrix_basic_fill(
    *,
    sheet: Any,
    basic_fill: MatrixBasicFillWorkbook,
) -> None:
    report_row = _find_required_row(sheet, "Report preparation")
    condition_row = _find_required_row(sheet, "条件确认")
    total_row = _find_required_row(sheet, "Total")
    _find_required_row(sheet, "Grand Cost")
    sample_template = _capture_template_row(sheet, _DETAIL_START_ROW)
    report_template = _capture_template_row(sheet, report_row)
    condition_template = _capture_template_row(sheet, condition_row)
    ltr_number_fill = _cell_fill_color(sheet, 2, 3)
    group_fill_colors = (ltr_number_fill, _LIGHT_BLUE_FILL)
    generated_detail_count = (
        sum(1 + len(group.lines) for group in basic_fill.groups) + 2
    )
    existing_detail_count = total_row - _DETAIL_START_ROW
    if generated_detail_count > existing_detail_count:
        _insert_rows(sheet, total_row, generated_detail_count - existing_detail_count)

    row_index = _DETAIL_START_ROW
    for group_index, group in enumerate(basic_fill.groups):
        group_start = row_index
        _write_template_row(
            sheet=sheet,
            template=sample_template,
            row_index=row_index,
            overrides={
                1: _display_group_label(group.group_label),
                3: "Sample preparation(if needed)",
            },
        )
        _clear_cell_fill(sheet=sheet, row_index=row_index, column=2)
        _set_cell_fill(sheet=sheet, row_index=row_index, column=3, color=ltr_number_fill)
        row_index += 1
        for line in group.lines:
            _write_matrix_detail_row(
                sheet=sheet,
                row_index=row_index,
                description=line.test_item,
            )
            row_index += 1
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
    _clear_cell_fill(sheet=sheet, row_index=report_row_index, column=2)
    row_index += 1
    _write_template_row(
        sheet=sheet,
        template=condition_template,
        row_index=row_index,
        overrides={1: "条件确认"},
    )
    _clear_cell_fill(sheet=sheet, row_index=row_index, column=2)
    total_row_index = row_index + 1
    _write_total_formulas(
        sheet=sheet,
        total_row_index=total_row_index,
        last_detail_row=row_index,
    )
    _set_a_column_bold(sheet, _DETAIL_START_ROW, total_row_index + 2)


def _write_matrix_detail_row(
    *,
    sheet: Any,
    row_index: int,
    description: str,
) -> None:
    sheet.Cells(row_index, 1).Value = ""
    sheet.Cells(row_index, 3).Value = description
    for column in (2, 4, 5, 6, 7, 8):
        sheet.Cells(row_index, column).Value = ""
    _clear_cell_fill(sheet=sheet, row_index=row_index, column=2)
    _set_formula(sheet, row_index, 9, _detail_fee_formula(row_index))


def _display_group_label(group_label: str) -> str:
    label = group_label.strip()
    if label.lower().startswith("group "):
        return label[6:].strip()
    return label


def _capture_template_row(sheet: Any, row_index: int) -> _TemplateRow:
    cells: list[str] = []
    formula_columns: list[int] = []
    for column in range(1, 10):
        formula = _cell_formula(sheet, row_index, column)
        if formula.startswith("="):
            cells.append(formula)
            formula_columns.append(column)
        else:
            cells.append(_cell_value(sheet, row_index, column))
    return _TemplateRow(cells=tuple(cells), formula_columns=tuple(formula_columns))


def _write_template_row(
    *,
    sheet: Any,
    template: _TemplateRow,
    row_index: int,
    overrides: dict[int, str],
) -> None:
    for column, value in enumerate(template.cells, start=1):
        text = overrides.get(column, value)
        if column in template.formula_columns:
            _set_formula(sheet, row_index, column, _detail_fee_formula(row_index))
        else:
            sheet.Cells(row_index, column).Value = text


def _detail_fee_formula(row_index: int) -> str:
    return f"=D{row_index}*F{row_index}*(1-H{row_index})+G{row_index}"


def _write_total_formulas(
    *,
    sheet: Any,
    total_row_index: int,
    last_detail_row: int,
) -> None:
    _set_formula(sheet, total_row_index, 2, f"=SUM(B{_DETAIL_START_ROW}:B{last_detail_row})")
    _set_formula(sheet, total_row_index, 9, f"=SUM(I{_DETAIL_START_ROW}:I{last_detail_row})")


def _find_required_row(sheet: Any, text: str) -> int:
    for row in range(1, 201):
        for column in range(1, 10):
            if _cell_text(sheet, row, column).lower() == text.lower():
                return row
    raise ValueError(f"Testing Prices anchor was not found: {text}")


def _cell_text(sheet: Any, row: int, column: int) -> str:
    value = sheet.Cells(row, column).Value
    if value is None:
        return ""
    return str(value).strip()


def _cell_value(sheet: Any, row: int, column: int) -> str:
    value = sheet.Cells(row, column).Value
    if value is None:
        return ""
    return str(value)


def _cell_formula(sheet: Any, row: int, column: int) -> str:
    value = sheet.Cells(row, column).Formula
    if value is None:
        return ""
    return str(value)


def _set_formula(sheet: Any, row: int, column: int, formula: str) -> None:
    sheet.Cells(row, column).Formula = formula


def _insert_rows(sheet: Any, row: int, count: int) -> None:
    if count <= 0:
        return
    if hasattr(sheet, "insert_rows"):
        sheet.insert_rows(row, count)
        return
    try:
        sheet.Rows(f"{row}:{row + count - 1}").Insert()
        return
    except Exception:
        pass
    for _ in range(count):
        sheet.Rows(row).Insert()


def _set_a_column_fill(
    *,
    sheet: Any,
    start_row: int,
    end_row: int,
    color: int,
) -> None:
    if hasattr(sheet, "set_a_column_fill"):
        sheet.set_a_column_fill(start_row, end_row, color)
        return
    sheet.Range(sheet.Cells(start_row, 1), sheet.Cells(end_row, 1)).Interior.Color = color


def _cell_fill_color(sheet: Any, row: int, column: int) -> int:
    return int(sheet.Cells(row, column).Interior.Color)


def _set_cell_fill(*, sheet: Any, row_index: int, column: int, color: int) -> None:
    if hasattr(sheet, "set_cell_fill"):
        sheet.set_cell_fill(row_index, column, color)
        return
    sheet.Cells(row_index, column).Interior.Color = color


def _clear_cell_fill(*, sheet: Any, row_index: int, column: int) -> None:
    if hasattr(sheet, "clear_cell_fill"):
        sheet.clear_cell_fill(row_index, column)
        return
    cell = sheet.Cells(row_index, column)
    if hasattr(cell.Interior, "ColorIndex"):
        cell.Interior.ColorIndex = _EXCEL_LINE_STYLE_NONE
    else:
        cell.Interior.Color = _WHITE_FILL


def _set_a_column_bold(sheet: Any, start_row: int, end_row: int) -> None:
    if end_row < start_row:
        return
    if hasattr(sheet, "set_a_column_bold"):
        sheet.set_a_column_bold(start_row, end_row, True)
        return
    sheet.Range(sheet.Cells(start_row, 1), sheet.Cells(end_row, 1)).Font.Bold = True


def _apply_a_column_group_borders(sheet: Any, start_row: int, end_row: int) -> None:
    if end_row < start_row:
        return
    if hasattr(sheet, "apply_a_column_group_borders"):
        sheet.apply_a_column_group_borders(start_row, end_row)
        return
    group_range = sheet.Range(sheet.Cells(start_row, 1), sheet.Cells(end_row, 1))
    group_range.Borders(_EXCEL_EDGE_LEFT).LineStyle = _EXCEL_LINE_STYLE_CONTINUOUS
    sheet.Cells(start_row, 1).Borders(_EXCEL_EDGE_TOP).LineStyle = (
        _EXCEL_LINE_STYLE_CONTINUOUS
    )


def _save_as(workbook: Any, target: Path) -> None:
    file_format = _EXCEL_FILE_FORMATS.get(target.suffix.lower())
    if file_format is None:
        raise ValueError(f"Unsupported fee output type: {target}")
    workbook.SaveAs(str(target), FileFormat=file_format)


def _decimal_text(value: Decimal | None) -> str:
    if value is None:
        return ""
    return format(value, "f")
