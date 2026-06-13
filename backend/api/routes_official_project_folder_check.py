"""Official project folder check and repair API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_official_project_folder_check_service
from backend.application.official_project_folder_check_service import (
    OfficialFolderCheckItem,
    OfficialFolderCheckPreview,
    OfficialFolderRepairResult,
    OfficialProjectFolderCheckConflictError,
    OfficialProjectFolderCheckError,
    OfficialProjectFolderCheckNotFoundError,
    OfficialProjectFolderCheckService,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/official-folder",
    tags=["official-folder"],
)


class OfficialFolderCheckItemResponse(BaseModel):
    """Response DTO for one folder-check item."""

    key: str
    label: str
    kind: str
    status: str
    path: str | None
    message: str
    repairable: bool = False


class OfficialFolderCheckPreviewResponse(BaseModel):
    """Response DTO for Official project folder check preview."""

    project_id: str
    status: str
    local_workspace_path: str | None
    official_project_folder_path: str | None
    required_folders: list[OfficialFolderCheckItemResponse]
    required_files: list[OfficialFolderCheckItemResponse]
    blockers: list[str]
    warnings: list[str]
    next_action: str


class OfficialFolderRepairResponse(BaseModel):
    """Response DTO for missing-folder repair."""

    project_id: str
    repair_status: str
    created_paths: list[str]
    unresolved_conflicts: list[str]
    errors: list[str]
    preview: OfficialFolderCheckPreviewResponse


@router.get("/check", response_model=OfficialFolderCheckPreviewResponse)
def check_official_folder(
    project_id: str,
    service: OfficialProjectFolderCheckService = Depends(
        get_official_project_folder_check_service
    ),
) -> OfficialFolderCheckPreviewResponse:
    """Return a read-only Official project folder check preview."""
    try:
        return _preview_response(service.preview(project_id))
    except OfficialProjectFolderCheckNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OfficialProjectFolderCheckError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/repair-folders", response_model=OfficialFolderRepairResponse)
def repair_official_folder(
    project_id: str,
    service: OfficialProjectFolderCheckService = Depends(
        get_official_project_folder_check_service
    ),
) -> OfficialFolderRepairResponse:
    """Create missing Official project folder directories only."""
    try:
        return _repair_response(service.repair_folders(project_id))
    except OfficialProjectFolderCheckNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OfficialProjectFolderCheckConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except OfficialProjectFolderCheckError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _preview_response(
    preview: OfficialFolderCheckPreview,
) -> OfficialFolderCheckPreviewResponse:
    """Convert preview dataclass into a response DTO."""
    return OfficialFolderCheckPreviewResponse(
        project_id=preview.project_id,
        status=preview.status,
        local_workspace_path=_path(preview.local_workspace_path),
        official_project_folder_path=_path(preview.official_project_folder_path),
        required_folders=[_item_response(item) for item in preview.required_folders],
        required_files=[_item_response(item) for item in preview.required_files],
        blockers=list(preview.blockers),
        warnings=list(preview.warnings),
        next_action=preview.next_action,
    )


def _repair_response(result: OfficialFolderRepairResult) -> OfficialFolderRepairResponse:
    """Convert repair result dataclass into a response DTO."""
    return OfficialFolderRepairResponse(
        project_id=result.project_id,
        repair_status=result.repair_status,
        created_paths=[str(path) for path in result.created_paths],
        unresolved_conflicts=[str(path) for path in result.unresolved_conflicts],
        errors=list(result.errors),
        preview=_preview_response(result.preview),
    )


def _item_response(item: OfficialFolderCheckItem) -> OfficialFolderCheckItemResponse:
    """Convert one check item into a response DTO."""
    return OfficialFolderCheckItemResponse(
        key=item.key,
        label=item.label,
        kind=item.kind,
        status=item.status,
        path=_path(item.path),
        message=item.message,
        repairable=item.repairable,
    )


def _path(path: Path | None) -> str | None:
    """Return a path string or None."""
    return str(path) if path is not None else None
