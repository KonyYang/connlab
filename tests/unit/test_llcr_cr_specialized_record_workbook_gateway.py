from __future__ import annotations

from dataclasses import replace

from openpyxl import load_workbook

from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordProjection,
    LlcrCrRecordRow,
    LlcrCrRecordSection,
    LlcrCrRecordStage,
)
from backend.infrastructure.office.llcr_cr_specialized_record_workbook_gateway import (
    LlcrCrSpecializedRecordWorkbookGateway,
)


def test_gateway_writes_one_llcr_file_with_shared_category_correction_and_delta_formulas(tmp_path) -> None:
    output_path = tmp_path / "llcr-record.xlsx"
    gateway = LlcrCrSpecializedRecordWorkbookGateway()

    written = gateway.write(output_path=output_path, projection=_projection())

    assert written == output_path
    assert output_path.suffix == ".xlsx"
    workbook = load_workbook(output_path, data_only=False, keep_vba=False)
    assert workbook.sheetnames == ["Record Summary", "SIG"]
    summary = workbook["Record Summary"]
    assert summary["A1"].value == "LLCR Test Record"
    assert [summary.cell(10, column).value for column in range(1, 8)] == [
        "Type",
        "Point category",
        "Group",
        "Samples",
        "Points / sample",
        "Stages",
        "Generated rows",
    ]
    sheet = workbook["SIG"]
    assert sheet["A8"].value == "Point ID"
    assert sheet["B8"].value == "Bulk Resistance (mΩ)"
    assert sheet["A9"].value == "SIG1"
    assert sheet["A10"].value == "SIG2"
    assert sheet["B9"].value is None
    assert sheet["E17"].value == '=IF(OR(D17="",NOT(COUNTIFS($A$9:$A$10,$B17,$B$9:$B$10,"<>")>0)),"",D17-VLOOKUP($B17,$A$9:$B$10,2,FALSE))'
    assert sheet["H17"].value == '=IF(OR(G17="",E17=""),"",G17-E17)'


def test_gateway_records_confirmed_point_profile_lineage(tmp_path) -> None:
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
    assert summary["B6"].value == "profile-1"
    assert summary["B7"].value == 2


def test_gateway_writes_cr_bulk_voltage_and_matrix_current_formula_without_delta(tmp_path) -> None:
    output_path = tmp_path / "cr-record.xlsx"
    source = _projection()
    cr_stages = tuple(
        replace(stage, test_item="CONTACT RESISTANCE (Power)", condition="10 A max", test_current_ampere="10")
        for stage in source.sections[0].stages
    )
    cr_section = replace(source.sections[0], record_type="cr", stages=cr_stages)
    projection = replace(source, record_type="cr", delta_r_enabled=False, sections=(cr_section,))

    LlcrCrSpecializedRecordWorkbookGateway().write(
        output_path=output_path, projection=projection,
    )

    workbook = load_workbook(output_path, data_only=False)
    assert workbook.sheetnames == ["Record Summary", "SIG"]
    sheet = workbook["SIG"]
    assert sheet["B8"].value == "Bulk Voltage (mV)"
    assert sheet["D16"].value == "Test current (A)"
    assert sheet["E16"].value == 10
    assert sheet["E18"].value == '=IF(OR(D18="",$E$16="",NOT(COUNTIFS($A$9:$A$10,$B18,$B$9:$B$10,"<>")>0)),"",(D18-VLOOKUP($B18,$A$9:$B$10,2,FALSE))/$E$16)'
    assert all("ΔR" not in str(cell.value) for row in sheet.iter_rows() for cell in row if cell.value)


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
        category_id="ppc-1",
        category_label="Signal",
        point_expression="1-2",
        stages=(
            LlcrCrRecordStage("Initial", "1", "row-1", "LLCR", "100 mA max", "", None),
            LlcrCrRecordStage("Final", "2", "row-2", "LLCR", "100 mA max", "", None),
        ),
        record_prefix="SIG",
    )
    return LlcrCrRecordProjection(
        project_id="project-1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=4,
        status="ready",
        sections=(section,),
        diagnostics=(),
        preview_fingerprint="fingerprint",
        record_type="llcr",
        point_profile_revision_id="profile-1",
        point_profile_revision_sequence=2,
        point_profile_fingerprint="profile-fingerprint",
        delta_r_enabled=True,
    )
