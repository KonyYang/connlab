"""API routes for test-record and fee document generation."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import (
    get_project_output_record_service,
    get_test_record_fee_document_generation_service,
)
from backend.application.project_output_record_service import ProjectOutputRecordService, RegisterProjectOutputCommand
from backend.application.test_record_fee_document_generation_service import (
    GeneratedApprovalDocument,
    TestRecordFeeDocumentGenerationCommand,
    TestRecordFeeDocumentGenerationError,
    TestRecordFeeDocumentGenerationNotFoundError,
    TestRecordFeeDocumentGenerationResult,
    TestRecordFeeDocumentGenerationService,
)
from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus


router = APIRouter(
    prefix="/api/projects/{project_id}/test-plan/drafts/{draft_id}",
    tags=["test-record-fee-document-generation"],
)


class TestRecordFeeDocumentGenerationRequest(BaseModel):
    """Request body for controlled test-record and fee document generation."""

    output_dir: str = Field(min_length=1)
    test_record_template_path: str | None = None
    fee_evaluation_template_path: str | None = None
    overwrite: bool = False
    include_test_record: bool = True
    include_fee_evaluation: bool = True


class GeneratedApprovalDocumentResponse(BaseModel):
    """One generated file response entry."""

    kind: str
    source_template_path: str
    output_path: str | None
    status: str
    warnings: list[str]


class TestRecordFeeDocumentGenerationResponse(BaseModel):
    """Response for one controlled generation request."""

    project_id: str
    draft_id: str
    generated_files: list[GeneratedApprovalDocumentResponse]
    warnings: list[str]


@router.post(
    "/record-fee-documents/generate",
    response_model=TestRecordFeeDocumentGenerationResponse,
)
def generate_test_record_fee_documents(
    project_id: str,
    draft_id: str,
    request: TestRecordFeeDocumentGenerationRequest,
    service: TestRecordFeeDocumentGenerationService = Depends(
        get_test_record_fee_document_generation_service
    ),
    output_service: ProjectOutputRecordService = Depends(get_project_output_record_service),
) -> TestRecordFeeDocumentGenerationResponse:
    """Generate approval-package test-record and fee documents."""
    try:
        result = service.generate(
            TestRecordFeeDocumentGenerationCommand(
                project_id=project_id,
                draft_id=draft_id,
                output_dir=Path(request.output_dir),
                test_record_template_path=(
                    Path(request.test_record_template_path)
                    if request.test_record_template_path is not None
                    else None
                ),
                fee_evaluation_template_path=(
                    Path(request.fee_evaluation_template_path)
                    if request.fee_evaluation_template_path is not None
                    else None
                ),
                overwrite=request.overwrite,
                include_test_record=request.include_test_record,
                include_fee_evaluation=request.include_fee_evaluation,
            )
        )
    except TestRecordFeeDocumentGenerationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TestRecordFeeDocumentGenerationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _register_generated_outputs(output_service, result)
    return _to_response(result)


def _register_generated_outputs(
    output_service: ProjectOutputRecordService,
    result: TestRecordFeeDocumentGenerationResult,
) -> None:
    for item in result.generated_files:
        if item.kind == "test_record":
            kind = ProjectOutputKind.TEST_RECORD_FORM
        elif item.kind == "fee_evaluation":
            kind = ProjectOutputKind.FEE_EVALUATION
        else:
            continue
        status = (
            ProjectOutputStatus.CURRENT
            if item.status in {"generated", "copied", "already_in_place"}
            else ProjectOutputStatus.FAILED
        )
        output_service.register_output(
            RegisterProjectOutputCommand(
                project_id=result.project_id,
                output_kind=kind,
                status=status,
                source=ProjectOutputSource.SYSTEM_GENERATED,
                output_path=str(item.output_path) if item.output_path is not None else None,
                draft_id=result.draft_id if status is ProjectOutputStatus.CURRENT else None,
                note="; ".join(item.warnings) if item.warnings else None,
            )
        )


def _to_response(
    result: TestRecordFeeDocumentGenerationResult,
) -> TestRecordFeeDocumentGenerationResponse:
    """Convert application result to API response DTO."""
    return TestRecordFeeDocumentGenerationResponse(
        project_id=result.project_id,
        draft_id=result.draft_id,
        generated_files=[_document_response(item) for item in result.generated_files],
        warnings=list(result.warnings),
    )


def _document_response(
    item: GeneratedApprovalDocument,
) -> GeneratedApprovalDocumentResponse:
    """Convert one generated-document record into a response entry."""
    return GeneratedApprovalDocumentResponse(
        kind=item.kind,
        source_template_path=str(item.source_template_path),
        output_path=str(item.output_path) if item.output_path is not None else None,
        status=item.status,
        warnings=list(item.warnings),
    )
