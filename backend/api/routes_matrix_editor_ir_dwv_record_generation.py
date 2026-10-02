"""Controlled IR/DWV current-state download and safe official publication."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from backend.api.dependencies import get_matrix_editor_ir_dwv_record_generation_service, get_matrix_editor_ir_dwv_record_publication_service
from backend.api.project_folder_write_guard import require_project_folder_write_slot
from backend.api.routes_matrix_editor_llcr_cr_record_generation import MatrixEditorLlcrCrRecordDraftRequest, _draft_command
from backend.application.confirmed_matrix_llcr_cr_record_generation_service import PreviewMatrixEditorLlcrCrPublicationCommand, PublishMatrixEditorLlcrCrPublicationCommand

router = APIRouter(tags=["matrix-editor-ir-dwv-record-generation"])


class IrDwvDraftRequest(MatrixEditorLlcrCrRecordDraftRequest):
    record_type: Literal["ir_dwv"]


class IrDwvDownloadRequest(IrDwvDraftRequest):
    preview_token: str


class IrDwvPublishRequest(IrDwvDownloadRequest):
    conflict_action: Literal["none", "archive"]


@router.post("/api/projects/{project_id}/matrix-editor/ir-dwv-record-draft/generate")
def download(project_id: str, request: IrDwvDownloadRequest,
             service=Depends(get_matrix_editor_ir_dwv_record_generation_service),
             publication=Depends(get_matrix_editor_ir_dwv_record_publication_service)):
    try:
        draft = _draft_command(project_id, request)
        publication.validate_download(PreviewMatrixEditorLlcrCrPublicationCommand(draft, request.matrix_has_pending_changes), request.preview_token)
        result = service.generate(draft)
    except (ValueError, OSError) as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    return FileResponse(result.output_path, filename=result.file_name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.post("/api/projects/{project_id}/matrix-editor/ir-dwv-record-publication/preview")
def preview(project_id: str, request: IrDwvDraftRequest, service=Depends(get_matrix_editor_ir_dwv_record_publication_service)):
    try:
        result = service.preview(PreviewMatrixEditorLlcrCrPublicationCommand(_draft_command(project_id, request), request.matrix_has_pending_changes))
    except (ValueError, OSError) as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    return {"project_id": result.project_id, "mode": result.mode, "status": result.status,
            "authority_status": result.authority_status, "target_path": str(result.target_path) if result.target_path else None,
            "existing_file": result.existing_file, "blockers": result.blockers, "information": result.information,
            "preview_token": result.preview_token}


@router.post("/api/projects/{project_id}/matrix-editor/ir-dwv-record-publication/publish", dependencies=[Depends(require_project_folder_write_slot)])
def publish(project_id: str, request: IrDwvPublishRequest, service=Depends(get_matrix_editor_ir_dwv_record_publication_service)):
    try:
        result = service.publish_under_folder_write_slot(PublishMatrixEditorLlcrCrPublicationCommand(
            _draft_command(project_id, request), request.preview_token, request.conflict_action, request.matrix_has_pending_changes))
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(409, detail=f"IR/DWV file operation failed: {exc}. The previous form is not overwritten automatically. Retry the reviewed action for recovery or inspect History/Test results.") from exc
    return {"project_id": result.project_id, "file_name": result.file_name, "target_path": str(result.target_path),
            "archive_path": str(result.archive_path) if result.archive_path else None}
