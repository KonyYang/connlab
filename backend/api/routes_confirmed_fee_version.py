"""Confirmed Fee authority version API routes."""

from __future__ import annotations

from typing import Protocol

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import get_confirmed_fee_version_service
from backend.application.confirmed_fee_version_service import (
    ConfirmFeeVersionCommand,
    ConfirmedFeePricingDraftChangedError,
    ConfirmedFeePricingDraftMissingError,
    ConfirmedFeePricingDraftStaleError,
    ConfirmedFeeSummaryValidationError,
    ConfirmedFeeVersionReadResult,
)
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    ConfirmedMatrixFeeTemplateBasicFillNotFoundError,
)
from backend.domain.confirmed_fee import ConfirmedFeeSummary, ConfirmedFeeVersion


router = APIRouter(tags=["confirmed-fee"])


class ConfirmedFeeVersionServicePort(Protocol):
    """Route dependency contract for Confirmed Fee version service."""

    def get_latest(self, project_id: str) -> ConfirmedFeeVersionReadResult:
        """Return latest Confirmed Fee status."""

    def confirm(self, command: ConfirmFeeVersionCommand) -> ConfirmedFeeVersion:
        """Create a Confirmed Fee version."""


class ConfirmedFeeSummaryRequest(BaseModel):
    testing_fee_total: str
    working_hours: str
    lab_manpower_cost: str
    external_cost: str
    grand_cost: str

    def to_domain(self) -> ConfirmedFeeSummary:
        """Convert API request totals to domain summary."""
        return ConfirmedFeeSummary(
            testing_fee_total=self.testing_fee_total,
            working_hours=self.working_hours,
            lab_manpower_cost=self.lab_manpower_cost,
            external_cost=self.external_cost,
            grand_cost=self.grand_cost,
        )


class ConfirmedFeeVersionCreateRequest(BaseModel):
    confirmed_by: str
    expected_pricing_draft_edit_id: str
    summary: ConfirmedFeeSummaryRequest
    expected_generation: int | None = None
    expected_payload_fingerprint: str | None = None
    expected_validation_token: str | None = None
    confirmation_note: str | None = None


class ConfirmedFeeSummaryResponse(BaseModel):
    testing_fee_total: str
    working_hours: str
    lab_manpower_cost: str
    external_cost: str
    grand_cost: str


class ConfirmedFeeVersionResponse(BaseModel):
    confirmed_fee_id: str
    project_id: str
    confirmed_fee_revision: int
    confirmed_matrix_id: str
    confirmed_revision: int
    fee_rule_version_id: str
    pricing_draft_edit_id: str
    pricing_effective_from: str | None
    summary: ConfirmedFeeSummaryResponse
    confirmed_by: str
    confirmed_at: str
    confirmation_note: str | None


class ConfirmedFeeLatestResponse(BaseModel):
    status: str
    current_confirmed_matrix_id: str
    current_confirmed_revision: int
    current_fee_rule_version_id: str
    fee_review_required_count: int = 0
    confirmed_fee: ConfirmedFeeVersionResponse | None


@router.get(
    "/api/projects/{project_id}/confirmed-fee/latest",
    response_model=ConfirmedFeeLatestResponse,
)
def get_confirmed_fee_latest(
    project_id: str,
    service: ConfirmedFeeVersionServicePort = Depends(get_confirmed_fee_version_service),
) -> ConfirmedFeeLatestResponse:
    """Return latest Confirmed Fee authority status for one project."""
    try:
        return _to_latest_response(service.get_latest(project_id))
    except ConfirmedMatrixFeeTemplateBasicFillNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/api/projects/{project_id}/confirmed-fee/versions",
    response_model=ConfirmedFeeLatestResponse,
)
def create_confirmed_fee_version(
    project_id: str,
    request: ConfirmedFeeVersionCreateRequest,
    service: ConfirmedFeeVersionServicePort = Depends(get_confirmed_fee_version_service),
) -> ConfirmedFeeLatestResponse:
    """Create a Confirmed Fee authority version from saved pricing draft."""
    try:
        if not request.confirmed_by.strip():
            raise ConfirmedFeeSummaryValidationError("confirmed_by is required.")
        version = service.confirm(
            ConfirmFeeVersionCommand(
                project_id=project_id,
                confirmed_by=request.confirmed_by,
                expected_pricing_draft_edit_id=request.expected_pricing_draft_edit_id,
                summary=request.summary.to_domain(),
                expected_generation=request.expected_generation,
                expected_payload_fingerprint=request.expected_payload_fingerprint,
                expected_validation_token=request.expected_validation_token,
                confirmation_note=request.confirmation_note,
            )
        )
        latest = service.get_latest(project_id)
        return _to_latest_response(
            ConfirmedFeeVersionReadResult(
                status=latest.status,
                current_context=latest.current_context,
                latest_confirmed_fee=version,
            )
        )
    except ConfirmedMatrixFeeTemplateBasicFillNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (
        ConfirmedFeePricingDraftMissingError,
        ConfirmedFeePricingDraftStaleError,
        ConfirmedFeePricingDraftChangedError,
    ) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ConfirmedFeeSummaryValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _to_latest_response(
    result: ConfirmedFeeVersionReadResult,
) -> ConfirmedFeeLatestResponse:
    return ConfirmedFeeLatestResponse(
        status=result.status,
        current_confirmed_matrix_id=result.current_context.confirmed_matrix_id,
        current_confirmed_revision=result.current_context.confirmed_revision,
        current_fee_rule_version_id=result.current_context.fee_rule_version_id,
        fee_review_required_count=result.fee_review_required_count,
        confirmed_fee=(
            _to_version_response(result.latest_confirmed_fee)
            if result.latest_confirmed_fee
            else None
        ),
    )


def _to_version_response(version: ConfirmedFeeVersion) -> ConfirmedFeeVersionResponse:
    return ConfirmedFeeVersionResponse(
        confirmed_fee_id=version.confirmed_fee_id,
        project_id=version.project_id,
        confirmed_fee_revision=version.confirmed_fee_revision,
        confirmed_matrix_id=version.confirmed_matrix_id,
        confirmed_revision=version.confirmed_revision,
        fee_rule_version_id=version.fee_rule_version_id,
        pricing_draft_edit_id=version.pricing_draft_edit_id,
        pricing_effective_from=version.pricing_effective_from,
        summary=ConfirmedFeeSummaryResponse(
            testing_fee_total=version.summary.testing_fee_total,
            working_hours=version.summary.working_hours,
            lab_manpower_cost=version.summary.lab_manpower_cost,
            external_cost=version.summary.external_cost,
            grand_cost=version.summary.grand_cost,
        ),
        confirmed_by=version.confirmed_by,
        confirmed_at=version.confirmed_at,
        confirmation_note=version.confirmation_note,
    )
