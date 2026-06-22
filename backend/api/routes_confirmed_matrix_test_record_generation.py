"""Confirmed-Matrix-backed Test Record Word generation API route."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from backend.api.dependencies import (
    get_confirmed_matrix_test_record_document_generation_service,
    get_settings,
)
from backend.application.confirmed_matrix_test_record_document_generation_service import (
    ConfirmedMatrixTestRecordDocumentGenerationError,
    ConfirmedMatrixTestRecordDocumentGenerationNotFoundError,
    ConfirmedMatrixTestRecordDocumentGenerationService,
    GenerateConfirmedMatrixTestRecordDocumentCommand,
)
from backend.shared.config import Settings


router = APIRouter(tags=["confirmed-matrix-test-record-generation"])


@router.post("/api/projects/{project_id}/confirmed-matrix/test-record-draft/generate")
def generate_confirmed_matrix_test_record_draft(
    project_id: str,
    service: ConfirmedMatrixTestRecordDocumentGenerationService = Depends(
        get_confirmed_matrix_test_record_document_generation_service
    ),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    """Generate and return one Word Test Record draft from active ConfirmedMatrix."""
    if settings.test_record.template_path is None:
        raise HTTPException(
            status_code=422,
            detail="Test Record template path is not configured.",
        )
    try:
        result = service.generate(
            GenerateConfirmedMatrixTestRecordDocumentCommand(
                project_id=project_id,
                output_dir=settings.data_dir / "generated_test_records",
                template_path=settings.test_record.template_path,
            )
        )
    except ConfirmedMatrixTestRecordDocumentGenerationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConfirmedMatrixTestRecordDocumentGenerationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    headers = {}
    if result.confirmed_basic_information_version is not None:
        headers["X-ConnLab-Basic-Information-Version"] = str(
            result.confirmed_basic_information_version
        )
    if result.confirmed_basic_information_source_signature_hash is not None:
        headers["X-ConnLab-Basic-Information-Source-Hash"] = (
            result.confirmed_basic_information_source_signature_hash
        )
    return FileResponse(
        path=result.output_path,
        filename=result.file_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )
