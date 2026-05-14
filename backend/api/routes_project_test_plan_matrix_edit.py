"""API routes for Matrix draft edit, validate, and confirm operations."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_project_test_plan_matrix_edit_service
from backend.application.project_test_plan_matrix_edit_service import (
    ConfirmProjectTestPlanMatrixCommand,
    MatrixDraftEditResult,
    MatrixValidationSummary,
    ProjectTestPlanMatrixEditError,
    ProjectTestPlanMatrixEditNotFoundError,
    ProjectTestPlanMatrixEditService,
    UpdateProjectTestPlanMatrixCommand,
    ValidateProjectTestPlanMatrixCommand,
)
from backend.domain import ProjectTestPlanDraft, ProjectTestPlanDraftStatus


router = APIRouter(
    prefix="/api/projects/{project_id}/test-plan/drafts/{draft_id}/matrix",
    tags=["project-test-plan-matrix-edit"],
)


class MatrixStepInput(BaseModel):
    """One editable Matrix step input row."""

    raw_token: str | None = None
    sequence: int | None = None
    test_item: str | None = None
    step_label: str | None = None
    section: str | None = None
    source_section: str | None = None
    method: str | None = None
    method_summary: str | None = None
    condition: str | None = None
    condition_summary: str | None = None
    requirement: str | None = None
    judgement_criteria: str | None = None
    reference_standard: str | None = None
    step_description: str | None = None
    duration_value: float | None = None
    duration_unit: str | None = None
    estimated_duration_days: float | None = None
    duration_days: float | None = None
    estimated_duration_hours: float | None = None
    estimated_duration_hint: str | None = None
    duration_hint: str | None = None
    source_table_index: int | None = None
    source_row_index: int | None = None
    source_trace: str | None = None
    note: str | None = None


class MatrixGroupInput(BaseModel):
    """One editable Matrix group input."""

    group_key: str | None = None
    group_label: str | None = None
    sample_size: float | None = None
    source_table_index: int | None = None
    steps: list[MatrixStepInput]


class MatrixDraftUpdateRequest(BaseModel):
    """Request body for Matrix draft update."""

    groups: list[MatrixGroupInput]


class MatrixDraftValidateRequest(BaseModel):
    """Request body for Matrix draft validation."""

    groups: list[MatrixGroupInput] | None = None


class MatrixDraftConfirmRequest(BaseModel):
    """Request body for Matrix draft confirmation."""

    groups: list[MatrixGroupInput] | None = None


class MatrixValidationSummaryResponse(BaseModel):
    """Validation summary response."""

    blockers: list[str]
    warnings: list[str]
    group_count: int
    step_count: int


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


class MatrixDraftActionResponse(BaseModel):
    """Matrix draft action response."""

    draft: ProjectTestPlanDraftResponse
    validation: MatrixValidationSummaryResponse
    created_new_draft: bool


class MatrixDraftValidateResponse(BaseModel):
    """Matrix draft validate-only response."""

    project_id: str
    draft_id: str
    validation: MatrixValidationSummaryResponse


@router.put("", response_model=MatrixDraftActionResponse)
def update_matrix_draft(
    project_id: str,
    draft_id: str,
    request: MatrixDraftUpdateRequest,
    service: ProjectTestPlanMatrixEditService = Depends(get_project_test_plan_matrix_edit_service),
) -> MatrixDraftActionResponse:
    """Persist Matrix group/step edits for one draft."""
    try:
        result = service.update_matrix_draft(
            UpdateProjectTestPlanMatrixCommand(
                project_id=project_id,
                draft_id=draft_id,
                groups=[item.model_dump() for item in request.groups],
            )
        )
    except ProjectTestPlanMatrixEditNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectTestPlanMatrixEditError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _action_response(result)


@router.post("/validate", response_model=MatrixDraftValidateResponse)
def validate_matrix_draft(
    project_id: str,
    draft_id: str,
    request: MatrixDraftValidateRequest | None = Body(default=None),
    service: ProjectTestPlanMatrixEditService = Depends(get_project_test_plan_matrix_edit_service),
) -> MatrixDraftValidateResponse:
    """Validate Matrix payload and return blockers/warnings."""
    groups = None
    if request is not None and request.groups is not None:
        groups = [item.model_dump() for item in request.groups]
    try:
        summary = service.validate_matrix_draft(
            ValidateProjectTestPlanMatrixCommand(
                project_id=project_id,
                draft_id=draft_id,
                groups=groups,
            )
        )
    except ProjectTestPlanMatrixEditNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectTestPlanMatrixEditError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MatrixDraftValidateResponse(
        project_id=project_id,
        draft_id=draft_id,
        validation=_summary_response(summary),
    )


@router.post("/confirm", response_model=MatrixDraftActionResponse)
def confirm_matrix_draft(
    project_id: str,
    draft_id: str,
    request: MatrixDraftConfirmRequest | None = Body(default=None),
    service: ProjectTestPlanMatrixEditService = Depends(get_project_test_plan_matrix_edit_service),
) -> MatrixDraftActionResponse:
    """Confirm Matrix draft as reviewed authority when validation passes."""
    groups = None
    if request is not None and request.groups is not None:
        groups = [item.model_dump() for item in request.groups]
    try:
        result = service.confirm_matrix_draft(
            ConfirmProjectTestPlanMatrixCommand(
                project_id=project_id,
                draft_id=draft_id,
                groups=groups,
            )
        )
    except ProjectTestPlanMatrixEditNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectTestPlanMatrixEditError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _action_response(result)


def _action_response(result: MatrixDraftEditResult) -> MatrixDraftActionResponse:
    return MatrixDraftActionResponse(
        draft=_draft_response(result.draft),
        validation=_summary_response(result.validation),
        created_new_draft=result.created_new_draft,
    )


def _summary_response(summary: MatrixValidationSummary) -> MatrixValidationSummaryResponse:
    return MatrixValidationSummaryResponse(
        blockers=list(summary.blockers),
        warnings=list(summary.warnings),
        group_count=summary.group_count,
        step_count=summary.step_count,
    )


def _draft_response(draft: ProjectTestPlanDraft) -> ProjectTestPlanDraftResponse:
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
