"""Project Basic Information API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_project_basic_information_service
from backend.api.lifecycle_errors import (
    lifecycle_guard_not_found,
    lifecycle_readonly_conflict,
)
from backend.application.project_lifecycle_write_guard import (
    ProjectLifecycleReadonlyError,
    ProjectLifecycleWriteGuardNotFoundError,
)
from backend.application.project_basic_information_service import (
    ConfirmProjectBasicInformationCommand,
    ProjectBasicInformationError,
    ProjectBasicInformationFieldSuggestion,
    ProjectBasicInformationMissingRequiredError,
    ProjectBasicInformationProjectNotFoundError,
    ProjectBasicInformationRecord,
    ProjectBasicInformationResult,
    ProjectBasicInformationService,
    SaveProjectBasicInformationDraftCommand,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/basic-information",
    tags=["project-basic-information"],
)


class ProjectBasicInformationDraftRequest(BaseModel):
    """Request DTO for saving Basic Information draft values."""

    values: dict[str, str] = Field(default_factory=dict)


class ProjectBasicInformationConfirmRequest(BaseModel):
    """Request DTO for confirming Basic Information values."""

    values: dict[str, str] = Field(default_factory=dict)
    confirmed_by: str = Field(min_length=1)


class ProjectBasicInformationRecordResponse(BaseModel):
    """Response DTO for one Basic Information record."""

    record_id: str
    project_id: str
    status: str
    version: int
    values: dict[str, str]
    source_signature: str
    created_at: str
    updated_at: str
    confirmed_at: str | None
    confirmed_by: str | None


class ProjectBasicInformationDraftResponse(BaseModel):
    """Response DTO for the current Basic Information draft."""

    values: dict[str, str]


class ProjectBasicInformationFieldSuggestionResponse(BaseModel):
    """Response DTO for one source field suggestion."""

    field_key: str
    source: str
    source_value: str
    needs_review: bool


class ProjectBasicInformationResponse(BaseModel):
    """Response DTO for Basic Information read model."""

    project_id: str
    status: str
    draft: ProjectBasicInformationDraftResponse
    latest_confirmed: ProjectBasicInformationRecordResponse | None
    field_suggestions: dict[str, ProjectBasicInformationFieldSuggestionResponse]
    changed_source_fields: list[str]
    missing_required_fields: list[str]
    missing_required_labels: list[str]
    blockers: list[str]
    warnings: list[str]


@router.get("", response_model=ProjectBasicInformationResponse)
def get_basic_information(
    project_id: str,
    service: ProjectBasicInformationService = Depends(
        get_project_basic_information_service
    ),
) -> ProjectBasicInformationResponse:
    """Return Project Basic Information draft/confirmed status."""
    try:
        return _response(service.get(project_id))
    except ProjectBasicInformationProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectLifecycleWriteGuardNotFoundError as exc:
        raise lifecycle_guard_not_found(exc) from exc
    except ProjectLifecycleReadonlyError as exc:
        raise lifecycle_readonly_conflict(exc) from exc
    except ProjectLifecycleWriteGuardNotFoundError as exc:
        raise lifecycle_guard_not_found(exc) from exc
    except ProjectLifecycleReadonlyError as exc:
        raise lifecycle_readonly_conflict(exc) from exc


@router.put("/draft", response_model=ProjectBasicInformationResponse)
def save_basic_information_draft(
    project_id: str,
    request: ProjectBasicInformationDraftRequest,
    service: ProjectBasicInformationService = Depends(
        get_project_basic_information_service
    ),
) -> ProjectBasicInformationResponse:
    """Save operator Basic Information draft values."""
    try:
        return _response(
            service.save_draft(
                SaveProjectBasicInformationDraftCommand(
                    project_id=project_id,
                    values=request.values,
                )
            )
        )
    except ProjectBasicInformationProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectLifecycleWriteGuardNotFoundError as exc:
        raise lifecycle_guard_not_found(exc) from exc
    except ProjectLifecycleReadonlyError as exc:
        raise lifecycle_readonly_conflict(exc) from exc


@router.post("/confirm", response_model=ProjectBasicInformationResponse)
def confirm_basic_information(
    project_id: str,
    request: ProjectBasicInformationConfirmRequest,
    service: ProjectBasicInformationService = Depends(
        get_project_basic_information_service
    ),
) -> ProjectBasicInformationResponse:
    """Confirm a new Basic Information authority version."""
    try:
        return _response(
            service.confirm(
                ConfirmProjectBasicInformationCommand(
                    project_id=project_id,
                    values=request.values,
                    confirmed_by=request.confirmed_by,
                )
            )
        )
    except ProjectBasicInformationMissingRequiredError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "message": str(exc),
                "missing_fields": list(exc.missing_fields),
                "missing_labels": list(exc.missing_labels),
            },
        ) from exc
    except ProjectBasicInformationProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectLifecycleWriteGuardNotFoundError as exc:
        raise lifecycle_guard_not_found(exc) from exc
    except ProjectLifecycleReadonlyError as exc:
        raise lifecycle_readonly_conflict(exc) from exc
    except ProjectBasicInformationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def _response(result: ProjectBasicInformationResult) -> ProjectBasicInformationResponse:
    """Convert application result to API response DTO."""
    return ProjectBasicInformationResponse(
        project_id=result.project_id,
        status=result.status,
        draft=ProjectBasicInformationDraftResponse(values=result.draft.values),
        latest_confirmed=(
            _record_response(result.latest_confirmed)
            if result.latest_confirmed is not None
            else None
        ),
        field_suggestions={
            key: _suggestion_response(value)
            for key, value in result.field_suggestions.items()
        },
        changed_source_fields=list(result.changed_source_fields),
        missing_required_fields=list(result.missing_required_fields),
        missing_required_labels=list(result.missing_required_labels),
        blockers=list(result.blockers),
        warnings=list(result.warnings),
    )


def _record_response(
    record: ProjectBasicInformationRecord,
) -> ProjectBasicInformationRecordResponse:
    """Convert one Basic Information record to response DTO."""
    return ProjectBasicInformationRecordResponse(
        record_id=record.record_id,
        project_id=record.project_id,
        status=record.status,
        version=record.version,
        values=record.values,
        source_signature=record.source_signature,
        created_at=record.created_at,
        updated_at=record.updated_at,
        confirmed_at=record.confirmed_at,
        confirmed_by=record.confirmed_by,
    )


def _suggestion_response(
    suggestion: ProjectBasicInformationFieldSuggestion,
) -> ProjectBasicInformationFieldSuggestionResponse:
    """Convert one field suggestion to response DTO."""
    return ProjectBasicInformationFieldSuggestionResponse(
        field_key=suggestion.field_key,
        source=suggestion.source,
        source_value=suggestion.source_value,
        needs_review=suggestion.needs_review,
    )
