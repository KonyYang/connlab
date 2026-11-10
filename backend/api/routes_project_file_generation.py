"""Read, start and recover independently selected project-file generation."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from backend.api import dependencies as deps


def get_service():
    return deps.get_project_file_generation_service()


router = APIRouter(prefix="/api/projects/{project_id}/project-folder/files", tags=["project-file-generation"])


class FileChoice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    key: Literal["customer_feedback_form", "fee_form", "test_record", "test_status", "application_form", "llcr_record", "cr_record", "ir_dwv_record"]
    source_token: str | None = None
    action: Literal["generate_missing", "skip", "replace_with_backup"]


class StartFilesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str = Field(min_length=1, max_length=100)
    workspace_token: str
    items: list[FileChoice] = Field(min_length=1, max_length=8)


def _call(action):
    try:
        return action()
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    except OSError as exc:
        raise HTTPException(503, "File generation storage is unavailable. Restore access and retry.") from exc


@router.get("")
def preview(project_id: str, service=Depends(get_service)):
    return _call(lambda: service.preview(project_id))


@router.post("/start", status_code=202)
def start(project_id: str, request: StartFilesRequest, service=Depends(get_service)):
    return _call(lambda: service.start(project_id, request.model_dump()))


@router.get("/operations/{operation_id}")
def read(project_id: str, operation_id: str, service=Depends(get_service)):
    return _call(lambda: service.read(project_id, operation_id))


@router.post("/operations/{operation_id}/resume", status_code=202)
def resume(project_id: str, operation_id: str, service=Depends(get_service)):
    return _call(lambda: service.resume(project_id, operation_id))
