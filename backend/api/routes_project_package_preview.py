"""Project package readiness preview API route."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_project_package_preview_service
from backend.application.project_package_preview_service import (
    ProjectPackageAuthorityContext,
    ProjectPackageFolderPreview,
    ProjectPackagePreview,
    ProjectPackagePreviewItem,
    ProjectPackagePreviewProjectNotFoundError,
    ProjectPackagePreviewService,
)


router = APIRouter(tags=["project-package-preview"])

PackagePreviewStatusResponse = Literal["ready", "blocked"]
PackagePreviewItemStatusResponse = Literal["ready", "blocked", "warning", "deferred"]
PackagePreviewMatrixSourceResponse = Literal["confirmed", "draft", "missing"]


class ProjectPackageFolderPreviewResponse(BaseModel):
    """Project folder state for package preview."""

    status: PackagePreviewItemStatusResponse
    path: str | None
    message: str


class ProjectPackageAuthorityContextResponse(BaseModel):
    """Authority context used by package preview."""

    confirmed_matrix_id: str | None
    confirmed_revision: int | None
    matrix_source: PackagePreviewMatrixSourceResponse
    project_matrix_draft_id: str | None
    confirmed_fee_id: str | None
    confirmed_fee_revision: int | None
    confirmed_fee_status: str


class ProjectPackagePreviewItemResponse(BaseModel):
    """One required or optional package preview item."""

    key: str
    label: str
    status: PackagePreviewItemStatusResponse
    target_folder: str | None
    target_path: str | None
    message: str


class ProjectPackagePreviewResponse(BaseModel):
    """Read-only package readiness preview response."""

    project_id: str
    status: PackagePreviewStatusResponse
    project_folder: ProjectPackageFolderPreviewResponse
    authority_context: ProjectPackageAuthorityContextResponse
    required_items: list[ProjectPackagePreviewItemResponse]
    optional_items: list[ProjectPackagePreviewItemResponse]
    blockers: list[str]
    warnings: list[str]


@router.get(
    "/api/projects/{project_id}/project-package/preview",
    response_model=ProjectPackagePreviewResponse,
)
def get_project_package_preview(
    project_id: str,
    service: ProjectPackagePreviewService = Depends(get_project_package_preview_service),
) -> ProjectPackagePreviewResponse:
    """Return read-only package readiness preview for one project."""
    try:
        return _to_response(service.preview(project_id))
    except ProjectPackagePreviewProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _to_response(result: ProjectPackagePreview) -> ProjectPackagePreviewResponse:
    return ProjectPackagePreviewResponse(
        project_id=result.project_id,
        status=result.status,
        project_folder=_folder_response(result.project_folder),
        authority_context=_authority_response(result.authority_context),
        required_items=[_item_response(item) for item in result.required_items],
        optional_items=[_item_response(item) for item in result.optional_items],
        blockers=list(result.blockers),
        warnings=list(result.warnings),
    )


def _folder_response(
    folder: ProjectPackageFolderPreview,
) -> ProjectPackageFolderPreviewResponse:
    return ProjectPackageFolderPreviewResponse(
        status=folder.status,
        path=folder.path,
        message=folder.message,
    )


def _authority_response(
    authority: ProjectPackageAuthorityContext,
) -> ProjectPackageAuthorityContextResponse:
    return ProjectPackageAuthorityContextResponse(
        confirmed_matrix_id=authority.confirmed_matrix_id,
        confirmed_revision=authority.confirmed_revision,
        matrix_source=authority.matrix_source,
        project_matrix_draft_id=authority.project_matrix_draft_id,
        confirmed_fee_id=authority.confirmed_fee_id,
        confirmed_fee_revision=authority.confirmed_fee_revision,
        confirmed_fee_status=authority.confirmed_fee_status,
    )


def _item_response(item: ProjectPackagePreviewItem) -> ProjectPackagePreviewItemResponse:
    return ProjectPackagePreviewItemResponse(
        key=item.key,
        label=item.label,
        status=item.status,
        target_folder=item.target_folder,
        target_path=item.target_path,
        message=item.message,
    )
