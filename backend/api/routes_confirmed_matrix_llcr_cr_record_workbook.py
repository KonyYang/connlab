"""Preview, generate, and download routes for specialized LLCR/CR workbooks."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

from backend.api.dependencies import (
    get_llcr_cr_record_workbook_artifact_store,
    get_llcr_cr_record_workbook_generation_service,
    get_llcr_cr_record_workbook_preview_service,
)
from backend.application.confirmed_matrix_llcr_cr_record_generation_service import (
    GenerateLlcrCrRecordWorkbookCommand,
    LlcrCrRecordWorkbookGenerationError,
    LlcrCrRecordWorkbookGenerationResult,
    LlcrCrRecordWorkbookGenerationService,
)
from backend.application.confirmed_matrix_llcr_cr_record_preview_service import (
    LlcrCrRecordWorkbookPreviewNotFoundError,
    LlcrCrRecordWorkbookPreviewService,
)
from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordDiagnostic,
    LlcrCrRecordProjection,
    LlcrCrRecordSection,
)
from backend.infrastructure.files.llcr_cr_specialized_record_artifact_store import (
    LlcrCrSpecializedRecordArtifactStore,
)

_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

router = APIRouter(tags=["confirmed-matrix-llcr-cr-record-workbook"])


class LlcrCrRecordWorkbookGenerateRequest(BaseModel):
    preview_fingerprint: str
    record_type: Literal["llcr", "cr"] = "llcr"

    @field_validator("preview_fingerprint")
    @classmethod
    def _require_fingerprint(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Preview fingerprint is required.")
        return normalized


class LlcrCrRecordDiagnosticResponse(BaseModel):
    code: str
    severity: str
    message: str
    confirmed_group_id: str | None
    confirmed_row_id: str | None
    step_sequence: int | None
    family_id: str | None
    normalized_prefix: str | None
    first_family_id: str | None
    first_family_label: str | None
    second_family_id: str | None
    second_family_label: str | None


class LlcrCrRecordRowResponse(BaseModel):
    sample_index: int
    contact_id: str
    contact_label: str


class LlcrCrRecordSectionResponse(BaseModel):
    record_type: Literal["llcr", "cr"]
    confirmed_group_id: str
    confirmed_row_id: str
    step_sequence: int
    step_suffix_note: str
    group_label: str
    source_step: str
    sample_count: int
    readings_per_sample: int
    rows: list[LlcrCrRecordRowResponse]
    category_id: str | None = None
    category_label: str | None = None
    point_expression: str | None = None
    record_prefix: str | None = None
    stages: list["LlcrCrRecordStageResponse"] = Field(default_factory=list)


class LlcrCrRecordStageResponse(BaseModel):
    label: str
    source_step: str
    confirmed_row_id: str
    test_item: str
    condition: str
    requirement: str
    test_current_ampere: str | None = None


class LlcrCrRecordWorkbookPreviewResponse(BaseModel):
    project_id: str
    status: str
    confirmed_matrix_id: str
    confirmed_revision: int
    preview_fingerprint: str | None
    row_count: int
    sections: list[LlcrCrRecordSectionResponse]
    diagnostics: list[LlcrCrRecordDiagnosticResponse]
    record_type: Literal["llcr", "cr"]
    point_profile_revision_id: str | None = None
    point_profile_revision_sequence: int | None = None
    delta_r_enabled: bool = False


class LlcrCrRecordWorkbookGenerateResponse(BaseModel):
    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    artifact_id: str
    file_name: str
    download_url: str
    record_type: Literal["llcr", "cr"]


@router.post(
    "/api/projects/{project_id}/confirmed-matrix/llcr-cr-record-workbook/preview",
    response_model=LlcrCrRecordWorkbookPreviewResponse,
)
def preview_llcr_cr_record_workbook(
    project_id: str,
    record_type: Literal["llcr", "cr"] = "llcr",
    service: LlcrCrRecordWorkbookPreviewService = Depends(
        get_llcr_cr_record_workbook_preview_service
    ),
) -> LlcrCrRecordWorkbookPreviewResponse:
    """Return a typed no-write projection from active confirmed contact authority."""
    try:
        projection = service.preview(project_id, record_type)
    except LlcrCrRecordWorkbookPreviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _preview_response(projection)


@router.post(
    "/api/projects/{project_id}/confirmed-matrix/llcr-cr-record-workbook/generate",
    response_model=LlcrCrRecordWorkbookGenerateResponse,
)
def generate_llcr_cr_record_workbook(
    project_id: str,
    request: LlcrCrRecordWorkbookGenerateRequest = Body(...),
    service: LlcrCrRecordWorkbookGenerationService = Depends(
        get_llcr_cr_record_workbook_generation_service
    ),
) -> LlcrCrRecordWorkbookGenerateResponse:
    """Generate only from the matching current no-write preview fingerprint."""
    try:
        result = service.generate(
            GenerateLlcrCrRecordWorkbookCommand(
                project_id=project_id,
                preview_fingerprint=request.preview_fingerprint,
                record_type=request.record_type,
            )
        )
    except LlcrCrRecordWorkbookGenerationError as exc:
        status_code = 409 if "changed" in str(exc).lower() else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return _generate_response(result)


@router.get(
    "/api/projects/{project_id}/confirmed-matrix/llcr-cr-record-workbook/files/{artifact_id}"
)
def download_llcr_cr_record_workbook(
    project_id: str,
    artifact_id: str,
    artifact_store: LlcrCrSpecializedRecordArtifactStore = Depends(
        get_llcr_cr_record_workbook_artifact_store
    ),
) -> FileResponse:
    """Serve one strictly contained generated specialized workbook."""
    try:
        artifact = artifact_store.resolve(project_id=project_id, artifact_id=artifact_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return FileResponse(
        path=artifact.output_path,
        filename=artifact.file_name,
        media_type=_XLSX_MEDIA_TYPE,
    )


def _preview_response(projection: LlcrCrRecordProjection) -> LlcrCrRecordWorkbookPreviewResponse:
    return LlcrCrRecordWorkbookPreviewResponse(
        project_id=projection.project_id,
        status=projection.status,
        confirmed_matrix_id=projection.confirmed_matrix_id,
        confirmed_revision=projection.confirmed_revision,
        preview_fingerprint=projection.preview_fingerprint,
        row_count=projection.row_count,
        sections=[_section_response(section) for section in projection.sections],
        diagnostics=[_diagnostic_response(item) for item in projection.diagnostics],
        record_type=projection.record_type or "llcr",
        point_profile_revision_id=projection.point_profile_revision_id,
        point_profile_revision_sequence=projection.point_profile_revision_sequence,
        delta_r_enabled=projection.delta_r_enabled,
    )


def _section_response(section: LlcrCrRecordSection) -> LlcrCrRecordSectionResponse:
    return LlcrCrRecordSectionResponse(
        record_type=section.record_type,
        confirmed_group_id=section.confirmed_group_id,
        confirmed_row_id=section.confirmed_row_id,
        step_sequence=section.step_sequence,
        step_suffix_note=section.step_suffix_note,
        group_label=section.group_label,
        source_step=section.source_step,
        sample_count=section.sample_count,
        readings_per_sample=section.readings_per_sample,
        rows=[
            LlcrCrRecordRowResponse(
                sample_index=row.sample_index,
                contact_id=row.contact_id,
                contact_label=row.contact_label,
            )
            for row in section.rows
        ],
        category_id=section.category_id,
        category_label=section.category_label,
        point_expression=section.point_expression,
        record_prefix=section.record_prefix,
        stages=[
            LlcrCrRecordStageResponse(
                label=stage.label,
                source_step=stage.source_step,
                confirmed_row_id=stage.confirmed_row_id,
                test_item=stage.test_item,
                condition=stage.condition,
                requirement=stage.requirement,
                test_current_ampere=stage.test_current_ampere,
            )
            for stage in section.stages
        ],
    )


def _diagnostic_response(item: LlcrCrRecordDiagnostic) -> LlcrCrRecordDiagnosticResponse:
    return LlcrCrRecordDiagnosticResponse(
        code=item.code,
        severity=item.severity,
        message=item.message,
        confirmed_group_id=item.confirmed_group_id,
        confirmed_row_id=item.confirmed_row_id,
        step_sequence=item.step_sequence,
        family_id=item.family_id,
        normalized_prefix=item.normalized_prefix,
        first_family_id=item.first_family_id,
        first_family_label=item.first_family_label,
        second_family_id=item.second_family_id,
        second_family_label=item.second_family_label,
    )


def _generate_response(
    result: LlcrCrRecordWorkbookGenerationResult,
) -> LlcrCrRecordWorkbookGenerateResponse:
    return LlcrCrRecordWorkbookGenerateResponse(
        project_id=result.project_id,
        confirmed_matrix_id=result.confirmed_matrix_id,
        confirmed_revision=result.confirmed_revision,
        artifact_id=result.artifact_id,
        file_name=result.file_name,
        download_url=(
            f"/api/projects/{result.project_id}/confirmed-matrix/llcr-cr-record-workbook/"
            f"files/{result.artifact_id}"
        ),
        record_type=result.record_type,
    )
