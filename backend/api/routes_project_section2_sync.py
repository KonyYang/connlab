"""Structured Project Section 2 date sync API routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_project_section2_sync_service
from backend.application.project_section2_sync_service import (
    ProjectSection2FieldSync,
    ProjectSection2SyncAmbiguousTargetError,
    ProjectSection2SyncCommand,
    ProjectSection2SyncConflictError,
    ProjectSection2SyncProjectNotFoundError,
    ProjectSection2SyncReadinessError,
    ProjectSection2SyncResult,
    ProjectSection2SyncService,
    ProjectSection2SyncValidationError,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/section2-sync",
    tags=["project-section2-sync"],
)


ProjectSection2FieldStatusResponse = Literal[
    "will_change",
    "changed",
    "unchanged",
    "skipped_missing_source",
    "blocked_invalid_source",
]
ProjectSection2SyncStatusResponse = Literal["ready", "up_to_date", "partial", "blocked", "synced"]


class ProjectSection2SyncRequest(BaseModel):
    """Request body for syncing previewed Confirmed Matrix dates."""

    expected_confirmed_matrix_id: str = Field(min_length=1)
    expected_confirmed_revision: int = Field(ge=1)
    operator: str | None = None


class ProjectSection2FieldSyncResponse(BaseModel):
    """Field-level Section 2 sync response."""

    field_key: Literal["received_date", "estimated_completion_date"]
    source_field_key: Literal["sample_received_date", "estimated_completion_date"]
    source_value: str | None
    current_value: str | None
    next_value: str | None
    status: ProjectSection2FieldStatusResponse
    message: str


class ProjectSection2SyncResponse(BaseModel):
    """Preview or sync result for structured Section 2 dates."""

    project_id: str
    application_form_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    fields: list[ProjectSection2FieldSyncResponse]
    status: ProjectSection2SyncStatusResponse
    synced_at: str | None = None
    operator: str | None = None


@router.get("/preview", response_model=ProjectSection2SyncResponse)
def preview_project_section2_sync(
    project_id: str,
    service: ProjectSection2SyncService = Depends(get_project_section2_sync_service),
) -> ProjectSection2SyncResponse:
    """Preview structured Section 2 date changes from active Confirmed Matrix."""
    try:
        result = service.preview(ProjectSection2SyncCommand(project_id=project_id))
    except ProjectSection2SyncProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ProjectSection2SyncAmbiguousTargetError, ProjectSection2SyncReadinessError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _to_response(result)


@router.post("", response_model=ProjectSection2SyncResponse)
def sync_project_section2(
    project_id: str,
    request: ProjectSection2SyncRequest,
    service: ProjectSection2SyncService = Depends(get_project_section2_sync_service),
) -> ProjectSection2SyncResponse:
    """Sync structured Section 2 dates after preview identity is confirmed."""
    try:
        result = service.sync(
            ProjectSection2SyncCommand(
                project_id=project_id,
                expected_confirmed_matrix_id=request.expected_confirmed_matrix_id,
                expected_confirmed_revision=request.expected_confirmed_revision,
                operator=request.operator,
            )
        )
    except ProjectSection2SyncProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ProjectSection2SyncAmbiguousTargetError, ProjectSection2SyncReadinessError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProjectSection2SyncConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProjectSection2SyncValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_response(result)


def _to_response(result: ProjectSection2SyncResult) -> ProjectSection2SyncResponse:
    return ProjectSection2SyncResponse(
        project_id=result.project_id,
        application_form_id=result.application_form_id,
        confirmed_matrix_id=result.confirmed_matrix_id,
        confirmed_revision=result.confirmed_revision,
        fields=[_field_response(field) for field in result.fields],
        status=result.status,
        synced_at=result.synced_at,
        operator=result.operator,
    )


def _field_response(field: ProjectSection2FieldSync) -> ProjectSection2FieldSyncResponse:
    return ProjectSection2FieldSyncResponse(
        field_key=field.field_key,
        source_field_key=field.source_field_key,
        source_value=field.source_value,
        current_value=field.current_value,
        next_value=field.next_value,
        status=field.status,
        message=field.message,
    )
