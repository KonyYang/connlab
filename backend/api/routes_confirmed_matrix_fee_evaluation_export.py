"""Confirmed-Matrix-backed Fee Evaluation workbook export API route."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Protocol

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator, model_validator

from backend.api.dependencies import (
    get_confirmed_matrix_fee_evaluation_export_service,
    get_settings,
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
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedManualRow,
)
from backend.application.fee_evaluation_template_discovery import (
    FeeEvaluationTemplateDiscoveryError,
    discover_fee_evaluation_template,
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
FEE_EDITED_UNIT_TYPES = {
    "per sample",
    "per reading",
    "per contact",
    "per cycle",
    "per time",
    "per hour",
    "per day",
    "per photo",
    "per report",
    "sample",
    "reading",
    "contact",
    "cycle",
    "time",
    "hour",
    "day",
    "photo",
    "report",
    "group",
    "specimen",
    "pending",
}


class FeeEvaluationExportServicePort(Protocol):
    """Route dependency contract for Fee Evaluation export services."""

    def export(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> ExportConfirmedMatrixFeeEvaluationResult:
        """Export one Fee Evaluation workbook."""


class ConfirmedMatrixFeeEvaluationExportRequest(BaseModel):
    template_path: str
    output_dir: str | None = None
    output_file_name: str | None = None
    overwrite: bool = False
    allow_review_required: bool = False
    fill_mode: Literal["fee_draft", "matrix_basic"] = "fee_draft"
    prepared_by: str | None = None
    approved_by: str | None = None


class ConfirmedMatrixFeeEvaluationExportResponse(BaseModel):
    project_id: str
    output_path: str
    output_format: str
    status: str
    confirmed_matrix_id: str
    confirmed_revision: int
    pricing_rule_version_id: str
    pricing_effective_from: str | None
    prepared_by: str | None
    approved_by: str | None
    output_record_id: str | None
    line_traceability: list["FeeEvaluationExportLineTraceResponse"]
    warnings: list[str]


class FeeEvaluationExportLineTraceResponse(BaseModel):
    line_id: str
    group_key: str
    group_label: str
    confirmed_group_id: str
    confirmed_row_id: str
    source_row_id: str | None
    row_order: int
    matched_rule_id: str | None
    matched_rule_version_id: str | None
    step_tokens: list[str]
    cell_value: str | None = None


class FeeEvaluationEditedRowExportRequest(BaseModel):
    source_line_id: str
    confirmed_group_id: str
    confirmed_row_id: str
    step_token: str = ""
    step_index: int
    spend_time: str
    unit_price: str
    unit_type: str
    units: str
    base_fee: str
    discount: str
    testing_fee: str
    notes: str = ""

    @field_validator(
        "source_line_id",
        "confirmed_group_id",
        "confirmed_row_id",
        "spend_time",
        "unit_price",
        "unit_type",
        "units",
        "base_fee",
        "discount",
        "testing_fee",
        "notes",
        "step_token",
    )
    @classmethod
    def _strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("source_line_id", "confirmed_group_id", "confirmed_row_id")
    @classmethod
    def _require_text(cls, value: str) -> str:
        if not value:
            raise ValueError("Fee Evaluation edited row identity is required.")
        return value

    @field_validator("step_index")
    @classmethod
    def _require_non_negative_step_index(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Fee Evaluation edited row step_index must be non-negative.")
        return value

    @field_validator("unit_type")
    @classmethod
    def _validate_unit_type(cls, value: str) -> str:
        if value.lower() not in FEE_EDITED_UNIT_TYPES:
            raise ValueError(f"Unsupported Fee Evaluation Unit Type: {value}")
        return value

    def to_application(self) -> FeeEvaluationEditedExportRow:
        """Convert this route DTO into an application-layer edited row."""
        return FeeEvaluationEditedExportRow(
            source_line_id=self.source_line_id,
            confirmed_group_id=self.confirmed_group_id,
            confirmed_row_id=self.confirmed_row_id,
            step_token=self.step_token,
            step_index=self.step_index,
            spend_time=self.spend_time,
            unit_price=self.unit_price,
            unit_type=self.unit_type,
            units=self.units,
            base_fee=self.base_fee,
            discount=self.discount,
            testing_fee=self.testing_fee,
            notes=self.notes,
        )


class FeeEvaluationEditedManualRowExportRequest(BaseModel):
    row_kind: str
    confirmed_group_id: str = ""
    group_key: str = ""
    group_label: str = ""
    spend_time: str
    unit_price: str
    unit_type: str
    units: str
    base_fee: str
    discount: str
    testing_fee: str
    notes: str = ""

    @field_validator(
        "row_kind",
        "confirmed_group_id",
        "group_key",
        "group_label",
        "spend_time",
        "unit_price",
        "unit_type",
        "units",
        "base_fee",
        "discount",
        "testing_fee",
        "notes",
    )
    @classmethod
    def _strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("row_kind")
    @classmethod
    def _validate_row_kind(cls, value: str) -> str:
        if value not in {"report_preparation", "sample_preparation"}:
            raise ValueError(f"Unsupported Fee Evaluation manual row: {value}")
        return value

    @field_validator("unit_type")
    @classmethod
    def _validate_unit_type(cls, value: str) -> str:
        if value.lower() not in FEE_EDITED_UNIT_TYPES:
            raise ValueError(f"Unsupported Fee Evaluation Unit Type: {value}")
        return value

    @model_validator(mode="after")
    def _validate_manual_row_identity(self) -> "FeeEvaluationEditedManualRowExportRequest":
        if self.row_kind == "sample_preparation" and not (
            self.confirmed_group_id and self.group_key and self.group_label
        ):
            raise ValueError(
                "Sample preparation manual row requires confirmed_group_id, "
                "group_key, and group_label."
            )
        return self

    def to_application(self) -> FeeEvaluationEditedManualRow:
        """Convert this route DTO into an application-layer manual row."""
        return FeeEvaluationEditedManualRow(
            row_kind=self.row_kind,
            spend_time=self.spend_time,
            unit_price=self.unit_price,
            unit_type=self.unit_type,
            units=self.units,
            base_fee=self.base_fee,
            discount=self.discount,
            testing_fee=self.testing_fee,
            notes=self.notes,
            confirmed_group_id=self.confirmed_group_id,
            group_key=self.group_key,
            group_label=self.group_label,
        )


class FeeEvaluationEditedSummaryExportRequest(BaseModel):
    condition_confirmation_spend_time: str = "0"
    external_cost: str = "0"
    external_cost_note: str = ""
    lab_manpower_hourly_rate: str = "200"

    @field_validator(
        "condition_confirmation_spend_time",
        "external_cost",
        "external_cost_note",
        "lab_manpower_hourly_rate",
    )
    @classmethod
    def _strip_text(cls, value: str) -> str:
        return value.strip()

    def to_application(self) -> FeeEvaluationEditedExportSummary:
        """Convert this route DTO into an application-layer summary."""
        return FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time=self.condition_confirmation_spend_time,
            external_cost=self.external_cost,
            external_cost_note=self.external_cost_note,
            lab_manpower_hourly_rate=self.lab_manpower_hourly_rate,
        )


class ConfirmedMatrixFeeEvaluationEditedFileRequest(BaseModel):
    rows: list[FeeEvaluationEditedRowExportRequest] = []
    summary: FeeEvaluationEditedSummaryExportRequest
    manual_rows: list[FeeEvaluationEditedManualRowExportRequest] = []

    @model_validator(mode="after")
    def _reject_duplicate_identities(self) -> "ConfirmedMatrixFeeEvaluationEditedFileRequest":
        identities = [
            (
                row.source_line_id,
                row.confirmed_group_id,
                row.confirmed_row_id,
                row.step_token,
                row.step_index,
            )
            for row in self.rows
        ]
        if len(set(identities)) != len(identities):
            raise ValueError("Duplicate Fee Evaluation edited row identity.")
        manual_identities = [
            (
                row.row_kind,
                row.confirmed_group_id if row.row_kind == "sample_preparation" else "",
                row.group_key if row.row_kind == "sample_preparation" else "",
                row.group_label if row.row_kind == "sample_preparation" else "",
            )
            for row in self.manual_rows
        ]
        if len(set(manual_identities)) != len(manual_identities):
            raise ValueError("Duplicate Fee Evaluation manual row identity.")
        return self

    def to_application(self) -> FeeEvaluationEditedExportValues:
        """Convert this route DTO into application-layer edited export values."""
        return FeeEvaluationEditedExportValues(
            rows=tuple(row.to_application() for row in self.rows),
            summary=self.summary.to_application(),
            manual_rows=tuple(row.to_application() for row in self.manual_rows),
        )


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
    except (ConfirmedMatrixFeeEvaluationExportError, ProjectOutputRecordError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_response(result)


@router.post("/api/projects/{project_id}/confirmed-matrix/fee-evaluation/file/generate")
def generate_confirmed_matrix_fee_file(
    project_id: str,
    request: ConfirmedMatrixFeeEvaluationEditedFileRequest | None = Body(default=None),
    service: FeeEvaluationExportServicePort = Depends(
        get_confirmed_matrix_fee_evaluation_export_service
    ),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    """Generate a Matrix basic-fill Fee Evaluation workbook for browser download."""
    output_dir = settings.data_dir / FEE_FILE_DOWNLOAD_DIR_NAME
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        template_path = discover_fee_evaluation_template(settings.templates_dir)
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
            )
        )
    except (
        ConfirmedMatrixFeeEvaluationExportNotFoundError,
        ConfirmedMatrixFeeDraftNotFoundError,
        ProjectOutputRecordNotFoundError,
        FeeEvaluationTemplateDiscoveryError,
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


def _to_response(
    result: ExportConfirmedMatrixFeeEvaluationResult,
) -> ConfirmedMatrixFeeEvaluationExportResponse:
    return ConfirmedMatrixFeeEvaluationExportResponse(
        project_id=result.project_id,
        output_path=str(result.output_path),
        output_format=result.output_format,
        status=result.status,
        confirmed_matrix_id=result.confirmed_matrix_id,
        confirmed_revision=result.confirmed_revision,
        pricing_rule_version_id=result.pricing_rule_version_id,
        pricing_effective_from=result.pricing_effective_from,
        prepared_by=result.prepared_by,
        approved_by=result.approved_by,
        output_record_id=result.output_record_id,
        line_traceability=[
            FeeEvaluationExportLineTraceResponse(
                line_id=line.line_id,
                group_key=line.group_key,
                group_label=line.group_label,
                confirmed_group_id=line.confirmed_group_id,
                confirmed_row_id=line.confirmed_row_id,
                source_row_id=line.source_row_id,
                row_order=line.row_order,
                matched_rule_id=line.matched_rule_id,
                matched_rule_version_id=line.matched_rule_version_id,
                step_tokens=list(line.step_tokens),
                cell_value=line.cell_value,
            )
            for line in result.line_traceability
        ],
        warnings=list(result.warnings),
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
