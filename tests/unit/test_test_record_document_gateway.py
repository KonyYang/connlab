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
