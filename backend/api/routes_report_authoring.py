"""Report Workspace preparation and copy downloads, never an official publish route."""
from dataclasses import asdict
import logging
from urllib.parse import quote
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from backend.api.dependencies import get_report_authoring_service
from backend.api.project_folder_write_guard import require_project_folder_write_slot
from backend.api.report_authoring_schemas import MappingRequest, SelectBaseRequest, ResultImportRequest, FactUpdateRequest, ResultUpdateRequest
from backend.domain.report_authoring import ReportAuthoringConflict
from backend.api.report_authoring_schemas import PhotoUpdateRequest
from backend.api.report_authoring_schemas import CustomerCopyRequest, CustomerCheckRequest


router = APIRouter(prefix="/api/projects/{project_id}/report-workspace/authoring")
logger = logging.getLogger(__name__)


def _state(service, project_id):
    state, context = service.state(project_id)
    payload = asdict(state)
    payload["context"] = context
    payload['applied_result_ids'] = service.active_result_ids(state)
    for source in payload["sources"]:
        source["download_url"] = f"/api/projects/{quote(project_id, safe='')}/report-workspace/authoring/sources/{source['source_id']}/download"
    for output in (*payload["outputs"], *payload["customer_outputs"]):
        output["file_name"] = output["artifact"]["file_name"]
        output["download_url"] = f"/api/projects/{quote(project_id, safe='')}/report-workspace/authoring/outputs/{output['output_id']}/download"
    return payload


def _error(exc):
    if isinstance(exc, LookupError):
        return HTTPException(404, "Report evidence is not available in this project.")
    if isinstance(exc, ReportAuthoringConflict):
        return HTTPException(409, str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(422, str(exc))
    logger.exception("Report evidence storage failed")
    return HTTPException(503, "Report evidence cannot be read or saved. Check storage access and retry.")


@router.get("")
def state(project_id: str, service=Depends(get_report_authoring_service)):
    try:
        return _state(service, project_id)
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.post("/sources", dependencies=[Depends(require_project_folder_write_slot)])
def upload_source(project_id: str, role: str = Form(...), expected_revision: int = Form(ge=0),
                        file: UploadFile = File(...), service=Depends(get_report_authoring_service)):
    content = file.file.read(50 * 1024 * 1024 + 1)
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(413, "Report evidence exceeds the 50 MB limit.")
    try:
        service.add_source(project_id, role=role, file_name=file.filename or "", content=content, expected_revision=expected_revision)
        return _state(service, project_id)
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.post("/mappings", dependencies=[Depends(require_project_folder_write_slot)])
def save_mapping(project_id: str, request: MappingRequest, service=Depends(get_report_authoring_service)):
    try:
        values = request.model_dump()
        values["sample_ids"] = tuple(values["sample_ids"])
        service.save_mapping(project_id, **values)
        return _state(service, project_id)
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.get("/sources/{source_id}/download")
def download_source(project_id: str, source_id: str, service=Depends(get_report_authoring_service)):
    try:
        source, content = service.source_content(project_id, source_id)
        return Response(content, media_type="application/octet-stream", headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(source.file_name, safe='')}",
            "X-Content-Type-Options": "nosniff"})
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.post("/base", dependencies=[Depends(require_project_folder_write_slot)])
def select_base(project_id: str, request: SelectBaseRequest, service=Depends(get_report_authoring_service)):
    try:
        service.select_base(project_id, request.source_id, request.expected_revision)
        return _state(service, project_id)
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.get("/outputs/{output_id}/download")
def download_output(project_id: str, output_id: str, service=Depends(get_report_authoring_service)):
    try:
        artifact, content = service.output_content(project_id, output_id)
        return Response(content, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(artifact.file_name, safe='')}",
                     "X-Content-Type-Options": "nosniff"})
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.get("/sources/{source_id}/table")
def source_table(project_id: str, source_id: str, sheet_name: str = "", service=Depends(get_report_authoring_service)):
    try:
        return asdict(service.source_table(project_id, source_id, sheet_name))
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.post("/results/preview")
def preview_result(project_id: str, request: ResultImportRequest, service=Depends(get_report_authoring_service)):
    try:
        return service.preview_result(project_id, request.model_dump())
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.post("/results/confirm", dependencies=[Depends(require_project_folder_write_slot)])
def confirm_result(project_id: str, request: ResultImportRequest, service=Depends(get_report_authoring_service)):
    try:
        service.confirm_result(project_id, request.model_dump())
        return _state(service, project_id)
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.post("/facts/preview")
def preview_facts(project_id: str, request: FactUpdateRequest, service=Depends(get_report_authoring_service)):
    try:
        return service.preview_facts(project_id, request.model_dump())
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.post("/facts/apply", dependencies=[Depends(require_project_folder_write_slot)])
def apply_facts(project_id: str, request: FactUpdateRequest, service=Depends(get_report_authoring_service)):
    try:
        service.apply_facts(project_id, request.model_dump())
        return _state(service, project_id)
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.get('/outputs/{output_id}/result-targets/{result_id}')
def result_targets(project_id: str, output_id: str, result_id: str, expected_revision: int,
                   service=Depends(get_report_authoring_service)):
    try:
        return service.result_targets(project_id, output_id, result_id, expected_revision)
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.post('/results/apply', dependencies=[Depends(require_project_folder_write_slot)])
def apply_result(project_id: str, request: ResultUpdateRequest, service=Depends(get_report_authoring_service)):
    try:
        service.apply_result(project_id, request.model_dump())
        return _state(service, project_id)
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.get('/outputs/{output_id}/photos')
def photo_slots(project_id: str, output_id: str, expected_revision: int, service=Depends(get_report_authoring_service)):
    try:
        return service.photo_slots(project_id, output_id, expected_revision)
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.get('/outputs/{output_id}/photos/{slot_id}')
def photo_content(project_id: str, output_id: str, slot_id: str, service=Depends(get_report_authoring_service)):
    try:
        content, mime = service.photo_content(project_id, output_id, slot_id)
        return Response(content, media_type=mime, headers={'X-Content-Type-Options': 'nosniff'})
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.post('/photos/apply', dependencies=[Depends(require_project_folder_write_slot)])
def apply_photos(project_id: str, request: PhotoUpdateRequest, service=Depends(get_report_authoring_service)):
    try:
        service.apply_photos(project_id, request.model_dump())
        return _state(service, project_id)
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.post('/customer/generate', dependencies=[Depends(require_project_folder_write_slot)])
def generate_customer(project_id: str, request: CustomerCopyRequest, service=Depends(get_report_authoring_service)):
    try:
        service.generate_customer(project_id, request.model_dump())
        return _state(service, project_id)
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.post('/customer/check', dependencies=[Depends(require_project_folder_write_slot)])
def check_customer(project_id: str, request: CustomerCheckRequest, service=Depends(get_report_authoring_service)):
    try:
        service.customer_check(project_id, request.model_dump())
        return _state(service, project_id)
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc


@router.get('/customer/{output_id}/part')
def customer_part(project_id: str, output_id: str, part: str, service=Depends(get_report_authoring_service)):
    try:
        content = service.customer_part(project_id, output_id, part)
        return Response(content, media_type='application/octet-stream', headers={
            'Content-Disposition': f"attachment; filename*=UTF-8''{quote(part.rsplit('/', 1)[-1], safe='')}",
            'X-Content-Type-Options': 'nosniff'})
    except (LookupError, ValueError, OSError) as exc:
        raise _error(exc) from exc
