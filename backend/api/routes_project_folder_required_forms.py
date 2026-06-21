"""Project Folder Required forms API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_project_folder_required_forms_service
from backend.application.project_folder_required_forms_service import (
    GenerateRequiredFormsCommand,
    ProjectFolderRequiredFormsService,
    RequiredFormPreviewItem,
    RequiredFormsConflictError,
    RequiredFormsContextMismatchError,
    RequiredFormsError,
    RequiredFormsGenerateItem,
    RequiredFormsGenerateResult,
    RequiredFormsGenerateTarget,
    RequiredFormsPreview,
    RequiredFormsTiming,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/project-folder/required-forms",
    tags=["project-folder-required-forms"],
)


class RequiredFormPreviewItemResponse(BaseModel):
    """Response DTO for one Required form preview item."""

    key: str
    label: str
    target_path: str | None
    status: str
    action: str
    message: str


class RequiredFormsPreviewResponse(BaseModel):
    """Response DTO for Required forms preview."""

    project_id: str
    status: str
    official_project_folder_path: str | None
    confirmed_matrix_id: str | None
    confirmed_revision: int | None
    confirmed_fee_id: str | None
    confirmed_fee_revision: int | None
    confirmed_fee_pricing_draft_edit_id: str | None
    confirmed_basic_information_version: int | None
    confirmed_basic_information_source_signature_hash: str | None
    customer_feedback_template_path: str | None
    items: list[RequiredFormPreviewItemResponse]
    blockers: list[str]
    warnings: list[str]


class RequiredFormsGenerateTargetRequest(BaseModel):
    """Expected final target DTO."""

    key: str = Field(min_length=1)
    target_path: str = Field(min_length=1)


class RequiredFormsGenerateRequest(BaseModel):
    """Request DTO for generating Required forms."""

    expected_official_project_folder_path: str = Field(min_length=1)
    expected_confirmed_matrix_id: str = Field(min_length=1)
    expected_confirmed_revision: int
    expected_confirmed_fee_id: str = Field(min_length=1)
    expected_confirmed_fee_revision: int
    expected_confirmed_fee_pricing_draft_edit_id: str = Field(min_length=1)
    expected_confirmed_basic_information_version: int
    expected_confirmed_basic_information_source_signature_hash: str = Field(min_length=1)
    expected_customer_feedback_template_path: str = Field(min_length=1)
    expected_targets: list[RequiredFormsGenerateTargetRequest]


class RequiredFormsGenerateItemResponse(BaseModel):
    """Response DTO for one generated Required form."""

    key: str
    label: str
    target_path: str
    status: str
    source_path: str | None
    output_record_id: str | None
    message: str


class RequiredFormsTimingResponse(BaseModel):
    """Diagnostic timing entry for Required forms generation."""

    label: str
    elapsed_ms: int


class RequiredFormsGenerateResponse(BaseModel):
    """Response DTO for Required forms generation."""

    project_id: str
    status: str
    official_project_folder_path: str
    items: list[RequiredFormsGenerateItemResponse]
    warnings: list[str]
    timings: list[RequiredFormsTimingResponse] = Field(default_factory=list)


@router.get("/preview", response_model=RequiredFormsPreviewResponse)
def preview_required_forms(
    project_id: str,
    service: ProjectFolderRequiredFormsService = Depends(
        get_project_folder_required_forms_service
    ),
) -> RequiredFormsPreviewResponse:
    """Return a read-only Required forms preview."""
    try:
        return _preview_response(service.preview(project_id))
    except RequiredFormsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/generate", response_model=RequiredFormsGenerateResponse)
def generate_required_forms(
    project_id: str,
    request: RequiredFormsGenerateRequest,
    service: ProjectFolderRequiredFormsService = Depends(
        get_project_folder_required_forms_service
    ),
) -> RequiredFormsGenerateResponse:
    """Generate Required forms into the local Official project folder."""
    command = GenerateRequiredFormsCommand(
        project_id=project_id,
        expected_official_project_folder_path=Path(
            request.expected_official_project_folder_path
        ),
        expected_confirmed_matrix_id=request.expected_confirmed_matrix_id,
        expected_confirmed_revision=request.expected_confirmed_revision,
        expected_confirmed_fee_id=request.expected_confirmed_fee_id,
        expected_confirmed_fee_revision=request.expected_confirmed_fee_revision,
        expected_confirmed_fee_pricing_draft_edit_id=(
            request.expected_confirmed_fee_pricing_draft_edit_id
        ),
        expected_confirmed_basic_information_version=(
            request.expected_confirmed_basic_information_version
        ),
        expected_confirmed_basic_information_source_signature_hash=(
            request.expected_confirmed_basic_information_source_signature_hash
        ),
        expected_customer_feedback_template_path=Path(
            request.expected_customer_feedback_template_path
        ),
        expected_targets=tuple(
            RequiredFormsGenerateTarget(item.key, Path(item.target_path))
            for item in request.expected_targets
        ),
    )
    try:
        return _generate_response(service.generate(command))
    except RequiredFormsContextMismatchError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except RequiredFormsConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except RequiredFormsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _preview_response(preview: RequiredFormsPreview) -> RequiredFormsPreviewResponse:
    """Convert preview dataclass to response DTO."""
    return RequiredFormsPreviewResponse(
        project_id=preview.project_id,
        status=preview.status,
        official_project_folder_path=_path(preview.official_project_folder_path),
        confirmed_matrix_id=preview.confirmed_matrix_id,
        confirmed_revision=preview.confirmed_revision,
        confirmed_fee_id=preview.confirmed_fee_id,
        confirmed_fee_revision=preview.confirmed_fee_revision,
        confirmed_fee_pricing_draft_edit_id=preview.confirmed_fee_pricing_draft_edit_id,
        confirmed_basic_information_version=preview.confirmed_basic_information_version,
        confirmed_basic_information_source_signature_hash=(
            preview.confirmed_basic_information_source_signature_hash
        ),
        customer_feedback_template_path=_path(preview.customer_feedback_template_path),
        items=[_preview_item_response(item) for item in preview.items],
        blockers=list(preview.blockers),
        warnings=list(preview.warnings),
    )


def _preview_item_response(
    item: RequiredFormPreviewItem,
) -> RequiredFormPreviewItemResponse:
    """Convert one preview item to response DTO."""
    return RequiredFormPreviewItemResponse(
        key=item.key,
        label=item.label,
        target_path=_path(item.target_path),
        status=item.status,
        action=item.action,
        message=item.message,
    )


def _generate_response(result: RequiredFormsGenerateResult) -> RequiredFormsGenerateResponse:
    """Convert generation result to response DTO."""
    return RequiredFormsGenerateResponse(
        project_id=result.project_id,
        status=result.status,
        official_project_folder_path=str(result.official_project_folder_path),
        items=[_generate_item_response(item) for item in result.items],
        warnings=list(result.warnings),
        timings=[_timing_response(item) for item in result.timings],
    )


def _generate_item_response(
    item: RequiredFormsGenerateItem,
) -> RequiredFormsGenerateItemResponse:
    """Convert one generation item to response DTO."""
    return RequiredFormsGenerateItemResponse(
        key=item.key,
        label=item.label,
        target_path=str(item.target_path),
        status=item.status,
        source_path=_path(item.source_path),
        output_record_id=item.output_record_id,
        message=item.message,
    )


def _path(path: Path | None) -> str | None:
    """Return path text for JSON responses."""
    return str(path) if path is not None else None


def _timing_response(item: RequiredFormsTiming) -> RequiredFormsTimingResponse:
    """Convert one timing entry to API response DTO."""
    return RequiredFormsTimingResponse(label=item.label, elapsed_ms=item.elapsed_ms)
