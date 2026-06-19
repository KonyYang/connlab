"""Project Folder Application Form Word write-back API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_project_application_form_write_back_service
from backend.application.project_application_form_write_back_service import (
    ProjectApplicationFormWriteBackError,
    ProjectApplicationFormWriteBackNotFoundError,
    ProjectApplicationFormWriteBackResult,
    ProjectApplicationFormWriteBackService,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/project-folder/application-form",
    tags=["project-folder-application-form"],
)


class ApplicationFormWriteBackFieldResponse(BaseModel):
    """One Word field write-back response."""

    field_key: str
    label: str
    old_value: str
    new_value: str
    location: str


class ApplicationFormWriteBackResponse(BaseModel):
    """Application Form write-back response."""

    project_id: str
    target_path: str
    status: str
    changed_fields: list[ApplicationFormWriteBackFieldResponse]
    unchanged_fields: list[ApplicationFormWriteBackFieldResponse]
    warnings: list[str]
    output_record_id: str | None


@router.post("/write-back", response_model=ApplicationFormWriteBackResponse)
def write_back_application_form(
    project_id: str,
    service: ProjectApplicationFormWriteBackService = Depends(
        get_project_application_form_write_back_service
    ),
) -> ApplicationFormWriteBackResponse:
    """Write structured project/application data into the copied Word form."""
    try:
        return _response(service.write_back(project_id))
    except ProjectApplicationFormWriteBackNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectApplicationFormWriteBackError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _response(
    result: ProjectApplicationFormWriteBackResult,
) -> ApplicationFormWriteBackResponse:
    return ApplicationFormWriteBackResponse(
        project_id=result.project_id,
        target_path=str(result.target_path),
        status=result.status,
        changed_fields=[_field(field) for field in result.changed_fields],
        unchanged_fields=[_field(field) for field in result.unchanged_fields],
        warnings=list(result.warnings),
        output_record_id=result.output_record_id,
    )


def _field(field) -> ApplicationFormWriteBackFieldResponse:
    return ApplicationFormWriteBackFieldResponse(
        field_key=field.field_key,
        label=field.label,
        old_value=field.old_value,
        new_value=field.new_value,
        location=field.location,
    )
