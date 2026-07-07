from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from backend.infrastructure.files.pdf_matrix_source_gateway import (
    PdfMatrixSourceGateway,
    PdfMatrixSourceGatewayError,
    PdfTableLocation,
    _merge_matrix_continuation_tables,
    _normalize_table,
    _split_paragraphs,
)
from backend.modules.test_plan.product_spec_matrix_parser import ProductSpecMatrixParser
from backend.modules.test_plan.spec_section_text_extractor import collect_section_text_blocks


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


def test_pdf_gateway_merges_matrix_table_continuation_page() -> None:
    matrix_start = _normalize_table(
        [
            ["TEST GROUP ID:", "", "1", "2", "3"],
            ["TEST DESCRIPTION", "SECTION", "Temp Life", "Thermal Shock", "Dust"],
            ["VISUAL EXAMINATION", "7.1", "1,10", "1,16", "1,7"],
            ["Current Rating", "6.1", "", "", "2"],
        ]
    )
    continuation = _normalize_table(
        [
            ["Contact Resistance, Low Level (LLCR)", "6.2", "2,5,7,9", "2,7,11,15", ""],
            ["Insulation Resistance", "6.4", "", "3,8,12", ""],
        ]
    )
    next_page_header = _normalize_table(
        [
            ["NUMBER GS-12-2186", "TYPE GENERAL PRODUCT SPECIFICATION", "", ""],
            ["TITLE DC PDU", "", "PAGE 10 of 11", "REVISION 01"],
        ]
    )

    tables, locations = _merge_matrix_continuation_tables(
        [matrix_start, next_page_header, continuation],
        [
            PdfTableLocation(
                table_index=1,
                page_number=9,
                page_table_index=2,
                preceding_paragraph="9.7 Qualification Test Table",
                text_preview="TEST GROUP ID:",
                row_count=len(matrix_start),
                column_count=5,
            ),
            PdfTableLocation(
                table_index=2,
                page_number=10,
                page_table_index=1,
                preceding_paragraph=None,
                text_preview="NUMBER GS-12-2186",
                row_count=len(next_page_header),
                column_count=4,
            ),
            PdfTableLocation(
                table_index=3,
                page_number=10,
                page_table_index=2,
                preceding_paragraph=None,
                text_preview="Contact Resistance, Low Level",
                row_count=len(continuation),
                column_count=5,
            ),
        ],
    )

    assert len(tables) == 2
    assert len(tables[0]) == 6
    assert tables[0][-2][0] == "Contact Resistance, Low Level (LLCR)"
    assert tables[1] == next_page_header
    assert locations[0].table_index == 1
    assert locations[0].page_number == 9
    assert locations[0].page_table_index == 2
    assert locations[0].row_count == 6
    assert locations[1].table_index == 2
    assert locations[1].page_number == 10
    assert locations[1].page_table_index == 1
    assert locations[2].table_index == 1
    assert locations[2].page_number == 10
    assert locations[2].page_table_index == 2
    assert "Continuation of page 9 table 2" in locations[2].text_preview
    assert "Continued on page 10" in locations[0].text_preview

    parsed = ProductSpecMatrixParser().parse_tables(
        [list(map(list, tables[0]))],
        table_contexts={1: "9.7 Qualification Test Table"},
    )

    assert parsed.blockers == ()
    assert len(parsed.rows) == 4
    group_1 = next(group for group in parsed.groups if group.group_label == "1")
    assert "VISUAL EXAMINATION" in [step.test_item for step in group_1.steps]
    assert "Contact Resistance, Low Level (LLCR)" in [
        step.test_item for step in group_1.steps
    ]


def test_pdf_gateway_repairs_split_sample_quantity_tail_and_notes() -> None:
    raw_table = [
        ["TEST GROUP ID:", "", "1", "2"],
        ["TEST DESCRIPTION", "SECTION", "Temp Life", "Thermal Shock"],
        ["VISUAL EXAMINATION", "7.1", "1", "1"],
        ["SAMPLES QUANTITY", "", "", ""],
        ["", "", "3(a)", "3b)"],
        ["(PCS)", "", "", ""],
    ]

    table = [list(row) for row in _normalize_table(raw_table)]
    parsed = ProductSpecMatrixParser().parse_tables(
        [table],
        paragraphs=_split_paragraphs(
            "Notes: a.Male connector and Female connector b.Male connector."
        ),
        table_contexts={1: "9.7 Qualification Test Table"},
    )

    assert table[-1] == ["SAMPLES QUANTITY (PCS)", "", "3(a)", "3(b)"]
    assert parsed.groups[0].sample_quantity_expression == "3(a)"
    assert parsed.groups[0].sample_note == "(a) Male connector and Female connector"
    assert parsed.groups[1].sample_quantity_expression == "3(b)"
    assert parsed.groups[1].sample_note == "(b) Male connector."


def test_pdf_gateway_splits_dense_page_text_into_section_blocks() -> None:
    paragraphs = _split_paragraphs(
        "NUMBER TYPE GENERAL 6.0 Electrical Characteristics "
        "6.1 Current Rating The temperature rise above ambient "
        "shall not exceed 30℃ at any point in the system. c. Reference - EIA 364-70 "
        "6.2 Contact Resistance The low-level contact resistance shall not exceed "
        "0.25 milliohms initially. Measurements shall be in accordance with EIA 364-23. "
        "7.0 Mechanical Characteristics "
        "7.1 Visual and dimensional inspections a. Reference - EIA-364-18 "
        "c. Requirement: Meets product drawing requirements."
    )
    sections = collect_section_text_blocks(paragraphs)

    assert "6.1" in sections
    assert "0.25" not in sections
    assert "0.25 milliohms initially" in sections["6.2"]
    assert "7.1" in sections

    parsed = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["TEST GROUP ID:", "", "1"],
                ["TEST DESCRIPTION", "SECTION", "Temp Life"],
                ["VISUAL EXAMINATION", "7.1", "1"],
                ["Current Rating", "6.1", "2"],
            ]
        ],
        paragraphs=paragraphs,
        table_contexts={1: "9.7 Qualification Test Table"},
    )

    assert parsed.rows[0].method == "EIA-364-18"
    assert parsed.rows[0].requirement == "No detrimental condition"
    assert parsed.rows[1].method == "EIA-364-70"
    assert parsed.rows[1].requirement == "≤ 30 ℃"


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
