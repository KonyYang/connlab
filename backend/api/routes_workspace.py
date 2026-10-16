"""Diagnostics for the actual active data workspace."""
from fastapi import APIRouter, Depends
from backend.api.dependencies import get_session, get_settings
from backend.application.workspace_info_service import WorkspaceInfoService
from backend.infrastructure.workspace_info import WorkspaceInfoReader

router = APIRouter(prefix="/api/workspace", tags=["workspace"])


@router.get("/info")
def workspace_info(session=Depends(get_session), settings=Depends(get_settings)):
    return WorkspaceInfoService(WorkspaceInfoReader(session, settings)).read()
