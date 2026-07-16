"""Confirmed-Matrix-backed Fee Evaluation workbook export API route."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import FileResponse

from backend.api.dependencies import (
    get_confirmed_matrix_fee_evaluation_export_service,
    get_fee_evaluation_template_resource_store,
    get_settings,
)
from backend.api.fee_evaluation_pricing_draft_http import (
    CurrentFeePricingDraftRequiredError,
    raise_fee_pricing_draft_not_current,
)
from backend.api.confirmed_matrix_fee_evaluation_export_dtos import (
    ConfirmedMatrixFeeEvaluationEditedFileRequest,
    ConfirmedMatrixFeeEvaluationExportRequest,
    ConfirmedMatrixFeeEvaluationExportResponse,
    to_export_response,
)
from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftNotFoundError,
)
from backend.application.confirmed_matrix_fee_evaluation_export_service import (
    ConfirmedMatrixFeeEvaluationExportError,
    ConfirmedMatrixFeeEvaluationExportNotFoundError,
    ConfirmedMatrixFeeEvaluationExportTimeoutError,
    ConfirmedMatrixFeeEvaluationExportUnavailableError,
    ExportConfirmedMatrixFeeEvaluationCommand,
    ExportConfirmedMatrixFeeEvaluationResult,
)
from backend.application.fee_evaluation_template_discovery import (
    FeeEvaluationTemplateDiscoveryError,
)
from backend.application.fee_evaluation_template_resource import (
    FeeEvaluationTemplateResourceError,
    FeeEvaluationTemplateResourceStore,
    resolve_fee_evaluation_template_path,
)
from backend.application.project_output_record_service import (
    ProjectOutputRecordError,
    ProjectOutputRecordNotFoundError,
)
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable
from backend.shared.config import Settings


router = APIRouter(tags=["confirmed-matrix-fee-evaluation-export"])

FEE_FILE_DOWNLOAD_DIR_NAME = "generated_fee_files"
FEE_FILE_MEDIA_TYPE = "application/vnd.ms-excel"


class FeeEvaluationExportServicePort(Protocol):
    """Route dependency contract for Fee Evaluation export services."""

    def export(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> ExportConfirmedMatrixFeeEvaluationResult:
        """Export one Fee Evaluation workbook."""


@router.post(
    "/api/projects/{project_id}/confirmed-matrix/fee-evaluation/export",
    response_model=ConfirmedMatrixFeeEvaluationExportResponse,
)
def export_confirmed_matrix_fee_evaluation(
    project_id: str,
    request: ConfirmedMatrixFeeEvaluationExportRequest,
    service: FeeEvaluationExportServicePort = Depends(
        get_confirmed_matrix_fee_evaluation_export_service
    ),
) -> ConfirmedMatrixFeeEvaluationExportResponse:
    """Generate a Fee Evaluation workbook from active Confirmed Matrix authority."""
    try:
        result = service.export(
            ExportConfirmedMatrixFeeEvaluationCommand(
                project_id=project_id,
                template_path=Path(request.template_path),
                output_dir=Path(request.output_dir) if request.output_dir else None,
                output_file_name=request.output_file_name,
                overwrite=request.overwrite,
                allow_review_required=request.allow_review_required,
                fill_mode=request.fill_mode,
                prepared_by=request.prepared_by,
                approved_by=request.approved_by,
                pricing_draft_edit_id=request.pricing_draft_edit_id,
                pricing_draft_generation=request.pricing_draft_generation,
                pricing_draft_payload_fingerprint=(
                    request.pricing_draft_payload_fingerprint
                ),
                pricing_draft_validation_token=request.pricing_draft_validation_token,
            )
        )
    except (
        ConfirmedMatrixFeeEvaluationExportNotFoundError,
        ConfirmedMatrixFeeDraftNotFoundError,
        ProjectOutputRecordNotFoundError,
    ) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (
        ConfirmedMatrixFeeEvaluationExportUnavailableError,
        OfficeAutomationUnavailable,
    ) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ConfirmedMatrixFeeEvaluationExportTimeoutError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "message": str(exc),
                "elapsed_seconds": exc.elapsed_seconds,
                "manual_cleanup_warning": exc.manual_cleanup_warning,
            },
        ) from exc
    except CurrentFeePricingDraftRequiredError as exc:
        raise_fee_pricing_draft_not_current(exc)
    except (ConfirmedMatrixFeeEvaluationExportError, ProjectOutputRecordError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return to_export_response(result)


@router.post("/api/projects/{project_id}/confirmed-matrix/fee-evaluation/file/generate")
def generate_confirmed_matrix_fee_file(
    project_id: str,
    request: ConfirmedMatrixFeeEvaluationEditedFileRequest | None = Body(default=None),
    service: FeeEvaluationExportServicePort = Depends(
        get_confirmed_matrix_fee_evaluation_export_service
    ),
    settings: Settings = Depends(get_settings),
    template_resource_store: FeeEvaluationTemplateResourceStore = Depends(
        get_fee_evaluation_template_resource_store
    ),
) -> FileResponse:
    """Generate a Matrix basic-fill Fee Evaluation workbook for browser download."""
    output_dir = settings.data_dir / FEE_FILE_DOWNLOAD_DIR_NAME
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        template_path = resolve_fee_evaluation_template_path(template_resource_store)
        result = service.export(
            ExportConfirmedMatrixFeeEvaluationCommand(
                project_id=project_id,
                template_path=template_path,
                output_dir=output_dir,
                output_file_name=None,
                overwrite=True,
                allow_review_required=True,
                fill_mode="matrix_basic",
                edited_values=request.to_application() if request else None,
                pricing_draft_edit_id=(request.pricing_draft_edit_id if request else None),
                pricing_draft_generation=(request.pricing_draft_generation if request else None),
                pricing_draft_payload_fingerprint=(
                    request.pricing_draft_payload_fingerprint if request else None
                ),
                pricing_draft_validation_token=(
                    request.pricing_draft_validation_token if request else None
                ),
            )
        )
    except (
        ConfirmedMatrixFeeEvaluationExportNotFoundError,
        ConfirmedMatrixFeeDraftNotFoundError,
        ProjectOutputRecordNotFoundError,
        FeeEvaluationTemplateDiscoveryError,
        FeeEvaluationTemplateResourceError,
    ) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (
        ConfirmedMatrixFeeEvaluationExportUnavailableError,
        OfficeAutomationUnavailable,
    ) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ConfirmedMatrixFeeEvaluationExportTimeoutError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "message": str(exc),
                "elapsed_seconds": exc.elapsed_seconds,
                "manual_cleanup_warning": exc.manual_cleanup_warning,
            },
        ) from exc
    except CurrentFeePricingDraftRequiredError as exc:
        raise_fee_pricing_draft_not_current(exc)
    except (ConfirmedMatrixFeeEvaluationExportError, ProjectOutputRecordError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    resolved_output_path = _validate_fee_file_download_path(
        result.output_path,
        output_dir,
    )
    return FileResponse(
        path=resolved_output_path,
        filename=resolved_output_path.name,
        media_type=FEE_FILE_MEDIA_TYPE,
    )


def _validate_fee_file_download_path(output_path: Path, output_dir: Path) -> Path:
    resolved_output_dir = output_dir.resolve()
    resolved_output_path = output_path.resolve()
    try:
        resolved_output_path.relative_to(resolved_output_dir)
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail="Invalid generated Fee file path: outside generated_fee_files.",
        ) from exc
    if not resolved_output_path.exists() or not resolved_output_path.is_file():
        raise HTTPException(
            status_code=500,
            detail="Invalid generated Fee file path: file was not created.",
        )
    if resolved_output_path.suffix.lower() != ".xls":
        raise HTTPException(
            status_code=500,
            detail="Invalid generated Fee file path: expected a .xls workbook.",
        )
    return resolved_output_path
