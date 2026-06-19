"""Request-material collection API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_project_request_material_collection_service
from backend.application.project_request_material_collection_service import (
    ProjectRequestMaterialCollectionConflictError,
    ProjectRequestMaterialCollectionError,
    ProjectRequestMaterialCollectionNotFoundError,
    ProjectRequestMaterialCollectionService,
    RequestMaterialCollectResult,
    RequestMaterialPreview,
    RequestMaterialPreviewItem,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/request-material",
    tags=["request-material"],
)


class RequestMaterialPreviewItemResponse(BaseModel):
    """Response DTO for one request-material target item."""

    source_asset_id: str
    source_asset_type: str
    source_role: str | None = None
    source_name: str
    source_path: str
    dedupe_key: str
    target_area: str
    target_path: str
    action: str
    status: str
    message: str
    review_required: bool = False
    size_bytes: int | None = None
    sha256: str | None = None


class RequestMaterialPreviewResponse(BaseModel):
    """Response DTO for request-material preview."""

    project_id: str
    local_workspace_path: str | None
    source_book_path: str | None
    official_project_folder_path: str | None
    status: str
    items: list[RequestMaterialPreviewItemResponse]
    blockers: list[str]
    warnings: list[str]


class RequestMaterialCollectResponse(RequestMaterialPreviewResponse):
    """Response DTO for request-material collection execution."""

    collection_id: str
    copied_paths: list[str]
    already_present_paths: list[str]
    skipped_paths: list[str]
    missing_source_paths: list[str]
    conflict_paths: list[str]


@router.get("/preview", response_model=RequestMaterialPreviewResponse)
def preview_request_material(
    project_id: str,
    service: ProjectRequestMaterialCollectionService = Depends(
        get_project_request_material_collection_service
    ),
) -> RequestMaterialPreviewResponse:
    """Preview request material before copying it into the Project Folder."""
    try:
        return _preview_response(service.preview(project_id))
    except ProjectRequestMaterialCollectionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectRequestMaterialCollectionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/collect", response_model=RequestMaterialCollectResponse)
def collect_request_material(
    project_id: str,
    service: ProjectRequestMaterialCollectionService = Depends(
        get_project_request_material_collection_service
    ),
) -> RequestMaterialCollectResponse:
    """Collect request material into the Official project folder."""
    try:
        return _collect_response(service.collect(project_id))
    except ProjectRequestMaterialCollectionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectRequestMaterialCollectionConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProjectRequestMaterialCollectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _preview_response(preview: RequestMaterialPreview) -> RequestMaterialPreviewResponse:
    """Convert a preview dataclass into a response DTO."""
    return RequestMaterialPreviewResponse(
        project_id=preview.project_id,
        local_workspace_path=_path(preview.local_workspace_path),
        source_book_path=_path(preview.source_book_path),
        official_project_folder_path=_path(preview.official_project_folder_path),
        status=preview.status,
        items=[_item_response(item) for item in preview.items],
        blockers=list(preview.blockers),
        warnings=list(preview.warnings),
    )


def _collect_response(result: RequestMaterialCollectResult) -> RequestMaterialCollectResponse:
    """Convert a collect result into a response DTO."""
    preview = _preview_response(result)
    return RequestMaterialCollectResponse(
        **preview.model_dump(),
        collection_id=result.collection_id,
        copied_paths=[str(path) for path in result.copied_paths],
        already_present_paths=[str(path) for path in result.already_present_paths],
        skipped_paths=[str(path) for path in result.skipped_paths],
        missing_source_paths=[str(path) for path in result.missing_source_paths],
        conflict_paths=[str(path) for path in result.conflict_paths],
    )


def _item_response(item: RequestMaterialPreviewItem) -> RequestMaterialPreviewItemResponse:
    """Convert a preview item into a response DTO."""
    return RequestMaterialPreviewItemResponse(
        source_asset_id=item.source_asset_id,
        source_asset_type=item.source_asset_type,
        source_role=item.source_role,
        source_name=item.source_name,
        source_path=str(item.source_path),
        dedupe_key=item.dedupe_key,
        target_area=item.target_area,
        target_path=str(item.target_path),
        action=item.action,
        status=item.status,
        message=item.message,
        review_required=item.review_required,
        size_bytes=item.size_bytes,
        sha256=item.sha256,
    )


def _path(path: Path | None) -> str | None:
    """Return a path string or None."""
    return str(path) if path is not None else None
