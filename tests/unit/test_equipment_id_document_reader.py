from __future__ import annotations

from pathlib import Path

from docx import Document

from backend.infrastructure.office.equipment_id_document_reader import (
    EquipmentIdDocumentReader,
)


def test_reads_paragraphs_and_table_cells_in_order_and_deduplicates(tmp_path: Path) -> None:
    source = tmp_path / "EquipmentID.docx"
    document = Document()
    document.add_paragraph("DG-Q-0033")
    document.add_paragraph("Customer fixture L-0002")
    document.add_paragraph("dg-q-0033")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "DG-Q-0103"
    table.cell(0, 1).text = "Customer fixture L-0002"
    document.save(source)

    result = EquipmentIdDocumentReader().read(source)

    assert result.source_path == source
    assert result.references == (
        "DG-Q-0033",
        "Customer fixture L-0002",
        "DG-Q-0103",
    )


def test_rejects_an_empty_equipment_id_document(tmp_path: Path) -> None:
    source = tmp_path / "EquipmentID.docx"
    Document().save(source)

    try:
        EquipmentIdDocumentReader().read(source)
    except ValueError as exc:
        assert "does not contain equipment references" in str(exc)
    else:
        raise AssertionError("Expected an empty EquipmentID.docx to be rejected")
