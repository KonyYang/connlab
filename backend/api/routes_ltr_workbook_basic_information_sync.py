"""LTR workbook Basic Information synchronization API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_ltr_workbook_basic_information_sync_service
from backend.application.ltr_workbook_basic_information_sync_service import (
    CommitLtrWorkbookBasicInformationSyncCommand,
    LtrWorkbookBasicInformationSyncError,
    LtrWorkbookBasicInformationSyncPreview,
    LtrWorkbookBasicInformationSyncResult,
    LtrWorkbookBasicInformationSyncService,
    PreviewLtrWorkbookBasicInformationSyncCommand,
)
from backend.infrastructure.office import LtrWorkbookLockTimeoutError


router = APIRouter(tags=["ltr-workbook-basic-information-sync"])


class LtrWorkbookBasicInformationSyncColumnResponse(BaseModel):
    """One workbook column value preview."""

    column: str
    field_name: str
    value: object


class LtrWorkbookBasicInformationSyncPreviewResponse(BaseModel):
    """LTR workbook Basic Information sync preview response."""

    status: str
    project_id: str
    ltr_number: str
    workbook_path: str | None
    target_sheet: str | None
    target_row: int | None
    columns: list[LtrWorkbookBasicInformationSyncColumnResponse]
    confirmed_basic_information_version: int | None
    confirmed_basic_information_source_signature_hash: str | None
    blockers: list[str]
    warnings: list[str]


class LtrWorkbookBasicInformationSyncCommitRequest(BaseModel):
    """Commit request for LTR workbook Basic Information sync."""

    operator_confirmed: bool
    preview_acknowledged: bool
    expected_confirmed_basic_information_version: int
    expected_confirmed_basic_information_source_signature_hash: str


class LtrWorkbookBasicInformationSyncCommitResponse(BaseModel):
    """Commit response for LTR workbook Basic Information sync."""

    project_id: str
    ltr_number: str
    workbook_path: str
    backup_path: str
    sheet_name: str
    row_number: int
    confirmed_basic_information_version: int
    confirmed_basic_information_source_signature_hash: str


@router.get(
    "/api/projects/{project_id}/ltr-workbook/basic-information-sync/preview",
    response_model=LtrWorkbookBasicInformationSyncPreviewResponse,
)
def preview_ltr_workbook_basic_information_sync(
    project_id: str,
    service: LtrWorkbookBasicInformationSyncService = Depends(
        get_ltr_workbook_basic_information_sync_service
    ),
) -> LtrWorkbookBasicInformationSyncPreviewResponse:
    """Preview syncing confirmed Basic Information into an existing LTR row."""
    try:
        return _preview_response(
            service.preview(
                PreviewLtrWorkbookBasicInformationSyncCommand(project_id=project_id)
            )
        )
    except LtrWorkbookLockTimeoutError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except LtrWorkbookBasicInformationSyncError as exc:
        detail = str(exc)
        raise HTTPException(
            status_code=_basic_information_sync_error_status(detail),
            detail=detail,
        ) from exc


@router.post(
    "/api/projects/{project_id}/ltr-workbook/basic-information-sync/commit",
    response_model=LtrWorkbookBasicInformationSyncCommitResponse,
)
def commit_ltr_workbook_basic_information_sync(
    project_id: str,
    request: LtrWorkbookBasicInformationSyncCommitRequest,
    service: LtrWorkbookBasicInformationSyncService = Depends(
        get_ltr_workbook_basic_information_sync_service
    ),
) -> LtrWorkbookBasicInformationSyncCommitResponse:
    """Commit confirmed Basic Information into an existing LTR workbook row."""
    try:
        return _commit_response(
            service.commit(
                CommitLtrWorkbookBasicInformationSyncCommand(
                    project_id=project_id,
                    operator_confirmed=request.operator_confirmed,
                    preview_acknowledged=request.preview_acknowledged,
                    expected_confirmed_basic_information_version=(
                        request.expected_confirmed_basic_information_version
                    ),
                    expected_confirmed_basic_information_source_signature_hash=(
                        request.expected_confirmed_basic_information_source_signature_hash
                    ),
                )
            )
        )
    except LtrWorkbookLockTimeoutError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except LtrWorkbookBasicInformationSyncError as exc:
        detail = str(exc)
        status_code = (
            409
            if "changed after preview" in detail
            else _basic_information_sync_error_status(detail)
        )
        raise HTTPException(status_code=status_code, detail=detail) from exc


def _basic_information_sync_error_status(detail: str) -> int:
    if "Registered LTR is required" in detail:
        return 404
    return 400


def _preview_response(
    preview: LtrWorkbookBasicInformationSyncPreview,
) -> LtrWorkbookBasicInformationSyncPreviewResponse:
    return LtrWorkbookBasicInformationSyncPreviewResponse(
        status=preview.status,
        project_id=preview.project_id,
        ltr_number=preview.ltr_number,
        workbook_path=str(preview.workbook_path) if preview.workbook_path else None,
        target_sheet=preview.target_sheet,
        target_row=preview.target_row,
        columns=[
            LtrWorkbookBasicInformationSyncColumnResponse(
                column=column.column,
                field_name=column.field_name,
                value=column.value,
            )
            for column in preview.columns
        ],
        confirmed_basic_information_version=preview.confirmed_basic_information_version,
        confirmed_basic_information_source_signature_hash=(
            preview.confirmed_basic_information_source_signature_hash
        ),
        blockers=list(preview.blockers),
        warnings=list(preview.warnings),
    )


def _commit_response(
    result: LtrWorkbookBasicInformationSyncResult,
) -> LtrWorkbookBasicInformationSyncCommitResponse:
    return LtrWorkbookBasicInformationSyncCommitResponse(
        project_id=result.project_id,
        ltr_number=result.ltr_number,
        workbook_path=str(result.workbook_path),
        backup_path=str(result.backup_path),
        sheet_name=result.sheet_name,
        row_number=result.row_number,
        confirmed_basic_information_version=result.confirmed_basic_information_version,
        confirmed_basic_information_source_signature_hash=(
            result.confirmed_basic_information_source_signature_hash
        ),
    )
