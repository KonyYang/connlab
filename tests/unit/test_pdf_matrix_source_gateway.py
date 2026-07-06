from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from backend.infrastructure.files.pdf_matrix_source_gateway import (
    PdfMatrixSourceGateway,
    PdfMatrixSourceGatewayError,
    _normalize_table,
)
from backend.modules.test_plan.product_spec_matrix_parser import ProductSpecMatrixParser


def test_pdf_gateway_extracts_text_table_and_page_locator(tmp_path: Path) -> None:
    pdf_path = tmp_path / "matrix-source.pdf"
    _write_matrix_pdf(pdf_path)

    snapshot = PdfMatrixSourceGateway().read_pdf_document(pdf_path)

    assert snapshot.paragraphs
    assert snapshot.tables == (
        (
            ("test Items", "Section", "Group 1", "Group 2"),
            ("Examination of Product", "5.4", "1,10", "1,13"),
            ("Contact Resistance (Low Level)", "6.1", "2,5", "2,8"),
        ),
    )
    assert len(snapshot.table_locations) == 1
    location = snapshot.table_locations[0]
    assert location.table_index == 1
    assert location.page_number == 1
    assert location.page_table_index == 1
    assert location.row_count == 3
    assert location.column_count == 4
    assert "Contact Resistance" in location.text_preview


def test_pdf_gateway_reports_no_extractable_text(tmp_path: Path) -> None:
    pdf_path = tmp_path / "blank.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.showPage()
    c.save()

    try:
        PdfMatrixSourceGateway().read_pdf_document(pdf_path)
    except PdfMatrixSourceGatewayError as exc:
        assert "no extractable text" in str(exc).lower()
    else:
        raise AssertionError("Expected no-text PDF to be blocked.")


def test_pdf_matrix_header_fragments_are_collapsed_for_parser() -> None:
    raw_table = [
        ["", "TEST GROUP ID:", "", "1", "2", "3"],
        ["", "", "", "High", "Thermal", ""],
        ["", "", "", "Temp", "Shock &", "Vibration &"],
        ["TEST DESCRIPTION", "", "Section", "Life", "Cyclic", "Shock"],
        ["", "", "", "", "Humidity", ""],
        ["VISUAL EXAMINATION", "", "5.4, 9.2", "1,15", "1,21", "1,26"],
        ["POROSITY", "", "5.3.1", "", "2", ""],
    ]

    table = [list(row) for row in _normalize_table(raw_table)]
    header = ProductSpecMatrixParser()._find_header(table)

    assert header is not None
    assert header.item_column == 0
    assert header.section_column == 2
    assert header.group_columns == ((3, "1"), (4, "2"), (5, "3"))
    assert table[1][0] == "TEST DESCRIPTION"


def test_pdf_split_section_header_is_repaired_for_parser() -> None:
    raw_table = [
        ["TEST GROUP ID:", "", "1", "2"],
        ["TEST DESCRIPTION", "SECTIO N", "Temp Life", "Thermal Shock & Humidity"],
        ["VISUAL EXAMINATION", "7.1", "1,9", "1,10"],
        ["Current Rating", "6.1", "2", ""],
    ]

    table = [list(row) for row in _normalize_table(raw_table)]
    header = ProductSpecMatrixParser()._find_header(table)

    assert header is not None
    assert header.item_column == 0
    assert header.section_column == 1
    assert header.group_columns == ((2, "1"), (3, "2"))
    assert table[1][1] == "SECTION"


def test_pdf_revision_record_table_is_not_a_matrix_candidate() -> None:
    raw_table = [
        ["Rev", "Page", "Description", "EC#", "Date"],
        ["01", "11", "THE FIRST RELEASE", "", "2024/02/27"],
        ["02", "4, 5, 6", "REMOVE OPTION AND CORRECT SOME TYPOS", "", "2024/04/24"],
    ]

    assert _normalize_table(raw_table) == ()


def _write_matrix_pdf(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=letter)
    c.drawString(72, 740, "Table 4: Qualification Test Matrix")
    rows = [
        ["test Items", "Section", "Group 1", "Group 2"],
        ["Examination of Product", "5.4", "1,10", "1,13"],
        ["Contact Resistance (Low Level)", "6.1", "2,5", "2,8"],
    ]
    x0 = 72
    y0 = 700
    col_widths = [180, 70, 80, 80]
    row_height = 26
    for row_index, row in enumerate(rows):
        y = y0 - row_index * row_height
        x = x0
        for col_index, value in enumerate(row):
            width = col_widths[col_index]
            c.rect(x, y - row_height, width, row_height)
            c.drawString(x + 4, y - 17, value)
            x += width
    c.showPage()
    c.save()
