"""Project test-plan source candidate and preview-by-candidate API routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import (
    get_project_test_plan_matrix_preview_service,
    get_project_test_plan_source_candidate_service,
)
from backend.api.routes_project_test_plan import (
    MatrixPreviewResponse,
    _prepare_preview_pdf_artifact,
    _preview_response,
    _preview_response_source,
)
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


class MatrixResolvedDirectoryCandidateResponse(BaseModel):
    """One path-free candidate from the current resolved directory."""

    candidate_id: str
    file_name: str


class MatrixSourceCandidatesResponse(BaseModel):
    """Project-scoped candidate source list response."""

    project_id: str
    view: Literal["registered_assets", "resolved_directory"]
    source_title: str
    candidates: list[
        MatrixSourceCandidateResponse | MatrixResolvedDirectoryCandidateResponse
    ]
    warnings: list[str]
    preferred_import_directory: str | None
    preferred_import_directory_source: str


@router.get("", response_model=MatrixSourceCandidatesResponse)
def list_project_test_plan_source_candidates(
    project_id: str,
    view: Literal["registered_assets", "resolved_directory"] = "registered_assets",
    service: ProjectTestPlanSourceCandidateService = Depends(
        get_project_test_plan_source_candidate_service
    ),
) -> MatrixSourceCandidatesResponse:
    """List project Matrix source candidates derived from project file assets."""
    try:
        if view == "resolved_directory":
            resolved = service.list_resolved_directory_candidates(project_id)
            return MatrixSourceCandidatesResponse(
                project_id=resolved.project_id,
                view=view,
                source_title=resolved.source_title,
                candidates=[
                    MatrixResolvedDirectoryCandidateResponse(
                        candidate_id=item.candidate_id,
                        file_name=item.file_name,
                    )
                    for item in resolved.candidates
                ],
                warnings=list(resolved.warnings),
                preferred_import_directory=None,
                preferred_import_directory_source=resolved.source_directory_kind,
            )
        result = service.list_source_candidates(project_id)
    except ProjectTestPlanSourceCandidateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectTestPlanSourceCandidateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MatrixSourceCandidatesResponse(
        project_id=result.project_id,
        view=view,
        source_title="Project source files",
        candidates=[_candidate_response(item) for item in result.candidates],
        warnings=list(result.warnings),
        preferred_import_directory=(
            str(result.preferred_import_directory)
            if result.preferred_import_directory is not None
            else None
        ),
        preferred_import_directory_source=result.preferred_import_directory_source,
    )


@router.post("/{source_asset_id}/matrix-preview", response_model=MatrixPreviewResponse)
def preview_project_test_plan_matrix_from_candidate(
    project_id: str,
    source_asset_id: str,
    view: Literal["registered_assets", "resolved_directory"] = "registered_assets",
    source_candidate_service: ProjectTestPlanSourceCandidateService = Depends(
        get_project_test_plan_source_candidate_service
    ),
    matrix_preview_service: ProjectTestPlanMatrixPreviewService = Depends(
        get_project_test_plan_matrix_preview_service
    ),
) -> MatrixPreviewResponse:
    """Preview Matrix from one selected project candidate source asset."""
    try:
        source_path = (
            source_candidate_service.get_resolved_directory_candidate_source_path(
                project_id=project_id,
                candidate_id=source_asset_id,
            )
            if view == "resolved_directory"
            else source_candidate_service.get_candidate_source_path(
                project_id=project_id,
                source_asset_id=source_asset_id,
            )
        )
        preview_pdf_token, table_locations = _prepare_preview_pdf_artifact(
            matrix_preview_service,
            source_path,
            require_token=False,
        )
        preview = matrix_preview_service.preview_from_path(
            MatrixPreviewFromPathCommand(
                source_path=source_path,
                project_id=project_id,
            ),
            preview_pdf_token=preview_pdf_token,
            table_locations=table_locations,
        )
    except ProjectTestPlanSourceCandidateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectTestPlanSourceCandidateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ProjectTestPlanMatrixPreviewError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _preview_response(_preview_response_source(preview, source_path))


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
