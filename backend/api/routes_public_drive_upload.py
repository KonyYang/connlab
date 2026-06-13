"""Public-drive Project Folder upload API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_public_drive_upload_service
from backend.application.public_drive_upload_service import (
    PublicDriveUploadBlockedError,
    PublicDriveUploadConflictError,
    PublicDriveUploadError,
    PublicDriveUploadItem,
    PublicDriveUploadNotFoundError,
    PublicDriveUploadPreview,
    PublicDriveUploadResult,
    PublicDriveUploadService,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/public-drive",
    tags=["public-drive"],
)


class PublicDriveUploadItemResponse(BaseModel):
    """Response DTO for one public-drive upload item."""

    kind: str
    relative_path: str
    local_path: str | None
    public_path: str
    action: str
    status: str
    message: str


class PublicDriveUploadPreviewResponse(BaseModel):
    """Response DTO for public-drive upload preview."""

    project_id: str
    status: str
    local_official_folder_path: str | None
    public_project_folder_path: str | None
    items: list[PublicDriveUploadItemResponse]
    blockers: list[str]
    warnings: list[str]
    counts: dict[str, int]
    next_action: str


class PublicDriveUploadResultResponse(BaseModel):
    """Response DTO for public-drive upload execution."""

    project_id: str
    upload_status: str
    copied: list[PublicDriveUploadItemResponse]
    updated: list[PublicDriveUploadItemResponse]
    skipped: list[PublicDriveUploadItemResponse]
    conflicts: list[PublicDriveUploadItemResponse]
    failed: list[PublicDriveUploadItemResponse]
    errors: list[str]
    preview: PublicDriveUploadPreviewResponse


@router.get("/preview", response_model=PublicDriveUploadPreviewResponse)
def preview_public_drive_upload(
    project_id: str,
    service: PublicDriveUploadService = Depends(get_public_drive_upload_service),
) -> PublicDriveUploadPreviewResponse:
    """Return a read-only public-drive upload preview."""
    try:
        return _preview_response(service.preview(project_id))
    except PublicDriveUploadNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PublicDriveUploadError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/upload", response_model=PublicDriveUploadResultResponse)
def upload_public_drive(
    project_id: str,
    service: PublicDriveUploadService = Depends(get_public_drive_upload_service),
) -> PublicDriveUploadResultResponse:
    """Execute a safe public-drive upload after a fresh preview."""
    try:
        return _result_response(service.upload(project_id))
    except PublicDriveUploadNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (PublicDriveUploadBlockedError, PublicDriveUploadConflictError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except PublicDriveUploadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _preview_response(preview: PublicDriveUploadPreview) -> PublicDriveUploadPreviewResponse:
    """Convert a preview dataclass into an API response."""
    return PublicDriveUploadPreviewResponse(
        project_id=preview.project_id,
        status=preview.status,
        local_official_folder_path=_path(preview.local_official_folder_path),
        public_project_folder_path=_path(preview.public_project_folder_path),
        items=[_item_response(item) for item in preview.items],
        blockers=list(preview.blockers),
        warnings=list(preview.warnings),
        counts=dict(preview.counts),
        next_action=preview.next_action,
    )


def _result_response(result: PublicDriveUploadResult) -> PublicDriveUploadResultResponse:
    """Convert an upload result dataclass into an API response."""
    return PublicDriveUploadResultResponse(
        project_id=result.project_id,
        upload_status=result.upload_status,
        copied=[_item_response(item) for item in result.copied],
        updated=[_item_response(item) for item in result.updated],
        skipped=[_item_response(item) for item in result.skipped],
        conflicts=[_item_response(item) for item in result.conflicts],
        failed=[_item_response(item) for item in result.failed],
        errors=list(result.errors),
        preview=_preview_response(result.preview),
    )


def _item_response(item: PublicDriveUploadItem) -> PublicDriveUploadItemResponse:
    """Convert one upload item into an API response."""
    return PublicDriveUploadItemResponse(
        kind=item.kind,
        relative_path=item.relative_path.as_posix(),
        local_path=_path(item.local_path),
        public_path=str(item.public_path),
        action=item.action,
        status=item.status,
        message=item.message,
    )


def _path(path: Path | None) -> str | None:
    """Return a path string or None."""
    return str(path) if path is not None else None
