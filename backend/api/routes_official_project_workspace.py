"""Official project workspace API routes."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.api.project_folder_write_guard import require_project_folder_write_slot
from backend.api.dependencies import (
    get_official_project_workspace_service, get_official_folder_relocation_service,
)
from backend.application.official_folder_relocation_service import (
    OfficialFolderRelocationPreview, OfficialFolderRelocationService,
)
from backend.application.project_lifecycle_write_guard import ProjectLifecycleReadonlyError
from backend.application.official_project_workspace_service import (
    OfficialWorkspaceConflictOption,
    OfficialProjectWorkspaceService,
    OfficialWorkspaceCreateError,
    OfficialWorkspaceCreateResult,
    OfficialWorkspaceError,
    OfficialWorkspaceNotFoundError,
    OfficialWorkspacePreview,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/official-workspace",
    tags=["official-workspace"],
)


class OfficialWorkspacePreviewResponse(BaseModel):
    """Preview response for local official project workspace creation."""

    project_id: str
    dl_number: str | None
    local_workspace_root: str | None
    local_workspace_path: str | None
    source_book_path: str | None
    template_path: str | None
    official_project_folder_path: str | None
    manifest_path: str | None
    template_root_mode: str | None
    status: str
    blockers: list[str]
    warnings: list[str]
    planned_paths: list[str]
    conflict_paths: list[str]
    conflict_options: list["OfficialWorkspaceConflictOptionResponse"]


class OfficialWorkspaceConflictOptionResponse(BaseModel):
    """Operator choice for an existing local project folder conflict."""

    key: str
    label: str
    description: str


class OfficialWorkspaceCreateRequest(BaseModel):
    """Create request for resolving local project folder conflicts."""

    conflict_strategy: Literal["backup_and_recreate"] | None = None


class OfficialWorkspaceCreateResponse(BaseModel):
    """Create response for local official project workspace creation."""

    workspace_id: str
    project_id: str
    dl_number: str
    local_workspace_path: str
    source_book_path: str
    official_project_folder_path: str
    manifest_path: str
    template_source_path: str
    created_paths: list[str]
    warnings: list[str]
    created_at: str


class OfficialFolderRelocationOptionResponse(BaseModel):
    key: str
    label: str
    description: str


class OfficialFolderRelocationPreviewResponse(BaseModel):
    status: Literal[
        "not_needed", "rename_available", "manual_relink_available", "blocked", "interrupted"
    ]
    current_path: str | None
    suggested_path: str | None
    candidate_path: str | None
    blockers: list[str]
    warnings: list[str]
    expected_context: str | None
    actions: list[OfficialFolderRelocationOptionResponse]


class OfficialFolderRelocationRequest(BaseModel):
    action: Literal[
        "rename_to_confirmed", "keep_current_name", "rebind_and_rename", "rebind_keep_custom", "resume"
    ]
    expected_context: str


@router.get("/preview", response_model=OfficialWorkspacePreviewResponse)
def preview_official_workspace(
    project_id: str,
    service: OfficialProjectWorkspaceService = Depends(get_official_project_workspace_service),
) -> OfficialWorkspacePreviewResponse:
    """Preview local official project workspace creation."""
    try:
        return _preview_response(service.preview(project_id))
    except OfficialWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OfficialWorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/create",
    response_model=OfficialWorkspaceCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_project_folder_write_slot)],
)
def create_official_workspace(
    project_id: str,
    request: OfficialWorkspaceCreateRequest | None = None,
    service: OfficialProjectWorkspaceService = Depends(get_official_project_workspace_service),
) -> OfficialWorkspaceCreateResponse:
    """Create or continue a local official project workspace."""
    try:
        return _create_response(
            service.create(
                project_id,
                conflict_strategy=request.conflict_strategy if request else None,
            )
        )
    except OfficialWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectLifecycleReadonlyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except OfficialWorkspaceCreateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except OfficialWorkspaceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/adopt",
    response_model=OfficialWorkspaceCreateResponse,
    dependencies=[Depends(require_project_folder_write_slot)],
)
def adopt_official_workspace(
    project_id: str,
    service: OfficialProjectWorkspaceService = Depends(get_official_project_workspace_service),
) -> OfficialWorkspaceCreateResponse:
    """Link a verified existing workspace without generating or moving business files."""
    try:
        return _create_response(service.adopt_existing(project_id))
    except OfficialWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProjectLifecycleReadonlyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except OfficialWorkspaceCreateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except OfficialWorkspaceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/relocation/preview", response_model=OfficialFolderRelocationPreviewResponse)
def preview_official_folder_relocation(
    project_id: str,
    service: OfficialFolderRelocationService = Depends(get_official_folder_relocation_service),
) -> OfficialFolderRelocationPreviewResponse:
    try:
        preview = service.preview(project_id)
    except OfficialWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (OfficialWorkspaceError, OSError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _relocation_preview_response(preview)


@router.post(
    "/relocation", response_model=OfficialWorkspaceCreateResponse,
    dependencies=[Depends(require_project_folder_write_slot)],
)
def relocate_official_folder(
    project_id: str, request: OfficialFolderRelocationRequest,
    service: OfficialFolderRelocationService = Depends(get_official_folder_relocation_service),
) -> OfficialWorkspaceCreateResponse:
    try:
        return _create_response(service.apply(project_id, request.action, request.expected_context))
    except OfficialWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (OfficialWorkspaceError, OSError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def _preview_response(preview: OfficialWorkspacePreview) -> OfficialWorkspacePreviewResponse:
    """Convert preview dataclass into a Pydantic response."""
    return OfficialWorkspacePreviewResponse(
        project_id=preview.project_id,
        dl_number=preview.dl_number,
        local_workspace_root=_path(preview.local_workspace_root),
        local_workspace_path=_path(preview.local_workspace_path),
        source_book_path=_path(preview.source_book_path),
        template_path=_path(preview.template_path),
        official_project_folder_path=_path(preview.official_folder_path),
        manifest_path=_path(preview.manifest_path),
        template_root_mode=preview.template_root_mode,
        status=preview.status,
        blockers=list(preview.blockers),
        warnings=list(preview.warnings),
        planned_paths=[str(path) for path in preview.planned_paths],
        conflict_paths=[str(path) for path in preview.conflict_paths],
        conflict_options=[
            _conflict_option_response(option)
            for option in preview.conflict_options
        ],
    )


def _relocation_preview_response(
    preview: OfficialFolderRelocationPreview,
) -> OfficialFolderRelocationPreviewResponse:
    return OfficialFolderRelocationPreviewResponse(
        status=preview.status,
        current_path=_path(preview.current_path),
        suggested_path=_path(preview.suggested_path),
        candidate_path=_path(preview.candidate_path),
        blockers=list(preview.blockers), warnings=list(preview.warnings),
        expected_context=preview.expected_context,
        actions=[OfficialFolderRelocationOptionResponse(
            key=option.key, label=option.label, description=option.description,
        ) for option in preview.actions],
    )


def _create_response(result: OfficialWorkspaceCreateResult) -> OfficialWorkspaceCreateResponse:
    """Convert create result into a Pydantic response."""
    record = result.record
    return OfficialWorkspaceCreateResponse(
        workspace_id=record.workspace_id,
        project_id=record.project_id,
        dl_number=record.dl_number,
        local_workspace_path=str(record.local_workspace_path),
        source_book_path=str(record.source_book_path),
        official_project_folder_path=str(record.official_folder_path),
        manifest_path=str(record.manifest_path),
        template_source_path=str(record.template_source_path),
        created_paths=[str(path) for path in result.created_paths],
        warnings=list(result.warnings),
        created_at=record.created_at,
    )


def _path(path: Path | None) -> str | None:
    """Return a string path or None."""
    return str(path) if path is not None else None


def _conflict_option_response(
    option: OfficialWorkspaceConflictOption,
) -> OfficialWorkspaceConflictOptionResponse:
    """Convert a conflict option to the API response model."""
    return OfficialWorkspaceConflictOptionResponse(
        key=option.key,
        label=option.label,
        description=option.description,
    )
