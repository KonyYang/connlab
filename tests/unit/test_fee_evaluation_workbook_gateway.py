from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import sys
import types

import pytest

from backend.application.confirmed_matrix_fee_draft_service import (
    FeeEvaluationDraft,
    FeeEvaluationGroup,
    FeeEvaluationHeader,
    FeeEvaluationLineItem,
)
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    MatrixBasicFillGroup,
    MatrixBasicFillHeader,
    MatrixBasicFillLine,
    MatrixBasicFillWorkbook,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedManualRow,
)
from backend.infrastructure.office.fee_evaluation_workbook_gateway import (
    FeeEvaluationWorkbookGateway,
)
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable


def test_fee_gateway_rejects_unsupported_template_type(tmp_path: Path) -> None:
    template = tmp_path / "fee.csv"
    template.write_text("x", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported fee template type"):
        FeeEvaluationWorkbookGateway().generate(
            template_path=template,
            output_path=tmp_path / "out.xls",
            preview=None,
        )


def test_fee_gateway_rejects_missing_template(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Template does not exist"):
        FeeEvaluationWorkbookGateway().generate(
            template_path=tmp_path / "missing.xls",
            output_path=tmp_path / "out.xls",
            preview=None,
        )


def test_fee_gateway_initializes_com_for_real_excel_dispatch(monkeypatch) -> None:
    calls: list[str] = []
    excel = object()
    pythoncom = types.SimpleNamespace(
        CoInitialize=lambda: calls.append("initialize"),
        CoUninitialize=lambda: calls.append("uninitialize"),
    )
    win32com_client = types.SimpleNamespace(
        DispatchEx=lambda name: calls.append(f"dispatch:{name}") or excel
    )
    monkeypatch.setitem(sys.modules, "pythoncom", pythoncom)
    monkeypatch.setitem(sys.modules, "win32com", types.SimpleNamespace(client=win32com_client))
    monkeypatch.setitem(sys.modules, "win32com.client", win32com_client)

    result, pythoncom_module = FeeEvaluationWorkbookGateway()._open_excel_application()
    pythoncom_module.CoUninitialize()

    assert result is excel
    assert calls == ["initialize", "dispatch:Excel.Application", "uninitialize"]


def test_fee_gateway_structured_writer_maps_draft_rows_to_testing_prices_sheet(
    tmp_path: Path,
) -> None:
    template = tmp_path / "fee.xls"
    template.write_text("template", encoding="utf-8")
    excel = _FakeExcel(_FakeWorkbook(sheet_names=("Testing Prices",)))
    output = tmp_path / "fee_out.xls"

    result = FeeEvaluationWorkbookGateway(
        excel_app_factory=lambda: excel
    ).generate_from_draft(
        template_path=template,
        output_path=output,
        draft=_draft(),
        prepared_by="Operator",
        approved_by="Lead",
    )

    sheet = excel.workbook.sheet
    assert result.output_path == output
    assert excel.workbook.opened_path == str(template)
    assert excel.workbook.saved_path == str(output)
    assert excel.workbook.saved_file_format == 56
    assert sheet.cells[(2, 1)] == "Project ID: P1"
    assert sheet.cells[(3, 1)] == "Confirmed Matrix: cmv-1 / rev 1"
    assert sheet.cells[(4, 1)] == "Fee rule version: fee_rules_v2026_06_03"
    assert sheet.cells[(6, 1)] == "Prepared by: Operator"
    assert sheet.cells[(7, 1)] == "Approved by: Lead"
    assert sheet.cells[(10, 1)] == "Group 1"
    assert sheet.cells[(10, 2)] == "2D"
    assert sheet.cells[(10, 3)] == "Fixture setup"
    assert sheet.cells[(10, 4)] == "100"
    assert sheet.cells[(10, 5)] == "1"
    assert sheet.cells[(10, 8)] == "100"
    assert sheet.cells[(10, 9)] == "line-1"
    assert sheet.cells[(10, 10)] == "cmg-1"
    assert sheet.cells[(10, 11)] == "cmr-1"
    assert sheet.cells[(10, 13)] == "fee_rule_fixture"
    assert sheet.cells[(10, 14)] == "fee_rules_v2026_06_03"
    assert sheet.cells[(11, 7)] == "Total"
    assert sheet.cells[(11, 8)] == "100"


def test_fee_gateway_structured_writer_rejects_missing_testing_prices_sheet(
    tmp_path: Path,
) -> None:
    template = tmp_path / "fee.xls"
    template.write_text("template", encoding="utf-8")
    excel = _FakeExcel(_FakeWorkbook(sheet_names=("Other",)))

    with pytest.raises(ValueError, match="Testing Prices"):
        FeeEvaluationWorkbookGateway(
            excel_app_factory=lambda: excel
        ).generate_from_draft(
            template_path=template,
            output_path=tmp_path / "out.xls",
            draft=_draft(),
            prepared_by="Operator",
            approved_by=None,
        )


def test_fee_gateway_structured_writer_uses_com_saveas_for_xlsx_output(
    tmp_path: Path,
) -> None:
    template = tmp_path / "fee.xls"
    template.write_text("template", encoding="utf-8")
    excel = _FakeExcel(_FakeWorkbook(sheet_names=("Testing Prices",)))
    output = tmp_path / "fee_out.xlsx"

    FeeEvaluationWorkbookGateway(
        excel_app_factory=lambda: excel
    ).generate_from_draft(
        template_path=template,
        output_path=output,
        draft=_draft(),
        prepared_by="Operator",
        approved_by=None,
    )

    assert excel.workbook.saved_path == str(output)
    assert excel.workbook.saved_file_format == 51


def test_fee_gateway_matrix_basic_fill_writes_only_a_and_c_detail_columns(
    tmp_path: Path,
) -> None:
    template = tmp_path / "fee.xls"
    template.write_text("template", encoding="utf-8")
    workbook = _FakeWorkbook(sheet_names=("Testing Prices",))
    workbook.sheet.cells[(5, 2)] = "0.5"
    workbook.sheet.cells[(5, 3)] = "Sample preparation"
    workbook.sheet.cells[(5, 5)] = "per sample"
    workbook.sheet.formulas[(5, 9)] = "=D5*F5*(1-H5)+G5"
    workbook.sheet.cell_fills[(2, 3)] = 0xD9D9D9
    workbook.sheet.cell_fills[(4, 1)] = 0xFCE4D6
    workbook.sheet.cell_fills[(5, 2)] = 65535
    workbook.sheet.cell_fills[(5, 3)] = 65535
    workbook.sheet.cells[(7, 3)] = "Report preparation"
    workbook.sheet.cells[(7, 2)] = "1"
    workbook.sheet.cells[(7, 5)] = "per report"
    workbook.sheet.formulas[(7, 9)] = "=D7*F7*(1-H7)+G7"
    workbook.sheet.cells[(8, 1)] = "条件确认"
    workbook.sheet.cells[(8, 2)] = "1"
    workbook.sheet.formulas[(8, 9)] = "=D8*F8*(1-H8)+G8"
    workbook.sheet.cells[(9, 7)] = "Total"
    workbook.sheet.cells[(11, 3)] = "Grand Cost"
    excel = _FakeExcel(workbook)
    output = tmp_path / "fee_out.xls"

    result = FeeEvaluationWorkbookGateway(
        excel_app_factory=lambda: excel
    ).generate_matrix_basic_fill(
        template_path=template,
        output_path=output,
        basic_fill=_basic_fill(),
        review_required=True,
        prepared_by="Operator",
        approved_by=None,
    )

    sheet = excel.workbook.sheet
    assert result.output_path == output
    assert sheet.cells[(5, 1)] == "1"
    assert sheet.cells[(5, 3)] == "Sample preparation"
    assert sheet.cells[(5, 2)] == "0"
    assert sheet.cells[(5, 4)] == "0"
    assert sheet.cells[(5, 5)] == "per sample"
    assert sheet.cells[(5, 6)] == "1"
    assert sheet.cells[(5, 7)] == "0"
    assert sheet.cells[(5, 8)] == "0"
    assert sheet.formulas[(5, 9)] == "=D5*F5*(1-H5)+G5"
    assert sheet.cells[(6, 1)] == ""
    assert sheet.cells[(6, 3)] == "Visual Examination"
    assert sheet.formulas[(6, 9)] == "=D6*F6*(1-H6)+G6"
    assert sheet.cells[(7, 1)] == ""
    assert sheet.cells[(7, 3)] == "LLCR"
    assert sheet.formulas[(7, 9)] == "=D7*F7*(1-H7)+G7"
    assert sheet.cells[(8, 1)] == "2"
    assert sheet.cells[(8, 3)] == "Sample preparation"
    assert sheet.cells[(8, 2)] == "0"
    assert sheet.cells[(8, 4)] == "0"
    assert sheet.cells[(8, 5)] == "per sample"
    assert sheet.cells[(8, 6)] == "1"
    assert sheet.cells[(8, 7)] == "0"
    assert sheet.cells[(8, 8)] == "0"
    assert sheet.formulas[(8, 9)] == "=D8*F8*(1-H8)+G8"
    assert sheet.cells[(9, 1)] == ""
    assert sheet.cells[(9, 3)] == "Dust Test"
    assert sheet.formulas[(9, 9)] == "=D9*F9*(1-H9)+G9"
    assert sheet.cells[(10, 3)] == "Report preparation"
    assert sheet.cells[(10, 2)] == "1"
    assert sheet.cells[(10, 5)] == "per report"
    assert sheet.formulas[(10, 9)] == "=D10*F10*(1-H10)+G10"
    assert sheet.cells[(11, 1)] == "条件确认"
    assert sheet.cells[(11, 2)] == "1"
    assert sheet.formulas[(11, 9)] == "=D11*F11*(1-H11)+G11"
    assert sheet.formulas[(12, 2)] == "=SUM(B5:B11)"
    assert sheet.formulas[(12, 9)] == "=SUM(I5:I11)"
    assert sheet.cells[(6, 2)] == ""
    assert sheet.cells[(6, 4)] == ""
    assert sheet.cells[(6, 9)] == "0.0"
    assert sheet.merged_ranges == []
    assert sheet.a_column_border_cleared_ranges == []
    assert sheet.a_column_group_borders == [(5, 7), (8, 9)]
    assert sheet.a_column_fills[(5, 7)] == 0xD9D9D9
    assert sheet.a_column_fills[(8, 9)] == 0xDDEBF7
    assert sheet.cell_fills[(5, 3)] == sheet.cell_fills[(8, 3)] == 0xD9D9D9
    assert (5, 2) not in sheet.cell_fills
    assert (6, 2) not in sheet.cell_fills
    assert (7, 2) not in sheet.cell_fills
    assert (8, 2) not in sheet.cell_fills
    assert (9, 2) not in sheet.cell_fills
    assert (10, 2) not in sheet.cell_fills
    assert (11, 2) not in sheet.cell_fills
    assert sheet.a_column_bold_ranges == [(5, 14)]
    assert "Matrix basic fill only." in result.warnings


def test_fee_gateway_matrix_basic_fill_batches_unedited_row_segments(
    tmp_path: Path,
) -> None:
    template = tmp_path / "fee.xls"
    template.write_text("template", encoding="utf-8")
    workbook = _FakeWorkbook(sheet_names=("Testing Prices",))
    workbook.sheet.cells[(5, 3)] = "Sample preparation"
    workbook.sheet.formulas[(5, 9)] = "=D5*F5*(1-H5)+G5"
    workbook.sheet.cells[(7, 3)] = "Report preparation"
    workbook.sheet.formulas[(7, 9)] = "=D7*F7*(1-H7)+G7"
    workbook.sheet.cells[(8, 1)] = "条件确认"
    workbook.sheet.formulas[(8, 9)] = "=D8*F8*(1-H8)+G8"
    workbook.sheet.cells[(9, 7)] = "Total"
    workbook.sheet.cells[(11, 3)] = "Grand Cost"
    excel = _FakeExcel(workbook)
    output = tmp_path / "fee_out.xls"

    FeeEvaluationWorkbookGateway(
        excel_app_factory=lambda: excel
    ).generate_matrix_basic_fill(
        template_path=template,
        output_path=output,
        basic_fill=_basic_fill(),
        review_required=False,
        prepared_by="Operator",
        approved_by=None,
    )

    sheet = excel.workbook.sheet
    assert sheet.row_value_writes <= 4
    assert sheet.block_value_writes >= 1
    assert sheet.cell_value_writes < 20


def test_fee_gateway_matrix_basic_fill_uses_cached_anchor_snapshot(
    tmp_path: Path,
) -> None:
    template = tmp_path / "fee.xls"
    template.write_text("template", encoding="utf-8")
    workbook = _FakeWorkbook(sheet_names=("Testing Prices",))
    workbook.sheet.cells[(2, 3)] = "LTR Number"
    workbook.sheet.cells[(2, 6)] = "Test Description"
    workbook.sheet.cells[(3, 3)] = "Requestor"
    workbook.sheet.cells[(3, 6)] = "Site"
    workbook.sheet.cells[(5, 3)] = "Sample preparation"
    workbook.sheet.formulas[(5, 9)] = "=D5*F5*(1-H5)+G5"
    workbook.sheet.cells[(7, 3)] = "Report preparation"
    workbook.sheet.formulas[(7, 9)] = "=D7*F7*(1-H7)+G7"
    workbook.sheet.cells[(8, 1)] = "条件确认"
    workbook.sheet.formulas[(8, 9)] = "=D8*F8*(1-H8)+G8"
    workbook.sheet.cells[(9, 7)] = "Total"
    workbook.sheet.cells[(10, 1)] = "External Cost"
    workbook.sheet.cells[(11, 3)] = "Grand Cost"
    excel = _FakeExcel(workbook)

    FeeEvaluationWorkbookGateway(
        excel_app_factory=lambda: excel
    ).generate_matrix_basic_fill(
        template_path=template,
        output_path=tmp_path / "fee_out.xls",
        basic_fill=_basic_fill(),
        review_required=False,
        prepared_by="Operator",
        approved_by=None,
        basic_information_values={
            "dl_number": "DL-BI",
            "product_description": "Connector from Basic Information",
            "test_item": "Qualification test",
            "requested_by": "Requester BI",
            "location": "Dongguan",
        },
    )

    sheet = excel.workbook.sheet
    assert sheet.range_value_reads == 1
    assert sheet.cell_value_reads < 40


def test_fee_gateway_matrix_basic_fill_does_not_clear_blank_comments(
    tmp_path: Path,
) -> None:
    template = tmp_path / "fee.xls"
    template.write_text("template", encoding="utf-8")
    workbook = _FakeWorkbook(sheet_names=("Testing Prices",))
    workbook.sheet.cells[(5, 3)] = "Sample preparation"
    workbook.sheet.formulas[(5, 9)] = "=D5*F5*(1-H5)+G5"
    workbook.sheet.cells[(7, 3)] = "Report preparation"
    workbook.sheet.formulas[(7, 9)] = "=D7*F7*(1-H7)+G7"
    workbook.sheet.cells[(8, 1)] = "条件确认"
    workbook.sheet.formulas[(8, 9)] = "=D8*F8*(1-H8)+G8"
    workbook.sheet.cells[(9, 7)] = "Total"
    workbook.sheet.cells[(11, 3)] = "Grand Cost"
    excel = _FakeExcel(workbook)

    FeeEvaluationWorkbookGateway(
        excel_app_factory=lambda: excel
    ).generate_matrix_basic_fill(
        template_path=template,
        output_path=tmp_path / "fee_out.xls",
        basic_fill=_basic_fill(),
        review_required=False,
        prepared_by="Operator",
        approved_by=None,
    )

    assert excel.workbook.sheet.comment_clear_calls == 0


def test_fee_gateway_matrix_basic_fill_writes_basic_information_identity(
    tmp_path: Path,
) -> None:
    template = tmp_path / "fee.xls"
    template.write_text("template", encoding="utf-8")
    workbook = _FakeWorkbook(sheet_names=("Testing Prices",))
    workbook.sheet.cells[(2, 3)] = "LTR Number"
    workbook.sheet.cells[(2, 6)] = "Test Description"
    workbook.sheet.cells[(3, 3)] = "Requestor"
    workbook.sheet.cells[(3, 6)] = "Site"
    workbook.sheet.cells[(5, 2)] = "0.5"
    workbook.sheet.cells[(5, 3)] = "Sample preparation"
    workbook.sheet.cells[(5, 5)] = "per sample"
    workbook.sheet.formulas[(5, 9)] = "=D5*F5*(1-H5)+G5"
    workbook.sheet.cells[(7, 3)] = "Report preparation"
    workbook.sheet.cells[(8, 1)] = "条件确认"
    workbook.sheet.cells[(9, 7)] = "Total"
    workbook.sheet.cells[(11, 3)] = "Grand Cost"
    excel = _FakeExcel(workbook)
    output = tmp_path / "fee_out.xls"

    FeeEvaluationWorkbookGateway(
        excel_app_factory=lambda: excel
    ).generate_matrix_basic_fill(
        template_path=template,
        output_path=output,
        basic_fill=_basic_fill(),
        review_required=False,
        prepared_by="Operator",
        approved_by=None,
        basic_information_values={
            "dl_number": "DL-BI",
            "product_description": "Connector from Basic Information",
            "test_item": "Qualification test",
            "requested_by": "Requester BI",
            "location": "Dongguan",
            "lab_performing_tests": "Dongguan Lab",
        },
    )

    sheet = excel.workbook.sheet
    assert sheet.cells[(2, 3)] == "LTR Number"
    assert sheet.cells[(2, 4)] == "DL-BI"
    assert sheet.cells[(2, 6)] == "Test Description"
    assert sheet.cells[(2, 7)] == "Connector from Basic Information Qualification test"
    assert sheet.cells[(3, 3)] == "Requestor"
    assert sheet.cells[(3, 4)] == "Requester BI"
    assert sheet.cells[(3, 6)] == "Site"
    assert sheet.cells[(3, 7)] == "Dongguan"
    assert (2, 1) not in sheet.cells
    assert (3, 1) not in sheet.cells
    assert (4, 1) not in sheet.cells
    assert excel.workbook.open_count == 1
    assert excel.workbook.save_count == 1
    assert excel.quit is True


def test_fee_gateway_matrix_basic_fill_writes_edited_values_and_notes(
    tmp_path: Path,
) -> None:
    template = tmp_path / "fee.xls"
    template.write_text("template", encoding="utf-8")
    workbook = _FakeWorkbook(sheet_names=("Testing Prices",))
    workbook.sheet.cells[(5, 3)] = "Sample preparation"
    workbook.sheet.formulas[(5, 9)] = "=D5*F5*(1-H5)+G5"
    workbook.sheet.cell_fills[(2, 3)] = 0xD9D9D9
    workbook.sheet.cells[(7, 3)] = "Report preparation"
    workbook.sheet.formulas[(7, 9)] = "=D7*F7*(1-H7)+G7"
    workbook.sheet.cells[(8, 1)] = "条件确认"
    workbook.sheet.formulas[(8, 9)] = "=D8*F8*(1-H8)+G8"
    workbook.sheet.cells[(9, 7)] = "Total"
    workbook.sheet.cells[(10, 1)] = "External Cost"
    workbook.sheet.formulas[(10, 9)] = "=D10"
    workbook.sheet.cells[(11, 3)] = "Grand Cost"
    excel = _FakeExcel(workbook)
    output = tmp_path / "fee_out.xls"

    result = FeeEvaluationWorkbookGateway(
        excel_app_factory=lambda: excel
    ).generate_matrix_basic_fill(
        template_path=template,
        output_path=output,
        basic_fill=_basic_fill(),
        review_required=False,
        prepared_by="Operator",
        approved_by=None,
        edited_values=_edited_values(),
    )

    sheet = excel.workbook.sheet
    assert result.output_path == output
    assert sheet.cells[(5, 2)] == "0.25"
    assert sheet.cells[(5, 4)] == "15"
    assert sheet.cells[(5, 5)] == "per sample"
    assert sheet.cells[(5, 6)] == "5"
    assert sheet.cells[(5, 7)] == "2"
    assert sheet.cells[(5, 8)] == "0.05"
    assert sheet.formulas[(5, 9)] == "=D5*F5*(1-H5)+G5"
    assert sheet.comments[(5, 9)] == "sample prep note"
    assert sheet.cells[(6, 2)] == "1.5"
    assert sheet.cells[(6, 3)] == "Visual Examination"
    assert sheet.cells[(6, 4)] == "20"
    assert sheet.cells[(6, 5)] == "per sample"
    assert sheet.cells[(6, 6)] == "2"
    assert sheet.cells[(6, 7)] == "5"
    assert sheet.cells[(6, 8)] == "0.1"
    assert sheet.formulas[(6, 9)] == "=D6*F6*(1-H6)+G6"
    assert sheet.comments[(6, 9)] == "discount approved"
    assert (7, 9) not in sheet.comments
    assert sheet.comment_clear_calls == 0
    assert sheet.cells[(10, 2)] == "0.75"
    assert sheet.cells[(10, 4)] == "100"
    assert sheet.cells[(10, 5)] == "per report"
    assert sheet.cells[(10, 6)] == "1"
    assert sheet.cells[(10, 7)] == "0"
    assert sheet.cells[(10, 8)] == "0"
    assert sheet.comments[(10, 9)] == "report note"
    assert sheet.cells[(11, 2)] == "0.5"
    assert sheet.cells[(13, 4)] == "150"
    assert sheet.formulas[(13, 9)] == "=D10"
    assert (13, 9) not in sheet.cells
    assert sheet.comments[(13, 4)] == "external tooling"
    assert sheet.block_value_writes >= 1
    assert sheet.formula_block_writes >= 1
    assert sheet.row_value_writes <= 6
    assert sheet.cell_value_writes <= 4


def test_fee_gateway_matrix_basic_fill_warns_when_note_comment_fails(
    tmp_path: Path,
) -> None:
    template = tmp_path / "fee.xls"
    template.write_text("template", encoding="utf-8")
    workbook = _FakeWorkbook(sheet_names=("Testing Prices",))
    workbook.sheet.cells[(5, 3)] = "Sample preparation"
    workbook.sheet.formulas[(5, 9)] = "=D5*F5*(1-H5)+G5"
    workbook.sheet.cells[(7, 3)] = "Report preparation"
    workbook.sheet.formulas[(7, 9)] = "=D7*F7*(1-H7)+G7"
    workbook.sheet.cells[(8, 1)] = "条件确认"
    workbook.sheet.formulas[(8, 9)] = "=D8*F8*(1-H8)+G8"
    workbook.sheet.cells[(9, 7)] = "Total"
    workbook.sheet.cells[(10, 1)] = "External Cost"
    workbook.sheet.cells[(11, 3)] = "Grand Cost"
    workbook.sheet.comment_failures.update({(6, 9), (13, 4)})
    excel = _FakeExcel(workbook)
    output = tmp_path / "fee_out.xls"

    result = FeeEvaluationWorkbookGateway(
        excel_app_factory=lambda: excel
    ).generate_matrix_basic_fill(
        template_path=template,
        output_path=output,
        basic_fill=_basic_fill(),
        review_required=False,
        prepared_by="Operator",
        approved_by=None,
        edited_values=_edited_values(),
    )

    assert any("Fee row note for Group 1 step -" in warning for warning in result.warnings)
    assert any("External Cost note was not exported" in warning for warning in result.warnings)
    assert (6, 9) not in excel.workbook.sheet.comments
    assert (13, 4) not in excel.workbook.sheet.comments


def test_fee_gateway_structured_writer_reports_unavailable_com(
    tmp_path: Path,
) -> None:
    template = tmp_path / "fee.xls"
    template.write_text("template", encoding="utf-8")

    def unavailable() -> object:
        raise OfficeAutomationUnavailable("Excel COM automation is unavailable.")

    with pytest.raises(OfficeAutomationUnavailable, match="unavailable"):
        FeeEvaluationWorkbookGateway(
            excel_app_factory=unavailable
        ).generate_from_draft(
            template_path=template,
            output_path=tmp_path / "out.xls",
            draft=_draft(),
            prepared_by="Operator",
            approved_by=None,
        )


def _basic_fill() -> MatrixBasicFillWorkbook:
    return MatrixBasicFillWorkbook(
        header=MatrixBasicFillHeader(
            project_id="P1",
            confirmed_matrix_id="cmv-1",
            confirmed_revision=1,
            generated_at="2026-06-05T10:00:00+08:00",
        ),
        status="ready",
        groups=(
            MatrixBasicFillGroup(
                group_key="g1",
                group_label="Group 1",
                confirmed_group_id="cmg-1",
                sample_quantity_expression="5",
                lines=(
                    MatrixBasicFillLine(
                        line_id="cmv-1:g1:cmr-visual",
                        group_key="g1",
                        group_label="Group 1",
                        confirmed_group_id="cmg-1",
                        confirmed_row_id="cmr-visual",
                        source_row_id="smr-visual",
                        row_order=1,
                        step_index=0,
                        test_item="Visual Examination",
                        cell_value="1 X",
                        step_tokens=(),
                    ),
                    MatrixBasicFillLine(
                        line_id="cmv-1:g1:cmr-llcr",
                        group_key="g1",
                        group_label="Group 1",
                        confirmed_group_id="cmg-1",
                        confirmed_row_id="cmr-llcr",
                        source_row_id="smr-llcr",
                        row_order=2,
                        step_index=0,
                        test_item="LLCR",
                        cell_value="abc",
                        step_tokens=(),
                    ),
                ),
            ),
            MatrixBasicFillGroup(
                group_key="g2",
                group_label="Group 2",
                confirmed_group_id="cmg-2",
                sample_quantity_expression="3",
                lines=(
                    MatrixBasicFillLine(
                        line_id="cmv-1:g2:cmr-dust",
                        group_key="g2",
                        group_label="Group 2",
                        confirmed_group_id="cmg-2",
                        confirmed_row_id="cmr-dust",
                        source_row_id="smr-dust",
                        row_order=3,
                        step_index=0,
                        test_item="Dust Test",
                        cell_value="1",
                        step_tokens=(),
                    ),
                ),
            ),
        ),
    )


def _edited_values() -> FeeEvaluationEditedExportValues:
    return FeeEvaluationEditedExportValues(
        rows=(
            FeeEvaluationEditedExportRow(
                source_line_id="cmv-1:g1:cmr-visual",
                confirmed_group_id="cmg-1",
                confirmed_row_id="cmr-visual",
                step_token="",
                step_index=0,
                spend_time="1.5",
                unit_price="20",
                unit_type="per sample",
                units="2",
                base_fee="5",
                discount="10%",
                testing_fee="41",
                notes="discount approved",
            ),
            FeeEvaluationEditedExportRow(
                source_line_id="cmv-1:g1:cmr-llcr",
                confirmed_group_id="cmg-1",
                confirmed_row_id="cmr-llcr",
                step_token="",
                step_index=0,
                spend_time="0",
                unit_price="0",
                unit_type="per reading",
                units="1",
                base_fee="0",
                discount="0%",
                testing_fee="0",
                notes="",
            ),
        ),
        manual_rows=(
            FeeEvaluationEditedManualRow(
                row_kind="sample_preparation",
                confirmed_group_id="cmg-1",
                group_key="g1",
                group_label="Group 1",
                spend_time="0.25",
                unit_price="15",
                unit_type="per sample",
                units="5",
                base_fee="2",
                discount="5%",
                testing_fee="73.25",
                notes="sample prep note",
            ),
            FeeEvaluationEditedManualRow(
                row_kind="report_preparation",
                spend_time="0.75",
                unit_price="100",
                unit_type="per report",
                units="1",
                base_fee="0",
                discount="0%",
                testing_fee="100",
                notes="report note",
            ),
        ),
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time="0.5",
            external_cost="150",
            external_cost_note="external tooling",
            lab_manpower_hourly_rate="200",
        ),
    )


def _draft() -> FeeEvaluationDraft:
    line = FeeEvaluationLineItem(
        line_id="line-1",
        status="calculated",
        review_required=False,
        review_reason=None,
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        group_key="g1",
        group_label="Group 1",
        confirmed_group_id="cmg-1",
        sample_quantity_expression="1",
        spend_time="2D",
        confirmed_row_id="cmr-1",
        source_row_id="smr-1",
        row_order=1,
        test_item="Fixture setup",
        section="6.1",
        method="Fixture",
        condition="",
        requirement="",
        step_tokens=("1",),
        matched_rule_id="fee_rule_fixture",
        matched_rule_version_id="fee_rules_v2026_06_03",
        matched_rule_name="Fixture setup",
        match_reason="exact",
        calculation_strategy="fixed_per_group",
        unit_label="group",
        unit_price=Decimal("100"),
        units=Decimal("1"),
        base_fee=Decimal("0"),
        discount_percent=Decimal("0"),
        testing_fee=Decimal("100"),
        warnings=(),
    )
    return FeeEvaluationDraft(
        header=FeeEvaluationHeader(
            project_id="P1",
            confirmed_matrix_id="cmv-1",
            confirmed_revision=1,
            pricing_rule_version_id="fee_rules_v2026_06_03",
            pricing_source_file_name="Testing Fee Evaluation-Even.xls",
            pricing_source_hash="sha256:abc",
            pricing_effective_from="2026-06-03",
            generated_at="2026-06-04T10:00:00+08:00",
        ),
        draft_status="ready",
        total_fee=Decimal("100"),
        review_required_count=0,
        groups=(
            FeeEvaluationGroup(
                group_key="g1",
                group_label="Group 1",
                sample_quantity_expression="1",
                line_items=(line,),
            ),
        ),
        warnings=(),
    )


class _FakeCell:
    def __init__(self, sheet: "_FakeSheet", row: int, column: int) -> None:
        self._sheet = sheet
        self._row = row
        self._column = column

    @property
    def Value(self) -> str | None:
        self._sheet.cell_value_reads += 1
        return self._sheet.cells.get((self._row, self._column))

    @Value.setter
    def Value(self, value: object) -> None:
        self._sheet.cell_value_writes += 1
        self._sheet.cells[(self._row, self._column)] = "" if value is None else str(value)

    @property
    def Formula(self) -> str | None:
        return self._sheet.formulas.get((self._row, self._column), self.Value)

    @Formula.setter
    def Formula(self, value: object) -> None:
        text = "" if value is None else str(value)
        self._sheet.formulas[(self._row, self._column)] = text
        self._sheet.cells[(self._row, self._column)] = "0.0" if text.startswith("=") else text

    @property
    def Interior(self) -> "_FakeInterior":
        return _FakeInterior(self._sheet, self._row, self._column)

    def ClearComments(self) -> None:
        self._sheet.comment_clear_calls += 1
        self._sheet.comments.pop((self._row, self._column), None)

    def AddComment(self, text: str) -> None:
        if (self._row, self._column) in self._sheet.comment_failures:
            raise RuntimeError("comment failed")
        self._sheet.comments[(self._row, self._column)] = text


class _FakeInterior:
    def __init__(self, sheet: "_FakeSheet", row: int, column: int) -> None:
        self._sheet = sheet
        self._row = row
        self._column = column

    @property
    def Color(self) -> int:
        return self._sheet.cell_fills.get((self._row, self._column), 16777215)

    @Color.setter
    def Color(self, value: int) -> None:
        self._sheet.cell_fills[(self._row, self._column)] = value


class _FakeSheet:
    def __init__(self) -> None:
        self.cells: dict[tuple[int, int], str] = {}
        self.formulas: dict[tuple[int, int], str] = {}
        self.cell_fills: dict[tuple[int, int], int] = {}
        self.merged_ranges: list[tuple[int, int, int, int]] = []
        self.a_column_fills: dict[tuple[int, int], int] = {}
        self.a_column_border_cleared_ranges: list[tuple[int, int]] = []
        self.a_column_group_borders: list[tuple[int, int]] = []
        self.a_column_bold_ranges: list[tuple[int, int]] = []
        self.comments: dict[tuple[int, int], str] = {}
        self.comment_failures: set[tuple[int, int]] = set()
        self.cell_value_writes = 0
        self.cell_value_reads = 0
        self.range_value_reads = 0
        self.row_value_writes = 0
        self.block_value_writes = 0
        self.formula_block_writes = 0
        self.comment_clear_calls = 0

    def Cells(self, row: int, column: int) -> _FakeCell:
        return _FakeCell(self, row, column)

    def Range(self, start: _FakeCell, end: _FakeCell) -> "_FakeRange":
        return _FakeRange(
            self,
            start._row,
            start._column,
            end._row,
            end._column,
        )

    def set_row_values(
        self,
        row: int,
        start_column: int,
        values: tuple[object | None, ...],
    ) -> None:
        self.row_value_writes += 1
        for offset, value in enumerate(values):
            self.cells[(row, start_column + offset)] = "" if value is None else str(value)

    def set_block_values(
        self,
        start_row: int,
        start_column: int,
        rows: tuple[tuple[object | None, ...], ...],
    ) -> None:
        self.block_value_writes += 1
        for row_offset, values in enumerate(rows):
            for column_offset, value in enumerate(values):
                self.cells[(start_row + row_offset, start_column + column_offset)] = (
                    "" if value is None else str(value)
                )

    def clear_cell_fill_range(self, start_row: int, end_row: int, column: int) -> None:
        for row in range(start_row, end_row + 1):
            self.cell_fills.pop((row, column), None)

    def set_formula_block(
        self,
        start_row: int,
        column: int,
        formulas: tuple[str, ...],
    ) -> None:
        self.formula_block_writes += 1
        for row_offset, formula in enumerate(formulas):
            row = start_row + row_offset
            self.formulas[(row, column)] = formula
            self.cells[(row, column)] = "0.0" if formula.startswith("=") else formula

    def insert_rows(self, row: int, count: int) -> None:
        shifted: dict[tuple[int, int], str] = {}
        for (cell_row, column), value in self.cells.items():
            shifted[(cell_row + count if cell_row >= row else cell_row, column)] = value
        self.cells = shifted
        shifted_formulas: dict[tuple[int, int], str] = {}
        for (cell_row, column), value in self.formulas.items():
            shifted_formulas[(cell_row + count if cell_row >= row else cell_row, column)] = value
        self.formulas = shifted_formulas
        shifted_fills: dict[tuple[int, int], int] = {}
        for (cell_row, column), value in self.cell_fills.items():
            shifted_fills[(cell_row + count if cell_row >= row else cell_row, column)] = value
        self.cell_fills = shifted_fills
        shifted_comments: dict[tuple[int, int], str] = {}
        for (cell_row, column), value in self.comments.items():
            shifted_comments[(cell_row + count if cell_row >= row else cell_row, column)] = value
        self.comments = shifted_comments

    def set_a_column_fill(self, start_row: int, end_row: int, color: int) -> None:
        self.a_column_fills[(start_row, end_row)] = color

    def clear_a_column_borders(self, start_row: int, end_row: int) -> None:
        self.a_column_border_cleared_ranges.append((start_row, end_row))

    def set_cell_fill(self, row: int, column: int, color: int) -> None:
        self.cell_fills[(row, column)] = color

    def clear_cell_fill(self, row: int, column: int) -> None:
        self.cell_fills.pop((row, column), None)

    def set_a_column_bold(self, start_row: int, end_row: int, bold: bool) -> None:
        if bold:
            self.a_column_bold_ranges.append((start_row, end_row))

    def apply_a_column_group_borders(self, start_row: int, end_row: int) -> None:
        self.a_column_group_borders.append((start_row, end_row))

    def set_cell_comment(self, row: int, column: int, text: str) -> None:
        if text and (row, column) in self.comment_failures:
            raise RuntimeError("comment failed")
        if text:
            self.comments[(row, column)] = text
        else:
            self.comment_clear_calls += 1
            self.comments.pop((row, column), None)


class _FakeRange:
    def __init__(
        self,
        sheet: _FakeSheet,
        start_row: int,
        start_column: int,
        end_row: int,
        end_column: int,
    ) -> None:
        self._sheet = sheet
        self._start_row = start_row
        self._start_column = start_column
        self._end_row = end_row
        self._end_column = end_column

    @property
    def Value(self) -> tuple[tuple[str | None, ...], ...]:
        self._sheet.range_value_reads += 1
        return tuple(
            tuple(
                self._sheet.cells.get((row, column))
                for column in range(self._start_column, self._end_column + 1)
            )
            for row in range(self._start_row, self._end_row + 1)
        )

    @Value.setter
    def Value(self, values: tuple[tuple[object | None, ...], ...]) -> None:
        for row_offset, row_values in enumerate(values):
            for column_offset, value in enumerate(row_values):
                self._sheet.cell_value_writes += 1
                self._sheet.cells[
                    (self._start_row + row_offset, self._start_column + column_offset)
                ] = "" if value is None else str(value)

    @property
    def Formula(self) -> tuple[tuple[str | None, ...], ...]:
        return tuple(
            tuple(
                self._sheet.formulas.get(
                    (row, column), self._sheet.cells.get((row, column))
                )
                for column in range(self._start_column, self._end_column + 1)
            )
            for row in range(self._start_row, self._end_row + 1)
        )


class _FakeWorksheets:
    def __init__(self, names: tuple[str, ...], sheet: _FakeSheet) -> None:
        self._names = names
        self._sheet = sheet

    def Item(self, key: object) -> _FakeSheet:
        if key == "Testing Prices" and "Testing Prices" in self._names:
            return self._sheet
        if isinstance(key, int) and 1 <= key <= len(self._names):
            return self._sheet
        raise RuntimeError(f"Sheet not found: {key}")


class _FakeWorkbook:
    def __init__(self, sheet_names: tuple[str, ...]) -> None:
        self.sheet = _FakeSheet()
        self.Worksheets = _FakeWorksheets(sheet_names, self.sheet)
        self.opened_path: str | None = None
        self.saved_path: str | None = None
        self.saved_file_format: int | None = None
        self.open_count = 0
        self.save_count = 0
        self.closed = False

    def SaveAs(self, path: str, FileFormat: int | None = None) -> None:
        self.save_count += 1
        self.saved_path = path
        self.saved_file_format = FileFormat

    def Close(self, SaveChanges: bool = False) -> None:
        self.closed = True


class _FakeWorkbooks:
    def __init__(self, workbook: _FakeWorkbook) -> None:
        self._workbook = workbook

    def Open(self, path: str) -> _FakeWorkbook:
        self._workbook.open_count += 1
        self._workbook.opened_path = path
        return self._workbook


class _FakeExcel:
    def __init__(self, workbook: _FakeWorkbook) -> None:
        self.workbook = workbook
        self.Workbooks = _FakeWorkbooks(workbook)
        self.Visible = True
        self.DisplayAlerts = True
        self.quit = False

    def Quit(self) -> None:
        self.quit = True
