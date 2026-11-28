"""Choose the content of a separately downloaded customer Word copy."""
from contextlib import nullcontext
from hashlib import file_digest
from pathlib import Path
import shutil
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from pydantic import BaseModel, ConfigDict, Field

from backend.api.dependencies import (get_customer_download_inputs, get_customer_report_choices,
    get_customer_report_source_reader, get_settings, get_session, get_test_report_template_resource_store,
    get_tools_customer_report_job_service)
from backend.api.routes_tools import CustomerReportJobResponse, _customer_report_name
from backend.application.test_report_template_resource import resolve_customer_report_template_path


router = APIRouter(tags=["customer-report"])


class SourceVersion(BaseModel):
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class CustomerChoicesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decisions: dict[str, str] = Field(default_factory=dict, max_length=2048)


def _current(project_id, expected, session, settings):
    source = get_customer_report_source_reader(session, settings).get_current_report(project_id)
    if source.status != "ready" or not source.file_path or source.file_sha256 != expected:
        raise HTTPException(409, "The current internal report changed or is ambiguous. Reload it or select the intended Word file.")
    return source


def _inspect(settings, inputs, choices, scope, name, open_source, expected=None):
    name = Path(name).name
    if Path(name).suffix.lower() != ".docx":
        raise HTTPException(422, "Select the internal report in Word .docx format.")
    # Windows deletes this handle's backing file even on abrupt process exit.
    # Word receives only the separate, prepared file after confirmation.
    source = tempfile.TemporaryFile(dir=settings.data_dir, prefix="cr-input-")
    try:
        with open_source() as original:
            shutil.copyfileobj(original, source)
        source.seek(0)
        if expected:
            if file_digest(source, "sha256").hexdigest() != expected:
                raise HTTPException(409, "The internal report changed during selection. Reload it and try again.")
            source.seek(0)
        return inputs.inspect(source, _customer_report_name(name), choices, scope, settings.data_dir)
    except Exception as exc:
        source.close()
        if isinstance(exc, (ValueError, OSError, RuntimeError)):
            raise HTTPException(422, str(exc)) from exc
        raise


@router.post("/api/tools/customer-report/inspect")
def inspect_upload(file: UploadFile = File(...), inputs=Depends(get_customer_download_inputs),
                   choices=Depends(get_customer_report_choices), settings=Depends(get_settings)):
    return _inspect(settings, inputs, choices, "tools", file.filename or "Internal Report.docx",
                    lambda: nullcontext(file.file))


@router.post("/api/projects/{project_id}/report-workspace/customer-download/inspect")
def inspect_registered(project_id: str, request: SourceVersion, inputs=Depends(get_customer_download_inputs),
                       choices=Depends(get_customer_report_choices), session=Depends(get_session), settings=Depends(get_settings)):
    report = _current(project_id, request.source_sha256, session, settings)
    return _inspect(settings, inputs, choices, "project:" + project_id, report.file_name,
                    lambda: Path(report.file_path).open("rb"), request.source_sha256)


@router.post("/api/tools/customer-report/inputs/{input_id}/generate", response_model=CustomerReportJobResponse, status_code=202)
def generate(input_id: str, request: CustomerChoicesRequest, inputs=Depends(get_customer_download_inputs),
             jobs=Depends(get_tools_customer_report_job_service), resources=Depends(get_test_report_template_resource_store),
             session=Depends(get_session), settings=Depends(get_settings)):
    def revalidate(scope, digest):
        if scope.startswith("project:"):
            _current(scope.removeprefix("project:"), digest, session, settings)

    try:
        return inputs.generate(input_id, request.decisions, resolve_customer_report_template_path(resources), jobs, revalidate)
    except LookupError as exc:
        raise HTTPException(410, str(exc)) from exc
    except (ValueError, OSError, RuntimeError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.delete("/api/tools/customer-report/inputs/{input_id}", status_code=204)
def discard(input_id: str, inputs=Depends(get_customer_download_inputs)):
    inputs.discard(input_id)
    return Response(status_code=204)
