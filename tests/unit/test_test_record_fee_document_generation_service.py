from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.application.test_record_fee_dataset_preview_service import (
    FeeDataset,
    FeeDatasetSummary,
    TestRecordDataset as RecordDataset,
    TestRecordFeeDatasetPreview as RecordFeePreview,
    TestRecordGroupDataset as RecordGroup,
    TestRecordStepDataset as RecordStep,
)
from backend.application.test_record_fee_document_generation_service import (
    TestRecordFeeDocumentGenerationCommand as GenerationCommand,
    TestRecordFeeDocumentGenerationError as GenerationError,
    TestRecordFeeDocumentGenerationService as GenerationService,
)
from backend.infrastructure.office import (
    FeeEvaluationWorkbookWriteResult,
    OfficeAutomationUnavailable,
    TestRecordDocumentWriteResult as RecordWriteResult,
)


def test_generation_creates_test_record_and_skips_unavailable_fee(tmp_path: Path) -> None:
    template = tmp_path / "record.docx"
    template.write_bytes(b"docx")
    fee_template = tmp_path / "fee.xls"
    fee_template.write_bytes(b"xls")

    service = GenerationService(
        dataset_preview_service=_PreviewService(),
        test_record_writer=_TestRecordWriter(),
        fee_writer=_UnavailableFeeWriter(),
    )

    result = service.generate(
        GenerationCommand(
            project_id="P1",
            draft_id="D1",
            output_dir=tmp_path,
            test_record_template_path=template,
            fee_evaluation_template_path=fee_template,
            include_test_record=True,
            include_fee_evaluation=True,
        )
    )

    assert len(result.generated_files) == 2
    assert result.generated_files[0].kind == "test_record"
    assert result.generated_files[0].status == "generated"
    assert result.generated_files[0].output_path is not None
    assert result.generated_files[1].kind == "fee_evaluation"
    assert result.generated_files[1].status == "skipped_unavailable"


def test_generation_rejects_both_outputs_disabled(tmp_path: Path) -> None:
    service = GenerationService(
        dataset_preview_service=_PreviewService(),
        test_record_writer=_TestRecordWriter(),
        fee_writer=_UnavailableFeeWriter(),
    )

    with pytest.raises(GenerationError, match="At least one"):
        service.generate(
            GenerationCommand(
                project_id="P1",
                draft_id="D1",
                output_dir=tmp_path,
                include_test_record=False,
                include_fee_evaluation=False,
            )
        )


def test_generation_rejects_existing_output_when_overwrite_false(tmp_path: Path) -> None:
    template = tmp_path / "record.docx"
    template.write_bytes(b"docx")
    existing = tmp_path / "spec_test_record_generated.docx"
    existing.write_bytes(b"exists")

    service = GenerationService(
        dataset_preview_service=_PreviewService(),
        test_record_writer=_TestRecordWriter(),
        fee_writer=_UnavailableFeeWriter(),
    )

    with pytest.raises(GenerationError, match="already exists"):
        service.generate(
            GenerationCommand(
                project_id="P1",
                draft_id="D1",
                output_dir=tmp_path,
                test_record_template_path=template,
                include_test_record=True,
                include_fee_evaluation=False,
            )
        )


class _PreviewService:
    def preview(self, _command):
        step = RecordStep(
            sequence=1,
            test_item="LLCR",
            condition_summary="After conditioning",
            method_summary="Measure LLCR",
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
        return RecordFeePreview(
            project_id="P1",
            draft_id="D1",
            source_document_name="spec.docx",
            test_record_dataset=RecordDataset(groups=(group,)),
            fee_dataset=FeeDataset(
                summary=FeeDatasetSummary(group_count=1, step_count=1, explicit_duration_days=1),
                line_items=(),
            ),
            warnings=(),
        )


class _TestRecordWriter:
    def generate(self, **kwargs):
        output_path = kwargs["output_path"]
        output_path.write_text("generated", encoding="utf-8")
        return RecordWriteResult(
            output_path=output_path,
            status="generated",
            group_count=1,
            warning_count=0,
            warnings=(),
        )


class _UnavailableFeeWriter:
    def generate(self, **_kwargs):
        raise OfficeAutomationUnavailable("Excel COM automation is required.")
