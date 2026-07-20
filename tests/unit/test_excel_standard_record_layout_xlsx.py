from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

from backend.infrastructure.office.excel_tabular_layout import ExcelTabularLayout
from backend.infrastructure.office.excel_workbook_gateway import ExcelWorkbookGateway


STANDARD_LAYOUT = ExcelTabularLayout(
    header_row_number=2,
    required_header_columns=(("文 件 编 号", 2),),
    optional_headers=("文 件 名 称", "备注"),
    include_row_number=True,
    require_unique_sheet_match=True,
)


def test_xlsx_explicit_layout_preserves_sparse_b_column_and_row_number(tmp_path: Path) -> None:
    workbook = tmp_path / "standard.xlsx"
    _write_sparse_xlsx(workbook, " 认可标准 ")

    result = ExcelWorkbookGateway().read_tabular_rows(
        workbook,
        expected_headers=("文 件 编 号",),
        expected_sheet_names=("认可标准",),
        layout=STANDARD_LAYOUT,
    )

    assert result.matched_sheet_names == (" 认可标准 ",)
    assert result.headers == ("文 件 编 号", "文 件 名 称", "备注")
    assert result.rows == (
        {
            "文 件 编 号": "ANSI/EIA-364-04B-2015",
            "文 件 名 称": "Contact resistance",
            "备注": "Current",
            "__sheet_name": " 认可标准 ",
            "__row_number": "3",
        },
    )


def test_default_xlsx_layout_remains_first_nonempty_header(tmp_path: Path) -> None:
    workbook = tmp_path / "default.xlsx"
    _write_default_xlsx(workbook)

    result = ExcelWorkbookGateway().read_tabular_rows(
        workbook,
        expected_headers=("Code", "Name"),
    )

    assert result.rows[0]["Code"] == "EIA-364-01"
    assert "__row_number" not in result.rows[0]


def _write_sparse_xlsx(path: Path, sheet_name: str) -> None:
    sheet = """<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1"><c r="A1" t="inlineStr"><is><t>Standard record</t></is></c></row>
    <row r="2">
      <c r="B2" t="inlineStr"><is><t>文 件 编 号</t></is></c>
      <c r="C2" t="inlineStr"><is><t>文 件 名 称</t></is></c>
      <c r="D2" t="inlineStr"><is><t>备注</t></is></c>
    </row>
    <row r="3">
      <c r="B3" t="inlineStr"><is><t>ANSI/EIA-364-04B-2015</t></is></c>
      <c r="C3" t="inlineStr"><is><t>Contact resistance</t></is></c>
      <c r="D3" t="inlineStr"><is><t>Current</t></is></c>
    </row>
  </sheetData>
</worksheet>"""
    _write_package(path, sheet_name, sheet)


def _write_default_xlsx(path: Path) -> None:
    sheet = """<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1"><c r="A1" t="inlineStr"><is><t>Code</t></is></c><c r="B1" t="inlineStr"><is><t>Name</t></is></c></row>
    <row r="2"><c r="A2" t="inlineStr"><is><t>EIA-364-01</t></is></c><c r="B2" t="inlineStr"><is><t>Example</t></is></c></row>
  </sheetData>
</worksheet>"""
    _write_package(path, "Data", sheet)


def _write_package(path: Path, sheet_name: str, sheet_xml: str) -> None:
    with ZipFile(path, "w") as archive:
        archive.writestr(
            "xl/workbook.xml",
            f'''<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
 <sheets><sheet name="{sheet_name}" sheetId="1" r:id="rId1"/></sheets>
</workbook>''',
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>''',
        )
        archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)
