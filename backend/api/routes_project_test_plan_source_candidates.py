"""Project test-plan source candidate and preview-by-candidate API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import (
    get_project_test_plan_matrix_preview_service,
    get_project_test_plan_source_candidate_service,
)
from backend.api.routes_project_test_plan import MatrixPreviewResponse, _preview_response
from backend.application.project_test_plan_matrix_preview_service import (
    MatrixPreviewFromPathCommand,
    ProjectTestPlanMatrixPreviewError,
    ProjectTestPlanMatrixPreviewService,
)
from backend.application.project_test_plan_source_candidate_service import (
    ProjectTestPlanSourceCandidate,
    ProjectTestPlanSourceCandidateError,
    ProjectTestPlanSourceCandidateNotFoundError,
    ProjectTestPlanSourceCandidateService,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/test-plan/source-candidates",
    tags=["project-test-plan-source-candidates"],
)


class MatrixSourceCandidateResponse(BaseModel):
    """One project source candidate in API response."""

    source_asset_id: str
    original_name: str
    extension: str
    asset_type: str
    candidate_kind: str
    reason: str
    stored_file_available: bool


class MatrixSourceCandidatesResponse(BaseModel):
    """Project-scoped candidate source list response."""

    project_id: str
    candidates: list[MatrixSourceCandidateResponse]
    warnings: list[str]


@router.get("", response_model=MatrixSourceCandidatesResponse)
def list_project_test_plan_source_candidates(
    project_id: str,
    service: ProjectTestPlanSourceCandidateService = Depends(
        get_project_test_plan_source_candidate_service
    ),
) -> MatrixSourceCandidatesResponse:
    """List project Matrix source candidates derived from project file assets."""
    try:
        result = service.list_source_candidates(project_id)
    except ProjectTestPlanSourceCandidateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return MatrixSourceCandidatesResponse(
        project_id=result.project_id,
        candidates=[_candidate_response(item) for item in result.candidates],
        warnings=list(result.warnings),
    )


@router.post("/{source_asset_id}/matrix-preview", response_model=MatrixPreviewResponse)
def preview_project_test_plan_matrix_from_candidate(
    project_id: str,
    source_asset_id: str,
    source_candidate_service: ProjectTestPlanSourceCandidateService = Depends(
        get_project_test_plan_source_candidate_service
    ),
    matrix_preview_service: ProjectTestPlanMatrixPreviewService = Depends(
        get_project_test_plan_matrix_preview_service
    ),
) -> MatrixPreviewResponse:
    """Preview Matrix from one selected project candidate source asset."""
    try:
        source_path = source_candidate_service.get_candidate_source_path(
            project_id=project_id,
            source_asset_id=source_asset_id,
        )
        preview = matrix_preview_service.preview_from_path(
            MatrixPreviewFromPathCommand(
                source_path=source_path,
                project_id=project_id,
            )
        )
    except ProjectTestPlanSourceCandidateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectTestPlanSourceCandidateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ProjectTestPlanMatrixPreviewError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _preview_response(preview)


def _candidate_response(
    candidate: ProjectTestPlanSourceCandidate,
) -> MatrixSourceCandidateResponse:
    return MatrixSourceCandidateResponse(
        source_asset_id=candidate.source_asset_id,
        original_name=candidate.original_name,
        extension=candidate.extension,
        asset_type=candidate.asset_type.value,
        candidate_kind=candidate.candidate_kind,
        reason=candidate.reason,
        stored_file_available=candidate.stored_file_available,
    )
