"""Project test-plan preview API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_project_test_plan_matrix_preview_service
from backend.application.project_test_plan_matrix_preview_service import (
    MatrixPreviewFromPathCommand,
    ProjectTestPlanMatrixPreview,
    ProjectTestPlanMatrixPreviewError,
    ProjectTestPlanMatrixPreviewService,
)
from backend.modules.test_plan import MatrixGroupPreview, MatrixStepPreview


router = APIRouter(tags=["project-test-plan"])


class MatrixPreviewFromPathRequest(BaseModel):
    """Request body for local-path Matrix preview calibration."""

    source_path: str = Field(min_length=1)
    project_id: str | None = None


class TestStepPreviewResponse(BaseModel):
    """One test step in a Matrix preview response."""

    sequence: int
    test_item: str
    source_section: str | None
    condition_summary: str | None
    method_summary: str | None
    reference_standard: str | None
    judgement_criteria: str | None
    estimated_duration_hint: str | None
    duration_source: str | None
    duration_status: str
    source_table_index: int
    source_row_index: int
    warnings: list[str]


class TestGroupPreviewResponse(BaseModel):
    """One test group in a Matrix preview response."""

    group_key: str
    group_label: str
    source_table_index: int
    extraction_status: str
    steps: list[TestStepPreviewResponse]


class MatrixPreviewResponse(BaseModel):
    """Read-only Matrix preview API response."""

    project_id: str | None
    source_document_path: str
    source_document_name: str
    source_format: str
    capability_status: str
    generated_at: str
    selected_table_index: int | None
    groups: list[TestGroupPreviewResponse]
    warnings: list[str]
    blockers: list[str]


@router.post(
    "/api/test-plan/matrix-preview-from-path",
    response_model=MatrixPreviewResponse,
)
def preview_matrix_from_path(
    request: MatrixPreviewFromPathRequest,
    service: ProjectTestPlanMatrixPreviewService = Depends(
        get_project_test_plan_matrix_preview_service
    ),
) -> MatrixPreviewResponse:
    """Return a read-only Matrix preview for a local product specification path."""
    try:
        preview = service.preview_from_path(
            MatrixPreviewFromPathCommand(
                source_path=Path(request.source_path),
                project_id=request.project_id,
            )
        )
    except ProjectTestPlanMatrixPreviewError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _preview_response(preview)


def _preview_response(preview: ProjectTestPlanMatrixPreview) -> MatrixPreviewResponse:
    """Convert an application preview to an API response."""
    return MatrixPreviewResponse(
        project_id=preview.project_id,
        source_document_path=str(preview.source_document_path),
        source_document_name=preview.source_document_name,
        source_format=preview.source_format,
        capability_status=preview.capability_status,
        generated_at=preview.generated_at,
        selected_table_index=preview.selected_table_index,
        groups=[_group_response(group) for group in preview.groups],
        warnings=list(preview.warnings),
        blockers=list(preview.blockers),
    )


def _group_response(group: MatrixGroupPreview) -> TestGroupPreviewResponse:
    """Convert one Matrix group to an API response."""
    return TestGroupPreviewResponse(
        group_key=group.group_key,
        group_label=group.group_label,
        source_table_index=group.source_table_index,
        extraction_status=group.extraction_status,
        steps=[_step_response(step) for step in group.steps],
    )


def _step_response(step: MatrixStepPreview) -> TestStepPreviewResponse:
    """Convert one Matrix step to an API response."""
    return TestStepPreviewResponse(
        sequence=step.sequence,
        test_item=step.test_item,
        source_section=step.source_section,
        condition_summary=step.condition_summary,
        method_summary=step.method_summary,
        reference_standard=step.reference_standard,
        judgement_criteria=step.judgement_criteria,
        estimated_duration_hint=step.estimated_duration_hint,
        duration_source=step.duration_source,
        duration_status=step.duration_status,
        source_table_index=step.source_table_index,
        source_row_index=step.source_row_index,
        warnings=list(step.warnings),
    )
