"""Read-only test record and fee dataset preview API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_test_record_fee_dataset_preview_service
from backend.application.test_record_fee_dataset_preview_service import (
    FeeDataset,
    FeeLineItemDataset,
    TestRecordDataset,
    TestRecordFeeDatasetPreview,
    TestRecordFeeDatasetPreviewCommand,
    TestRecordFeeDatasetPreviewError,
    TestRecordFeeDatasetPreviewNotFoundError,
    TestRecordFeeDatasetPreviewService,
    TestRecordGroupDataset,
    TestRecordStepDataset,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/test-plan/drafts/{draft_id}",
    tags=["test-record-fee-dataset-preview"],
)


class TestRecordFeeDatasetPreviewRequest(BaseModel):
    """Request body for dataset preview."""

    include_test_record_dataset: bool = True
    include_fee_dataset: bool = True


class TestRecordStepResponse(BaseModel):
    """One test step row for future test record generation."""

    sequence: int | None
    test_item: str | None
    condition_summary: str | None
    method_summary: str | None
    reference_standard: str | None
    judgement_criteria: str | None
    duration_hint: str | None
    source_section: str | None
    source_table_index: int | None
    source_row_index: int | None
    warnings: list[str]


class TestRecordGroupResponse(BaseModel):
    """One test group for future test record generation."""

    group_key: str
    group_label: str
    source_table_index: int | None
    steps: list[TestRecordStepResponse]
    warnings: list[str]


class TestRecordDatasetResponse(BaseModel):
    """Structured test record input dataset preview."""

    groups: list[TestRecordGroupResponse]


class FeeSummaryResponse(BaseModel):
    """Summary fields for fee evaluation preview."""

    group_count: int
    step_count: int
    explicit_duration_days: int


class FeeLineItemResponse(BaseModel):
    """One fee evaluation line candidate."""

    group_label: str
    sequence: int | None
    description: str
    duration_hint: str | None
    quantity_basis: str
    pricing_status: str
    warnings: list[str]


class FeeDatasetResponse(BaseModel):
    """Structured fee evaluation input dataset preview."""

    summary: FeeSummaryResponse
    line_items: list[FeeLineItemResponse]


class TestRecordFeeDatasetPreviewResponse(BaseModel):
    """Read-only dataset preview response."""

    project_id: str
    draft_id: str
    source_document_name: str
    test_record_dataset: TestRecordDatasetResponse | None
    fee_dataset: FeeDatasetResponse | None
    warnings: list[str]


@router.post(
    "/record-fee-dataset-preview",
    response_model=TestRecordFeeDatasetPreviewResponse,
)
def preview_record_fee_dataset(
    project_id: str,
    draft_id: str,
    request: TestRecordFeeDatasetPreviewRequest,
    service: TestRecordFeeDatasetPreviewService = Depends(
        get_test_record_fee_dataset_preview_service
    ),
) -> TestRecordFeeDatasetPreviewResponse:
    """Preview test-record and fee datasets without generating files."""
    try:
        preview = service.preview(
            TestRecordFeeDatasetPreviewCommand(
                project_id=project_id,
                draft_id=draft_id,
                include_test_record_dataset=request.include_test_record_dataset,
                include_fee_dataset=request.include_fee_dataset,
            )
        )
    except TestRecordFeeDatasetPreviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TestRecordFeeDatasetPreviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(preview)


def _to_response(
    preview: TestRecordFeeDatasetPreview,
) -> TestRecordFeeDatasetPreviewResponse:
    """Convert application preview DTO to API response."""
    return TestRecordFeeDatasetPreviewResponse(
        project_id=preview.project_id,
        draft_id=preview.draft_id,
        source_document_name=preview.source_document_name,
        test_record_dataset=(
            _test_record_dataset(preview.test_record_dataset)
            if preview.test_record_dataset is not None
            else None
        ),
        fee_dataset=(
            _fee_dataset(preview.fee_dataset)
            if preview.fee_dataset is not None
            else None
        ),
        warnings=list(preview.warnings),
    )


def _test_record_dataset(
    dataset: TestRecordDataset,
) -> TestRecordDatasetResponse:
    return TestRecordDatasetResponse(
        groups=[_test_record_group(group) for group in dataset.groups]
    )


def _test_record_group(group: TestRecordGroupDataset) -> TestRecordGroupResponse:
    return TestRecordGroupResponse(
        group_key=group.group_key,
        group_label=group.group_label,
        source_table_index=group.source_table_index,
        steps=[_test_record_step(step) for step in group.steps],
        warnings=list(group.warnings),
    )


def _test_record_step(step: TestRecordStepDataset) -> TestRecordStepResponse:
    return TestRecordStepResponse(
        sequence=step.sequence,
        test_item=step.test_item,
        condition_summary=step.condition_summary,
        method_summary=step.method_summary,
        reference_standard=step.reference_standard,
        judgement_criteria=step.judgement_criteria,
        duration_hint=step.duration_hint,
        source_section=step.source_section,
        source_table_index=step.source_table_index,
        source_row_index=step.source_row_index,
        warnings=list(step.warnings),
    )


def _fee_dataset(dataset: FeeDataset) -> FeeDatasetResponse:
    return FeeDatasetResponse(
        summary=FeeSummaryResponse(
            group_count=dataset.summary.group_count,
            step_count=dataset.summary.step_count,
            explicit_duration_days=dataset.summary.explicit_duration_days,
        ),
        line_items=[_fee_line_item(item) for item in dataset.line_items],
    )


def _fee_line_item(item: FeeLineItemDataset) -> FeeLineItemResponse:
    return FeeLineItemResponse(
        group_label=item.group_label,
        sequence=item.sequence,
        description=item.description,
        duration_hint=item.duration_hint,
        quantity_basis=item.quantity_basis,
        pricing_status=item.pricing_status,
        warnings=list(item.warnings),
    )
