"""API routes for approval package preview and placement."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.api.dependencies import (
    get_approval_package_service,
    get_project_output_record_service,
)
from backend.application.approval_package_service import (
    ApprovalPackageCommand,
    ApprovalPackageConflictError,
    ApprovalPackageError,
    ApprovalPackageNotFoundError,
    ApprovalPackageResult,
    ApprovalPackageService,
)
from backend.application.project_output_record_service import (
    ProjectOutputRecordService,
    RegisterProjectOutputCommand,
)
from backend.application.project_lifecycle_service import (
    ProjectLifecycleError,
    ProjectLifecycleNotFoundError,
)
from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus


router = APIRouter(prefix="/api/projects/{project_id}/approval-package", tags=["approval-package"])


class ApprovalPackageRequest(BaseModel):
    """Shared request body for approval package preview and execute."""

    project_folder_path: str = Field(min_length=1)
    completed_application_form_path: str = Field(min_length=1)
    test_record_output_path: str = Field(min_length=1)
    fee_evaluation_output_path: str | None = None
    evidence_source_paths: list[str] = Field(default_factory=list)
    overwrite: bool = False


class ApprovalPackageItemResponse(BaseModel):
    """One approval package item response entry."""

    source_path: str
    target_relative_path: str
    target_path: str
    classification: str
    status: str
    warnings: list[str]


class ApprovalPackageResponse(BaseModel):
    """Approval package preview or execution response."""

    project_id: str
    project_folder_path: str
    mode: str
    items: list[ApprovalPackageItemResponse]
    warnings: list[str]
    blockers: list[str]


@router.post("/preview", response_model=ApprovalPackageResponse)
def preview_approval_package(
    project_id: str,
    request: ApprovalPackageRequest,
    service: ApprovalPackageService = Depends(get_approval_package_service),
) -> ApprovalPackageResponse:
    """Preview approval package placement without copying files."""
    try:
        result = service.preview(_command(project_id, request))
    except (
        ApprovalPackageNotFoundError,
        ProjectLifecycleNotFoundError,
    ) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (
        ApprovalPackageError,
        ProjectLifecycleError,
    ) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _response(result)


@router.post("/execute", response_model=ApprovalPackageResponse, status_code=status.HTTP_201_CREATED)
def execute_approval_package(
    project_id: str,
    request: ApprovalPackageRequest,
    service: ApprovalPackageService = Depends(get_approval_package_service),
    output_service: ProjectOutputRecordService = Depends(get_project_output_record_service),
) -> ApprovalPackageResponse:
    """Execute approval package placement by copying files."""
    try:
        result = service.execute(_command(project_id, request))
    except (
        ApprovalPackageNotFoundError,
        ProjectLifecycleNotFoundError,
    ) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ApprovalPackageConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (
        ApprovalPackageError,
        ProjectLifecycleError,
    ) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _register_approval_package_outputs(project_id, output_service, result)
    return _response(result)


def _register_approval_package_outputs(
    project_id: str,
    output_service: ProjectOutputRecordService,
    result: ApprovalPackageResult,
) -> None:
    active_draft_id = output_service.get_status_summary(project_id).active_draft_id
    item_map = {
        "application_form": ProjectOutputKind.SECTION2_WRITE_BACK,
        "test_record": ProjectOutputKind.TEST_RECORD_FORM,
        "fee_evaluation": ProjectOutputKind.FEE_EVALUATION,
    }
    for item in result.items:
        kind = item_map.get(item.classification)
        if kind is None:
            continue
        status = (
            ProjectOutputStatus.CURRENT
            if item.status in {"copied", "already_in_place"}
            else ProjectOutputStatus.FAILED
        )
        if status is ProjectOutputStatus.CURRENT and active_draft_id is None:
            status = ProjectOutputStatus.MANUAL
        output_service.register_output(
            RegisterProjectOutputCommand(
                project_id=project_id,
                output_kind=kind,
                status=status,
                source=ProjectOutputSource.SYSTEM_EXECUTED,
                output_path=str(item.target_path),
                draft_id=active_draft_id if status is ProjectOutputStatus.CURRENT else None,
                note="; ".join(item.warnings) if item.warnings else None,
            )
        )
    approval_status = ProjectOutputStatus.CURRENT if not result.blockers else ProjectOutputStatus.FAILED
    if approval_status is ProjectOutputStatus.CURRENT and active_draft_id is None:
        approval_status = ProjectOutputStatus.MANUAL
    output_service.register_output(
        RegisterProjectOutputCommand(
            project_id=project_id,
            output_kind=ProjectOutputKind.APPROVAL_PACKAGE,
            status=approval_status,
            source=ProjectOutputSource.SYSTEM_EXECUTED,
            output_path=str(result.project_folder_path),
            draft_id=active_draft_id if approval_status is ProjectOutputStatus.CURRENT else None,
            note="; ".join(result.blockers) if result.blockers else None,
        )
    )


def _command(project_id: str, request: ApprovalPackageRequest) -> ApprovalPackageCommand:
    """Convert request model to service command."""
    return ApprovalPackageCommand(
        project_id=project_id,
        project_folder_path=Path(request.project_folder_path),
        completed_application_form_path=Path(request.completed_application_form_path),
        test_record_output_path=Path(request.test_record_output_path),
        fee_evaluation_output_path=(
            Path(request.fee_evaluation_output_path)
            if request.fee_evaluation_output_path is not None
            else None
        ),
        evidence_source_paths=tuple(Path(path) for path in request.evidence_source_paths),
        overwrite=request.overwrite,
    )


def _response(result: ApprovalPackageResult) -> ApprovalPackageResponse:
    """Convert service result to API response."""
    return ApprovalPackageResponse(
        project_id=result.project_id,
        project_folder_path=str(result.project_folder_path),
        mode=result.mode,
        items=[
            ApprovalPackageItemResponse(
                source_path=str(item.source_path),
                target_relative_path=str(item.target_relative_path),
                target_path=str(item.target_path),
                classification=item.classification,
                status=item.status,
                warnings=list(item.warnings),
            )
            for item in result.items
        ],
        warnings=list(result.warnings),
        blockers=list(result.blockers),
    )
