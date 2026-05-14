"""API routes for persisted project output lineage/status records."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_project_output_record_service
from backend.application.project_output_record_service import (
    ProjectOutputRecordError,
    ProjectOutputRecordNotFoundError,
    ProjectOutputRecordService,
    RegisterProjectOutputCommand,
)
from backend.domain import (
    ProjectOutputKind,
    ProjectOutputSource,
    ProjectOutputStatus,
)


router = APIRouter(prefix="/api/projects/{project_id}/output-records", tags=["project-output-records"])


class ProjectOutputRecordRequest(BaseModel):
    """Request body for one persisted project output record."""

    output_kind: ProjectOutputKind
    status: ProjectOutputStatus
    source: ProjectOutputSource
    output_path: str | None = None
    draft_id: str | None = None
    note: str | None = None


class ProjectOutputRecordResponse(BaseModel):
    """Persisted project output record response."""

    output_record_id: str
    project_id: str
    draft_id: str | None
    draft_version: int | None
    output_kind: ProjectOutputKind
    output_path: str | None
    status: ProjectOutputStatus
    source: ProjectOutputSource
    created_at: str
    updated_at: str
    note: str | None


class ProjectOutputStatusItemResponse(BaseModel):
    """Project output kind status item for Workbench."""

    output_kind: ProjectOutputKind
    status: ProjectOutputStatus
    output_path: str | None
    source: ProjectOutputSource | None
    draft_id: str | None
    draft_version: int | None
    reason: str
    updated_at: str | None


class ProjectOutputStatusSummaryResponse(BaseModel):
    """Project output status summary for Workbench."""

    project_id: str
    active_draft_id: str | None
    active_draft_version: int | None
    items: list[ProjectOutputStatusItemResponse]


@router.post("", response_model=ProjectOutputRecordResponse, status_code=201)
def create_project_output_record(
    project_id: str,
    request: ProjectOutputRecordRequest,
    service: ProjectOutputRecordService = Depends(get_project_output_record_service),
) -> ProjectOutputRecordResponse:
    """Persist one Project output lineage/status record."""
    try:
        record = service.register_output(
            RegisterProjectOutputCommand(
                project_id=project_id,
                output_kind=request.output_kind,
                status=request.status,
                source=request.source,
                output_path=request.output_path,
                draft_id=request.draft_id,
                note=request.note,
            )
        )
    except ProjectOutputRecordNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectOutputRecordError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ProjectOutputRecordResponse(**asdict(record))


@router.get("", response_model=list[ProjectOutputRecordResponse])
def list_project_output_records(
    project_id: str,
    service: ProjectOutputRecordService = Depends(get_project_output_record_service),
) -> list[ProjectOutputRecordResponse]:
    """List persisted project output records."""
    try:
        return [ProjectOutputRecordResponse(**asdict(item)) for item in service.list_records(project_id)]
    except ProjectOutputRecordNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/status", response_model=ProjectOutputStatusSummaryResponse)
def get_project_output_status(
    project_id: str,
    service: ProjectOutputRecordService = Depends(get_project_output_record_service),
) -> ProjectOutputStatusSummaryResponse:
    """Return reload-safe project output status summary."""
    try:
        summary = service.get_status_summary(project_id)
    except ProjectOutputRecordNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ProjectOutputStatusSummaryResponse(
        project_id=summary.project_id,
        active_draft_id=summary.active_draft_id,
        active_draft_version=summary.active_draft_version,
        items=[ProjectOutputStatusItemResponse(**asdict(item)) for item in summary.items],
    )
