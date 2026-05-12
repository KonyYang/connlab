"""Project test-plan draft persistence API routes."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_project_test_plan_draft_service
from backend.application.project_test_plan_draft_service import (
    CreateProjectTestPlanDraftCommand,
    ProjectTestPlanDraftError,
    ProjectTestPlanDraftNotFoundError,
    ProjectTestPlanDraftService,
    UpdateProjectTestPlanDraftCommand,
)
from backend.domain import ProjectTestPlanDraft, ProjectTestPlanDraftStatus


router = APIRouter(prefix="/api/projects/{project_id}/test-plan/drafts", tags=["project-test-plan-drafts"])


class ProjectTestPlanDraftCreateRequest(BaseModel):
    """Request body for creating a Project test-plan draft snapshot."""

    source_document_path: str = Field(min_length=1)
    source_document_name: str = Field(min_length=1)
    source_format: str = Field(min_length=1)
    payload: dict[str, Any]
    status: ProjectTestPlanDraftStatus = ProjectTestPlanDraftStatus.DRAFT
    source_asset_id: str | None = None
    source_case_id: str | None = None
    source_draft_id: str | None = None


class ProjectTestPlanDraftUpdateRequest(BaseModel):
    """Request body for updating a Project test-plan draft snapshot."""

    payload: dict[str, Any] | None = None
    status: ProjectTestPlanDraftStatus | None = None


class ProjectTestPlanDraftResponse(BaseModel):
    """Project test-plan draft API response."""

    draft_id: str
    project_id: str
    source_document_path: str
    source_document_name: str
    source_format: str
    source_asset_id: str | None
    source_case_id: str | None
    source_draft_id: str | None
    status: ProjectTestPlanDraftStatus
    version: int
    payload: dict[str, Any]
    created_at: str
    updated_at: str
    reviewed_at: str | None


@router.post("", response_model=ProjectTestPlanDraftResponse, status_code=201)
def create_project_test_plan_draft(
    project_id: str,
    request: ProjectTestPlanDraftCreateRequest,
    service: ProjectTestPlanDraftService = Depends(get_project_test_plan_draft_service),
) -> ProjectTestPlanDraftResponse:
    """Create a Project-scoped test-plan draft snapshot."""
    try:
        draft = service.create_draft(
            CreateProjectTestPlanDraftCommand(
                project_id=project_id,
                source_document_path=request.source_document_path,
                source_document_name=request.source_document_name,
                source_format=request.source_format,
                source_asset_id=request.source_asset_id,
                source_case_id=request.source_case_id,
                source_draft_id=request.source_draft_id,
                status=request.status,
                payload=request.payload,
            )
        )
    except ProjectTestPlanDraftNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectTestPlanDraftError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(draft)


@router.get("", response_model=list[ProjectTestPlanDraftResponse])
def list_project_test_plan_drafts(
    project_id: str,
    service: ProjectTestPlanDraftService = Depends(get_project_test_plan_draft_service),
) -> list[ProjectTestPlanDraftResponse]:
    """List Project-scoped test-plan draft snapshots."""
    try:
        return [_to_response(draft) for draft in service.list_by_project(project_id)]
    except ProjectTestPlanDraftNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{draft_id}", response_model=ProjectTestPlanDraftResponse)
def get_project_test_plan_draft(
    project_id: str,
    draft_id: str,
    service: ProjectTestPlanDraftService = Depends(get_project_test_plan_draft_service),
) -> ProjectTestPlanDraftResponse:
    """Return one Project-scoped test-plan draft snapshot."""
    try:
        return _to_response(service.get_draft(project_id, draft_id))
    except ProjectTestPlanDraftNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{draft_id}", response_model=ProjectTestPlanDraftResponse)
def update_project_test_plan_draft(
    project_id: str,
    draft_id: str,
    request: ProjectTestPlanDraftUpdateRequest,
    service: ProjectTestPlanDraftService = Depends(get_project_test_plan_draft_service),
) -> ProjectTestPlanDraftResponse:
    """Update one Project-scoped test-plan draft snapshot."""
    try:
        return _to_response(
            service.update_draft(
                UpdateProjectTestPlanDraftCommand(
                    project_id=project_id,
                    draft_id=draft_id,
                    payload=request.payload,
                    status=request.status,
                )
            )
        )
    except ProjectTestPlanDraftNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectTestPlanDraftError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _to_response(draft: ProjectTestPlanDraft) -> ProjectTestPlanDraftResponse:
    """Convert a domain draft to an API response."""
    return ProjectTestPlanDraftResponse(
        draft_id=draft.draft_id,
        project_id=draft.project_id,
        source_document_path=draft.source_document_path,
        source_document_name=draft.source_document_name,
        source_format=draft.source_format,
        source_asset_id=draft.source_asset_id,
        source_case_id=draft.source_case_id,
        source_draft_id=draft.source_draft_id,
        status=draft.status,
        version=draft.version,
        payload=json.loads(draft.payload_json),
        created_at=draft.created_at,
        updated_at=draft.updated_at,
        reviewed_at=draft.reviewed_at,
    )
