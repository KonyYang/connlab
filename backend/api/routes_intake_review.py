"""Unified intake case review and confirmation API routes."""

from __future__ import annotations

from typing import Any
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import (
    get_frozen_field_revision_request_service,
    get_intake_case_review_service,
    get_intake_confirmation_service,
)
from backend.application.frozen_field_revision_request_service import (
    FrozenFieldRevisionRequestNotFoundError,
    FrozenFieldRevisionRequestService,
    FrozenFieldRevisionRequestValidationError,
)
from backend.application.intake_case_review_service import (
    DraftPrecheckIssue,
    IntakeCaseReview,
    IntakeCaseReviewFrozenError,
    IntakeCaseReviewItem,
    IntakeCaseReviewNotFoundError,
    IntakeCaseReviewService,
)
from backend.application.intake_confirmation_service import (
    IntakeConfirmationError,
    IntakeConfirmationNotFoundError,
    IntakeConfirmationResult,
    IntakeConfirmationService,
)


router = APIRouter(tags=["intake-review"])


class IntakeCaseReviewFieldResponse(BaseModel):
    """One field shown in the unified case review."""

    key: str
    label: str
    value: Any = None
    required: bool = False
    missing: bool = False


class IntakeCaseReviewItemResponse(BaseModel):
    """One intake case review response item."""

    case_id: str
    status: str
    selected_form_asset_id: str | None = None
    selected_asset_name: str | None = None
    confirmed_project_id: str | None = None
    operator_notes: str | None = None
    missing_required_fields: list[str]
    confirm_allowed: bool
    base_editing_frozen: bool = False
    frozen_field_keys: list[str] = Field(default_factory=list)
    frozen_reason: str | None = None
    fields: list[IntakeCaseReviewFieldResponse]
    sample_rows: list[dict[str, Any]]
    requested_testing_rows: list[dict[str, Any]]
    project_setup: dict[str, Any] = Field(default_factory=dict)
    precheck_issues: list["DraftPrecheckIssueResponse"]


class DraftPrecheckIssueResponse(BaseModel):
    """One deterministic draft precheck issue."""

    level: str
    field_key: str
    message: str


class IntakeCaseReviewResponse(BaseModel):
    """Unified review data for one package."""

    package_id: str
    source_type: str
    package_status: str
    source_original_name: str
    subject: str | None = None
    sender_name: str | None = None
    sender_email: str | None = None
    cases: list[IntakeCaseReviewItemResponse]


class ConfirmIntakeCaseRequest(BaseModel):
    """Explicit operator confirmation request."""

    operator_confirmed: bool = False


class UpdateIntakeCaseReviewFieldsRequest(BaseModel):
    """Operator field corrections for one intake case review."""

    fields: dict[str, Any]
    sample_rows: list[dict[str, Any]] | None = None
    requested_testing_rows: list[dict[str, Any]] | None = None
    project_setup: dict[str, Any] | None = None


class ConfirmIntakeCaseResponse(BaseModel):
    """Project records created by intake confirmation."""

    case_id: str
    project_id: str
    application_form_id: str
    sample_count: int
    file_asset_count: int


class FrozenFieldRevisionChangeRequest(BaseModel):
    """One requested frozen-field change."""

    field_key: str
    proposed_value: Any = None


class CreateFrozenFieldRevisionRequestRequest(BaseModel):
    """Create payload for frozen-field revision request."""

    reason: str
    requested_by: str | None = None
    changes: list[FrozenFieldRevisionChangeRequest]


class FrozenFieldRevisionChangeResponse(BaseModel):
    """One stored frozen-field change entry."""

    field_key: str
    field_label: str | None = None
    current_value: Any = None
    proposed_value: Any = None


class FrozenFieldRevisionRequestResponse(BaseModel):
    """Frozen-field revision request response."""

    request_id: str
    intake_case_id: str
    project_id: str | None = None
    ltr_record_id: str | None = None
    ltr_number: str | None = None
    status: str
    requested_by: str | None = None
    reason: str
    changes: list[FrozenFieldRevisionChangeResponse]
    created_at: str
    updated_at: str


@router.get(
    "/api/intake-packages/{package_id}/case-review",
    response_model=IntakeCaseReviewResponse,
)
def get_intake_case_review(
    package_id: str,
    service: IntakeCaseReviewService = Depends(get_intake_case_review_service),
) -> IntakeCaseReviewResponse:
    """Return unified review data for email-import and manual-intake cases."""
    try:
        return _case_review_response(service.get_package_review(package_id))
    except IntakeCaseReviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/api/intake-cases/{case_id}/confirm",
    response_model=ConfirmIntakeCaseResponse,
)
def confirm_intake_case(
    case_id: str,
    request: ConfirmIntakeCaseRequest,
    service: IntakeConfirmationService = Depends(get_intake_confirmation_service),
) -> ConfirmIntakeCaseResponse:
    """Confirm one reviewed intake case into one Project after explicit approval."""
    if not request.operator_confirmed:
        raise HTTPException(status_code=400, detail="Operator confirmation is required.")
    try:
        return _confirmation_response(service.confirm_case(case_id))
    except IntakeConfirmationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IntakeConfirmationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch(
    "/api/intake-cases/{case_id}/review-fields",
    response_model=IntakeCaseReviewItemResponse,
)
def update_intake_case_review_fields(
    case_id: str,
    request: UpdateIntakeCaseReviewFieldsRequest,
    service: IntakeCaseReviewService = Depends(get_intake_case_review_service),
) -> IntakeCaseReviewItemResponse:
    """Persist operator field corrections for one intake case."""
    try:
        return _case_item_response(
            service.update_case_fields(
                case_id,
                request.fields,
                sample_rows=request.sample_rows,
                requested_testing_rows=request.requested_testing_rows,
                project_setup=request.project_setup,
            )
        )
    except IntakeCaseReviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IntakeCaseReviewFrozenError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "message": str(exc),
                "field_keys": list(exc.field_keys),
            },
        ) from exc


@router.post(
    "/api/intake-cases/{case_id}/frozen-field-revision-requests",
    response_model=FrozenFieldRevisionRequestResponse,
    status_code=201,
)
def create_frozen_field_revision_request(
    case_id: str,
    request: CreateFrozenFieldRevisionRequestRequest,
    service: FrozenFieldRevisionRequestService = Depends(get_frozen_field_revision_request_service),
) -> FrozenFieldRevisionRequestResponse:
    """Create one frozen-field revision request for a frozen intake case."""
    try:
        record = service.create_request(
            case_id,
            reason=request.reason,
            requested_by=request.requested_by,
            changes=[item.model_dump() for item in request.changes],
        )
        return _frozen_field_revision_request_response(record)
    except IntakeCaseReviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FrozenFieldRevisionRequestValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/api/intake-cases/{case_id}/frozen-field-revision-requests",
    response_model=list[FrozenFieldRevisionRequestResponse],
)
def list_frozen_field_revision_requests_by_case(
    case_id: str,
    service: FrozenFieldRevisionRequestService = Depends(get_frozen_field_revision_request_service),
) -> list[FrozenFieldRevisionRequestResponse]:
    """List frozen-field revision requests for one intake case."""
    return [_frozen_field_revision_request_response(item) for item in service.list_by_case(case_id)]


@router.get(
    "/api/projects/{project_id}/frozen-field-revision-requests",
    response_model=list[FrozenFieldRevisionRequestResponse],
)
def list_frozen_field_revision_requests_by_project(
    project_id: str,
    service: FrozenFieldRevisionRequestService = Depends(get_frozen_field_revision_request_service),
) -> list[FrozenFieldRevisionRequestResponse]:
    """List frozen-field revision requests for one confirmed project."""
    return [
        _frozen_field_revision_request_response(item)
        for item in service.list_by_project(project_id)
    ]


@router.get(
    "/api/frozen-field-revision-requests/{request_id}",
    response_model=FrozenFieldRevisionRequestResponse,
)
def get_frozen_field_revision_request(
    request_id: str,
    service: FrozenFieldRevisionRequestService = Depends(get_frozen_field_revision_request_service),
) -> FrozenFieldRevisionRequestResponse:
    """Get one frozen-field revision request by id."""
    try:
        return _frozen_field_revision_request_response(service.get(request_id))
    except FrozenFieldRevisionRequestNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _case_review_response(review: IntakeCaseReview) -> IntakeCaseReviewResponse:
    """Convert case review read model to API response."""
    return IntakeCaseReviewResponse(
        package_id=review.package.package_id,
        source_type=review.package.source_type.value,
        package_status=review.package.status.value,
        source_original_name=review.package.source_original_name,
        subject=review.package.subject,
        sender_name=review.package.sender_name,
        sender_email=review.package.sender_email,
        cases=[_case_item_response(item) for item in review.cases],
    )


def _case_item_response(item: IntakeCaseReviewItem) -> IntakeCaseReviewItemResponse:
    """Convert one case review item to API response."""
    return IntakeCaseReviewItemResponse(
        case_id=item.case.case_id,
        status=item.case.status.value,
        selected_form_asset_id=item.case.selected_form_asset_id,
        selected_asset_name=item.selected_asset.original_name if item.selected_asset else None,
        confirmed_project_id=item.case.confirmed_project_id,
        operator_notes=item.case.reviewer_notes,
        missing_required_fields=list(item.missing_required_fields),
        confirm_allowed=not item.missing_required_fields
        and item.case.status.value == "needs_review"
        and item.case.confirmed_project_id is None,
        base_editing_frozen=item.base_editing_frozen,
        frozen_field_keys=list(item.frozen_field_keys),
        frozen_reason=item.frozen_reason,
        sample_rows=_sample_rows(item.parsed_fields),
        requested_testing_rows=_requested_testing_rows(item.parsed_fields),
        project_setup=item.project_setup,
        precheck_issues=[_precheck_issue_response(issue) for issue in item.precheck_issues],
        fields=[
            _field_response("form_no", "Form No.", item.parsed_fields, required=False),
            _field_response("revision", "Revision", item.parsed_fields, required=False),
            _field_response("reference_doc", "Reference Doc.", item.parsed_fields, required=False),
            _field_response("product_name", "Product Name", item.parsed_fields, required=True),
            _field_response("requester", "Requester", item.parsed_fields, required=True),
            _field_response("phone", "Phone #", item.parsed_fields, required=False),
            _field_response("request_date", "Date", item.parsed_fields, required=False),
            _field_response("email", "Email", item.parsed_fields, required=False),
            _field_response("business_unit", "Business Unit", item.parsed_fields, required=False),
            _field_response("manufacturing_site", "Mfg. Site", item.parsed_fields, required=False),
            _field_response("project_no", "Project #", item.parsed_fields, required=False),
            _field_response(
                "lab_test_request_number",
                "Lab Test Request Number",
                item.parsed_fields,
                required=False,
            ),
            _field_response("results_format", "Results Format", item.parsed_fields, required=False),
            _field_response(
                "requested_completion_date",
                "Requested Testing Completion Date",
                item.parsed_fields,
                required=False,
            ),
            _field_response("test_type", "Test Type", item.parsed_fields, required=False),
            _field_response("sample_status", "Test Sample Status", item.parsed_fields, required=False),
            _field_response("project_type", "Project Type", item.parsed_fields, required=False),
            _field_response(
                "post_testing_disposition",
                "Post-Testing Sample Disposition",
                item.parsed_fields,
                required=False,
            ),
            _field_response("requested_testing", "Requested Testing", item.parsed_fields, required=False),
            _field_response("confidential", "Confidential", item.parsed_fields, required=False),
            _field_response("subcontract", "Subcontract", item.parsed_fields, required=False),
            _field_response(
                "additional_information",
                "Additional Information",
                item.parsed_fields,
                required=False,
            ),
            _field_response(
                "send_copies_recipients",
                "Send copies of test results/reports to",
                item.parsed_fields,
                required=False,
            ),
        ],
    )


def _precheck_issue_response(issue: DraftPrecheckIssue) -> DraftPrecheckIssueResponse:
    """Convert one draft precheck issue to API response."""
    return DraftPrecheckIssueResponse(
        level=issue.level,
        field_key=issue.field_key,
        message=issue.message,
    )


def _sample_rows(fields: dict[str, Any]) -> list[dict[str, Any]]:
    """Return parsed sample rows from draft fields."""
    rows = fields.get("samples")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _requested_testing_rows(fields: dict[str, Any]) -> list[dict[str, Any]]:
    """Return parsed requested-testing rows from draft fields."""
    rows = fields.get("requested_testing_rows")
    if not isinstance(rows, list):
        return []
    return [
        {"test_to_be_performed": row.get("test_to_be_performed", ""), "applicable_specification": row.get("applicable_specification", "")}
        for row in rows
        if isinstance(row, dict)
    ]


def _field_response(
    key: str,
    label: str,
    fields: dict[str, Any],
    *,
    required: bool,
) -> IntakeCaseReviewFieldResponse:
    """Convert one draft field to response."""
    value = fields.get(key)
    missing = required and not _has_value(value)
    return IntakeCaseReviewFieldResponse(
        key=key,
        label=label,
        value=value,
        required=required,
        missing=missing,
    )


def _confirmation_response(result: IntakeConfirmationResult) -> ConfirmIntakeCaseResponse:
    """Convert confirmation output to API response."""
    return ConfirmIntakeCaseResponse(
        case_id=result.intake_case.case_id,
        project_id=result.project.project_id,
        application_form_id=result.application_form.form_id,
        sample_count=len(result.sample_infos),
        file_asset_count=len(result.file_assets),
    )


def _frozen_field_revision_request_response(item) -> FrozenFieldRevisionRequestResponse:
    """Convert frozen-field revision request record to API response."""
    changes: list[FrozenFieldRevisionChangeResponse] = []
    try:
        decoded = json.loads(item.field_changes_json)
    except json.JSONDecodeError:
        decoded = []
    if isinstance(decoded, list):
        for entry in decoded:
            if not isinstance(entry, dict):
                continue
            changes.append(
                FrozenFieldRevisionChangeResponse(
                    field_key=str(entry.get("field_key", "")),
                    field_label=entry.get("field_label"),
                    current_value=entry.get("current_value"),
                    proposed_value=entry.get("proposed_value"),
                )
            )
    return FrozenFieldRevisionRequestResponse(
        request_id=item.request_id,
        intake_case_id=item.intake_case_id,
        project_id=item.project_id,
        ltr_record_id=item.ltr_record_id,
        ltr_number=item.ltr_number,
        status=item.status.value,
        requested_by=item.requested_by,
        reason=item.reason,
        changes=changes,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _has_value(value: object) -> bool:
    """Return whether a draft value is present."""
    if value in (None, ""):
        return False
    return bool(str(value).strip())
