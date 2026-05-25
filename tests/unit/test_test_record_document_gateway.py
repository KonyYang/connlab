from __future__ import annotations

from pathlib import Path

import pytest
from docx import Document

from backend.application.test_record_fee_dataset_preview_service import (
    TestRecordGroupDataset as RecordGroup,
    TestRecordStepDataset as RecordStep,
)
from backend.infrastructure.office.test_record_document_gateway import TestRecordDocumentGateway


def test_test_record_gateway_generates_docx(tmp_path: Path) -> None:
    template = tmp_path / "template.docx"
    Document().save(template)
    output = tmp_path / "generated.docx"

    step = RecordStep(
        sequence=1,
        test_item="LLCR",
        condition_summary="After conditioning",
        method_summary="Measure",
        reference_standard="EIA-364-23",
        judgement_criteria="20 mOhm max",
        duration_hint="1 day(s)",
        source_section="5.4",
        source_table_index=21,
        source_row_index=5,
        warnings=(),
    )
    group = RecordGroup(
        group_key="group_1",
        group_label="Group 1",
        source_table_index=21,
        steps=(step,),
        warnings=(),
    )

    result = TestRecordDocumentGateway().generate(
        template_path=template,
        output_path=output,
        source_document_name="spec.docx",
        groups=(group,),
        warnings=("missing duration",),
    )

    assert output.exists()
    assert result.status == "generated"


def test_test_record_gateway_rejects_non_docx_template(tmp_path: Path) -> None:
    template = tmp_path / "template.txt"
    template.write_text("x", encoding="utf-8")

    with pytest.raises(ValueError, match="Only .docx"):
        TestRecordDocumentGateway().generate(
            template_path=template,
            output_path=tmp_path / "out.docx",
            source_document_name="spec.docx",
            groups=(),
            warnings=(),
        )


def test_gateway_generates_confirmed_matrix_test_record_docx(tmp_path: Path) -> None:
    output = tmp_path / "confirmed-record.docx"
    group = _ConfirmedGroup()

    result = TestRecordDocumentGateway().generate_from_confirmed_matrix(
        output_path=output,
        project_id="P1",
        project_no="DL-001",
        product_description="Connector",
        applicable_specification="GS-12-1507",
        confirmed_matrix_id="cmv-1",
        groups=(group,),
    )

    assert result == output
    document = Document(output)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    table_text = "\n".join(
        cell.text for table in document.tables for row in table.rows for cell in row.cells
    )
    assert "ConnLab Test Record Draft" in text
    assert "Project No.: DL-001" in text
    assert "Product Description: Connector" in text
    assert "Applicable Specification: GS-12-1507" in text
    assert "Group Number: Group 1" in text
    assert "Sample Quantity & Number:" in text
    assert "5" in text
    assert "Start Date/Time:" in text
    assert "Equipment ID No.:" in text
    assert "Tested By:" in text
    assert "Visual" in table_text
    assert "EIA-364-18" in table_text
    assert "No damage" in table_text


class _ConfirmedStep:
    sequence = 1
    raw_token = "1"
    test_item = "Visual"
    section = "6.1"
    method = "EIA-364-18"
    condition = "10x"
    requirement = "No damage"


class _ConfirmedGroup:
    group_key = "g1"
    group_label = "Group 1"
    sample_quantity_expression = "5"
    step_count = 1
    steps = (_ConfirmedStep(),)
