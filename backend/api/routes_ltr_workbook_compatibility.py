"""API route for real LTR workbook compatibility baseline checks."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_ltr_workbook_compatibility_service
from backend.application.ltr_workbook_compatibility_service import (
    LtrWorkbookCompatibilityNotFoundError,
    LtrWorkbookCompatibilityResult,
    LtrWorkbookCompatibilityService,
)


router = APIRouter(tags=["ltr-workbook"])


class LtrWorkbookCompatibilityResponse(BaseModel):
    """Read-only compatibility baseline response."""

    compatible: bool
    resource_path: str | None
    extension: str | None
    workbook_open_read_ok: bool
    workbook_read_only: bool | None
    sheet_names: list[str]
    annual_sheet_names: list[str]
    write_enabled: bool
    modify_password_configured: bool
    lock_dir_configured: bool
    backup_dir_configured: bool
    blockers: list[str]
    notes: list[str]


@router.get(
    "/api/external-resources/ltr-workbook/compatibility-baseline",
    response_model=LtrWorkbookCompatibilityResponse,
)
def check_ltr_workbook_compatibility_baseline(
    service: LtrWorkbookCompatibilityService = Depends(
        get_ltr_workbook_compatibility_service
    ),
) -> LtrWorkbookCompatibilityResponse:
    """Return compatibility baseline for real public-drive workbook operations."""
    try:
        return _to_response(service.check())
    except LtrWorkbookCompatibilityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, RuntimeError, FileNotFoundError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _to_response(
    result: LtrWorkbookCompatibilityResult,
) -> LtrWorkbookCompatibilityResponse:
    """Convert domain result to API response."""
    return LtrWorkbookCompatibilityResponse(
        compatible=result.compatible,
        resource_path=result.resource_path,
        extension=result.extension,
        workbook_open_read_ok=result.workbook_open_read_ok,
        workbook_read_only=result.workbook_read_only,
        sheet_names=list(result.sheet_names),
        annual_sheet_names=list(result.annual_sheet_names),
        write_enabled=result.write_enabled,
        modify_password_configured=result.modify_password_configured,
        lock_dir_configured=result.lock_dir_configured,
        backup_dir_configured=result.backup_dir_configured,
        blockers=list(result.blockers),
        notes=list(result.notes),
    )
