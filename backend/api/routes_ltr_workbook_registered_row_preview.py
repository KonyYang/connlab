"""Registered LTR workbook row read-only preview API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.api.dependencies import get_registered_ltr_workbook_row_preview_service
from backend.application.registered_ltr_workbook_row_preview_service import (
    RegisteredLtrWorkbookRowPreview,
    RegisteredLtrWorkbookRowPreviewCommand,
    RegisteredLtrWorkbookRowPreviewService,
)


router = APIRouter(tags=["ltr-workbook-registered-row-preview"])


class RegisteredLtrWorkbookRowPreviewValueResponse(BaseModel):
    """One read-only registered LTR workbook row value."""

    field_name: str
    label: str
    value: object
    is_blank: bool


class RegisteredLtrWorkbookRowPreviewResponse(BaseModel):
    """Read-only registered LTR workbook row preview response."""

    status: str
    project_id: str
    ltr_number: str | None
    message: str
    workbook_path: str | None
    sheet_name: str | None
    row_number: int | None
    row_values: list[RegisteredLtrWorkbookRowPreviewValueResponse]
    blockers: list[str]
    warnings: list[str]


@router.get(
    "/api/projects/{project_id}/ltr-workbook/registered-row-preview",
    response_model=RegisteredLtrWorkbookRowPreviewResponse,
)
def preview_registered_ltr_workbook_row(
    project_id: str,
    service: RegisteredLtrWorkbookRowPreviewService = Depends(
        get_registered_ltr_workbook_row_preview_service
    ),
) -> RegisteredLtrWorkbookRowPreviewResponse:
    """Preview the public LTR workbook row for the project's registered DL number."""
    return _preview_response(
        service.preview(RegisteredLtrWorkbookRowPreviewCommand(project_id=project_id))
    )


def _preview_response(
    preview: RegisteredLtrWorkbookRowPreview,
) -> RegisteredLtrWorkbookRowPreviewResponse:
    return RegisteredLtrWorkbookRowPreviewResponse(
        status=preview.status,
        project_id=preview.project_id,
        ltr_number=preview.ltr_number,
        message=preview.message,
        workbook_path=str(preview.workbook_path) if preview.workbook_path else None,
        sheet_name=preview.sheet_name,
        row_number=preview.row_number,
        row_values=[
            RegisteredLtrWorkbookRowPreviewValueResponse(
                field_name=value.field_name,
                label=value.label,
                value=value.value,
                is_blank=value.is_blank,
            )
            for value in preview.row_values
        ],
        blockers=list(preview.blockers),
        warnings=list(preview.warnings),
    )
