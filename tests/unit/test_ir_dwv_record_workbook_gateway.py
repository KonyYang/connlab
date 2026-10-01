from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

import pytest
from openpyxl import load_workbook

from backend.infrastructure.files.ir_dwv_record_artifact_store import (
    IrDwvRecordArtifactStore,
)

from backend.infrastructure.office.ir_dwv_record_workbook_gateway import (
    IrDwvEquipment,
    IrDwvRecordGroup,
    IrDwvRecordProjection,
    IrDwvRecordStep,
    IrDwvRecordWorkbookGateway,
    copy_block,
)
from backend.infrastructure.office.ir_dwv_record_workbook_layout import (
    block_layout,
    plan_block_placements,
)
from scripts.inventory_ir_dwv_template import inventory_workbook


FIXTURE = Path(__file__).parents[1] / "fixtures" / "ir_dwv" / "IR_DWV_Template.xlsx"


def _projection(
    *,
    samples: int = 5,
    steps: int = 1,
    pairs: tuple[str, ...] = ("Odd&Even",),
) -> IrDwvRecordProjection:
    return IrDwvRecordProjection(
        request_number="DL-2026-07-115",
        product_name="Custom Pwr 14P VH",
        tested_by="Even Yang",
        checked_by="Peter Qiu",
        approved_by="Gentle Zeng",
        requestor="David Tao",
        start_date="2026/08/18",
        finish_date="2026/08/18",
        ambient_temperature="25.7°C",
        relative_humidity="48.5%RH",
        equipment=(
            IrDwvEquipment(
                instrument="Eleactrical Safety Compliance Analyzer",
                gage_id="DG-Q-0624",
                last_calibration="2024/12/30",
                calibration_due="2025/12/29",
            ),
        ),
        groups=(
            IrDwvRecordGroup(
                label="Group 1",
                sample_count=samples,
                steps=tuple(
                    IrDwvRecordStep(
                        label=(
                            "Initial"
                            if index == 0
                            else "Final"
                            if index == steps - 1
                            else f"After Step {index}"
                        ),
                        ir_condition="500VDC 2min. mated",
                        dwv_condition="1500VDC 1min. Mated",
                        measurement_pairs=pairs,
                        expected_fee_quantity=samples * len(pairs),
                    )
                    for index in range(steps)
                ),
            ),
        ),
    )


def test_copy_block_preserves_formatting_merges_dimensions_and_translates_formulas():
    source_book = load_workbook(FIXTURE)
    source = source_book["Group 1"]
    target = source_book.create_sheet("Copied")

    copy_block(
        source,
        target,
        source_min_row=1,
        source_max_row=40,
        source_min_column=2,
        source_max_column=12,
        target_min_row=1,
        target_min_column=15,
    )

    assert target["O1"].value == source["B1"].value
    assert target["O1"]._style == source["B1"]._style
    assert target.row_dimensions[1].height == source.row_dimensions[1].height
    assert target.column_dimensions["O"].width == source.column_dimensions["B"].width
    assert "O1:Q2" in {str(item) for item in target.merged_cells.ranges}
    assert target["U34"].value == "=MIN(U22:Y33)"
    source_book.close()


@pytest.mark.parametrize("samples", [3, 5, 7])
def test_writer_resizes_samples_and_rebuilds_conditions_headers_and_statistics(
    tmp_path: Path,
    samples: int,
):
    target = tmp_path / f"record-{samples}.xlsx"
    IrDwvRecordWorkbookGateway(FIXTURE).write(
        output_path=target,
        projection=_projection(samples=samples),
    )

    workbook = load_workbook(target, data_only=False)
    sheet = workbook["Group 1"]
    layout = block_layout(
        origin_column=2,
        sample_count=samples,
        pair_count=1,
    )
    assert sheet.cell(layout.conditions_start_row, layout.origin_column).value == (
        "1. IR testing/ 1# 500VDC 2min. mated"
    )
    assert sheet.cell(layout.conditions_start_row, layout.dwv_start_column).value == (
        f"{samples + 1}. DWV testing/ 1# 1500VDC 1min. Mated"
    )
    assert [
        sheet.cell(layout.sample_id_row, column).value
        for column in range(layout.ir_start_column, layout.ir_end_column + 1)
    ] == [f"{index}#" for index in range(1, samples + 1)]
    assert [
        sheet.cell(layout.sequence_row, column).value
        for column in range(layout.ir_start_column, layout.dwv_end_column + 1)
    ] == list(range(1, 2 * samples + 1))
    assert sheet.cell(layout.data_start_row, layout.origin_column).value == "Odd&Even"
    assert all(
        sheet.cell(layout.data_start_row, column).value is None
        for column in range(layout.ir_start_column, layout.dwv_end_column + 1)
    )
    dwv_range = (
        f"{sheet.cell(layout.data_start_row, layout.dwv_start_column).coordinate}:"
        f"{sheet.cell(layout.data_end_row, layout.dwv_end_column).coordinate}"
    )
    assert sheet.cell(layout.stats_min_row, layout.dwv_start_column).value == f"=MIN({dwv_range})"
    assert sheet.cell(layout.stats_max_row, layout.dwv_start_column).value == f"=MAX({dwv_range})"
    assert sheet.cell(layout.stats_average_row, layout.dwv_start_column).value == (
        f"=AVERAGE({dwv_range})"
    )
    assert sheet.cell(layout.stats_stdev_row, layout.dwv_start_column).value == (
        f"=STDEV({dwv_range})"
    )
    workbook.close()


@pytest.mark.parametrize(
    ("step_count", "expected_sheets", "expected_origins"),
    [
        (2, ["Group 1"], [2, 15]),
        (3, ["Group 1"], [2, 15, 26]),
        (4, ["Group 1", "Group 1 (2)"], [2, 15, 26, 2]),
    ],
)
def test_writer_places_steps_across_sheets(
    tmp_path: Path,
    step_count: int,
    expected_sheets: list[str],
    expected_origins: list[int],
):
    placements = plan_block_placements(
        sample_count=5,
        pair_count=1,
        step_count=step_count,
    )
    assert [item.origin_column for item in placements] == expected_origins

    target = tmp_path / f"steps-{step_count}.xlsx"
    IrDwvRecordWorkbookGateway(FIXTURE).write(
        output_path=target,
        projection=_projection(steps=step_count),
    )
    workbook = load_workbook(target)
    assert workbook.sheetnames == expected_sheets
    workbook.close()


def test_writer_clears_all_template_measurements_when_pairs_are_empty(tmp_path: Path):
    target = tmp_path / "empty-pairs.xlsx"
    IrDwvRecordWorkbookGateway(FIXTURE).write(
        output_path=target,
        projection=_projection(pairs=()),
    )

    workbook = load_workbook(target, data_only=False)
    sheet = workbook["Group 1"]
    layout = block_layout(origin_column=2, sample_count=5, pair_count=0)
    for row in range(layout.data_start_row, layout.data_end_row + 1):
        assert sheet.cell(row, layout.origin_column).value is None
        for column in range(layout.ir_start_column, layout.dwv_end_column + 1):
            assert sheet.cell(row, column).value is None
    workbook.close()


def test_writer_blocks_a_template_with_a_changed_fingerprint(tmp_path: Path):
    changed_template = tmp_path / "changed.xlsx"
    workbook = load_workbook(FIXTURE)
    workbook["Group 1"]["B1"] = "Unexpected template"
    workbook.save(changed_template)
    workbook.close()

    with pytest.raises(ValueError, match="fingerprint"):
        IrDwvRecordWorkbookGateway(changed_template).write(
            output_path=tmp_path / "record.xlsx",
            projection=_projection(),
        )


def test_writer_blocks_fee_quantity_mismatch(tmp_path: Path):
    projection = _projection()
    bad_step = replace(projection.groups[0].steps[0], expected_fee_quantity=99)
    bad_group = replace(projection.groups[0], steps=(bad_step,))

    with pytest.raises(ValueError, match="Fee quantity"):
        IrDwvRecordWorkbookGateway(FIXTURE).write(
            output_path=tmp_path / "record.xlsx",
            projection=replace(projection, groups=(bad_group,)),
        )



def test_ir_dwv_artifact_store_uses_contained_uuid_paths(tmp_path: Path):
    store = IrDwvRecordArtifactStore(tmp_path)
    artifact = store.prepare_draft(project_id="project/one", record_type="ir_dwv")

    assert artifact.output_path.parent == tmp_path / "project_one"
    assert artifact.output_path.suffix == ".xlsx"
    artifact.output_path.touch()
    resolved = store.resolve(
        project_id="project/one",
        artifact_id=artifact.artifact_id,
    )
    assert resolved.output_path == artifact.output_path.resolve()

    with pytest.raises(ValueError, match="Record type"):
        store.prepare_draft(project_id="project/one", record_type="llcr")

def test_template_inventory_matches_the_frozen_fixture():
    expected_path = FIXTURE.with_name("template_inventory.json")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    assert inventory_workbook(FIXTURE) == expected

@pytest.mark.parametrize(
    ("samples", "step_count", "expected_sheet_indexes"),
    [
        (3, 5, [0, 0, 0, 0, 1]),
        (7, 3, [0, 0, 1]),
    ],
)
def test_step_capacity_changes_with_block_width(
    samples: int,
    step_count: int,
    expected_sheet_indexes: list[int],
):
    placements = plan_block_placements(
        sample_count=samples,
        pair_count=1,
        step_count=step_count,
    )

    assert [item.sheet_index for item in placements] == expected_sheet_indexes


@pytest.mark.parametrize("samples", [0, -1, 3.5, True])
def test_writer_blocks_non_positive_or_non_integer_sample_counts(
    tmp_path: Path,
    samples,
):
    with pytest.raises(ValueError, match="positive integer"):
        IrDwvRecordWorkbookGateway(FIXTURE).write(
            output_path=tmp_path / "record.xlsx",
            projection=_projection(samples=samples),
        )


def test_writer_blocks_when_registered_template_has_an_excel_lock(tmp_path: Path):
    template = tmp_path / "IR&DWV Template.xlsx"
    template.write_bytes(FIXTURE.read_bytes())
    template.with_name("~$IR&DWV Template.xlsx").write_bytes(b"locked")

    with pytest.raises(
        ValueError,
        match="请关闭 Excel 中的 IR&DWV Template.xlsx",
    ):
        IrDwvRecordWorkbookGateway(template).write(
            output_path=tmp_path / "record.xlsx",
            projection=_projection(),
        )
