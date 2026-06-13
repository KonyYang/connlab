"""Project API routes."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from backend.api.dependencies import (
    get_project_lifecycle_management_service,
    get_project_registry_summary_service,
    get_project_service,
)
from backend.application.project_lifecycle_management_service import (
    ProjectLifecycleManagementError,
    ProjectLifecycleManagementNotFoundError,
    ProjectLifecycleManagementService,
    ProjectStopCommand,
    ProjectStopResult,
    TemporaryProjectDeletePreview,
    TemporaryProjectDeleteResult,
)
from backend.application.project_registry_summary_service import (
    ProjectRegistryRow,
    ProjectRegistrySummaryService,
)
from backend.application.project_service import (
    CreateProjectCommand,
    CreateTemporaryProjectCommand,
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


class TemporaryProjectCreateRequest(BaseModel):
    """Request body for creating a temporary planning project."""

    request_summary: str | None = None
    sample_description: str | None = None
    test_item: str | None = None
    requestor: str | None = None
    source_asset_ids: list[str] = Field(default_factory=list)
    notes: str | None = None


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
    sample_description: str | None = None
    test_item: str | None = None
    temporary_source_asset_ids: list[str] = Field(default_factory=list)
    temporary_notes: str | None = None


class TemporaryProjectCreateResponse(BaseModel):
    """Response returned after creating a temporary planning project."""

    project_id: str
    display_project_id: str
    display_project_id_kind: str
    has_registered_ltr: bool
    status: str
    next_route: str


class TemporaryProjectDeletePreviewResponse(BaseModel):
    """Response for safe temporary project deletion preview."""

    project_id: str
    can_delete: bool
    blockers: list[str]
    warnings: list[str]
    recommended_action: str


class TemporaryProjectDeleteResponse(BaseModel):
    """Response returned after deleting a safe temporary project."""

    project_id: str
    deleted: bool
    deleted_temporary_context: bool


class ProjectStopRequest(BaseModel):
    """Request body for stopping a project."""

    reason: str | None = None
    operator: str | None = None


class ProjectStopResponse(BaseModel):
    """Response returned after stopping a project."""

    project_id: str
    previous_status: str
    status: str
    status_label: str
    reason: str
    audit_recorded: bool


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
    display_project_id: str
    display_project_id_kind: str
    has_registered_ltr: bool
    temporary_project_id: str | None = None
    registered_ltr_number: str | None = None
    temporary_source_asset_ids: list[str] = Field(default_factory=list)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    request: ProjectCreateRequest,
    service: ProjectService = Depends(get_project_service),
    registry_service: ProjectRegistrySummaryService = Depends(
        get_project_registry_summary_service
    ),
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
    return _to_response(project, registry_service.get_row(project.project_id))


@router.post(
    "/temporary",
    response_model=TemporaryProjectCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_temporary_project(
    request: TemporaryProjectCreateRequest,
    service: ProjectService = Depends(get_project_service),
    registry_service: ProjectRegistrySummaryService = Depends(
        get_project_registry_summary_service
    ),
) -> TemporaryProjectCreateResponse:
    """Create an active temporary planning project without registering an LTR."""
    project = service.create_temporary_project(
        CreateTemporaryProjectCommand(
            request_summary=request.request_summary,
            sample_description=request.sample_description,
            test_item=request.test_item,
            requestor=request.requestor,
            source_asset_ids=tuple(request.source_asset_ids),
            notes=request.notes,
        )
    )
    registry_row = registry_service.get_row(project.project_id)
    if registry_row is None:
        raise HTTPException(
            status_code=500,
            detail="Temporary project was created but registry identity could not be resolved.",
        )
    return TemporaryProjectCreateResponse(
        project_id=project.project_id,
        display_project_id=registry_row.display_project_id,
        display_project_id_kind=registry_row.display_project_id_kind,
        has_registered_ltr=registry_row.has_registered_ltr,
        status=project.status.value,
        next_route=f"/projects/{project.project_id}",
    )


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    service: ProjectService = Depends(get_project_service),
    registry_service: ProjectRegistrySummaryService = Depends(
        get_project_registry_summary_service
    ),
) -> list[ProjectResponse]:
    """List projects."""
    return [
        _to_response(project, registry_service.get_row(project.project_id))
        for project in service.list_projects()
    ]


@router.get("/registry", response_model=list[ProjectRegistryRowResponse])
def list_project_registry_rows(
    service: ProjectRegistrySummaryService = Depends(
        get_project_registry_summary_service
    ),
) -> list[ProjectRegistryRowResponse]:
    """List display-ready Project registry rows."""
    return [_to_registry_response(row) for row in service.list_rows()]


@router.get(
    "/{project_id}/delete-preview",
    response_model=TemporaryProjectDeletePreviewResponse,
)
def preview_temporary_project_delete(
    project_id: str,
    service: ProjectLifecycleManagementService = Depends(
        get_project_lifecycle_management_service
    ),
) -> TemporaryProjectDeletePreviewResponse:
    """Preview whether a temporary project can be safely deleted."""
    try:
        preview = service.preview_temporary_delete(project_id)
    except ProjectLifecycleManagementNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_delete_preview_response(preview)


@router.delete(
    "/{project_id}/temporary",
    response_model=TemporaryProjectDeleteResponse,
)
def delete_temporary_project(
    project_id: str,
    service: ProjectLifecycleManagementService = Depends(
        get_project_lifecycle_management_service
    ),
) -> TemporaryProjectDeleteResponse:
    """Delete one safe mistaken or duplicate temporary planning project."""
    try:
        result = service.delete_temporary_project(project_id)
    except ProjectLifecycleManagementNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectLifecycleManagementError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _to_delete_response(result)


@router.post("/{project_id}/stop", response_model=ProjectStopResponse)
def stop_project(
    project_id: str,
    request: ProjectStopRequest,
    service: ProjectLifecycleManagementService = Depends(
        get_project_lifecycle_management_service
    ),
) -> ProjectStopResponse:
    """Stop a project while preserving history."""
    try:
        result = service.stop_project(
            ProjectStopCommand(
                project_id=project_id,
                reason=request.reason,
                operator=request.operator,
            )
        )
    except ProjectLifecycleManagementNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_stop_response(result)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
    registry_service: ProjectRegistrySummaryService = Depends(
        get_project_registry_summary_service
    ),
) -> ProjectResponse:
    """Get one project by ID."""
    try:
        project = service.get_project(project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_response(project, registry_service.get_row(project_id))


def _to_response(
    project: Project,
    registry_row: ProjectRegistryRow | None = None,
) -> ProjectResponse:
    """Convert a project domain object to an API response DTO."""
    return ProjectResponse(
        project_id=project.project_id,
        project_no=project.project_no,
        product_name=project.product_name,
        requestor=project.requestor,
        status=project.status.value,
        business_unit=project.business_unit,
        created_on=project.created_on,
        sample_description=registry_row.sample_description if registry_row else None,
        test_item=registry_row.test_item if registry_row else None,
        temporary_source_asset_ids=(
            list(registry_row.temporary_source_asset_ids) if registry_row else []
        ),
        temporary_notes=(
            registry_row.notes
            if registry_row and registry_row.display_project_id_kind == "temporary"
            else None
        ),
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
        display_project_id=row.display_project_id,
        display_project_id_kind=row.display_project_id_kind,
        has_registered_ltr=row.has_registered_ltr,
        temporary_project_id=row.temporary_project_id,
        registered_ltr_number=row.registered_ltr_number,
        temporary_source_asset_ids=list(row.temporary_source_asset_ids),
    )


def _to_delete_preview_response(
    preview: TemporaryProjectDeletePreview,
) -> TemporaryProjectDeletePreviewResponse:
    """Convert safe-delete preview into an API response."""
    return TemporaryProjectDeletePreviewResponse(
        project_id=preview.project_id,
        can_delete=preview.can_delete,
        blockers=list(preview.blockers),
        warnings=list(preview.warnings),
        recommended_action=preview.recommended_action,
    )


def _to_delete_response(
    result: TemporaryProjectDeleteResult,
) -> TemporaryProjectDeleteResponse:
    """Convert delete result into an API response."""
    return TemporaryProjectDeleteResponse(
        project_id=result.project_id,
        deleted=result.deleted,
        deleted_temporary_context=result.deleted_temporary_context,
    )


def _to_stop_response(result: ProjectStopResult) -> ProjectStopResponse:
    """Convert stop result into an API response."""
    return ProjectStopResponse(
        project_id=result.project_id,
        previous_status=result.previous_status,
        status=result.status,
        status_label=result.status_label,
        reason=result.reason,
        audit_recorded=result.audit_recorded,
    )
