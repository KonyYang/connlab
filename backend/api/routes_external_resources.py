"""External resource registry API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import (
    get_external_resource_service,
    get_ltr_workbook_local_config_service,
    get_local_path_picker_service,
)
from backend.application.external_resource_service import (
    ExternalResourceNotFoundError,
    ExternalResourceService,
)
from backend.application.ltr_workbook_local_config_service import (
    LtrWorkbookLocalConfigService,
)
from backend.application.local_path_picker_service import LocalPathPickerService
from backend.domain import ExternalResource, ExternalResourceType


router = APIRouter(tags=["external-resources"])


class ExternalResourceUpsertRequest(BaseModel):
    """Request body for registering an external resource."""

    path: str = Field(min_length=1)
    active: bool = True


class ExternalResourceResponse(BaseModel):
    """External resource registry response."""

    resource_id: str
    resource_type: ExternalResourceType
    path: str
    active: bool
    validation_status: str
    last_validated_at: str | None
    validation_failure_reason: str | None


class ExternalResourcePickResponse(BaseModel):
    """Native picker selection response."""

    path: str | None


@router.get(
    "/api/external-resources",
    response_model=list[ExternalResourceResponse],
)
def list_external_resources(
    service: ExternalResourceService = Depends(get_external_resource_service),
) -> list[ExternalResourceResponse]:
    """Return registered external resources."""
    return [_to_response(resource) for resource in service.list_resources()]


@router.put(
    "/api/external-resources/{resource_type}",
    response_model=ExternalResourceResponse,
)
def upsert_external_resource(
    resource_type: ExternalResourceType,
    request: ExternalResourceUpsertRequest,
    service: ExternalResourceService = Depends(get_external_resource_service),
    ltr_config: LtrWorkbookLocalConfigService = Depends(
        get_ltr_workbook_local_config_service
    ),
) -> ExternalResourceResponse:
    """Register or update an external resource path."""
    resource = service.upsert_resource(resource_type, Path(request.path), request.active)
    if resource_type is ExternalResourceType.LTR_WORKBOOK:
        ltr_config.sync_workbook_path(resource.path)
    return _to_response(resource)


@router.post(
    "/api/external-resources/{resource_type}/validate",
    response_model=ExternalResourceResponse,
)
def validate_external_resource(
    resource_type: ExternalResourceType,
    service: ExternalResourceService = Depends(get_external_resource_service),
) -> ExternalResourceResponse:
    """Validate one registered external resource."""
    try:
        return _to_response(service.validate_resource(resource_type))
    except ExternalResourceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/api/external-resources/{resource_type}/pick",
    response_model=ExternalResourcePickResponse,
)
def pick_external_resource_path(
    resource_type: ExternalResourceType,
    service: LocalPathPickerService = Depends(get_local_path_picker_service),
) -> ExternalResourcePickResponse:
    """Open a native picker for one external resource path."""
    selected = service.pick_path(resource_type)
    return ExternalResourcePickResponse(path=str(selected) if selected else None)


def _to_response(resource: ExternalResource) -> ExternalResourceResponse:
    """Convert a domain resource to an API response."""
    return ExternalResourceResponse(
        resource_id=resource.resource_id,
        resource_type=resource.resource_type,
        path=str(resource.path),
        active=resource.active,
        validation_status=resource.validation_status.value,
        last_validated_at=resource.last_validated_at,
        validation_failure_reason=resource.validation_failure_reason,
    )
