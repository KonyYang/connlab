"""Previewed project-file encryption API."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_project_file_encryption_service
from backend.application.project_file_encryption_service import (
    ProjectFileEncryptionBlockedError,
    ProjectFileEncryptionCommand,
    ProjectFileEncryptionError,
    ProjectFileEncryptionPlanStaleError,
    ProjectFileEncryptionPreview,
    ProjectFileEncryptionResult,
    ProjectFileEncryptionService,
    ProjectFileEncryptionWorkspaceNotFoundError,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/file-encryption",
    tags=["project-file-encryption"],
)


class ProjectFileEncryptionItemResponse(BaseModel):
    """Path-free preview for one candidate file."""

    file_name: str
    location: Literal["official_root", "test_results"]
    office_kind: Literal["word", "excel", "powerpoint"]
    mode: Literal["replace_in_place", "secured_copy"]
    conflict: bool


class ProjectFileEncryptionPreviewResponse(BaseModel):
    """Controlled preview returned before any mutation."""

    project_id: str
    status: Literal["ready", "conflict", "empty", "blocked"]
    plan_token: str
    conflict_count: int
    items: list[ProjectFileEncryptionItemResponse]
    blockers: list[str]
    warnings: list[str]


class ProjectFileEncryptionExecuteRequest(BaseModel):
    """Execute only an unchanged plan; no filesystem paths are accepted."""

    expected_plan_token: str = Field(min_length=1)
    conflict_action: Literal["overwrite", "skip"]


class ProjectFileEncryptionResultItemResponse(BaseModel):
    """One path-free execution outcome."""

    file_name: str
    location: Literal["official_root", "test_results"]
    status: Literal["encrypted", "skipped", "failed"]
    message: str


class ProjectFileEncryptionResultResponse(BaseModel):
    """Batch execution outcome."""

    project_id: str
    encrypted_count: int
    skipped_count: int
    failed_count: int
    items: list[ProjectFileEncryptionResultItemResponse]


@router.post("/preview", response_model=ProjectFileEncryptionPreviewResponse)
def preview_project_file_encryption(
    project_id: str,
    service: ProjectFileEncryptionService = Depends(get_project_file_encryption_service),
) -> ProjectFileEncryptionPreviewResponse:
    """Preview exact files and conflicts without accepting a client path."""
    try:
        return _preview_response(service.preview(project_id))
    except ProjectFileEncryptionWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectFileEncryptionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/execute", response_model=ProjectFileEncryptionResultResponse)
def execute_project_file_encryption(
    project_id: str,
    request: ProjectFileEncryptionExecuteRequest,
    service: ProjectFileEncryptionService = Depends(get_project_file_encryption_service),
) -> ProjectFileEncryptionResultResponse:
    """Execute a fresh preview plan using one explicit conflict policy."""
    try:
        return _result_response(
            service.execute(
                ProjectFileEncryptionCommand(
                    project_id=project_id,
                    expected_plan_token=request.expected_plan_token,
                    conflict_action=request.conflict_action,
                )
            )
        )
    except ProjectFileEncryptionWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ProjectFileEncryptionPlanStaleError, ProjectFileEncryptionBlockedError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProjectFileEncryptionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _preview_response(preview: ProjectFileEncryptionPreview) -> ProjectFileEncryptionPreviewResponse:
    return ProjectFileEncryptionPreviewResponse(
        project_id=preview.project_id,
        status=preview.status,
        plan_token=preview.plan_token,
        conflict_count=preview.conflict_count,
        items=[
            ProjectFileEncryptionItemResponse(
                file_name=item.file_name,
                location=item.location,
                office_kind=item.office_kind,
                mode=item.mode,
                conflict=item.conflict,
            )
            for item in preview.items
        ],
        blockers=list(preview.blockers),
        warnings=list(preview.warnings),
    )


def _result_response(result: ProjectFileEncryptionResult) -> ProjectFileEncryptionResultResponse:
    return ProjectFileEncryptionResultResponse(
        project_id=result.project_id,
        encrypted_count=result.encrypted_count,
        skipped_count=result.skipped_count,
        failed_count=result.failed_count,
        items=[
            ProjectFileEncryptionResultItemResponse(
                file_name=item.file_name,
                location=item.location,
                status=item.status,
                message=item.message,
            )
            for item in result.items
        ],
    )

