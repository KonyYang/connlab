"""HTTP boundary for a zero-write live Matrix Editor XLSX export."""

from __future__ import annotations

from typing import Literal
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from backend.api.dependencies_matrix_editor_live_xlsx_export import (
    get_matrix_editor_live_xlsx_export_service,
)
from backend.application.matrix_editor_live_xlsx_export_service import (
    MatrixEditorLiveXlsxExportCell,
    MatrixEditorLiveXlsxExportError,
    MatrixEditorLiveXlsxExportGroup,
    MatrixEditorLiveXlsxExportRequest,
    MatrixEditorLiveXlsxExportRow,
    MatrixEditorLiveXlsxExportService,
)

router = APIRouter(tags=["matrix-editor-live-xlsx-export"])
MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class CellRequest(BaseModel):
    group_id: str = Field(min_length=1, max_length=128)
    step_text: str = Field(default="", max_length=255)


class GroupRequest(BaseModel):
    group_id: str = Field(min_length=1, max_length=128)
    group_key: str = Field(min_length=1, max_length=128)
    group_label: str = Field(min_length=1, max_length=255)
    sample_size: str = Field(default="", max_length=255)
    time_display: str = Field(default="", max_length=32)


class RowRequest(BaseModel):
    row_id: str = Field(min_length=1, max_length=128)
    test_item: str = Field(default="", max_length=2048)
    section: str = Field(default="", max_length=2048)
    test_method: str = Field(default="", max_length=2048)
    condition: str = Field(default="", max_length=2048)
    requirement: str = Field(default="", max_length=2048)
    cells: list[CellRequest]


class LiveXlsxExportRequest(BaseModel):
    source: Literal["matrix_editor_current_ui_state"]
    project_reference: str = Field(min_length=1, max_length=255)
    groups: list[GroupRequest]
    rows: list[RowRequest]


@router.post("/api/projects/{project_id}/matrix-editor/live-xlsx-export")
def export_live_matrix_xlsx(
    project_id: str,
    request: LiveXlsxExportRequest,
    service: MatrixEditorLiveXlsxExportService = Depends(
        get_matrix_editor_live_xlsx_export_service
    ),
) -> Response:
    """Return an immutable current-UI snapshot as XLSX bytes."""
    del project_id
    try:
        result = service.export(
            MatrixEditorLiveXlsxExportRequest(
                source=request.source,
                project_reference=request.project_reference,
                groups=tuple(
                    MatrixEditorLiveXlsxExportGroup(
                        item.group_id, item.group_key, item.group_label,
                        item.sample_size, item.time_display,
                    )
                    for item in request.groups
                ),
                rows=tuple(
                    MatrixEditorLiveXlsxExportRow(
                        item.row_id, item.test_item, item.section, item.test_method,
                        item.condition, item.requirement,
                        tuple(
                            MatrixEditorLiveXlsxExportCell(cell.group_id, cell.step_text)
                            for cell in item.cells
                        ),
                    )
                    for item in request.rows
                ),
            )
        )
    except MatrixEditorLiveXlsxExportError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "matrix_editor_live_xlsx_export_blocked",
                "message": str(exc),
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "matrix_editor_live_xlsx_export_failed",
                "message": "Matrix export could not be created.",
            },
        ) from exc
    disposition = (
        'attachment; filename="Matrix-Draft.xlsx"; '
        f"filename*=UTF-8''{quote(result.file_name)}"
    )
    return Response(
        result.content,
        media_type=MEDIA_TYPE,
        headers={"Content-Disposition": disposition},
    )
