"""Fee Evaluation pricing draft persistence API routes."""

from __future__ import annotations

from typing import Protocol

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_fee_evaluation_pricing_draft_service
from backend.api.routes_confirmed_matrix_fee_evaluation_export import (
    ConfirmedMatrixFeeEvaluationEditedFileRequest,
    FeeEvaluationEditedManualRowExportRequest,
    FeeEvaluationEditedRowExportRequest,
    FeeEvaluationEditedSummaryExportRequest,
)
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    ConfirmedMatrixFeeTemplateBasicFillNotFoundError,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftLoadResult,
    FeeEvaluationPricingDraftSnapshot,
    SaveFeeEvaluationPricingDraftCommand,
)


router = APIRouter(tags=["confirmed-matrix-fee-evaluation-pricing-draft"])


class FeeEvaluationPricingDraftServicePort(Protocol):
    """Route dependency contract for pricing draft persistence."""

    def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
        """Load saved pricing draft state for one project."""

    def save(
        self, command: SaveFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftLoadResult:
        """Save pricing draft state for one project."""


class FeeEvaluationPricingDraftResponse(BaseModel):
    status: str
    current_confirmed_matrix_id: str
    current_confirmed_revision: int
    current_fee_rule_version_id: str
    saved_confirmed_matrix_id: str | None = None
    saved_confirmed_revision: int | None = None
    saved_fee_rule_version_id: str | None = None
    saved_updated_at: str | None = None
    payload: ConfirmedMatrixFeeEvaluationEditedFileRequest | None = None


@router.get(
    "/api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft",
    response_model=FeeEvaluationPricingDraftResponse,
)
def get_fee_evaluation_pricing_draft(
    project_id: str,
    service: FeeEvaluationPricingDraftServicePort = Depends(
        get_fee_evaluation_pricing_draft_service
    ),
) -> FeeEvaluationPricingDraftResponse:
    """Return saved Fee Evaluation pricing draft state for the current context."""
    try:
        return _to_response(service.load(project_id))
    except ConfirmedMatrixFeeTemplateBasicFillNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put(
    "/api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft",
    response_model=FeeEvaluationPricingDraftResponse,
)
def save_fee_evaluation_pricing_draft(
    project_id: str,
    request: ConfirmedMatrixFeeEvaluationEditedFileRequest,
    service: FeeEvaluationPricingDraftServicePort = Depends(
        get_fee_evaluation_pricing_draft_service
    ),
) -> FeeEvaluationPricingDraftResponse:
    """Persist Fee Evaluation pricing draft edits for the current context."""
    try:
        return _to_response(
            service.save(
                SaveFeeEvaluationPricingDraftCommand(
                    project_id=project_id,
                    edited_values=request.to_application(),
                )
            )
        )
    except ConfirmedMatrixFeeTemplateBasicFillNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _to_response(
    result: FeeEvaluationPricingDraftLoadResult,
) -> FeeEvaluationPricingDraftResponse:
    snapshot = result.saved_snapshot
    return FeeEvaluationPricingDraftResponse(
        status=result.status,
        current_confirmed_matrix_id=result.current_context.confirmed_matrix_id,
        current_confirmed_revision=result.current_context.confirmed_revision,
        current_fee_rule_version_id=result.current_context.fee_rule_version_id,
        saved_confirmed_matrix_id=snapshot.confirmed_matrix_id if snapshot else None,
        saved_confirmed_revision=snapshot.confirmed_revision if snapshot else None,
        saved_fee_rule_version_id=snapshot.fee_rule_version_id if snapshot else None,
        saved_updated_at=snapshot.updated_at if snapshot else None,
        payload=_to_payload(snapshot) if result.status == "current" and snapshot else None,
    )


def _to_payload(
    snapshot: FeeEvaluationPricingDraftSnapshot,
) -> ConfirmedMatrixFeeEvaluationEditedFileRequest:
    values = snapshot.edited_values
    return ConfirmedMatrixFeeEvaluationEditedFileRequest(
        rows=[
            FeeEvaluationEditedRowExportRequest(
                source_line_id=row.source_line_id,
                confirmed_group_id=row.confirmed_group_id,
                confirmed_row_id=row.confirmed_row_id,
                step_token=row.step_token,
                step_index=row.step_index,
                spend_time=row.spend_time,
                unit_price=row.unit_price,
                unit_type=row.unit_type,
                units=row.units,
                base_fee=row.base_fee,
                discount=row.discount,
                testing_fee=row.testing_fee,
                notes=row.notes,
            )
            for row in values.rows
        ],
        summary=FeeEvaluationEditedSummaryExportRequest(
            condition_confirmation_spend_time=(
                values.summary.condition_confirmation_spend_time
            ),
            external_cost=values.summary.external_cost,
            external_cost_note=values.summary.external_cost_note,
            lab_manpower_hourly_rate=values.summary.lab_manpower_hourly_rate,
        ),
        manual_rows=[
            FeeEvaluationEditedManualRowExportRequest(
                row_kind=row.row_kind,
                confirmed_group_id=row.confirmed_group_id,
                group_key=row.group_key,
                group_label=row.group_label,
                spend_time=row.spend_time,
                unit_price=row.unit_price,
                unit_type=row.unit_type,
                units=row.units,
                base_fee=row.base_fee,
                discount=row.discount,
                testing_fee=row.testing_fee,
                notes=row.notes,
            )
            for row in values.manual_rows
        ],
    )
