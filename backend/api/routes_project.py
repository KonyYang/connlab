"""Project API routes."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from backend.api.dependencies import get_project_service
from backend.application.project_service import (
    CreateProjectCommand,
    ProjectNotFoundError,
    ProjectService,
)
from backend.domain import Project


router = APIRouter(prefix="/api/projects", tags=["projects"])


class ProjectCreateRequest(BaseModel):
    """Request body for creating a project."""

    project_no: str = Field(min_length=1)
    product_name: str = Field(min_length=1)
    requestor: str = Field(min_length=1)
    business_unit: str | None = None


class ProjectResponse(BaseModel):
    """Typed project response returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    project_id: str
    project_no: str
    product_name: str
    requestor: str
    status: str
    business_unit: str | None = None
    created_on: date | None = None


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    request: ProjectCreateRequest,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Create a project."""
    project = service.create_project(
        CreateProjectCommand(
            project_no=request.project_no,
            product_name=request.product_name,
            requestor=request.requestor,
            business_unit=request.business_unit,
        )
    )
    return _to_response(project)


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    service: ProjectService = Depends(get_project_service),
) -> list[ProjectResponse]:
    """List projects."""
    return [_to_response(project) for project in service.list_projects()]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Get one project by ID."""
    try:
        return _to_response(service.get_project(project_id))
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _to_response(project: Project) -> ProjectResponse:
    """Convert a project domain object to an API response DTO."""
    return ProjectResponse(
        project_id=project.project_id,
        project_no=project.project_no,
        product_name=project.product_name,
        requestor=project.requestor,
        status=project.status.value,
        business_unit=project.business_unit,
        created_on=project.created_on,
    )
