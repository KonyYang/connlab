"""LTR workbook write API routes."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.api.dependencies import get_ltr_workbook_write_commit_service
from backend.application.ltr_service import LtrError
from backend.application.ltr_workbook_write_commit_service import (
    CommitLtrWorkbookWriteCommand,
    LtrWorkbookWriteCommitError,
    LtrWorkbookWriteCommitResult,
    LtrWorkbookWriteCommitService,
)
from backend.application.project_lifecycle_service import ProjectLifecycleError
from backend.domain import LtrRecord
from backend.infrastructure.office import LtrWorkbookWriteError


router = APIRouter(tags=["ltr-workbook"])


class LtrRecordResponse(BaseModel):
    """LTR record API response."""

    ltr_id: str
    project_id: str
    ltr_number: str
    status: str
    registered_on: date | None = None
    requested_by: str | None = None
    requested_date: date | None = None
    notes: str | None = None


class LtrWorkbookWriteCommitRequest(BaseModel):
    """Request body for confirmed external LTR workbook write commit."""

    plan_date: date
    operator_confirmed: bool
    preview_acknowledged: bool
    allow_year_sheet_bootstrap: bool = False
    number_input: str | None = None
    test_item: str = Field(min_length=1)
    sample_description: str = Field(min_length=1)
    location: str = Field(min_length=1)
    test_type_in_sheet: str = Field(min_length=1)
    project_leader: str = Field(min_length=1)
    requested_by: str | None = None
    requested_date: date | None = None
    operator_note: str | None = None


class LtrWorkbookWriteCommitResponse(BaseModel):
    """Response after a committed external LTR workbook write."""

    ltr: LtrRecordResponse
    action: str
    workbook_path: str
    backup_path: str
    sheet_name: str
    row_number: int
    ltr_number: str


@router.post(
    "/api/projects/{project_id}/ltr-workbook/write-commit",
    response_model=LtrWorkbookWriteCommitResponse,
    status_code=status.HTTP_201_CREATED,
)
def commit_ltr_workbook_write(
    project_id: str,
    request: LtrWorkbookWriteCommitRequest,
    service: LtrWorkbookWriteCommitService = Depends(
        get_ltr_workbook_write_commit_service
    ),
) -> LtrWorkbookWriteCommitResponse:
    """Commit an external LTR workbook write after preview acknowledgement."""
    try:
        return _workbook_write_commit_to_response(
            service.commit_project(
                project_id,
                CommitLtrWorkbookWriteCommand(
                    plan_date=request.plan_date,
                    operator_confirmed=request.operator_confirmed,
                    preview_acknowledged=request.preview_acknowledged,
                    allow_year_sheet_bootstrap=request.allow_year_sheet_bootstrap,
                    number_input=request.number_input,
                    test_item=request.test_item,
                    sample_description=request.sample_description,
                    location=request.location,
                    test_type_in_sheet=request.test_type_in_sheet,
                    project_leader=request.project_leader,
                    requested_by=request.requested_by,
                    requested_date=request.requested_date,
                    operator_note=request.operator_note,
                ),
            )
        )
    except (LtrWorkbookWriteCommitError, LtrWorkbookWriteError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (LtrError, ProjectLifecycleError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _workbook_write_commit_to_response(
    result: LtrWorkbookWriteCommitResult,
) -> LtrWorkbookWriteCommitResponse:
    """Convert committed workbook write result to API response."""
    return LtrWorkbookWriteCommitResponse(
        ltr=_to_response(result.ltr),
        action=result.action,
        workbook_path=str(result.workbook_path),
        backup_path=str(result.backup_path),
        sheet_name=result.pointer.sheet_name,
        row_number=result.pointer.row_number,
        ltr_number=result.ltr_number,
    )


def _to_response(record: LtrRecord) -> LtrRecordResponse:
    """Convert a domain LTR record to an API response."""
    return LtrRecordResponse(
        ltr_id=record.ltr_id,
        project_id=record.project_id,
        ltr_number=record.ltr_number,
        status=record.status.value,
        registered_on=record.registered_on,
        requested_by=record.requested_by,
        requested_date=record.requested_date,
        notes=record.notes,
    )
