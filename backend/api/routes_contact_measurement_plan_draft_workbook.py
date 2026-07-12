"""Typed preview, generation, and download boundary for draft plan workbooks."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.api.dependencies import (
    get_draft_measurement_plan_workbook_artifact_store,
    get_draft_measurement_plan_workbook_generation_service,
    get_draft_measurement_plan_workbook_preview_service,
)
from backend.application.draft_measurement_plan_workbook_generation_service import (
    DraftMeasurementPlanWorkbookGenerationError,
)
from backend.application.draft_measurement_plan_workbook_preview_service import (
    DraftMeasurementPlanWorkbookPreviewError,
)

router = APIRouter(tags=["contact-measurement-plan-draft-workbook"])
_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class DraftWorkbookGenerateRequest(BaseModel):
    preview_fingerprint: str = Field(min_length=1)


class DraftWorkbookPreviewResponse(BaseModel):
    project_id: str
    revision_id: str | None
    revision_sequence: int | None
    revision_state: str | None
    revision_fingerprint: str | None
    matrix_id: str | None
    matrix_revision: int | None
    matrix_binding_fingerprint: str | None
    status: str
    output_label: str | None
    preview_fingerprint: str | None
    row_count: int
    sections: list[dict[str, object]]
    diagnostics: list[dict[str, str]]
    generate_allowed: bool


class DraftWorkbookArtifactResponse(BaseModel):
    project_id: str
    revision_id: str
    artifact_id: str
    file_name: str
    output_label: str
    download_url: str
    cleanup_warning: str | None = None


@router.post("/api/projects/{project_id}/contact-measurement-plan/revisions/{revision_id}/draft-workbook/preview", response_model=DraftWorkbookPreviewResponse)
def preview(project_id: str, revision_id: str, service=Depends(get_draft_measurement_plan_workbook_preview_service)) -> DraftWorkbookPreviewResponse:
    try:
        return _preview_response(service.preview(project_id, revision_id))
    except DraftMeasurementPlanWorkbookPreviewError as exc:
        raise HTTPException(status_code=409, detail={"code": "draft_workbook_stale", "message": str(exc)}) from exc


@router.post("/api/projects/{project_id}/contact-measurement-plan/revisions/{revision_id}/draft-workbook/generate", response_model=DraftWorkbookArtifactResponse)
def generate(project_id: str, revision_id: str, request: DraftWorkbookGenerateRequest = Body(...), service=Depends(get_draft_measurement_plan_workbook_generation_service)) -> DraftWorkbookArtifactResponse:
    try:
        result = service.generate(project_id, revision_id, request.preview_fingerprint)
    except DraftMeasurementPlanWorkbookGenerationError as exc:
        status = 409 if "preview again" in str(exc).lower() else 422
        raise HTTPException(status_code=status, detail={"code": "draft_workbook_stale" if status == 409 else "draft_workbook_blocked", "message": str(exc)}) from exc
    return _artifact_response(project_id, result.revision_id, result.artifact_id, result.file_name, result.output_label, result.cleanup_warning)


@router.get("/api/projects/{project_id}/contact-measurement-plan/draft-workbook/artifacts/latest", response_model=DraftWorkbookArtifactResponse | None)
def latest(project_id: str, store=Depends(get_draft_measurement_plan_workbook_artifact_store)) -> DraftWorkbookArtifactResponse | None:
    artifact = store.latest(project_id=project_id)
    if artifact is None:
        return None
    return _artifact_response(project_id, str(artifact.metadata.get("revision_id") or ""), artifact.artifact_id, artifact.file_name, str(artifact.metadata.get("output_label") or "DRAFT"))


@router.get("/api/projects/{project_id}/contact-measurement-plan/draft-workbook/files/{artifact_id}")
def download(project_id: str, artifact_id: str, store=Depends(get_draft_measurement_plan_workbook_artifact_store)) -> FileResponse:
    try:
        artifact = store.resolve(project_id=project_id, artifact_id=artifact_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return FileResponse(artifact.output_path, filename=artifact.file_name, media_type=_XLSX)


def _preview_response(projection) -> DraftWorkbookPreviewResponse:
    return DraftWorkbookPreviewResponse(
        **{**asdict(projection), "row_count": projection.row_count, "generate_allowed": projection.generate_allowed,
           "sections": [asdict(item) for item in projection.sections], "diagnostics": [asdict(item) for item in projection.diagnostics]}
    )


def _artifact_response(project_id: str, revision_id: str, artifact_id: str, file_name: str, output_label: str, cleanup_warning: str | None = None) -> DraftWorkbookArtifactResponse:
    return DraftWorkbookArtifactResponse(project_id=project_id, revision_id=revision_id, artifact_id=artifact_id, file_name=file_name, output_label=output_label, cleanup_warning=cleanup_warning, download_url=f"/api/projects/{project_id}/contact-measurement-plan/draft-workbook/files/{artifact_id}")
