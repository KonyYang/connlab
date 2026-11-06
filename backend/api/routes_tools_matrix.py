"""Standalone planning endpoints never establish project authority."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from urllib.parse import quote
from backend.application.tools_matrix_planning import prepare_planning_matrix
from backend.api.routes_matrix_editor_live_xlsx_export import LiveXlsxExportRequest, _to_application_request, MEDIA_TYPE
from backend.api.dependencies_matrix_editor_live_xlsx_export import get_matrix_editor_live_xlsx_export_service
from fastapi import UploadFile
from backend.api.matrix_editor_session_dtos import MatrixEditorSessionDraftSaveRequest
from backend.api.routes_confirmed_matrix_fee_draft import _to_response
from backend.application.tools_matrix_planning import evaluate_planning_fees
from backend.api.confirmed_matrix_fee_evaluation_export_dtos import ConfirmedMatrixFeeEvaluationEditedFileRequest
from backend.api.dependencies import get_fee_evaluation_template_resource_store
from backend.application.fee_evaluation_template_resource import resolve_fee_evaluation_template_path
from backend.application.tools_fee_export_service import ToolsFeeExportService
from backend.infrastructure.office.tools_fee_download_gateway import ToolsFeeDownloadGateway
from backend.infrastructure.office.fee_form_import_gateway import read_fee_form, MAX_FILE_BYTES
from backend.api.dependencies import get_matrix_method_version_sync_service
from backend.api.routes_matrix_method_version_sync import MatrixMethodVersionSuggestionRequest, suggest_matrix_method_versions
from dataclasses import asdict
from backend.api.dependencies import get_session, get_project_registry_summary_service, get_matrix_editor_session_service
from backend.api.routes_matrix_editor_session import get_matrix_editor_session_seed
from backend.infrastructure.storage.repositories.fee_evaluation_pricing_draft_edit import FeeEvaluationPricingDraftEditRepository
from backend.infrastructure.storage.repositories.confirmed_matrix_authority import ConfirmedMatrixAuthorityRepository
from backend.application.tools_legacy_recovery import recover_pricing

router=APIRouter(prefix='/api/tools/matrix', tags=['tools-matrix'])
class ImportRequest(BaseModel):
    preview_payload: dict

@router.post('/prepare')
def prepare(request: ImportRequest):
    try:
        from backend.api.routes_matrix_import_commit import _to_draft_response
        result = prepare_planning_matrix(request.preview_payload)
        result['project_matrix_draft'] = _to_draft_response(result['project_matrix_draft'])
        return result
    except (ValueError, KeyError) as exc: raise HTTPException(422, str(exc)) from exc

@router.post('/export')
def export(request: LiveXlsxExportRequest, service=Depends(get_matrix_editor_live_xlsx_export_service)):
    try: result=service.export(_to_application_request(request))
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    return Response(result.content,media_type=MEDIA_TYPE,headers={'Content-Disposition':f"attachment; filename*=UTF-8''{quote(result.file_name)}"})




@router.post('/fees')
def fees(request: MatrixEditorSessionDraftSaveRequest):
    try:
        return _to_response(evaluate_planning_fees(request.model_dump()))
    except (ValueError, KeyError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/fees/import')
def import_fees(file: UploadFile):
    try:
        return read_fee_form(file.file.read(MAX_FILE_BYTES + 1), file.filename or '')
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    finally:
        file.file.close()


class FeeExportRequest(BaseModel):
    matrix: MatrixEditorSessionDraftSaveRequest
    values: ConfirmedMatrixFeeEvaluationEditedFileRequest


@router.post('/fees/export')
def export_fees(request: FeeExportRequest, resources=Depends(get_fee_evaluation_template_resource_store)):
    try:
        template = resolve_fee_evaluation_template_path(resources)
        name, content = ToolsFeeExportService(ToolsFeeDownloadGateway()).export(
            matrix=request.matrix.model_dump(), template=template, edited_values=request.values.to_application())
        return Response(content, media_type=MEDIA_TYPE,
            headers={'Content-Disposition':f"attachment; filename*=UTF-8''{quote(name)}"})
    except (ValueError, OSError, RuntimeError) as exc:
        raise HTTPException(422, str(exc)) from exc



@router.post('/method-versions')
def method_versions(request: MatrixMethodVersionSuggestionRequest,
                    service=Depends(get_matrix_method_version_sync_service)):
    return suggest_matrix_method_versions('', request, service)



@router.get('/legacy/{project_id}')
def recover_legacy(project_id: str, session=Depends(get_session),
                   registry=Depends(get_project_registry_summary_service),
                   matrix_service=Depends(get_matrix_editor_session_service)):
    identity = registry.get_row(project_id)
    if identity is None or identity.display_project_id_kind != 'temporary':
        raise HTTPException(409, 'Only retained temporary work can be copied into Tools.')
    seed = get_matrix_editor_session_seed(project_id, matrix_service)
    pricing = FeeEvaluationPricingDraftEditRepository(session).get_latest_by_project(project_id)
    original_matrix = ConfirmedMatrixAuthorityRepository(session).get(pricing.confirmed_matrix_id) if pricing else None
    values, skipped = (None, [])
    if seed.editor_draft is not None:
        values, skipped = recover_pricing(seed.editor_draft.model_dump(), pricing, original_matrix)
    return {'seed':seed, 'fee_values':asdict(values) if values else None,
            'unmatched_fee_rows':skipped, 'retained_fee_values':asdict(pricing.edited_values) if pricing else None}
