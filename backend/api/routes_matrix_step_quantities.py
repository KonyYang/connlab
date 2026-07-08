"""Matrix Step quantity setup API routes."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.application.matrix_step_quantity_service import (
    MatrixStepQuantityDraftResponse as MatrixStepQuantityDraftReadModel,
    MatrixStepQuantityError,
    MatrixStepQuantityNotFoundError,
    MatrixStepQuantitySaveCommand,
    MatrixStepQuantitySaveItem,
    MatrixStepQuantityService,
    MatrixStepQuantityValidationError,
)
from backend.infrastructure.storage.repositories import (
    ProjectBasicInformationRepository,
    ProjectMatrixDraftRepository,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/matrix-drafts",
    tags=["matrix-step-quantities"],
)


class MatrixStepQuantityItemResponse(BaseModel):
    """Step quantity setup row response."""

    draft_group_id: str
    draft_row_id: str
    step_sequence: int
    step_suffix_note: str | None = None
    raw_token: str | None = None
    test_item: str
    test_points_per_sample: str | None = None
    readings_per_point: str | None = None
    contact_points_per_sample: str | None = None
    total_readings: str | None = None
    source: str
    review_required: bool
    review_reason: str | None = None


class MatrixStepQuantityDraftResponse(BaseModel):
    """Step quantity setup response for one Matrix draft."""

    project_id: str
    project_matrix_draft_id: str
    items: list[MatrixStepQuantityItemResponse]


class MatrixStepQuantitySaveItemRequest(BaseModel):
    """Step quantity setup save row."""

    draft_group_id: str
    draft_row_id: str
    step_sequence: int
    step_suffix_note: str | None = None
    raw_token: str | None = None
    test_points_per_sample: str | None = None
    readings_per_point: str | None = None
    contact_points_per_sample: str | None = None
    source: str
    review_required: bool = False
    review_reason: str | None = None


class MatrixStepQuantitySaveRequest(BaseModel):
    """Batch save request for Matrix Step quantity setup."""

    items: list[MatrixStepQuantitySaveItemRequest]


def _get_matrix_step_quantity_service(
    session: Session = Depends(get_session),
) -> MatrixStepQuantityService:
    return MatrixStepQuantityService(
        draft_store=ProjectMatrixDraftRepository(session),
        basic_information_store=ProjectBasicInformationRepository(session),
        clock=lambda: datetime.now(timezone.utc).isoformat(),
        id_factory=lambda: uuid4().hex,
    )


@router.get(
    "/{project_matrix_draft_id}/step-quantities",
    response_model=MatrixStepQuantityDraftResponse,
)
def get_matrix_step_quantities(
    project_id: str,
    project_matrix_draft_id: str,
    service: MatrixStepQuantityService = Depends(_get_matrix_step_quantity_service),
) -> MatrixStepQuantityDraftResponse:
    """Return Matrix Step quantity setup rows for one draft."""
    try:
        response = service.get_draft(
            project_id=project_id,
            project_matrix_draft_id=project_matrix_draft_id,
        )
    except MatrixStepQuantityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_response(response)


@router.put(
    "/{project_matrix_draft_id}/step-quantities",
    response_model=MatrixStepQuantityDraftResponse,
)
def save_matrix_step_quantities(
    project_id: str,
    project_matrix_draft_id: str,
    request: MatrixStepQuantitySaveRequest,
    service: MatrixStepQuantityService = Depends(_get_matrix_step_quantity_service),
) -> MatrixStepQuantityDraftResponse:
    """Persist Matrix Step quantity setup rows for one draft."""
    try:
        response = service.save_draft(
            MatrixStepQuantitySaveCommand(
                project_id=project_id,
                project_matrix_draft_id=project_matrix_draft_id,
                items=tuple(
                    MatrixStepQuantitySaveItem(
                        draft_group_id=item.draft_group_id,
                        draft_row_id=item.draft_row_id,
                        step_sequence=item.step_sequence,
                        step_suffix_note=item.step_suffix_note,
                        raw_token=item.raw_token,
                        test_points_per_sample=item.test_points_per_sample,
                        readings_per_point=item.readings_per_point,
                        contact_points_per_sample=item.contact_points_per_sample,
                        source=item.source,
                        review_required=item.review_required,
                        review_reason=item.review_reason,
                    )
                    for item in request.items
                ),
            )
        )
    except MatrixStepQuantityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MatrixStepQuantityValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except MatrixStepQuantityError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(response)


def _to_response(
    response: MatrixStepQuantityDraftReadModel,
) -> MatrixStepQuantityDraftResponse:
    return MatrixStepQuantityDraftResponse(
        project_id=response.project_id,
        project_matrix_draft_id=response.project_matrix_draft_id,
        items=[
            MatrixStepQuantityItemResponse(
                draft_group_id=item.draft_group_id,
                draft_row_id=item.draft_row_id,
                step_sequence=item.step_sequence,
                step_suffix_note=item.step_suffix_note,
                raw_token=item.raw_token,
                test_item=item.test_item,
                test_points_per_sample=item.test_points_per_sample,
                readings_per_point=item.readings_per_point,
                contact_points_per_sample=item.contact_points_per_sample,
                total_readings=item.total_readings,
                source=item.source,
                review_required=item.review_required,
                review_reason=item.review_reason,
            )
            for item in response.items
        ],
    )
