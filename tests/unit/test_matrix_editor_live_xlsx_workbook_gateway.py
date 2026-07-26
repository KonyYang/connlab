from io import BytesIO

from openpyxl import load_workbook

from backend.application.matrix_editor_live_xlsx_export_service import (
    MatrixEditorLiveXlsxExportCell,
    MatrixEditorLiveXlsxExportGroup,
    MatrixEditorLiveXlsxExportProjection,
    MatrixEditorLiveXlsxExportRow,
)
from backend.infrastructure.office.matrix_editor_live_xlsx_workbook_gateway import (
    MatrixEditorLiveXlsxWorkbookGateway,
)


def test_workbook_gateway_writes_reference_layout_and_true_blank_fee_cells():
    projection = MatrixEditorLiveXlsxExportProjection(
        groups=(MatrixEditorLiveXlsxExportGroup("g1", "G1", "Group 1", "5", "2.5 d"),),
        rows=(
            MatrixEditorLiveXlsxExportRow(
                "r1", "Thermal Shock", "4", "EIA", "-40/125", "Pass",
                (MatrixEditorLiveXlsxExportCell("g1", "1"),),
            ),
        ),
    )
    content = MatrixEditorLiveXlsxWorkbookGateway().render(projection)
    workbook = load_workbook(BytesIO(content), data_only=False)
    sheet = workbook["Sheet"]
    assert sheet.max_row == 5
    assert [cell.value for cell in sheet[1]] == [
        "Test Item", "Section", "Test Method", "Condition", "Requirement", "Group 1", "Notes"
    ]
    assert [sheet.cell(row, 1).value for row in range(2, 6)] == [
        "Thermal Shock", "Sample size", "Time", "Fee"
    ]
    assert sheet["F3"].value == "5"
    assert sheet["F4"].value == "2.5 d"
    assert all(sheet.cell(5, column).value is None for column in range(2, 8))
    assert sheet["A1"].fill.fgColor.rgb == "00CCCCCC"
    assert workbook.defined_names == {}
