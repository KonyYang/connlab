"""Project evidence placement API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.api.dependencies import get_evidence_placement_service
from backend.application.evidence_placement_service import (
    EvidencePlacementConflictError,
    EvidencePlacementError,
    EvidencePlacementNotFoundError,
    EvidencePlacementResult,
    EvidencePlacementService,
)
from backend.application.project_lifecycle_service import (
    ProjectLifecycleError,
    ProjectLifecycleNotFoundError,
)
from backend.modules.folder import EvidencePlacementItem, EvidencePlacementPlan


router = APIRouter(prefix="/api/projects/{project_id}/evidence", tags=["evidence"])


class EvidencePlacementItemResponse(BaseModel):
    """One evidence placement preview item."""

    asset_id: str
    category: str
    source_path: str
    target_path: str
    missing_source: bool
    target_exists: bool
    duplicate_target: bool
    conflict: bool


class EvidencePlacementPlanResponse(BaseModel):
    """Evidence placement preview response."""

    project_id: str
    project_folder_path: str
    evidence_root_path: str
    conflict: bool
    items: list[EvidencePlacementItemResponse]
    conflicts: list[str]
    warnings: list[str]


class EvidencePlacementResultResponse(BaseModel):
    """Evidence placement execution response."""

    plan: EvidencePlacementPlanResponse
    copied_paths: list[str]


@router.post("/placement-preview", response_model=EvidencePlacementPlanResponse)
def preview_evidence_placement(
    project_id: str,
    service: EvidencePlacementService = Depends(get_evidence_placement_service),
) -> EvidencePlacementPlanResponse:
    """Preview project evidence placement without copying files."""
    try:
        return _plan_response(service.preview_project(project_id))
    except (EvidencePlacementNotFoundError, ProjectLifecycleNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (EvidencePlacementError, ProjectLifecycleError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/place",
    response_model=EvidencePlacementResultResponse,
    status_code=status.HTTP_201_CREATED,
)
def place_evidence(
    project_id: str,
    service: EvidencePlacementService = Depends(get_evidence_placement_service),
) -> EvidencePlacementResultResponse:
    """Copy project evidence into the generated project folder without overwrite."""
    try:
        return _result_response(service.place_project(project_id))
    except (EvidencePlacementNotFoundError, ProjectLifecycleNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except EvidencePlacementConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (EvidencePlacementError, ProjectLifecycleError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _result_response(result: EvidencePlacementResult) -> EvidencePlacementResultResponse:
    """Convert an execution result to API response."""
    return EvidencePlacementResultResponse(
        plan=_plan_response(result.plan),
        copied_paths=[str(path) for path in result.copied_paths],
    )


def _plan_response(plan: EvidencePlacementPlan) -> EvidencePlacementPlanResponse:
    """Convert a placement plan to API response."""
    return EvidencePlacementPlanResponse(
        project_id=plan.project_id,
        project_folder_path=str(plan.project_folder_path),
        evidence_root_path=str(plan.evidence_root_path),
        conflict=plan.conflict,
        items=[_item_response(item) for item in plan.items],
        conflicts=list(plan.conflicts),
        warnings=list(plan.warnings),
    )


def _item_response(item: EvidencePlacementItem) -> EvidencePlacementItemResponse:
    """Convert one placement item to API response."""
    return EvidencePlacementItemResponse(
        asset_id=item.asset_id,
        category=item.category.value,
        source_path=str(item.source_path),
        target_path=str(item.target_path),
        missing_source=item.missing_source,
        target_exists=item.target_exists,
        duplicate_target=item.duplicate_target,
        conflict=item.conflict,
    )
