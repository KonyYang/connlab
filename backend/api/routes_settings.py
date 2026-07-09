"""Settings API routes for local operator-managed configuration."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.application.ltr_workbook_password_settings_service import (
    LtrWorkbookPasswordSettingsError,
    LtrWorkbookPasswordSettingsService,
)


router = APIRouter(tags=["settings"])


class LtrWorkbookPasswordStatusResponse(BaseModel):
    """Password configuration status for the local Settings page editor."""

    configured: bool
    overridden_by_environment: bool = False
    password: str | None = None


class UpdateLtrWorkbookPasswordRequest(BaseModel):
    """Request body for updating the LTR workbook password."""

    password: str = Field(min_length=1)
    operator_confirmed: bool = False


@router.get(
    "/api/settings/ltr-workbook-password",
    response_model=LtrWorkbookPasswordStatusResponse,
)
def get_ltr_workbook_password_status() -> LtrWorkbookPasswordStatusResponse:
    """Return whether the LTR workbook password is configured."""
    return _to_response(LtrWorkbookPasswordSettingsService().status())


@router.put(
    "/api/settings/ltr-workbook-password",
    response_model=LtrWorkbookPasswordStatusResponse,
)
def update_ltr_workbook_password(
    request: UpdateLtrWorkbookPasswordRequest,
) -> LtrWorkbookPasswordStatusResponse:
    """Update the local LTR workbook password after explicit confirmation."""
    try:
        return _to_response(
            LtrWorkbookPasswordSettingsService().update_password(
                request.password,
                operator_confirmed=request.operator_confirmed,
            )
        )
    except LtrWorkbookPasswordSettingsError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _to_response(status) -> LtrWorkbookPasswordStatusResponse:
    return LtrWorkbookPasswordStatusResponse(
        configured=status.configured,
        overridden_by_environment=status.overridden_by_environment,
        password=status.password,
    )
