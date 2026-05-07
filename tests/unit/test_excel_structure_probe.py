from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import pytest

from backend.infrastructure.office import (
    ExcelWorkbookGateway,
    UnsupportedLtrWorkbookError,
)


def test_excel_structure_probe_accepts_matching_sheet_headers_and_date(
    tmp_path: Path,
) -> None:
    workbook = tmp_path / "standard.xlsx"
    _write_minimal_xlsx(
        workbook,
        sheet_name="Standard Records",
        rows=[
            ["LTR Number", "Date", "Test Item", "Sample Description"],
            ["DL-2026-05-001", "2026-05-07", "Qualification", "Samples"],
        ],
    )

    result = ExcelWorkbookGateway().probe_structure(
        workbook,
        expected_headers=("LTR Number", "Test Item", "Sample Description"),
        expected_date_headers=("Date",),
        expected_sheet_name_patterns=(r".*record.*",),
    )

    assert result.valid is True
    assert result.matched_sheet_names == ("Standard Records",)
    assert result.missing_headers == ()
    assert result.missing_date_headers == ()


def test_excel_structure_probe_reports_missing_header(tmp_path: Path) -> None:
    workbook = tmp_path / "standard.xlsx"
    _write_minimal_xlsx(
        workbook,
        sheet_name="Standard Records",
        rows=[["LTR Number", "Date"]],
    )

    result = ExcelWorkbookGateway().probe_structure(
        workbook,
        expected_headers=("LTR Number", "Test Item"),
        expected_date_headers=("Date",),
        expected_sheet_name_patterns=(r".*record.*",),
    )

    assert result.valid is False
    assert result.missing_headers == ("Test Item",)
    assert result.failure_reason == "Missing required headers: Test Item"


def test_excel_structure_probe_reports_missing_sheet(tmp_path: Path) -> None:
    workbook = tmp_path / "standard.xlsx"
    _write_minimal_xlsx(workbook, sheet_name="Other", rows=[["LTR Number"]])

    result = ExcelWorkbookGateway().probe_structure(
        workbook,
        expected_headers=("LTR Number",),
        expected_sheet_name_patterns=(r".*record.*",),
    )

    assert result.valid is False
    assert result.matched_sheet_names == ()
    assert result.failure_reason == "No worksheet matched the expected sheet rules."


def test_excel_structure_probe_is_xlsx_only(tmp_path: Path) -> None:
    workbook = tmp_path / "legacy.xls"
    workbook.write_bytes(b"legacy")

    with pytest.raises(UnsupportedLtrWorkbookError, match="supports .xlsx only"):
        ExcelWorkbookGateway().probe_structure(
            workbook,
            expected_headers=("LTR Number",),
        )


def _write_minimal_xlsx(
    path: Path,
    *,
    sheet_name: str,
    rows: list[list[str]],
) -> None:
    """Write a minimal XLSX package that the gateway can read."""
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
    """Return worksheet XML using inline string cells."""
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
