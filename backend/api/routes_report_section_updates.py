"""Report-section copy downloads never use client-supplied filesystem paths."""
from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from pathlib import Path
import tempfile
import logging
from typing import Literal

from backend.api.dependencies import get_report_section_update_service
from backend.api.project_folder_write_guard import require_project_folder_write_slot
from backend.application.current_report_update_service import CurrentReportFileConflictError


router = APIRouter(prefix="/api/projects/{project_id}/report-workspace/update-source")
logger = logging.getLogger(__name__)


def _update_error(project_id, exc):
    logger.warning("Internal Report draft update failed for project %s", project_id, exc_info=True)
    detail = str(exc) if isinstance(exc, ValueError) else "The report could not be updated. Close it in Word and retry."
    return HTTPException(409, detail)


def _download_url(project_id, revision):
    from urllib.parse import quote
    return f"/api/projects/{quote(project_id, safe='')}/report-workspace/update-source/download/{revision}"


@router.get("")
def source(project_id: str, service=Depends(get_report_section_update_service)):
    try:
        result = service.source(project_id)
        return {"status": result.status, "mode": result.mode, "file_name": result.file_name,
                "file_sha256": result.file_sha256, "report_revision_id": None,
                "draft_revision_id": result.report_revision_id if result.mode == "download_draft" else None,
                "folder_path": None, "official_folder_path": None, "can_publish_to_official": False,
                "download_url": _download_url(project_id, result.report_revision_id)
                    if result.mode == "download_draft" and result.report_revision_id else None}
    except (ValueError, OSError) as exc:
        raise HTTPException(409, "The report source cannot be read. Select the Internal Report again.") from exc


class LlcrUpdate(BaseModel):
    dataset_id: str
    expected_report_sha256: str = Field(min_length=64, max_length=64)
    expected_mode: Literal["official", "download_draft"] = "download_draft"


@router.post("/select", dependencies=[Depends(require_project_folder_write_slot)])
async def select_source(project_id: str, file: UploadFile = File(...), expected_report_sha256: str | None = Form(default=None),
                        service=Depends(get_report_section_update_service)):
    if not (file.filename or "").casefold().endswith(".docx"):
        raise HTTPException(422, "Choose an Internal Report .docx file.")
    content = await file.read(30 * 1024 * 1024 + 1)
    if len(content) > 30 * 1024 * 1024:
        raise HTTPException(413, "The Internal Report exceeds the 30 MB limit.")
    try:
        with tempfile.TemporaryDirectory(prefix="connlab-report-source-") as directory:
            path = Path(directory) / "selected.docx"
            path.write_bytes(content)
            result = await run_in_threadpool(service.select_source, project_id, path, expected_report_sha256)
            return _result(project_id, result)
    except (ValueError, OSError, RuntimeError) as exc:
        raise _update_error(project_id, exc) from exc


def _result(project_id, result):
    if result.get("draft_revision_id"):
        result["download_url"] = _download_url(project_id, result["draft_revision_id"])
    if result.get("archive_path"):
        result["archive_path"] = str(result["archive_path"])
    return result


@router.post("/llcr", dependencies=[Depends(require_project_folder_write_slot)])
def update_llcr(project_id: str, request: LlcrUpdate, service=Depends(get_report_section_update_service)):
    try:
        return _result(project_id, service.update_llcr(project_id, request.dataset_id, request.expected_report_sha256, request.expected_mode))
    except (ValueError, OSError, RuntimeError, CurrentReportFileConflictError) as exc:
        raise _update_error(project_id, exc) from exc


@router.post("/equipment", dependencies=[Depends(require_project_folder_write_slot)])
async def update_equipment(project_id: str, expected_report_sha256: str = Form(min_length=64, max_length=64),
                           expected_mode: Literal["official", "download_draft"] = Form("download_draft"),
                           file: UploadFile | None = File(default=None), references_text: str | None = Form(default=None),
                           service=Depends(get_report_section_update_service)):
    content = None
    if file is not None:
        if not (file.filename or "").casefold().endswith(".docx"):
            raise HTTPException(422, "Choose an EquipmentID .docx document.")
        content = await file.read(20 * 1024 * 1024 + 1)
        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(413, "Equipment selection exceeds the 20 MB limit.")
    if references_text is not None and len(references_text) > 100000:
        raise HTTPException(413, "Equipment ID text is too long.")
    try:
        result = await run_in_threadpool(service.update_equipment, project_id, expected_report_sha256,
                                        expected_mode=expected_mode, content=content, references_text=references_text)
        return _result(project_id, result)
    except (ValueError, OSError, RuntimeError, CurrentReportFileConflictError) as exc:
        raise _update_error(project_id, exc) from exc


@router.get("/download/{revision}")
def download(project_id: str, revision: str, service=Depends(get_report_section_update_service)):
    try:
        result = service.download(project_id, revision)
    except (KeyError, ValueError, OSError) as exc:
        raise HTTPException(410, "The draft download is unavailable. Select the report and update again.") from exc
    return FileResponse(result.file_path, filename=result.file_name,
                        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
