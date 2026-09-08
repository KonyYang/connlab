"""Project Schedule authority API."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_project_schedule_service
from backend.application.project_schedule_service import (
    ConfirmProjectScheduleCommand,
    ProjectScheduleConflictError,
    ProjectScheduleReadinessError,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/project-schedule",
    tags=["project-schedule"],
)


class ProjectScheduleSuggestionResponse(BaseModel):
    post_test_buffer_days: str
    test_start_date: str
    test_complete_date: str
    estimated_completion_date: str


class ProjectScheduleRevisionResponse(BaseModel):
    revision_id: str
    project_id: str
    revision_sequence: int
    state: str
    fingerprint: str
    matrix_input_fingerprint: str
    based_on_confirmed_matrix_id: str
    based_on_confirmed_matrix_revision: int
    based_on_basic_information_version: int
    sample_received_date: str
    post_test_buffer_days: str
    test_start_date: str
    test_complete_date: str
    estimated_completion_date: str
    confirmed_by: str
    confirmed_at: str
    superseded_at: str | None = None
    superseded_reason: str | None = None


class ProjectScheduleWorkspaceResponse(BaseModel):
    status: str
    project_id: str
    sample_received_date: str
    critical_group_id: str | None
    critical_group_days: str
    suggestion: ProjectScheduleSuggestionResponse
    confirmed_revision: ProjectScheduleRevisionResponse | None


class ConfirmProjectScheduleRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=255)
    expected_revision_id: str | None = Field(default=None, max_length=64)
    expected_fingerprint: str | None = Field(default=None, max_length=128)
    post_test_buffer_days: str = Field(max_length=64)
    test_start_date: str = Field(min_length=1, max_length=32)
    test_complete_date: str = Field(min_length=1, max_length=32)
    estimated_completion_date: str = Field(min_length=1, max_length=32)


@router.get("", response_model=ProjectScheduleWorkspaceResponse)
def get_project_schedule(project_id: str, service=Depends(get_project_schedule_service)):
    try:
        return asdict(service.get_workspace(project_id))
    except ProjectScheduleReadinessError as exc:
        _raise_readiness(exc)


@router.post("/confirm", response_model=ProjectScheduleRevisionResponse)
def confirm_project_schedule(
    project_id: str,
    request: ConfirmProjectScheduleRequest,
    service=Depends(get_project_schedule_service),
):
    try:
        revision = service.confirm(
            ConfirmProjectScheduleCommand(
                project_id=project_id,
                expected_revision_id=request.expected_revision_id,
                expected_fingerprint=request.expected_fingerprint,
                post_test_buffer_days=request.post_test_buffer_days,
                test_start_date=request.test_start_date,
                test_complete_date=request.test_complete_date,
                estimated_completion_date=request.estimated_completion_date,
                confirmed_by=request.actor,
            )
        )
    except ProjectScheduleConflictError as exc:
        raise HTTPException(
            409,
            detail={"code": "project_schedule_conflict", "message": str(exc)},
        ) from exc
    except (ProjectScheduleReadinessError, ValueError) as exc:
        _raise_readiness(exc)
    return asdict(revision)


def _raise_readiness(exc: Exception) -> None:
    raise HTTPException(
        422,
        detail={"code": "project_schedule_validation", "message": str(exc)},
    ) from exc
