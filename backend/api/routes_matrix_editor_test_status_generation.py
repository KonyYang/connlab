"""Matrix-Editor-current-state Test Status workbook generation route."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from backend.api.dependencies import (
    get_matrix_editor_test_status_workbook_generation_service,
    get_settings,
)
from backend.api.routes_matrix_editor_test_record_generation import (
    MatrixEditorTestRecordDraftRequest,
)
from backend.application.matrix_editor_test_status_workbook_generation_service import (
    GenerateMatrixEditorTestStatusWorkbookCommand,
    MatrixEditorTestStatusGroupInput,
    MatrixEditorTestStatusRowInput,
    MatrixEditorTestStatusWorkbookGenerationError,
    MatrixEditorTestStatusWorkbookGenerationNotFoundError,
    MatrixEditorTestStatusWorkbookGenerationService,
)
from backend.shared.config import Settings


router = APIRouter(tags=["matrix-editor-test-status-generation"])


class MatrixEditorTestStatusDraftRequest(MatrixEditorTestRecordDraftRequest):
    """Current Matrix Editor state used for preview-only Test Status output."""

    project_reference: str | None = None


@router.post("/api/projects/{project_id}/matrix-editor/test-status-draft/generate")
def generate_matrix_editor_test_status_draft(
    project_id: str,
    request: MatrixEditorTestStatusDraftRequest,
    service: MatrixEditorTestStatusWorkbookGenerationService = Depends(
        get_matrix_editor_test_status_workbook_generation_service
    ),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    if request.source != "matrix_editor_current_ui_state":
        raise HTTPException(
            status_code=422,
            detail="Matrix Editor Test Status preview requires current UI state payload.",
        )
    try:
        result = service.generate(
            GenerateMatrixEditorTestStatusWorkbookCommand(
                project_id=project_id,
                project_reference=request.project_reference,
                output_dir=settings.data_dir / "generated_test_status_previews",
                groups=tuple(
                    MatrixEditorTestStatusGroupInput(
                        group.group_key,
                        group.group_label,
                        group.sample_quantity_expression,
                    )
                    for group in request.groups
                ),
                rows=tuple(
                    MatrixEditorTestStatusRowInput(
                        row.test_item,
                        row.is_sample_row,
                        row.group_values,
                    )
                    for row in request.rows
                ),
            )
        )
    except MatrixEditorTestStatusWorkbookGenerationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MatrixEditorTestStatusWorkbookGenerationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return FileResponse(
        path=result.output_path,
        filename=result.file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
