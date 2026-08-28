"""Matrix-Editor-current-state Test Record preview generation API route."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.api.dependencies import (
    get_matrix_editor_test_record_document_generation_service,
    get_matrix_editor_test_record_publication_service,
    get_settings,
    get_test_record_template_resource_store,
)
from backend.api.lifecycle_errors import lifecycle_readonly_conflict
from backend.application.matrix_editor_test_record_document_generation_service import (
    GenerateMatrixEditorTestRecordDocumentCommand,
    MatrixEditorTestRecordDocumentGenerationError,
    MatrixEditorTestRecordDocumentGenerationNotFoundError,
    MatrixEditorTestRecordDocumentGenerationService,
    MatrixEditorTestRecordGroupInput,
    MatrixEditorTestRecordRowInput,
)
from backend.application.matrix_editor_test_record_authority import (
    build_matrix_editor_test_record_signature,
)
from backend.application.matrix_editor_test_record_publication_service import (
    ExecuteMatrixEditorTestRecordPublicationCommand,
    MatrixEditorTestRecordPublicationBlockedError,
    MatrixEditorTestRecordPublicationConflictError,
    MatrixEditorTestRecordPublicationError,
    MatrixEditorTestRecordPublicationService,
    PreviewMatrixEditorTestRecordPublicationCommand,
)
from backend.application.project_lifecycle_write_guard import (
    ProjectLifecycleReadonlyError,
)
from backend.application.test_record_template_resource import (
    TestRecordTemplateResourceError,
    TestRecordTemplateResourceStore,
    resolve_test_record_template_path,
)
from backend.shared.config import Settings
from backend.infrastructure.files.test_record_publication_gateway import (
    TestRecordPublicationTargetChangedError,
)


router = APIRouter(tags=["matrix-editor-test-record-generation"])


class MatrixEditorTestRecordGroupRequest(BaseModel):
    """Current Matrix Editor group payload for preview generation."""

    group_key: str = Field(min_length=1)
    group_label: str = Field(min_length=1)
    sample_quantity_expression: str = ""


class MatrixEditorTestRecordRowRequest(BaseModel):
    """Current Matrix Editor row payload for preview generation."""

    test_item: str = ""
    section: str = ""
    method: str = ""
    condition: str = ""
    requirement: str = ""
    is_sample_row: bool = False
    group_values: dict[str, str] = Field(default_factory=dict)


class MatrixEditorTestRecordDraftRequest(BaseModel):
    """Current Matrix Editor state payload for preview-only Test Record output."""

    source: str = "matrix_editor_current_ui_state"
    groups: list[MatrixEditorTestRecordGroupRequest]
    rows: list[MatrixEditorTestRecordRowRequest]


class MatrixEditorTestRecordPublicationExecuteRequest(
    MatrixEditorTestRecordDraftRequest
):
    """Explicit direct publication after a matching preview."""

    preview_token: str = Field(min_length=1)
    conflict_action: str = Field(pattern="^(none|archive|recycle)$")


class MatrixEditorTestRecordPublicationPreviewResponse(BaseModel):
    project_id: str
    mode: str
    status: str
    target_path: str | None
    existing_file: bool
    existing_modified_at: str | None
    blockers: list[str]
    preview_token: str


class MatrixEditorTestRecordPublicationResultResponse(BaseModel):
    project_id: str
    target_path: str
    archive_path: str | None
    file_name: str


@router.post(
    "/api/projects/{project_id}/matrix-editor/test-record-publication/preview",
    response_model=MatrixEditorTestRecordPublicationPreviewResponse,
)
def preview_matrix_editor_test_record_publication(
    project_id: str,
    request: MatrixEditorTestRecordDraftRequest,
    service: MatrixEditorTestRecordPublicationService = Depends(
        get_matrix_editor_test_record_publication_service
    ),
) -> MatrixEditorTestRecordPublicationPreviewResponse:
    """Route the current draft to download or a previewed official-folder write."""
    _require_current_ui_source(request.source)
    preview = service.preview(
        PreviewMatrixEditorTestRecordPublicationCommand(
            project_id=project_id,
            draft_signature=_draft_signature(request),
        )
    )
    return MatrixEditorTestRecordPublicationPreviewResponse(
        project_id=preview.project_id,
        mode=preview.mode,
        status=preview.status,
        target_path=str(preview.target_path) if preview.target_path else None,
        existing_file=preview.existing_file,
        existing_modified_at=preview.existing_modified_at,
        blockers=list(preview.blockers),
        preview_token=preview.preview_token,
    )


@router.post(
    "/api/projects/{project_id}/matrix-editor/test-record-publication/publish",
    response_model=MatrixEditorTestRecordPublicationResultResponse,
)
def publish_matrix_editor_test_record(
    project_id: str,
    request: MatrixEditorTestRecordPublicationExecuteRequest,
    service: MatrixEditorTestRecordPublicationService = Depends(
        get_matrix_editor_test_record_publication_service
    ),
    settings: Settings = Depends(get_settings),
    template_resource_store: TestRecordTemplateResourceStore = Depends(
        get_test_record_template_resource_store
    ),
) -> MatrixEditorTestRecordPublicationResultResponse:
    """Publish after validating the preview token and explicit conflict action."""
    _require_current_ui_source(request.source)
    template_path = _resolve_template(settings, template_resource_store)
    draft_request = MatrixEditorTestRecordDraftRequest.model_validate(
        request.model_dump(include={"source", "groups", "rows"})
    )
    try:
        result = service.execute(
            ExecuteMatrixEditorTestRecordPublicationCommand(
                project_id=project_id,
                draft_signature=_draft_signature(draft_request),
                preview_token=request.preview_token,
                conflict_action=request.conflict_action,
                staging_dir=settings.data_dir / "generated_test_record_publications",
                template_path=template_path,
                groups=_group_inputs(request),
                rows=_row_inputs(request),
            )
        )
    except ProjectLifecycleReadonlyError as exc:
        raise lifecycle_readonly_conflict(exc) from exc
    except MatrixEditorTestRecordPublicationBlockedError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except (
        MatrixEditorTestRecordPublicationConflictError,
        TestRecordPublicationTargetChangedError,
    ) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (
        MatrixEditorTestRecordPublicationError,
        MatrixEditorTestRecordDocumentGenerationError,
        OSError,
        RuntimeError,
    ) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return MatrixEditorTestRecordPublicationResultResponse(
        project_id=result.project_id,
        target_path=str(result.target_path),
        archive_path=str(result.archive_path) if result.archive_path else None,
        file_name=result.file_name,
    )


@router.post("/api/projects/{project_id}/matrix-editor/test-record-draft/generate")
def generate_matrix_editor_test_record_draft_preview(
    project_id: str,
    request: MatrixEditorTestRecordDraftRequest,
    service: MatrixEditorTestRecordDocumentGenerationService = Depends(
        get_matrix_editor_test_record_document_generation_service
    ),
    settings: Settings = Depends(get_settings),
    template_resource_store: TestRecordTemplateResourceStore = Depends(
        get_test_record_template_resource_store
    ),
) -> FileResponse:
    """Generate and return one preview Test Record from current Matrix Editor state."""
    if request.source != "matrix_editor_current_ui_state":
        raise HTTPException(
            status_code=422,
            detail="Matrix Editor Test Record preview requires current UI state payload.",
        )
    try:
        template_path = resolve_test_record_template_path(
            template_resource_store,
            configured_template_path=settings.test_record.template_path,
        )
    except TestRecordTemplateResourceError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    try:
        result = service.generate(
            GenerateMatrixEditorTestRecordDocumentCommand(
                project_id=project_id,
                output_dir=settings.data_dir / "generated_test_record_previews",
                template_path=template_path,
                groups=tuple(
                    MatrixEditorTestRecordGroupInput(
                        group_key=group.group_key,
                        group_label=group.group_label,
                        sample_quantity_expression=group.sample_quantity_expression,
                    )
                    for group in request.groups
                ),
                rows=tuple(
                    MatrixEditorTestRecordRowInput(
                        test_item=row.test_item,
                        section=row.section,
                        method=row.method,
                        condition=row.condition,
                        requirement=row.requirement,
                        is_sample_row=row.is_sample_row,
                        group_values=row.group_values,
                    )
                    for row in request.rows
                ),
            )
        )
    except MatrixEditorTestRecordDocumentGenerationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MatrixEditorTestRecordDocumentGenerationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return FileResponse(
        path=result.output_path,
        filename=result.file_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


def _require_current_ui_source(source: str) -> None:
    if source != "matrix_editor_current_ui_state":
        raise HTTPException(
            status_code=422,
            detail="Matrix Editor Test Record preview requires current UI state payload.",
        )


def _resolve_template(
    settings: Settings,
    template_resource_store: TestRecordTemplateResourceStore,
):
    try:
        return resolve_test_record_template_path(
            template_resource_store,
            configured_template_path=settings.test_record.template_path,
        )
    except TestRecordTemplateResourceError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _draft_signature(request: MatrixEditorTestRecordDraftRequest) -> str:
    return build_matrix_editor_test_record_signature(
        groups=request.groups,
        rows=request.rows,
    )


def _group_inputs(
    request: MatrixEditorTestRecordDraftRequest,
) -> tuple[MatrixEditorTestRecordGroupInput, ...]:
    return tuple(
        MatrixEditorTestRecordGroupInput(
            group_key=group.group_key,
            group_label=group.group_label,
            sample_quantity_expression=group.sample_quantity_expression,
        )
        for group in request.groups
    )


def _row_inputs(
    request: MatrixEditorTestRecordDraftRequest,
) -> tuple[MatrixEditorTestRecordRowInput, ...]:
    return tuple(
        MatrixEditorTestRecordRowInput(
            test_item=row.test_item,
            section=row.section,
            method=row.method,
            condition=row.condition,
            requirement=row.requirement,
            is_sample_row=row.is_sample_row,
            group_values=row.group_values,
        )
        for row in request.rows
    )
