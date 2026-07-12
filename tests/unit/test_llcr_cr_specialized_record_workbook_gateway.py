from __future__ import annotations

from dataclasses import replace

from openpyxl import load_workbook

from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordProjection,
    LlcrCrRecordRow,
    LlcrCrRecordSection,
)
from backend.infrastructure.office.llcr_cr_specialized_record_workbook_gateway import (
    LlcrCrSpecializedRecordWorkbookGateway,
)


def test_gateway_writes_fixed_macro_free_sheets_blocks_and_guarded_formulas(tmp_path) -> None:
    output_path = tmp_path / "llcr-record.xlsx"
    gateway = LlcrCrSpecializedRecordWorkbookGateway()

    written = gateway.write(output_path=output_path, projection=_projection())

    assert written == output_path
    assert output_path.suffix == ".xlsx"
    workbook = load_workbook(output_path, data_only=False, keep_vba=False)
    assert workbook.sheetnames == ["Record Summary", "LLCR Record", "CR Record"]
    summary = workbook["Record Summary"]
    assert summary["A1"].value == "LLCR/CR Specialized Record Workbook"
    assert [summary.cell(8, column).value for column in range(1, 8)] == [
        "Type",
        "Group",
        "Source Step",
        "Samples",
        "Readings / sample",
        "Generated rows",
        "Status",
    ]
    sheet = workbook["LLCR Record"]
    assert [sheet.cell(3, column).value for column in range(1, 12)] == [
        "Type",
        "Group",
        "Source Step",
        "Sample",
        "Contact ID",
        "Contact Label",
        "Initial",
        "After",
        "Final",
        "Result",
        "Remarks",
    ]
    assert sheet["E4"].value == "SIG1"
    assert sheet["G6"].value == '=IF(COUNT(G4:G5)=0,"",AVERAGE(G4:G5))'
    assert sheet["H6"].value == '=IF(COUNT(H4:H5)=0,"",AVERAGE(H4:H5))'
    assert sheet["I6"].value == '=IF(COUNT(I4:I5)=0,"",AVERAGE(I4:I5))'
    assert sheet["J6"].value == '=IF(COUNTA(J4:J5)=0,"",COUNTIF(J4:J5,"PASS")&"/"&COUNTA(J4:J5))'


def test_gateway_marks_partial_compatible_confirmed_measurement_plan_metadata(tmp_path) -> None:
    output_path = tmp_path / "partial-record.xlsx"
    projection = replace(
        _projection(),
        status="partial_compatible",
        measurement_plan_revision_id="revision-3",
        measurement_plan_revision_sequence=3,
        effective_measurement_plan_status="partial_compatible",
    )

    LlcrCrSpecializedRecordWorkbookGateway().write(
        output_path=output_path,
        projection=projection,
    )

    summary = load_workbook(output_path, data_only=False)["Record Summary"]
    assert summary["B7"].value == "PARTIAL COMPATIBLE"
    assert summary["E3"].value == "revision-3"
    assert summary["E4"].value == 3
    assert summary["E5"].value == "partial_compatible"


def _projection() -> LlcrCrRecordProjection:
    section = LlcrCrRecordSection(
        record_type="llcr",
        confirmed_group_id="group-1",
        confirmed_row_id="row-1",
        step_sequence=2,
        step_suffix_note="",
        group_label="Group 1",
        source_step="2",
        sample_count=1,
        readings_per_sample=2,
        rows=(
            LlcrCrRecordRow(sample_index=1, contact_id="SIG1", contact_label="Signal contact"),
            LlcrCrRecordRow(sample_index=1, contact_id="SIG2", contact_label="Signal contact"),
        ),
    )
    return LlcrCrRecordProjection(
        project_id="project-1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=4,
        status="ready",
        sections=(section,),
        diagnostics=(),
        preview_fingerprint="fingerprint",
    )
