"""Intake and precheck API routes."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from backend.api.dependencies import get_intake_precheck_service
from backend.application.intake_precheck_service import (
    IntakeNotFoundError,
    IntakePrecheckService,
    ParsedFormRecord,
)
from backend.domain import ApplicationForm, PrecheckIssue, PrecheckResult, SampleInfo


router = APIRouter(tags=["intake"])


class SampleInfoResponse(BaseModel):
    """Parsed sample row response."""

    sample_id: str
    product_name: str
    part_number: str
    quantity: int | None = None


class ApplicationFormResponse(BaseModel):
    """Parsed and persisted application form response."""

    form_id: str
    project_id: str
    form_no: str
    revision: str
    requester: str
    email: str | None = None
    project_number: str | None = None
    requested_testing: str | None = None
    samples: list[SampleInfoResponse]


class PrecheckIssueResponse(BaseModel):
    """Precheck issue response."""

    issue_id: str
    category: str
    level: str
    message: str
    field_name: str | None = None
    resolved: bool = False


class PrecheckResultResponse(BaseModel):
    """Precheck result response."""

    result_id: str
    application_form_id: str
    status: str
    checked_on: date | None = None
    issues: list[PrecheckIssueResponse]


@router.post(
    "/api/projects/{project_id}/application-form",
    response_model=ApplicationFormResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_application_form(
    project_id: str,
    file: UploadFile = File(...),
    service: IntakePrecheckService = Depends(get_intake_precheck_service),
) -> ApplicationFormResponse:
    """Upload, parse, and persist an application form."""
    try:
        record = service.upload_application_form(project_id, file.filename or "", file.file)
        return _form_response(record)
    except IntakeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/api/application-forms/{application_form_id}/precheck/run",
    response_model=PrecheckResultResponse,
)
def run_precheck(
    application_form_id: str,
    service: IntakePrecheckService = Depends(get_intake_precheck_service),
) -> PrecheckResultResponse:
    """Run deterministic precheck for a parsed application form."""
    try:
        return _precheck_response(service.run_precheck(application_form_id))
    except IntakeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/api/projects/{project_id}/prechecks/latest",
    response_model=PrecheckResultResponse,
)
def get_latest_precheck(
    project_id: str,
    service: IntakePrecheckService = Depends(get_intake_precheck_service),
) -> PrecheckResultResponse:
    """Return the latest precheck result for a project."""
    try:
        return _precheck_response(service.latest_precheck(project_id))
    except IntakeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch(
    "/api/precheck-issues/{issue_id}/resolve",
    response_model=PrecheckIssueResponse,
)
def resolve_issue(
    issue_id: str,
    service: IntakePrecheckService = Depends(get_intake_precheck_service),
) -> PrecheckIssueResponse:
    """Resolve one precheck issue."""
    try:
        return _issue_response(service.resolve_issue(issue_id))
    except IntakeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _form_response(record: ParsedFormRecord) -> ApplicationFormResponse:
    """Convert parsed form service output to API response."""
    return ApplicationFormResponse(
        form_id=record.form.form_id,
        project_id=record.form.project_id,
        form_no=record.form.form_no,
        revision=record.form.revision,
        requester=record.form.requester,
        email=record.form.email,
        project_number=record.form.project_number,
        requested_testing=record.form.requested_testing,
        samples=[_sample_response(sample) for sample in record.samples],
    )


def _sample_response(sample: SampleInfo) -> SampleInfoResponse:
    """Convert sample domain row to response DTO."""
    return SampleInfoResponse(
        sample_id=sample.sample_id,
        product_name=sample.product_name,
        part_number=sample.part_number,
        quantity=sample.quantity,
    )


def _precheck_response(result: PrecheckResult) -> PrecheckResultResponse:
    """Convert precheck domain result to response DTO."""
    return PrecheckResultResponse(
        result_id=result.result_id,
        application_form_id=result.application_form_id,
        status=result.status.value,
        checked_on=result.checked_on,
        issues=[_issue_response(issue) for issue in result.issues],
    )


def _issue_response(issue: PrecheckIssue) -> PrecheckIssueResponse:
    """Convert precheck issue domain row to response DTO."""
    return PrecheckIssueResponse(
        issue_id=issue.issue_id,
        category=issue.category.value,
        level=issue.level.value,
        message=issue.message,
        field_name=issue.field_name,
        resolved=issue.resolved,
    )
