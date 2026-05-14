"""Controlled Section 2 write-back API routes."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import (
    get_project_output_record_service,
    get_section2_write_back_service,
)
from backend.application.project_output_record_service import ProjectOutputRecordService, RegisterProjectOutputCommand
from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus
from backend.application.section2_write_back_service import (
    Section2WriteBackCommand,
    Section2WriteBackError,
    Section2WriteBackNotFoundError,
    Section2WriteBackResult,
    Section2WriteBackService,
)
from backend.infrastructure.office import WordSection2FieldChange


router = APIRouter(
    prefix="/api/projects/{project_id}/test-plan/drafts/{draft_id}",
    tags=["section2-write-back"],
)


class Section2WriteBackRequest(BaseModel):
    """Request body for controlled Section 2 write-back."""

    target_application_form_path: str = Field(min_length=1)
    received_date: date
    lab: str | None = None
    assigned_personnel: str | None = None
    sample_condition: str | None = None
    sample_preparation_days: int = Field(default=1, ge=0)
    test_group_scheduling_buffer_days: int = Field(default=1, ge=0)
    report_drafting_days: int = Field(default=3, ge=0)
    review_days: int = Field(default=1, ge=0)
    operator: str | None = None


class Section2ChangedFieldResponse(BaseModel):
    """Single Section 2 field write-back result."""

    field_key: str
    label: str
    old_value: str
    new_value: str
    location: str


class Section2WriteBackResponse(BaseModel):
    """Controlled Section 2 write-back response."""

    project_id: str
    draft_id: str
    target_application_form_path: str
    backup_path: str
    changed_fields: list[Section2ChangedFieldResponse]
    unchanged_fields: list[Section2ChangedFieldResponse]
    warnings: list[str]
    written_at: str
    operator: str | None


@router.post("/section2-write-back", response_model=Section2WriteBackResponse)
def write_back_section2(
    project_id: str,
    draft_id: str,
    request: Section2WriteBackRequest,
    service: Section2WriteBackService = Depends(get_section2_write_back_service),
    output_service: ProjectOutputRecordService = Depends(get_project_output_record_service),
) -> Section2WriteBackResponse:
    """Write approved Section 2 values into the target application form."""
    try:
        result = service.write_back(
            Section2WriteBackCommand(
                project_id=project_id,
                draft_id=draft_id,
                target_application_form_path=Path(request.target_application_form_path),
                received_date=request.received_date,
                lab=request.lab,
                assigned_personnel=request.assigned_personnel,
                sample_condition=request.sample_condition,
                sample_preparation_days=request.sample_preparation_days,
                test_group_scheduling_buffer_days=(
                    request.test_group_scheduling_buffer_days
                ),
                report_drafting_days=request.report_drafting_days,
                review_days=request.review_days,
                operator=request.operator,
            )
        )
    except Section2WriteBackNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Section2WriteBackError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    output_service.register_output(
        RegisterProjectOutputCommand(
            project_id=project_id,
            output_kind=ProjectOutputKind.SECTION2_WRITE_BACK,
            status=ProjectOutputStatus.CURRENT,
            source=ProjectOutputSource.SYSTEM_EXECUTED,
            output_path=str(result.target_application_form_path),
            draft_id=draft_id,
        )
    )
    return _to_response(result)


def _to_response(result: Section2WriteBackResult) -> Section2WriteBackResponse:
    """Convert an application result to an API response."""
    return Section2WriteBackResponse(
        project_id=result.project_id,
        draft_id=result.draft_id,
        target_application_form_path=str(result.target_application_form_path),
        backup_path=str(result.backup_path),
        changed_fields=[_field_response(item) for item in result.changed_fields],
        unchanged_fields=[_field_response(item) for item in result.unchanged_fields],
        warnings=list(result.warnings),
        written_at=result.written_at,
        operator=result.operator,
    )


def _field_response(change: WordSection2FieldChange) -> Section2ChangedFieldResponse:
    """Convert a gateway field change into an API DTO."""
    return Section2ChangedFieldResponse(
        field_key=change.field_key,
        label=change.label,
        old_value=change.old_value,
        new_value=change.new_value,
        location=change.location,
    )
