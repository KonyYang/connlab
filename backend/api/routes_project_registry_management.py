"""HTTP contracts for recoverable project record management."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_project_registry_management_service
from backend.application.project_registry_models import (
    ProjectRegistryEntry, ProjectRegistryPreview, ProjectRegistryConflict, ProjectRegistryNotFound,
)

router = APIRouter(prefix="/api/project-registry", tags=["project-registry"])


class TrashRequest(BaseModel):
    token: str = Field(min_length=1)
    reason: str = Field(min_length=1, max_length=2000)
    actor: str | None = Field(default=None, max_length=255)


class RestoreRequest(BaseModel):
    token: str = Field(min_length=1)
    destination: Literal["active", "history"] = "active"
    replace_conflicts: bool = False
    actor: str | None = Field(default=None, max_length=255)


def _call(action):
    try:
        return action()
    except ProjectRegistryNotFound as exc:
        raise HTTPException(404, detail={"code": "project_registry_not_found", "message": str(exc)}) from exc
    except ProjectRegistryConflict as exc:
        raise HTTPException(409, detail={"code": exc.code, "message": str(exc)}) from exc
    except ValueError as exc:
        raise HTTPException(409, detail={"code": "project_registry_invalid_action", "message": str(exc)}) from exc


@router.get("/entries", response_model=list[ProjectRegistryEntry])
def entries(location: Literal["trash", "history"], service=Depends(get_project_registry_management_service)):
    return _call(lambda: service.list_entries(location))


@router.get("/{project_id}/preview", response_model=ProjectRegistryPreview)
def preview(project_id: str, action: Literal["trash", "restore"], service=Depends(get_project_registry_management_service)):
    return _call(lambda: service.preview(project_id, action))


@router.post("/{project_id}/trash", response_model=ProjectRegistryEntry)
def trash(project_id: str, request: TrashRequest, service=Depends(get_project_registry_management_service)):
    return _call(lambda: service.trash(project_id, **request.model_dump()))


@router.post("/{project_id}/restore", response_model=ProjectRegistryEntry)
def restore(project_id: str, request: RestoreRequest, service=Depends(get_project_registry_management_service)):
    return _call(lambda: service.restore(project_id, **request.model_dump()))
