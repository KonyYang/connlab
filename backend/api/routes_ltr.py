"""LTR API routes."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.application.ltr_service import (
    DuplicateActiveLtrError,
    LtrError,
    LtrNotFoundError,
    LtrService,
    RegisterLtrCommand,
)
from backend.api.dependencies import get_ltr_service
from backend.domain import LtrRecord


router = APIRouter(tags=["ltr"])


class LtrRegisterRequest(BaseModel):
    """Request body for LTR registration."""

    ltr_number: str = Field(min_length=1)
    requested_by: str | None = None
    requested_date: date | None = None
    notes: str | None = None


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


@router.post(
    "/api/projects/{project_id}/ltr",
    response_model=LtrRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_ltr(
    project_id: str,
    request: LtrRegisterRequest,
    service: LtrService = Depends(get_ltr_service),
) -> LtrRecordResponse:
    """Register an LTR for a project."""
    try:
        return _to_response(
            service.register_ltr(
                project_id,
                RegisterLtrCommand(
                    ltr_number=request.ltr_number,
                    requested_by=request.requested_by,
                    requested_date=request.requested_date,
                    notes=request.notes,
                ),
            )
        )
    except LtrNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DuplicateActiveLtrError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except LtrError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/projects/{project_id}/ltr", response_model=list[LtrRecordResponse])
def list_project_ltrs(
    project_id: str,
    service: LtrService = Depends(get_ltr_service),
) -> list[LtrRecordResponse]:
    """Return LTR records for a project."""
    try:
        return [_to_response(ltr) for ltr in service.list_project_ltrs(project_id)]
    except LtrNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/api/ltr-records", response_model=list[LtrRecordResponse])
def search_ltr_records(
    query: str = Query(default=""),
    service: LtrService = Depends(get_ltr_service),
) -> list[LtrRecordResponse]:
    """Search LTR records by query string."""
    return [_to_response(ltr) for ltr in service.search_ltrs(query)]


def _to_response(ltr: LtrRecord) -> LtrRecordResponse:
    """Convert an LTR domain record to API response."""
    return LtrRecordResponse(
        ltr_id=ltr.ltr_id,
        project_id=ltr.project_id,
        ltr_number=ltr.ltr_number,
        status=ltr.status.value,
        registered_on=ltr.registered_on,
        requested_by=ltr.requested_by,
        requested_date=ltr.requested_date,
        notes=ltr.notes,
    )
