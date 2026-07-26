from datetime import datetime

import pytest

from backend.application.matrix_editor_live_xlsx_export_service import (
    MatrixEditorLiveXlsxExportCell,
    MatrixEditorLiveXlsxExportError,
    MatrixEditorLiveXlsxExportGroup,
    MatrixEditorLiveXlsxExportRequest,
    MatrixEditorLiveXlsxExportRow,
    MatrixEditorLiveXlsxExportService,
)


class SpyGateway:
    def __init__(self) -> None:
        self.calls = []

    def render(self, projection):
        self.calls.append(projection)
        return b"xlsx"


def request(*, rows=1, groups=1):
    export_groups = tuple(
        MatrixEditorLiveXlsxExportGroup(f"g{i}", f"G{i}", f"Group {i}", "", "0 d")
        for i in range(groups)
    )
    export_rows = tuple(
        MatrixEditorLiveXlsxExportRow(
            f"r{i}", "Item", "", "", "", "",
            tuple(
                MatrixEditorLiveXlsxExportCell(group.group_id, "1" if index == 0 else "")
                for index, group in enumerate(export_groups)
            ),
        )
        for i in range(rows)
    )
    return MatrixEditorLiveXlsxExportRequest(
        "matrix_editor_current_ui_state", "DL:2026/01", export_groups, export_rows
    )


def test_service_builds_windows_safe_timestamped_filename():
    gateway = SpyGateway()
    service = MatrixEditorLiveXlsxExportService(
        gateway, clock=lambda: datetime(2026, 7, 26, 9, 8, 7)
    )
    result = service.export(request())
    assert result.file_name == "DL_2026_01 Matrix Draft 20260726090807.xlsx"
    assert result.content == b"xlsx"
    assert len(gateway.calls) == 1


@pytest.mark.parametrize(
    "candidate",
    [
        request(rows=0),
        request(groups=65),
        request(rows=1, groups=1),
    ],
)
def test_service_rejects_invalid_shape_before_gateway(candidate):
    if candidate.rows:
        row = candidate.rows[0]
        candidate = MatrixEditorLiveXlsxExportRequest(
            candidate.source,
            candidate.project_reference,
            candidate.groups,
            (
                MatrixEditorLiveXlsxExportRow(
                    row.row_id, row.test_item, row.section, row.test_method,
                    row.condition, row.requirement,
                    (MatrixEditorLiveXlsxExportCell(row.cells[0].group_id, ""),),
                ),
            ),
        )
    gateway = SpyGateway()
    with pytest.raises(MatrixEditorLiveXlsxExportError):
        MatrixEditorLiveXlsxExportService(gateway).export(candidate)
    assert gateway.calls == []


def test_service_rejects_nonrectangular_and_duplicate_ids_before_gateway():
    base = request()
    gateway = SpyGateway()
    bad = MatrixEditorLiveXlsxExportRequest(
        base.source,
        base.project_reference,
        base.groups + base.groups,
        base.rows,
    )
    with pytest.raises(MatrixEditorLiveXlsxExportError):
        MatrixEditorLiveXlsxExportService(gateway).export(bad)
    assert gateway.calls == []


def test_service_rejects_row_and_total_cell_caps_before_gateway():
    gateway = SpyGateway()
    for candidate in (request(rows=513), request(rows=257, groups=64)):
        with pytest.raises(MatrixEditorLiveXlsxExportError):
            MatrixEditorLiveXlsxExportService(gateway).export(candidate)
    assert gateway.calls == []


def test_service_rejects_string_caps_before_gateway():
    base = request()
    gateway = SpyGateway()
    oversized_group = MatrixEditorLiveXlsxExportGroup("g0", "G0", "x" * 256, "", "0 d")
    candidate = MatrixEditorLiveXlsxExportRequest(
        base.source,
        base.project_reference,
        (oversized_group,),
        (
            MatrixEditorLiveXlsxExportRow(
                "r0", "x" * 2049, "", "", "", "",
                (MatrixEditorLiveXlsxExportCell("g0", "1"),),
            ),
        ),
    )
    with pytest.raises(MatrixEditorLiveXlsxExportError):
        MatrixEditorLiveXlsxExportService(gateway).export(candidate)
    assert gateway.calls == []
