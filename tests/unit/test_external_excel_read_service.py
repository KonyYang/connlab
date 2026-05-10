from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import pytest

from backend.application.external_excel_read_service import (
    ExternalExcelReadError,
    ExternalExcelReadService,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ExternalResourceValidationStatus,
)


def test_read_standard_records_returns_structured_rows_with_query(tmp_path: Path) -> None:
    workbook = tmp_path / "standard.xlsx"
    _write_minimal_xlsx(
        workbook,
        sheet_name="Standard Records",
        rows=[
            ["LTR Number", "Test Item", "Sample Description"],
            ["EIA-364-01", "Contact resistance", "Power connector"],
            ["EIA-364-02", "Thermal shock", "Signal connector"],
        ],
    )
    service = ExternalExcelReadService(
        _Store(
            [
                _resource(
                    ExternalResourceType.STANDARD_RECORD_EXCEL,
                    workbook,
                )
            ]
        )
    )

    result = service.read_standard_records(query="thermal")

    assert result.resource_path == str(workbook)
    assert result.matched_sheets == ("Standard Records",)
    assert len(result.rows) == 1
    assert result.rows[0].standard_code == "EIA-364-02"
    assert result.rows[0].source_sheet == "Standard Records"


def test_read_equipment_rows_returns_structured_rows(tmp_path: Path) -> None:
    workbook = tmp_path / "equipment.xlsx"
    _write_minimal_xlsx(
        workbook,
        sheet_name="Equipment Calibration",
        rows=[
            ["Equipment ID", "Equipment Name", "Calibration Due Date"],
            ["EQ-001", "Load Frame", "2026-08-10"],
        ],
    )
    service = ExternalExcelReadService(
        _Store(
            [
                _resource(
                    ExternalResourceType.EQUIPMENT_CALIBRATION_EXCEL,
                    workbook,
                )
            ]
        )
    )

    result = service.read_equipment_calibrations()

    assert result.matched_sheets == ("Equipment Calibration",)
    assert len(result.rows) == 1
    assert result.rows[0].equipment_id == "EQ-001"
    assert result.rows[0].equipment_name == "Load Frame"
    assert result.rows[0].calibration_due_date == "2026-08-10"


def test_read_requires_active_registered_resource(tmp_path: Path) -> None:
    workbook = tmp_path / "standard.xlsx"
    _write_minimal_xlsx(
        workbook,
        sheet_name="Standard Records",
        rows=[["LTR Number", "Test Item", "Sample Description"]],
    )
    service = ExternalExcelReadService(
        _Store(
            [
                ExternalResource(
                    resource_id="R1",
                    resource_type=ExternalResourceType.STANDARD_RECORD_EXCEL,
                    path=workbook,
                    active=False,
                    validation_status=ExternalResourceValidationStatus.NOT_VALIDATED,
                )
            ]
        )
    )

    with pytest.raises(ExternalExcelReadError, match="inactive"):
        service.read_standard_records()


class _Store:
    def __init__(self, resources: list[ExternalResource]) -> None:
        self._resources = {resource.resource_type: resource for resource in resources}

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        return self._resources.get(resource_type)


def _resource(resource_type: ExternalResourceType, path: Path) -> ExternalResource:
    return ExternalResource(
        resource_id=f"R-{resource_type.value}",
        resource_type=resource_type,
        path=path,
        active=True,
        validation_status=ExternalResourceValidationStatus.VALID,
    )


def _write_minimal_xlsx(
    path: Path,
    *,
    sheet_name: str,
    rows: list[list[str]],
) -> None:
    with ZipFile(path, "w") as archive:
        archive.writestr(
            "xl/workbook.xml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="{sheet_name}" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>""",
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"
    Target="worksheets/sheet1.xml"/>
</Relationships>""",
        )
        archive.writestr("xl/worksheets/sheet1.xml", _sheet_xml(rows))


def _sheet_xml(rows: list[list[str]]) -> str:
    row_xml = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for column_index, value in enumerate(row):
            reference = f"{chr(65 + column_index)}{row_index}"
            cells.append(
                f'<c r="{reference}" t="inlineStr"><is><t>{value}</t></is></c>'
            )
        row_xml.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(row_xml)}</sheetData>'
        "</worksheet>"
    )
