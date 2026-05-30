"""Project test-plan preview API routes."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.api.dependencies import get_project_test_plan_matrix_preview_service
from backend.application.project_test_plan_matrix_preview_service import (
    MatrixPreviewFromPathCommand,
    ProjectTestPlanMatrixPreview,
    ProjectTestPlanMatrixPreviewError,
    ProjectTestPlanMatrixPreviewService,
)
from backend.modules.test_plan import MatrixGroupPreview, MatrixStepPreview


router = APIRouter(tags=["project-test-plan"])
_PREVIEW_DIR = Path("tmp/matrix_import_previews")
_PREVIEW_TOKEN_MAP: dict[str, Path] = {}


class MatrixPreviewFromPathRequest(BaseModel):
    """Request body for local-path Matrix preview calibration."""

    source_path: str = Field(min_length=1)
    project_id: str | None = None


class TestStepPreviewResponse(BaseModel):
    """One test step in a Matrix preview response."""

    sequence: int
    raw_token: str
    suffix_note: str | None
    test_item: str
    source_section: str | None
    source_note: str | None
    source_note_origin: str | None
    source_item_section_note: str | None
    condition_summary: str | None
    method_summary: str | None
    reference_standard: str | None
    judgement_criteria: str | None
    estimated_duration_hint: str | None
    duration_source: str | None
    duration_status: str
    source_table_index: int
    source_row_index: int
    warnings: list[str]


class TestGroupPreviewResponse(BaseModel):
    """One test group in a Matrix preview response."""

    group_key: str
    group_label: str
    source_table_index: int
    extraction_status: str
    sample_size: int | None
    sample_quantity_expression: str | None
    sample_note: str | None
    steps: list[TestStepPreviewResponse]


class MatrixPreviewResponse(BaseModel):
    """Read-only Matrix preview API response."""

    project_id: str | None
    source_document_path: str
    source_document_name: str
    source_format: str
    capability_status: str
    generated_at: str
    selected_table_index: int | None
    selected_page_number: int | None = None
    selected_page_table_index: int | None = None
    candidate_tables: list[dict[str, object]] = Field(default_factory=list)
    preview_pdf_token: str | None = None
    rows: list[dict[str, object]] = Field(default_factory=list)
    groups: list[TestGroupPreviewResponse]
    warnings: list[str]
    blockers: list[str]


@router.post(
    "/api/test-plan/matrix-preview-from-path",
    response_model=MatrixPreviewResponse,
)
def preview_matrix_from_path(
    request: MatrixPreviewFromPathRequest,
    service: ProjectTestPlanMatrixPreviewService = Depends(
        get_project_test_plan_matrix_preview_service
    ),
) -> MatrixPreviewResponse:
    """Return a read-only Matrix preview for a local product specification path."""
    try:
        preview = service.preview_from_path(
            MatrixPreviewFromPathCommand(
                source_path=Path(request.source_path),
                project_id=request.project_id,
            )
        )
    except ProjectTestPlanMatrixPreviewError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _preview_response(preview)


@router.post(
    "/api/test-plan/matrix-preview-from-upload",
    response_model=MatrixPreviewResponse,
)
async def preview_matrix_from_upload(
    file: UploadFile = File(...),
    project_id: str | None = Form(default=None),
    page_number: int | None = Form(default=None),
    page_table_index: int | None = Form(default=None),
    table_text_query: str | None = Form(default=None),
    service: ProjectTestPlanMatrixPreviewService = Depends(
        get_project_test_plan_matrix_preview_service
    ),
) -> MatrixPreviewResponse:
    """Return a read-only Matrix preview for an uploaded `.docx` file."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix != ".docx":
        raise HTTPException(status_code=400, detail="Only .docx is supported.")
    original_name = file.filename or "uploaded.docx"
    temp_path: Path | None = None
    with NamedTemporaryFile(delete=False, suffix=".docx") as temp:
        content = await file.read()
        temp.write(content)
        temp_path = Path(temp.name)
    try:
        _PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
        for stale_file in _PREVIEW_DIR.glob("*.pdf"):
            stale_file.unlink(missing_ok=True)
        _PREVIEW_TOKEN_MAP.clear()
        preview_token = uuid4().hex
        preview_pdf_path = _PREVIEW_DIR / f"{preview_token}.pdf"
        table_locations = ()
        try:
            table_locations = service._office.read_word_table_locations(temp_path)
        except Exception:
            table_locations = ()
        service._office.export_word_preview_pdf(temp_path, preview_pdf_path)
        _PREVIEW_TOKEN_MAP[preview_token] = preview_pdf_path
        preview = service.preview_from_path(
            MatrixPreviewFromPathCommand(
                source_path=temp_path,
                project_id=project_id,
                page_number=page_number,
                page_table_index=page_table_index,
                table_text_query=table_text_query,
            ),
            preview_pdf_token=preview_token,
            table_locations=table_locations,
        )
        if preview.source_document_name != original_name:
            preview = ProjectTestPlanMatrixPreview(
                project_id=preview.project_id,
                source_document_path=preview.source_document_path,
                source_document_name=original_name,
                source_format=preview.source_format,
                capability_status=preview.capability_status,
                generated_at=preview.generated_at,
                groups=preview.groups,
                warnings=preview.warnings,
                blockers=preview.blockers,
                selected_table_index=preview.selected_table_index,
                selected_page_number=preview.selected_page_number,
                selected_page_table_index=preview.selected_page_table_index,
                candidate_tables=preview.candidate_tables,
                preview_pdf_token=preview.preview_pdf_token,
                rows=preview.rows,
            )
        return _preview_response(preview)
    except ProjectTestPlanMatrixPreviewError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


@router.get("/api/test-plan/matrix-preview-pdf/{token}")
def preview_matrix_pdf(token: str) -> FileResponse:
    """Serve a generated matrix preview PDF by token."""
    path = _PREVIEW_TOKEN_MAP.get(token)
    if path is None or not path.is_file():
        raise HTTPException(status_code=404, detail="Preview PDF not found.")
    resolved = path.resolve()
    preview_root = _PREVIEW_DIR.resolve()
    if not str(resolved).startswith(str(preview_root)):
        raise HTTPException(status_code=400, detail="Invalid preview token path.")
    return FileResponse(
        resolved,
        media_type="application/pdf",
        filename=resolved.name,
        headers={"Content-Disposition": f'inline; filename="{resolved.name}"'},
    )


def _preview_response(preview: ProjectTestPlanMatrixPreview) -> MatrixPreviewResponse:
    """Convert an application preview to an API response."""
    return MatrixPreviewResponse(
        project_id=preview.project_id,
        source_document_path=str(preview.source_document_path),
        source_document_name=preview.source_document_name,
        source_format=preview.source_format,
        capability_status=preview.capability_status,
        generated_at=preview.generated_at,
        selected_table_index=preview.selected_table_index,
        selected_page_number=preview.selected_page_number,
        selected_page_table_index=preview.selected_page_table_index,
        candidate_tables=list(preview.candidate_tables),
        preview_pdf_token=preview.preview_pdf_token,
        rows=[
            {
                "source_row_index": row.source_row_index,
                "test_item": row.test_item,
                "source_section": row.source_section,
                "method": row.method,
                "condition": row.condition,
                "requirement": row.requirement,
                "detail_extraction_status": row.detail_extraction_status,
                "detail_extraction_source_section": row.detail_extraction_source_section,
                "detail_extraction_notes": list(row.detail_extraction_notes),
                "group_tokens": row.group_tokens,
                "is_sample_row": row.is_sample_row,
            }
            for row in preview.rows
        ],
        groups=[_group_response(group) for group in preview.groups],
        warnings=list(preview.warnings),
        blockers=list(preview.blockers),
    )


def _group_response(group: MatrixGroupPreview) -> TestGroupPreviewResponse:
    """Convert one Matrix group to an API response."""
    return TestGroupPreviewResponse(
        group_key=group.group_key,
        group_label=group.group_label,
        source_table_index=group.source_table_index,
        extraction_status=group.extraction_status,
        sample_size=group.sample_size,
        sample_quantity_expression=group.sample_quantity_expression,
        sample_note=group.sample_note,
        steps=[_step_response(step) for step in group.steps],
    )


def _step_response(step: MatrixStepPreview) -> TestStepPreviewResponse:
    """Convert one Matrix step to an API response."""
    return TestStepPreviewResponse(
        sequence=step.sequence,
        raw_token=step.raw_token,
        suffix_note=step.suffix_note,
        test_item=step.test_item,
        source_section=step.source_section,
        source_note=step.source_note,
        source_note_origin=step.source_note_origin,
        source_item_section_note=step.source_item_section_note,
        condition_summary=step.condition_summary,
        method_summary=step.method_summary,
        reference_standard=step.reference_standard,
        judgement_criteria=step.judgement_criteria,
        estimated_duration_hint=step.estimated_duration_hint,
        duration_source=step.duration_source,
        duration_status=step.duration_status,
        source_table_index=step.source_table_index,
        source_row_index=step.source_row_index,
        warnings=list(step.warnings),
    )
