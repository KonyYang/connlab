"""Project-independent file tools for safe local downloads."""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from backend.api.dependencies import (
    get_settings,
    get_test_report_template_resource_store,
    get_tools_customer_report_job_service,
    get_tools_service,
    get_tools_equipment_report_service,
)
from backend.application.tools_customer_report_job_service import (
    ToolsCustomerReportJobService,
)
from backend.application.test_report_template_resource import (
    TestReportTemplateResourceError,
    resolve_customer_report_template_path,
)
from backend.application.tools_service import ToolsError, ToolsService
from backend.application.tools_equipment_report_service import ToolsEquipmentReportService
from backend.shared.config import Settings


router = APIRouter(prefix="/api/tools", tags=["tools"])


class CustomerReportJobResponse(BaseModel):
    operation_id: str
    status: Literal["queued", "running", "completed", "failed"]
    stage: str
    elapsed_seconds: float
    message: str | None


@router.post(
    "/customer-report/jobs",
    response_model=CustomerReportJobResponse,
    status_code=202,
)
def start_customer_report_job(
    file: UploadFile = File(...),
    jobs: ToolsCustomerReportJobService = Depends(
        get_tools_customer_report_job_service
    ),
    settings: Settings = Depends(get_settings),
    template_store=Depends(get_test_report_template_resource_store),
) -> dict[str, object]:
    """Upload one source and return before slow Word automation starts."""
    root = Path(tempfile.mkdtemp(prefix="tools-customer-report-", dir=settings.data_dir))
    source = root / _safe_upload_name(file.filename, fallback="Internal Report.docx")
    output = root / _customer_report_name(source.name)
    try:
        _save_upload(file, source)
        template = resolve_customer_report_template_path(template_store)
        return jobs.start(
            root=root,
            source_path=source,
            template_path=template,
            output_path=output,
        )
    except (TestReportTemplateResourceError, ToolsError, ValueError) as exc:
        shutil.rmtree(root, ignore_errors=True)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise


@router.get(
    "/customer-report/jobs/{operation_id}",
    response_model=CustomerReportJobResponse,
)
def read_customer_report_job(
    operation_id: str,
    jobs: ToolsCustomerReportJobService = Depends(
        get_tools_customer_report_job_service
    ),
) -> dict[str, object]:
    try:
        return jobs.read(operation_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/customer-report/jobs/{operation_id}/download")
def download_customer_report_job(
    operation_id: str,
    jobs: ToolsCustomerReportJobService = Depends(
        get_tools_customer_report_job_service
    ),
) -> FileResponse:
    try:
        output = jobs.output_path(operation_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return FileResponse(
        output,
        filename=output.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        background=BackgroundTask(jobs.complete_download, operation_id),
    )


@router.post("/customer-report")
def convert_customer_report(
    file: UploadFile = File(...),
    service: ToolsService = Depends(get_tools_service),
    settings: Settings = Depends(get_settings),
    template_store=Depends(get_test_report_template_resource_store),
) -> FileResponse:
    """Convert one uploaded compatible Internal Report without changing its source."""
    root = Path(tempfile.mkdtemp(prefix="tools-customer-report-", dir=settings.data_dir))
    source = root / _safe_upload_name(file.filename, fallback="Internal Report.docx")
    output = root / _customer_report_name(source.name)
    try:
        _save_upload(file, source)
        template = resolve_customer_report_template_path(template_store)
        result = service.generate_customer_report(
            source_path=source,
            template_path=template,
            output_path=output,
        )
    except (TestReportTemplateResourceError, ToolsError, ValueError) as exc:
        shutil.rmtree(root, ignore_errors=True)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise
    return FileResponse(
        result,
        filename=result.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        background=BackgroundTask(shutil.rmtree, root, ignore_errors=True),
    )


@router.post("/encrypt-copy")
def encrypt_copy(
    file: UploadFile = File(...),
    service: ToolsService = Depends(get_tools_service),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    """Encrypt one uploaded Office file into a new ``_Secured`` copy."""
    root = Path(tempfile.mkdtemp(prefix="tools-encrypt-copy-", dir=settings.data_dir))
    source = root / _safe_upload_name(file.filename, fallback="document.docx")
    output = root / _secured_copy_name(source.name)
    try:
        _save_upload(file, source)
        result = service.encrypt_copy(source_path=source, output_path=output)
    except (ToolsError, ValueError) as exc:
        shutil.rmtree(root, ignore_errors=True)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise
    return FileResponse(
        result,
        filename=result.name,
        media_type="application/octet-stream",
        background=BackgroundTask(shutil.rmtree, root, ignore_errors=True),
    )


@router.post("/equipment-list")
def update_equipment_list(
    file: UploadFile = File(...),
    equipment_file: UploadFile | None = File(default=None),
    references_text: str | None = Form(default=None),
    service: ToolsEquipmentReportService = Depends(get_tools_equipment_report_service),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    """Update a downloaded copy; uploads cannot address project or server paths."""
    root = Path(tempfile.mkdtemp(prefix="tools-equipment-list-", dir=settings.data_dir))
    source = root / "report" / _safe_upload_name(file.filename, fallback="Internal Report.docx")
    output = root / "output" / f"{source.stem}_EquipmentUpdated.docx"
    equipment = None
    try:
        _save_upload(file, source)
        if equipment_file is not None:
            equipment = root / "selection" / _safe_upload_name(equipment_file.filename, fallback="EquipmentID.docx")
            _save_upload(equipment_file, equipment)
        result = service.update(source_path=source, output_path=output,
                                equipment_path=equipment, references_text=references_text)
        review = _equipment_review_header(result.statistics)
    except (LookupError, OSError, RuntimeError, ValueError) as exc:
        shutil.rmtree(root, ignore_errors=True)
        detail = str(exc) if isinstance(exc, ValueError) else (
            "The report could not be updated. Check the selected documents and calibration workbook in Settings."
        )
        raise HTTPException(status_code=422, detail=detail) from exc
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise
    return FileResponse(
        result.output_path, filename=output.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"X-Equipment-Review": review,
                 "Access-Control-Expose-Headers": "Content-Disposition, X-Equipment-Review"},
        background=BackgroundTask(shutil.rmtree, root, ignore_errors=True),
    )


def _equipment_review_header(statistics: dict[str, object]) -> str:
    # Keep HTTP headers bounded even for a large selection; never silently hide issues.
    review = {**statistics, "omitted": {key: 0 for key in ("unmatched", "incomplete", "expired")}}
    review.update({key: list(statistics[key]) for key in review["omitted"]})
    while True:
        encoded = json.dumps(review, ensure_ascii=True, separators=(",", ":"))
        if len(encoded) <= 7000:
            return encoded
        key = max(review["omitted"], key=lambda category: len(json.dumps(review[category])))
        review[key].pop()
        review["omitted"][key] += 1


def _save_upload(file: UploadFile, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as stream:
        shutil.copyfileobj(file.file, stream)


def _safe_upload_name(name: str | None, *, fallback: str) -> str:
    candidate = Path(name or fallback).name
    candidate = re.sub(r"[^A-Za-z0-9._ -]+", "_", candidate).strip(" .")
    return candidate or fallback


def _customer_report_name(source_name: str) -> str:
    source = Path(source_name)
    stem = source.stem
    first, separator, remainder = stem.partition(" ")
    if not first.casefold().endswith("-cr"):
        first = f"{first}-CR"
    return f"{first}{separator}{remainder}{source.suffix}"


def _secured_copy_name(source_name: str) -> str:
    source = Path(source_name)
    return f"{source.stem}_Secured{source.suffix}"
