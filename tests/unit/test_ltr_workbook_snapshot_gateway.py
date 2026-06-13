from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import pytest

from backend.infrastructure.office import (
    ExcelWorkbookGateway,
    LtrWorkbookFormat,
    UnreadableLtrWorkbookError,
    UnsupportedLtrWorkbookError,
)


def test_ltr_workbook_snapshot_reads_xlsx_metadata_and_numbers(
    tmp_path: Path,
) -> None:
    """The LTR workbook gateway reads .xlsx metadata and existing numbers."""
    workbook_path = tmp_path / "ltr.xlsx"
    _write_minimal_xlsx(
        workbook_path,
        sheet_name="2026",
        rows=[
            ["DL", "Requested By"],
            ["DL-2026-04-001", "Alice"],
            ["DL-2026-04-002A", "Suffix"],
            ["W123", "External"],
            ["not an ltr", ""],
        ],
    )

    snapshot = ExcelWorkbookGateway().read_ltr_workbook_snapshot(workbook_path)

    assert snapshot.workbook_path == workbook_path
    assert snapshot.workbook_format is LtrWorkbookFormat.XLSX
    assert snapshot.size_bytes > 0
    assert snapshot.sheet_names == ("2026",)
    assert snapshot.readable_sheet_names == ("2026",)
    assert snapshot.sheet_strategy == "year_sheets"
    assert snapshot.existing_ltr_numbers == (
            "DL-2026-04-001",
            "DL-2026-04-002A",
    )
    assert snapshot.unsupported_reason is None


def test_ltr_workbook_snapshot_reports_missing_file(tmp_path: Path) -> None:
    """Missing workbook paths fail explicitly."""
    with pytest.raises(FileNotFoundError, match="LTR workbook does not exist"):
        ExcelWorkbookGateway().read_ltr_workbook_snapshot(tmp_path / "missing.xlsx")


def test_ltr_workbook_snapshot_rejects_legacy_xls_without_writing(
    tmp_path: Path,
) -> None:
    """Legacy .xls is detected but waits for a later adapter task."""
    workbook_path = tmp_path / "ltr.xls"
    workbook_path.write_bytes(b"legacy")

    with pytest.raises(UnsupportedLtrWorkbookError, match="Legacy .xls"):
        ExcelWorkbookGateway().read_ltr_workbook_snapshot(workbook_path)


def test_ltr_workbook_snapshot_rejects_unsupported_extension(tmp_path: Path) -> None:
    """Unsupported workbook extensions fail explicitly."""
    workbook_path = tmp_path / "ltr.csv"
    workbook_path.write_text("DL-2026-04-001", encoding="utf-8")

    with pytest.raises(UnsupportedLtrWorkbookError, match="Unsupported LTR workbook"):
        ExcelWorkbookGateway().read_ltr_workbook_snapshot(workbook_path)


def test_ltr_workbook_snapshot_rejects_corrupt_xlsx(tmp_path: Path) -> None:
    """Unreadable .xlsx files fail with a gateway error."""
    workbook_path = tmp_path / "corrupt.xlsx"
    workbook_path.write_bytes(b"not a zip")

    with pytest.raises(UnreadableLtrWorkbookError, match="Unable to read XLSX"):
        ExcelWorkbookGateway().read_ltr_workbook_snapshot(workbook_path)


def test_ltr_workbook_gateway_has_no_write_method() -> None:
    """The workbook gateway must remain read-only."""
    public_methods = {
        name
        for name in dir(ExcelWorkbookGateway)
        if not name.startswith("_") and callable(getattr(ExcelWorkbookGateway, name))
    }

    assert public_methods == {
        "probe_structure",
        "read_tabular_rows",
        "read_ltr_workbook_snapshot",
        "read_workbook",
    }
    assert not any("write" in name or "save" in name for name in public_methods)


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
