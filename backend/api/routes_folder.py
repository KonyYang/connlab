"""Project folder preview and generation API routes."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.api.dependencies import get_folder_service
from backend.application.folder_service import (
    FolderCommand,
    FolderConflictError,
    FolderError,
    FolderNotFoundError,
    FolderService,
)
from backend.application.project_lifecycle_service import (
    ProjectLifecycleError,
    ProjectLifecycleNotFoundError,
)
from backend.modules.folder import FolderGenerationResult, FolderPlan, FolderPlanItem


router = APIRouter(prefix="/api/projects/{project_id}/folder", tags=["folder"])


class FolderRequest(BaseModel):
    """Request body for folder preview and generation."""

    template_path: str = Field(min_length=1)
    target_root: str = Field(min_length=1)
    dl_number: str | None = None
    plan_date: date | None = None


class FolderPlanItemResponse(BaseModel):
    """One folder preview item response."""

    source_path: str
    target_path: str
    item_type: str
    conflict: bool


class FolderPlanResponse(BaseModel):
    """Folder preview response."""

    project_folder_path: str
    conflict: bool
    items: list[FolderPlanItemResponse]


class FolderGenerationResponse(BaseModel):
    """Folder generation response."""

    folder_id: str
    project_folder_path: str
    generated_paths: list[str]


@router.post("/preview", response_model=FolderPlanResponse)
def preview_folder(
    project_id: str,
    request: FolderRequest,
    service: FolderService = Depends(get_folder_service),
) -> FolderPlanResponse:
    """Preview project folder generation."""
    try:
        return _plan_response(service.preview_folder(project_id, _command(request)))
    except (FolderNotFoundError, ProjectLifecycleNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (FolderError, ProjectLifecycleError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/generate",
    response_model=FolderGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_folder(
    project_id: str,
    request: FolderRequest,
    service: FolderService = Depends(get_folder_service),
) -> FolderGenerationResponse:
    """Generate project folder from template."""
    try:
        record = service.generate_folder(project_id, _command(request))
        return _generation_response(record.record.folder_id, record.result)
    except (FolderNotFoundError, ProjectLifecycleNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FolderConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (FolderError, ProjectLifecycleError, ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _command(request: FolderRequest) -> FolderCommand:
    """Convert API request to application command."""
    return FolderCommand(
        template_path=Path(request.template_path),
        target_root=Path(request.target_root),
        dl_number=request.dl_number,
        plan_date=request.plan_date,
    )


def _plan_response(plan: FolderPlan) -> FolderPlanResponse:
    """Convert a folder plan to response DTO."""
    return FolderPlanResponse(
        project_folder_path=str(plan.project_folder_path),
        conflict=plan.conflict,
        items=[_item_response(item) for item in plan.items],
    )


def _item_response(item: FolderPlanItem) -> FolderPlanItemResponse:
    """Convert a folder plan item to response DTO."""
    return FolderPlanItemResponse(
        source_path=str(item.source_path),
        target_path=str(item.target_path),
        item_type=item.item_type,
        conflict=item.conflict,
    )


def _generation_response(
    folder_id: str,
    result: FolderGenerationResult,
) -> FolderGenerationResponse:
    """Convert generation result to response DTO."""
    return FolderGenerationResponse(
        folder_id=folder_id,
        project_folder_path=str(result.project_folder_path),
        generated_paths=[str(path) for path in result.generated_paths],
    )
