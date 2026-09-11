"""Start/read/resume transport; the browser never owns generation continuation."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_project_folder_generation_service
from backend.api.diagnostic_route import DiagnosticRoute

router = APIRouter(prefix="/api/projects/{project_id}/project-folder/generation", tags=["project-folder-generation"], route_class=DiagnosticRoute)


class GenerationStartRequest(BaseModel):
    expected_context: str
    request_id: str = Field(min_length=1, max_length=100)
    conflict_strategy: Literal[
        "continue_existing", "backup_and_recreate", "overwrite_rebuild"
    ] | None = None
    replaces_operation_id: str | None = None


class GenerationResumeRequest(BaseModel):
    operation_id: str


class GenerationResponse(BaseModel):
    project_id: str
    operation_id: str
    status: Literal["queued", "running", "blocked", "interrupted", "completed"]
    step: int
    completed_steps: list[str]
    message: str | None
    can_restart: bool = False


def _call(action):
    try:
        return action()
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=503, detail="Generation storage is unavailable. Review the configured folder and retry.") from exc


@router.get("/preview")
def preview(project_id: str, service=Depends(get_project_folder_generation_service)):
    return _call(lambda: service.preview(project_id))


@router.get("", response_model=GenerationResponse | None)
def read(project_id: str, service=Depends(get_project_folder_generation_service)):
    return _call(lambda: service.read(project_id))


@router.post("/start", response_model=GenerationResponse, status_code=202)
def start(project_id: str, request: GenerationStartRequest, service=Depends(get_project_folder_generation_service)):
    return _call(lambda: service.start(project_id, request.conflict_strategy, request.expected_context, request.request_id,
                                     replaces_operation_id=request.replaces_operation_id))


@router.post("/resume", response_model=GenerationResponse, status_code=202)
def resume(project_id: str, request: GenerationResumeRequest, service=Depends(get_project_folder_generation_service)):
    return _call(lambda: service.resume(project_id, request.operation_id))
