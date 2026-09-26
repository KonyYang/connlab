"""Project Schedule authority API."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_project_schedule_service
from backend.application.project_schedule_service import (
    ProjectScheduleProjectNotFoundError,
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
    based_on_confirmed_matrix_id: str | None
    based_on_confirmed_matrix_revision: int | None
    based_on_basic_information_version: int | None
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
    except ProjectScheduleProjectNotFoundError as exc:
        _raise_project_not_found(exc)
    except ProjectScheduleReadinessError as exc:
        _raise_readiness(exc)


@router.post("/confirm", response_model=ProjectScheduleRevisionResponse)
def confirm_project_schedule(
    project_id: str,
    request: ConfirmProjectScheduleRequest,
    service=Depends(get_project_schedule_service),
):
    raise HTTPException(
        410,
        detail={
            "code": "project_schedule_confirm_retired",
            "message": "Project Schedule is now confirmed with Matrix. Open Matrix Editor and use Confirm Matrix.",
        },
    )


def _raise_project_not_found(exc: Exception) -> None:
    raise HTTPException(
        404,
        detail={"code": "project_not_found", "message": str(exc)},
    ) from exc


def _raise_readiness(exc: Exception) -> None:
    raise HTTPException(
        422,
        detail={"code": "project_schedule_validation", "message": str(exc)},
    ) from exc
