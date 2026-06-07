"""Project API routes."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from backend.api.dependencies import (
    get_project_registry_summary_service,
    get_project_service,
)
from backend.application.project_registry_summary_service import (
    ProjectRegistryRow,
    ProjectRegistrySummaryService,
)
from backend.application.project_service import (
    CreateProjectCommand,
    ProjectNotFoundError,
    ProjectService,
)
from backend.domain import Project


router = APIRouter(prefix="/api/projects", tags=["projects"])


class ProjectCreateRequest(BaseModel):
    """Request body for creating a project."""

    project_no: str | None = None
    product_name: str = Field(min_length=1)
    requestor: str = Field(min_length=1)
    business_unit: str | None = None


class ProjectResponse(BaseModel):
    """Typed project response returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    project_id: str
    project_no: str | None = None
    product_name: str
    requestor: str
    status: str
    business_unit: str | None = None
    created_on: date | None = None


class ProjectRegistryRowResponse(BaseModel):
    """Typed row returned by the Project registry summary endpoint."""

    project_id: str
    ltr_number: str | None = None
    sample_description: str | None = None
    test_item: str | None = None
    requestor: str
    business_unit: str | None = None
    status: str
    progress: int
    notes: str | None = None


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


@router.get("/registry", response_model=list[ProjectRegistryRowResponse])
def list_project_registry_rows(
    service: ProjectRegistrySummaryService = Depends(
        get_project_registry_summary_service
    ),
) -> list[ProjectRegistryRowResponse]:
    """List display-ready Project registry rows."""
    return [_to_registry_response(row) for row in service.list_rows()]


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


def _to_registry_response(row: ProjectRegistryRow) -> ProjectRegistryRowResponse:
    """Convert a registry application row to an API response DTO."""
    return ProjectRegistryRowResponse(
        project_id=row.project_id,
        ltr_number=row.ltr_number,
        sample_description=row.sample_description,
        test_item=row.test_item,
        requestor=row.requestor,
        business_unit=row.business_unit,
        status=row.status,
        progress=row.progress,
        notes=row.notes,
    )
