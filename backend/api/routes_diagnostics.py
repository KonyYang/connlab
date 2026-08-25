"""Local support diagnostics endpoints."""

from __future__ import annotations

import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.application.support_diagnostic_bundle_service import (
    SupportDiagnosticBundleService,
)


router = APIRouter(prefix="/api/support", tags=["support-diagnostics"])
_logger = logging.getLogger("connlab.frontend")


class FrontendErrorReport(BaseModel):
    kind: Literal["window_error", "unhandled_rejection"]
    message: str = Field(min_length=1, max_length=2000)
    stack: str | None = Field(default=None, max_length=8000)
    page_path: str | None = Field(default=None, max_length=500)


@router.post("/frontend-errors", status_code=204)
def report_frontend_error(report: FrontendErrorReport) -> Response:
    """Record a bounded browser error without accepting arbitrary structured data."""
    _logger.error(
        "frontend_error kind=%s page=%s message=%s stack=%s",
        report.kind,
        _safe_page_path(report.page_path),
        _single_line(report.message),
        _single_line(report.stack or "unavailable"),
    )
    return Response(status_code=204)


@router.get("/diagnostics")
def export_support_diagnostics() -> StreamingResponse:
    """Download a privacy-bounded ZIP suitable for offline support."""
    logs_dir = Path(os.getenv("CONNLAB_LOGS_DIR", "logs"))
    manifest_value = os.getenv("CONNLAB_RELEASE_MANIFEST_PATH")
    service = SupportDiagnosticBundleService(
        logs_dir=logs_dir,
        release_manifest_path=Path(manifest_value) if manifest_value else None,
    )
    bundle = service.build_bundle()
    return StreamingResponse(
        BytesIO(bundle.content),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{bundle.filename}"',
            "Cache-Control": "no-store",
        },
    )


def _single_line(value: str) -> str:
    return " ".join(value.splitlines())


def _safe_page_path(value: str | None) -> str:
    return _single_line(value or "unknown").split("?", 1)[0]
