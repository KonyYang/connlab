"""Read-only Section 2 completion preview API routes."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_section2_completion_preview_service
from backend.application.section2_completion_preview_service import (
    Section2CompletionPreview,
    Section2CompletionPreviewCommand,
    Section2CompletionPreviewError,
    Section2CompletionPreviewNotFoundError,
    Section2CompletionPreviewService,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/test-plan/drafts/{draft_id}",
    tags=["section2-preview"],
)


class Section2CompletionPreviewRequest(BaseModel):
    """Request body for read-only Section 2 completion preview."""

    received_date: date
    lab: str | None = None
    assigned_personnel: str | None = None
    sample_condition: str | None = None
    sample_preparation_days: int = Field(default=1, ge=0)
    test_group_scheduling_buffer_days: int = Field(default=1, ge=0)
    report_drafting_days: int = Field(default=3, ge=0)
    review_days: int = Field(default=1, ge=0)


class Section2DurationSummaryResponse(BaseModel):
    """Duration components used by the Section 2 preview response."""

    sample_preparation_days: int
    test_group_scheduling_buffer_days: int
    explicit_test_duration_days: int
    report_drafting_days: int
    review_days: int
    total_estimated_days: int
    duration_basis: str


class Section2CompletionPreviewResponse(BaseModel):
    """Read-only Section 2 completion preview response."""

    project_id: str
    draft_id: str
    source_document_name: str
    received_date: date
    estimated_completion_date: date
    lab: str | None
    assigned_personnel: str | None
    sample_condition: str | None
    test_demand_summary: str
    duration_summary: Section2DurationSummaryResponse
    warnings: list[str]


@router.post("/section2-preview", response_model=Section2CompletionPreviewResponse)
def preview_section2_completion(
    project_id: str,
    draft_id: str,
    request: Section2CompletionPreviewRequest,
    service: Section2CompletionPreviewService = Depends(
        get_section2_completion_preview_service
    ),
) -> Section2CompletionPreviewResponse:
    """Preview Section 2 values without writing the application form."""
    try:
        preview = service.preview(
            Section2CompletionPreviewCommand(
                project_id=project_id,
                draft_id=draft_id,
                received_date=request.received_date,
                lab=request.lab,
                assigned_personnel=request.assigned_personnel,
                sample_condition=request.sample_condition,
                sample_preparation_days=request.sample_preparation_days,
                test_group_scheduling_buffer_days=(
                    request.test_group_scheduling_buffer_days
                ),
                report_drafting_days=request.report_drafting_days,
                review_days=request.review_days,
            )
        )
    except Section2CompletionPreviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Section2CompletionPreviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(preview)


def _to_response(
    preview: Section2CompletionPreview,
) -> Section2CompletionPreviewResponse:
    """Convert an application preview DTO to an API response."""
    return Section2CompletionPreviewResponse(
        project_id=preview.project_id,
        draft_id=preview.draft_id,
        source_document_name=preview.source_document_name,
        received_date=preview.received_date,
        estimated_completion_date=preview.estimated_completion_date,
        lab=preview.lab,
        assigned_personnel=preview.assigned_personnel,
        sample_condition=preview.sample_condition,
        test_demand_summary=preview.test_demand_summary,
        duration_summary=Section2DurationSummaryResponse(
            sample_preparation_days=preview.duration_summary.sample_preparation_days,
            test_group_scheduling_buffer_days=(
                preview.duration_summary.test_group_scheduling_buffer_days
            ),
            explicit_test_duration_days=(
                preview.duration_summary.explicit_test_duration_days
            ),
            report_drafting_days=preview.duration_summary.report_drafting_days,
            review_days=preview.duration_summary.review_days,
            total_estimated_days=preview.duration_summary.total_estimated_days,
            duration_basis=preview.duration_summary.duration_basis,
        ),
        warnings=list(preview.warnings),
    )
