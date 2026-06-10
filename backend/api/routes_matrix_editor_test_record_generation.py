"""Matrix-Editor-current-state Test Record preview generation API route."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.api.dependencies import (
    get_matrix_editor_test_record_document_generation_service,
    get_settings,
)
from backend.application.matrix_editor_test_record_document_generation_service import (
    GenerateMatrixEditorTestRecordDocumentCommand,
    MatrixEditorTestRecordDocumentGenerationError,
    MatrixEditorTestRecordDocumentGenerationNotFoundError,
    MatrixEditorTestRecordDocumentGenerationService,
    MatrixEditorTestRecordGroupInput,
    MatrixEditorTestRecordRowInput,
)
from backend.shared.config import Settings


router = APIRouter(tags=["matrix-editor-test-record-generation"])


class MatrixEditorTestRecordGroupRequest(BaseModel):
    """Current Matrix Editor group payload for preview generation."""

    group_key: str = Field(min_length=1)
    group_label: str = Field(min_length=1)
    sample_quantity_expression: str = ""


class MatrixEditorTestRecordRowRequest(BaseModel):
    """Current Matrix Editor row payload for preview generation."""

    test_item: str = ""
    section: str = ""
    method: str = ""
    condition: str = ""
    requirement: str = ""
    is_sample_row: bool = False
    group_values: dict[str, str] = Field(default_factory=dict)


class MatrixEditorTestRecordDraftRequest(BaseModel):
    """Current Matrix Editor state payload for preview-only Test Record output."""

    source: str = "matrix_editor_current_ui_state"
    groups: list[MatrixEditorTestRecordGroupRequest]
    rows: list[MatrixEditorTestRecordRowRequest]


@router.post("/api/projects/{project_id}/matrix-editor/test-record-draft/generate")
def generate_matrix_editor_test_record_draft_preview(
    project_id: str,
    request: MatrixEditorTestRecordDraftRequest,
    service: MatrixEditorTestRecordDocumentGenerationService = Depends(
        get_matrix_editor_test_record_document_generation_service
    ),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    """Generate and return one preview Test Record from current Matrix Editor state."""
    if request.source != "matrix_editor_current_ui_state":
        raise HTTPException(
            status_code=422,
            detail="Matrix Editor Test Record preview requires current UI state payload.",
        )
    if settings.test_record.template_path is None:
        raise HTTPException(
            status_code=422,
            detail="Test Record template path is not configured.",
        )
    try:
        result = service.generate(
            GenerateMatrixEditorTestRecordDocumentCommand(
                project_id=project_id,
                output_dir=settings.data_dir / "generated_test_record_previews",
                template_path=settings.test_record.template_path,
                groups=tuple(
                    MatrixEditorTestRecordGroupInput(
                        group_key=group.group_key,
                        group_label=group.group_label,
                        sample_quantity_expression=group.sample_quantity_expression,
                    )
                    for group in request.groups
                ),
                rows=tuple(
                    MatrixEditorTestRecordRowInput(
                        test_item=row.test_item,
                        section=row.section,
                        method=row.method,
                        condition=row.condition,
                        requirement=row.requirement,
                        is_sample_row=row.is_sample_row,
                        group_values=row.group_values,
                    )
                    for row in request.rows
                ),
            )
        )
    except MatrixEditorTestRecordDocumentGenerationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MatrixEditorTestRecordDocumentGenerationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return FileResponse(
        path=result.output_path,
        filename=result.file_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
