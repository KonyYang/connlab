"""Public folder workflow API routes for Sync, Submit, and Pull."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_public_folder_workflow_service
from backend.application.public_folder_workflow_service import (
    PublicFolderAutoSyncCommand,
    PublicFolderWorkflowBlockedError,
    PublicFolderWorkflowConflictError,
    PublicFolderWorkflowContext,
    PublicFolderWorkflowError,
    PublicFolderWorkflowExecuteCommand,
    PublicFolderWorkflowItem,
    PublicFolderWorkflowNotFoundError,
    PublicFolderWorkflowPreview,
    PublicFolderWorkflowResult,
    PublicFolderWorkflowService,
    PublicFolderWorkflowState,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/public-folder-workflow",
    tags=["public-folder-workflow"],
)


class PublicFolderWorkflowItemResponse(BaseModel):
    """Response DTO for one preview item."""

    kind: str
    relative_path: str
    local_path: str | None
    public_path: str | None
    action: str
    status: str
    message: str


class PublicFolderWorkflowPreviewResponse(BaseModel):
    """Response DTO for public folder workflow previews."""

    project_id: str
    operation_type: str
    status: str
    local_official_folder_path: str | None
    public_root: str | None
    public_root_class: str | None
    public_folder_year: int | None
    year_source: str | None
    year_evidence: str | None
    public_open_path: str | None
    public_closed_path: str | None
    target_path: str | None
    items: list[PublicFolderWorkflowItemResponse]
    blockers: list[str]
    warnings: list[str]
    conflicts: list[str]
    required_confirmations: list[str]
    counts: dict[str, int]
    preview_hash: str
    next_action: str
    auto_sync_enabled: bool
    sync_locked: bool


class PublicFolderWorkflowContextResponse(BaseModel):
    """Response DTO for public folder workflow context."""

    project_id: str
    auto_sync_enabled: bool
    sync_locked: bool
    submitted_at: str | None
    public_root: str | None
    public_root_class: str | None
    public_folder_year: int | None
    year_source: str | None
    year_evidence: str | None
    local_official_folder_path: str | None
    public_open_path: str | None
    public_closed_path: str | None
    blockers: list[str]
    warnings: list[str]


class PublicFolderWorkflowExecuteRequest(BaseModel):
    """Request DTO for explicit execute operations."""

    preview_hash: str
    confirmed: bool
    confirm_directory_creation: bool = False
    operator: str | None = None


class PublicFolderAutoSyncRequest(BaseModel):
    """Request DTO for persisted auto-sync preference."""

    auto_sync_enabled: bool


class PublicFolderWorkflowStateResponse(BaseModel):
    """Response DTO for persisted workflow state."""

    project_id: str
    auto_sync_enabled: bool
    sync_locked: bool
    submitted_at: str | None
    submit_operation_id: str | None
    last_sync_operation_id: str | None
    last_pull_operation_id: str | None
    created_at: str | None
    updated_at: str | None


class PublicFolderWorkflowResultResponse(BaseModel):
    """Response DTO for execute results."""

    project_id: str
    operation_id: str
    operation_type: str
    status: str
    counts: dict[str, int]
    errors: list[str]
    preview: PublicFolderWorkflowPreviewResponse


@router.get("/context", response_model=PublicFolderWorkflowContextResponse)
def get_public_folder_workflow_context(
    project_id: str,
    service: PublicFolderWorkflowService = Depends(get_public_folder_workflow_service),
) -> PublicFolderWorkflowContextResponse:
    """Return public folder workflow context."""
    try:
        return _context_response(service.context(project_id))
    except PublicFolderWorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PublicFolderWorkflowError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.put("/auto-sync", response_model=PublicFolderWorkflowStateResponse)
def set_public_folder_auto_sync(
    project_id: str,
    request: PublicFolderAutoSyncRequest,
    service: PublicFolderWorkflowService = Depends(get_public_folder_workflow_service),
) -> PublicFolderWorkflowStateResponse:
    """Persist the backend-owned auto-sync preference."""
    try:
        return _state_response(
            service.set_auto_sync(
                project_id,
                PublicFolderAutoSyncCommand(auto_sync_enabled=request.auto_sync_enabled),
            )
        )
    except PublicFolderWorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sync/preview", response_model=PublicFolderWorkflowPreviewResponse)
def preview_sync(
    project_id: str,
    service: PublicFolderWorkflowService = Depends(get_public_folder_workflow_service),
) -> PublicFolderWorkflowPreviewResponse:
    """Return a read-only Sync preview."""
    return _preview_route(lambda: service.preview_sync(project_id))


@router.post("/sync/execute", response_model=PublicFolderWorkflowResultResponse)
def execute_sync(
    project_id: str,
    request: PublicFolderWorkflowExecuteRequest,
    service: PublicFolderWorkflowService = Depends(get_public_folder_workflow_service),
) -> PublicFolderWorkflowResultResponse:
    """Execute Sync after explicit confirmation and preview-hash validation."""
    return _result_route(lambda: service.execute_sync(project_id, _execute_command(request)))


@router.post("/submit/preview", response_model=PublicFolderWorkflowPreviewResponse)
def preview_submit(
    project_id: str,
    service: PublicFolderWorkflowService = Depends(get_public_folder_workflow_service),
) -> PublicFolderWorkflowPreviewResponse:
    """Return a read-only Submit preview."""
    return _preview_route(lambda: service.preview_submit(project_id))


@router.post("/submit/execute", response_model=PublicFolderWorkflowResultResponse)
def execute_submit(
    project_id: str,
    request: PublicFolderWorkflowExecuteRequest,
    service: PublicFolderWorkflowService = Depends(get_public_folder_workflow_service),
) -> PublicFolderWorkflowResultResponse:
    """Execute Submit and persist backend sync lock."""
    return _result_route(lambda: service.execute_submit(project_id, _execute_command(request)))


@router.post("/pull/preview", response_model=PublicFolderWorkflowPreviewResponse)
def preview_pull(
    project_id: str,
    service: PublicFolderWorkflowService = Depends(get_public_folder_workflow_service),
) -> PublicFolderWorkflowPreviewResponse:
    """Return a read-only Pull preview."""
    return _preview_route(lambda: service.preview_pull(project_id))


@router.post("/pull/execute", response_model=PublicFolderWorkflowResultResponse)
def execute_pull(
    project_id: str,
    request: PublicFolderWorkflowExecuteRequest,
    service: PublicFolderWorkflowService = Depends(get_public_folder_workflow_service),
) -> PublicFolderWorkflowResultResponse:
    """Execute Pull to a local history folder."""
    return _result_route(lambda: service.execute_pull(project_id, _execute_command(request)))


def _preview_route(callback) -> PublicFolderWorkflowPreviewResponse:
    try:
        return _preview_response(callback())
    except PublicFolderWorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PublicFolderWorkflowError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def _result_route(callback) -> PublicFolderWorkflowResultResponse:
    try:
        return _result_response(callback())
    except PublicFolderWorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (PublicFolderWorkflowBlockedError, PublicFolderWorkflowConflictError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except PublicFolderWorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _execute_command(request: PublicFolderWorkflowExecuteRequest) -> PublicFolderWorkflowExecuteCommand:
    return PublicFolderWorkflowExecuteCommand(
        preview_hash=request.preview_hash,
        confirmed=request.confirmed,
        confirm_directory_creation=request.confirm_directory_creation,
        operator=request.operator,
    )


def _context_response(context: PublicFolderWorkflowContext) -> PublicFolderWorkflowContextResponse:
    return PublicFolderWorkflowContextResponse(
        project_id=context.project_id,
        auto_sync_enabled=context.auto_sync_enabled,
        sync_locked=context.sync_locked,
        submitted_at=context.submitted_at,
        public_root=_path(context.public_root),
        public_root_class=context.public_root_class,
        public_folder_year=context.public_folder_year,
        year_source=context.year_source,
        year_evidence=context.year_evidence,
        local_official_folder_path=_path(context.local_official_folder_path),
        public_open_path=_path(context.public_open_path),
        public_closed_path=_path(context.public_closed_path),
        blockers=list(context.blockers),
        warnings=list(context.warnings),
    )


def _state_response(state: PublicFolderWorkflowState) -> PublicFolderWorkflowStateResponse:
    return PublicFolderWorkflowStateResponse(
        project_id=state.project_id,
        auto_sync_enabled=state.auto_sync_enabled,
        sync_locked=state.sync_locked,
        submitted_at=state.submitted_at,
        submit_operation_id=state.submit_operation_id,
        last_sync_operation_id=state.last_sync_operation_id,
        last_pull_operation_id=state.last_pull_operation_id,
        created_at=state.created_at,
        updated_at=state.updated_at,
    )


def _result_response(result: PublicFolderWorkflowResult) -> PublicFolderWorkflowResultResponse:
    return PublicFolderWorkflowResultResponse(
        project_id=result.project_id,
        operation_id=result.operation_id,
        operation_type=result.operation_type,
        status=result.status,
        counts=dict(result.counts),
        errors=list(result.errors),
        preview=_preview_response(result.preview),
    )


def _preview_response(preview: PublicFolderWorkflowPreview) -> PublicFolderWorkflowPreviewResponse:
    return PublicFolderWorkflowPreviewResponse(
        project_id=preview.project_id,
        operation_type=preview.operation_type,
        status=preview.status,
        local_official_folder_path=_path(preview.local_official_folder_path),
        public_root=_path(preview.public_root),
        public_root_class=preview.public_root_class,
        public_folder_year=preview.public_folder_year,
        year_source=preview.year_source,
        year_evidence=preview.year_evidence,
        public_open_path=_path(preview.public_open_path),
        public_closed_path=_path(preview.public_closed_path),
        target_path=_path(preview.target_path),
        items=[_item_response(item) for item in preview.items],
        blockers=list(preview.blockers),
        warnings=list(preview.warnings),
        conflicts=list(preview.conflicts),
        required_confirmations=list(preview.required_confirmations),
        counts=dict(preview.counts),
        preview_hash=preview.preview_hash,
        next_action=preview.next_action,
        auto_sync_enabled=preview.auto_sync_enabled,
        sync_locked=preview.sync_locked,
    )


def _item_response(item: PublicFolderWorkflowItem) -> PublicFolderWorkflowItemResponse:
    return PublicFolderWorkflowItemResponse(
        kind=item.kind,
        relative_path=item.relative_path.as_posix(),
        local_path=_path(item.local_path),
        public_path=_path(item.public_path),
        action=item.action,
        status=item.status,
        message=item.message,
    )


def _path(path: Path | None) -> str | None:
    return str(path) if path is not None else None
