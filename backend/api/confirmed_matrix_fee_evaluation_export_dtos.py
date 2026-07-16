"""Request, response, and conversion DTOs for Fee Evaluation exports."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

from backend.api.fee_evaluation_pricing_draft_http import (
    FeePricingDraftAttestationRequest,
)
from backend.application.confirmed_matrix_fee_evaluation_export_service import (
    ExportConfirmedMatrixFeeEvaluationResult,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedManualRow,
)


FEE_EDITED_UNIT_TYPES = {
    "per sample", "per reading", "per contact", "per cycle", "per time",
    "per hour", "per day", "per photo", "per report", "sample", "reading",
    "contact", "cycle", "time", "hour", "day", "photo", "report", "group",
    "specimen", "pending",
}


class ConfirmedMatrixFeeEvaluationExportRequest(FeePricingDraftAttestationRequest):
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
        "source_line_id", "confirmed_group_id", "confirmed_row_id", "spend_time",
        "unit_price", "unit_type", "units", "base_fee", "discount", "testing_fee",
        "notes", "step_token",
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
        return FeeEvaluationEditedExportRow(**self.model_dump())


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
        "row_kind", "confirmed_group_id", "group_key", "group_label", "spend_time",
        "unit_price", "unit_type", "units", "base_fee", "discount", "testing_fee",
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
        return FeeEvaluationEditedManualRow(**self.model_dump())


class FeeEvaluationEditedSummaryExportRequest(BaseModel):
    condition_confirmation_spend_time: str = "0"
    external_cost: str = "0"
    external_cost_note: str = ""
    lab_manpower_hourly_rate: str = "200"

    @field_validator(
        "condition_confirmation_spend_time", "external_cost", "external_cost_note",
        "lab_manpower_hourly_rate",
    )
    @classmethod
    def _strip_text(cls, value: str) -> str:
        return value.strip()

    def to_application(self) -> FeeEvaluationEditedExportSummary:
        return FeeEvaluationEditedExportSummary(**self.model_dump())


class ConfirmedMatrixFeeEvaluationEditedFileRequest(FeePricingDraftAttestationRequest):
    rows: list[FeeEvaluationEditedRowExportRequest] = []
    summary: FeeEvaluationEditedSummaryExportRequest
    manual_rows: list[FeeEvaluationEditedManualRowExportRequest] = []

    @model_validator(mode="after")
    def _reject_duplicate_identities(self) -> "ConfirmedMatrixFeeEvaluationEditedFileRequest":
        identities = [
            (row.source_line_id, row.confirmed_group_id, row.confirmed_row_id,
             row.step_token, row.step_index)
            for row in self.rows
        ]
        if len(set(identities)) != len(identities):
            raise ValueError("Duplicate Fee Evaluation edited row identity.")
        manual_identities = [
            (row.row_kind,
             row.confirmed_group_id if row.row_kind == "sample_preparation" else "",
             row.group_key if row.row_kind == "sample_preparation" else "",
             row.group_label if row.row_kind == "sample_preparation" else "")
            for row in self.manual_rows
        ]
        if len(set(manual_identities)) != len(manual_identities):
            raise ValueError("Duplicate Fee Evaluation manual row identity.")
        return self

    def to_application(self) -> FeeEvaluationEditedExportValues:
        return FeeEvaluationEditedExportValues(
            rows=tuple(row.to_application() for row in self.rows),
            summary=self.summary.to_application(),
            manual_rows=tuple(row.to_application() for row in self.manual_rows),
        )


def to_export_response(
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
