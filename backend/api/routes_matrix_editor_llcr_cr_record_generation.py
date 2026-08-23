"""Current-state Matrix Editor LLCR/CR workbook generation route."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.api.dependencies import (
    get_matrix_editor_llcr_cr_record_generation_service,
)
from backend.application.matrix_editor_llcr_cr_record_generation_service import (
    GenerateMatrixEditorLlcrCrRecordCommand,
    MatrixEditorLlcrCrRecordGenerationError,
    MatrixEditorLlcrCrRecordGenerationService,
)
from backend.application.matrix_editor_llcr_cr_record_projection import (
    MatrixEditorLlcrCrRecordGroupInput,
    MatrixEditorLlcrCrRecordRowInput,
)

router = APIRouter(tags=["matrix-editor-llcr-cr-record-generation"])
_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class MatrixEditorLlcrCrRecordGroupRequest(BaseModel):
    group_key: str = Field(min_length=1)
    group_label: str = Field(min_length=1)
    sample_quantity_expression: str = ""
    sample_note: str | None = None


class MatrixEditorLlcrCrRecordRowRequest(BaseModel):
    test_item: str = ""
    section: str = ""
    method: str = ""
    condition: str = ""
    requirement: str = ""
    is_sample_row: bool = False
    group_values: dict[str, str] = Field(default_factory=dict)


class MatrixEditorLlcrCrRecordDraftRequest(BaseModel):
    source: Literal["matrix_editor_current_ui_state"]
    record_type: Literal["llcr", "cr"]
    groups: list[MatrixEditorLlcrCrRecordGroupRequest]
    rows: list[MatrixEditorLlcrCrRecordRowRequest]


@router.post(
    "/api/projects/{project_id}/matrix-editor/llcr-cr-record-draft/generate"
)
def generate_matrix_editor_llcr_cr_record_draft(
    project_id: str,
    request: MatrixEditorLlcrCrRecordDraftRequest,
    service: MatrixEditorLlcrCrRecordGenerationService = Depends(
        get_matrix_editor_llcr_cr_record_generation_service
    ),
) -> FileResponse:
    """Return one preview workbook generated only from current UI-state input."""
    try:
        result = service.generate(
            GenerateMatrixEditorLlcrCrRecordCommand(
                project_id=project_id,
                record_type=request.record_type,
                groups=tuple(
                    MatrixEditorLlcrCrRecordGroupInput(
                        group_key=group.group_key,
                        group_label=group.group_label,
                        sample_quantity_expression=group.sample_quantity_expression,
                        sample_note=group.sample_note,
                    )
                    for group in request.groups
                ),
                rows=tuple(
                    MatrixEditorLlcrCrRecordRowInput(
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
    except MatrixEditorLlcrCrRecordGenerationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return FileResponse(
        path=result.output_path,
        filename=result.file_name,
        media_type=_XLSX_MEDIA_TYPE,
    )
