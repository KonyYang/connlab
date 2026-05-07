"""Intake and precheck API routes."""

from __future__ import annotations

import shutil
import tempfile
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.api.dependencies import (
    get_direct_word_intake_service,
    get_email_package_application_form_service,
    get_exception_workflow_service,
    get_intake_asset_download_service,
    get_intake_asset_application_form_eligibility_service,
    get_intake_asset_preview_service,
    get_intake_form_selection_service,
    get_intake_package_query_service,
    get_intake_precheck_service,
    get_manual_intake_service,
    get_msg_package_intake_service,
    get_new_project_application_draft_service,
    get_project_creation_draft_lifecycle_service,
    get_project_creation_draft_query_service,
)
from backend.application.intake_asset_download_service import (
    IntakeAssetDownloadError,
    IntakeAssetDownloadNotFoundError,
    IntakeAssetDownloadService,
)
from backend.application.direct_word_intake_service import (
    DirectWordIntakeError,
    DirectWordIntakeResult,
    DirectWordIntakeService,
)
from backend.application.email_package_application_form_service import (
    EmailPackageApplicationFormError,
    EmailPackageApplicationFormNotFoundError,
    EmailPackageApplicationFormService,
)
from backend.application.intake_asset_preview_service import (
    IntakeAssetPreview,
    IntakeAssetPreviewError,
    IntakeAssetPreviewNotFoundError,
    IntakeAssetPreviewService,
    PreviewField,
    PreviewMetadata,
    PreviewTable,
)
from backend.application.application_form_eligibility_service import (
    ApplicationFormEligibility,
    ApplicationFormEligibilityNotFoundError,
    IntakeAssetApplicationFormEligibilityService,
)
from backend.application.exception_workflow_service import (
    ExceptionWorkflowIssue,
    ExceptionWorkflowNotFoundError,
    ExceptionWorkflowReview,
    ExceptionWorkflowService,
)
from backend.application.intake_precheck_service import (
    IntakeNotFoundError,
    IntakePrecheckService,
    ParsedFormRecord,
)
from backend.application.intake_form_selection_service import (
    FormSelectionResult,
    IntakeFormSelectionService,
    IntakeSelectionError,
    IntakeSelectionNotFoundError,
)
from backend.application.intake_package_query_service import (
    IntakePackageDetail,
    IntakePackageQueryNotFoundError,
    IntakePackageQueryService,
)
from backend.application.msg_package_intake_service import (
    MsgPackageIntakeError,
    MsgPackageIntakeResult,
    MsgPackageIntakeService,
)
from backend.application.new_project_application_draft_service import (
    NewProjectApplicationDraftNotFoundError,
    NewProjectApplicationDraftResult,
    NewProjectApplicationDraftService,
)
from backend.application.project_creation_draft_lifecycle_service import (
    ProjectCreationDraftLifecycleError,
    ProjectCreationDraftLifecycleNotFoundError,
    ProjectCreationDraftLifecycleResult,
    ProjectCreationDraftLifecycleService,
)
from backend.application.project_creation_draft_query_service import (
    ProjectCreationDraftQueryError,
    ProjectCreationDraftQueryService,
    ProjectCreationDraftRow,
)
from backend.application.manual_intake_service import (
    ManualIntakeError,
    ManualIntakeInput,
    ManualIntakeResult,
    ManualIntakeService,
    ManualSampleInput,
)
from backend.domain import (
    ApplicationForm,
    IntakeAsset,
    IntakeCase,
    PrecheckIssue,
    PrecheckResult,
    SampleInfo,
)


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


class ExceptionWorkflowIssueResponse(BaseModel):
    """One explicit exception workflow issue."""

    kind: str
    message: str
    operator_action: str
    blocking: bool
    asset_id: str | None = None
    case_id: str | None = None


class ExceptionWorkflowReviewResponse(BaseModel):
    """Intake package exception workflow review response."""

    package_id: str
    package_status: str
    case_ids: list[str]
    draft_ids: list[str]
    issues: list[ExceptionWorkflowIssueResponse]


class IntakeAssetResponse(BaseModel):
    """Stored intake asset response."""

    asset_id: str
    original_name: str
    extension: str
    mime_type: str | None = None
    size_bytes: int
    asset_role: str
    candidate_score: int | None = None


class IntakeAssetPreviewMetadataResponse(BaseModel):
    """Safe attachment metadata for preview rendering."""

    asset_id: str
    original_name: str
    extension: str
    mime_type: str | None = None
    size_bytes: int
    asset_role: str


class IntakeAssetPreviewFieldResponse(BaseModel):
    """One preview field for a structured attachment preview."""

    label: str
    value: str


class IntakeAssetPreviewTableResponse(BaseModel):
    """One preview table section for an attachment."""

    title: str
    headers: list[str]
    rows: list[list[str]]


class IntakeAssetPreviewResponse(BaseModel):
    """Typed response for one selected intake asset preview."""

    kind: str
    metadata: IntakeAssetPreviewMetadataResponse
    title: str
    fields: list[IntakeAssetPreviewFieldResponse]
    tables: list[IntakeAssetPreviewTableResponse]
    warnings: list[str]
    message: str | None = None
    image_data_url: str | None = None


class ApplicationFormEligibilityResponse(BaseModel):
    """Eligibility response for the Intake application-form gate."""

    eligible: bool
    reason_code: str
    message: str
    observed_header_cell: str | None = None
    observed_footer_text: str | None = None
    expected_text: str


class IntakePackageImportResponse(BaseModel):
    """Manual `.msg` package import response."""

    package_id: str
    source_type: str
    package_status: str
    source_original_name: str
    subject: str | None = None
    sender_name: str | None = None
    sender_email: str | None = None
    received_at: str | None = None
    asset_count: int
    candidate_count: int
    next_action: str
    assets: list[IntakeAssetResponse]


class IntakeCaseSummaryResponse(BaseModel):
    """Intake case summary for package detail."""

    case_id: str
    selected_form_asset_id: str | None = None
    status: str
    confirmed_project_id: str | None = None


class IntakePackageDetailResponse(BaseModel):
    """Read-only intake package detail response."""

    package_id: str
    source_type: str
    package_status: str
    source_original_name: str
    source_stored: bool
    subject: str | None = None
    sender_name: str | None = None
    sender_email: str | None = None
    received_at: str | None = None
    asset_count: int
    candidate_count: int
    case_count: int
    next_action: str
    assets: list[IntakeAssetResponse]
    candidate_assets: list[IntakeAssetResponse]
    cases: list[IntakeCaseSummaryResponse]


class ManualSampleInputRequest(BaseModel):
    """Manual sample fields from the no-email intake form."""

    product_name: str | None = None
    part_number: str | None = None
    revision: str | None = None
    lot_or_traceability: str | None = None
    material: str | None = None
    plating: str | None = None
    housing_material: str | None = None
    quantity: int | None = None


class ManualIntakeRequest(BaseModel):
    """No-email manual intake request."""

    product_name: str | None = None
    requester: str | None = None
    email: str | None = None
    business_unit: str | None = None
    project_no: str | None = None
    form_no: str | None = None
    revision: str | None = None
    requested_testing: str | None = None
    sample: ManualSampleInputRequest | None = None
    operator_notes: str | None = None


class ManualIntakeResponse(BaseModel):
    """Stored no-email manual intake response."""

    package_id: str
    case_id: str
    draft_id: str
    package_status: str
    selected_form_asset_id: str
    missing_required_fields: list[str]
    next_action: str


class NewProjectApplicationDraftResponse(BaseModel):
    """Prepared editable draft for the single-page New Project editor."""

    package_id: str
    case_id: str
    draft_id: str
    package_status: str
    selected_form_asset_id: str | None = None
    next_action: str


class ProjectCreationDraftLifecycleResponse(BaseModel):
    """Response for saving or discarding a New Project creation draft."""

    package_id: str
    action: str
    package_status: str | None = None
    deleted_package: bool = False
    deleted_assets: int = 0
    deleted_cases: int = 0
    deleted_drafts: int = 0
    deleted_files: bool = False
    message: str


class ProjectCreationDraftRowResponse(BaseModel):
    """One saved creation draft row for Drafts / In Progress."""

    package_id: str
    source_type: str
    source_name: str
    subject: str | None = None
    requester: str | None = None
    product_name: str | None = None
    updated_at: str | None = None
    current_step: str
    selected_form_asset_id: str | None = None
    active_case_id: str | None = None


class SelectApplicationFormRequest(BaseModel):
    """Human selected application form asset request."""

    asset_id: str
    replace_existing: bool = False


class SelectApplicationFormResponse(BaseModel):
    """Review case created from a selected application form asset."""

    package_id: str
    case_id: str
    draft_id: str
    selected_form_asset_id: str
    package_status: str
    next_action: str


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
    "/api/intake-packages/import-msg",
    response_model=IntakePackageImportResponse,
    status_code=status.HTTP_201_CREATED,
)
def import_msg_package(
    file: UploadFile = File(...),
    service: MsgPackageIntakeService = Depends(get_msg_package_intake_service),
) -> IntakePackageImportResponse:
    """Import one manually selected Outlook `.msg` package."""
    try:
        return _msg_import_response(
            service.import_msg_package(file.filename or "source.msg", file.file)
        )
    except MsgPackageIntakeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/api/intake-packages/import-docx",
    response_model=IntakePackageImportResponse,
    status_code=status.HTTP_201_CREATED,
)
def import_direct_word_application_form(
    file: UploadFile = File(...),
    service: DirectWordIntakeService = Depends(get_direct_word_intake_service),
) -> IntakePackageImportResponse:
    """Import one directly selected Word application form."""
    original_name = Path(file.filename or "application.docx").name
    suffix = Path(original_name).suffix or ".docx"
    with tempfile.TemporaryDirectory() as directory:
        temporary_path = Path(directory) / original_name
        with temporary_path.open("wb") as handle:
            shutil.copyfileobj(file.file, handle)
        try:
            return _direct_word_import_response(service.import_word_form(temporary_path))
        except DirectWordIntakeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/api/intake-packages/{package_id}/application-form",
    response_model=SelectApplicationFormResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_email_package_application_form(
    package_id: str,
    file: UploadFile = File(...),
    service: EmailPackageApplicationFormService = Depends(
        get_email_package_application_form_service
    ),
) -> SelectApplicationFormResponse:
    """Upload a Word application form into an existing email intake package."""
    original_name = Path(file.filename or "application.docx").name
    with tempfile.TemporaryDirectory() as directory:
        temporary_path = Path(directory) / original_name
        with temporary_path.open("wb") as handle:
            shutil.copyfileobj(file.file, handle)
        try:
            return _form_selection_response(
                service.upload_application_form(package_id, temporary_path)
            )
        except EmailPackageApplicationFormNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except IntakeSelectionNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except IntakeSelectionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except EmailPackageApplicationFormError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/api/intake-packages/{package_id}",
    response_model=IntakePackageDetailResponse,
)
def get_intake_package_detail(
    package_id: str,
    service: IntakePackageQueryService = Depends(get_intake_package_query_service),
) -> IntakePackageDetailResponse:
    """Return source, asset, candidate, and case state for one intake package."""
    try:
        return _package_detail_response(service.get_detail(package_id))
    except IntakePackageQueryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/api/intake-assets/{asset_id}/preview",
    response_model=IntakeAssetPreviewResponse,
)
def preview_intake_asset(
    asset_id: str,
    service: IntakeAssetPreviewService = Depends(get_intake_asset_preview_service),
) -> IntakeAssetPreviewResponse:
    """Return a safe preview for one registered intake asset."""
    try:
        return _intake_asset_preview_response(service.preview_asset(asset_id))
    except IntakeAssetPreviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IntakeAssetPreviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/intake-assets/{asset_id}/download")
def download_intake_asset(
    asset_id: str,
    service: IntakeAssetDownloadService = Depends(get_intake_asset_download_service),
) -> FileResponse:
    """Return the stored file for one registered intake asset as a browser download."""
    try:
        download = service.get_downloadable(asset_id)
    except IntakeAssetDownloadNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IntakeAssetDownloadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FileResponse(
        path=download.path,
        filename=download.filename,
        media_type=download.media_type,
    )


@router.post(
    "/api/intake-assets/{asset_id}/application-form/validate",
    response_model=ApplicationFormEligibilityResponse,
)
def validate_intake_asset_application_form(
    asset_id: str,
    service: IntakeAssetApplicationFormEligibilityService = Depends(
        get_intake_asset_application_form_eligibility_service
    ),
) -> ApplicationFormEligibilityResponse:
    """Validate whether one intake asset can enter Precheck as the application form."""
    try:
        return _application_form_eligibility_response(service.evaluate_asset(asset_id))
    except ApplicationFormEligibilityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/api/intake-packages/{package_id}/select-form",
    response_model=SelectApplicationFormResponse,
)
def select_application_form_asset(
    package_id: str,
    request: SelectApplicationFormRequest,
    service: IntakeFormSelectionService = Depends(get_intake_form_selection_service),
) -> SelectApplicationFormResponse:
    """Select one intake asset as the source application form for Precheck."""
    try:
        return _form_selection_response(
            service.select_form_asset(
                package_id,
                request.asset_id,
                replace_existing=request.replace_existing,
            )
        )
    except IntakeSelectionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IntakeSelectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/api/intake-packages/{package_id}/application-draft",
    response_model=NewProjectApplicationDraftResponse,
)
def ensure_new_project_application_draft(
    package_id: str,
    service: NewProjectApplicationDraftService = Depends(
        get_new_project_application_draft_service
    ),
) -> NewProjectApplicationDraftResponse:
    """Prepare a blank editable application draft without importing a form."""
    try:
        return _new_project_application_draft_response(service.ensure_draft(package_id))
    except NewProjectApplicationDraftNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/api/intake-packages/manual",
    response_model=ManualIntakeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_manual_intake(
    request: ManualIntakeRequest,
    service: ManualIntakeService = Depends(get_manual_intake_service),
) -> ManualIntakeResponse:
    """Create one no-email manual intake case without creating a project."""
    try:
        return _manual_intake_response(
            service.create_manual_case(_manual_intake_input(request))
        )
    except ManualIntakeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/api/intake-packages/{package_id}/draft/save",
    response_model=ProjectCreationDraftLifecycleResponse,
)
def save_project_creation_draft(
    package_id: str,
    service: ProjectCreationDraftLifecycleService = Depends(
        get_project_creation_draft_lifecycle_service
    ),
) -> ProjectCreationDraftLifecycleResponse:
    """Persist one New Project creation draft for later continuation."""
    try:
        return _project_creation_draft_lifecycle_response(service.save_draft(package_id))
    except ProjectCreationDraftLifecycleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectCreationDraftLifecycleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/api/intake-packages/{package_id}/draft/discard",
    response_model=ProjectCreationDraftLifecycleResponse,
)
def discard_unsaved_project_creation_draft(
    package_id: str,
    service: ProjectCreationDraftLifecycleService = Depends(
        get_project_creation_draft_lifecycle_service
    ),
) -> ProjectCreationDraftLifecycleResponse:
    """Delete one unsaved New Project creation package and stored files."""
    try:
        return _project_creation_draft_lifecycle_response(
            service.discard_unsaved(package_id)
        )
    except ProjectCreationDraftLifecycleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectCreationDraftLifecycleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/api/project-creation-drafts",
    response_model=list[ProjectCreationDraftRowResponse],
)
def list_project_creation_drafts(
    service: ProjectCreationDraftQueryService = Depends(
        get_project_creation_draft_query_service
    ),
) -> list[ProjectCreationDraftRowResponse]:
    """Return saved New Project creation drafts for continuation."""
    try:
        return [
            _project_creation_draft_row_response(row)
            for row in service.list_saved_drafts()
        ]
    except ProjectCreationDraftQueryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/api/project-creation-drafts/{package_id}/discard",
    response_model=ProjectCreationDraftLifecycleResponse,
)
def discard_saved_project_creation_draft(
    package_id: str,
    service: ProjectCreationDraftLifecycleService = Depends(
        get_project_creation_draft_lifecycle_service
    ),
) -> ProjectCreationDraftLifecycleResponse:
    """Discard one saved creation draft from Drafts / In Progress."""
    try:
        return _project_creation_draft_lifecycle_response(
            service.discard_saved_draft(package_id)
        )
    except ProjectCreationDraftLifecycleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectCreationDraftLifecycleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/api/intake-packages/{package_id}/exceptions/review",
    response_model=ExceptionWorkflowReviewResponse,
)
def review_intake_package_exceptions(
    package_id: str,
    service: ExceptionWorkflowService = Depends(get_exception_workflow_service),
) -> ExceptionWorkflowReviewResponse:
    """Review and persist explicit exception workflow state for an intake package."""
    try:
        return _exception_review_response(service.review_package(package_id))
    except ExceptionWorkflowNotFoundError as exc:
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


def _exception_review_response(
    review: ExceptionWorkflowReview,
) -> ExceptionWorkflowReviewResponse:
    """Convert exception workflow review to API response."""
    return ExceptionWorkflowReviewResponse(
        package_id=review.package_id,
        package_status=review.package.status.value,
        case_ids=[case.case_id for case in review.cases],
        draft_ids=[draft.draft_id for draft in review.drafts],
        issues=[_exception_issue_response(issue) for issue in review.issues],
    )


def _exception_issue_response(
    issue: ExceptionWorkflowIssue,
) -> ExceptionWorkflowIssueResponse:
    """Convert one exception workflow issue to API response."""
    return ExceptionWorkflowIssueResponse(
        kind=issue.kind.value,
        message=issue.message,
        operator_action=issue.operator_action,
        blocking=issue.blocking,
        asset_id=issue.asset_id,
        case_id=issue.case_id,
    )


def _msg_import_response(result: MsgPackageIntakeResult) -> IntakePackageImportResponse:
    """Convert manual `.msg` import output to API response."""
    return IntakePackageImportResponse(
        package_id=result.package.package_id,
        source_type=result.package.source_type.value,
        package_status=result.package.status.value,
        source_original_name=result.package.source_original_name,
        subject=result.package.subject,
        sender_name=result.package.sender_name,
        sender_email=result.package.sender_email,
        received_at=result.package.received_at,
        asset_count=len(result.assets),
        candidate_count=len(result.candidates),
        next_action=(
            "review_application_form_candidates"
            if result.candidates
            else "resolve_missing_application_form"
        ),
        assets=[_intake_asset_response(asset) for asset in result.assets],
    )


def _direct_word_import_response(
    result: DirectWordIntakeResult,
) -> IntakePackageImportResponse:
    """Convert direct Word intake output to the shared import response."""
    return IntakePackageImportResponse(
        package_id=result.package.package_id,
        source_type=result.package.source_type.value,
        package_status=result.package.status.value,
        source_original_name=result.package.source_original_name,
        subject=result.package.subject,
        sender_name=result.package.sender_name,
        sender_email=result.package.sender_email,
        received_at=result.package.received_at,
        asset_count=1,
        candidate_count=1,
        next_action="review_application_form_candidates",
        assets=[_intake_asset_response(result.asset)],
    )


def _package_detail_response(detail: IntakePackageDetail) -> IntakePackageDetailResponse:
    """Convert package detail read model to API response."""
    return IntakePackageDetailResponse(
        package_id=detail.package.package_id,
        source_type=detail.package.source_type.value,
        package_status=detail.package.status.value,
        source_original_name=detail.package.source_original_name,
        source_stored=detail.package.source_stored_path.is_file(),
        subject=detail.package.subject,
        sender_name=detail.package.sender_name,
        sender_email=detail.package.sender_email,
        received_at=detail.package.received_at,
        asset_count=len(detail.assets),
        candidate_count=len(detail.candidate_assets),
        case_count=len(detail.cases),
        next_action=_package_next_action(detail),
        assets=[_intake_asset_response(asset) for asset in detail.assets],
        candidate_assets=[_intake_asset_response(asset) for asset in detail.candidate_assets],
        cases=[_intake_case_response(case) for case in detail.cases],
    )


def _manual_intake_input(request: ManualIntakeRequest) -> ManualIntakeInput:
    """Convert API manual intake request to service input."""
    sample = request.sample or ManualSampleInputRequest()
    return ManualIntakeInput(
        product_name=request.product_name,
        requester=request.requester,
        email=request.email,
        business_unit=request.business_unit,
        project_no=request.project_no,
        form_no=request.form_no,
        revision=request.revision,
        requested_testing=request.requested_testing,
        sample=ManualSampleInput(
            product_name=sample.product_name,
            part_number=sample.part_number,
            revision=sample.revision,
            lot_or_traceability=sample.lot_or_traceability,
            material=sample.material,
            plating=sample.plating,
            housing_material=sample.housing_material,
            quantity=sample.quantity,
        ),
        operator_notes=request.operator_notes,
    )


def _manual_intake_response(result: ManualIntakeResult) -> ManualIntakeResponse:
    """Convert manual intake service output to API response."""
    return ManualIntakeResponse(
        package_id=result.package.package_id,
        case_id=result.case.case_id,
        draft_id=result.draft.draft_id,
        package_status=result.package.status.value,
        selected_form_asset_id=result.asset.asset_id,
        missing_required_fields=list(result.missing_required_fields),
        next_action=(
            "review_manual_intake"
            if not result.missing_required_fields
            else "complete_required_manual_fields"
        ),
    )


def _project_creation_draft_lifecycle_response(
    result: ProjectCreationDraftLifecycleResult,
) -> ProjectCreationDraftLifecycleResponse:
    """Convert creation draft lifecycle result to API response."""
    if result.action == "save_draft":
        message = "Creation draft saved. Continue it later from Drafts / In Progress."
    elif result.action == "discard_saved_draft":
        message = "Saved creation draft discarded. ConnLab imported copies were removed."
    else:
        message = "Unsaved creation session discarded. ConnLab imported copies were removed."
    return ProjectCreationDraftLifecycleResponse(
        package_id=result.package_id,
        action=result.action,
        package_status=result.package_status,
        deleted_package=result.deleted_package,
        deleted_assets=result.deleted_assets,
        deleted_cases=result.deleted_cases,
        deleted_drafts=result.deleted_drafts,
        deleted_files=result.deleted_files,
        message=message,
    )


def _project_creation_draft_row_response(
    row: ProjectCreationDraftRow,
) -> ProjectCreationDraftRowResponse:
    """Convert saved creation draft row to API response."""
    return ProjectCreationDraftRowResponse(
        package_id=row.package_id,
        source_type=row.source_type,
        source_name=row.source_name,
        subject=row.subject,
        requester=row.requester,
        product_name=row.product_name,
        updated_at=row.updated_at,
        current_step=row.current_step,
        selected_form_asset_id=row.selected_form_asset_id,
        active_case_id=row.active_case_id,
    )


def _form_selection_response(
    result: FormSelectionResult,
) -> SelectApplicationFormResponse:
    """Convert selected form case creation output to API response."""
    return SelectApplicationFormResponse(
        package_id=result.package_id,
        case_id=result.case.case_id,
        draft_id=result.draft.draft_id,
        selected_form_asset_id=result.selected_asset.asset_id,
        package_status="ready_for_review",
        next_action="review_selected_application_form",
    )


def _new_project_application_draft_response(
    result: NewProjectApplicationDraftResult,
) -> NewProjectApplicationDraftResponse:
    """Convert an editable application draft result to an API response."""
    return NewProjectApplicationDraftResponse(
        package_id=result.package.package_id,
        case_id=result.case.case_id,
        draft_id=result.draft.draft_id,
        package_status=result.package.status.value,
        selected_form_asset_id=result.case.selected_form_asset_id,
        next_action="edit_application_information",
    )


def _package_next_action(detail: IntakePackageDetail) -> str:
    """Return the next operator action for package detail."""
    if not detail.candidate_assets:
        return "resolve_missing_application_form"
    if len(detail.candidate_assets) > len(detail.cases):
        return "create_review_cases"
    return "review_created_cases"


def _intake_asset_response(asset: IntakeAsset) -> IntakeAssetResponse:
    """Convert an intake asset to API response."""
    return IntakeAssetResponse(
        asset_id=asset.asset_id,
        original_name=asset.original_name,
        extension=asset.extension,
        mime_type=asset.mime_type,
        size_bytes=asset.size_bytes,
        asset_role=asset.asset_role.value,
        candidate_score=asset.candidate_score,
    )


def _intake_asset_preview_response(
    preview: IntakeAssetPreview,
) -> IntakeAssetPreviewResponse:
    """Convert an intake asset preview to an API response."""
    return IntakeAssetPreviewResponse(
        kind=preview.kind,
        metadata=_preview_metadata_response(preview.metadata),
        title=preview.title,
        fields=[_preview_field_response(field) for field in preview.fields],
        tables=[_preview_table_response(table) for table in preview.tables],
        warnings=list(preview.warnings),
        message=preview.message,
        image_data_url=preview.image_data_url,
    )


def _application_form_eligibility_response(
    result: ApplicationFormEligibility,
) -> ApplicationFormEligibilityResponse:
    """Convert application-form eligibility to an API response."""
    return ApplicationFormEligibilityResponse(
        eligible=result.eligible,
        reason_code=result.reason_code,
        message=result.message,
        observed_header_cell=result.observed_header_cell,
        observed_footer_text=result.observed_footer_text,
        expected_text=result.expected_text,
    )


def _preview_metadata_response(
    metadata: PreviewMetadata,
) -> IntakeAssetPreviewMetadataResponse:
    """Convert path-free preview metadata to a response DTO."""
    return IntakeAssetPreviewMetadataResponse(
        asset_id=metadata.asset_id,
        original_name=metadata.original_name,
        extension=metadata.extension,
        mime_type=metadata.mime_type,
        size_bytes=metadata.size_bytes,
        asset_role=metadata.asset_role,
    )


def _preview_field_response(field: PreviewField) -> IntakeAssetPreviewFieldResponse:
    """Convert one preview field to a response DTO."""
    return IntakeAssetPreviewFieldResponse(label=field.label, value=field.value)


def _preview_table_response(table: PreviewTable) -> IntakeAssetPreviewTableResponse:
    """Convert one preview table to a response DTO."""
    return IntakeAssetPreviewTableResponse(
        title=table.title,
        headers=list(table.headers),
        rows=[list(row) for row in table.rows],
    )


def _intake_case_response(case: IntakeCase) -> IntakeCaseSummaryResponse:
    """Convert an intake case to package detail response."""
    return IntakeCaseSummaryResponse(
        case_id=case.case_id,
        selected_form_asset_id=case.selected_form_asset_id,
        status=case.status.value,
        confirmed_project_id=case.confirmed_project_id,
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
