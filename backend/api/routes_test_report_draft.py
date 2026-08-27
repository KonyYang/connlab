"""Downloadable initialization-report draft API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from backend.api.dependencies import (
    get_settings,
    get_test_report_draft_service,
    get_test_report_template_resource_store,
)
from backend.application.test_report_draft_service import (
    GenerateTestReportDraftCommand,
    TestReportDraftGenerationError,
    TestReportDraftNotFoundError,
    TestReportDraftService,
)
from backend.application.test_report_template_resource import (
    TestReportTemplateResourceError,
    TestReportTemplateResourceStore,
    resolve_test_report_template_path,
)
from backend.shared.config import Settings


router = APIRouter(tags=["test-report-draft"])


@router.post("/api/projects/{project_id}/test-report-draft/generate")
def generate_test_report_draft(
    project_id: str,
    service: TestReportDraftService = Depends(get_test_report_draft_service),
    settings: Settings = Depends(get_settings),
    template_resource_store: TestReportTemplateResourceStore = Depends(
        get_test_report_template_resource_store
    ),
) -> FileResponse:
    """Generate and download one new E-3707_H initialization-report draft."""
    try:
        template_path = resolve_test_report_template_path(template_resource_store)
        result = service.generate(
            GenerateTestReportDraftCommand(
                project_id=project_id,
                template_path=template_path,
                output_dir=settings.data_dir / "generated_test_reports",
            )
        )
    except TestReportDraftNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (TestReportTemplateResourceError, TestReportDraftGenerationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return FileResponse(
        path=result.output_path,
        filename=result.file_name,
        media_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        headers={
            "X-ConnLab-Basic-Information-Version": str(
                result.confirmed_basic_information_version
            ),
            "X-ConnLab-Basic-Information-Source-Hash": (
                result.confirmed_basic_information_source_signature_hash
            ),
            "X-ConnLab-Confirmed-Matrix-ID": result.confirmed_matrix_id,
        },
    )
